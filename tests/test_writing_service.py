"""Test bộ chấm viết. Test quan trọng nhất là "cùng ý, khác cách viết, vẫn đạt" —
nó bắt lỗi chấm quá khắt khe, thứ hỏng hơn nhiều so với chấm rộng tay."""
import inspect

import pytest

from app.services import writing_service as ws

EMAIL = {
    "kind": "guided_email",
    "min_words": 12,
    "required_chunks": [
        ["i'd like to take", "i would like to take", "i want to take", "can i take"],
        ["next monday", "on monday"],
        ["let me know", "please let me know", "is that ok"],
    ],
    "common_mistakes": [{"mistake": "I very like", "fix_vi": "Dùng “I really like”, không phải “I very like”."}],
}


# --- Không có AI ---

def test_cham_viet_khong_goi_llm():
    """Ràng buộc nền của project: app phải dạy đủ khi không có API key nào.

    Kiểm bằng danh sách import chứ không phải grep chuỗi — chú thích được phép nhắc tới LLM.
    """
    imports = {
        line.split()[1].split(".")[0]
        for line in inspect.getsource(ws).splitlines()
        if line.startswith(("import ", "from "))
    }
    cam = {"anthropic", "openai", "google", "httpx", "requests", "urllib", "socket", "aiohttp"}
    assert not (imports & cam), f"writing_service không được import {sorted(imports & cam)}"


# --- fill_blank ---

FILL = {"kind": "fill_blank", "blanks": [["on leave", "off"], ["tomorrow"]]}


def test_fill_blank_dung_het_duoc_100():
    assert ws.grade(FILL, ["on leave", "tomorrow"])["score"] == 100


def test_fill_blank_nhan_moi_dap_an_trong_danh_sach():
    assert ws.grade(FILL, ["off", "tomorrow"])["score"] == 100


def test_fill_blank_sai_chinh_ta_mot_ky_tu_van_duoc_phan_lon_diem():
    kq = ws.grade(FILL, ["on leav", "tomorrow"])
    assert kq["score"] == round((ws.DIEM_GAN_DUNG + 100) / 2)
    assert "chính tả" in kq["feedback_vi"]


def test_fill_blank_sai_han_thi_khong_duoc_diem_o_do():
    kq = ws.grade(FILL, ["banana", "tomorrow"])
    assert kq["score"] == 50


def test_fill_blank_bo_trong_het_duoc_0():
    assert ws.grade(FILL, ["", ""])["score"] == 0


# --- reorder: điểm từng phần ---

REORDER = {"kind": "reorder", "ordered_lines": ["Hi team.", "The server is down.", "Thanks."]}


def test_reorder_dung_het_duoc_100():
    assert ws.grade(REORDER, REORDER["ordered_lines"])["score"] == 100


def test_reorder_sai_mot_cap_van_duoc_diem_cao_khong_phai_0():
    kq = ws.grade(REORDER, ["Hi team.", "Thanks.", "The server is down."])
    assert 0 < kq["score"] < 100, "sắp gần đúng phải được điểm gần đúng"
    assert kq["score"] >= 60


def test_reorder_thieu_cau_thi_bao_thieu():
    kq = ws.grade(REORDER, ["Hi team."])
    assert kq["score"] == 0
    assert "đủ" in kq["feedback_vi"]


# --- guided_email: chấm rộng tay ---

@pytest.mark.parametrize("bai_viet", [
    "Hi Linh, I'd like to take next Monday off as annual leave. Please let me know. Thanks, Hoa.",
    "Hello Linh, I would like to take a day on Monday. Let me know if that works. Regards, Hoa.",
    "Dear Linh, Can I take next Monday as leave? Please let me know soon. Best, Hoa.",
])
def test_cung_mot_y_ba_cach_viet_khac_nhau_deu_dat(bai_viet):
    """Test quan trọng nhất của file: chấm luật không được phạt cách diễn đạt khác."""
    kq = ws.grade(EMAIL, bai_viet)
    assert kq["score"] >= 75, f"{kq['score']} — {kq['feedback_vi']}"
    assert kq["correct"] is True


def test_email_thieu_chao_va_ket_bi_tru_phan_cau_truc():
    day_du = ws.grade(EMAIL, "Hi Linh, I'd like to take next Monday off. Please let me know. Thanks.")
    thieu = ws.grade(EMAIL, "I'd like to take next Monday off and please let me know about it soon")
    assert thieu["score"] < day_du["score"]
    assert "thiếu" in thieu["feedback_vi"].lower()


