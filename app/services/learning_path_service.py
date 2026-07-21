"""Lộ trình, mastery update, recommended-next + why-this-next (PART J, L).

why-this-next là luật thuần: nó hiện ở mọi lần vào trang chủ; nếu gọi LLM thì đây là
khoản tốn nhất hệ thống, và luật làm tốt hơn.
"""
import logging
import uuid
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utcnow
from app.models.content import Activity, Item, Lesson, Prerequisite
from app.models.enums import ContentStatus, LessonState, Phase
from app.models.progress import ItemAttempt, LessonProgress, ReviewQueue
from app.services import prerequisite_service as prereq

log = logging.getLogger(__name__)

PHASE_ORDER = [
    Phase.ORIENTATION, Phase.FOUNDATION, Phase.DAILY,
    Phase.OFFICE, Phase.IT_ENGLISH, Phase.READING,
]
RECENT_ATTEMPTS = 3  # chỉ lấy 3 lần gần nhất: phải *đang* làm được, không phải *từng* làm được

# Kỹ năng mỗi bài rèn, suy từ phase (nội dung mỗi phase đồng nhất: foundation/daily/office/
# it_english có drill nói + đoạn nghe; reading có đọc hiểu + đoạn nghe). Không lưu DB — tránh
# migration; nếu sau này một phase trộn nhiều kiểu bài thì chuyển sang suy từ activity.
PHASE_SKILLS: dict[str, list[str]] = {
    Phase.FOUNDATION: ["speak", "listen"],
    Phase.DAILY: ["speak", "listen"],
    Phase.OFFICE: ["speak", "listen"],
    Phase.IT_ENGLISH: ["speak", "listen"],
    Phase.READING: ["read", "listen"],
    Phase.ORIENTATION: ["listen"],
}


def skills_for_phase(phase: str) -> list[str]:
    return PHASE_SKILLS.get(phase, [])


async def _recent_scores_by_kind(
    db: AsyncSession, user_id: uuid.UUID, lesson_id: uuid.UUID
) -> tuple[dict[str, float], int]:
    """Trung bình 3 lần thử gần nhất mỗi item, gom theo activity_kind."""
    stmt = (
        select(ItemAttempt)
        .where(
            ItemAttempt.user_id == user_id,
            ItemAttempt.lesson_id == lesson_id,
            ItemAttempt.is_preview.is_(False),
        )
        .order_by(ItemAttempt.created_at.desc())
    )
    attempts = (await db.execute(stmt)).scalars().all()

    per_item: dict[uuid.UUID, list[ItemAttempt]] = {}
    for att in attempts:
        bucket = per_item.setdefault(att.item_id, [])
        if len(bucket) < RECENT_ATTEMPTS:
            bucket.append(att)

    by_kind: dict[str, list[float]] = {}
    speaking_attempts = 0
    for bucket in per_item.values():
        kind = bucket[0].activity_kind
        avg = sum(a.score for a in bucket) / len(bucket)
        by_kind.setdefault(kind, []).append(avg)
        if kind in ("speak", "shadow"):
            speaking_attempts += len(bucket)

    # gom shadow vào speak để khớp mastery_weights
    scores: dict[str, list[float]] = {}
    for kind, vals in by_kind.items():
        key = "speak" if kind in ("speak", "shadow") else kind
        scores.setdefault(key, []).extend(vals)
    return ({k: sum(v) / len(v) for k, v in scores.items()}, speaking_attempts)


