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
from app.models.content import Activity, Item, Lesson, MediaAsset
from app.models.enums import ActivityKind
from app.services import placement_service

log = logging.getLogger(__name__)
settings = get_settings()

PLACEMENT_DIR = Path("seeds/placement")


# Tốc độ đọc theo BẬC, không theo phase. Trước đây ba chỗ hardcode
# `0.85 if phase == "foundation" else 1.0`, nên F18-F20 (bậc B1) nói chậm 0.85 — chậm hơn
# cả bài A2 — còn toàn bộ bậc B1 không bao giờ vượt 1.0. Mục tiêu sản phẩm là standup và
# call với khách nước ngoài, nơi người ta nói nhanh hơn 1.0; học viên thạo hết ở 1.0 vẫn
# đứng hình trong cuộc gọi thật.
TOC_DO = {"pre_a1": 0.85, "a1": 0.9, "a2": 1.0, "b1": 1.1}


def toc_do_theo_bac(cefr: str) -> float:
    return TOC_DO.get(cefr, 1.0)


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

        # Bậc của từng Item, tra qua Activity -> Lesson. Cần trước khi sinh tiếng vì tốc độ
        # đọc lấy theo bậc.
        bac_cua_item = {
            item_id: cefr
            for item_id, cefr in (
                await db.execute(
                    select(Item.id, Lesson.cefr_target)
                    .join(Activity, Item.activity_id == Activity.id)
                    .join(Lesson, Activity.lesson_id == Lesson.id)
                )
            ).all()
        }

        # 1. Item có expected_text (drill nói + quiz nghe)
        items = (
            await db.execute(select(Item).where(Item.expected_text.isnot(None)))
        ).scalars().all()
        for item in items:
            dest = media / "tts" / f"{item.id}.wav"
            if dest.exists() and not force:
                skipped += 1
                continue
            speed = toc_do_theo_bac(bac_cua_item.get(item.id, "a2"))
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
                # Tên file gắn hash nội dung — xem placement_service.audio_name.
                text = placement_service.audio_text(spec)
                name = placement_service.audio_name(spec)
                if not text or not name:
                    continue
                dest = media / "placement" / name
                if dest.exists() and not force:
                    skipped += 1
                    continue
                wav = await _synth(client, text, "en_US_female", 1.0)
                if wav is None:
                    failed += 1
                    continue
                await _write(db, dest, wav, "en_US_female")
                made += 1

        # 3. Đoạn nghe của từng bài — câu hỏi nghe không có tiếng thì không trả lời được.
        listen_acts = (
            await db.execute(
                select(Activity, Lesson.cefr_target)
                .join(Lesson, Activity.lesson_id == Lesson.id)
                .where(Activity.kind == ActivityKind.LISTEN)
            )
        ).all()
        for act, cefr in listen_acts:
            text = ((act.config or {}).get("transcript_en") or "").strip()
            if not text:
                continue
            dest = media / "tts" / f"{act.id}.wav"
            if dest.exists() and not force:
                skipped += 1
                continue
            # Tốc độ theo bậc, không lấy từ YAML: một nguồn duy nhất thì không lệch được.
            wav = await _synth(client, text, "en_US_female", toc_do_theo_bac(cefr))
            if wav is None:
                failed += 1
                continue
            await _write(db, dest, wav, "en_US_female")
            made += 1

        # 4. Hội thoại + từ vựng của từng bài (nội dung "học" trước câu hỏi)
        lessons = (await db.execute(select(Lesson))).scalars().all()
        for lesson in lessons:
            speed = toc_do_theo_bac(lesson.cefr_target)
            # hội thoại: mỗi lượt một file
            turns = (lesson.dialogue or {}).get("turns", [])
            for i, turn in enumerate(turns):
                text = (turn.get("en") or "").strip()
                if not text:
                    continue
                dest = media / "dialogue" / f"{lesson.code}_{i}.wav"
                if dest.exists() and not force:
                    skipped += 1
                    continue
                wav = await _synth(client, text, "en_US_female", speed)
                if wav is None:
                    failed += 1
                    continue
                await _write(db, dest, wav, "en_US_female")
                made += 1
            # từ vựng: đọc câu ví dụ (chunk)
            for i, v in enumerate(lesson.vocabulary or []):
                text = (v.get("chunk") or v.get("term") or "").strip()
                if not text:
                    continue
                dest = media / "vocab" / f"{lesson.code}_{i}.wav"
                if dest.exists() and not force:
                    skipped += 1
                    continue
                wav = await _synth(client, text, "en_US_female", speed)
                if wav is None:
                    failed += 1
                    continue
                await _write(db, dest, wav, "en_US_female")
                made += 1

        # 5. Roleplay: câu của "partner" mỗi node
        rp_dir = Path("seeds/roleplay")
        for path in sorted(rp_dir.glob("RP-*.yaml")):
            rp = yaml.safe_load(path.read_text(encoding="utf-8"))
            for nid, node in rp.get("nodes", {}).items():
                text = (node.get("partner_en") or "").strip()
                if not text:
                    continue
                dest = media / "roleplay" / f"{rp['id']}_{nid}.wav"
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
