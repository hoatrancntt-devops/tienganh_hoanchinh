"""Test hai form đề thật: cân đối, tương đương nhau, và không rò đáp án xuống client."""
import pytest

from app.api.routes.placement import SECRET_FIELDS, get_form
from app.models.enums import Cefr
from app.services import placement_scoring as sc
from app.services import placement_service as ps
from app.services import writing_service as ws

FORMS = ["A", "B"]
SKILL_SECTIONS = ("listening", "speaking", "reading", "writing")


def _form(name):
    return ps.load_form(name)


def _difficulties(form, section):
    return sorted(i.get("difficulty", 2) for i in form["items"] if i["section"] == section)


# --- Bốn kỹ năng đều có mặt ---

@pytest.mark.parametrize("name", FORMS)
def test_de_do_du_bon_ky_nang(name):
    có = {i["section"] for i in _form(name)["items"]}
    thiếu = set(SKILL_SECTIONS) - có
    assert not thiếu, f"form {name} thiếu phần: {thiếu}"


@pytest.mark.parametrize("name", FORMS)
def test_cau_hoi_doc_bang_tieng_anh(name):
    """Hỏi bằng tiếng Việt là đo hiểu tiếng Việt, không phải đọc hiểu tiếng Anh."""
    for item in _form(name)["items"]:
        if item["section"] == "reading":
            assert item.get("prompt_en"), f"{item['id']} thiếu câu hỏi tiếng Anh"


@pytest.mark.parametrize("name", FORMS)
def test_phan_doc_va_viet_khong_bao_gio_sinh_audio(name):
    """Bài đọc mà nghe được thì không còn là bài đọc.

    Kiểm bằng hành vi của `audio_text` — đó là một chỗ duy nhất quyết định câu nào có
    tiếng, dùng chung cho cả bộ sinh audio lẫn API trả đề.
    """
    for item in _form(name)["items"]:
        if item["section"] in ("reading", "writing", "vocab", "grammar", "self"):
            assert ps.audio_text(item) is None, f"{item['id']} sẽ bị sinh audio"


def test_read_aloud_khong_can_tieng_nhung_repeat_thi_can():
    """read_aloud có chữ trên màn hình; repeat thì không, nên bắt buộc phải có tiếng."""
    assert ps.audio_text({"section": "speaking", "kind": "read_aloud",
                          "expected_text": "He works in IT."}) is None
    assert ps.audio_text({"section": "speaking", "kind": "repeat",
                          "expected_text": "He works in IT."}) == "He works in IT."


# --- Hai form phải tương đương ---

@pytest.mark.parametrize("section", ["vocab", "grammar", "listening", "reading", "writing"])
def test_hai_form_cung_phan_bo_do_kho(section):
    """Thi lại bằng form khác mà lệch độ khó thì kết quả lệch, và không ai biết."""
    a, b = _difficulties(_form("A"), section), _difficulties(_form("B"), section)
    assert a == b, f"section '{section}': form A {a} vs form B {b}"


@pytest.mark.parametrize("section", list(SKILL_SECTIONS) + ["vocab", "grammar", "self"])
def test_hai_form_cung_so_cau_moi_phan(section):
    assert (ps._section_sizes(_form("A")).get(section)
            == ps._section_sizes(_form("B")).get(section))


# --- Ngân sách thời gian ---

@pytest.mark.parametrize("name", FORMS)
def test_de_khong_dai_qua_18_phut(name):
    """Bỏ ngang ở bước đầu tiên là rủi ro lớn nhất của cả thiết kế bốn kỹ năng."""
    assert _form(name)["est_minutes"] <= 18


# --- Không rò đáp án ---

@pytest.mark.parametrize("name", FORMS)
async def test_form_tra_ve_client_khong_chua_dap_an(name):
    payload = await get_form(name)
    for item in payload["items"]:
        lo = SECRET_FIELDS & set(item)
        assert not lo, f"{item['id']} rò trường bí mật: {sorted(lo)}"


@pytest.mark.parametrize("name", FORMS)
async def test_client_van_du_thong_tin_de_dung_giao_dien(name):
    """Lột đáp án xong vẫn phải biết SỐ ô để vẽ ô nhập."""
    goc = {i["id"]: i for i in _form(name)["items"]}
    for item in (await get_form(name))["items"]:
        if goc[item["id"]].get("blanks"):
            assert item["so_o"] == len(goc[item["id"]]["blanks"])


# --- Chấm được đầu-cuối ---

@pytest.mark.parametrize("name", FORMS)
def test_moi_cau_viet_deu_cham_duoc(name):
    for item in _form(name)["items"]:
        if item["section"] == "writing":
            kq = ws.grade(item, ["x"] * 3)
            assert 0 <= kq["score"] <= 100
            assert kq["feedback_vi"]


