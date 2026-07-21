"""Nạp nội dung thật vào SQLite in-memory và kiểm tra đường ống Đọc/Viết end-to-end.

Bất biến quan trọng nhất ở đây: bài đọc KHÔNG BAO GIỜ sinh audio. Đó là lỗi im lặng —
không có gì báo, chỉ là kỹ năng đọc lặng lẽ biến thành kỹ năng nghe.
"""
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.content import Activity, Item, Lesson
from app.models.enums import ActivityKind
from app.seeds.loader import load_content
from app.services import writing_service as ws


@pytest_asyncio.fixture(scope="module")
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        await load_content(session)
        yield session
    await engine.dispose()


async def _lesson(db, code: str) -> Lesson:
    return (await db.execute(select(Lesson).where(Lesson.code == code))).scalar_one()


async def _acts(db, lesson: Lesson) -> dict[str, Activity]:
    rows = (await db.execute(select(Activity).where(Activity.lesson_id == lesson.id))).scalars()
    return {a.kind: a for a in rows}


# --- Bài đọc ---

async def test_r01_co_hoat_dong_doc(db):
    lesson = await _lesson(db, "R01")
    assert lesson.reading_passage, "R01 phải có reading_passage"
    assert lesson.reading_passage["kind"] == "email"
    assert ActivityKind.READ in await _acts(db, lesson)


async def test_bai_doc_khong_con_nam_trong_dialogue(db):
    """Email từng bị nhét vào `dialogue` với speaker turns rồi sinh audio."""
    lesson = await _lesson(db, "R01")
    assert not (lesson.dialogue or {}).get("turns"), (
        "R01 vẫn còn dialogue — email sẽ lại được đọc thành tiếng"
    )


async def test_bai_doc_khong_bao_gio_sinh_audio(db):
    """generate_audio chỉ sinh tiếng cho Item có expected_text. Bài đọc phải để None."""
    rows = (await db.execute(
        select(Item, Activity).join(Activity, Item.activity_id == Activity.id)
        .where(Activity.kind == ActivityKind.READ)
    )).all()
    assert rows, "chưa có Item đọc nào để kiểm"
    for item, act in rows:
        assert item.expected_text is None, (
            f"Item đọc {item.id} có expected_text — sẽ bị sinh audio và biến thành bài nghe"
        )


async def test_cau_hoi_doc_bang_tieng_anh(db):
    """Hỏi bằng tiếng Việt là đo hiểu tiếng Việt, không phải đọc hiểu tiếng Anh."""
    rows = (await db.execute(
        select(Item).join(Activity, Item.activity_id == Activity.id)
        .where(Activity.kind == ActivityKind.READ)
    )).scalars().all()
    co_dau = set("àáảãạăâđêôơưèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵ")
    for item in rows:
        assert item.prompt_en, f"Item đọc {item.id} thiếu câu hỏi tiếng Anh"
        assert not (co_dau & set(item.prompt_en.lower())), (
            f"câu hỏi đọc '{item.prompt_en[:40]}' có dấu tiếng Việt"
        )


async def test_bai_doc_co_it_nhat_hai_loai_cau_hoi(db):
    rows = (await db.execute(
        select(Item).join(Activity, Item.activity_id == Activity.id)
        .where(Activity.kind == ActivityKind.READ)
    )).scalars().all()
    loai = {t for item in rows for t in item.tags if t in ("scan", "skim", "infer", "guess_word")}
    assert len(loai) >= 2, f"chỉ có một loại câu hỏi đọc: {loai}"


# --- Bài viết ---

async def test_r01_co_hoat_dong_viet(db):
    lesson = await _lesson(db, "R01")
    acts = await _acts(db, lesson)
    assert ActivityKind.WRITE in acts
    assert acts[ActivityKind.WRITE].config["kind"] == "guided_email"


async def test_config_gui_xuong_client_khong_chua_dap_an(db):
    """`config` là payload cho trình duyệt. Đáp án chỉ được nằm ở Item phía server."""
    rows = (await db.execute(
        select(Activity).where(Activity.kind == ActivityKind.WRITE)
    )).scalars().all()
    for act in rows:
        assert "required_chunks" not in act.config
        assert "blanks" not in act.config
        assert "accept" not in act.config
        assert "ordered_lines" not in act.config, "gửi đúng thứ tự xuống là gửi luôn đáp án"


async def test_bai_viet_cham_duoc_bang_du_lieu_da_seed(db):
    """Nối trọn vòng: dữ liệu từ YAML -> DB -> bộ chấm, không qua tay người."""
    lesson = await _lesson(db, "R01")
    acts = await _acts(db, lesson)
    item = (await db.execute(
        select(Item).where(Item.activity_id == acts[ActivityKind.WRITE].id)
    )).scalar_one()
    task = dict(item.scoring_weights)
    task["common_mistakes"] = lesson.common_mistakes

    tot = ws.grade(task, "Hi Linh, I'll send my notes but could I have until Thursday? "
                         "I still need to pull the logs. Let me know if that works. Thanks, Hoa.")
    assert tot["score"] >= 75, tot["feedback_vi"]

    kem = ws.grade(task, "ok")
    assert kem["score"] < 50


async def test_bai_viet_khong_sinh_audio(db):
    rows = (await db.execute(
        select(Item).join(Activity, Item.activity_id == Activity.id)
        .where(Activity.kind == ActivityKind.WRITE)
    )).scalars().all()
    assert rows
    for item in rows:
        assert item.expected_text is None


# --- Mastery ---

async def test_mastery_weights_cua_r01_co_ca_doc_va_viet(db):
    lesson = await _lesson(db, "R01")
    assert "read" in lesson.mastery_weights
    assert "write" in lesson.mastery_weights
    assert sum(lesson.mastery_weights.values()) == pytest.approx(1.0)
