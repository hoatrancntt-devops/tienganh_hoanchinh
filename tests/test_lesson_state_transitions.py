"""Trạng thái bài phải phản ánh đúng việc học viên đã làm gì.

Lỗi đã gặp: học viên làm xong hoạt động đầu tiên của một bài chưa từng đụng tới, nhưng lộ
trình vẫn hiện bài đó là "khoá". Nguyên nhân: bản ghi LessonProgress vừa tạo chưa flush nên
`state` là None, phép kiểm `state in (AVAILABLE, PREVIEWABLE, LOCKED)` trượt.
"""
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.content import Activity, Item, Lesson
from app.models.enums import LessonState
from app.models.progress import ItemAttempt, LessonProgress
from app.models.user import User
from app.seeds.loader import load_content
from app.services import learning_path_service as path


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        await session.execute(text("PRAGMA foreign_keys=ON"))
        await load_content(session)
        yield session
    await engine.dispose()


async def _hoc_vien(db) -> User:
    user = User(email="hv@test.vn", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _lam_mot_hoat_dong(db, user: User, code: str, diem: float) -> Lesson:
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one()
    act = (
        await db.execute(select(Activity).where(Activity.lesson_id == lesson.id))
    ).scalars().first()
    item = (await db.execute(select(Item).where(Item.activity_id == act.id))).scalars().first()
    db.add(ItemAttempt(user_id=user.id, item_id=item.id, lesson_id=lesson.id,
                       activity_kind=act.kind, is_correct=diem >= 50, score=diem))
    await db.commit()
    return lesson


async def _trang_thai(db, user: User, lesson: Lesson) -> str:
    prog = (await db.execute(
        select(LessonProgress).where(LessonProgress.user_id == user.id,
                                     LessonProgress.lesson_id == lesson.id)
    )).scalar_one()
    return prog.state


async def test_lam_hoat_dong_dau_tien_thi_bai_chuyen_sang_dang_hoc(db):
    """Bài chưa từng đụng tới: làm một hoạt động xong phải là “đang học”, không phải “khoá”."""
    user = await _hoc_vien(db)
    lesson = await _lam_mot_hoat_dong(db, user, "S01", 40.0)

    ket_qua = await path.update_mastery(db, user.id, lesson.id)

    assert ket_qua["state"] == LessonState.IN_PROGRESS, (
        f"làm xong một hoạt động mà bài vẫn ở trạng thái '{ket_qua['state']}'"
    )
    assert await _trang_thai(db, user, lesson) == LessonState.IN_PROGRESS


async def test_dat_nguong_thi_chuyen_thang_sang_hoan_thanh(db):
    user = await _hoc_vien(db)
    lesson = await _lam_mot_hoat_dong(db, user, "S01", 100.0)
    await path.update_mastery(db, user.id, lesson.id)
    # S01 có nhiều trục nên một hoạt động điểm cao chưa chắc đủ; kiểm bằng chính ngưỡng.
    prog = (await db.execute(
        select(LessonProgress).where(LessonProgress.lesson_id == lesson.id)
    )).scalar_one()
    mong_doi = (LessonState.MASTERED if prog.mastery_raw >= lesson.mastery_threshold
                else LessonState.IN_PROGRESS)
    assert prog.state == mong_doi


async def test_bai_da_hoan_thanh_khong_bi_go_khi_diem_tut(db):
    """Nâng ngưỡng hoặc điểm trôi không được tước mất thành quả đã có."""
    user = await _hoc_vien(db)
    lesson = (await db.execute(select(Lesson).where(Lesson.code == "S01"))).scalar_one()
    db.add(LessonProgress(user_id=user.id, lesson_id=lesson.id, attempts_count=1,
                          state=LessonState.MASTERED, mastery_raw=95.0))
    await db.commit()

    await _lam_mot_hoat_dong(db, user, "S01", 10.0)
    await path.update_mastery(db, user.id, lesson.id)

    assert await _trang_thai(db, user, lesson) == LessonState.MASTERED


async def test_dem_dung_so_lan_thu(db):
    user = await _hoc_vien(db)
    lesson = await _lam_mot_hoat_dong(db, user, "S01", 60.0)
    await path.update_mastery(db, user.id, lesson.id)
    await path.update_mastery(db, user.id, lesson.id)
    prog = (await db.execute(
        select(LessonProgress).where(LessonProgress.lesson_id == lesson.id)
    )).scalar_one()
    assert prog.attempts_count == 2
