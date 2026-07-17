"""Data contract của một lesson YAML (PART K). Pydantic là hợp đồng, không phải trang trí."""
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Vocab(BaseModel):
    model_config = ConfigDict(extra="forbid")
    term: str
    ipa: str = Field(min_length=1)
    meaning_vi: str
    chunk: str = Field(min_length=3)  # luôn dạy trong khối, không dạy từ trơ
    tags: list[str] = []


class Pattern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pattern: str
    meaning_vi: str
    slots: dict[str, list[str]] = {}


class Turn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    speaker: str
    en: str
    vi: str


class Dialogue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context_vi: str
    turns: list[Turn] = []


class ListenQ(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q_vi: str
    choices: list[str] = Field(min_length=2)
    answer: int
    difficulty: int = Field(default=2, ge=1, le=5)


class Listening(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    speed: float = Field(default=1.0, ge=0.5, le=1.5)
    voice: str = "en_US_female"
    transcript_en: str
    transcript_vi: str
    questions: list[ListenQ] = []


class Drill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str = Field(pattern="^(read_aloud|shadow|repeat|substitute|respond)$")
    prompt_en: str = ""
    prompt_vi: str = ""
    expected_text: str | None = None
    ipa: str = ""
    focus_phonemes: list[str] = []
    accept_patterns: list[str] = []

    @model_validator(mode="after")
    def open_needs_patterns(self):
        if self.expected_text is None and self.kind == "respond" and not self.accept_patterns:
            raise ValueError("drill respond mở phải có accept_patterns (fallback khi không có AI)")
        return self


class Explanation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    why_vi: str = Field(min_length=20)
    how_vi: str = Field(min_length=15)
    contrast_vi: str = ""


class Detect(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phoneme_missing: list[str] = []
    phoneme_inserted: list[str] = []


class Mistake(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mistake: str
    why_vi: str
    fix_vi: str
    detect: Detect = Detect()


class QuizItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str = Field(default="mcq", pattern="^(mcq|mcq_listen|fill_chunk)$")
    prompt_vi: str
    audio_text: str = ""      # câu sẽ đọc lên với mcq_listen
    choices: list[str] = Field(min_length=2)
    answer: int
    difficulty: int = Field(default=2, ge=1, le=5)
    focus_phonemes: list[str] = []


class Prereq(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lesson: str
    min_mastery: int = Field(default=80, ge=0, le=100)
    kind: str = Field(default="hard", pattern="^(hard|soft)$")


class Unlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mastery_threshold: int = Field(default=80, ge=50, le=100)
    mastery_weights: dict[str, float] = {"speak": 0.5, "quiz": 0.3, "listen": 0.2}
    min_speaking_attempts: int = Field(default=4, ge=0)
    challenge_threshold: int = Field(default=85, ge=50, le=100)

    @field_validator("mastery_weights")
    @classmethod
    def weights_sum_to_one(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"mastery_weights phải cộng đúng 1.0, đang là {total}")
        return v


class LessonYAML(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    id: str = Field(pattern=r"^[A-Z]{1,3}-?\d{0,2}[A-Z]?$")
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    title_vi: str
    title_en: str = ""
    phase: str = Field(pattern="^(orientation|foundation|daily|office|it_english|reading)$")
    topic: str = Field(pattern="^(core|social|food|transport|office|it_english)$")
    cefr_target: str = Field(default="pre_a1", pattern="^(pre_a1|a1|a2|b1)$")
    order_index: int = Field(ge=0)
    est_minutes: int = Field(default=10, ge=3, le=12)  # bài dài là bài không được học
    is_checkpoint: bool = False
    unit: str
    status: str = Field(default="published", pattern="^(draft|published)$")

    objective_vi: str = Field(min_length=15)
    objective_observable: str = Field(min_length=10)
    prerequisites: list[Prereq] = []
    vocabulary: list[Vocab] = []
    sentence_patterns: list[Pattern] = []
    dialogue: Dialogue | None = None
    listening_snippet: Listening | None = None
    speaking_drills: list[Drill] = []
    vietnamese_explanation: Explanation
    common_mistakes: list[Mistake] = Field(min_length=2)
    memory_trick_vi: str = ""
    mini_quiz: list[QuizItem] = []
    unlock_condition: Unlock = Unlock()
    recommended_next: dict = {}

    @model_validator(mode="after")
    def speaking_phase_needs_drills(self):
        if self.phase in ("foundation", "daily", "office", "it_english"):
            if len(self.speaking_drills) < 4:
                raise ValueError(
                    f"{self.id}: phase '{self.phase}' cần ≥4 speaking_drills, "
                    f"đang có {len(self.speaking_drills)}"
                )
        return self
