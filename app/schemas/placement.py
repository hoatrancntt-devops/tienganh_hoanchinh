import uuid

from pydantic import BaseModel, Field


class ResponseIn(BaseModel):
    item_ref: str
    section: str = Field(pattern="^(vocab|grammar|listening|reading|writing|speaking|self)$")
    kind: str = Field(
        pattern="^(mcq|mcq_read|read_aloud|repeat|short_answer|likert"
                "|fill_blank|error_correction|reorder|guided_email)$"
    )
    choice_index: int | None = None
    text: str | None = Field(default=None, max_length=2000)
    # Bài viết nhiều ô. Chặn độ dài ở tầng schema: ô nhập tự do là chỗ dễ bị nhét
    # văn bản khổng lồ nhất.
    texts: list[str] = Field(default_factory=list, max_length=20)
    audio_ref: str | None = None
    latency_ms: int = 0
    replay_count: int = Field(default=0, ge=0, le=5)


class PlacementSubmitIn(BaseModel):
    test_id: uuid.UUID
    responses: list[ResponseIn]


class PlacementResultOut(BaseModel):
    test_id: uuid.UUID
    result_cefr: str
    confidence: str
    scores: dict
    speaking_detail: dict
    entry_lesson_code: str | None
    strengths_vi: list[str]
    gaps_vi: list[str]
    explanation_vi: str
    estimated_weeks_to_goal: int
    can_challenge: bool
