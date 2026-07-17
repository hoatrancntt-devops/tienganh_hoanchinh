"""Piper qua CLI. Audio sinh sẵn lúc seed -> chi phí runtime của phần nghe bằng 0."""
import logging
import os
import shutil
import subprocess
import tempfile

log = logging.getLogger("speech.tts")

VOICES_DIR = os.getenv("PIPER_VOICES_DIR", "/opt/piper/voices")
VOICE_MAP = {
    "en_US_female": os.getenv("PIPER_VOICE_F", "en_US-amy-medium.onnx"),
    "en_US_male": os.getenv("PIPER_VOICE_M", "en_US-ryan-medium.onnx"),
}


class TTSError(Exception):
    pass


def _binary() -> str | None:
    return shutil.which("piper") or (
        "/opt/piper/piper" if os.path.exists("/opt/piper/piper") else None
    )


def is_available() -> bool:
    if _binary() is None:
        return False
    return any(os.path.exists(os.path.join(VOICES_DIR, v)) for v in VOICE_MAP.values())


def synthesize(text: str, voice: str = "en_US_female", speed: float = 1.0) -> bytes:
    binary = _binary()
    if binary is None:
        raise TTSError("Không tìm thấy piper. Kiểm tra image speech.")
    model = os.path.join(VOICES_DIR, VOICE_MAP.get(voice, VOICE_MAP["en_US_female"]))
    if not os.path.exists(model):
        raise TTSError(f"Không tìm thấy voice: {model}")
    length_scale = round(1.0 / max(0.5, min(1.5, speed)), 3)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out = tmp.name
    try:
        proc = subprocess.run(
            [binary, "--model", model, "--output_file", out, "--length_scale", str(length_scale)],
            input=text.encode(), capture_output=True, timeout=60,
        )
        if proc.returncode != 0:
            raise TTSError(f"piper lỗi: {proc.stderr.decode()[:200]}")
        with open(out, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(out):
            os.unlink(out)
