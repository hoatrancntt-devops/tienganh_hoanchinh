"""Seed lại KHÔNG được xoá tiến độ học viên.

Trước bản này, `make seed` xoá sạch: loader `delete(Activity)` mỗi lần chạy, Item cascade
từ Activity, ItemAttempt cascade từ Item. Không có gì báo. Nó khiến mọi thay đổi nội dung
đều phải đánh đổi bằng toàn bộ lịch sử làm bài của học viên.
"""
import pytest
import pytest_asyncio
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.content import Activity, Item, Lesson
from app.models.enums import ActivityKind
from app.models.progress import ItemAttempt
from app.models.user import User
from app.seeds.loader import load_content


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        # SQLite mặc định TẮT khoá ngoại; Postgres thì luôn bật. Không bật ở đây thì test
        # xanh giả — đúng cái bẫy làm lỗi này sống sót tới tận production.
        await session.execute(text("PRAGMA foreign_keys=ON"))
        await load_content(session)
        yield session
    await engine.dispose()


async def _lam_bai(db, code: str = "F01") -> tuple[User, Item]:
    user = User(email="hv@test.vn", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    lesson = (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one()
    act = (
        await db.execute(select(Activity).where(Activity.lesson_id == lesson.id))
    ).scalars().first()
    item = (await db.execute(select(Item).where(Item.activity_id == act.id))).scalars().first()
    db.add(ItemAttempt(user_id=user.id, item_id=item.id, lesson_id=lesson.id,
                       activity_kind=act.kind, is_correct=True, score=92.0))
    await db.commit()
    return user, item


async def _dem(db, model) -> int:
    return (await db.execute(select(func.count()).select_from(model))).scalar()


async def test_seed_lai_khong_xoa_luot_lam_bai(db):
    await _lam_bai(db)
    truoc = await _dem(db, ItemAttempt)
    assert truoc == 1

    await load_content(db)          # đúng ý là chạy lại `make seed`

    assert await _dem(db, ItemAttempt) == truoc, "seed lại vẫn xoá tiến độ học viên"


async def test_seed_lai_giu_nguyen_id_cua_item(db):
    """Giữ nguyên ID mới là thứ thực sự bảo vệ tiến độ — không chỉ giữ số lượng."""
    _, item = await _lam_bai(db)
    id_cu = item.id
    await load_content(db)
    att = (await db.execute(select(ItemAttempt))).scalar_one()
    assert att.item_id == id_cu


async def test_seed_ba_lan_van_khong_nhan_ban_activity(db):
    lesson = (await db.execute(select(Lesson).where(Lesson.code == "F01"))).scalar_one()

    async def dem_act():
        return len((await db.execute(
            select(Activity).where(Activity.lesson_id == lesson.id)
        )).scalars().all())

    lan_dau = await dem_act()
    await load_content(db)
    await load_content(db)
    assert await dem_act() == lan_dau


async def test_seed_lai_van_cap_nhat_noi_dung(db):
    """Giữ tiến độ mà không cập nhật nội dung thì vô dụng — phải được cả hai."""
    lesson = (await db.execute(select(Lesson).where(Lesson.code == "F01"))).scalar_one()
    act = (await db.execute(
        select(Activity).where(Activity.lesson_id == lesson.id,
                               Activity.kind == ActivityKind.QUIZ)
    )).scalar_one()
    item = (await db.execute(
        select(Item).where(Item.activity_id == act.id, Item.order_index == 0)
    )).scalar_one()
    that = item.prompt_vi

    item.prompt_vi = "NOI DUNG BI SUA TAY"
    await db.commit()

    await load_content(db)
    await db.refresh(item)
    assert item.prompt_vi == that, "seed lại phải ghi đè nội dung về đúng YAML"


async def test_bo_bot_cau_thi_cau_do_bi_xoa(db):
    """Câu bị bỏ khỏi giáo trình phải biến mất, không nằm lại làm rác."""
    lesson = (await db.execute(select(Lesson).where(Lesson.code == "F01"))).scalar_one()
    act = (await db.execute(
        select(Activity).where(Activity.lesson_id == lesson.id,
                               Activity.kind == ActivityKind.QUIZ)
    )).scalar_one()
    so_cau = len((await db.execute(select(Item).where(Item.activity_id == act.id)))
                 .scalars().all())

    # Thêm một câu thừa ở cuối rồi seed lại — nó không có trong YAML nên phải bị dọn.
    db.add(Item(activity_id=act.id, order_index=so_cau + 5, kind="mcq", prompt_vi="thua"))
    await db.commit()

    await load_content(db)
    con_lai = len((await db.execute(select(Item).where(Item.activity_id == act.id)))
                  .scalars().all())
    assert con_lai == so_cau


@pytest.mark.parametrize("kind", [ActivityKind.LISTEN, ActivityKind.SPEAK, ActivityKind.QUIZ])
async def test_moi_loai_hoat_dong_deu_giu_duoc_tien_do(db, kind):
    lesson = (await db.execute(select(Lesson).where(Lesson.code == "F01"))).scalar_one()
    act = (await db.execute(
        select(Activity).where(Activity.lesson_id == lesson.id, Activity.kind == kind)
    )).scalar_one_or_none()
    if act is None:
        pytest.skip(f"F01 không có hoạt động {kind}")
    item = (await db.execute(select(Item).where(Item.activity_id == act.id))).scalars().first()
    user = User(email=f"hv-{kind}@test.vn", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    db.add(ItemAttempt(user_id=user.id, item_id=item.id, lesson_id=lesson.id,
                       activity_kind=kind, is_correct=True, score=80.0))
    await db.commit()

    await load_content(db)

    assert await _dem(db, ItemAttempt) == 1
