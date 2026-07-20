"""Web SSR: Jinja2 + HTMX. Route mỏng, mọi luật nằm ở services."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user_optional
from app.db.session import get_session
from app.models.assessment import PlacementTest
from app.models.content import Lesson
from app.models.enums import LessonState, Phase
from app.models.user import User
from app.services import learning_path_service as path
from app.services import notification_service as notif
from app.services import placement_service, prerequisite_service
from app.services.ai import router as ai_router

from app import __version__

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")
# Cache-busting cho file tĩnh: đổi version -> URL đổi -> Cloudflare/edge lấy bản mới.
templates.env.globals["sv"] = __version__

# (tên, phụ đề, "xong phase này bạn LÀM ĐƯỢC gì", nhãn ngắn cho bản đồ lộ trình)
PHASE_META = {
    Phase.ORIENTATION: ("Khởi động", "Làm quen hệ thống",
                        "Biết cách học và dùng hệ thống.", "Khởi động"),
    Phase.FOUNDATION: ("Nền tảng", "Âm và câu lõi",
                       "Phát âm rõ, nghe ra âm, nói câu lõi ở tốc độ thật.", "Nền tảng"),
    Phase.DAILY: ("Giao tiếp hằng ngày", "Xã giao, ăn uống, đi lại",
                  "Chào hỏi, small talk, gọi món, hỏi đường — và đáp lại tự nhiên.", "Hằng ngày"),
    Phase.OFFICE: ("Công sở", "Họp, xin nghỉ, báo tiến độ",
                   "Nhận việc, hỏi làm rõ, báo tiến độ, đặt lịch, xin giúp đỡ.", "Công sở"),
    Phase.IT_ENGLISH: ("Tiếng Anh CNTT", "Báo sự cố, helpdesk, standup, họp",
                       "Báo sự cố, hỗ trợ người dùng, standup, giải thích, chốt việc với đối tác.", "CNTT"),
    Phase.READING: ("Đọc phục vụ công việc", "Lỗi, release notes, ticket, log, API",
                    "Đọc nhanh và đúng tài liệu IT, rút ra việc phải làm.", "Đọc"),
}

# Kỹ năng: icon + nhãn tiếng Việt. "write" chưa có bài chấm — đánh dấu sắp có.
SKILL_META = {
    "listen": {"icon": "🎧", "label": "Nghe"},
    "speak": {"icon": "🎙", "label": "Nói"},
    "read": {"icon": "📖", "label": "Đọc"},
    "write": {"icon": "✍️", "label": "Viết"},
}


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


async def _shell(request: Request, db: AsyncSession, user: User | None) -> dict:
    """Context dùng cho mọi trang có nav."""
    ctx: dict = {"user": user, "unread": 0, "streak": 0, "ai_enabled": False, "profile": None}
    if user:
        await db.refresh(user, ["profile"])
        ctx["unread"] = await notif.unread_count(db, user.id)
        ctx["streak"] = user.profile.streak_days if user.profile else 0
        ctx["profile"] = user.profile
        ctx["ai_enabled"] = await ai_router.ai_enabled(db)
    return ctx


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return templates.TemplateResponse(request, "landing.html", {"user": None})
    await db.refresh(user, ["profile"])
    if user.profile and user.profile.onboarded_at is None:
        return _redirect("/onboarding")
    return _redirect("/learn")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: User | None = Depends(current_user_optional)):
    if user:
        return _redirect("/learn")
    return templates.TemplateResponse(request, "auth/login.html", {"user": None})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: User | None = Depends(current_user_optional)):
    if user:
        return _redirect("/learn")
    return templates.TemplateResponse(request, "auth/register.html", {"user": None})


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    ctx = await _shell(request, db, user)
    return templates.TemplateResponse(request, "onboarding.html", ctx)


@router.get("/placement", response_class=HTMLResponse)
async def placement_page(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    ctx = await _shell(request, db, user)
    can, reason = await placement_service.can_retake(db, user.id)
    ctx.update({"can_take": can, "block_reason": reason})
    return templates.TemplateResponse(request, "placement.html", ctx)


@router.get("/placement/result", response_class=HTMLResponse)
async def placement_result(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    stmt = (
        select(PlacementTest)
        .where(PlacementTest.user_id == user.id, PlacementTest.finished_at.isnot(None))
        .order_by(PlacementTest.finished_at.desc())
    )
    test = (await db.execute(stmt)).scalars().first()
    if test is None:
        return _redirect("/placement")
    ctx = await _shell(request, db, user)
    ctx["test"] = test
    ctx["band_vi"] = {"pre_a1": "Chưa có nền (Pre-A1)", "a1": "Sơ cấp (A1)",
                      "a2": "Sơ trung cấp (A2)"}.get(test.result_cefr, test.result_cefr)
    return templates.TemplateResponse(request, "placement_result.html", ctx)


@router.get("/learn", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    await db.refresh(user, ["profile"])
    if user.profile and user.profile.onboarded_at is None:
        return _redirect("/onboarding")

    ctx = await _shell(request, db, user)
    cards = await path.lesson_cards(db, user.id)
    next_up = await path.next_up(db, user.id)
    health = await prerequisite_service.retention_health(db, user.id)

    phases = []
    for phase, (title, sub, outcome, short) in PHASE_META.items():
        group = [c for c in cards if c["phase"] == phase]
        if not group:
            continue
        mastered = sum(1 for c in group if c["state"] == LessonState.MASTERED)
        started = any(c["state"] != LessonState.LOCKED for c in group)
        phases.append({
            "key": phase, "title": title, "sub": sub, "outcome": outcome,
            "short": short, "cards": group,
            "mastered": mastered, "total": len(group),
            "pct": round(mastered / len(group) * 100) if group else 0,
            "locked": all(c["state"] == LessonState.LOCKED for c in group),
            "started": started,
            "skills": path.skills_for_phase(phase),
        })

    # Bản đồ lộ trình: phase "hiện tại" = phase chứa bài next_up (hoặc phase dở đầu tiên).
    current_phase = next((c["phase"] for c in cards if c["code"] == next_up.get("code")), None)
    if current_phase is None:
        current_phase = next((p["key"] for p in phases if p["pct"] < 100), None)
    for p in phases:
        p["is_current"] = p["key"] == current_phase

    # next_up: gắn kỹ năng để hero hiện nhãn Nghe/Nói/Đọc.
    if next_up.get("code"):
        nu_card = next((c for c in cards if c["code"] == next_up["code"]), None)
        if nu_card:
            next_up["skills"] = nu_card["skills"]
            next_up["is_checkpoint"] = nu_card["is_checkpoint"]

    total = len(cards)
    done = sum(1 for c in cards if c["state"] == LessonState.MASTERED)
    ctx.update({
        "phases": phases, "next_up": next_up,
        "retention": round(health * 100),
        "overall_pct": round(done / total * 100) if total else 0,
        "done": done, "total": total,
        "skill_meta": SKILL_META,
        "is_new_user": done == 0,
    })
    return templates.TemplateResponse(request, "dashboard.html", ctx)


@router.get("/learn/lesson/{code}", response_class=HTMLResponse)
async def lesson_player(
    code: str,
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one_or_none()
    if lesson is None:
        return _redirect("/learn")

    state = await prerequisite_service.evaluate_lesson_state(db, user.id, lesson)
    ctx = await _shell(request, db, user)

    if state["state"] == LessonState.LOCKED:
        blocker = None
        if state["blocking"]:
            blocker = (
                await db.execute(select(Lesson).where(Lesson.code == state["blocking"]))
            ).scalar_one_or_none()
        ctx.update({"lesson": lesson, "reason_vi": state["warning_vi"], "blocker": blocker})
        return templates.TemplateResponse(request, "lesson_locked.html", ctx)

    is_preview = state["state"] == LessonState.PREVIEWABLE
    await db.refresh(lesson, ["activities"])
    activities = []
    for act in lesson.activities:
        await db.refresh(act, ["items"])
        activities.append({
            "id": str(act.id), "kind": act.kind, "title_vi": act.title_vi,
            "items": [
                {"id": str(i.id), "kind": i.kind, "prompt_en": i.prompt_en,
                 "prompt_vi": i.prompt_vi, "ipa": i.ipa, "choices": i.choices,
                 "expected_text": i.expected_text if i.kind != "mcq" else None,
                 "focus_phonemes": i.focus_phonemes,
                 "audio": f"/media/tts/{i.id}.wav" if i.expected_text else None}
                for i in act.items
            ],
        })
        if is_preview:
            break  # preview: chỉ hoạt động đầu tiên

    ctx.update({
        "lesson": lesson, "activities": activities, "is_preview": is_preview,
        "blocking": state["blocking"], "state": state["state"],
        # Nội dung "học" hiển thị trước câu hỏi. Bản xem trước chỉ cho từ vựng, ẩn hội thoại.
        "study": {
            "topic": lesson.topic or "core",
            "vocabulary": lesson.vocabulary or [],
            "dialogue": {} if is_preview else (lesson.dialogue or {}),
            "sentence_patterns": lesson.sentence_patterns or [],
        },
    })
    return templates.TemplateResponse(request, "lesson.html", ctx)


@router.get("/learn/challenge/{code}", response_class=HTMLResponse)
async def challenge_page(
    code: str,
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one_or_none()
    if lesson is None:
        return _redirect("/learn")
    ctx = await _shell(request, db, user)
    ctx["lesson"] = lesson
    return templates.TemplateResponse(request, "challenge.html", ctx)


@router.get("/learn/review", response_class=HTMLResponse)
async def review_page(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    from datetime import datetime, timezone

    from app.models.content import Item
    from app.models.progress import ReviewQueue

    stmt = (
        select(ReviewQueue)
        .where(ReviewQueue.user_id == user.id,
               ReviewQueue.due_at <= datetime.now(timezone.utc))
        .order_by(ReviewQueue.due_at)
        .limit(10)
    )
    rows = (await db.execute(stmt)).scalars().all()
    items = []
    for row in rows:
        item = await db.get(Item, row.item_id)
        if item and item.answer_index is not None:
            items.append({"id": str(item.id), "prompt_vi": item.prompt_vi,
                          "choices": item.choices})
    ctx = await _shell(request, db, user)
    ctx["items"] = items
    return templates.TemplateResponse(request, "review.html", ctx)


@router.get("/learn/roleplay", response_class=HTMLResponse)
async def roleplay_list(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    from app.services import roleplay_service

    ctx = await _shell(request, db, user)
    ctx["scenarios"] = roleplay_service.list_scenarios()
    return templates.TemplateResponse(request, "roleplay_list.html", ctx)


@router.get("/learn/roleplay/{rid}", response_class=HTMLResponse)
async def roleplay_run(
    rid: str,
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    from app.services import roleplay_service

    scenario = roleplay_service.get_scenario(rid)
    if scenario is None:
        return _redirect("/learn/roleplay")
    ctx = await _shell(request, db, user)
    ctx["scenario"] = scenario
    return templates.TemplateResponse(request, "roleplay.html", ctx)


@router.get("/learn/write", response_class=HTMLResponse)
async def writing_list(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    from app.services import writing_service

    ctx = await _shell(request, db, user)
    ctx["sets"] = writing_service.list_sets()
    return templates.TemplateResponse(request, "writing_list.html", ctx)


@router.get("/learn/write/{sid}", response_class=HTMLResponse)
async def writing_set(
    sid: str,
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    from app.services import writing_service

    wset = writing_service.get_set(sid)
    if wset is None:
        return _redirect("/learn/write")
    ctx = await _shell(request, db, user)
    ctx["wset"] = wset
    return templates.TemplateResponse(request, "writing.html", ctx)


@router.post("/learn/write/grade", response_class=JSONResponse)
async def writing_grade(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return JSONResponse({"detail": "Chưa đăng nhập"}, status_code=401)
    from app.services import writing_service

    body = await request.json()
    wset = writing_service.get_set(body.get("set_id", ""))
    if wset is None:
        return JSONResponse({"detail": "Không tìm thấy bài"}, status_code=404)
    tasks = wset.get("tasks", [])
    idx = body.get("task_index", -1)
    if not isinstance(idx, int) or not 0 <= idx < len(tasks):
        return JSONResponse({"detail": "Câu không hợp lệ"}, status_code=400)
    return JSONResponse(writing_service.grade(tasks[idx], body.get("answer", "")))


@router.get("/notifications", response_class=HTMLResponse)
async def notifications_page(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    ctx = await _shell(request, db, user)
    ctx["items"] = await notif.list_recent(db, user.id, 50)
    return templates.TemplateResponse(request, "notifications.html", ctx)


@router.get("/partials/notifications", response_class=HTMLResponse)
async def notifications_partial(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return HTMLResponse("")
    rows = await notif.list_recent(db, user.id, 8)
    return templates.TemplateResponse(
        request, "partials/notif_dropdown.html", {"items": rows, "user": user}
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_session),
):
    if user is None:
        return _redirect("/login")
    ctx = await _shell(request, db, user)
    return templates.TemplateResponse(request, "settings.html", ctx)
