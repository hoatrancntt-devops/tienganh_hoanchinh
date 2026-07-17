import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import Cefr, Role


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255))
    full_name: Mapped[str] = mapped_column(sa.String(120), default="")
    role: Mapped[str] = mapped_column(sa.String(20), default=Role.LEARNER, index=True)
    locale: Mapped[str] = mapped_column(sa.String(10), default="vi")
    timezone: Mapped[str] = mapped_column(sa.String(60), default="Asia/Ho_Chi_Minh")
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN


class UserProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    cefr_level_current: Mapped[str] = mapped_column(sa.String(10), default=Cefr.PRE_A1)
    goal: Mapped[str] = mapped_column(sa.String(20), default="speaking")  # speaking | reading
    daily_goal_minutes: Mapped[int] = mapped_column(sa.Integer, default=10)
    job_role: Mapped[str] = mapped_column(sa.String(80), default="")
    reminder_hour: Mapped[int] = mapped_column(sa.Integer, default=20)  # giờ địa phương
    email_opt_in: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    email_skip_count: Mapped[int] = mapped_column(sa.Integer, default=0)  # 5 lần -> tự tắt
    streak_days: Mapped[int] = mapped_column(sa.Integer, default=0)
    streak_freezes: Mapped[int] = mapped_column(sa.Integer, default=1)  # tối đa 2
    last_study_date: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    onboarded_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="profile")


class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    user_agent: Mapped[str] = mapped_column(sa.String(255), default="")
    ip: Mapped[str] = mapped_column(sa.String(64), default="")
