"""Cổng chất lượng cho nội dung Đọc và Viết, chạy trên toàn bộ giáo trình thật.

Đây là thứ bắt lỗi soạn bài mà cổng schema không thấy: đáp án mẫu không qua nổi bộ chấm
của chính nó, bài đọc dài quá bậc, hoặc câu trả lời bừa vẫn được điểm cao.
"""
import pytest

from app.seeds.validate_content import load_all
from app.services import writing_service as ws

# Trần độ dài bài đọc theo bậc. Người mất gốc gặp một đoạn 120 từ ở bài thứ hai sẽ bỏ.
GIOI_HAN_TU = {"pre_a1": 60, "a1": 90, "a2": 130, "b1": 200}


@pytest.fixture(scope="module")
def lessons():
    items, errors = load_all()
    assert not errors, f"YAML không hợp lệ: {errors[:3]}"
    return items


@pytest.fixture(scope="module")
def co_doc(lessons):
    return [x for x in lessons if x.reading_passage]


@pytest.fixture(scope="module")
def co_viet(lessons):
    return [x for x in lessons if x.writing_task]


def _dap_an_dung(wt) -> list[str]:
    if wt.kind == "reorder":
        return list(wt.ordered_lines)
    if wt.blanks:
        return [nhom[0] for nhom in wt.blanks]
    return [wt.sample_en]


def _dap_an_bay(wt) -> list[str]:
    if wt.kind == "reorder":
        return list(reversed(wt.ordered_lines))
    if wt.blanks:
        return ["zzz"] * len(wt.blanks)
    return ["zzz"]


def test_co_it_nhat_mot_bai_co_doc_va_viet(co_doc, co_viet):
    assert co_doc and co_viet


def test_dap_an_dung_luon_duoc_diem_tuyet_doi(co_viet):
    """Bộ chấm phải chấp nhận chính đáp án mà người soạn khai là đúng."""
    hong = []
    for x in co_viet:
        kq = ws.grade(x.writing_task.model_dump(), _dap_an_dung(x.writing_task))
        if kq["score"] != 100:
            hong.append(f"{x.id}: {kq['score']} — {kq['feedback_vi']}")
    assert not hong, "\n".join(hong)


def test_tra_loi_bay_khong_duoc_diem_cao(co_viet):
    """Nếu gõ bừa vẫn qua thì bài viết không đo được gì."""
    de_dai = []
    for x in co_viet:
        kq = ws.grade(x.writing_task.model_dump(), _dap_an_bay(x.writing_task))
        if kq["score"] > 40:
            de_dai.append(f"{x.id}: trả lời bừa được {kq['score']}")
    assert not de_dai, "\n".join(de_dai)


def test_bai_mau_cua_guided_email_qua_duoc_bo_cham(co_viet):
    """`sample_en` là bài mẫu người soạn viết — nó phải qua bộ chấm của chính bài đó."""
    hong = []
    for x in co_viet:
        wt = x.writing_task
        if wt.kind == "guided_email" and wt.sample_en:
            kq = ws.grade(wt.model_dump(), wt.sample_en)
            if kq["score"] < 75:
                hong.append(f"{x.id}: mẫu chỉ được {kq['score']} — {kq['feedback_vi']}")
    assert not hong, "\n".join(hong)


def test_bai_doc_khong_dai_qua_bac(co_doc):
    qua_dai = []
    for x in co_doc:
        so_tu = len(x.reading_passage.text_en.split())
        tran = GIOI_HAN_TU[x.cefr_target]
        if so_tu > tran:
            qua_dai.append(f"{x.id} ({x.cefr_target}): {so_tu} từ, trần {tran}")
    assert not qua_dai, "\n".join(qua_dai)


def test_cau_hoi_doc_bang_tieng_anh(co_doc):
    """Hỏi bằng tiếng Việt là đo hiểu tiếng Việt, không phải đọc hiểu tiếng Anh."""
    co_dau = set("àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ")
    sai = []
    for x in co_doc:
        for q in x.reading_passage.questions:
            if co_dau & set(q.q_en.lower()):
                sai.append(f"{x.id}: “{q.q_en[:40]}” có dấu tiếng Việt")
    assert not sai, "\n".join(sai)


def test_bai_doc_khong_khai_truong_sinh_audio(co_doc):
    """Bài đọc mà nghe được thì không còn là bài đọc."""
    for x in co_doc:
        khai = x.reading_passage.model_dump()
        assert "transcript_en" not in khai
        assert "audio" not in khai


def test_moi_bai_co_doc_hoac_viet_deu_tinh_vao_mastery(lessons):
    """Có nội dung mà không có trọng số thì học viên làm xong cũng không được tính."""
    thieu = []
    for x in lessons:
        w = x.unlock_condition.mastery_weights
        if x.reading_passage and "read" not in w:
            thieu.append(f"{x.id}: có bài đọc nhưng mastery_weights thiếu 'read'")
        if x.writing_task and "write" not in w:
            thieu.append(f"{x.id}: có bài viết nhưng mastery_weights thiếu 'write'")
        if "read" in w and not x.reading_passage:
            thieu.append(f"{x.id}: có trọng số 'read' nhưng không có bài đọc")
        if "write" in w and not x.writing_task:
            thieu.append(f"{x.id}: có trọng số 'write' nhưng không có bài viết")
    assert not thieu, "\n".join(thieu)


def test_bai_doc_co_dap_an_trong_pham_vi(co_doc):
    for x in co_doc:
        for q in x.reading_passage.questions:
            assert 0 <= q.answer < len(q.choices), f"{x.id}: answer ngoài phạm vi"


def test_bai_doc_co_ban_dich_tieng_viet(co_doc):
    """Bản dịch ẩn tới khi trả lời xong, nhưng phải có — không ai đoán mò được cả đoạn."""
    for x in co_doc:
        assert x.reading_passage.text_vi.strip(), f"{x.id}: thiếu text_vi"


# --- Ngưỡng riêng từng kỹ năng ở checkpoint ---

def test_moi_checkpoint_deu_co_nguong_rieng_tung_ky_nang(lessons):
    """Điểm tổng che được một kỹ năng yếu: đọc 90 kéo nói 40 lên vẫn qua."""
    thieu = [x.id for x in lessons if x.is_checkpoint and not x.unlock_condition.min_per_skill]
    assert not thieu, f"checkpoint chưa đặt min_per_skill: {thieu}"


def test_nguong_rieng_chi_dat_cho_ky_nang_bai_do_thuc_su_do(lessons):
    """Đặt ngưỡng cho kỹ năng bài không đo thì học viên bị chặn bởi một con số không có thật."""
    sai = []
    for x in lessons:
        w = x.unlock_condition.mastery_weights
        for ky_nang in x.unlock_condition.min_per_skill:
            if ky_nang not in w:
                sai.append(f"{x.id}: đặt ngưỡng '{ky_nang}' nhưng mastery_weights không đo nó")
    assert not sai, "\n".join(sai)


def test_nguong_rieng_khong_cao_hon_nguong_tong(lessons):
    """Ngưỡng riêng cao hơn ngưỡng tổng thì nó thành cổng chặn cứng, không còn là cảnh báo."""
    sai = []
    for x in lessons:
        tong = x.unlock_condition.mastery_threshold
        for ky_nang, n in x.unlock_condition.min_per_skill.items():
            if n > tong:
                sai.append(f"{x.id}: ngưỡng '{ky_nang}'={n} > ngưỡng tổng {tong}")
    assert not sai, "\n".join(sai)
