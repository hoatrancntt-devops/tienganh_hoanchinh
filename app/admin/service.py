"""Logic đọc/ghi cấu hình admin. Route chỉ điều phối, không chứa luật."""
import uuid
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import mask
from app.db.base import utcnow
from app.models.ops import AIUsage, AuditLog
from app.services import settings_service as cfg
from app.services.ai import router as ai_router
from app.services.ai.providers import REGISTRY

PROVIDERS = list(REGISTRY.keys())


async def audit(db: AsyncSession, actor_id: uuid.UUID, action: str, diff: dict, ip: str = "") -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity_type="app_settings",
                    diff=diff, ip=ip))
    await db.commit()


# ---------- mail ----------

async def read_mail_settings(db: AsyncSession) -> dict:
    from app.services import mail_service

    return {
        "provider": await cfg.get(db, "mail.provider", "none"),
        "sender": await cfg.get(db, "mail.sender"),
        "m365_tenant_id": await cfg.get(db, "mail.m365.tenant_id"),
        "m365_client_id": await cfg.get(db, "mail.m365.client_id"),
        "m365_client_secret_masked": mask(await cfg.get(db, "mail.m365.client_secret")),
        "smtp_host": await cfg.get(db, "mail.smtp.host"),
        "smtp_port": await cfg.get_int(db, "mail.smtp.port", 587),
        "smtp_username": await cfg.get(db, "mail.smtp.username"),
        "smtp_password_masked": mask(await cfg.get(db, "mail.smtp.password")),
        "smtp_use_tls": await cfg.get_bool(db, "mail.smtp.use_tls", True),
        "configured": await mail_service.is_configured(db),
    }


async def write_mail_settings(db: AsyncSession, payload, actor_id: uuid.UUID) -> None:
    pairs = {
        "mail.provider": payload.provider,
        "mail.sender": str(payload.sender or ""),
        "mail.m365.tenant_id": payload.m365_tenant_id,
        "mail.m365.client_id": payload.m365_client_id,
        "mail.smtp.host": payload.smtp_host,
        "mail.smtp.port": str(payload.smtp_port),
        "mail.smtp.username": payload.smtp_username,
        "mail.smtp.use_tls": "true" if payload.smtp_use_tls else "false",
    }
    # Secret để trống = giữ giá trị cũ. Nếu không, mỗi lần lưu form là xoá mất key.
    if payload.m365_client_secret:
        pairs["mail.m365.client_secret"] = payload.m365_client_secret
    if payload.smtp_password:
        pairs["mail.smtp.password"] = payload.smtp_password
    await cfg.set_many(db, pairs, actor_id)
    await db.commit()
    await audit(db, actor_id, "update_mail_settings",
                {"provider": payload.provider, "sender": str(payload.sender or "")})


# ---------- ai ----------

async def read_ai_settings(db: AsyncSession) -> dict:
    from app.core.config import get_settings

    s = get_settings()
    providers = []
    for name in PROVIDERS:
        key = await cfg.get(db, f"ai.provider.{name}.api_key")
        providers.append({
            "provider": name,
            "api_key_masked": mask(key),
            "base_url": await cfg.get(db, f"ai.provider.{name}.base_url"),
            "enabled": await cfg.get_bool(db, f"ai.provider.{name}.enabled", True),
            "has_key": bool(key) or name == "ollama",
        })
    budget = await ai_router.budget_state(db)
    return {
        "ai_enabled": await cfg.get_bool(db, "ai.enabled", True),
        "route_t1": await cfg.get(db, "ai.route.t1", s.LLM_ROUTE_T1),
        "route_t2": await cfg.get(db, "ai.route.t2", s.LLM_ROUTE_T2),
        "user_daily_calls": await cfg.get_int(db, "ai.user_daily_calls", s.AI_USER_DAILY_CALLS),
        "global_monthly_usd": budget["cap"],
        "spent_this_month_usd": budget["spent"],
        "providers": providers,
    }


async def write_ai_settings(db: AsyncSession, payload, actor_id: uuid.UUID) -> None:
    pairs = {
        "ai.enabled": "true" if payload.ai_enabled else "false",
        "ai.route.t1": payload.route_t1,
        "ai.route.t2": payload.route_t2,
        "ai.user_daily_calls": str(payload.user_daily_calls),
        "ai.global_monthly_usd": str(payload.global_monthly_usd),
    }
    changed = []
    for prov in payload.providers:
        pairs[f"ai.provider.{prov.provider}.base_url"] = prov.base_url
        pairs[f"ai.provider.{prov.provider}.enabled"] = "true" if prov.enabled else "false"
        if prov.api_key:
            pairs[f"ai.provider.{prov.provider}.api_key"] = prov.api_key
            changed.append(prov.provider)
    await cfg.set_many(db, pairs, actor_id)
    await db.commit()
    # Audit ghi TÊN provider đổi key, không bao giờ ghi giá trị key.
    await audit(db, actor_id, "update_ai_settings",
                {"routes": [payload.route_t1, payload.route_t2], "keys_changed": changed})


# ---------- dashboard ----------

async def ai_cost_report(db: AsyncSession, days: int = 30) -> dict:
    since = utcnow() - timedelta(days=days)
    by_task = (
        await db.execute(
            select(AIUsage.task_name, func.sum(AIUsage.cost_usd), func.count(AIUsage.id))
            .where(AIUsage.created_at >= since)
            .group_by(AIUsage.task_name)
        )
    ).all()
    saved = (
        await db.execute(
            select(func.coalesce(func.sum(AIUsage.tokens_saved), 0)).where(
                AIUsage.created_at >= since
            )
        )
    ).scalar_one()
    hits = (
        await db.execute(
            select(func.count(AIUsage.id)).where(
                AIUsage.created_at >= since, AIUsage.cache_hit.is_(True)
            )
        )
    ).scalar_one()
    total = (
        await db.execute(select(func.count(AIUsage.id)).where(AIUsage.created_at >= since))
    ).scalar_one()
    return {
        "by_task": [{"task": t, "cost_usd": round(c or 0, 4), "calls": n} for t, c, n in by_task],
        "tokens_saved": saved,          # con số này biện minh cho công sức làm cache
        "cache_hit_rate": round(hits / total, 3) if total else 0.0,
        "total_calls": total,
    }
