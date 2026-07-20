"""Cốt truyện xuyên suốt: dàn nhân vật và chương theo phase.

Nội dung tĩnh, không có state của người học, nên đọc thẳng từ YAML và cache — không cần bảng
DB và migration cho một màn hình giới thiệu.
"""
from functools import lru_cache
from pathlib import Path

import yaml

STORY_FILE = Path("seeds/story/chapters.yaml")


@lru_cache(maxsize=1)
def _story() -> dict:
    if not STORY_FILE.exists():
        return {}
    return yaml.safe_load(STORY_FILE.read_text(encoding="utf-8")) or {}


def chapter_for_phase(phase: str) -> dict | None:
    """Chương của phase, kèm hồ sơ những nhân vật lần đầu xuất hiện."""
    story = _story()
    chapter = next((c for c in story.get("chapters", []) if c.get("phase") == phase), None)
    if chapter is None:
        return None
    by_name = {c["name"]: c for c in story.get("cast", [])}
    return {
        **chapter,
        "setting_vi": story.get("setting_vi", ""),
        "cast": [by_name[n] for n in chapter.get("new_faces", []) if n in by_name],
    }


def cast() -> list[dict]:
    return _story().get("cast", [])
