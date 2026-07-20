"""Luyện viết — bài tập gõ câu, chấm bằng so khớp chuẩn hoá (KHÔNG cần LLM).

Stateless: nội dung tĩnh từ seeds/writing/*.yaml, không lưu DB. Hai loại bài:
- translate: dịch Việt→Anh, so với danh sách đáp án chấp nhận (khớp chính xác hoặc gần).
- compose: viết theo yêu cầu, chấm bằng độ phủ từ khoá + độ dài tối thiểu.
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


def grade(task: dict, answer: str) -> dict:
    kind = task.get("kind", "translate")
    ans = (answer or "").strip()
    if not ans:
        return {"score": 0, "correct": False, "feedback_vi": "Bạn chưa viết gì.",
                "sample": task.get("sample_en") or (task.get("accept") or [""])[0]}

    if kind == "compose":
        return _grade_compose(task, ans)
    return _grade_translate(task, ans)


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
