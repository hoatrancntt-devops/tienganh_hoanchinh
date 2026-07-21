"""Anti-skip / prerequisite engine (PART L).

Luật cốt lõi, không phần nào là placeholder:
  - DAG có validate chu trình lúc GHI, không phải lúc chạy.
  - mastery hiệu dụng suy giảm 1%/ngày, sàn 60%.
  - hard chặn, soft chỉ cảnh báo.
  - đã mở là mở vĩnh viễn: needs_review không khoá lại bài phía sau.
"""
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utcnow
from app.models.content import Lesson, Prerequisite
from app.models.enums import LessonState, PrereqKind
from app.models.progress import LessonProgress

log = logging.getLogger(__name__)

DECAY_PER_DAY = 0.01
DECAY_FLOOR = 0.60
PREVIEW_RATIO = 0.60  # đạt >=60% mức yêu cầu của cạnh hard cuối cùng -> cho xem trước


class CycleError(Exception):
    pass


# ---------- mastery ----------

def effective_mastery(raw: float, last_activity_at: datetime | None) -> float:
    """Suy giảm theo ngày không luyện. Dùng cho cạnh tiên quyết; hiển thị vẫn dùng raw."""
    if raw <= 0 or last_activity_at is None:
        return raw
    ts = last_activity_at
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    days = max(0, (datetime.now(timezone.utc) - ts).days)
    return raw * max(DECAY_FLOOR, 1 - DECAY_PER_DAY * days)


def compute_mastery_raw(scores_by_kind: dict[str, float], lesson: Lesson) -> float:
    """scores_by_kind: trung bình 3 lần thử gần nhất mỗi kind, thang 0-100."""
    weights: dict = lesson.mastery_weights or {"speak": 0.5, "quiz": 0.3, "listen": 0.2}
    total_w = sum(weights.values()) or 1.0
    score = sum(scores_by_kind.get(k, 0.0) * w for k, w in weights.items()) / total_w
    return round(min(100.0, max(0.0, score)), 2)


def skills_below_threshold(scores_by_kind: dict[str, float], lesson: Lesson) -> list[tuple[str, float, int]]:
    """Các kỹ năng chưa đạt ngưỡng riêng của bài. Trả (kỹ năng, điểm đang có, ngưỡng cần).

    Điểm tổng có thể che một kỹ năng yếu: đọc 90 kéo nói 40 lên vẫn qua ngưỡng chung, và
    tuyên bố đầu ra của level thành lời hứa suông. Chỉ checkpoint mới khai `min_per_skill`.

    CẢNH BÁO chứ không chặn: với người mất gốc, thêm một cổng chặn cứng là thêm một chỗ
    bỏ cuộc. Học viên vẫn qua bài, nhưng được chỉ đúng kỹ năng cần quay lại.
    """
    can = lesson.min_per_skill or {}
    thieu = []
    for ky_nang, nguong in can.items():
        diem = scores_by_kind.get(ky_nang)
        if diem is not None and diem < nguong:
            thieu.append((ky_nang, round(diem, 1), nguong))
    return sorted(thieu, key=lambda x: x[1])


def apply_speaking_gate(raw: float, speaking_attempts: int, lesson: Lesson) -> float:
    """Chốt chặn chống lách: quiz giỏi + bỏ phần nói không được vượt ngưỡng."""
    if lesson.min_speaking_attempts > 0 and speaking_attempts < lesson.min_speaking_attempts:
        return min(raw, float(lesson.mastery_threshold - 1))
    return raw


# ---------- DAG ----------

async def _load_edges(db: AsyncSession) -> dict[uuid.UUID, list[Prerequisite]]:
    rows = (await db.execute(select(Prerequisite))).scalars().all()
    edges: dict[uuid.UUID, list[Prerequisite]] = defaultdict(list)
    for edge in rows:
        edges[edge.lesson_id].append(edge)
    return edges


