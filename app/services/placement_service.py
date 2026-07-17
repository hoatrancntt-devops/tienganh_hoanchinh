"""Placement test (PART I). Chấm 100% bằng luật — chi phí AI bằng 0."""
import logging
import uuid
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utcnow
from app.models.assessment import CEFR_ORDER, PlacementResponse, PlacementTest
from app.models.content import Lesson
from app.models.enums import Cefr
from app.models.user import User
from app.services import prerequisite_service as prereq

log = logging.getLogger(__name__)

FORMS_DIR = Path("seeds/placement")
_forms_cache: dict[str, dict] = {}

WEIGHTS = {"knowledge": 0.30, "listening": 0.30, "speaking": 0.40}  # nói nặng nhất: đó là mục tiêu
BANDS = [(35, Cefr.PRE_A1), (65, Cefr.A1), (101, Cefr.A2)]
ENTRY_LESSON = {Cefr.PRE_A1: "F01", Cefr.A1: "F05", Cefr.A2: "D01"}
REPLAY_PENALTY = 0.15  # nghe 3 lần mới hiểu thì chưa thực sự nghe hiểu


def load_form(form: str = "A") -> dict:
    if form in _forms_cache:
        return _forms_cache[form]
    path = FORMS_DIR / f"form_{form.lower()}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy form xếp lớp: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    _forms_cache[form] = data
    return data


async def start_test(db: AsyncSession, user: User, form: str = "A") -> PlacementTest:
    test = PlacementTest(user_id=user.id, form=form.upper(), started_at=utcnow())
    db.add(test)
    await db.commit()
    await db.refresh(test)
    return test


def _score_mcq(item: dict, choice_index: int | None, replay_count: int) -> tuple[bool, float]:
    correct = choice_index is not None and choice_index == item["answer"]
    if not correct:
        return False, 0.0
    weight = item.get("difficulty", 2)
    score = 100.0 * (0.5 + 0.5 * weight / 5)          # câu khó đúng đáng giá hơn câu dễ đúng
    score *= max(0.0, 1 - REPLAY_PENALTY * replay_count)
    return True, round(min(100.0, score), 2)


def _score_speaking(item: dict, speech: dict | None) -> dict:
    """speech: kết quả từ speech_service (pronunciation/fluency/communication)."""
    if not speech:
        return {"pronunciation": 0.0, "fluency": 0.0, "communication": 0.0, "score": 0.0,
                "silent": True}
    kind = item["kind"]
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
    silent = not str(speech.get("transcript", "")).strip()
    return {"pronunciation": pron, "fluency": flu, "communication": comm,
            "score": round(score, 2), "silent": silent}


