import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ActivityKind, Cefr, ContentStatus, Phase, PrereqKind


class Course(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "courses"

    slug: Mapped[str] = mapped_column(sa.String(80), unique=True, index=True)
    title_vi: Mapped[str] = mapped_column(sa.String(160))
    title_en: Mapped[str] = mapped_column(sa.String(160), default="")
    cefr_from: Mapped[str] = mapped_column(sa.String(10), default=Cefr.PRE_A1)
    cefr_to: Mapped[str] = mapped_column(sa.String(10), default=Cefr.A2)
    track: Mapped[str] = mapped_column(sa.String(30), default="speaking_core")
    status: Mapped[str] = mapped_column(sa.String(20), default=ContentStatus.PUBLISHED)


class Topic(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "topics"

    slug: Mapped[str] = mapped_column(sa.String(40), unique=True, index=True)
    title_vi: Mapped[str] = mapped_column(sa.String(120))


class Unit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "units"

    course_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("courses.id", ondelete="CASCADE"))
    topic_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("topics.id"))
    code: Mapped[str] = mapped_column(sa.String(20), unique=True, index=True)
    order_index: Mapped[int] = mapped_column(sa.Integer, default=0)
    title_vi: Mapped[str] = mapped_column(sa.String(160))
    objectives_vi: Mapped[list] = mapped_column(sa.JSON, default=list)

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan"
    )


class Lesson(Base, UUIDMixin, TimestampMixin):
    """Blueprint PART K. `code` là id ổn định (F07), tách khỏi slug và order_index."""

    __tablename__ = "lessons"

    unit_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("units.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(sa.String(20), unique=True, index=True)
    slug: Mapped[str] = mapped_column(sa.String(120), unique=True, index=True)
    phase: Mapped[str] = mapped_column(sa.String(20), default=Phase.FOUNDATION, index=True)
    topic: Mapped[str] = mapped_column(sa.String(30), default="core")
    cefr_target: Mapped[str] = mapped_column(sa.String(10), default=Cefr.PRE_A1)
    order_index: Mapped[int] = mapped_column(sa.Integer, default=0)
    title_vi: Mapped[str] = mapped_column(sa.String(200))
    title_en: Mapped[str] = mapped_column(sa.String(200), default="")
    est_minutes: Mapped[int] = mapped_column(sa.Integer, default=10)
    is_checkpoint: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    status: Mapped[str] = mapped_column(sa.String(20), default=ContentStatus.DRAFT, index=True)

    objective_vi: Mapped[str] = mapped_column(sa.Text, default="")
    objective_observable: Mapped[str] = mapped_column(sa.Text, default="")
    # Bắt buộc phi kỹ thuật: hai trường này là fallback khi không có AI key.
    vietnamese_explanation: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    common_mistakes: Mapped[list] = mapped_column(sa.JSON, default=list)
    memory_trick_vi: Mapped[str] = mapped_column(sa.Text, default="")
    # Nội dung "học" hiển thị TRƯỚC câu hỏi: hội thoại (EN/VI), từ vựng, mẫu câu.
    dialogue: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    vocabulary: Mapped[list] = mapped_column(sa.JSON, default=list)
    sentence_patterns: Mapped[list] = mapped_column(sa.JSON, default=list)
    # Văn bản để ĐỌC. Cố ý không có trường audio: bài đọc phát được tiếng thì học viên
    # sẽ nghe thay vì đọc, và phần đọc lại thành phần nghe.
    reading_passage: Mapped[dict] = mapped_column(sa.JSON, default=dict)

    mastery_threshold: Mapped[int] = mapped_column(sa.Integer, default=80)
    mastery_weights: Mapped[dict] = mapped_column(
        sa.JSON, default=lambda: {"speak": 0.5, "quiz": 0.3, "listen": 0.2}
    )
    min_speaking_attempts: Mapped[int] = mapped_column(sa.Integer, default=4)
    challenge_threshold: Mapped[int] = mapped_column(sa.Integer, default=85)
    # Ngưỡng riêng từng kỹ năng ở checkpoint — xem chú thích Unlock.min_per_skill.
    min_per_skill: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    recommended_next: Mapped[dict] = mapped_column(sa.JSON, default=dict)

    unit: Mapped[Unit] = relationship(back_populates="lessons")
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan", order_by="Activity.order_index"
    )


class Activity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "activities"

    lesson_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("lessons.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(sa.String(20), default=ActivityKind.QUIZ)
    order_index: Mapped[int] = mapped_column(sa.Integer, default=0)
    title_vi: Mapped[str] = mapped_column(sa.String(160), default="")
    config: Mapped[dict] = mapped_column(sa.JSON, default=dict)

    lesson: Mapped[Lesson] = relationship(back_populates="activities")
    items: Mapped[list["Item"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan", order_by="Item.order_index"
    )


class Item(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "items"

    activity_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("activities.id", ondelete="CASCADE"), index=True
    )
    order_index: Mapped[int] = mapped_column(sa.Integer, default=0)
    kind: Mapped[str] = mapped_column(sa.String(30), default="mcq")
    prompt_en: Mapped[str] = mapped_column(sa.Text, default="")
    prompt_vi: Mapped[str] = mapped_column(sa.Text, default="")
    expected_text: Mapped[str | None] = mapped_column(sa.Text)  # None = câu trả lời mở
    ipa: Mapped[str] = mapped_column(sa.String(200), default="")
    choices: Mapped[list] = mapped_column(sa.JSON, default=list)
    answer_index: Mapped[int | None] = mapped_column(sa.Integer)
    accept_patterns: Mapped[list] = mapped_column(sa.JSON, default=list)  # fallback khi không AI
    focus_phonemes: Mapped[list] = mapped_column(sa.JSON, default=list)
    scoring_weights: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    difficulty: Mapped[int] = mapped_column(sa.Integer, default=2)  # 1..5
    audio_asset_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("media_assets.id"))
    tags: Mapped[list] = mapped_column(sa.JSON, default=list)

    activity: Mapped[Activity] = relationship(back_populates="items")


class MediaAsset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "media_assets"

    kind: Mapped[str] = mapped_column(sa.String(20), default="audio")
    path: Mapped[str] = mapped_column(sa.String(400))
    checksum: Mapped[str] = mapped_column(sa.String(64), index=True)  # seed lại chỉ sinh phần mới
    duration_ms: Mapped[int] = mapped_column(sa.Integer, default=0)
    voice: Mapped[str] = mapped_column(sa.String(40), default="")
    generated_by: Mapped[str] = mapped_column(sa.String(20), default="piper")


class Prerequisite(Base, UUIDMixin, TimestampMixin):
    """Cạnh có hướng của DAG. Checkpoint dùng chung cơ chế này, không có hệ thống thứ hai."""

    __tablename__ = "prerequisites"
    __table_args__ = (sa.UniqueConstraint("lesson_id", "requires_lesson_id", name="uq_prereq_edge"),)

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    requires_lesson_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    min_mastery: Mapped[int] = mapped_column(sa.Integer, default=80)
    kind: Mapped[str] = mapped_column(sa.String(10), default=PrereqKind.HARD)


class ContentVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_versions"

    entity_type: Mapped[str] = mapped_column(sa.String(40), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid(as_uuid=True), index=True)
    snapshot: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    author_id: Mapped[uuid.UUID | None] = mapped_column(sa.ForeignKey("users.id"))
