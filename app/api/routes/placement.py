from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.api.routes.speech import take_placement_speech
from app.db.session import get_session
from app.models.assessment import PlacementTest
from app.models.enums import NotifType
from app.models.user import User
from app.schemas.placement import PlacementResultOut, PlacementSubmitIn
from app.services import notification_service as notif
from app.services import placement_service

router = APIRouter(prefix="/api/v1/placement", tags=["placement"])


@router.get("/form/{form}")
async def get_form(form: str = "A"):
    """Trả form đã lột đáp án — đáp án không bao giờ rời server."""
    try:
        data = placement_service.load_form(form)
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    items = [
        {k: v for k, v in item.items()
         if k not in ("answer", "expected_text", "accept_patterns", "transcript_en")}
        for item in data["items"]
    ]
    return {"form": data["form"], "est_minutes": data.get("est_minutes", 14), "items": items}


@router.post("/start")
async def start(
    form: str = "A", user: User = Depends(current_user), db: AsyncSession = Depends(get_session)
):
    ok, reason = await placement_service.can_retake(db, user.id)
    if not ok:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, reason)
    test = await placement_service.start_test(db, user, form)
    return {"test_id": test.id, "form": test.form}


@router.post("/submit", response_model=PlacementResultOut)
async def submit(
    payload: PlacementSubmitIn,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    test = await db.get(PlacementTest, payload.test_id)
    if test is None or test.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bài test.")
    if test.finished_at:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bài test này đã nộp rồi.")

    # Điểm nói lấy từ buffer phía server, không lấy từ payload của client.
    speech_results = take_placement_speech(payload.test_id)
    result = await placement_service.submit(
        db, test, [r.model_dump() for r in payload.responses], speech_results=speech_results
    )
    await db.refresh(user, ["profile"])
    await notif.notify(
        db, user, NotifType.PLACEMENT_READY,
        "Kết quả xếp lớp đã sẵn sàng",
        result["explanation_vi"][:200],
        link="/learn", dedup_key=f"placement:{test.id}",
        email=True, email_subject="Kết quả xếp lớp của bạn",
        email_html=f"<p>{result['explanation_vi']}</p><p><a href='/learn'>Bắt đầu học</a></p>",
    )
    return result


@router.get("/last", response_model=PlacementResultOut | None)
async def last_result(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    stmt = (
        select(PlacementTest)
        .where(PlacementTest.user_id == user.id, PlacementTest.finished_at.isnot(None))
        .order_by(PlacementTest.finished_at.desc())
    )
    test = (await db.execute(stmt)).scalars().first()
    if test is None:
        return None
    return {
        "test_id": test.id, "result_cefr": test.result_cefr, "confidence": test.confidence,
        "scores": test.result_scores, "speaking_detail": {},
        "entry_lesson_code": placement_service.ENTRY_LESSON.get(test.result_cefr),
        "strengths_vi": [], "gaps_vi": [], "explanation_vi": test.explanation_vi,
        "estimated_weeks_to_goal": 0, "can_challenge": test.can_challenge,
    }
