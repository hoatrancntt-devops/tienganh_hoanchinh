"""Luyện viết — bài tập gõ câu, chấm bằng so khớp chuẩn hoá (KHÔNG cần LLM).

Dùng chung cho hai chỗ:
- Bộ luyện viết độc lập ở /learn/write (nội dung tĩnh từ seeds/writing/*.yaml, không lưu DB)
- `writing_task` nhúng trong từng bài học (nội dung từ seeds/content/**, có tính vào mastery)

Sáu dạng bài, tất cả chấm được bằng luật:
- translate:         dịch Việt→Anh, so với danh sách đáp án chấp nhận
- compose:           viết theo yêu cầu, chấm bằng độ phủ từ khoá + độ dài tối thiểu
- fill_blank:        điền từ vào chỗ trống
- error_correction:  sửa câu sai
- reorder:           sắp xếp câu thành đoạn đúng thứ tự
- guided_email:      viết email theo khung, chấm bốn tầng

Nguyên tắc chấm: THƯỞNG CÁI LÀM ĐƯỢC, KHÔNG PHẠT CÁI KHÔNG PHÁT HIỆN ĐƯỢC. Luật không
đọc hiểu ngữ nghĩa, nên thứ nó không kiểm tra được đều mặc định là đạt. Chấm chặt bằng luật
sẽ đánh trượt người viết đúng theo cách khác — hỏng hơn nhiều so với cho điểm rộng tay.
"""
import re
import unicodedata
from pathlib import Path

import yaml

WR_DIR = Path("seeds/writing")
_cache: dict[str, dict] = {}


