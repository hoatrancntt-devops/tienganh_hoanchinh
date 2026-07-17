import uuid

from pydantic import BaseModel, Field


class AskIn(BaseModel):
    task: str = Field(default="explain", pattern="^(explain|sentence_repair|open_feedback)$")
    lesson_id: uuid.UUID | None = None
    question: str = Field(min_length=2, max_length=500)


class AskOut(BaseModel):
    answer_vi: str
    source: str          # ai | cache | fallback
    provider: str = ""
    model: str = ""
    degraded: bool = False
