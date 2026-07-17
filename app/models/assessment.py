import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import Cefr


class SpeechAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "speech_attempts"
    __table_args__ = (sa.Index("ix_speech_user_time", "user_id", "created_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("items.id"))
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("lessons.id"))
    audio_path: Mapped[str] = mapped_column(sa.String(400), default="")
    transcript: Mapped[str] = mapped_column(sa.Text, default="")
    score_pronunciation: Mapped[float] = mapped_column(sa.Float, default=0.0)
    score_fluency: Mapped[float] = mapped_column(sa.Float, default=0.0)
    score_communication: Mapped[float] = mapped_column(sa.Float, default=0.0)
    score_overall: Mapped[float] = mapped_column(sa.Float, default=0.0)
    wpm: Mapped[float] = mapped_column(sa.Float, default=0.0)
    pause_ratio: Mapped[float] = mapped_column(sa.Float, default=0.0)
    phoneme_diff: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    feedback_vi: Mapped[str] = mapped_column(sa.Text, default="")
    engine_version: Mapped[str] = mapped_column(sa.String(40), default="")
    duration_ms: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_preview: Mapped[bool] = mapped_column(sa.Boolean, default=False)


class PlacementTest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "placement_tests"

    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    form: Mapped[str] = mapped_column(sa.String(2), default="A")  # A | B
    started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    result_cefr: Mapped[str | None] = mapped_column(sa.String(10))
    confidence: Mapped[str] = mapped_column(sa.String(10), default="medium")
    result_scores: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    explanation_vi: Mapped[str] = mapped_column(sa.Text, default="")
    recommended_course_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("courses.id"))
    entry_lesson_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("lessons.id"))
    can_challenge: Mapped[bool] = mapped_column(sa.Boolean, default=False)


class PlacementResponse(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "placement_responses"

    test_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("placement_tests.id", ondelete="CASCADE"), index=True
    )
    item_ref: Mapped[str] = mapped_column(sa.String(40))  # id trong YAML form, không phải Item
    section: Mapped[str] = mapped_column(sa.String(20))
    kind: Mapped[str] = mapped_column(sa.String(20))
    choice_index: Mapped[int | None] = mapped_column(sa.Integer)
    audio_ref: Mapped[str | None] = mapped_column(sa.String(400))
    is_correct: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    score: Mapped[float] = mapped_column(sa.Float, default=0.0)
    detail: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    latency_ms: Mapped[int] = mapped_column(sa.Integer, default=0)
    replay_count: Mapped[int] = mapped_column(sa.Integer, default=0)


CEFR_ORDER = [Cefr.PRE_A1, Cefr.A1, Cefr.A2, Cefr.B1]
