"""Seed: nội dung YAML -> DB, sinh audio, tạo admin và tài khoản demo.

Chạy: make seed  (hoặc: python -m scripts.seed_data)
Idempotent — chạy lại chỉ cập nhật.
"""
import asyncio
import logging
import sys

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal, init_db
from app.seeds.generate_audio import generate_all
from app.seeds.loader import load_content
from app.services import auth_service

log = logging.getLogger("seed")
settings = get_settings()

DEMO_EMAIL = "demo@englishatwork.vn"
DEMO_PASSWORD = "demo12345"


async def seed(skip_audio: bool = False) -> int:
    setup_logging(settings.DEBUG)
    await init_db()

    async with SessionLocal() as db:
        try:
            stats = await load_content(db)
        except ValueError as exc:
            print(f"\n[X] {exc}\n")
            return 1
        log.info("noi dung: %s bai, %s canh tien quyet", stats["lessons"], stats["edges"])

        admin = await auth_service.ensure_admin(db, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
        if admin:
            log.info("admin san sang: %s", admin.email)
        else:
            log.warning("Chua dat ADMIN_EMAIL/ADMIN_PASSWORD — khong tao admin.")

        if await auth_service.get_by_email(db, DEMO_EMAIL) is None:
            await auth_service.register(
                db, DEMO_EMAIL, DEMO_PASSWORD, full_name="Học Viên Demo"
            )
            log.info("tai khoan demo: %s / %s", DEMO_EMAIL, DEMO_PASSWORD)

        if not skip_audio:
            audio = await generate_all(db)
            if audio.get("reason"):
                log.warning(
                    "Audio chua sinh (%s). App van chay nhung khong co tieng — "
                    "khoi dong container speech roi chay lai: make seed", audio["reason"]
                )
            else:
                log.info("audio: %s file moi, %s bo qua", audio["made"], audio["skipped"])

    print("\n[OK] Seed xong. Vao http://localhost:9999\n")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(seed(skip_audio="--no-audio" in sys.argv)))