async def update_mastery(db: AsyncSession, user_id: uuid.UUID, lesson_id: uuid.UUID) -> dict:
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise ValueError("lesson not found")

    scores, speaking_attempts = await _recent_scores_by_kind(db, user_id, lesson_id)
    raw = prereq.compute_mastery_raw(scores, lesson)
    raw = prereq.apply_speaking_gate(raw, speaking_attempts, lesson)

    prog = (
        await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
            )
        )
    ).scalar_one_or_none()
    if prog is None:
        # default= chỉ áp lúc INSERT, chưa flush thì mọi cột chưa khai vẫn là None.
        # `state` phải khai luôn: thiếu nó thì `prog.state` là None, phép kiểm
        # `state in (AVAILABLE, PREVIEWABLE, LOCKED)` bên dưới trượt, và bài không bao giờ
        # chuyển sang "đang học" — học viên làm xong một hoạt động mà lộ trình vẫn hiện khoá.
        prog = LessonProgress(user_id=user_id, lesson_id=lesson_id, attempts_count=0,
                              state=LessonState.LOCKED)
        db.add(prog)

    prog.mastery_raw = raw
    prog.speaking_attempts = speaking_attempts
    prog.attempts_count = (prog.attempts_count or 0) + 1
    prog.last_activity_at = utcnow()

    unlocked: list[str] = []
    if raw >= lesson.mastery_threshold:
        if prog.state != LessonState.MASTERED:
            prog.mastered_at = utcnow()
        prog.state = LessonState.MASTERED
        await db.commit()
        unlocked = await prereq.recompute_downstream(db, user_id, lesson_id)
    else:
        if prog.state in (LessonState.AVAILABLE, LessonState.PREVIEWABLE, LessonState.LOCKED):
            prog.state = LessonState.IN_PROGRESS
        await db.commit()

    # Kỹ năng lệch: điểm tổng đạt nhưng một kỹ năng còn dưới ngưỡng riêng của bài.
    yeu = prereq.skills_below_threshold(scores, lesson)
    canh_bao = ""
    if yeu:
        ten = {"speak": "Nói", "listen": "Nghe", "read": "Đọc", "write": "Viết", "quiz": "Từ vựng"}
        chi_tiet = ", ".join(f"{ten.get(k, k)} {d:.0f}/{n}" for k, d, n in yeu)
        canh_bao = (
            f"Bạn qua bài này, nhưng còn lệch: {chi_tiet}. "
            f"Nên quay lại luyện thêm phần {ten.get(yeu[0][0], yeu[0][0])} trước khi đi tiếp."
        )

    return {
        "mastery_raw": raw,
        "state": prog.state,
        "threshold": lesson.mastery_threshold,
        "speaking_attempts": speaking_attempts,
        "unlocked_codes": unlocked,
        "skill_warning_vi": canh_bao,
    }


async def lesson_cards(db: AsyncSession, user_id: uuid.UUID, phase: str | None = None) -> list[dict]:
    stmt = select(Lesson).where(Lesson.status == ContentStatus.PUBLISHED)
    if phase:
        stmt = stmt.where(Lesson.phase == phase)
    lessons = (await db.execute(stmt.order_by(Lesson.phase, Lesson.order_index))).scalars().all()

    progress = {
        p.lesson_id: p
        for p in (
            await db.execute(select(LessonProgress).where(LessonProgress.user_id == user_id))
        ).scalars().all()
    }
    edges: dict[uuid.UUID, list[Prerequisite]] = {}
    for edge in (await db.execute(select(Prerequisite))).scalars().all():
        edges.setdefault(edge.lesson_id, []).append(edge)

    health = await prereq.retention_health(db, user_id)
    cards = []
    for lesson in lessons:
        result = await prereq.evaluate_lesson_state(
            db, user_id, lesson, edges.get(lesson.id, []), progress
        )
        prog = progress.get(lesson.id)
        raw = prog.mastery_raw if prog else 0.0
        eff = prereq.effective_mastery(raw, prog.last_activity_at if prog else None)
        level, msg = result["warning_level"], result["warning_vi"]
        # `debt` là cảnh báo duy nhất chặn được người đang có available.
        if health < 0.70 and result["state"] == LessonState.AVAILABLE:
            level = "debt"
            msg = f"Sức khoẻ ghi nhớ {health:.0%}. Ôn 5 phút trước khi học bài mới."
        cards.append({
            "lesson_id": lesson.id, "code": lesson.code, "title_vi": lesson.title_vi,
            "phase": lesson.phase, "est_minutes": lesson.est_minutes,
            "state": result["state"], "mastery_raw": round(raw, 1),
            "mastery_effective": round(eff, 1), "threshold": lesson.mastery_threshold,
            "warning_level": level, "warning_vi": msg,
            "blocking_lesson_code": result["blocking"],
            "is_checkpoint": lesson.is_checkpoint,
            "objective_vi": lesson.objective_vi,
            "skills": skills_for_phase(lesson.phase),
        })
    return cards


