"""Placement test (PART I). Chấm 100% bằng luật — chi phí AI bằng 0.

Luật chấm nằm ở `placement_scoring` (thuần, test được). File này giữ phần I/O:
nạp form, ghi DB, mở khoá bài vào.
"""
import hashlib
import logging
import uuid
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utcnow
from app.models.assessment import PlacementResponse, PlacementTest
from app.models.content import Lesson
from app.models.enums import Cefr
from app.models.user import User
from app.services import placement_scoring as scoring
from app.services import prerequisite_service as prereq
from app.services import roadmap_service as roadmap
from app.services import writing_service as writing

log = logging.getLogger(__name__)

FORMS_DIR = Path("seeds/placement")
_forms_cache: dict[str, dict] = {}

# Tái xuất để route và test không phải biết module nào giữ hằng số.
ENTRY_LESSON = scoring.ENTRY_LESSON
BANDS = scoring.BANDS
WEIGHTS = scoring.WEIGHTS

MCQ_SECTIONS = ("vocab", "grammar", "listening", "reading")
BAND_VI = {
    Cefr.PRE_A1: "chưa có nền (Pre-A1)",
    Cefr.A1: "sơ cấp (A1)",
    Cefr.A2: "sơ trung cấp (A2)",
    Cefr.B1: "trung cấp (B1)",
}


def audio_text(item: dict) -> str | None:
    """Câu sẽ được đọc lên cho item này, hoặc None nếu item không có tiếng.

    Một chỗ duy nhất quyết định điều đó, để bộ sinh audio và API trả đề không lệch nhau.
    """
    if item.get("section") not in ("listening", "speaking"):
        return None
    if item.get("section") == "speaking" and item.get("kind") != "repeat":
        return None                       # read_aloud có chữ trên màn hình, không cần tiếng
    return item.get("transcript_en") or item.get("expected_text") or None


def audio_name(item: dict) -> str | None:
    """Tên file audio = mã câu + hash NỘI DUNG.

    Trước đây tên file chỉ là mã câu, mà bộ sinh audio bỏ qua file đã tồn tại. Nên khi sửa
    lời một câu nghe nhưng giữ nguyên mã, học viên vẫn nghe câu CŨ trong khi đề hỏi câu MỚI
    — và không có gì báo. Gắn hash nội dung vào tên khiến chuyện đó không xảy ra được nữa:
    lời đổi thì tên đổi, file cũ đơn giản là không ai dùng tới.
    """
    text = audio_text(item)
    if not text:
        return None
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{item['id']}-{digest}.wav"


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


def _section_sizes(form: dict) -> dict[str, int]:
    """Số câu mỗi section CÓ TRONG FORM — dùng làm mẫu số, không dùng số câu đã trả lời."""
    sizes: dict[str, int] = {}
    for item in form["items"]:
        sizes[item["section"]] = sizes.get(item["section"], 0) + 1
    return sizes