async def validate_no_cycle(
    db: AsyncSession, new_lesson_id: uuid.UUID, new_requires_id: uuid.UUID
) -> None:
    """Gọi TRƯỚC khi thêm cạnh. Cạnh mới hợp lệ khi requires không tới được lesson."""
    if new_lesson_id == new_requires_id:
        raise CycleError("Một bài không thể là tiên quyết của chính nó.")
    edges = await _load_edges(db)
    edges[new_lesson_id].append(
        Prerequisite(lesson_id=new_lesson_id, requires_lesson_id=new_requires_id)
    )
    color: dict[uuid.UUID, int] = {}

    def visit(node: uuid.UUID) -> None:
        color[node] = 1  # đang duyệt
        for edge in edges.get(node, []):
            nxt = edge.requires_lesson_id
            if color.get(nxt) == 1:
                raise CycleError("Cạnh này tạo vòng lặp trong lộ trình.")
            if color.get(nxt) is None:
                visit(nxt)
        color[node] = 2

    for node in list(edges.keys()):
        if color.get(node) is None:
            visit(node)


# ---------- unlock ----------

async def _progress_map(db: AsyncSession, user_id: uuid.UUID) -> dict[uuid.UUID, LessonProgress]:
    rows = (
        await db.execute(select(LessonProgress).where(LessonProgress.user_id == user_id))
    ).scalars().all()
    return {row.lesson_id: row for row in rows}


def _edge_satisfied(edge: Prerequisite, prog: LessonProgress | None) -> tuple[bool, float]:
    if prog is None:
        return False, 0.0
    eff = effective_mastery(prog.mastery_raw, prog.last_activity_at)
    return eff >= edge.min_mastery, eff


async def evaluate_lesson_state(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson: Lesson,
    edges: list[Prerequisite] | None = None,
    progress: dict[uuid.UUID, LessonProgress] | None = None,
) -> dict:
    """Trả về state + cảnh báo. Thứ tự đánh giá đúng PART L, dừng ở kết quả đầu tiên khớp."""
    if progress is None:
        progress = await _progress_map(db, user_id)
    if edges is None:
        all_edges = await _load_edges(db)
        edges = all_edges.get(lesson.id, [])

    prog = progress.get(lesson.id)

    # 1. đã mastered / in_progress -> giữ nguyên
    if prog and prog.state in (LessonState.MASTERED, LessonState.IN_PROGRESS,
                              LessonState.NEEDS_REVIEW):
        return {"state": prog.state, "warning_level": "none", "warning_vi": "",
                "blocking": None}

    # 2. admin override
    if prog and prog.admin_override:
        return {"state": LessonState.AVAILABLE, "warning_level": "info",
                "warning_vi": "Bài này được quản trị viên mở thủ công.", "blocking": None}

    hard_unmet: list[tuple[Prerequisite, float]] = []
    soft_unmet: list[tuple[Prerequisite, float]] = []
    for edge in edges:
        ok, eff = _edge_satisfied(edge, progress.get(edge.requires_lesson_id))
        if ok:
            continue
        (hard_unmet if edge.kind == PrereqKind.HARD else soft_unmet).append((edge, eff))

    # 3. còn cạnh hard chưa thoả -> locked, hoặc previewable nếu sắp tới nơi
    if hard_unmet:
        edge, eff = hard_unmet[0]
        blocker = await db.get(Lesson, edge.requires_lesson_id)
        code = blocker.code if blocker else "?"
        title = blocker.title_vi if blocker else "bài trước"
        gap = edge.min_mastery - eff
        msg = (
            f"Cần đạt {edge.min_mastery}% ở bài “{title}”, bạn đang {eff:.0f}% "
            f"— còn {gap:.0f}%, khoảng {max(1, round(gap / 10))} buổi."
        )
        if len(hard_unmet) == 1 and eff >= edge.min_mastery * PREVIEW_RATIO:
            return {"state": LessonState.PREVIEWABLE, "warning_level": "blocked",
                    "warning_vi": msg, "blocking": code}
        return {"state": LessonState.LOCKED, "warning_level": "blocked",
                "warning_vi": msg, "blocking": code}

    # 4. hard đã thoả -> available; soft chỉ gắn cảnh báo
    warning_level, warning_vi = "none", ""
    if soft_unmet:
        edge, eff = soft_unmet[0]
        blocker = await db.get(Lesson, edge.requires_lesson_id)
        title = blocker.title_vi if blocker else "bài liên quan"
        gap = edge.min_mastery - eff
        warning_level = "caution" if gap >= 15 else "info"
        warning_vi = (
            f"Bạn chưa vững bài “{title}” ({eff:.0f}%/{edge.min_mastery}%). "
            f"Vào bài này vẫn được, nhưng nên ôn 5 phút trước."
        )
    return {"state": LessonState.AVAILABLE, "warning_level": warning_level,
            "warning_vi": warning_vi, "blocking": None}


