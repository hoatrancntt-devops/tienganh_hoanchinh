"""Nạp YAML vào DB. Idempotent: chạy lại chỉ cập nhật, không tạo trùng."""
import logging

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import (
    Activity,
    Course,
    Item,
    Lesson,
    Prerequisite,
    Topic,
    Unit,
)
from app.models.enums import ActivityKind, Cefr, ContentStatus, Phase
from app.seeds.schema import LessonYAML
from app.seeds.validate_content import check_graph, check_pedagogy, load_all

log = logging.getLogger(__name__)

TOPICS = [
    ("core", "Nền tảng"), ("social", "Giao tiếp xã giao"), ("food", "Ăn uống"),
    ("transport", "Đi lại"), ("office", "Công sở"), ("it_english", "Tiếng Anh CNTT"),
]
UNITS = [
    ("U-F1", "Nền tảng 1: âm tiếng Việt không có", 1, "core"),
    ("U-F2", "Nền tảng 2: âm cuối và cụm phụ âm", 2, "core"),
    ("U-F3", "Nền tảng 3: trọng âm và câu lõi", 3, "core"),
    ("U-F4", "Nền tảng 4: câu sinh tồn", 4, "core"),
    ("U-D1", "Xã giao", 5, "social"),
    ("U-D2", "Ăn uống", 6, "food"),
    ("U-D3", "Đi lại", 7, "transport"),
    ("U-O1", "Công sở", 8, "office"),
    ("U-I1", "CNTT: hỗ trợ & báo sự cố", 9, "it_english"),
    ("U-I2", "CNTT: làm việc nhóm & báo cáo", 10, "it_english"),
    ("U-I3", "CNTT: mạng, cloud, bảo mật, dữ liệu", 11, "it_english"),
    ("U-I4", "CNTT: giao tiếp với bên ngoài & viết", 12, "it_english"),
    ("U-R1", "Đọc phục vụ công việc", 13, "core"),
]
COURSE = ("speaking-core", "Nghe nói giao tiếp công sở", "Speaking Core")


async def _upsert_taxonomy(db: AsyncSession) -> tuple[Course, dict[str, Unit]]:
    for slug, title in TOPICS:
        if not (await db.execute(select(Topic).where(Topic.slug == slug))).scalar_one_or_none():
            db.add(Topic(slug=slug, title_vi=title))
    await db.commit()

    course = (
        await db.execute(select(Course).where(Course.slug == COURSE[0]))
    ).scalar_one_or_none()
    if course is None:
        course = Course(slug=COURSE[0], title_vi=COURSE[1], title_en=COURSE[2],
                        cefr_from=Cefr.PRE_A1, cefr_to=Cefr.B1, track="speaking_core")
        db.add(course)
        await db.commit()
        await db.refresh(course)

    topics = {t.slug: t for t in (await db.execute(select(Topic))).scalars().all()}
    units: dict[str, Unit] = {}
    for code, title, order, topic_slug in UNITS:
        unit = (await db.execute(select(Unit).where(Unit.code == code))).scalar_one_or_none()
        if unit is None:
            unit = Unit(course_id=course.id, code=code, title_vi=title, order_index=order,
                        topic_id=topics[topic_slug].id, objectives_vi=[])
            db.add(unit)
            await db.commit()
            await db.refresh(unit)
        units[code] = unit
    return course, units


async def _upsert_lesson(db: AsyncSession, spec: LessonYAML, unit: Unit) -> Lesson:
    lesson = (
        await db.execute(select(Lesson).where(Lesson.code == spec.id))
    ).scalar_one_or_none()

    # Nội dung học: gắn sẵn đường dẫn audio (sinh ở generate_audio) theo mã bài + chỉ số.
    dialogue = {}
    if spec.dialogue:
        dialogue = {
            "context_vi": spec.dialogue.context_vi,
            "turns": [
                {"speaker": t.speaker, "en": t.en, "vi": t.vi,
                 "audio": f"/media/dialogue/{spec.id}_{i}.wav"}
                for i, t in enumerate(spec.dialogue.turns)
            ],
        }
    vocabulary = [
        {"term": v.term, "ipa": v.ipa, "meaning_vi": v.meaning_vi, "chunk": v.chunk,
         "audio": f"/media/vocab/{spec.id}_{i}.wav"}
        for i, v in enumerate(spec.vocabulary)
    ]
    sentence_patterns = [
        {"pattern": p.pattern, "meaning_vi": p.meaning_vi} for p in spec.sentence_patterns
    ]
    # Không gắn khoá audio nào ở đây — xem chú thích cột Lesson.reading_passage.
    reading_passage = {}
    if spec.reading_passage:
        rp = spec.reading_passage
        reading_passage = {
            "id": rp.id, "kind": rp.kind, "context_vi": rp.context_vi,
            "text_en": rp.text_en, "text_vi": rp.text_vi,
        }

    fields = dict(
        unit_id=unit.id, slug=spec.slug, phase=Phase(spec.phase), topic=spec.topic,
        cefr_target=Cefr(spec.cefr_target), order_index=spec.order_index,
        title_vi=spec.title_vi, title_en=spec.title_en, est_minutes=spec.est_minutes,
        is_checkpoint=spec.is_checkpoint, status=ContentStatus(spec.status),
        objective_vi=spec.objective_vi, objective_observable=spec.objective_observable,
        vietnamese_explanation=spec.vietnamese_explanation.model_dump(),
        common_mistakes=[m.model_dump() for m in spec.common_mistakes],
        memory_trick_vi=spec.memory_trick_vi,
        dialogue=dialogue,
        vocabulary=vocabulary,
        sentence_patterns=sentence_patterns,
        reading_passage=reading_passage,
        mastery_threshold=spec.unlock_condition.mastery_threshold,
        mastery_weights=spec.unlock_condition.mastery_weights,
        min_speaking_attempts=spec.unlock_condition.min_speaking_attempts,
        challenge_threshold=spec.unlock_condition.challenge_threshold,
        min_per_skill=spec.unlock_condition.min_per_skill,
        recommended_next=spec.recommended_next,
    )
    if lesson is None:
        lesson = Lesson(code=spec.id, **fields)
        db.add(lesson)
    else:
        for k, v in fields.items():
            setattr(lesson, k, v)
    await db.commit()
    await db.refresh(lesson)

    await _upsert_activities(db, lesson, _activity_specs(spec))
    return lesson


