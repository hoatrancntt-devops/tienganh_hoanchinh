from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.db.session import get_session
from app.services import mail_service
from app.services.ai import router as ai_router

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Liveness: nhẹ, không đụng DB — dùng cho healthcheck của container."""
    return {"status": "ok", "version": __version__}


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_session)):
    """Readiness: có DB. Mail/AI chưa cấu hình KHÔNG làm app unready — app vẫn dạy được."""
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "mail_configured": await mail_service.is_configured(db) if db_ok else False,
        "ai_enabled": await ai_router.ai_enabled(db) if db_ok else False,
    }
