"""Router AI: cache -> provider chain -> hạ tier -> ollama -> rule-based.

Circuit breaker mỗi provider: không có nó, một provider chết sẽ khiến mọi request chờ
timeout và kéo sập trải nghiệm cả app.
"""
import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import timedelta
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import utcnow
from app.models.ops import AICache, AIUsage
from app.services import settings_service as cfg
from app.services.ai.base import LLMError, LLMRequest, LLMResponse, ProviderConfig
from app.services.ai.providers import REGISTRY
from app.services.ai.tasks import TaskSpec

log = logging.getLogger(__name__)
_settings = get_settings()

CB_THRESHOLD = 5     # 5 lỗi/60s -> mở
CB_WINDOW = 60
CB_OPEN_FOR = 300    # mở 5 phút
CACHE_TTL_DAYS = 30
PROVIDER_NAMES = list(REGISTRY.keys())

_breaker: dict[str, dict] = {}
_prices: dict | None = None


class AIUnavailable(Exception):
    """Không có provider nào dùng được. Caller phải rơi về fallback rule-based."""


# ---------- circuit breaker ----------

def _cb_allow(provider: str) -> bool:
    state = _breaker.get(provider)
    if not state:
        return True
    if state.get("open_until", 0) > time.monotonic():
        return False
    return True


def _cb_record(provider: str, ok: bool) -> None:
    state = _breaker.setdefault(provider, {"fails": [], "open_until": 0})
    now = time.monotonic()
    if ok:
        state["fails"].clear()
        state["open_until"] = 0
        return
    state["fails"] = [t for t in state["fails"] if now - t < CB_WINDOW]
    state["fails"].append(now)
    if len(state["fails"]) >= CB_THRESHOLD:
        state["open_until"] = now + CB_OPEN_FOR
        state["fails"].clear()
        log.warning("circuit breaker OPEN: %s", provider)


# ---------- giá ----------

def _load_prices() -> dict:
    """Giá nằm ngoài code: không đáng build lại image chỉ để sửa một con số."""
    global _prices
    if _prices is not None:
        return _prices
    path = Path(_settings.LLM_PRICES_PATH)
    if path.exists():
        try:
            _prices = json.loads(path.read_text(encoding="utf-8"))
            return _prices
        except json.JSONDecodeError:
            log.warning("llm_prices.json hỏng, dùng giá 0")
    _prices = {}
    return _prices


def _cost(provider: str, model: str, in_tok: int, out_tok: int) -> float:
    entry = _load_prices().get(f"{provider}:{model}") or _load_prices().get(provider) or {}
    return round(
        in_tok / 1_000_000 * entry.get("input_per_mtok", 0.0)
        + out_tok / 1_000_000 * entry.get("output_per_mtok", 0.0),
        6,
    )


# ---------- cache ----------

def _cache_key(spec: TaskSpec, scope_id: str, payload: str) -> str:
    normalized = " ".join(payload.lower().split())
    raw = f"{spec.prompt_version}|{scope_id}|{normalized}"
    return hashlib.sha256(raw.encode()).hexdigest()[:64]