async def next_up(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Hàng đợi ưu tiên PART L. Lấy mục đầu tiên khớp."""
    # 1. nợ ôn tập nghiêm trọng
    health = await prereq.retention_health(db, user_id)
    if health < 0.70:
        return {
            "lesson_id": None, "code": None, "title_vi": "Buổi ôn 5 phút", "kind": "review",
            "reason_vi": (
                f"Sức khoẻ ghi nhớ của bạn còn {health:.0%}. "
                "5 phút ôn giờ tiết kiệm 20 phút học lại sau."
            ),
        }

    # 2. bài đang dở trong 72 giờ
    cutoff = utcnow() - timedelta(hours=72)
    stmt = (
        select(LessonProgress)
        .where(
            LessonProgress.user_id == user_id,
            LessonProgress.state == LessonState.IN_PROGRESS,
            LessonProgress.last_activity_at >= cutoff,
        )
        .order_by(LessonProgress.last_activity_at.desc())
    )
    prog = (await db.execute(stmt)).scalars().first()
    if prog:
        lesson = await db.get(Lesson, prog.lesson_id)
        remaining = await _remaining_activities(db, user_id, lesson.id)
        return {
            "lesson_id": lesson.id, "code": lesson.code, "title_vi": lesson.title_vi,
            "kind": "continue",
            "reason_vi": f"Bạn đang học dở bài này, còn {remaining} hoạt động nữa là xong.",
        }

    # 3. ôn tập đến hạn (>=5 mục quá hạn)
    due = (
        await db.execute(
            select(func.count(ReviewQueue.id)).where(
                ReviewQueue.user_id == user_id, ReviewQueue.due_at <= utcnow()
            )
        )
    ).scalar_one()
    if due >= 5:
        return {
            "lesson_id": None, "code": None, "title_vi": "Ôn tập nhanh", "kind": "review",
            "reason_vi": (
                f"{due} từ bạn học tuần trước sắp trôi. "
                "5 phút ôn giờ tiết kiệm 20 phút học lại sau."
            ),
        }

    cards = await lesson_cards(db, user_id)
    open_cards = [c for c in cards if c["state"] == LessonState.AVAILABLE]

    # 4. checkpoint đang chờ
    for card in open_cards:
        lesson = await db.get(Lesson, card["lesson_id"])
        if lesson and lesson.is_checkpoint:
            return {
                "lesson_id": lesson.id, "code": lesson.code, "title_vi": lesson.title_vi,
                "kind": "checkpoint",
                "reason_vi": (
                    f"Bạn đã xong hết bài của phase này. Vượt “{lesson.title_vi}” "
                    "là mở được phase tiếp theo."
                ),
            }

    if not open_cards:
        return {"lesson_id": None, "code": None, "title_vi": None, "kind": "done",
                "reason_vi": "Bạn đã mở hết nội dung hiện có. Nội dung mới đang được soạn."}

    # 5/6. bài kế trong phase, ưu tiên nhánh học ít nhất -> tránh học lệch chủ đề
    by_topic: dict[str, list[dict]] = {}
    for card in open_cards:
        lesson = await db.get(Lesson, card["lesson_id"])
        by_topic.setdefault(lesson.topic, []).append(card)

    mastered_by_topic = {}
    for topic in by_topic:
        cnt = 0
        for card in cards:
            lesson = await db.get(Lesson, card["lesson_id"])
            if lesson.topic == topic and card["state"] == LessonState.MASTERED:
                cnt += 1
        mastered_by_topic[topic] = cnt

    if len(by_topic) > 1:
        weakest = min(mastered_by_topic, key=mastered_by_topic.get)
        card = sorted(by_topic[weakest], key=lambda c: c["code"])[0]
        strongest = max(mastered_by_topic, key=mastered_by_topic.get)
        if mastered_by_topic[strongest] - mastered_by_topic[weakest] >= 3:
            return {
                "lesson_id": card["lesson_id"], "code": card["code"],
                "title_vi": card["title_vi"], "kind": "branch",
                "reason_vi": (
                    f"Bạn đã học {mastered_by_topic[strongest]} bài chủ đề khác "
                    f"nhưng chưa bài nào về “{weakest}”. Học lệch một chủ đề "
                    "sẽ hụt khi tình huống thật xảy ra."
                ),
            }

    card = sorted(open_cards, key=lambda c: c["code"])[0]
    reason = await _reason_from_last_struggle(db, user_id, card)
    return {
        "lesson_id": card["lesson_id"], "code": card["code"], "title_vi": card["title_vi"],
        "kind": "new", "reason_vi": reason,
    }


async def _remaining_activities(db: AsyncSession, user_id: uuid.UUID, lesson_id: uuid.UUID) -> int:
    total = (
        await db.execute(
            select(func.count(Activity.id)).where(Activity.lesson_id == lesson_id)
        )
    ).scalar_one()
    done = (
        await db.execute(
            select(func.count(func.distinct(Item.activity_id)))
            .select_from(ItemAttempt)
            .join(Item, Item.id == ItemAttempt.item_id)
            .where(ItemAttempt.user_id == user_id, ItemAttempt.lesson_id == lesson_id)
        )
    ).scalar_one()
    return max(0, total - done)


async def _reason_from_last_struggle(db: AsyncSession, user_id: uuid.UUID, card: dict) -> str:
    """why-this-next phải nêu lý do RIÊNG của người đó. "Bài tiếp theo trong lộ trình"
    không phải lý do — đó là nói lại thứ họ đã nhìn thấy."""
    lesson = await db.get(Lesson, card["lesson_id"])
    stmt = (
        select(ItemAttempt)
        .where(ItemAttempt.user_id == user_id, ItemAttempt.score < 70)
        .order_by(ItemAttempt.created_at.desc())
        .limit(8)
    )
    weak = (await db.execute(stmt)).scalars().all()
    focus = set()
    for att in weak:
        item = await db.get(Item, att.item_id)
        if item:
            focus.update(item.focus_phonemes or [])
    # Lấy focus_phonemes của bài qua JOIN, KHÔNG đi qua quan hệ lazy (vỡ trong async).
    lesson_focus: set = set()
    rows = (
        await db.execute(
            select(Item.focus_phonemes)
            .join(Activity, Activity.id == Item.activity_id)
            .where(Activity.lesson_id == lesson.id)
        )
    ).scalars().all()
    for fp in rows:
        lesson_focus.update(fp or [])
    overlap = focus & lesson_focus
    if overlap:
        sounds = ", ".join(f"/{p}/" for p in sorted(overlap)[:2])
        return (
            f"Bài này dạy âm {sounds} — đúng âm bạn còn sai ở "
            f"{len(weak)} câu gần đây."
        )
    return (
        f"Bài này mất khoảng {lesson.est_minutes} phút và mở ra "
        f"{await _downstream_count(db, lesson.id)} bài tiếp theo."
    )


async def _downstream_count(db: AsyncSession, lesson_id: uuid.UUID) -> int:
    return (
        await db.execute(
            select(func.count(Prerequisite.id)).where(
                Prerequisite.requires_lesson_id == lesson_id
            )
        )
    ).scalar_one()


async def schedule_reviews(db: AsyncSession, user_id: uuid.UUID, item_ids: list[uuid.UUID]) -> None:
    """SM-2 rút gọn: đúng -> giãn, sai -> về 1 ngày."""
    for item_id in item_ids:
        row = (
            await db.execute(
                select(ReviewQueue).where(
                    ReviewQueue.user_id == user_id, ReviewQueue.item_id == item_id
                )
            )
        ).scalar_one_or_none()
        if row is None:
            db.add(
                ReviewQueue(user_id=user_id, item_id=item_id, due_at=utcnow() + timedelta(days=1))
            )
        else:
            row.interval_days = min(60, max(1, round(row.interval_days * row.ease)))
            row.due_at = utcnow() + timedelta(days=row.interval_days)
    await db.commit()
