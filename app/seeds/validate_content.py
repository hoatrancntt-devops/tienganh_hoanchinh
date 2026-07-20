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


def main() -> int:
    lessons, errors = load_all()
    if lessons:
        errors += check_graph(lessons)
        errors += check_pedagogy(lessons)
        errors += check_units(lessons)

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