async def _cache_get(db: AsyncSession, key: str) -> dict | None:
    row = (
        await db.execute(
            select(AICache).where(AICache.cache_key == key, AICache.expires_at > utcnow())
        )
    ).scalar_one_or_none()
    if not row:
        return None
    row.hit_count += 1
    await db.commit()
    return {"response": row.response, "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens}


async def _cache_put(db: AsyncSession, key: str, spec: TaskSpec, resp: LLMResponse,
                     ttl_mult: float = 1.0) -> None:
    db.add(
        AICache(
            cache_key=key, prompt_version=spec.prompt_version,
            response={"text": resp.text, "provider": resp.provider, "model": resp.model},
            input_tokens=resp.input_tokens, output_tokens=resp.output_tokens,
            expires_at=utcnow() + timedelta(days=CACHE_TTL_DAYS * ttl_mult),
        )
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()  # hai request đồng thời cùng miss -> một cái thắng, không sao


# ---------- ngân sách ----------

async def _spent_this_month(db: AsyncSession) -> float:
    start = utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return (
        await db.execute(
            select(func.coalesce(func.sum(AIUsage.cost_usd), 0.0)).where(AIUsage.created_at >= start)
        )
    ).scalar_one()


async def _user_calls_today(db: AsyncSession, user_id: uuid.UUID) -> int:
    start = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        await db.execute(
            select(func.count(AIUsage.id)).where(
                AIUsage.user_id == user_id,
                AIUsage.created_at >= start,
                AIUsage.cache_hit.is_(False),
            )
        )
    ).scalar_one()


async def budget_state(db: AsyncSession) -> dict:
    """Hạ cấp tiệm tiến theo mức tiêu, không bật/tắt đột ngột."""
    cap = await cfg.get_float(db, "ai.global_monthly_usd", _settings.AI_GLOBAL_MONTHLY_USD)
    spent = await _spent_this_month(db)
    ratio = spent / cap if cap > 0 else 0.0
    if ratio >= 0.90:
        mode = "cache_only"
    elif ratio >= 0.70:
        mode = "degraded"   # T2 -> T1, cache TTL x2
    else:
        mode = "normal"
    return {"mode": mode, "spent": round(spent, 4), "cap": cap, "ratio": round(ratio, 3)}


# ---------- provider resolution ----------

async def _provider_config(db: AsyncSession, name: str) -> ProviderConfig:
    return ProviderConfig(
        api_key=await cfg.get(db, f"ai.provider.{name}.api_key"),
        base_url=await cfg.get(db, f"ai.provider.{name}.base_url"),
    )


async def _route_chain(db: AsyncSession, tier: str) -> list[tuple[str, str]]:
    """"anthropic:claude-haiku-4-5,gemini:gemini-2.0-flash" -> [(provider, model), ...]"""
    key = f"ai.route.{tier.lower()}"
    env_default = _settings.LLM_ROUTE_T1 if tier == "T1" else _settings.LLM_ROUTE_T2
    raw = await cfg.get(db, key, env_default)
    chain = []
    for part in raw.split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        provider, model = part.split(":", 1)
        provider = provider.strip()
        if provider in REGISTRY:
            chain.append((provider, model.strip()))
    return chain


async def ai_enabled(db: AsyncSession) -> bool:
    if not await cfg.get_bool(db, "ai.enabled", True):
        return False
    for tier in ("T1", "T2"):
        for provider, _ in await _route_chain(db, tier):
            if provider == "ollama":
                return True
            if await cfg.get(db, f"ai.provider.{provider}.api_key"):
                return True
    return False


# ---------- gọi chính ----------

async def _log_usage(db: AsyncSession, **kw) -> None:
    db.add(AIUsage(**kw))
    await db.commit()


async def complete(
    db: AsyncSession,
    spec: TaskSpec,
    user_prompt: str,
    user_id: uuid.UUID | None = None,
    scope_id: str = "global",
    history: list[dict] | None = None,
) -> LLMResponse:
    """Thang fallback bậc 1-5. Bậc 6 (rule-based) do caller xử lý qua AIUnavailable."""
    budget = await budget_state(db)
    ttl_mult = 2.0 if budget["mode"] == "degraded" else 1.0

    # Bậc 1: cache
    key = _cache_key(spec, scope_id, user_prompt) if spec.cacheable else ""
    if key:
        cached = await _cache_get(db, key)
        if cached:
            saved = cached["input_tokens"] + cached["output_tokens"]
            await _log_usage(
                db, user_id=user_id, task_name=spec.name, prompt_version=spec.prompt_version,
                provider=cached["response"].get("provider", ""),
                model=cached["response"].get("model", ""), tier=spec.tier,
                cache_hit=True, tokens_saved=saved, cost_usd=0.0, status="ok",
            )
            return LLMResponse(
                text=cached["response"]["text"], provider=cached["response"].get("provider", ""),
                model=cached["response"].get("model", ""), from_cache=True,
            )

    if not await cfg.get_bool(db, "ai.enabled", True):
        raise AIUnavailable("AI đang tắt")
    if budget["mode"] == "cache_only":
        await _log_usage(db, user_id=user_id, task_name=spec.name, tier=spec.tier,
                         status="budget_exhausted", error_code="global_cap")
        raise AIUnavailable("Đã chạm trần chi phí tháng")

    if user_id:
        cap_calls = await cfg.get_int(db, "ai.user_daily_calls", _settings.AI_USER_DAILY_CALLS)
        if cap_calls and await _user_calls_today(db, user_id) >= cap_calls:
            await _log_usage(db, user_id=user_id, task_name=spec.name, tier=spec.tier,
                             status="quota_exhausted", error_code="user_daily")
            raise AIUnavailable("Hết hạn mức ngày")

    tier = spec.tier
    if budget["mode"] == "degraded" and tier == "T2" and spec.degradable:
        tier = "T1"  # bậc 4: hạ tier

    req = LLMRequest(
        system=spec.system_vi,
        messages=[*(history or []), {"role": "user", "content": user_prompt}],
        max_tokens=spec.max_output_tokens, temperature=spec.temperature,
    )

    # Bậc 2-3-5: đi hết chain; ollama nằm cuối chain trong config.
    chain = await _route_chain(db, tier)
    if tier == "T2" and spec.degradable:
        chain += await _route_chain(db, "T1")
    if not chain:
        raise AIUnavailable("Chưa cấu hình route cho tier " + tier)

    last_error = "unknown"
    for provider_name, model in chain:
        if not _cb_allow(provider_name):
            continue
        provider_cfg = await _provider_config(db, provider_name)
        provider = REGISTRY[provider_name](provider_cfg)
        for attempt in range(2):  # thử 2 lần, backoff 1s
            try:
                resp = await provider.complete(req, model)
                _cb_record(provider_name, ok=True)
                cost = _cost(provider_name, model, resp.input_tokens, resp.output_tokens)
                await _log_usage(
                    db, user_id=user_id, task_name=spec.name,
                    prompt_version=spec.prompt_version, provider=provider_name,
                    model=resp.model, tier=tier, input_tokens=resp.input_tokens,
                    output_tokens=resp.output_tokens, usage_estimated=resp.usage_estimated,
                    cost_usd=cost, latency_ms=resp.latency_ms, status="ok",
                )
                if key:
                    await _cache_put(db, key, spec, resp, ttl_mult)
                return resp
            except LLMError as exc:
                last_error = f"{provider_name}: {exc}"
                _cb_record(provider_name, ok=not exc.retryable)
                log.warning("provider %s failed (%s): %s", provider_name, exc.code, exc)
                await _log_usage(
                    db, user_id=user_id, task_name=spec.name, provider=provider_name,
                    model=model, tier=tier, status="error", error_code=exc.code,
                )
                if not exc.retryable or attempt == 1:
                    break
                await asyncio.sleep(1)

    raise AIUnavailable(f"Mọi provider đều lỗi. Cuối cùng: {last_error}")


async def health_report(db: AsyncSession) -> list[dict]:
    out = []
    for name in PROVIDER_NAMES:
        provider_cfg = await _provider_config(db, name)
        provider = REGISTRY[name](provider_cfg)
        state = _breaker.get(name, {})
        out.append({
            "provider": name,
            "has_key": bool(provider_cfg.api_key) or name == "ollama",
            "healthy": await provider.health(),
            "circuit_open": state.get("open_until", 0) > time.monotonic(),
        })
    return out
