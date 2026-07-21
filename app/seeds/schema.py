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
    # Bối cảnh tiếng Việt đặt trước khi phát: ai đang nói, ở đâu, đang cần gì.
    context_vi: str = ""
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


class ReadQ(BaseModel):
    """Câu hỏi đọc hiểu. Đề bằng tiếng Anh — hỏi bằng tiếng Việt là đo hiểu tiếng Việt."""
    model_config = ConfigDict(extra="forbid")
    q_en: str = Field(min_length=5)
    choices: list[str] = Field(min_length=2)
    answer: int
    # scan: tìm thông tin cụ thể · skim: ý chính · infer: suy luận · guess_word: đoán nghĩa từ ngữ cảnh
    skill: str = Field(default="scan", pattern="^(scan|skim|infer|guess_word)$")
    difficulty: int = Field(default=2, ge=1, le=5)


class ReadingPassage(BaseModel):
    """Văn bản liền mạch để ĐỌC.

    Khác `Dialogue` ở hai điểm sống còn: không chia lượt người nói, và KHÔNG SINH AUDIO.
    Bài đọc mà nghe được thì học viên sẽ nghe thay vì đọc, và kỹ năng đọc lại biến mất —
    đó đúng là hiện trạng của 11 bài phase `reading` trước bản này.
    """
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: str = Field(default="email", pattern="^(email|chat|ticket|doc|announcement|log)$")
    context_vi: str = ""
    text_en: str = Field(min_length=40)
    text_vi: str = Field(min_length=20)      # bản dịch, chỉ mở sau khi trả lời
    questions: list[ReadQ] = Field(min_length=2)

    @model_validator(mode="after")
    def cau_hoi_phai_da_dang(self):
        if len({q.skill for q in self.questions}) < 2:
            raise ValueError(
                f"{self.id}: cần ≥2 loại câu hỏi đọc khác nhau (scan/skim/infer/guess_word), "
                f"đang chỉ có một loại"
            )
        return self


class WritingTask(BaseModel):
    """Bài viết nhúng trong bài học. Chấm 100% bằng luật qua `writing_service.grade()`.

    Dùng chung từ vựng dạng bài với bộ luyện viết độc lập ở `seeds/writing/*.yaml` —
    một bộ chấm, một tập tên dạng bài, không dựng hệ song song.

    `guided_email` là dạng duy nhất có đầu ra tự do, nên nó bắt buộc khai `required_chunks`
    kèm biến thể chấp nhận được. Thiếu biến thể là nguyên nhân số một khiến chấm luật đánh
    trượt người viết đúng theo cách khác.
    """
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: str = Field(
        pattern="^(translate|compose|fill_blank|error_correction|reorder|guided_email)$"
    )
    # Thể loại của bài `guided_email`. `email` cần lời chào và lời kết; `note` thì không —
    # status update, bài standup và comment review vốn dĩ không có hai thứ đó, đòi chúng là
    # dạy sai văn phong.
    style: str = Field(default="email", pattern="^(email|note)$")
    prompt_vi: str = Field(min_length=10)
    prompt_en: str = ""
    hint_vi: str = ""
    sample_en: str = ""

    accept: list[str] = []                   # translate
    keywords: list[str] = []                 # compose
    blanks: list[list[str]] = []             # fill_blank / error_correction: mỗi ô một tập đáp án
    ordered_lines: list[str] = []            # reorder: ĐÚNG thứ tự; UI xáo trước khi hiện
    frame_vi: list[str] = []                 # guided_email: khung mở/thân/kết hiện cạnh ô nhập
    required_chunks: list[list[str]] = []    # guided_email: mỗi nhóm = các cách nói cùng một ý
    min_words: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def du_lieu_khop_voi_dang_bai(self):
        if self.kind == "translate" and not self.accept:
            raise ValueError(f"{self.id}: dạng 'translate' phải có `accept`")
        if self.kind == "compose" and not self.keywords:
            raise ValueError(f"{self.id}: dạng 'compose' phải có `keywords`")
        if self.kind in ("fill_blank", "error_correction") and not self.blanks:
            raise ValueError(f"{self.id}: dạng '{self.kind}' phải có `blanks`")
        if self.kind == "reorder" and len(self.ordered_lines) < 3:
            raise ValueError(f"{self.id}: dạng 'reorder' cần ≥3 câu trong `ordered_lines`")
        if self.kind == "guided_email":
            if len(self.required_chunks) < 3:
                raise ValueError(f"{self.id}: 'guided_email' cần ≥3 nhóm `required_chunks`")
            if self.min_words < 5:
                raise ValueError(f"{self.id}: 'guided_email' cần `min_words` ≥5")
        if any(not nhom for nhom in self.required_chunks):
            raise ValueError(f"{self.id}: có nhóm `required_chunks` rỗng")
        if any(not nhom for nhom in self.blanks):
            raise ValueError(f"{self.id}: có ô trống không khai đáp án nào")
        return self


class Prereq(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lesson: str
    min_mastery: int = Field(default=80, ge=0, le=100)
    kind: str = Field(default="hard", pattern="^(hard|soft)$")


# Khoá hợp lệ của mastery_weights. Gõ sai tên khoá không làm gãy gì — trọng số đó chỉ
# lặng lẽ không bao giờ khớp điểm nào, và bài nhẹ đi đúng phần đó.
MASTERY_KINDS = {"speak", "listen", "read", "write", "quiz"}


class Unlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mastery_threshold: int = Field(default=80, ge=50, le=100)
    mastery_weights: dict[str, float] = {
        "speak": 0.30, "listen": 0.20, "read": 0.15, "write": 0.15, "quiz": 0.20,
    }
    min_speaking_attempts: int = Field(default=4, ge=0)
    challenge_threshold: int = Field(default=85, ge=50, le=100)
    # Ngưỡng tối thiểu cho từng kỹ năng, dùng ở checkpoint. Điểm tổng có thể che một kỹ năng
    # yếu: đọc 90 kéo nói 40 lên vẫn qua, và tuyên bố đầu ra của level thành lời hứa suông.
    min_per_skill: dict[str, int] = {}

    @field_validator("min_per_skill")
    @classmethod
    def per_skill_hop_le(cls, v: dict[str, int]) -> dict[str, int]:
        la = set(v) - MASTERY_KINDS
        if la:
            raise ValueError(f"min_per_skill có khoá lạ {sorted(la)}")
        for k, n in v.items():
            if not 0 <= n <= 100:
                raise ValueError(f"min_per_skill['{k}'] = {n}, phải trong 0..100")
        return v

    @field_validator("mastery_weights")
    @classmethod
    def weights_sum_to_one(cls, v: dict[str, float]) -> dict[str, float]:
        la = set(v) - MASTERY_KINDS
        if la:
            raise ValueError(
                f"mastery_weights có khoá lạ {sorted(la)} — hợp lệ: {sorted(MASTERY_KINDS)}"
            )
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
    # Bài dài là bài không được học. Trần nới từ 12 lên 16 khi thêm Đọc + Viết vào mọi bài:
    # đọc ~2 phút, viết ~3 phút. Player chia hai khối (nghe-nói / đọc-viết) để dừng giữa được.
    est_minutes: int = Field(default=10, ge=3, le=16)
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
    reading_passage: ReadingPassage | None = None
    writing_task: WritingTask | None = None
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
