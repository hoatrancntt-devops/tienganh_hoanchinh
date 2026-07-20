from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_session
from app.models.content import Activity, Item, Lesson
from app.models.enums import LessonState, NotifType
from app.models.progress import ItemAttempt
from app.models.user import User
from app.schemas.learning import AttemptResultOut, LessonCardOut, NextUpOut, SubmitAttemptIn
from app.services import learning_path_service as path
from app.services import notification_service as notif
from app.services import prerequisite_service as prereq
from app.services.ai import fallback

router = APIRouter(prefix="/api/v1/learn", tags=["learning"])


@router.get("/path", response_model=list[LessonCardOut])
async def learning_path(
    phase: str | None = None,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    return await path.lesson_cards(db, user.id, phase)


@router.get("/next", response_model=NextUpOut)
async def next_up(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    return await path.next_up(db, user.id)


@router.get("/lessons/{code}")
async def lesson_detail(
    code: str, user: User = Depends(current_user), db: AsyncSession = Depends(get_session)
):
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bài học.")

    state = await prereq.evaluate_lesson_state(db, user.id, lesson)
    if state["state"] == LessonState.LOCKED:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail={"reason_vi": state["warning_vi"], "blocking": state["blocking"],
                    "challenge_available": True},
        )

    is_preview = state["state"] == LessonState.PREVIEWABLE
    await db.refresh(lesson, ["activities"])
    activities = []
    for act in lesson.activities:
        await db.refresh(act, ["items"])
        items = [
            {"id": i.id, "kind": i.kind, "prompt_en": i.prompt_en, "prompt_vi": i.prompt_vi,
             "ipa": i.ipa, "choices": i.choices, "focus_phonemes": i.focus_phonemes,
             "audio_asset_id": i.audio_asset_id}
            for i in act.items
        ]
        activities.append({"id": act.id, "kind": act.kind, "title_vi": act.title_vi,
                           "items": items})
        # Preview: chỉ mục tiêu, từ vựng, hội thoại + hoạt động nói ĐẦU TIÊN.
        if is_preview and len(activities) >= 1:
            break

    return {
        "code": lesson.code, "title_vi": lesson.title_vi, "phase": lesson.phase,
        "est_minutes": lesson.est_minutes, "objective_vi": lesson.objective_vi,
        "vietnamese_explanation": lesson.vietnamese_explanation,
        "common_mistakes": lesson.common_mistakes,
        "memory_trick_vi": lesson.memory_trick_vi,
        "vocabulary": lesson.vocabulary,
        "dialogue": {} if is_preview else lesson.dialogue,
        "sentence_patterns": lesson.sentence_patterns,
        "threshold": lesson.mastery_threshold,
        "state": state["state"], "is_preview": is_preview,
        "preview_banner_vi": (
            "Đây là bản xem trước. Điểm không được tính. "
            f"Mở khoá bài này bằng cách hoàn thành [{state['blocking']}] hoặc thi vượt."
        ) if is_preview else "",
        "activities": activities,
    }


@router.post("/attempt", response_model=AttemptResultOut)
async def submit_attempt(
    payload: SubmitAttemptIn,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    item = await db.get(Item, payload.item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy câu hỏi.")
    activity = await db.get(Activity, item.activity_id)
    lesson = await db.get(Lesson, activity.lesson_id)

    # Chấm quiz/vocab bằng so đáp án — không LLM.
    if item.answer_index is not None:
        is_correct = payload.choice_index == item.answer_index
        score = 100.0 if is_correct else 0.0
        feedback = "Chính xác." if is_correct else _wrong_answer_hint(lesson, item)
    else:
        result = fallback.open_feedback(item, payload.text or "")
        is_correct = "đúng ý" in result
        score = 80.0 if is_correct else 40.0
        feedback = result

    db.add(
        ItemAttempt(
            user_id=user.id, item_id=item.id, lesson_id=lesson.id,
            activity_kind=activity.kind, is_correct=is_correct, score=score,
            response={"choice_index": payload.choice_index, "text": payload.text},
            latency_ms=payload.latency_ms, is_preview=payload.is_preview,
        )
    )
    await db.commit()

    if payload.is_preview:
        # Preview chấm thật nhưng không cộng mastery — người tưởng mình biết rồi
        # tự phát hiện ra mình chưa, bằng dữ liệu của chính họ.
        return AttemptResultOut(
            is_correct=is_correct, score=score, feedback_vi=feedback,
            mastery_raw=0.0, state=LessonState.PREVIEWABLE, unlocked_codes=[],
        )

    result = await path.update_mastery(db, user.id, lesson.id)
    await path.schedule_reviews(db, user.id, [item.id])
    await db.refresh(user, ["profile"])
    await notif.record_study(db, user)

    if result["unlocked_codes"]:
        await notif.notify(
            db, user, NotifType.LESSON_UNLOCKED,
            f"{len(result['unlocked_codes'])} bài mới đã mở",  # gộp nhóm, không 5 dòng
            ", ".join(result["unlocked_codes"]), link="/learn",
            dedup_key=f"unlock:{lesson.code}", expires_days=7,
        )
    if lesson.is_checkpoint and result["state"] == LessonState.MASTERED:
        await notif.notify(
            db, user, NotifType.CHECKPOINT_PASSED,
            f"Bạn đã vượt {lesson.title_vi}",
            "Phase tiếp theo đã mở.", link="/learn",
            dedup_key=f"cp:{lesson.code}", email=True,
        )

    return AttemptResultOut(
        is_correct=is_correct, score=score, feedback_vi=feedback,
        mastery_raw=result["mastery_raw"], state=result["state"],
        unlocked_codes=result["unlocked_codes"],
    )


def _wrong_answer_hint(lesson: Lesson, item: Item) -> str:
    """Feedback lấy từ seed, không tốn token AI."""
    for mistake in lesson.common_mistakes or []:
        detect = mistake.get("detect", {})
        missing = set(detect.get("phoneme_missing", []))
        if missing & set(item.focus_phonemes or []):
            return f"{mistake.get('why_vi', '')} Cách sửa: {mistake.get('fix_vi', '')}"
    exp = lesson.vietnamese_explanation or {}
    return exp.get("contrast_vi") or exp.get("how_vi") or "Chưa đúng. Nghe lại câu mẫu nhé."


@router.post("/challenge/{code}")
async def challenge(
    code: str, score: float,
    user: User = Depends(current_user), db: AsyncSession = Depends(get_session),
):
    """Lối thoát duy nhất cho người đã biết — nhưng vẫn kiểm chứng năng lực."""
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy bài học.")
    passed = await prereq.grant_challenge_pass(db, user.id, lesson, score)
    return {
        "passed": passed, "threshold": lesson.challenge_threshold, "score": score,
        "message_vi": (
            "Bạn đã chứng minh mình nắm được bài này. Đã mở khoá."
            if passed else
            f"Cần {lesson.challenge_threshold}% để thi vượt, bạn được {score:.0f}%. "
            "Học bài này sẽ nhanh thôi vì bạn đã gần đạt."
        ),
    }


@router.get("/health/retention")
async def retention(user: User = Depends(current_user), db: AsyncSession = Depends(get_session)):
    value = await prereq.retention_health(db, user.id)
    return {"retention_health": round(value, 3), "needs_forced_review": value < 0.70}