def _activity_specs(spec: LessonYAML) -> list[dict]:
    """Mô tả các hoạt động của bài dưới dạng dữ liệu thuần, chưa chạm DB.

    Thứ tự trong danh sách là thứ tự học viên gặp trên player.
    """
    out: list[dict] = []

    if spec.listening_snippet:
        s = spec.listening_snippet
        out.append({
            "kind": ActivityKind.LISTEN, "title_vi": "Nghe hội thoại",
            "config": {"transcript_en": s.transcript_en, "transcript_vi": s.transcript_vi,
                       "context_vi": s.context_vi, "snippet_id": s.id, "speed": s.speed},
            "items": [
                {"kind": "mcq", "prompt_vi": q.q_vi, "prompt_en": s.transcript_en,
                 "choices": q.choices, "answer_index": q.answer, "difficulty": q.difficulty,
                 "tags": ["listening", s.id]}
                for q in s.questions
            ],
        })

    if spec.speaking_drills:
        out.append({
            "kind": ActivityKind.SPEAK, "title_vi": "Luyện nói", "config": {},
            "items": [
                {"kind": d.kind, "prompt_en": d.prompt_en or (d.expected_text or ""),
                 "prompt_vi": d.prompt_vi, "expected_text": d.expected_text, "ipa": d.ipa,
                 "focus_phonemes": d.focus_phonemes, "accept_patterns": d.accept_patterns,
                 "difficulty": 2, "tags": ["speak", spec.phase]}
                for d in spec.speaking_drills
            ],
        })

    if spec.reading_passage:
        rp = spec.reading_passage
        out.append({
            "kind": ActivityKind.READ, "title_vi": "Đọc hiểu",
            "config": {"passage_id": rp.id, "kind": rp.kind, "context_vi": rp.context_vi,
                       "text_en": rp.text_en, "text_vi": rp.text_vi},
            # expected_text để None: generate_audio chỉ sinh tiếng cho Item có expected_text,
            # nên đây là chỗ giữ cho bài đọc không bao giờ đọc thành tiếng.
            "items": [
                {"kind": "mcq_read", "prompt_en": q.q_en, "prompt_vi": "",
                 "expected_text": None, "choices": q.choices, "answer_index": q.answer,
                 "difficulty": q.difficulty, "tags": ["read", q.skill, rp.id]}
                for q in rp.questions
            ],
        })

    if spec.writing_task:
        wt = spec.writing_task
        out.append({
            "kind": ActivityKind.WRITE, "title_vi": "Luyện viết",
            # config là payload cho trình duyệt: KHÔNG chứa đáp án. `lines` sắp theo bảng
            # chữ cái chứ không theo thứ tự đúng — gửi đúng thứ tự xuống là gửi luôn đáp án.
            "config": {"task_id": wt.id, "kind": wt.kind, "frame_vi": wt.frame_vi,
                       "min_words": wt.min_words, "hint_vi": wt.hint_vi,
                       "so_o": len(wt.blanks), "lines": sorted(wt.ordered_lines)},
            "items": [{
                "kind": wt.kind, "prompt_en": wt.prompt_en, "prompt_vi": wt.prompt_vi,
                "expected_text": None, "choices": [], "answer_index": None,
                "accept_patterns": wt.accept,
                "scoring_weights": {"kind": wt.kind, "min_words": wt.min_words,
                                    "keywords": wt.keywords, "blanks": wt.blanks,
                                    "ordered_lines": wt.ordered_lines,
                                    "required_chunks": wt.required_chunks,
                                    "hint_vi": wt.hint_vi, "sample_en": wt.sample_en},
                "difficulty": 2, "tags": ["write", wt.kind],
            }],
        })

    if spec.mini_quiz:
        out.append({
            "kind": ActivityKind.QUIZ, "title_vi": "Củng cố nhanh", "config": {},
            "items": [
                {"kind": q.kind, "prompt_vi": q.prompt_vi, "prompt_en": q.audio_text,
                 "expected_text": q.audio_text or None, "choices": q.choices,
                 "answer_index": q.answer, "difficulty": q.difficulty,
                 "focus_phonemes": q.focus_phonemes, "tags": ["quiz"]}
                for q in spec.mini_quiz
            ],
        })
    return out


