"""In-app + email outbox (PART N).

Ba luật giữ email không thành spam: trần tần suất, giờ yên lặng, tự tắt sau 5 lần bỏ qua.
Một lần bị đánh dấu spam làm hỏng khả năng gửi thư cho TẤT CẢ người còn lại.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utcnow
from app.models.enums import NotifType, OutboxStatus
from app.models.ops import EmailOutbox, Notification
from app.models.user import User
from app.services import mail_service

log = logging.getLogger(__name__)

QUIET_START, QUIET_END = 22, 7          # giờ địa phương
MAX_EMAIL_PER_DAY = 1
MAX_EMAIL_PER_WEEK = 3
CRITICAL = {NotifType.CHECKPOINT_PASSED, NotifType.PLACEMENT_READY}  # không tính vào trần
MAX_SEND_ATTEMPTS = 3
BACKOFF_MIN = [1, 5, 25]
EMAIL_SKIP_LIMIT = 5


def _local_now(user: User) -> datetime:
    try:
        return datetime.now(ZoneInfo(user.timezone))
    except Exception:
        return datetime.now(timezone.utc)


def _next_allowed_slot(user: User) -> datetime:
    """Giờ yên lặng: dời sang cửa sổ tiếp theo, không gửi."""
    local = _local_now(user)
    if QUIET_START <= local.hour or local.hour < QUIET_END:
        target = local.replace(hour=QUIET_END, minute=0, second=0, microsecond=0)
        if local.hour >= QUIET_START:
            target += timedelta(days=1)
        return target.astimezone(timezone.utc)
    return utcnow()


async def notify(
    db: AsyncSession,
    user: User,
    type_: str,
    title_vi: str,
    body_vi: str = "",
    link: str = "",
    dedup_key: str | None = None,
    email: bool = False,
    email_subject: str | None = None,
    email_html: str | None = None,
    expires_days: int | None = None,
) -> Notification | None:
    key = dedup_key or f"{type_}:{_local_now(user).date().isoformat()}"
    notif = Notification(
        user_id=user.id, type=type_, dedup_key=key, title_vi=title_vi,
        body_vi=body_vi, link=link,
        expires_at=utcnow() + timedelta(days=expires_days) if expires_days else None,
    )
    db.add(notif)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None  # dedup: job chạy hai lần không tạo trùng

    if email and await _email_allowed(db, user, type_):
        await queue_email(
            db, user, email_subject or title_vi,
            email_html or f"<p>{body_vi}</p>", scheduled_at=_next_allowed_slot(user),
        )
    return notif


async def _email_allowed(db: AsyncSession, user: User, type_: str) -> bool:
    profile = user.profile
    if not profile or not profile.email_opt_in:
        return False
    if type_ in CRITICAL:
        return True
    if profile.email_skip_count >= EMAIL_SKIP_LIMIT:
        return False  # đã tự tắt
    day_ago, week_ago = utcnow() - timedelta(days=1), utcnow() - timedelta(days=7)
    per_day = (
        await db.execute(
            select(func.count(EmailOutbox.id)).where(
                EmailOutbox.user_id == user.id, EmailOutbox.created_at >= day_ago
            )
        )
    ).scalar_one()
    if per_day >= MAX_EMAIL_PER_DAY:
        return False
    per_week = (
        await db.execute(
            select(func.count(EmailOutbox.id)).where(
                EmailOutbox.user_id == user.id, EmailOutbox.created_at >= week_ago
            )
        )
    ).scalar_one()
    return per_week < MAX_EMAIL_PER_WEEK


async def queue_email(
    db: AsyncSession, user: User | None, subject: str, body_html: str,
    to_email: str | None = None, scheduled_at: datetime | None = None,
) -> EmailOutbox:
    row = EmailOutbox(
        user_id=user.id if user else None,
        to_email=to_email or (user.email if user else ""),
        subject=subject, body_html=body_html,
        scheduled_at=scheduled_at or utcnow(),
    )
    db.add(row)
    await db.commit()
    return row


async def flush_outbox(db: AsyncSession, limit: int = 20) -> dict:
    """Job 60s. Retry 3 lần, backoff 1/5/25 phút."""
    if not await mail_service.is_configured(db):
        return {"sent": 0, "failed": 0, "skipped": "mail chưa cấu hình"}

    stmt = (
        select(EmailOutbox)
        .where(EmailOutbox.status == OutboxStatus.PENDING, EmailOutbox.scheduled_at <= utcnow())
        .order_by(EmailOutbox.scheduled_at)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).scalars().all()
    sent = failed = 0
    for row in rows:
        try:
            await mail_service.send(db, row.to_email, row.subject, row.body_html)
            row.status, row.sent_at = OutboxStatus.SENT, utcnow()
            sent += 1
        except Exception as exc:
            row.attempts += 1
            row.last_error = str(exc)[:500]
            if row.attempts >= MAX_SEND_ATTEMPTS:
                row.status = OutboxStatus.FAILED
                failed += 1
            else:
                row.scheduled_at = utcnow() + timedelta(minutes=BACKOFF_MIN[row.attempts - 1])
            log.warning("outbox send failed (attempt %s): %s", row.attempts, exc)
    await db.commit()
    return {"sent": sent, "failed": failed}


async def unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    return (
        await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
                (Notification.expires_at.is_(None)) | (Notification.expires_at > utcnow()),
            )
        )
    ).scalar_one()


async def list_recent(db: AsyncSession, user_id: uuid.UUID, limit: int = 20) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(
            Notification.user_id == user_id,
            (Notification.expires_at.is_(None)) | (Notification.expires_at > utcnow()),
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars().all())


async def mark_read(db: AsyncSession, user_id: uuid.UUID, notif_id: uuid.UUID | None = None) -> int:
    stmt = select(Notification).where(
        Notification.user_id == user_id, Notification.read_at.is_(None)
    )
    if notif_id:
        stmt = stmt.where(Notification.id == notif_id)
    rows = (await db.execute(stmt)).scalars().all()
    for row in rows:
        row.read_at = utcnow()
    await db.commit()
    return len(rows)


# ---------- streak ----------

async def record_study(db: AsyncSession, user: User) -> None:
    """Một ngày vào streak khi >=1 hoạt động xong. Mở app rồi đóng không tính."""
    profile = user.profile
    if not profile:
        return
    today = _local_now(user).date()
    last = profile.last_study_date.date() if profile.last_study_date else None
    if last == today:
        return
    if last == today - timedelta(days=1) or last is None:
        profile.streak_days += 1
    else:
        gap = (today - last).days
        # Freeze: người đi làm có họp khuya và con ốm. Mất streak 30 ngày là lý do bỏ học số một.
        if gap == 2 and profile.streak_freezes > 0:
            profile.streak_freezes -= 1
            profile.streak_days += 1
            await notify(
                db, user, NotifType.STREAK_LOST,
                "Đã dùng 1 ngày nghỉ",
                f"Streak {profile.streak_days} ngày của bạn vẫn còn.",
                expires_days=7,
            )
        else:
            profile.streak_days = 1
    profile.last_study_date = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
    await db.commit()


async def check_streak_warning(db: AsyncSession, user: User) -> None:
    """21:00 giờ địa phương. Chỉ khi streak>=3 — streak 1 ngày mất đi thì không ai tiếc."""
    profile = user.profile
    if not profile or profile.streak_days < 3:
        return
    today = _local_now(user).date()
    if profile.last_study_date and profile.last_study_date.date() == today:
        return
    await notify(
        db, user, NotifType.STREAK_WARNING,
        f"Streak {profile.streak_days} ngày. Còn 3 tiếng.",
        "5 phút ôn là giữ được.",
        link="/learn/review",  # ở 21:00, thứ khả thi là việc nhỏ — không phải bài mới
        email=True,
        email_subject=f"Streak {profile.streak_days} ngày của bạn sắp mất",
        email_html=(
            f"<p>Bạn đang có <b>{profile.streak_days} ngày</b> liên tiếp. "
            "Chỉ cần 5 phút ôn là giữ được.</p>"
            '<p><a href="/learn/review">Ôn 5 phút</a></p>'
        ),
        expires_days=1,
    )


async def daily_reminder(db: AsyncSession, user: User, next_up: dict) -> None:
    profile = user.profile
    if not profile:
        return
    today = _local_now(user).date()
    if profile.last_study_date and profile.last_study_date.date() == today:
        return
    title = next_up.get("title_vi") or "Bài học hôm nay"
    reason = next_up.get("reason_vi", "")
    await notify(
        db, user, NotifType.DAILY_REMINDER,
        f"{profile.daily_goal_minutes} phút cho “{title}”", reason,
        link="/learn", email=True,
        email_subject=f"[{profile.daily_goal_minutes} phút] {title}",
        email_html=(
            f"<p>{reason}</p><p><a href=\"/learn\">Học ngay</a></p>"
            "<p style='font-size:12px;color:#888'>"
            "<a href='/settings'>Đổi giờ nhắc hoặc tắt email</a></p>"
        ),
        expires_days=1,
    )
