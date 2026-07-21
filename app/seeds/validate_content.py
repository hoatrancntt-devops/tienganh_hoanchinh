"""Cổng chất lượng. Chạy trong CI, không chạy bằng thiện chí.

Chặn publish nếu thiếu vietnamese_explanation hoặc <2 common_mistakes — hai trường
đó giữ cho app hoạt động khi không có AI key; thiếu chúng là thủng tầng fallback.
"""
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.seeds.schema import LessonYAML

CONTENT_DIR = Path("seeds/content")


def check_units(lessons: list[LessonYAML]) -> list[str]:
    """Bắt sớm lỗi unit chưa khai báo — nếu không, seed lúc deploy mới nổ."""
    from app.seeds.loader import UNITS  # lazy: loader nhập ngược module này

    declared = {code for code, *_ in UNITS}
    errors = []
    for lesson in lessons:
        if lesson.unit not in declared:
            errors.append(f"{lesson.id}: unit '{lesson.unit}' chưa khai báo trong loader.UNITS.")
    return errors


def load_all() -> tuple[list[LessonYAML], list[str]]:
    lessons, errors = [], []
    files = sorted(CONTENT_DIR.rglob("*.yaml"))
    if not files:
        errors.append(f"Không tìm thấy file YAML nào trong {CONTENT_DIR}")
        return lessons, errors

    for path in files:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: YAML hỏng — {exc}")
            continue
        try:
            lessons.append(LessonYAML(**raw))
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(x) for x in err["loc"])
                errors.append(f"{path.name}: {loc} — {err['msg']}")
    return lessons, errors


def check_graph(lessons: list[LessonYAML]) -> list[str]:
    errors = []
    codes = {lesson.id for lesson in lessons}
    if len(codes) != len(lessons):
        errors.append("Có mã bài trùng nhau.")

    edges: dict[str, list[str]] = {}
    for lesson in lessons:
        for pre in lesson.prerequisites:
            if pre.lesson not in codes:
                errors.append(f"{lesson.id}: tiên quyết '{pre.lesson}' không tồn tại.")
            edges.setdefault(lesson.id, []).append(pre.lesson)

    # Chu trình: bắt lúc validate, không phải lúc học viên bị kẹt.
    color: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for nxt in edges.get(node, []):
            if color.get(nxt) == 1:
                cycle = " -> ".join(stack[stack.index(nxt):] + [nxt])
                errors.append(f"Vòng lặp trong DAG: {cycle}")
                return
            if color.get(nxt) is None:
                visit(nxt)
        stack.pop()
        color[node] = 2

    for lesson in lessons:
        if color.get(lesson.id) is None:
            visit(lesson.id)

    # Bài không thể tới được: có tiên quyết nhưng không nằm trong chuỗi nào bắt đầu từ gốc.
    roots = {lesson.id for lesson in lessons if not lesson.prerequisites}
    if not roots:
        errors.append("Không có bài gốc nào (bài không cần tiên quyết) — học viên không vào được.")
    return errors


def check_pedagogy(lessons: list[LessonYAML]) -> list[str]:
    errors = []
    for lesson in lessons:
        exp = lesson.vietnamese_explanation
        if not exp.why_vi.strip() or not exp.how_vi.strip():
            errors.append(f"{lesson.id}: vietnamese_explanation rỗng — thủng tầng fallback không-AI.")
        if len(lesson.common_mistakes) < 2:
            errors.append(f"{lesson.id}: cần ≥2 common_mistakes.")
        for m in lesson.common_mistakes:
            if not m.fix_vi.strip():
                errors.append(f"{lesson.id}: common_mistake '{m.mistake[:30]}' thiếu fix_vi.")
        if not lesson.is_checkpoint and not lesson.mini_quiz:
            errors.append(f"{lesson.id}: chưa có mini_quiz.")
        for v in lesson.vocabulary:
            if not v.chunk.strip() or not v.ipa.strip():
                errors.append(f"{lesson.id}: vocab '{v.term}' thiếu chunk hoặc ipa.")
        for q in lesson.mini_quiz:
            if not 0 <= q.answer < len(q.choices):
                errors.append(f"{lesson.id}: quiz '{q.prompt_vi[:30]}' có answer ngoài phạm vi.")
            if q.kind == "mcq_listen" and not q.audio_text:
                errors.append(f"{lesson.id}: quiz mcq_listen thiếu audio_text.")
        if lesson.listening_snippet:
            for q in lesson.listening_snippet.questions:
                if not 0 <= q.answer < len(q.choices):
                    errors.append(f"{lesson.id}: câu nghe có answer ngoài phạm vi.")
    return errors


# Bộ ký hiệu mà speech_service/g2p.py có thể sinh ra. Tag nằm ngoài đây sẽ không bao giờ
# khớp với kết quả chấm, nên phản hồi lỗi phát âm im lặng không chạy — không có gì báo sai.
# Cố ý chép lại thay vì import: app và speech_service là hai service riêng, app không phụ
# thuộc speech_service lúc chạy. Nếu g2p đổi bộ ký hiệu thì phải cập nhật danh sách này.
# Lưu ý hai cái bẫy đã từng dính:
#   - 'g' là U+0067 ASCII, KHÔNG phải 'ɡ' U+0261 (script g) hay dùng trong chuỗi ipa.
#   - g2p không dùng dấu dài ('i' chứ không phải 'iː') và phân rã cụm phụ âm thành âm đơn
#     ('s' + 't', không phải 'st').
G2P_PHONEMES = {
    "aɪ", "aʊ", "b", "d", "dʒ", "eɪ", "f", "g", "h", "i", "j", "k", "l", "m", "n",
    "oʊ", "p", "r", "s", "t", "tʃ", "u", "v", "w", "z", "æ", "ð", "ŋ", "ɑ", "ɑr",
    "ɔ", "ɔr", "ɔɪ", "ə", "ər", "ɛ", "ɛr", "ɜr", "ɪ", "ɪr", "ʃ", "ʊ", "ʌ", "θ",
}


