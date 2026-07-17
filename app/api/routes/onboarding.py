from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["onboarding"])


class OnboardIn(BaseModel):
    goal: str = Field(pattern="^(speaking|reading)$")
    daily_goal_minutes: int = Field(ge=5, le=60)
    job_role: str = ""


@router.put("/onboarding")
async def save_onboarding(
    payload: OnboardIn,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """Không set onboarded_at ở đây — placement mới là thứ kết thúc onboarding."""
    await db.refresh(user, ["profile"])
    profile = user.profile
    profile.goal = payload.goal
    profile.daily_goal_minutes = payload.daily_goal_minutes
    if payload.job_role:
        profile.job_role = payload.job_role[:80]
    await db.commit()
    return {"goal": profile.goal, "daily_goal_minutes": profile.daily_goal_minutes}
