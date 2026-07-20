from fastapi import APIRouter

from app.api.routes import (
    ai, auth, health, learning, notifications, onboarding, placement, roleplay, speech,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(placement.router)
api_router.include_router(learning.router)
api_router.include_router(speech.router)
api_router.include_router(roleplay.router)
api_router.include_router(notifications.router)
api_router.include_router(ai.router)

__all__ = ["api_router"]