def check_phoneme_tags(lessons: list[LessonYAML]) -> list[str]:
    """Tag âm vị sai chính tả không làm gãy gì cả — nó chỉ lặng lẽ tắt phản hồi phát âm."""
    errors = []

    def check(tags: list[str], lesson_id: str, where: str) -> None:
        for tag in tags:
            if tag not in G2P_PHONEMES:
                errors.append(
                    f"{lesson_id}: {where} có âm vị '{tag}' không nằm trong bộ ký hiệu của g2p "
                    f"— sẽ không bao giờ khớp, phản hồi phát âm sẽ im lặng."
                )

    for lesson in lessons:
        for drill in lesson.speaking_drills:
            check(drill.focus_phonemes, lesson.id, "speaking_drill")
        for q in lesson.mini_quiz:
            check(q.focus_phonemes, lesson.id, "mini_quiz")
        for m in lesson.common_mistakes:
            check(m.detect.phoneme_missing, lesson.id, "common_mistake.detect.phoneme_missing")
            check(m.detect.phoneme_inserted, lesson.id, "common_mistake.detect.phoneme_inserted")
    return errors


def check_unlock_reachable(lessons: list[LessonYAML]) -> list[str]:
    """Bài B đòi bài A cao hơn mức A cần để hoàn thành → học viên kẹt ở khoảng giữa.

    Đạt đủ điểm xong bài A nhưng vẫn không mở được B, và không có gì nói cho họ biết
    còn thiếu bao nhiêu. Chỉ chặn tiên quyết 'hard' — 'soft' là gợi ý, không khoá đường đi.
    """
    done = {lesson.id: lesson.unlock_condition.mastery_threshold for lesson in lessons}
    errors = []
    for lesson in lessons:
        for pre in lesson.prerequisites:
            if pre.kind != "hard":
                continue
            need, have = pre.min_mastery, done.get(pre.lesson)
            if have is not None and need > have:
                errors.append(
                    f"{lesson.id}: đòi {pre.lesson} ≥{need} nhưng {pre.lesson} hoàn thành chỉ cần "
                    f"{have} — học viên đạt {have}..{need - 1} sẽ kẹt, không mở được bài nào."
                )
    return errors


def check_level_order(lessons: list[LessonYAML]) -> list[str]:
    """Bài tiên quyết không được nằm ở bậc cao hơn bài phụ thuộc.

    `cefr_target` là trục dọc của lộ trình (xem docs/khung-level.md). Một cạnh đi từ bậc
    cao xuống bậc thấp nghĩa là học viên phải thạo nội dung khó hơn để mở nội dung dễ hơn —
    lỗi này không làm gãy gì, nó chỉ lặng lẽ dựng một bức tường trước bài lẽ ra học sớm.
    """
    rank = {"pre_a1": 1, "a1": 2, "a2": 3, "b1": 4}
    level = {lesson.id: rank[lesson.cefr_target] for lesson in lessons}
    errors = []
    for lesson in lessons:
        for pre in lesson.prerequisites:
            src = level.get(pre.lesson)
            if src is not None and src > level[lesson.id]:
                errors.append(
                    f"{lesson.id} ({lesson.cefr_target}): tiên quyết '{pre.lesson}' ở bậc cao hơn "
                    f"— bài dễ bị khoá sau bài khó."
                )
    return errors


def main() -> int:
    # Thông báo lỗi viết bằng tiếng Việt, nhưng stdout mặc định của Windows là cp1252 —
    # không ép UTF-8 thì cổng chất lượng tự chết khi cần báo lỗi, đúng lúc cần nó nhất.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    lessons, errors = load_all()
    if lessons:
        errors += check_graph(lessons)
        errors += check_pedagogy(lessons)
        errors += check_units(lessons)
        errors += check_phoneme_tags(lessons)
        errors += check_unlock_reachable(lessons)
        errors += check_level_order(lessons)

    if errors:
        print(f"\n[X] {len(errors)} loi noi dung:\n")
        for e in errors:
            print(f"  - {e}")
        print()
        return 1

    by_phase: dict[str, int] = {}
    for lesson in lessons:
        by_phase[lesson.phase] = by_phase.get(lesson.phase, 0) + 1
    vocab = sum(len(lesson.vocabulary) for lesson in lessons)
    drills = sum(len(lesson.speaking_drills) for lesson in lessons)
    snippets = sum(1 for lesson in lessons if lesson.listening_snippet)

    print(f"\n[OK] {len(lessons)} bai hop le")
    for phase, n in sorted(by_phase.items()):
        print(f"   {phase:<12} {n}")
    print(f"   vocab {vocab} - drills {drills} - listening {snippets}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
