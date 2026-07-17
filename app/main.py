import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.admin import admin_api, admin_router
from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal, engine, init_db
from app.services import auth_service
from app.services import settings_service as cfg
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.web.routes import router as web_router

log = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.DEBUG)
    for sub in ("", "tts", "placement", "attempts"):
        (Path(settings.MEDIA_DIR) / sub).mkdir(parents=True, exist_ok=True)
    if settings.is_sqlite:
        Path("./data").mkdir(exist_ok=True)

    await init_db()
    async with SessionLocal() as db:
        await cfg.load_all(db)
        # Không có mật khẩu mặc định: env trống thì không tạo admin.
        await auth_service.ensure_admin(db, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
    start_scheduler()
    log.info("%s v%s started on port %s", settings.APP_NAME, __version__, settings.APP_PORT)
    yield
    stop_scheduler()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    docs_url="/docs" if settings.APP_ENV != "prod" else None,
    lifespan=lifespan,
)

app.include_router(api_router)
app.include_router(admin_api)
app.include_router(admin_router)
app.include_router(web_router)

_static = Path("app/web/static")
if _static.exists():
    app.mount("/static", StaticFiles(directory=str(_static)), name="static")
_media = Path(settings.MEDIA_DIR)
_media.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media)), name="media")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    """Không bao giờ hiện stack trace hay lỗi tiếng Anh cho học viên."""
    log.exception("unhandled error on %s", request.url.path)
    if request.url.path.startswith(("/api/", "/admin/settings")):
        return JSONResponse(
            status_code=500,
            content={"detail": "Hệ thống gặp sự cố. Bạn thử lại sau ít phút nhé."},
        )
    return RedirectResponse("/learn", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=settings.DEBUG)
