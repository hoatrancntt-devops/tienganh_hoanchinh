"""Admin: dashboard + cấu hình mail M365/SMTP + API key AI, sửa trực tiếp trên web."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import service as admin_service
from app.api.deps import admin_user, client_ip, current_user_optional
from app.db.session import get_session
from app.models.content import Lesson, Prerequisite
from app.models.enums import ContentStatus, OutboxStatus
from app.models.ops import EmailOutbox
from app.models.user import User
from app.schemas.admin import AISettingsIn, AISettingsOut, MailSettingsIn, MailSettingsOut, TestMailIn
from app.services import mail_service
from app.services.ai import router as ai_router

router = APIRouter(prefix="/admin", tags=["admin"])
api = APIRouter(prefix="/api/v1/admin", tags=["admin-api"])
templates = Jinja2Templates(directory="app/admin/templates")


# ---------- JSON API ----------

@api.get("/settings/mail", response_model=MailSettingsOut)
async def get_mail(_: User = Depends(admin_user), db: AsyncSession = Depends(get_session)):
    return await admin_service.read_mail_settings(db)


@api.put("/settings/mail", response_model=MailSettingsOut)
async def put_mail(
    payload: MailSettingsIn, request: Request,
    user: User = Depends(admin_user), db: AsyncSession = Depends(get_session),
):
    await admin_service.write_mail_settings(db, payload, user.id)
    await admin_service.audit(db, user.id, "mail_saved", {}, client_ip(request))
    return await admin_service.read_mail_settings(db)


@api.post("/settings/mail/test")
async def test_mail(
    payload: TestMailIn, _: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    """Gửi thẳng, không qua outbox: admin cần biết ngay cấu hình đúng hay sai."""
    try:
        await mail_service.send_test(db, payload.to_email)
    except mail_service.MailError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return {"ok": True, "message_vi": f"Đã gửi thư thử tới {payload.to_email}."}


@api.get("/settings/ai", response_model=AISettingsOut)
async def get_ai(_: User = Depends(admin_user), db: AsyncSession = Depends(get_session)):
    return await admin_service.read_ai_settings(db)


@api.put("/settings/ai", response_model=AISettingsOut)
async def put_ai(
    payload: AISettingsIn, user: User = Depends(admin_user),
    db: AsyncSession = Depends(get_session),
):
    await admin_service.write_ai_settings(db, payload, user.id)
    return await admin_service.read_ai_settings(db)


@api.get("/ai/health")
async def ai_health(_: User = Depends(admin_user), db: AsyncSession = Depends(get_session)):
    return {"providers": await ai_router.health_report(db),
            "budget": await ai_router.budget_state(db)}


@api.get("/ai/cost")
async def ai_cost(
    days: int = 30, _: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    return await admin_service.ai_cost_report(db, days)


# ---------- HTML ----------

@router.get("/login", response_class=HTMLResponse)
async def admin_login(request: Request, user: User | None = Depends(current_user_optional)):
    if user and user.is_admin:
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(request, "login.html", {})


async def _dashboard_ctx(db: AsyncSession) -> dict:
    users = (await db.execute(select(func.count(User.id)))).scalar_one()
    lessons = (
        await db.execute(
            select(func.count(Lesson.id)).where(Lesson.status == ContentStatus.PUBLISHED)
        )
    ).scalar_one()
    pending = (
        await db.execute(
            select(func.count(EmailOutbox.id)).where(EmailOutbox.status == OutboxStatus.PENDING)
        )
    ).scalar_one()
    return {
        "users": users, "lessons": lessons, "pending_emails": pending,
        "mail_configured": await mail_service.is_configured(db),
        "ai_enabled": await ai_router.ai_enabled(db),
        "cost": await admin_service.ai_cost_report(db, 30),
    }


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request, user: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    ctx = await _dashboard_ctx(db)
    return templates.TemplateResponse(
        request, "dashboard.html", {"user": user, "page": "dashboard", **ctx}
    )


@router.get("/settings/mail", response_class=HTMLResponse)
async def mail_page(
    request: Request, user: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    return templates.TemplateResponse(
        request, "settings_mail.html",
        {"user": user, "page": "mail", "s": await admin_service.read_mail_settings(db)},
    )


@router.get("/settings/ai", response_class=HTMLResponse)
async def ai_page(
    request: Request, user: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    return templates.TemplateResponse(
        request, "settings_ai.html",
        {"user": user, "page": "ai", "s": await admin_service.read_ai_settings(db)},
    )


@router.get("/content", response_class=HTMLResponse)
async def content_page(
    request: Request, user: User = Depends(admin_user), db: AsyncSession = Depends(get_session)
):
    lessons = (
        await db.execute(select(Lesson).order_by(Lesson.phase, Lesson.order_index))
    ).scalars().all()
    edges = (await db.execute(select(Prerequisite))).scalars().all()
    by_id = {lesson.id: lesson for lesson in lessons}
    rows = []
    for lesson in lessons:
        prereqs = [
            f"{by_id[e.requires_lesson_id].code} ≥{e.min_mastery}%"
            f"{'' if e.kind == 'hard' else ' (mềm)'}"
            for e in edges
            if e.lesson_id == lesson.id and e.requires_lesson_id in by_id
        ]
        rows.append({"l": lesson, "prereqs": prereqs})
    return templates.TemplateResponse(
        request, "content.html", {"user": user, "page": "content", "rows": rows}
    )
