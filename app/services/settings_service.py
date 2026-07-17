"""Cấu hình runtime do admin sửa trên web. Ưu tiên DB, fallback env.

Secret luôn mã hoá trước khi ghi và chỉ giải mã trong process, không bao giờ trả nguyên văn ra API.
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt, encrypt, mask
from app.models.ops import AppSetting

log = logging.getLogger(__name__)

# Cache tiến trình: settings đọc ở mọi request AI/mail, query mỗi lần là phí.
_cache: dict[str, str] = {}
_loaded = False

SECRET_KEYS = {
    "mail.m365.client_secret",
    "mail.smtp.password",
    "ai.provider.anthropic.api_key",
    "ai.provider.openai.api_key",
    "ai.provider.gemini.api_key",
    "ai.provider.openrouter.api_key",
    "ai.provider.azure_openai.api_key",
    "ai.provider.ollama.api_key",
}


async def load_all(db: AsyncSession) -> dict[str, str]:
    global _loaded
    rows = (await db.execute(select(AppSetting))).scalars().all()
    _cache.clear()
    for row in rows:
        _cache[row.key] = decrypt(row.value) if row.is_secret else row.value
    _loaded = True
    return dict(_cache)


async def get(db: AsyncSession, key: str, default: str = "") -> str:
    if not _loaded:
        await load_all(db)
    return _cache.get(key) or default


async def get_bool(db: AsyncSession, key: str, default: bool = False) -> bool:
    raw = await get(db, key, "")
    return raw.lower() in {"1", "true", "yes", "on"} if raw else default


async def get_int(db: AsyncSession, key: str, default: int = 0) -> int:
    raw = await get(db, key, "")
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


async def get_float(db: AsyncSession, key: str, default: float = 0.0) -> float:
    raw = await get(db, key, "")
    try:
        return float(raw) if raw else default
    except ValueError:
        return default


async def get_masked(db: AsyncSession, key: str) -> str:
    return mask(await get(db, key, ""))


async def set_value(db: AsyncSession, key: str, value: str, actor_id=None) -> None:
    """Không commit — caller quyết định ranh giới transaction."""
    is_secret = key in SECRET_KEYS
    stored = encrypt(value) if (is_secret and value) else value
    row = (await db.execute(select(AppSetting).where(AppSetting.key == key))).scalar_one_or_none()
    if row is None:
        db.add(AppSetting(key=key, value=stored, is_secret=is_secret, updated_by=actor_id))
    else:
        row.value = stored
        row.is_secret = is_secret
        row.updated_by = actor_id
    _cache[key] = value


async def set_many(db: AsyncSession, pairs: dict[str, str], actor_id=None) -> None:
    for key, value in pairs.items():
        await set_value(db, key, value, actor_id)


def invalidate() -> None:
    global _loaded
    _loaded = False
    _cache.clear()
