import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import OutboxStatus


class AppSetting(Base, UUIDMixin, TimestampMixin):
    """Cấu hình admin sửa trên web (mail M365, AI key). Secret mã hoá bằng app.core.crypto."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(sa.String(120), unique=True, index=True)
    value: Mapped[str] = mapped_column(sa.Text, default="")
    is_secret: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("users.id"))


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        # Chống job chạy hai lần tạo trùng.
        sa.UniqueConstraint("user_id", "dedup_key", name="uq_notif_dedup"),
        sa.Index("ix_notif_user_unread", "user_id", "read_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(sa.String(40), index=True)
    dedup_key: Mapped[str] = mapped_column(sa.String(160))
    title_vi: Mapped[str] = mapped_column(sa.String(200))
    body_vi: Mapped[str] = mapped_column(sa.Text, default="")
    link: Mapped[str] = mapped_column(sa.String(300), default="")
    read_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class EmailOutbox(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "email_outbox"
    __table_args__ = (sa.Index("ix_outbox_pending", "status", "scheduled_at"),)

    user_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    to_email: Mapped[str] = mapped_column(sa.String(255))
    subject: Mapped[str] = mapped_column(sa.String(255))
    body_html: Mapped[str] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.String(20), default=OutboxStatus.PENDING, index=True)
    attempts: Mapped[int] = mapped_column(sa.Integer, default=0)
    last_error: Mapped[str] = mapped_column(sa.Text, default="")
    scheduled_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class AICache(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_cache"

    cache_key: Mapped[str] = mapped_column(sa.String(80), unique=True, index=True)
    prompt_version: Mapped[str] = mapped_column(sa.String(40))
    response: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    input_tokens: Mapped[int] = mapped_column(sa.Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(sa.Integer, default=0)
    hit_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), index=True)


class AIUsage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_usage"
    __table_args__ = (sa.Index("ix_usage_user_time", "user_id", "created_at"),)

    user_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    task_name: Mapped[str] = mapped_column(sa.String(40), index=True)
    prompt_version: Mapped[str] = mapped_column(sa.String(40), default="")
    provider: Mapped[str] = mapped_column(sa.String(30), default="")
    model: Mapped[str] = mapped_column(sa.String(80), default="")
    tier: Mapped[str] = mapped_column(sa.String(4), default="T1")
    input_tokens: Mapped[int] = mapped_column(sa.Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(sa.Integer, default=0)
    usage_estimated: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    # Chốt tại thời điểm gọi: giá đổi thì lịch sử chi phí không được đổi theo.
    cost_usd: Mapped[float] = mapped_column(sa.Float, default=0.0)
    cache_hit: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    tokens_saved: Mapped[int] = mapped_column(sa.Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(sa.Integer, default=0)
    status: Mapped[str] = mapped_column(sa.String(20), default="ok")
    error_code: Mapped[str] = mapped_column(sa.String(60), default="")


class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(sa.String(60), index=True)
    entity_type: Mapped[str] = mapped_column(sa.String(40), default="")
    entity_id: Mapped[str] = mapped_column(sa.String(60), default="")
    diff: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    ip: Mapped[str] = mapped_column(sa.String(64), default="")
