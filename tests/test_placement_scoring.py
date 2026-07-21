"""Test luật xếp band. Mỗi test tương ứng một lỗi thật đã tìm thấy khi rà soát."""
import pytest

from app.models.assessment import CEFR_ORDER
from app.models.enums import Cefr
from app.services import placement_scoring as sc


def _perfect_paper() -> tuple[float, float]:
    """Điểm knowledge/listening khi trả lời đúng 100% form A."""
    vocab = [1, 2, 3, 4, 5]
    grammar = [1, 2, 3, 4]
    listening = [1, 2, 2, 3, 4, 5]
    k_scores = [sc.score_mcq(d, True, 0, False) for d in vocab + grammar]
    l_scores = [sc.score_mcq(d, True, 0, True) for d in listening]
    return (
        sc.section_average(k_scores, len(k_scores)),
        sc.section_average(l_scores, len(l_scores)),
    )


# --- Trần điểm: phải chạm được B1 ---

def test_tra_loi_dung_het_va_noi_tot_thi_dat_b1():
    knowledge, listening = _perfect_paper()
    verdict = sc.decide(knowledge, listening, 95.0, speech_available=True, silent_count=0)
    assert verdict.band == Cefr.B1, (
        f"trần điểm vẫn còn chặn: overall={verdict.overall} knowledge={knowledge} "
        f"listening={listening}"
    )


def test_cau_de_tra_loi_dung_khong_bi_ep_xuong_60():
    assert sc.score_mcq(1, True, 0, False) >= 80
    assert sc.score_mcq(5, True, 0, False) == 100.0


# --- Bất biến: không bao giờ tụt quá 1 bậc ---

@pytest.mark.parametrize("knowledge,listening,speaking,speech", [
    (90.0, 90.0, 29.0, True),     # giỏi giấy, yếu nói, lại sát biên
    (60.0, 75.0, 0.0, False),     # micro hỏng, lại sát biên
    (85.0, 85.0, 10.0, True),
    (100.0, 100.0, 0.0, False),
    (61.0, 61.0, 29.0, True),
])
def test_khong_bao_gio_tut_qua_mot_bac(knowledge, listening, speaking, speech):
    verdict = sc.decide(knowledge, listening, speaking, speech, silent_count=0)
    tut = CEFR_ORDER.index(verdict.band_raw) - CEFR_ORDER.index(verdict.band)
    assert tut <= 1, f"tụt {tut} bậc: {verdict.band_raw} -> {verdict.band}"


def test_quet_toan_dai_diem_khong_ca_nao_tut_hai_bac():
    """Quét dày thay vì chỉ vài ca mẫu — lỗi cũ chỉ lộ ở đúng vùng sát mốc cắt."""
    for k in range(0, 101, 5):
        for lis in range(0, 101, 5):
            for sp in range(0, 101, 10):
                for speech in (True, False):
                    v = sc.decide(float(k), float(lis), float(sp), speech, silent_count=0)
                    tut = CEFR_ORDER.index(v.band_raw) - CEFR_ORDER.index(v.band)
                    assert tut <= 1, f"k={k} l={lis} sp={sp} speech={speech}: tụt {tut} bậc"


def test_gioi_giay_yeu_noi_khong_bi_day_ve_pre_a1():
    """Ca cụ thể của lỗi cũ: nghe hiểu 90/100 mà bị xếp vào bài dạy âm /θ/."""
    verdict = sc.decide(90.0, 90.0, 29.0, speech_available=True, silent_count=0)
    assert verdict.band != Cefr.PRE_A1
    assert sc.ENTRY_LESSON[verdict.band] != "F01"


def test_micro_hong_van_xep_duoc_tu_hai_truc_con_lai():
    verdict = sc.decide(60.0, 75.0, 0.0, speech_available=False, silent_count=0)
    assert verdict.band != Cefr.PRE_A1
    assert verdict.confidence == "low"


# --- Mẫu số: bỏ câu khó không được làm điểm tăng ---

def test_bo_cau_kho_khong_lam_diem_tang():
    chi_mot_cau_kho = sc.section_average([sc.score_mcq(5, True, 0, False)], 9)
    lam_dung_ca_chin = sc.section_average(
        [sc.score_mcq(d, True, 0, False) for d in [1, 2, 3, 4, 5, 1, 2, 3, 4]], 9
    )
    assert chi_mot_cau_kho < lam_dung_ca_chin


