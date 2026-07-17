import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_session
from app.models.user import User
from app.services import notification_service as notif

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    limit: int = 20, user: User = Depends(current_user), db: AsyncSession = Depends(get_session)
):
    rows = await notif.list_recent(db, user.id, limit)
    return {
        "unread": await notif.unread_count(db, user.id),
        "items": [
            {"id": n.id, "type": n.type, "title_vi": n.title_vi, "body_vi": n.body_vi,
             "link": n.link, "read": n.read_at is not None, "created_at": n.created_at}
            for n in rows
        ],
    }


@router.get("/unread-count")
async def unread(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    return {"unread": await notif.unread_count(db, user.id)}


@router.post("/{notif_id}/read")
async def mark_one(
    notif_id: uuid.UUID, user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    return {"marked": await notif.mark_read(db, user.id, notif_id)}


@router.post("/read-all")
async def mark_all(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    return {"marked": await notif.mark_read(db, user.id)}


@router.put("/preferences")
async def update_prefs(
    reminder_hour: int | None = None,
    email_opt_in: bool | None = None,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    await db.refresh(user, ["profile"])
    profile = user.profile
    if reminder_hour is not None:
        profile.reminder_hour = max(6, min(22, reminder_hour))
    if email_opt_in is not None:
        profile.email_opt_in = email_opt_in
        if email_opt_in:
            profile.email_skip_count = 0  # bật lại = reset bộ đếm tự tắt
    await db.commit()
    return {"reminder_hour": profile.reminder_hour, "email_opt_in": profile.email_opt_in}