async def submit(
    db: AsyncSession, test: PlacementTest, responses: list[dict], speech_results: dict | None = None
) -> dict:
    """responses: list dict theo ResponseIn. speech_results: {item_ref: {...}} từ speech service."""
    form = load_form(test.form)
    items = {i["id"]: i for i in form["items"]}
    speech_results = speech_results or {}

    buckets: dict[str, list[float]] = {"vocab": [], "grammar": [], "listening": [], "speaking": []}
    speak_detail: dict[str, list[float]] = {"pronunciation": [], "fluency": [], "communication": []}
    self_answers: list[int] = []
    silent_count = 0

    for resp in responses:
        item = items.get(resp["item_ref"])
        if not item:
            continue
        row = PlacementResponse(
            test_id=test.id, item_ref=resp["item_ref"], section=resp["section"],
            kind=resp["kind"], choice_index=resp.get("choice_index"),
            audio_ref=resp.get("audio_ref"), latency_ms=resp.get("latency_ms", 0),
            replay_count=resp.get("replay_count", 0),
        )
        if resp["section"] == "self":
            self_answers.append(resp.get("choice_index") or 0)
            row.score = 0.0
        elif resp["section"] == "speaking":
            detail = _score_speaking(item, speech_results.get(resp["item_ref"]))
            row.score = detail["score"]
            row.is_correct = detail["score"] >= 50
            row.detail = detail
            buckets["speaking"].append(detail["score"])
            for key in speak_detail:
                speak_detail[key].append(detail[key])
            if detail["silent"]:
                silent_count += 1
        else:
            ok, score = _score_mcq(item, resp.get("choice_index"), resp.get("replay_count", 0))
            row.is_correct, row.score = ok, score
            buckets[resp["section"]].append(score)
        db.add(row)

    def avg(vals: list[float]) -> float:
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    knowledge = avg(buckets["vocab"] + buckets["grammar"])
    listening = avg(buckets["listening"])
    speaking = avg(buckets["speaking"])
    speech_available = bool(buckets["speaking"])

    if speech_available:
        overall = (
            WEIGHTS["knowledge"] * knowledge
            + WEIGHTS["listening"] * listening
            + WEIGHTS["speaking"] * speaking
        )
    else:
        overall = 0.5 * knowledge + 0.5 * listening

    band = next(cefr for limit, cefr in BANDS if overall < limit)
    confidence = "high"
    notes: list[str] = []

    # Sàn im lặng: >=3/5 lượt nói rỗng -> Pre-A1, không tính trung bình.
    if silent_count >= 3:
        band, confidence = Cefr.PRE_A1, "low"
        notes.append("Phần nói gần như không có dữ liệu.")
    else:
        # Speaking có quyền phủ quyết: đọc hiểu tốt nhưng câm thì bắt đầu ở chỗ tập nói.
        if speech_available and speaking < 30 and band != Cefr.PRE_A1:
            band = CEFR_ORDER[max(0, CEFR_ORDER.index(band) - 1)]
            notes.append("Điểm nói thấp nên lộ trình bắt đầu sớm hơn một bậc.")
        if not speech_available:
            band = CEFR_ORDER[max(0, CEFR_ORDER.index(band) - 1)]
            confidence = "low"
            notes.append("Chưa chấm được phần nói nên hệ thống xếp thận trọng.")

    # Tự đánh giá: KHÔNG cộng điểm. Chỉ phá thế cân bằng + đặt confidence.
    self_avg = sum(self_answers) / len(self_answers) if self_answers else 3.0
    near_edge = any(abs(overall - limit) <= 3 for limit, _ in BANDS[:-1])
    if near_edge and CEFR_ORDER.index(band) > 0:
        band = CEFR_ORDER[CEFR_ORDER.index(band) - 1]  # sát biên -> nghiêng về phía thấp hơn
        notes.append("Điểm nằm sát ranh giới nên xếp về mức thấp hơn cho chắc.")
    measured_level = CEFR_ORDER.index(band) + 1
    if abs(self_avg - measured_level * 1.5) >= 2 and confidence == "high":
        confidence = "low"

    strengths, gaps = [], []
    if listening >= 60:
        strengths.append("Nghe hiểu câu ngắn khá tốt")
    if speaking >= 60:
        strengths.append("Phát âm rõ, người nghe hiểu được")
    if knowledge >= 60:
        strengths.append("Vốn từ nền đủ dùng")
    if speaking < 45:
        gaps.append("Nói còn ngập ngừng và thiếu âm cuối")
    if listening < 45:
        gaps.append("Chưa bắt kịp khi người nói nói ở tốc độ thật")
    if knowledge < 45:
        gaps.append("Thiếu vốn từ công sở cơ bản")

    band_vi = {Cefr.PRE_A1: "chưa có nền (Pre-A1)", Cefr.A1: "sơ cấp (A1)",
               Cefr.A2: "sơ trung cấp (A2)"}[band]
    explanation = (
        f"Bạn đang ở mức {band_vi}. Điểm nghe {listening:.0f}, nói {speaking:.0f}, "
        f"từ vựng và ngữ pháp {knowledge:.0f} trên thang 100. "
    )
    if self_answers and self_avg <= 2 and speaking >= 55:
        explanation += (
            "Bạn tự nhận là chưa dám nói, nhưng phần phát âm của bạn khá ổn — "
            "vấn đề là sự tự tin, không phải năng lực. "
        )
    explanation += " ".join(notes)
    explanation += (
        " Lộ trình sẽ bắt đầu từ chỗ hợp với bạn nhất, và bạn có thể thi vượt "
        "bất cứ bài nào nếu thấy quá dễ."
    )

    entry_code = ENTRY_LESSON[band]
    entry = (
        await db.execute(select(Lesson).where(Lesson.code == entry_code))
    ).scalar_one_or_none()

    test.finished_at = utcnow()
    test.result_cefr = band
    test.confidence = confidence
    test.result_scores = {"knowledge": knowledge, "listening": listening,
                          "speaking": speaking, "overall": round(overall, 2)}
    test.explanation_vi = explanation
    test.entry_lesson_id = entry.id if entry else None
    test.can_challenge = confidence == "low"
    await db.commit()

    if entry:
        # Chỉ mở khoá. Không đánh dấu mastered — nếu không, placement làm rỗng ruột anti-skip.
        await prereq.unlock_from_placement(db, test.user_id, entry)
        user = await db.get(User, test.user_id)
        if user:
            await db.refresh(user, ["profile"])  # profile là lazy relationship, phải nạp trước
            if user.profile:
                user.profile.cefr_level_current = band
                user.profile.onboarded_at = utcnow()
                await db.commit()

    weeks = {Cefr.PRE_A1: 14, Cefr.A1: 10, Cefr.A2: 7}[band]
    return {
        "test_id": test.id, "result_cefr": band, "confidence": confidence,
        "scores": test.result_scores,
        "speaking_detail": {k: avg(v) for k, v in speak_detail.items()},
        "entry_lesson_code": entry_code, "strengths_vi": strengths[:2], "gaps_vi": gaps[:2],
        "explanation_vi": explanation, "estimated_weeks_to_goal": weeks,
        "can_challenge": test.can_challenge,
    }


async def can_retake(db: AsyncSession, user_id: uuid.UUID) -> tuple[bool, str]:
    stmt = (
        select(PlacementTest)
        .where(PlacementTest.user_id == user_id, PlacementTest.finished_at.isnot(None))
        .order_by(PlacementTest.finished_at.desc())
    )
    last = (await db.execute(stmt)).scalars().first()
    if last is None:
        return True, ""
    if last.confidence == "low":
        return True, ""  # kết quả không chắc chắn -> cho làm lại ngay
    finished = last.finished_at
    if finished.tzinfo is None:
        from datetime import timezone as _tz
        finished = finished.replace(tzinfo=_tz.utc)
    days = (utcnow() - finished).days
    if days >= 14:
        return True, ""
    return False, f"Bạn có thể làm lại sau {14 - days} ngày nữa."
