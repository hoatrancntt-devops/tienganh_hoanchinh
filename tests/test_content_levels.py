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


# --- Đường cong đòi hỏi phải TĂNG theo bậc ---

def test_nguong_mastery_tang_dan_theo_bac(lessons):
    """Bậc cao không được dễ hơn bậc thấp.

    Trước bản này đường cong đi NGƯỢC: F01–F04 (bậc pre_a1, tuần đầu của người mất gốc)
    có ngưỡng 78 — cao nhất giáo trình — còn CP-I và CP-R (checkpoint B1, bài chốt cuối)
    chỉ 70. Tức là đòi hỏi nhiều nhất ở người biết ít nhất.
    """
    tran = {}
    san = {}
    for x in lessons:
        n = x.unlock_condition.mastery_threshold
        r = RANK[x.cefr_target]
        tran[r] = max(tran.get(r, 0), n)
        san[r] = min(san.get(r, 100), n)
    for thap in sorted(san):
        for cao in sorted(san):
            if cao > thap:
                assert san[cao] >= tran[thap], (
                    f"bậc {cao} có bài dễ hơn bậc {thap}: "
                    f"thấp nhất {san[cao]} < cao nhất {tran[thap]}"
                )


def test_bac_thap_nhat_khong_kho_hon_bac_cao_nhat(lessons):
    """Kiểm thẳng cái ca cụ thể đã từng sai."""
    pre = max(x.unlock_condition.mastery_threshold for x in lessons if x.cefr_target == "pre_a1")
    b1 = min(x.unlock_condition.mastery_threshold for x in lessons if x.cefr_target == "b1")
    assert pre < b1, f"pre_a1 đòi tới {pre} nhưng b1 chỉ đòi {b1}"


TRUC_CHINH = 0.20   # trọng số từ đây trở lên thì kỹ năng đó là trục chính của bài


def test_nguong_tung_ky_nang_cung_tang_dan(lessons):
    """Ngưỡng nói riêng ở checkpoint A1 từng là 65 còn ở B1 là 60 — cũng ngược.

    Chỉ so các kỹ năng là TRỤC CHÍNH của bài. Trục phụ được phép có ngưỡng thấp hơn:
    CP-R là checkpoint đọc, nghe chỉ chiếm 10% điểm — đòi ngưỡng nghe cao ở đó là chặn
    người đọc giỏi bằng một thứ bài đó không dạy.
    """
    theo_bac = {}
    for x in lessons:
        w = x.unlock_condition.mastery_weights
        for ky_nang, n in x.unlock_condition.min_per_skill.items():
            if w.get(ky_nang, 0) >= TRUC_CHINH:
                theo_bac.setdefault(ky_nang, {})[RANK[x.cefr_target]] = n
    for ky_nang, muc in theo_bac.items():
        bac = sorted(muc)
        for a, b in zip(bac, bac[1:], strict=False):
            assert muc[b] >= muc[a], (
                f"ngưỡng '{ky_nang}': bậc {b} đòi {muc[b]} < bậc {a} đòi {muc[a]}"
            )


def test_van_giu_cong_bat_buoc_mo_mieng(lessons):
    """Hạ ngưỡng ĐIỂM nhưng giữ cổng SỐ LẦN: vẫn phải luyện, chỉ là không bị chặn đường."""
    for x in lessons:
        if x.speaking_drills:
            assert x.unlock_condition.min_speaking_attempts >= 4, (
                f"{x.id}: có drill nói nhưng không bắt buộc số lần thử"
            )
