"""faster-whisper, nạp lười, giải phóng được.

`initial_prompt` chứa câu đích rất quan trọng: whisper vốn hay TỰ SỬA lỗi phát âm về
từ đúng. Ép nó bám kịch bản để phần chấm còn nhìn thấy lỗi thật.
"""
import logging
import os
import wave

log = logging.getLogger("speech.asr")

MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE = os.getenv("WHISPER_COMPUTE", "int8")

_model = None


def is_loaded() -> bool:
    return _model is not None


def _load():
    global _model
    if _model is not None:
        return _model
    from faster_whisper import WhisperModel

    log.info("loading whisper %s (%s/%s)...", MODEL_NAME, DEVICE, COMPUTE)
    _model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE,
                          cpu_threads=int(os.getenv("WHISPER_THREADS", "2")))
    log.info("whisper loaded")
    return _model


def unload() -> None:
    global _model
    _model = None
    import gc

    gc.collect()


def _duration(path: str) -> float:
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate() or 16000)
    except Exception:
        return 0.0


def transcribe(path: str, expected_text: str = "") -> dict:
    model = _load()
    segments, info = model.transcribe(
        path, language="en", beam_size=1, vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 400},
        word_timestamps=True, condition_on_previous_text=False,
        initial_prompt=expected_text or None, temperature=0.0,
    )
    words, texts = [], []
    for seg in segments:
        texts.append(seg.text)
        for w in (seg.words or []):
            words.append({
                "word": w.word.strip(),
                "start": round(w.start, 3),
                "end": round(w.end, 3),
                "prob": round(getattr(w, "probability", 0.0) or 0.0, 3),
            })
    return {
        "text": " ".join(t.strip() for t in texts).strip(),
        "words": words,
        "duration_s": round(getattr(info, "duration", 0.0) or _duration(path), 3),
    }
