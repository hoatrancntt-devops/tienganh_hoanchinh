"""Phần chấm thuần của bài xếp lớp — không chạm DB, không async, test được trực tiếp.

Tách khỏi `placement_service` để mọi luật xếp band có thể kiểm chứng bằng test đơn vị.
`placement_service` giữ phần I/O: nạp form, ghi DB, mở khoá bài.
"""
from dataclasses import dataclass, field

from app.models.assessment import CEFR_ORDER
from app.models.enums import Cefr

# Nói nặng nhất vì đó là mục tiêu sản phẩm. Ba trục phải cộng đúng 1.0.
WEIGHTS = {"knowledge": 0.30, "listening": 0.30, "speaking": 0.40}

# Mốc cắt trên thang 0-100. Mốc cuối là trần mở để band cao nhất luôn có chỗ.
#
# Luật "sát biên" bên dưới hạ một bậc khi điểm nằm trong NEAR_EDGE của một mốc, nên mốc
# HIỆU DỤNG cao hơn mốc ghi ở đây đúng NEAR_EDGE điểm. Các con số dưới đây đã trừ sẵn
# phần bù đó để mốc hiệu dụng rơi vào 30 / 60 / 82 — tương ứng: đúng ~40% -> A1,
# ~70% -> A2, gần hết + nói khá -> B1. Sửa NEAR_EDGE thì phải sửa cả đây.
# `test_moc_cat_hieu_dung_dung_nhu_thiet_ke` khoá bất biến này.
BANDS: list[tuple[float, Cefr]] = [
    (27.0, Cefr.PRE_A1),
    (57.0, Cefr.A1),
    (79.0, Cefr.A2),
    (101.0, Cefr.B1),
]

# Bài đầu của mỗi level, theo bảng ánh xạ level trong docs/khung-level.md.
ENTRY_LESSON = {
    Cefr.PRE_A1: "F01",
    Cefr.A1: "F05",
    Cefr.A2: "F09",
    Cefr.B1: "F18",
}

WEEKS_TO_GOAL = {Cefr.PRE_A1: 16, Cefr.A1: 12, Cefr.A2: 8, Cefr.B1: 5}

# Nghe lại lần đầu là để làm quen giọng, không phạt. Từ lần thứ hai mới trừ, và có trần.
REPLAY_FREE = 1
REPLAY_PENALTY = 0.10
REPLAY_PENALTY_CAP = 0.20

# Câu dễ trả lời đúng vẫn là trả lời đúng. Nền 0.8 giữ cho thang không bị nén xuống đáy.
SCORE_BASE = 0.8
SCORE_SPREAD = 0.2

SILENT_FLOOR = 3            # số lượt nói có tiếng nhưng rỗng chữ -> sàn Pre-A1
NEAR_EDGE = 3.0             # khoảng cách tới mốc cắt được coi là "sát biên"
SPEAKING_VETO = 30.0        # dưới mức này thì nói chưa dùng được, dù điểm giấy cao
IMBALANCE_SPREAD = 40.0     # chênh lệch giữa trục cao nhất và thấp nhất -> kết quả kém tin cậy
SLOW_FACTOR = 3.0           # chậm hơn ngần này lần trung vị của chính học viên -> nghi đoán mò


def score_mcq(difficulty: int, correct: bool, replay_count: int, is_listening: bool) -> float:
    """Điểm một câu trắc nghiệm, thang 0-100."""
    if not correct:
        return 0.0
    score = 100.0 * (SCORE_BASE + SCORE_SPREAD * difficulty / 5)
    if is_listening:
        billable = max(0, replay_count - REPLAY_FREE)
        score *= 1 - min(REPLAY_PENALTY_CAP, REPLAY_PENALTY * billable)
    return round(min(100.0, score), 2)


def score_speaking(kind: str, speech: dict | None) -> dict:
    """speech: kết quả từ speech_service, hoặc None khi không thu được gì.

    Phân biệt hai tình huống mà bản cũ gộp làm một:
    - `no_data`: không có kết quả chấm (micro hỏng, service chết) -> thiếu dữ liệu
    - `silent`: có audio hợp lệ nhưng không ra chữ nào -> học viên thực sự không nói được
    Gộp hai thứ này lại chính là nguyên nhân một sự cố micro kéo band xuống tận Pre-A1.
    """
    if not speech:
        return {"pronunciation": 0.0, "fluency": 0.0, "communication": 0.0,
                "score": 0.0, "silent": False, "no_data": True}
    pron = float(speech.get("pronunciation", 0))
    flu = float(speech.get("fluency", 0))
    comm = float(speech.get("communication", 0))
    if kind == "read_aloud":
        score = pron
    elif kind == "repeat":
        # đo trí nhớ làm việc thính giác: người mất gốc rơi rụng nửa cuối câu
        score = 0.6 * pron + 0.4 * comm
    else:  # short_answer
        score = 0.5 * comm + 0.3 * flu + 0.2 * pron
    return {"pronunciation": pron, "fluency": flu, "communication": comm,
            "score": round(score, 2), "silent": not str(speech.get("transcript", "")).strip(),
            "no_data": False}