async def recompute_downstream(db: AsyncSession, user_id: uuid.UUID, lesson_id: uuid.UUID) -> list[str]:
    """Theo sự kiện, không quét toàn bộ: chỉ đánh giá lại các bài có cạnh trỏ tới lesson_id."""
    stmt = select(Prerequisite.lesson_id).where(Prerequisite.requires_lesson_id == lesson_id)
    dependent_ids = (await db.execute(stmt)).scalars().all()
    if not dependent_ids:
        return []

    progress = await _progress_map(db, user_id)
    all_edges = await _load_edges(db)
    unlocked: list[str] = []

    for dep_id in dependent_ids:
        lesson = await db.get(Lesson, dep_id)
        if not lesson:
            continue
        result = await evaluate_lesson_state(
            db, user_id, lesson, all_edges.get(dep_id, []), progress
        )
        prog = progress.get(dep_id)
        if prog is None:
            prog = LessonProgress(user_id=user_id, lesson_id=dep_id, state=result["state"])
            db.add(prog)
            progress[dep_id] = prog
        was_locked = prog.state in (LessonState.LOCKED, LessonState.PREVIEWABLE)
        # Đã mở là mở vĩnh viễn: không bao giờ hạ available -> locked.
        if prog.state in (LessonState.LOCKED, LessonState.PREVIEWABLE):
            prog.state = result["state"]
        if was_locked and prog.state == LessonState.AVAILABLE:
            unlocked.append(lesson.code)
    await db.commit()
    return unlocked


async def unlock_from_placement(
    db: AsyncSession, user_id: uuid.UUID, entry_lesson: Lesson
) -> None:
    """Xếp lớp CHỈ mở khoá, không bao giờ đánh dấu mastered.

    Nếu nó set mastered, chính placement test sẽ làm rỗng ruột engine chống nhảy cóc.
    """
    stmt = select(Lesson).where(
        Lesson.phase == entry_lesson.phase, Lesson.order_index <= entry_lesson.order_index
    )
    lessons = (await db.execute(stmt)).scalars().all()
    progress = await _progress_map(db, user_id)
    for lesson in lessons:
        prog = progress.get(lesson.id)
        if prog is None:
            db.add(
                LessonProgress(
                    user_id=user_id, lesson_id=lesson.id,
                    state=LessonState.AVAILABLE, unlocked_by="placement",
                )
            )
        elif prog.state == LessonState.LOCKED:
            prog.state = LessonState.AVAILABLE
            prog.unlocked_by = "placement"
    await db.commit()


async def grant_challenge_pass(
    db: AsyncSession, user_id: uuid.UUID, lesson: Lesson, score: float
) -> bool:
    """Thi vượt: ngưỡng cao hơn đường học thường (85), vì đó là đặc quyền."""
    if score < lesson.challenge_threshold:
        return False
    prog = (
        await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson.id
            )
        )
    ).scalar_one_or_none()
    if prog is None:
        prog = LessonProgress(user_id=user_id, lesson_id=lesson.id, mastery_raw=0.0)
        db.add(prog)
    prog.state = LessonState.MASTERED
    prog.mastery_raw = max(prog.mastery_raw or 0.0, score)
    prog.unlocked_by = "challenge"
    prog.last_activity_at = utcnow()
    prog.mastered_at = utcnow()
    await db.commit()
    await recompute_downstream(db, user_id, lesson.id)
    return True


async def retention_health(db: AsyncSession, user_id: uuid.UUID) -> float:
    """Tỷ lệ bài mastered chưa rơi khỏi ngưỡng. <70% -> chèn buổi ôn bắt buộc."""
    rows = (
        await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.state.in_([LessonState.MASTERED, LessonState.NEEDS_REVIEW]),
            )
        )
    ).scalars().all()
    if not rows:
        return 1.0
    healthy = 0
    for prog in rows:
        lesson = await db.get(Lesson, prog.lesson_id)
        threshold = lesson.mastery_threshold if lesson else 80
        if effective_mastery(prog.mastery_raw, prog.last_activity_at) >= threshold - 10:
            healthy += 1
    return healthy / len(rows)
