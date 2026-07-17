"""APScheduler in-process (PART N).

15 phút thay vì mỗi phút: hầu hết học viên cùng một timezone, cửa sổ 15 phút đủ chính xác
cho một lời nhắc học và giảm 15 lần số lượt quét vô ích.
"""
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete, select, text

from app.core.config import get_settings
from app.db.base import utcnow
from app.db.session import SessionLocal
from app.models.enums import NotifType
from app.models.ops import AICache, Notification
from app.models.user import User
from app.services import auth_service
from app.services import learning_path_service as path
from app.services import notification_service as notif

log = logging.getLogger(__name__)
_settings = get_settings()
scheduler = AsyncIOScheduler(timezone="UTC")

LOCK_KEY = 918273645  # advisory lock: nhiều worker uvicorn -> chỉ một worker chạy job


async def _acquire_lock(db) -> bool:
    """Không có lock này thì mỗi email gửi hai lần khi chạy >1 worker."""
    if _settings.is_sqlite:
        return True
    row = await db.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": LOCK_KEY})
    return bool(row.scalar())


async def _release_lock(db) -> None:
    if not _settings.is_sqlite:
        await db.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": LOCK_KEY})


def _local_hour(user: User) -> int:
    try:
        return datetime.now(ZoneInfo(user.timezone)).hour
    except Exception:
        return datetime.now(ZoneInfo(_settings.DEFAULT_TZ)).hour


async def job_outbox_flush() -> None:
    async with SessionLocal() as db:
        if not await _acquire_lock(db):
            return
        try:
            result = await notif.flush_outbox(db)
            if result.get("sent"):
                log.info("outbox flushed: %s", result)
        finally:
            await _release_lock(db)


async def job_reminder_tick() -> None:
    async with SessionLocal() as db:
        if not await _acquire_lock(db):
            return
        try:
            users = (
                await db.execute(select(User).where(User.is_active.is_(True)))
            ).scalars().all()
            for user in users:
                await db.refresh(user, ["profile"])
                if not user.profile or user.profile.onboarded_at is None:
                    continue
                if _local_hour(user) != user.profile.reminder_hour:
                    continue
                next_up = await path.next_up(db, user.id)
                await notif.daily_reminder(db, user, next_up)
        finally:
            await _release_lock(db)


async def job_streak_tick() -> None:
    async with SessionLocal() as db:
        if not await _acquire_lock(db):
            return
        try:
            users = (
                await db.execute(select(User).where(User.is_active.is_(True)))
            ).scalars().all()
            for user in users:
                await db.refresh(user, ["profile"])
                if not user.profile:
                    continue
                hour = _local_hour(user)
                if hour == 21:
                    await notif.check_streak_warning(db, user)
                elif hour == 0:
                    await _settle_streak(db, user)
        finally:
            await _release_lock(db)


async def _settle_streak(db, user: User) -> None:
    profile = user.profile
    if not profile or profile.streak_days == 0:
        return
    today = datetime.now(ZoneInfo(user.timezone or _settings.DEFAULT_TZ)).date()
    last = profile.last_study_date.date() if profile.last_study_date else None
    if last is None or (today - last).days <= 1:
        return
    if profile.streak_freezes > 0:
        profile.streak_freezes -= 1
    else:
        lost = profile.streak_days
        profile.streak_days = 0
        await notif.notify(
            db, user, NotifType.STREAK_LOST, f"Streak {lost} ngày đã dừng",
            "Không sao. Bắt đầu lại hôm nay, 5 phút là đủ.", link="/learn",
            dedup_key=f"streak_lost:{today.isoformat()}", expires_days=3,
        )
    await db.commit()


async def job_weekly_freeze_grant() -> None:
    """Freeze tự động 1/tuần, tích luỹ tối đa 2."""
    async with SessionLocal() as db:
        if not await _acquire_lock(db):
            return
        try:
            users = (await db.execute(select(User))).scalars().all()
            for user in users:
                await db.refresh(user, ["profile"])
                if user.profile and user.profile.streak_freezes < 2:
                    user.profile.streak_freezes += 1
            await db.commit()
        finally:
            await _release_lock(db)


async def job_housekeeping() -> None:
    async with SessionLocal() as db:
        if not await _acquire_lock(db):
            return
        try:
            purged = await auth_service.purge_expired_sessions(db)
            await db.execute(delete(AICache).where(AICache.expires_at < utcnow()))
            # Thông báo quá hạn là nhiễu.
            await db.execute(
                delete(Notification).where(
                    Notification.expires_at.isnot(None),
                    Notification.expires_at < utcnow() - timedelta(days=30),
                )
            )
            await db.commit()
            log.info("housekeeping done, sessions purged=%s", purged)
        finally:
            await _release_lock(db)


def start_scheduler() -> AsyncIOScheduler | None:
    if not _settings.SCHEDULER_ENABLED:
        log.info("scheduler disabled")
        return None
    # coalesce + max_instances=1: job chậm không chồng lên chính nó.
    common = {"coalesce": True, "max_instances": 1, "misfire_grace_time": 300}
    scheduler.add_job(job_outbox_flush, "interval", seconds=60, id="outbox", **common)
    scheduler.add_job(job_reminder_tick, "interval", minutes=15, id="reminder", **common)
    scheduler.add_job(job_streak_tick, "interval", minutes=15, id="streak", **common)
    scheduler.add_job(job_weekly_freeze_grant, "cron", day_of_week="mon", hour=0,
                      id="freeze", **common)
    scheduler.add_job(job_housekeeping, "cron", hour=3, id="housekeeping", **common)
    scheduler.start()
    log.info("scheduler started with %s jobs", len(scheduler.get_jobs()))
    return scheduler


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
