from enum import StrEnum


class Role(StrEnum):
    LEARNER = "learner"
    ADMIN = "admin"


class Cefr(StrEnum):
    PRE_A1 = "pre_a1"
    A1 = "a1"
    A2 = "a2"
    B1 = "b1"


class Phase(StrEnum):
    ORIENTATION = "orientation"
    FOUNDATION = "foundation"
    DAILY = "daily"
    OFFICE = "office"
    IT_ENGLISH = "it_english"
    READING = "reading"
    REINFORCEMENT = "reinforcement"


class LessonState(StrEnum):
    LOCKED = "locked"
    PREVIEWABLE = "previewable"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"
    NEEDS_REVIEW = "needs_review"


class PrereqKind(StrEnum):
    HARD = "hard"   # chặn
    SOFT = "soft"   # chỉ cảnh báo


class ActivityKind(StrEnum):
    LISTEN = "listen"
    SHADOW = "shadow"
    SPEAK = "speak"
    VOCAB = "vocab"
    READ = "read"
    WRITE = "write"
    QUIZ = "quiz"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotifType(StrEnum):
    DAILY_REMINDER = "daily_reminder"
    STREAK_WARNING = "streak_warning"
    STREAK_LOST = "streak_lost"
    CHECKPOINT_PASSED = "checkpoint_passed"
    LESSON_UNLOCKED = "lesson_unlocked"
    REVIEW_DUE = "review_due"
    RETENTION_DEBT = "retention_debt"
    WEEKLY_REPORT = "weekly_report"
    PLACEMENT_READY = "placement_ready"