# --- Sàn im lặng: phân biệt "không nói được" với "không thu được" ---

def test_im_lang_that_thi_pre_a1():
    verdict = sc.decide(80.0, 80.0, 0.0, speech_available=True, silent_count=4)
    assert verdict.band == Cefr.PRE_A1
    assert verdict.confidence == "low"


def test_khong_co_du_lieu_noi_khong_bi_tinh_la_im_lang():
    assert sc.score_speaking("read_aloud", None)["no_data"] is True
    assert sc.score_speaking("read_aloud", None)["silent"] is False
    co_tieng_khong_ra_chu = sc.score_speaking(
        "read_aloud", {"pronunciation": 10, "fluency": 0, "communication": 0, "transcript": "  "}
    )
    assert co_tieng_khong_ra_chu["silent"] is True
    assert co_tieng_khong_ra_chu["no_data"] is False


# --- Phạt nghe lại ---

def test_nghe_lai_lan_dau_khong_bi_phat():
    assert sc.score_mcq(3, True, 1, True) == sc.score_mcq(3, True, 0, True)


def test_phat_nghe_lai_co_tran_va_chi_ap_cho_phan_nghe():
    khong_nghe = sc.score_mcq(3, True, 5, False)
    co_nghe = sc.score_mcq(3, True, 5, True)
    assert khong_nghe == sc.score_mcq(3, True, 0, False)     # vocab/grammar không bị phạt
    assert co_nghe < khong_nghe                              # phần nghe thì có phạt
    assert co_nghe == pytest.approx(khong_nghe * (1 - sc.REPLAY_PENALTY_CAP))  # đúng bằng trần


# --- Confidence: luật rõ ràng, không còn công thức lệch thứ nguyên ---

def test_lech_ky_nang_lon_thi_confidence_thap():
    verdict = sc.decide(95.0, 95.0, 20.0, speech_available=True, silent_count=0)
    assert verdict.confidence == "low"


def test_deu_ba_truc_va_xa_moc_cat_thi_confidence_cao():
    verdict = sc.decide(70.0, 70.0, 70.0, speech_available=True, silent_count=0)
    assert verdict.confidence == "high"


def test_tra_loi_cham_bat_thuong_chi_ha_confidence_khong_tru_diem():
    deu = sc.decide(70.0, 70.0, 70.0, True, 0, slow_ratio=0.0)
    cham = sc.decide(70.0, 70.0, 70.0, True, 0, slow_ratio=0.9)
    assert cham.overall == deu.overall      # không trừ điểm
    assert cham.confidence == "low"


def test_slow_ratio_bo_qua_khi_qua_it_du_lieu():
    assert sc.slow_answer_ratio([100, 200]) == 0.0
    assert sc.slow_answer_ratio([100, 100, 100, 100, 9000]) == pytest.approx(0.2)


# --- Nhất quán cấu hình ---

def test_moi_band_deu_co_bai_vao_va_so_tuan():
    for _, band in sc.BANDS:
        assert band in sc.ENTRY_LESSON
        assert band in sc.WEEKS_TO_GOAL
    assert len(sc.BANDS) == len(CEFR_ORDER)


def test_trong_so_cong_dung_mot():
    assert sum(sc.WEIGHTS.values()) == pytest.approx(1.0)


@pytest.mark.parametrize("overall,mong_doi", [
    (25.0, Cefr.PRE_A1),
    (33.0, Cefr.A1),      # ngay trên mốc hiệu dụng 30
    (55.0, Cefr.A1),
    (63.0, Cefr.A2),      # ngay trên mốc hiệu dụng 60
    (78.0, Cefr.A2),
    (85.0, Cefr.B1),      # ngay trên mốc hiệu dụng 82
])
def test_moc_cat_hieu_dung_dung_nhu_thiet_ke(overall, mong_doi):
    """Mốc HIỆU DỤNG (sau khi luật sát biên đã chạy) phải là 30/60/82.

    BANDS ghi 27/57/79 vì đã trừ sẵn phần bù NEAR_EDGE. Test này khoá cặp đôi đó lại:
    đổi NEAR_EDGE mà quên đổi BANDS thì test đỏ ngay.
    """
    verdict = sc.decide(overall, overall, overall, speech_available=True, silent_count=0)
    assert verdict.band == mong_doi, f"overall={overall} -> {verdict.band}, chờ {mong_doi}"