@pytest.mark.parametrize("name", FORMS)
def test_bai_viet_mau_dat_diem_cao(name):
    """`sample_en` là bài mẫu do chính mình viết — nó phải qua được bộ chấm của chính mình."""
    for item in _form(name)["items"]:
        if item["section"] == "writing" and item.get("sample_en"):
            kq = ws.grade(item, item["sample_en"])
            assert kq["score"] >= 75, f"{item['id']}: mẫu chỉ được {kq['score']} — {kq['feedback_vi']}"


def _perfect_axes(name):
    """Điểm từng trục khi trả lời đúng 100%."""
    form = _form(name)
    sizes = ps._section_sizes(form)
    out = {}
    for sec, key in [("listening", "listening"), ("reading", "reading")]:
        diem = [sc.score_mcq(i.get("difficulty", 2), True, 0, sec == "listening")
                for i in form["items"] if i["section"] == sec]
        out[key] = sc.section_average(diem, sizes[sec])
    kn = [sc.score_mcq(i.get("difficulty", 2), True, 0, False)
          for i in form["items"] if i["section"] in ("vocab", "grammar")]
    out["knowledge"] = sc.section_average(kn, sizes["vocab"] + sizes["grammar"])
    out["writing"] = 95.0
    out["speaking"] = 95.0
    return out


@pytest.mark.parametrize("name", FORMS)
def test_lam_dung_het_tren_de_that_thi_dat_b1(name):
    verdict = sc.decide(_perfect_axes(name), speech_available=True, silent_count=0)
    assert verdict.band == Cefr.B1, f"form {name}: overall={verdict.overall}"


@pytest.mark.parametrize("name", FORMS)
def test_hai_form_cho_ket_qua_lech_khong_qua_5_diem(name):
    a = sc.decide(_perfect_axes("A"), True, 0).overall
    b = sc.decide(_perfect_axes("B"), True, 0).overall
    assert abs(a - b) <= 5, f"form A {a} vs form B {b}"


# --- Hai trục kỹ năng phải thật sự độc lập ---

def test_doc_tot_nghe_kem_khac_nghe_tot_doc_kem():
    """Nếu hai ca này ra cùng kết quả thì trục mới chỉ là trang trí."""
    doc_tot = sc.decide({"listening": 30, "reading": 85, "speaking": 55,
                         "writing": 60, "knowledge": 70}, True, 0)
    nghe_tot = sc.decide({"listening": 85, "reading": 30, "speaking": 55,
                          "writing": 60, "knowledge": 70}, True, 0)
    assert doc_tot.overall != nghe_tot.overall


def test_thieu_phan_noi_van_xep_duoc_tu_ba_ky_nang_con_lai():
    v = sc.decide({"listening": 70, "reading": 72, "writing": 65, "knowledge": 68},
                  speech_available=False, silent_count=0)
    assert v.band != Cefr.PRE_A1
    assert v.confidence == "low"


def test_knowledge_khong_tinh_vao_luat_lech_ky_nang():
    """`knowledge` là trục phụ. Kéo nó vào sẽ báo lệch ở học viên hoàn toàn bình thường."""
    v = sc.decide({"listening": 70, "reading": 70, "speaking": 70, "writing": 70,
                   "knowledge": 20}, True, 0)
    assert v.confidence == "high"


# --- Tên file audio phải đổi khi lời câu nghe đổi ---

@pytest.mark.parametrize("name", FORMS)
def test_moi_cau_co_tieng_deu_co_ten_file_kem_hash(name):
    for item in _form(name)["items"]:
        ten = ps.audio_name(item)
        if ps.audio_text(item):
            assert ten and ten.startswith(item["id"] + "-") and ten.endswith(".wav")
        else:
            assert ten is None, f"{item['id']} không nên có audio"


def test_doi_loi_cau_nghe_thi_doi_ten_file():
    """Bảo vệ chính xác cái bẫy đã dính: sửa lời nhưng giữ mã câu, học viên nghe file cũ.

    Bộ sinh audio bỏ qua file đã tồn tại, nên tên trùng = tiếng cũ + câu hỏi mới, và
    không có gì báo.
    """
    goc = {"id": "L3", "section": "listening", "transcript_en": "He works in the IT department."}
    sua = {"id": "L3", "section": "listening", "transcript_en": "Sorry, I can't join right now."}
    assert ps.audio_name(goc) != ps.audio_name(sua)


@pytest.mark.parametrize("name", FORMS)
async def test_api_tra_ve_url_audio_dung_ten_file(name):
    for item in (await get_form(name))["items"]:
        goc = next(i for i in _form(name)["items"] if i["id"] == item["id"])
        if ps.audio_text(goc):
            assert item["audio"] == f"/media/placement/{ps.audio_name(goc)}"
        else:
            assert "audio" not in item