def section_average(earned: list[float], total_items: int) -> float:
    """Mẫu số là TOÀN BỘ câu của section trong form, không phải số câu đã trả lời.

    Bản cũ chia cho số câu đã trả lời, nên bỏ qua câu khó lại làm điểm tăng: trả lời đúng
    mỗi một câu khó nhất được 100 điểm, làm đúng cả chín câu chỉ được 78.
    """
    if total_items <= 0:
        return 0.0
    return round(sum(earned) / total_items, 2)


def band_for(overall: float) -> Cefr:
    return next(cefr for limit, cefr in BANDS if overall < limit)


def _demote(band: Cefr) -> Cefr:
    return CEFR_ORDER[max(0, CEFR_ORDER.index(band) - 1)]


def _barely_qualified(overall: float, band: Cefr) -> bool:
    """Vừa đủ điểm vào band này — tức là chỉ nhỉnh hơn mốc dưới của chính nó vài điểm.

    Chỉ xét phía TRÊN mốc. Bản cũ dùng `abs()` nên bắt cả phía dưới, nghĩa là người sắp
    lên hạng cũng bị hạ một bậc — phạt vì gần giỏi, không phải vì gần yếu.
    """
    index = CEFR_ORDER.index(band)
    if index == 0:
        return False                      # Pre-A1 là sàn, không có mốc dưới để bám
    lower_bound = BANDS[index - 1][0]
    return 0 <= overall - lower_bound <= NEAR_EDGE


def slow_answer_ratio(latencies: list[int]) -> float:
    """Tỉ lệ câu chậm bất thường so với trung vị của chính học viên đó.

    Dùng làm tín hiệu tin cậy, KHÔNG trừ điểm: chậm có thể là do suy nghĩ kỹ, do mạng,
    hoặc do đọc lại đề. Không đủ căn cứ để phạt.
    """
    usable = [ms for ms in latencies if ms > 0]
    if len(usable) < 4:
        return 0.0
    ordered = sorted(usable)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    if median <= 0:
        return 0.0
    return sum(1 for ms in usable if ms > SLOW_FACTOR * median) / len(usable)


@dataclass
class Verdict:
    band: Cefr
    band_raw: Cefr
    confidence: str
    overall: float
    notes: list[str] = field(default_factory=list)


def decide(
    knowledge: float,
    listening: float,
    speaking: float,
    speech_available: bool,
    silent_count: int,
    slow_ratio: float = 0.0,
) -> Verdict:
    """Xếp band từ ba trục điểm.

    Bất biến quan trọng: band cuối KHÔNG BAO GIỜ thấp hơn `band_raw` quá một bậc.
    Bản cũ có ba nhánh hạ bậc chạy nối tiếp và cộng dồn được, nên người nghe hiểu 90/100
    nhưng yếu nói bị đẩy về Pre-A1 — tức là về bài dạy âm /θ/.
    """
    if speech_available:
        overall = (
            WEIGHTS["knowledge"] * knowledge
            + WEIGHTS["listening"] * listening
            + WEIGHTS["speaking"] * speaking
        )
    else:
        # Chuẩn hoá lại trên hai trục còn lại thay vì bịa trọng số mới.
        w = WEIGHTS["knowledge"] + WEIGHTS["listening"]
        overall = (WEIGHTS["knowledge"] * knowledge + WEIGHTS["listening"] * listening) / w
    overall = round(overall, 2)

    band_raw = band_for(overall)

    # Sàn im lặng: có tiếng nhưng không ra chữ ở phần lớn lượt nói. Đây là kết luận
    # tự nó, không phải một lần hạ bậc — nên nó thoát sớm.
    if speech_available and silent_count >= SILENT_FLOOR:
        return Verdict(
            band=Cefr.PRE_A1, band_raw=band_raw, confidence="low", overall=overall,
            notes=["Phần nói gần như không có dữ liệu."],
        )

    # Gom mọi lý do hạ bậc rồi hạ ĐÚNG MỘT LẦN.
    reasons: list[str] = []
    if speech_available and speaking < SPEAKING_VETO and band_raw != Cefr.PRE_A1:
        reasons.append("Điểm nói thấp nên lộ trình bắt đầu sớm hơn một bậc.")
    if not speech_available:
        reasons.append("Chưa chấm được phần nói nên hệ thống xếp thận trọng.")
    if _barely_qualified(overall, band_raw):
        reasons.append("Điểm nằm sát ranh giới nên xếp về mức thấp hơn cho chắc.")

    band = _demote(band_raw) if reasons else band_raw

    axes = [knowledge, listening] + ([speaking] if speech_available else [])
    confidence = "high"
    if not speech_available:
        confidence = "low"
    elif max(axes) - min(axes) > IMBALANCE_SPREAD:
        confidence = "low"
        reasons.append("Các kỹ năng chênh nhau nhiều nên kết quả chỉ là ước lượng.")
    elif _barely_qualified(overall, band_raw):
        confidence = "low"
    elif slow_ratio > 0.5:
        confidence = "low"

    return Verdict(band=band, band_raw=band_raw, confidence=confidence,
                   overall=overall, notes=reasons)
