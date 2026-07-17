"""Bậc 6 của thang fallback: rule-based. Đây là bậc quyết định sản phẩm sống hay chết khi AI hỏng.

Luôn có nội dung thật để trả về, vì vietnamese_explanation và common_mistakes là trường
bắt buộc trong mọi lesson (cổng chất lượng chặn publish nếu thiếu).
"""
import difflib
import re

from app.models.content import Item, Lesson


def static_explanation(lesson: Lesson | None, question: str) -> str:
    if lesson is None:
        return (
            "AI assistant chưa được bật nên mình chưa trả lời tự do được. "
            "Bạn xem phần “Giải thích” trong bài nhé — phần đó viết sẵn cho đúng câu hỏi này."
        )
    exp = lesson.vietnamese_explanation or {}
    parts = [exp.get("why_vi", ""), exp.get("how_vi", ""), exp.get("contrast_vi", "")]
    body = " ".join(p for p in parts if p)

    # Bắt từ khoá trong câu hỏi để trỏ đúng lỗi thường gặp đã soạn sẵn.
    lowered = question.lower()
    for mistake in lesson.common_mistakes or []:
        keywords = re.findall(r"\w+", (mistake.get("mistake", "") or "").lower())
        if any(k in lowered for k in keywords if len(k) > 3):
            body += (
                f"\n\nLỗi bạn đang hỏi rất phổ biến: {mistake.get('mistake', '')} "
                f"{mistake.get('why_vi', '')} Cách sửa: {mistake.get('fix_vi', '')}"
            )
            break
    if lesson.memory_trick_vi:
        body += f"\n\nMẹo nhớ: {lesson.memory_trick_vi}"
    return body or "Bài này chưa có phần giải thích. Bạn báo quản trị viên giúp mình nhé."


def _normalize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def sentence_repair(item: Item, said: str) -> str:
    expected = item.expected_text or ""
    if not expected:
        return open_feedback(item, said)
    exp_words, said_words = _normalize(expected), _normalize(said)
    matcher = difflib.SequenceMatcher(None, exp_words, said_words)
    problems = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            problems.append(f"thiếu “{' '.join(exp_words[i1:i2])}”")
        elif tag == "replace":
            problems.append(f"“{' '.join(said_words[j1:j2])}” đáng ra là “{' '.join(exp_words[i1:i2])}”")
        elif tag == "insert":
            problems.append(f"thừa “{' '.join(said_words[j1:j2])}”")
    if not problems:
        return f"Chuẩn rồi. Câu đúng: “{expected}”"
    # Chỉ nêu MỘT lỗi: sửa hết một lượt làm người học nản.
    return f"Gần đúng rồi. Chỗ cần sửa: {problems[0]}. Câu đúng: “{expected}”"


def open_feedback(item: Item, said: str) -> str:
    """Chấm bằng accept_patterns + độ phủ từ khoá."""
    said_words = set(_normalize(said))
    if not said_words:
        return "Mình chưa nghe được gì. Bạn thử ghi âm lại, nói to hơn một chút nhé."
    for pattern in item.accept_patterns or []:
        keys = {w for w in _normalize(re.sub(r"\{.*?\}", "", pattern)) if len(w) > 2}
        if keys and len(keys & said_words) / len(keys) >= 0.6:
            return "Câu trả lời của bạn đúng ý và người nghe hiểu được. Tiếp tục nhé."
    hint = (item.accept_patterns or [""])[0]
    return (
        "Ý của bạn chưa rõ với người nghe. "
        + (f"Thử theo mẫu: “{hint}”." if hint else "Thử trả lời ngắn và thẳng vào câu hỏi.")
    )


def unavailable_message() -> str:
    return (
        "Bạn đã dùng hết lượt hỏi AI hôm nay. Phần “Giải thích” và “Lỗi thường gặp” "
        "trong bài vẫn dùng được bình thường — mai bạn quay lại hỏi tiếp nhé."
    )
