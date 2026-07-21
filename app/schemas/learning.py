import uuid

from pydantic import BaseModel, Field


class LessonCardOut(BaseModel):
    lesson_id: uuid.UUID
    code: str
    title_vi: str
    phase: str
    est_minutes: int
    state: str
    mastery_raw: float
    mastery_effective: float
    threshold: int
    warning_level: str          # none | info | caution | blocked | debt
    warning_vi: str
    blocking_lesson_code: str | None = None


class NextUpOut(BaseModel):
    lesson_id: uuid.UUID | None
    code: str | None
    title_vi: str | None
    reason_vi: str              # why-this-next: luật, không LLM
    kind: str                   # review | continue | checkpoint | new | branch | done


class SubmitAttemptIn(BaseModel):
    item_id: uuid.UUID
    choice_index: int | None = None
    text: str | None = None
    # Bài viết nhiều ô (fill_blank, error_correction, reorder). Chặn độ dài ở tầng schema:
    # ô nhập tự do là chỗ dễ bị nhét văn bản khổng lồ nhất.
    texts: list[str] = Field(default_factory=list, max_length=20)
    latency_ms: int = Field(default=0, ge=0)
    is_preview: bool = False


class AttemptResultOut(BaseModel):
    is_correct: bool
    score: float
    feedback_vi: str
    mastery_raw: float
    state: str
    unlocked_codes: list[str] = []