def test_email_thieu_y_bat_buoc_thi_duoc_goi_y_cu_the():
    kq = ws.grade(EMAIL, "Hi Linh, I need something next Monday. Please let me know. Thanks, Hoa.")
    assert "i'd like to take" in kq["feedback_vi"].lower()


def test_email_qua_ngan_bi_tru_phan_co_hoc():
    ngan = ws.grade(EMAIL, "Hi. Thanks.")
    du = ws.grade(EMAIL, "Hi Linh, I'd like to take next Monday off. Please let me know. Thanks.")
    assert ngan["score"] < 60
    assert ngan["detail"]["co_hoc"] < du["detail"]["co_hoc"], "chưa đủ số từ phải bị trừ phần cơ học"
    assert ngan["detail"]["so_tu"] == 2


def test_email_dinh_loi_thuong_gap_thi_hien_cach_sua():
    kq = ws.grade(EMAIL, "Hi Linh, I very like to take next Monday off. Please let me know. Thanks.")
    assert "really like" in kq["feedback_vi"]


def test_email_rong_khong_no_va_tra_ve_0():
    kq = ws.grade(EMAIL, "")
    assert kq["score"] == 0
    assert kq["feedback_vi"]


# --- Giữ nguyên hành vi của bộ luyện viết độc lập ---

def test_translate_van_chay_nhu_cu():
    task = {"kind": "translate", "accept": ["I'll send the report by end of day"]}
    assert ws.grade(task, "I'll send the report by end of day.")["score"] == 100
    assert ws.grade(task, "I will send report")["score"] < 100


def test_compose_van_chay_nhu_cu():
    task = {"kind": "compose", "keywords": ["in a meeting", "reply"], "min_words": 5}
    kq = ws.grade(task, "Sorry, I'm in a meeting now. I'll reply in an hour.")
    assert kq["score"] == 100


def test_noi_dung_luyen_viet_co_san_van_cham_duoc():
    """Chạy trên seeds/writing thật: mọi task phải chấm được, không nổ."""
    for bo in ws.list_sets():
        wset = ws.get_set(bo["id"])
        for task in wset["tasks"]:
            kq = ws.grade(task, "something")
            assert 0 <= kq["score"] <= 100
            assert kq["feedback_vi"]


# --- Phản hồi tiếng Việt luôn có ---

@pytest.mark.parametrize("task,answer", [
    (FILL, ["on leave", "tomorrow"]),
    (REORDER, REORDER["ordered_lines"]),
    (EMAIL, "Hi Linh, I'd like to take next Monday off. Please let me know. Thanks, Hoa."),
    ({"kind": "translate", "accept": ["I work in IT"]}, "I work in IT"),
])
def test_phan_hoi_tieng_viet_khong_rong_ke_ca_khi_dat_100(task, answer):
    kq = ws.grade(task, answer)
    assert kq["feedback_vi"].strip(), "kể cả điểm tuyệt đối cũng phải nói cụ thể cái gì đã đúng"


def test_dang_bai_la_thi_bao_loi_ro_rang():
    kq = ws.grade({"kind": "khong_ton_tai"}, "abc")
    assert kq["score"] == 0


# --- Thể loại `note`: status update / standup / comment review không có lời chào ---

NOTE = {**EMAIL, "style": "note"}


def test_note_khong_bi_tru_diem_vi_thieu_loi_chao():
    """Standup và status update vốn dĩ không mở bằng “Hi X” — đòi nó là dạy sai văn phong."""
    bai = "I'd like to take next Monday off. Let me know if that works for the team."
    assert ws.grade(NOTE, bai)["score"] > ws.grade(EMAIL, bai)["score"]
    assert ws.grade(NOTE, bai)["score"] == 100


def test_email_van_bi_doi_loi_chao_va_loi_ket():
    """Nới cho `note` không được nới luôn cho email thật."""
    kq = ws.grade(EMAIL, "I'd like to take next Monday off. Let me know if that works.")
    assert kq["score"] < 100
    assert "chào" in kq["feedback_vi"]


def test_note_van_bi_tru_khi_thieu_y_bat_buoc():
    """`note` chỉ nới phần cấu trúc, không nới phần nội dung."""
    kq = ws.grade(NOTE, "Something happened today and I will look at it tomorrow morning.")
    assert kq["score"] < 70
    assert "thiếu" in kq["feedback_vi"].lower()