# Giá trị mặc định cho các cột không phải hoạt động nào cũng khai.
_ITEM_DEFAULTS = {
    "prompt_en": "", "prompt_vi": "", "expected_text": None, "ipa": "",
    "choices": [], "answer_index": None, "accept_patterns": [], "focus_phonemes": [],
    "scoring_weights": {}, "difficulty": 2, "tags": [],
}


async def _upsert_activities(db: AsyncSession, lesson: Lesson, specs: list[dict]) -> None:
    """Cập nhật tại chỗ thay vì xoá rồi dựng lại.

    Bản cũ `delete(Activity)` mỗi lần seed. `Item.activity_id` cascade từ Activity, và
    `ItemAttempt.item_id` cascade từ Item — nên mỗi lần `make seed` là XOÁ SẠCH lịch sử
    làm bài của mọi học viên. Không có gì báo, và `LessonProgress` còn lại thì tính lại
    từ số 0.

    Khoá định danh: Activity theo (lesson, kind), Item theo (activity, order_index).
    Đánh đổi đã biết: đảo thứ tự câu trong cùng một hoạt động sẽ gán lượt làm bài cũ sang
    câu khác. Chấp nhận được vì mastery tính gộp theo loại hoạt động, và đảo thứ tự câu
    là việc hiếm — đổi lại, sửa nội dung không còn thổi bay tiến độ học viên.
    """
    hien_co = {
        act.kind: act
        for act in (
            await db.execute(select(Activity).where(Activity.lesson_id == lesson.id))
        ).scalars().all()
    }
    giu_lai = set()

    for order, aspec in enumerate(specs):
        kind = str(aspec["kind"])
        giu_lai.add(kind)
        act = hien_co.get(kind)
        if act is None:
            act = Activity(lesson_id=lesson.id, kind=aspec["kind"])
            db.add(act)
        act.order_index = order
        act.title_vi = aspec["title_vi"]
        act.config = aspec["config"]
        await db.flush()            # cần act.id để gắn Item, nhưng chưa chốt transaction

        cu = {
            item.order_index: item
            for item in (
                await db.execute(select(Item).where(Item.activity_id == act.id))
            ).scalars().all()
        }
        for i, ispec in enumerate(aspec["items"]):
            item = cu.pop(i, None)
            if item is None:
                item = Item(activity_id=act.id, order_index=i)
                db.add(item)
            for field, mac_dinh in _ITEM_DEFAULTS.items():
                setattr(item, field, ispec.get(field, mac_dinh))
            item.kind = ispec["kind"]
        # Câu bị bỏ khỏi giáo trình thì xoá — lượt làm bài của nó đi theo, đúng như vậy.
        for thua in cu.values():
            await db.delete(thua)

    for kind, act in hien_co.items():
        if kind not in giu_lai:
            await db.delete(act)
    # Một lần commit cho cả bài: nếu giữa chừng hỏng thì bài đó không bị nửa vời.
    await db.commit()


async def _upsert_edges(db: AsyncSession, specs: list[LessonYAML]) -> int:
    codes = {
        lesson.code: lesson
        for lesson in (await db.execute(select(Lesson))).scalars().all()
    }
    await db.execute(delete(Prerequisite))
    await db.commit()
    n = 0
    for spec in specs:
        for pre in spec.prerequisites:
            if spec.id not in codes or pre.lesson not in codes:
                continue
            db.add(Prerequisite(
                lesson_id=codes[spec.id].id, requires_lesson_id=codes[pre.lesson].id,
                min_mastery=pre.min_mastery, kind=pre.kind,
            ))
            n += 1
    await db.commit()
    return n


async def load_content(db: AsyncSession) -> dict:
    specs, errors = load_all()
    if errors:
        raise ValueError("Nội dung không hợp lệ:\n  " + "\n  ".join(errors))
    errors = check_graph(specs) + check_pedagogy(specs)
    if errors:
        raise ValueError("Nội dung không hợp lệ:\n  " + "\n  ".join(errors))

    _, units = await _upsert_taxonomy(db)
    for spec in specs:
        if spec.unit not in units:
            raise ValueError(f"{spec.id}: unit '{spec.unit}' chưa khai báo trong loader.UNITS")
        await _upsert_lesson(db, spec, units[spec.unit])
    edges = await _upsert_edges(db, specs)
    log.info("loaded %s lessons, %s edges", len(specs), edges)
    return {"lessons": len(specs), "edges": edges}
