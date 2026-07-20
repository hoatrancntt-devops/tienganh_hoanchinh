from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_session
from app.models.user import User
from app.services import notification_service as notif
from app.services import roleplay_service

router = APIRouter(prefix="/api/v1/roleplay", tags=["roleplay"])


@router.get("")
async def list_roleplay(_: User = Depends(current_user)):
    return {"scenarios": roleplay_service.list_scenarios()}


@router.get("/{rid}")
async def get_roleplay(rid: str, _: User = Depends(current_user)):
    scenario = roleplay_service.get_scenario(rid)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy kịch bản.")
    return scenario


@router.post("/{rid}/complete")
async def complete_roleplay(
    rid: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_session)
):
    """Hoàn thành một lượt đóng vai — tính vào streak học tập."""
    if roleplay_service.get_scenario(rid) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy kịch bản.")
    await db.refresh(user, ["profile"])
    await notif.record_study(db, user)
    return {"ok": True}
