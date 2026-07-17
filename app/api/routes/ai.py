from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_session
from app.models.content import Lesson
from app.models.user import User
from app.schemas.ai import AskIn, AskOut
from app.services.ai import assistant
from app.services.ai import router as ai_router

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.get("/status")
async def status(db: AsyncSession = Depends(get_session)):
    """UI dùng cờ này để ẨN HẲN nút AI, không phải disable.
    Nút bấm không được là nhắc người ta về thứ họ không có."""
    return {"ai_enabled": await ai_router.ai_enabled(db)}


@router.post("/ask", response_model=AskOut)
async def ask(
    payload: AskIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_session)
):
    lesson = None
    if payload.lesson_id:
        lesson = await db.get(Lesson, payload.lesson_id)
    # sentence_repair / open_feedback cần item_id -> để message sau khi có speaking UI
    return await assistant.explain(db, payload.question, lesson, user.id)


@router.get("/budget")
async def budget(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    state = await ai_router.budget_state(db)
    return {"mode": state["mode"], "ratio": state["ratio"]}