def _load_all() -> dict[str, dict]:
    if _cache:
        return _cache
    for path in sorted(WR_DIR.glob("WR-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        _cache[data["id"]] = data
    return _cache


def list_sets() -> list[dict]:
    return [
        {"id": d["id"], "title_vi": d["title_vi"], "context_vi": d.get("context_vi", ""),
         "topic": d.get("topic", "core"), "count": len(d.get("tasks", []))}
        for d in _load_all().values()
    ]


def get_set(sid: str) -> dict | None:
    return _load_all().get(sid)


def _normalize(s: str) -> str:
    """Bỏ hoa/thường, dấu câu cuối, nháy cong, khoảng trắng thừa để so khớp công bằng."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[.!?,;:\"]+", "", s)
    return s.strip()


def _tokens(s: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9']+", _normalize(s)) if t]


def _f1(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    sa = {}
    for t in ta:
        sa[t] = sa.get(t, 0) + 1
    overlap = 0
    for t in tb:
        if sa.get(t, 0) > 0:
            sa[t] -= 1
            overlap += 1
    if overlap == 0:
        return 0.0
    prec, rec = overlap / len(tb), overlap / len(ta)
    return 2 * prec * rec / (prec + rec)


def grade(task: dict, answer: str | list[str]) -> dict:
    """Chấm một bài viết.

    `answer` là chuỗi với các dạng một ô (translate/compose/guided_email), hoặc danh sách
    với các dạng nhiều ô (fill_blank/error_correction/reorder).
    """
    kind = task.get("kind", "translate")

    if kind in ("fill_blank", "error_correction"):
        return _grade_blanks(task, _as_list(answer))
    if kind == "reorder":
        return _grade_reorder(task, _as_list(answer))

    ans = (answer if isinstance(answer, str) else " ".join(_as_list(answer))).strip()
    if not ans:
        return {"score": 0, "correct": False, "feedback_vi": "Bạn chưa viết gì.",
                "sample": task.get("sample_en") or (task.get("accept") or [""])[0]}
    if kind == "guided_email":
        return _grade_guided_email(task, ans)
    if kind == "compose":
        return _grade_compose(task, ans)
    return _grade_translate(task, ans)


def _as_list(answer: str | list[str]) -> list[str]:
    if isinstance(answer, list):
        return [str(a) for a in answer]
    return [answer] if answer else []


def _levenshtein(a: str, b: str) -> int:
    """Chỉ dùng để phân biệt lỗi gõ với lỗi từ vựng, nên không cần tối ưu."""
    if a == b:
        return 0
    if not a or not b:
        return len(a) or len(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


GAN_DUNG_TOI_DA = 2      # sai <=2 ký tự -> lỗi gõ, không phải sai từ
DIEM_GAN_DUNG = 80


def _grade_blanks(task: dict, answers: list[str]) -> dict:
    """fill_blank / error_correction: chấm từng ô rồi lấy trung bình.

    Sai chính tả 1-2 ký tự vẫn được phần lớn điểm — người mất gốc gõ sai chính tả liên tục,
    đánh trượt vì chuyện đó thì không đo được cái đang muốn đo.
    """
    blanks: list[list[str]] = task.get("blanks") or []
    if not blanks:
        return {"score": 0, "correct": False, "feedback_vi": "Bài này thiếu dữ liệu để chấm.",
                "sample": ""}
    diem: list[int] = []
    sai: list[str] = []
    for i, accept in enumerate(blanks):
        ans = _normalize(answers[i] if i < len(answers) else "")
        chuan = [_normalize(a) for a in accept]
        if ans and ans in chuan:
            diem.append(100)
        elif ans and any(_levenshtein(ans, c) <= GAN_DUNG_TOI_DA for c in chuan):
            diem.append(DIEM_GAN_DUNG)
            sai.append(f"ô {i + 1} gần đúng, chỉ sai chính tả (“{accept[0]}”)")
        else:
            diem.append(0)
            sai.append(f"ô {i + 1} chưa đúng — đáp án “{accept[0]}”")
    score = round(sum(diem) / len(diem))
    if not sai:
        fb = "Bạn điền đúng tất cả các ô."
    else:
        fb = ("Gần được rồi. " if score >= 60 else "Còn vài chỗ cần sửa. ") + "; ".join(sai[:3]) + "."
    if task.get("hint_vi"):
        fb += " Gợi ý: " + task["hint_vi"]
    return {"score": score, "correct": score >= 80, "feedback_vi": fb,
            "sample": " / ".join(b[0] for b in blanks), "detail": {"tung_o": diem}}


def _grade_reorder(task: dict, answers: list[str]) -> dict:
    """reorder: tính theo số cặp đúng thứ tự, KHÔNG chấm nhị phân.

    Sắp gần đúng phải được điểm gần đúng — sai một chỗ mà mất trắng thì học viên không học
    được gì từ kết quả.
    """
    dung: list[str] = task.get("ordered_lines") or []
    if len(dung) < 2:
        return {"score": 0, "correct": False, "feedback_vi": "Bài này thiếu dữ liệu để chấm.",
                "sample": ""}
    vi_tri = {_normalize(line): i for i, line in enumerate(dung)}
    nop = [vi_tri.get(_normalize(a)) for a in answers]
    nop = [x for x in nop if x is not None]
    mau = " → ".join(dung)
    if len(nop) < len(dung):
        return {"score": 0, "correct": False, "sample": mau,
                "feedback_vi": "Bạn chưa xếp đủ số câu."}
    tong = len(nop) * (len(nop) - 1) // 2
    dung_cap = sum(1 for i in range(len(nop)) for j in range(i + 1, len(nop)) if nop[i] < nop[j])
    score = round(100 * dung_cap / tong) if tong else 100
    fb = ("Bạn xếp đúng toàn bộ thứ tự." if score == 100
          else f"Thứ tự chưa đúng hẳn — bạn xếp đúng {dung_cap}/{tong} cặp câu.")
    return {"score": score, "correct": score == 100, "feedback_vi": fb, "sample": mau,
            "detail": {"thu_tu_nop": nop}}


# guided_email chấm bốn tầng, cộng điểm, tổng đúng 100.
DIEM_CAU_TRUC, DIEM_NOI_DUNG, DIEM_CO_HOC, DIEM_LOI = 25, 40, 20, 15
CHAO = ("hi", "hello", "dear", "good morning", "good afternoon")
KET = ("thanks", "thank you", "regards", "best", "cheers", "sincerely")


def _grade_guided_email(task: dict, ans: str) -> dict:
    """Dạng duy nhất có đầu ra tự do.

    `required_chunks` là danh sách NHÓM, mỗi nhóm gồm nhiều cách diễn đạt cùng một ý. Thiếu
    biến thể là nguyên nhân số một khiến chấm luật đánh trượt người viết đúng.
    """
    thuong = _normalize(ans)
    tu = _tokens(ans)
    thieu: list[str] = []

    co_chao = any(thuong.startswith(c) for c in CHAO) or any(f" {c} " in f" {thuong} " for c in CHAO)
    co_ket = any(k in thuong[-70:] for k in KET)
    co_than = len(tu) >= 5
    diem_cau_truc = DIEM_CAU_TRUC * sum([co_chao, co_than, co_ket]) / 3
    if not co_chao:
        thieu.append("lời chào ở đầu (Hi / Hello / Dear + tên)")
    if not co_ket:
        thieu.append("lời kết (Thanks / Regards) trước khi ký tên")

    nhom: list[list[str]] = task.get("required_chunks") or []
    dat = [any(_normalize(bt) in thuong for bt in g) for g in nhom]
    diem_noi_dung = DIEM_NOI_DUNG * (sum(dat) / len(dat)) if dat else DIEM_NOI_DUNG
    for g, ok in zip(nhom, dat, strict=True):
        if not ok:
            thieu.append(f"ý “{g[0]}”")

    min_words = int(task.get("min_words") or 0)
    raw = ans.strip()
    du_dai = len(tu) >= min_words
    diem_co_hoc = DIEM_CO_HOC * sum([du_dai, raw[:1].isupper(), raw[-1:] in ".!?"]) / 3
    if not du_dai:
        thieu.append(f"độ dài (cần ít nhất {min_words} từ, bạn viết {len(tu)})")

    mistakes: list[dict] = task.get("common_mistakes") or []
    dinh = [m for m in mistakes
            if _normalize(m.get("mistake", "")) and _normalize(m["mistake"]) in thuong]
    diem_loi = DIEM_LOI * max(0.0, 1 - len(dinh) / len(mistakes)) if mistakes else DIEM_LOI

    score = min(100, round(diem_cau_truc + diem_noi_dung + diem_co_hoc + diem_loi))
    if not thieu and not dinh:
        fb = "Email của bạn đủ ba phần và có đủ thông tin người nhận cần."
    else:
        fb = ("Gần được rồi. " if score >= 60 else "Còn vài chỗ cần sửa. ")
        if thieu:
            fb += "Còn thiếu: " + "; ".join(thieu[:3]) + ". "
        for m in dinh[:2]:
            fb += m.get("fix_vi", "") + " "
    return {
        "score": score, "correct": score >= 75, "feedback_vi": fb.strip(),
        "sample": task.get("sample_en", ""),
        "detail": {"cau_truc": round(diem_cau_truc, 1), "noi_dung": round(diem_noi_dung, 1),
                   "co_hoc": round(diem_co_hoc, 1), "loi_thuong_gap": round(diem_loi, 1),
                   "so_tu": len(tu)},
    }


def _grade_translate(task: dict, ans: str) -> dict:
    accept = task.get("accept", [])
    norm_ans = _normalize(ans)
    if any(norm_ans == _normalize(a) for a in accept):
        return {"score": 100, "correct": True, "feedback_vi": "Chính xác! 🎉",
                "sample": accept[0]}
    best = max((_f1(ans, a) for a in accept), default=0.0)
    score = round(best * 100)
    sample = accept[0] if accept else ""
    if score >= 75:
        fb = "Gần đúng — ý đúng rồi, chỉ khác chút. So với mẫu bên dưới nhé."
        correct = True
    elif score >= 45:
        fb = "Đúng một phần. Xem gợi ý và mẫu rồi thử lại."
        correct = False
    else:
        fb = "Chưa đúng. Xem gợi ý và câu mẫu, rồi viết lại."
        correct = False
    if task.get("hint_vi"):
        fb += " Gợi ý: " + task["hint_vi"]
    return {"score": score, "correct": correct, "feedback_vi": fb, "sample": sample}


def _grade_compose(task: dict, ans: str) -> dict:
    keywords = task.get("keywords", [])
    min_words = task.get("min_words", 3)
    norm = _normalize(ans)
    words = len(_tokens(ans))
    hit = [k for k in keywords if _normalize(k) in norm]
    missing = [k for k in keywords if _normalize(k) not in norm]
    coverage = len(hit) / len(keywords) if keywords else 1.0
    score = round(coverage * 100)
    if words < min_words:
        score = min(score, 40)

    if words < min_words:
        fb = f"Hơi ngắn — viết đủ ý hơn (ít nhất khoảng {min_words} từ)."
        correct = False
    elif not missing:
        fb = "Tốt! Đủ ý chính. Tham khảo thêm câu mẫu bên dưới."
        correct = True
    elif coverage >= 0.5:
        fb = "Khá ổn, nhưng còn thiếu ý: " + ", ".join(f"“{m}”" for m in missing) + "."
        correct = False
    else:
        fb = "Còn thiếu các ý quan trọng: " + ", ".join(f"“{m}”" for m in missing) + "."
        correct = False
    if task.get("hint_vi"):
        fb += " Gợi ý: " + task["hint_vi"]
    return {"score": score, "correct": correct, "feedback_vi": fb,
            "sample": task.get("sample_en", "")}


def invalidate() -> None:
    _cache.clear()
