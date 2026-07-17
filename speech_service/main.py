"""Speech service: /transcribe và /synthesize.

Tách container để web process luôn nhẹ. Model nạp lười, tự giải phóng sau 10 phút
không dùng, và tối đa 2 job ASR song song — không có semaphore này thì 5 người
bấm ghi âm cùng lúc là máy 8GB swap.
"""
import asyncio
import logging
import os
import tempfile
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from speech_service import asr, tts
from speech_service.feedback_vi import build_feedback
from speech_service.scoring import score_attempt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("speech")

MAX_CONCURRENT = int(os.getenv("SPEECH_MAX_CONCURRENT", "2"))
IDLE_UNLOAD_S = int(os.getenv("SPEECH_IDLE_UNLOAD_S", "600"))
ENGINE_VERSION = "whisper-" + os.getenv("WHISPER_MODEL", "small") + "+scoring-1"

_sem = asyncio.Semaphore(MAX_CONCURRENT)
_last_used = time.monotonic()


async def _idle_reaper() -> None:
    while True:
        await asyncio.sleep(60)
        if asr.is_loaded() and time.monotonic() - _last_used > IDLE_UNLOAD_S:
            asr.unload()
            log.info("model unloaded after idle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_idle_reaper())
    log.info("speech service up (max_concurrent=%s, idle_unload=%ss)", MAX_CONCURRENT, IDLE_UNLOAD_S)
    yield
    task.cancel()
    asr.unload()


app = FastAPI(title="Speech Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": asr.is_loaded(),
        "engine": ENGINE_VERSION,
        "queue_free": _sem._value,
        "tts_available": tts.is_available(),
    }


@app.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    expected_text: str = Form(""),
    kind: str = Form("read_aloud"),
    accept_patterns: str = Form(""),
):
    """Nhận WAV 16k mono (app đã chuẩn hoá bằng ffmpeg). Trả transcript + 3 trục điểm."""
    global _last_used
    data = await audio.read()
    if len(data) < 1000:
        raise HTTPException(400, "Audio quá ngắn hoặc rỗng.")

    try:
        await asyncio.wait_for(_sem.acquire(), timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(503, "Hệ thống đang bận. Bạn thử lại sau vài giây nhé.") from None

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        _last_used = time.monotonic()
        result = await asyncio.to_thread(asr.transcribe, tmp_path, expected_text)
        _last_used = time.monotonic()
    finally:
        _sem.release()
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    patterns = [p for p in accept_patterns.split("|") if p.strip()]
    scores = score_attempt(
        expected_text=expected_text, transcript=result["text"], words=result["words"],
        duration_s=result["duration_s"], kind=kind, accept_patterns=patterns,
    )
    scores["transcript"] = result["text"]
    scores["duration_ms"] = int(result["duration_s"] * 1000)
    scores["engine_version"] = ENGINE_VERSION
    scores["feedback_vi"] = build_feedback(scores, kind)
    return scores


class SynthIn(BaseModel):
    text: str
    voice: str = "en_US_female"
    speed: float = 1.0


@app.post("/synthesize")
async def synthesize(payload: SynthIn):
    """Trả WAV bytes. Chỉ dùng lúc seed và khi admin lưu item mới — không nằm trên đường học."""
    if not payload.text.strip():
        raise HTTPException(400, "Text rỗng.")
    try:
        wav = await asyncio.to_thread(tts.synthesize, payload.text, payload.voice, payload.speed)
    except tts.TTSError as exc:
        raise HTTPException(503, str(exc)) from exc
    from fastapi.responses import Response

    return Response(content=wav, media_type="audio/wav")
