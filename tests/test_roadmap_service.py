"""Ước lượng lộ trình phải phản ánh học viên cụ thể, không phải một hằng số theo band."""
import pytest

from app.services import roadmap_service as rm


def _uoc(**kw):
    mac_dinh = dict(bai_con_lai=40, phut_moi_bai=14, phut_moi_ngay_muc_tieu=10)
    return rm.uoc_luong(**{**mac_dinh, **kw})


def test_hoc_nhieu_phut_moi_ngay_thi_xong_som_hon():
    """Đây là thứ hằng số cũ không làm được: hai người cùng band, khác nhịp, cùng con số."""
    cham = _uoc(phut_moi_ngay_muc_tieu=10)
    nhanh = _uoc(phut_moi_ngay_muc_tieu=30)
    assert nhanh.tuan_toi_da < cham.tuan_toi_da


def test_con_it_bai_thi_con_it_tuan():
    assert _uoc(bai_con_lai=5).tuan_toi_da < _uoc(bai_con_lai=50).tuan_toi_da


def test_xong_het_thi_bao_da_xong():
    kq = _uoc(bai_con_lai=0)
    assert kq.tuan_toi_da == 0
    assert "hoàn thành" in kq.mo_ta_vi


# --- Tốc độ thật thay cho mục tiêu tự đặt ---

def test_tuan_dau_dung_muc_tieu_tu_dat():
    kq = _uoc(so_ngay_da_hoc=2, bai_da_xong=1, phut_da_hoc=20)
    assert kq.theo_toc_do_that is False
    assert "mục tiêu bạn đặt" in kq.mo_ta_vi


def test_du_du_lieu_thi_chuyen_sang_toc_do_that():
    kq = _uoc(so_ngay_da_hoc=10, bai_da_xong=8, phut_da_hoc=112)
    assert kq.theo_toc_do_that is True
    assert "tốc độ học thật" in kq.mo_ta_vi


def test_dat_muc_tieu_cao_nhung_hoc_it_thi_uoc_luong_dai_ra():
    """Người đặt 30 phút/ngày mà học 5 phút phải thấy con số thật, không phải con số mong muốn."""
    theo_muc_tieu = _uoc(phut_moi_ngay_muc_tieu=30, so_ngay_da_hoc=2, bai_da_xong=1, phut_da_hoc=10)
    theo_that = _uoc(phut_moi_ngay_muc_tieu=30, so_ngay_da_hoc=10, bai_da_xong=4, phut_da_hoc=50)
    assert theo_that.tuan_toi_da > theo_muc_tieu.tuan_toi_da


# --- Không nổ ở các ca biên ---

@pytest.mark.parametrize("kw", [
    {"so_ngay_da_hoc": 0, "phut_da_hoc": 0, "bai_da_xong": 0},
    {"phut_moi_ngay_muc_tieu": 0},
    {"phut_moi_bai": 0},
    {"so_ngay_da_hoc": 30, "bai_da_xong": 10, "phut_da_hoc": 0},
])
def test_khong_chia_cho_khong(kw):
    kq = _uoc(**kw)
    assert kq.tuan_toi_thieu >= 1
    assert kq.tuan_toi_da >= kq.tuan_toi_thieu


def test_luon_tra_ve_mot_khoang_khong_phai_con_so_gia_vo_chinh_xac():
    kq = _uoc(bai_con_lai=40)
    assert kq.tuan_toi_thieu < kq.tuan_toi_da
    assert "–" in kq.mo_ta_vi


def test_mo_ta_luon_noi_ro_dua_tren_can_cu_nao():
    for kw in ({}, {"so_ngay_da_hoc": 10, "bai_da_xong": 8, "phut_da_hoc": 112}):
        assert "dựa trên" in _uoc(**kw).mo_ta_vi
