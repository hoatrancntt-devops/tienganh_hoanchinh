"""Ghép router + fallback. Đây là API mà routes gọi — routes không biết provider tồn tại."""
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Item, Lesson
from app.services.ai import fallback
from app.services.ai.router import AIUnavailable, complete
from app.services.ai.tasks import EXPLAIN, OPEN_FEEDBACK, SENTENCE_REPAIR

log = logging.getLogger(__name__)


async def explain(
    db: AsyncSession, question: str, lesson: Lesson | None, user_id: uuid.UUID | None
) -> dict:
    context = ""
    if lesson:
        # Chỉ kèm ngữ cảnh bài, KHÔNG kèm cả lịch sử: prompt ngắn là tiết kiệm lớn nhất.
        context = (
            f"Bài đang học: {lesson.title_vi} ({lesson.code}). "
            f"Mục tiêu: {lesson.objective_vi}. "
        )
    try:
        resp = await complete(
            db, EXPLAIN, context + "Câu hỏi của học viên: " + question,
            user_id=user_id, scope_id=lesson.code if lesson else "global",
        )
        return {
            "answer_vi": resp.text, "source": "cache" if resp.from_cache else "ai",
            "provider": resp.provider, "model": resp.model, "degraded": False,
        }
    except AIUnavailable as exc:
        log.info("explain fallback: %s", exc)
        return {
            "answer_vi": fallback.static_explanation(lesson, question),
            "source": "fallback", "degraded": True,
        }


async def sentence_repair(
    db: AsyncSession, item: Item, said: str, user_id: uuid.UUID | None
) -> dict:
    prompt = (
        f"Câu đích: {item.expected_text or '(câu trả lời mở)'}\n"
        f"Học viên nói: {said}"
    )
    try:
        resp = await complete(
            db, SENTENCE_REPAIR, prompt, user_id=user_id, scope_id=str(item.id)
        )
        return {"answer_vi": resp.text, "source": "cache" if resp.from_cache else "ai",
                "provider": resp.provider, "model": resp.model, "degraded": False}
    except AIUnavailable:
        return {"answer_vi": fallback.sentence_repair(item, said),
                "source": "fallback", "degraded": True}


async def open_feedback(
    db: AsyncSession, item: Item, said: str, user_id: uuid.UUID | None
) -> dict:
    prompt = f"Câu hỏi: {item.prompt_en}\nHọc viên trả lời: {said}"
    try:
        resp = await complete(
            db, OPEN_FEEDBACK, prompt, user_id=user_id, scope_id=str(item.id)
        )
        return {"answer_vi": resp.text, "source": "ai", "provider": resp.provider,
                "model": resp.model, "degraded": False}
    except AIUnavailable:
        return {"answer_vi": fallback.open_feedback(item, said),
                "source": "fallback", "degraded": True}
