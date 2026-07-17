import uuid

from pydantic import BaseModel, Field


class ResponseIn(BaseModel):
    item_ref: str
    section: str = Field(pattern="^(vocab|grammar|listening|speaking|self)$")
    kind: str = Field(pattern="^(mcq|read_aloud|repeat|short_answer|likert)$")
    choice_index: int | None = None
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
