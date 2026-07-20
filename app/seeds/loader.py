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
        mastery_threshold=spec.unlock_condition.mastery_threshold,
        mastery_weights=spec.unlock_condition.mastery_weights,
        min_speaking_attempts=spec.unlock_condition.min_speaking_attempts,
        challenge_threshold=spec.unlock_condition.challenge_threshold,
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

    # Activity/Item dựng lại từ đầu: nội dung là YAML, DB chỉ là bản chiếu.
    await db.execute(delete(Activity).where(Activity.lesson_id == lesson.id))
    await db.commit()

    order = 0

    if spec.listening_snippet:
        snippet = spec.listening_snippet
        act = Activity(lesson_id=lesson.id, kind=ActivityKind.LISTEN, order_index=order,
                       title_vi="Nghe hội thoại",
                       config={"transcript_en": snippet.transcript_en,
                               "transcript_vi": snippet.transcript_vi,
                               "snippet_id": snippet.id, "speed": snippet.speed})
        db.add(act)
        await db.commit()
        await db.refresh(act)
        for i, q in enumerate(snippet.questions):
            db.add(Item(activity_id=act.id, order_index=i, kind="mcq",
                        prompt_vi=q.q_vi, prompt_en=snippet.transcript_en,
                        choices=q.choices, answer_index=q.answer, difficulty=q.difficulty,
                        tags=["listening", snippet.id]))
        order += 1

    if spec.speaking_drills:
        act = Activity(lesson_id=lesson.id, kind=ActivityKind.SPEAK, order_index=order,
                       title_vi="Luyện nói", config={})
        db.add(act)
        await db.commit()
        await db.refresh(act)
        phase_tag = spec.phase
        for i, d in enumerate(spec.speaking_drills):
            db.add(Item(
                activity_id=act.id, order_index=i, kind=d.kind,
                prompt_en=d.prompt_en or (d.expected_text or ""),
                prompt_vi=d.prompt_vi, expected_text=d.expected_text, ipa=d.ipa,
                focus_phonemes=d.focus_phonemes, accept_patterns=d.accept_patterns,
                scoring_weights={}, difficulty=2, tags=["speak", phase_tag],
            ))
        order += 1

    if spec.mini_quiz:
        act = Activity(lesson_id=lesson.id, kind=ActivityKind.QUIZ, order_index=order,
                       title_vi="Củng cố nhanh", config={})
        db.add(act)
        await db.commit()
        await db.refresh(act)
        for i, q in enumerate(spec.mini_quiz):
            db.add(Item(
                activity_id=act.id, order_index=i, kind=q.kind, prompt_vi=q.prompt_vi,
                prompt_en=q.audio_text, expected_text=q.audio_text or None,
                choices=q.choices, answer_index=q.answer, difficulty=q.difficulty,
                focus_phonemes=q.focus_phonemes, tags=["quiz"],
            ))
    await db.commit()
    return lesson


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
