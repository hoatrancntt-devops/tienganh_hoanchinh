"""Bất biến của giáo trình. Chạy trên nội dung thật trong seeds/content, không dùng dữ liệu giả."""
import pytest

from app.seeds.validate_content import (
    check_graph,
    check_level_order,
    check_pedagogy,
    check_unlock_reachable,
    load_all,
)
from app.services import placement_scoring as sc

RANK = {"pre_a1": 1, "a1": 2, "a2": 3, "b1": 4}


@pytest.fixture(scope="module")
def lessons():
    items, errors = load_all()
    assert not errors, f"YAML không hợp lệ: {errors[:5]}"
    return items


def test_giao_trinh_khong_co_loi_chan_publish(lessons):
    errors = (
        check_graph(lessons)
        + check_pedagogy(lessons)
        + check_unlock_reachable(lessons)
        + check_level_order(lessons)
    )
    assert not errors, "\n".join(errors[:10])


def test_bai_de_khong_bi_khoa_sau_bai_kho(lessons):
    """Bất biến trục dọc: tiên quyết luôn ở bậc thấp hơn hoặc bằng."""
    assert check_level_order(lessons) == []


def test_moi_band_xep_lop_deu_co_bai_vao_ton_tai(lessons):
    codes = {lesson.id for lesson in lessons}
    for band, code in sc.ENTRY_LESSON.items():
        assert code in codes, f"band {band} vào bài '{code}' nhưng bài đó không tồn tại"


def test_bai_vao_cua_moi_band_dung_bac_cua_band_do(lessons):
    """Xếp vào A2 thì phải vào bài A2, không phải bài A1 hay B1."""
    by_id = {lesson.id: lesson for lesson in lessons}
    for band, code in sc.ENTRY_LESSON.items():
        assert by_id[code].cefr_target == band.value, (
            f"band {band.value} vào bài {code} có cefr_target={by_id[code].cefr_target}"
        )


def test_bai_vao_la_bai_som_nhat_cua_bac(lessons):
    """Không được vào giữa bậc — nếu không, học viên nhảy qua phần đầu của chính bậc mình."""
    for band, code in sc.ENTRY_LESSON.items():
        cung_bac = [x for x in lessons if x.cefr_target == band.value]
        # Bài vào phải không có tiên quyết cứng nào cùng bậc, tức là cửa vào của bậc đó.
        entry = next(x for x in cung_bac if x.id == code)
        cung_bac_ids = {x.id for x in cung_bac}
        chan = [p.lesson for p in entry.prerequisites
                if p.kind == "hard" and p.lesson in cung_bac_ids]
        assert not chan, f"bài vào {code} còn bị chặn bởi bài cùng bậc: {chan}"


def test_moi_bac_deu_co_bai(lessons):
    co = {lesson.cefr_target for lesson in lessons}
    assert co == set(RANK), f"thiếu bậc: {set(RANK) - co}"
