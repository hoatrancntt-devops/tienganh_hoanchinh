"""Đăng ký, đăng nhập, session cookie phía server."""
import hashlib
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password, needs_rehash, new_session_token, verify_password
from app.db.base import utcnow
from app.models.enums import Role
from app.models.user import Session, User, UserProfile

log = logging.getLogger(__name__)
_settings = get_settings()


class AuthError(Exception):
    pass


def _hash_token(token: str) -> str:
    """Lưu hash thay vì token: DB rò rỉ không kéo theo chiếm phiên."""
    return hashlib.sha256(token.encode()).hexdigest()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email.lower().strip())
    return (await db.execute(stmt)).scalar_one_or_none()


async def register(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str = "",
    goal: str = "speaking",
    daily_goal_minutes: int = 10,
    role: str = Role.LEARNER,
) -> User:
    email = email.lower().strip()
    if await get_by_email(db, email):
        raise AuthError("Email này đã được đăng ký.")
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        timezone=_settings.DEFAULT_TZ,
    )
    db.add(user)
    await db.flush()
    db.add(
        UserProfile(user_id=user.id, goal=goal, daily_goal_minutes=daily_goal_minutes)
    )
    await db.commit()
    await db.refresh(user)
    log.info("user registered: %s", email)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await get_by_email(db, email)
    # Luôn chạy verify kể cả khi user không tồn tại: chống dò email qua thời gian phản hồi.
    reference = user.password_hash if user else hash_password("dummy-timing-guard")
    ok = verify_password(password, reference)
    if not user or not ok:
        raise AuthError("Email hoặc mật khẩu không đúng.")
    if not user.is_active:
        raise AuthError("Tài khoản đã bị khoá.")
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    user.last_login_at = utcnow()
    await db.commit()
    return user


async def create_session(db: AsyncSession, user: User, ua: str = "", ip: str = "") -> str:
    token = new_session_token()
    db.add(
        Session(
            user_id=user.id,
            token_hash=_hash_token(token),
            expires_at=utcnow() + timedelta(hours=_settings.SESSION_TTL_HOURS),
            user_agent=ua[:255],
            ip=ip[:64],
        )
    )
    await db.commit()
    return token


async def resolve_session(db: AsyncSession, token: str) -> User | None:
    if not token:
        return None
    stmt = select(Session).where(Session.token_hash == _hash_token(token))
    sess = (await db.execute(stmt)).scalar_one_or_none()
    if not sess or sess.revoked_at:
        return None
    expires = sess.expires_at
    if expires.tzinfo is None:  # SQLite trả naive
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        return None
    user = await db.get(User, sess.user_id)
    return user if user and user.is_active else None


async def revoke_session(db: AsyncSession, token: str) -> None:
    stmt = select(Session).where(Session.token_hash == _hash_token(token))
    sess = (await db.execute(stmt)).scalar_one_or_none()
    if sess:
        sess.revoked_at = utcnow()
        await db.commit()


async def change_password(db: AsyncSession, user: User, old: str, new: str) -> None:
    if not verify_password(old, user.password_hash):
        raise AuthError("Mật khẩu hiện tại không đúng.")
    if len(new) < 8:
        raise AuthError("Mật khẩu mới cần ít nhất 8 ký tự.")
    user.password_hash = hash_password(new)
    await db.commit()


async def ensure_admin(db: AsyncSession, email: str | None, password: str | None) -> User | None:
    """Bootstrap admin từ env. Không tạo nếu env trống — không có mật khẩu mặc định."""
    if not email or not password:
        log.warning("ADMIN_EMAIL/ADMIN_PASSWORD chưa đặt, bỏ qua bootstrap admin")
        return None
    existing = await get_by_email(db, email)
    if existing:
        if existing.role != Role.ADMIN:
            existing.role = Role.ADMIN
            await db.commit()
        return existing
    user = await register(db, email, password, full_name="Administrator", role=Role.ADMIN)
    log.info("admin bootstrapped: %s", email)
    return user


async def purge_expired_sessions(db: AsyncSession) -> int:
    from sqlalchemy import delete

    res = await db.execute(delete(Session).where(Session.expires_at < utcnow()))
    await db.commit()
    return res.rowcount or 0
