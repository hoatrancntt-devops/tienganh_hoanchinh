"""Nhận audio từ trình duyệt, chuẩn hoá bằng ffmpeg, gọi speech service, lưu điểm.

Chuẩn hoá ở SERVER chứ không tin client: Safari iOS cho mp4/aac, Chrome cho webm/opus.
"""
import logging
import subprocess
import tempfile
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.assessment import PlacementTest, SpeechAttempt
from app.models.content import Activity, Item, Lesson
from app.models.enums import NotifType
from app.models.progress import ItemAttempt
from app.models.user import User
from app.services import learning_path_service as path
from app.services import notification_service as notif

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/speech", tags=["speech"])
settings = get_settings()

MAX_BYTES = 4 * 1024 * 1024   # ~60s audio nén; câu học dài nhất ~15s
MAX_SECONDS = 30

# Kết quả chấm nói của placement, giữ phía server để client không thể tự khai điểm.
# Buffer tiến trình: đủ cho 1 worker của MVP; nhiều worker cần chuyển sang bảng riêng.
PLACEMENT_SPEECH: dict[str, dict[str, dict]] = {}


def _normalize(raw: bytes) -> bytes:
    """Về WAV 16kHz mono — định dạng duy nhất whisper nhận."""
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as src:
        src.write(raw)
        src_path = src.name
    dst_path = src_path + ".wav"
    try:
        proc = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", src_path, "-t", str(MAX_SECONDS),
             "-ac", "1", "-ar", "16000", "-f", "wav", dst_path],
            capture_output=True, timeout=30,
        )
        if proc.returncode != 0:
            raise HTTPException(400, "Không đọc được file ghi âm. Bạn thử ghi lại nhé.")
        return Path(dst_path).read_bytes()
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(400, "File ghi âm quá dài.") from exc
    finally:
        for p in (src_path, dst_path):
            Path(p).unlink(missing_ok=True)


async def _call_speech(wav: bytes, expected: str, kind: str, patterns: list[str]) -> dict:
    if not settings.SPEECH_ENABLED:
        raise HTTPException(503, "Chấm nói đang tắt.")
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.SPEECH_SERVICE_URL}/transcribe",
                files={"audio": ("a.wav", wav, "audio/wav")},
                data={"expected_text": expected or "", "kind": kind,
                      "accept_patterns": "|".join(patterns or [])},
            )
    except httpx.RequestError as exc:
        log.warning("speech service unreachable: %s", exc)
        raise HTTPException(503, "Dịch vụ chấm nói chưa sẵn sàng. Bạn thử lại sau ít phút.") from exc
    if resp.status_code == 503:
        raise HTTPException(503, resp.json().get("detail", "Hệ thống đang bận."))
    if resp.status_code >= 400:
        raise HTTPException(502, "Chấm nói lỗi. Bạn thử lại nhé.")
    return resp.json()


async def _read_audio(audio: UploadFile) -> bytes:
    raw = await audio.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File ghi âm quá lớn.")
    if len(raw) < 800:
        raise HTTPException(400, "Chưa nghe được gì. Bạn nói to hơn nhé.")
    return raw


