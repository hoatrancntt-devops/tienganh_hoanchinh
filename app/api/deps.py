"""Dependency dùng chung cho mọi route."""
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.services import auth_service

_settings = get_settings()


async def current_user_optional(
    request: Request, db: AsyncSession = Depends(get_session)
) -> User | None:
    token = request.cookies.get(_settings.SESSION_COOKIE, "")
    return await auth_service.resolve_session(db, token)


async def current_user(
    user: User | None = Depends(current_user_optional),
) -> User:
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bạn cần đăng nhập.")
    return user


async def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Chỉ quản trị viên truy cập được.")
    return user


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "")
