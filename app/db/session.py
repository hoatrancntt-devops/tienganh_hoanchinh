import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base

log = logging.getLogger(__name__)
_settings = get_settings()

_engine_kwargs: dict = {"echo": _settings.DB_ECHO, "future": True}
if not _settings.is_sqlite:
    # 8GB RAM: pool nhỏ, recycle để không giữ connection chết qua đêm.
    _engine_kwargs.update(pool_size=5, max_overflow=5, pool_pre_ping=True, pool_recycle=1800)

engine = create_async_engine(_settings.DATABASE_URL, **_engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Dev/test: tạo bảng trực tiếp. Prod dùng Alembic."""
    import app.models  # noqa: F401  - đăng ký mapper

    async with engine.begin() as conn:
        if _settings.is_sqlite:
            from sqlalchemy import text

            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
    log.info("database ready")
