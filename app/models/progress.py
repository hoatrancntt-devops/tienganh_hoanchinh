import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import LessonState


class Enrollment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "enrollments"
    __table_args__ = (sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("courses.id", ondelete="CASCADE"))
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    current_lesson_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("lessons.id"))


class LessonProgress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress"),
        sa.Index("ix_progress_user_state", "user_id", "state"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    state: Mapped[str] = mapped_column(sa.String(20), default=LessonState.LOCKED)
    mastery_raw: Mapped[float] = mapped_column(sa.Float, default=0.0)
    speaking_attempts: Mapped[int] = mapped_column(sa.Integer, default=0)
    attempts_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    unlocked_by: Mapped[str] = mapped_column(sa.String(20), default="prereq")
    admin_override: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    mastered_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class ItemAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "item_attempts"
    __table_args__ = (sa.Index("ix_attempt_user_item", "user_id", "item_id", "created_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("items.id", ondelete="CASCADE"))
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("lessons.id"), index=True)
    activity_kind: Mapped[str] = mapped_column(sa.String(20), default="quiz")
    is_correct: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    score: Mapped[float] = mapped_column(sa.Float, default=0.0)
    response: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    latency_ms: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_preview: Mapped[bool] = mapped_column(sa.Boolean, default=False)  # preview không tính mastery


class ReviewQueue(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "review_queue"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "item_id", name="uq_review"),
        sa.Index("ix_review_due", "user_id", "due_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("items.id", ondelete="CASCADE"))
    due_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    interval_days: Mapped[int] = mapped_column(sa.Integer, default=1)
    ease: Mapped[float] = mapped_column(sa.Float, default=2.5)