@router.get("/health")
async def speech_health():
    if not settings.SPEECH_ENABLED:
        return {"available": False, "reason": "disabled"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{settings.SPEECH_SERVICE_URL}/health")
        return {"available": r.status_code == 200, **r.json()}
    except httpx.RequestError:
        return {"available": False, "reason": "unreachable"}


@router.post("/attempt")
async def speech_attempt(
    audio: UploadFile = File(...),
    item_id: uuid.UUID = Form(...),
    is_preview: bool = Form(False),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    item = await db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy câu hỏi.")
    activity = await db.get(Activity, item.activity_id)
    lesson = await db.get(Lesson, activity.lesson_id)

    wav = _normalize(await _read_audio(audio))
    result = await _call_speech(wav, item.expected_text or "", item.kind, item.accept_patterns)

    # Lưu audio để học viên nghe lại — tự so sánh với giọng mẫu là phần dạy học
    # có giá trị nhất, độc lập với thuật toán.
    rel = f"attempts/{user.id}/{uuid.uuid4().hex}.wav"
    dest = Path(settings.MEDIA_DIR) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(wav)

    db.add(SpeechAttempt(
        user_id=user.id, item_id=item.id, lesson_id=lesson.id, audio_path=rel,
        transcript=result["transcript"],
        score_pronunciation=result["pronunciation"], score_fluency=result["fluency"],
        score_communication=result["communication"], score_overall=result["overall"],
        wpm=result["wpm"], pause_ratio=result["pause_ratio"],
        phoneme_diff=result["phoneme_diff"], feedback_vi=result["feedback_vi"],
        engine_version=result["engine_version"], duration_ms=result["duration_ms"],
        is_preview=is_preview,
    ))
    db.add(ItemAttempt(
        user_id=user.id, item_id=item.id, lesson_id=lesson.id,
        activity_kind=activity.kind, is_correct=result["overall"] >= 70,
        score=result["overall"], response={"transcript": result["transcript"]},
        is_preview=is_preview,
    ))
    await db.commit()

    payload = {
        "score_pronunciation": result["pronunciation"],
        "score_fluency": result["fluency"],
        "score_communication": result["communication"],
        "score_overall": result["overall"],
        "transcript": result["transcript"],
        "phoneme_diff": result["phoneme_diff"],
        "feedback_vi": result["feedback_vi"],
        "audio_url": f"/media/{rel}",
    }
    if is_preview:
        payload.update({"mastery_raw": 0.0, "state": "previewable", "unlocked_codes": []})
        return payload

    progress = await path.update_mastery(db, user.id, lesson.id)
    await path.schedule_reviews(db, user.id, [item.id])
    await db.refresh(user, ["profile"])
    await notif.record_study(db, user)

    if progress["unlocked_codes"]:
        await notif.notify(
            db, user, NotifType.LESSON_UNLOCKED,
            f"{len(progress['unlocked_codes'])} bài mới đã mở",
            ", ".join(progress["unlocked_codes"]), link="/learn",
            dedup_key=f"unlock:{lesson.code}", expires_days=7,
        )
    if lesson.is_checkpoint and progress["state"] == "mastered":
        await notif.notify(
            db, user, NotifType.CHECKPOINT_PASSED, f"Bạn đã vượt {lesson.title_vi}",
            "Phase tiếp theo đã mở.", link="/learn",
            dedup_key=f"cp:{lesson.code}", email=True,
        )

    payload.update({
        "mastery_raw": progress["mastery_raw"], "state": progress["state"],
        "unlocked_codes": progress["unlocked_codes"],
    })
    return payload


@router.post("/placement")
async def placement_speech(
    audio: UploadFile = File(...),
    test_id: uuid.UUID = Form(...),
    item_ref: str = Form(...),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """Chấm một lượt nói của bài xếp lớp. Điểm giữ phía server tới lúc nộp bài."""
    from app.services.placement_service import load_form

    test = await db.get(PlacementTest, test_id)
    if test is None or test.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bài test.")
    if test.finished_at:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài test đã nộp.")

    form = load_form(test.form)
    item = next((i for i in form["items"] if i["id"] == item_ref), None)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Câu này không có trong đề.")

    wav = _normalize(await _read_audio(audio))
    result = await _call_speech(
        wav, item.get("expected_text") or "", item["kind"], item.get("accept_patterns", [])
    )

    PLACEMENT_SPEECH.setdefault(str(test_id), {})[item_ref] = {
        "pronunciation": result["pronunciation"],
        "fluency": result["fluency"],
        "communication": result["communication"],
        "transcript": result["transcript"],
    }

    db.add(SpeechAttempt(
        user_id=user.id, audio_path="", transcript=result["transcript"],
        score_pronunciation=result["pronunciation"], score_fluency=result["fluency"],
        score_communication=result["communication"], score_overall=result["overall"],
        wpm=result["wpm"], pause_ratio=result["pause_ratio"],
        phoneme_diff=result["phoneme_diff"], feedback_vi=result["feedback_vi"],
        engine_version=result["engine_version"], duration_ms=result["duration_ms"],
    ))
    await db.commit()

    # Không trả điểm cho client: học viên đang thi, biết điểm từng câu sẽ đoán được đề.
    return {"ok": True}


def take_placement_speech(test_id: uuid.UUID) -> dict:
    """Lấy và xoá buffer. Gọi đúng một lần lúc nộp bài."""
    return PLACEMENT_SPEECH.pop(str(test_id), {})
