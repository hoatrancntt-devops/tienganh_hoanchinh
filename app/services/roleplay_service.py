"""Roleplay đóng vai — kịch bản phân nhánh, đọc từ YAML, KHÔNG cần LLM.

Stateless: nội dung tĩnh từ seeds/roleplay/*.yaml, không lưu DB. Audio partner sinh lúc seed.
"""
from pathlib import Path

import yaml

RP_DIR = Path("seeds/roleplay")
_cache: dict[str, dict] = {}


def _load_all() -> dict[str, dict]:
    if _cache:
        return _cache
    for path in sorted(RP_DIR.glob("RP-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        _cache[data["id"]] = data
    return _cache


def list_scenarios() -> list[dict]:
    return [
        {"id": d["id"], "title_vi": d["title_vi"], "context_vi": d["context_vi"],
         "topic": d.get("topic", "core"), "partner": d.get("partner", "")}
        for d in _load_all().values()
    ]


def get_scenario(rid: str) -> dict | None:
    d = _load_all().get(rid)
    if not d:
        return None
    # Gắn đường dẫn audio cho câu của "partner" mỗi node (sinh ở generate_audio).
    nodes = {}
    for nid, node in d["nodes"].items():
        nodes[nid] = {**node, "audio": f"/media/roleplay/{rid}_{nid}.wav"}
    return {**d, "nodes": nodes}


def invalidate() -> None:
    _cache.clear()