async def submit(
    db: AsyncSession, test: PlacementTest, responses: list[dict], speech_results: dict | None = None
) -> dict:
    """responses: list dict theo ResponseIn. speech_results: {item_ref: {...}} từ speech service."""
    form = load_form(test.form)
    items = {i["id"]: i for i in form["items"]}
    sizes = _section_sizes(form)
    speech_results = speech_results or {}

    earned: dict[str, list[float]] = {s: [] for s in MCQ_SECTIONS}
    write_scores: list[float] = []
    speak_scores: list[float] = []
    speak_detail: dict[str, list[float]] = {"pronunciation": [], "fluency": [], "communication": []}
    self_answers: list[int] = []
    latencies: list[int] = []
    silent_count = 0
    speech_seen = 0

    for resp in responses:
        item = items.get(resp["item_ref"])
        if not item:
            continue
        section = resp["section"]
        row = PlacementResponse(
            test_id=test.id, item_ref=resp["item_ref"], section=section,
            kind=resp["kind"], choice_index=resp.get("choice_index"),
            audio_ref=resp.get("audio_ref"), latency_ms=resp.get("latency_ms", 0),
            replay_count=resp.get("replay_count", 0),
        )
        if section == "self":
            choice = resp.get("choice_index")
            if choice is not None:          # bỏ trống KHÁC với "Không bao giờ"
                self_answers.append(choice)
            row.score = 0.0
        elif section == "speaking":
            detail = scoring.score_speaking(item["kind"], speech_results.get(resp["item_ref"]))
            row.score = detail["score"]
            row.is_correct = detail["score"] >= 50
            row.detail = detail
            if not detail["no_data"]:
                speech_seen += 1
                speak_scores.append(detail["score"])
                for key in speak_detail:
                    speak_detail[key].append(detail[key])
                if detail["silent"]:
                    silent_count += 1
        elif section == "writing":
            # Cùng bộ chấm với bài viết trong bài học — một luật, một chỗ sửa.
            graded = writing.grade(item, resp.get("texts") or [resp.get("text") or ""])
            row.score = float(graded["score"])
            row.is_correct = bool(graded["correct"])
            row.detail = {"feedback_vi": graded["feedback_vi"]}
            write_scores.append(row.score)
        elif section in earned:
            choice = resp.get("choice_index")
            correct = choice is not None and choice == item["answer"]
            score = scoring.score_mcq(
                difficulty=item.get("difficulty", 2), correct=correct,
                replay_count=resp.get("replay_count", 0), is_listening=section == "listening",
            )
            row.is_correct, row.score = correct, score
            earned[section].append(score)
            latencies.append(resp.get("latency_ms", 0))
        db.add(row)

    knowledge_total = sizes.get("vocab", 0) + sizes.get("grammar", 0)
    knowledge = scoring.section_average(earned["vocab"] + earned["grammar"], knowledge_total)
    listening = scoring.section_average(earned["listening"], sizes.get("listening", 0))
    reading = scoring.section_average(earned["reading"], sizes.get("reading", 0))
    writing_score = scoring.section_average(write_scores, sizes.get("writing", 0))
    speech_available = speech_seen > 0
    speaking = scoring.section_average(speak_scores, speech_seen) if speech_available else 0.0

    axes = {"knowledge": knowledge, "listening": listening, "reading": reading,
            "writing": writing_score, "speaking": speaking}
    verdict = scoring.decide(
        axes, speech_available=speech_available, silent_count=silent_count,
        slow_ratio=scoring.slow_answer_ratio(latencies),
    )
    band, confidence, overall = verdict.band, verdict.confidence, verdict.overall

    strengths, gaps = [], []
    if listening >= 60:
        strengths.append("Nghe hiểu câu ngắn khá tốt")
    if speaking >= 60:
        strengths.append("Phát âm rõ, người nghe hiểu được")
    if reading >= 60:
        strengths.append("Đọc email công việc lấy được ý chính")
    if writing_score >= 60:
        strengths.append("Viết được câu đủ ý, đúng cấu trúc")
    if knowledge >= 60:
        strengths.append("Vốn từ nền đủ dùng")
    if speech_available and speaking < 45:
        gaps.append("Nói còn ngập ngừng và thiếu âm cuối")
    if listening < 45:
        gaps.append("Chưa bắt kịp khi người nói nói ở tốc độ thật")
    if reading < 45:
        gaps.append("Đọc email còn phải dịch từng chữ")
    if writing_score < 45:
        gaps.append("Viết câu còn thiếu cấu trúc và từ nối")
    if knowledge < 45:
        gaps.append("Thiếu vốn từ công sở cơ bản")

    self_avg = sum(self_answers) / len(self_answers) if self_answers else None
    explanation = (
        f"Bạn đang ở mức {BAND_VI[band]}. Nghe {listening:.0f}, nói {speaking:.0f}, "
        f"đọc {reading:.0f}, viết {writing_score:.0f} trên thang 100 "
        f"(từ vựng và ngữ pháp {knowledge:.0f}). "
    )
    if self_avg is not None and self_avg <= 2 and speaking >= 55:
        explanation += (
            "Bạn tự nhận là chưa dám nói, nhưng phần phát âm của bạn khá ổn — "
            "vấn đề là sự tự tin, không phải năng lực. "
        )
    explanation += " ".join(verdict.notes)
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
                          "speaking": speaking, "reading": reading,
                          "writing": writing_score, "overall": overall}
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

    def avg(vals: list[float]) -> float:
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    return {
        "test_id": test.id, "result_cefr": band, "confidence": confidence,
        "scores": test.result_scores,
        "speaking_detail": {k: avg(v) for k, v in speak_detail.items()},
        "entry_lesson_code": entry_code, "strengths_vi": strengths[:2], "gaps_vi": gaps[:2],
        "explanation_vi": explanation,
        # Tính từ số bài còn lại và nhịp học thật, không phải hằng số theo band. Ngay sau khi
        # xếp lớp thì chưa có nhịp học nào nên nó rơi về mục tiêu học viên tự đặt ở onboarding.
        "estimated_weeks_to_goal": (await roadmap.cho_hoc_vien(db, test.user_id)).tuan_toi_da,
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
