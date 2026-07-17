from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_ip, current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import LoginIn, ProfileOut, RegisterIn, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
_settings = get_settings()


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        _settings.SESSION_COOKIE, token,
        httponly=True, samesite="lax",
        secure=_settings.APP_ENV == "prod",  # prod bắt buộc HTTPS: micro không chạy trên HTTP thuần
        max_age=_settings.SESSION_TTL_HOURS * 3600, path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterIn, request: Request, response: Response,
    db: AsyncSession = Depends(get_session),
):
    try:
        user = await auth_service.register(
            db, payload.email, payload.password, payload.full_name,
            payload.goal, payload.daily_goal_minutes,
        )
    except auth_service.AuthError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    token = await auth_service.create_session(
        db, user, request.headers.get("user-agent", ""), client_ip(request)
    )
    _set_cookie(response, token)
    return user


@router.post("/login", response_model=UserOut)
async def login(
    payload: LoginIn, request: Request, response: Response,
    db: AsyncSession = Depends(get_session),
):
    try:
        user = await auth_service.authenticate(db, payload.email, payload.password)
    except auth_service.AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    token = await auth_service.create_session(
        db, user, request.headers.get("user-agent", ""), client_ip(request)
    )
    _set_cookie(response, token)
    return user


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_session)):
    token = request.cookies.get(_settings.SESSION_COOKIE, "")
    if token:
        await auth_service.revoke_session(db, token)
    response.delete_cookie(_settings.SESSION_COOKIE, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return user


@router.get("/me/profile", response_model=ProfileOut)
async def my_profile(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    await db.refresh(user, ["profile"])
    if user.profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có hồ sơ.")
    return user.profile
