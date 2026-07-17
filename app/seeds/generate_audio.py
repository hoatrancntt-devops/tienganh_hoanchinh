"""Sinh audio bằng Piper qua speech service, lưu ra media/, bỏ qua file đã có.

Chạy lúc seed, KHÔNG lúc build: giữ image nhỏ. Chi phí runtime của phần nghe bằng 0.
"""
import asyncio
import hashlib
import logging
from pathlib import Path

import httpx
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.content import Item, MediaAsset

log = logging.getLogger(__name__)
settings = get_settings()

PLACEMENT_DIR = Path("seeds/placement")


async def _synth(client: httpx.AsyncClient, text: str, voice: str, speed: float) -> bytes | None:
    try:
        r = await client.post(
            f"{settings.SPEECH_SERVICE_URL}/synthesize",
            json={"text": text, "voice": voice, "speed": speed}, timeout=60,
        )
    except httpx.RequestError as exc:
        log.warning("speech service không tới được: %s", exc)
        return None
    if r.status_code != 200:
        log.warning("synthesize lỗi (%s): %s", r.status_code, r.text[:120])
        return None
    return r.content


async def _write(db: AsyncSession, dest: Path, wav: bytes, voice: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(wav)
    checksum = hashlib.sha256(wav).hexdigest()
    rel = str(dest.relative_to(settings.MEDIA_DIR))
    exists = (
        await db.execute(select(MediaAsset).where(MediaAsset.path == rel))
    ).scalar_one_or_none()
    if exists is None:
        db.add(MediaAsset(kind="audio", path=rel, checksum=checksum, voice=voice))
        await db.commit()


async def generate_all(db: AsyncSession, force: bool = False) -> dict:
    media = Path(settings.MEDIA_DIR)
    made = skipped = failed = 0

    async with httpx.AsyncClient() as client:
        try:
            health = await client.get(f"{settings.SPEECH_SERVICE_URL}/health", timeout=5)
            if not health.json().get("tts_available"):
                log.warning("Piper chưa sẵn sàng — bỏ qua sinh audio. App vẫn chạy, thiếu tiếng.")
                return {"made": 0, "skipped": 0, "failed": 0, "reason": "tts_unavailable"}
        except httpx.RequestError:
            log.warning("speech service chưa lên — bỏ qua sinh audio.")
            return {"made": 0, "skipped": 0, "failed": 0, "reason": "service_down"}

        # 1. Item có expected_text (drill nói + quiz nghe)
        items = (
            await db.execute(select(Item).where(Item.expected_text.isnot(None)))
        ).scalars().all()
        for item in items:
            dest = media / "tts" / f"{item.id}.wav"
            if dest.exists() and not force:
                skipped += 1
                continue
            # Foundation nói chậm hơn: 0.85x. Phần còn lại tốc độ thật.
            speed = 0.85 if "foundation" in (item.tags or []) else 1.0
            wav = await _synth(client, item.expected_text, "en_US_female", speed)
            if wav is None:
                failed += 1
                continue
            await _write(db, dest, wav, "en_US_female")
            made += 1

        # 2. Câu nghe của bài xếp lớp
        for path in sorted(PLACEMENT_DIR.glob("form_*.yaml")):
            form = yaml.safe_load(path.read_text(encoding="utf-8"))
            for spec in form["items"]:
                text = spec.get("transcript_en") or spec.get("expected_text")
                if not text or spec["section"] not in ("listening", "speaking"):
                    continue
                if spec["section"] == "speaking" and spec["kind"] != "repeat":
                    continue  # read_aloud có chữ trên màn hình, không cần tiếng
                dest = media / "placement" / f"{spec['id']}.wav"
                if dest.exists() and not force:
                    skipped += 1
                    continue
                wav = await _synth(client, text, "en_US_female", 1.0)
                if wav is None:
                    failed += 1
                    continue
                await _write(db, dest, wav, "en_US_female")
                made += 1

    log.info("audio: %s mới, %s bỏ qua, %s lỗi", made, skipped, failed)
    return {"made": made, "skipped": skipped, "failed": failed}


if __name__ == "__main__":
    from app.core.logging import setup_logging
    from app.db.session import SessionLocal

    async def _main():
        setup_logging()
        async with SessionLocal() as db:
            await generate_all(db)

    asyncio.run(_main())
