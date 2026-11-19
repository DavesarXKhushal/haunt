from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def count_from_usage_sidecar(usage_file: Path) -> Counter:
    """Read a ``.usage.json`` sidecar (``{skill_name: {"use_count": N, ...}}``), the
    convention some agent runtimes keep instead of raw Skill-tool transcripts."""
    counts: Counter = Counter()
    if not usage_file.exists():
        return counts
    try:
        data = json.loads(usage_file.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return counts
    if not isinstance(data, dict):
        return counts
    for name, record in data.items():
        if isinstance(record, dict):
            count = record.get("use_count", 0)
            if isinstance(count, int) and count > 0:
                counts[name] = count
    return counts


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _skill_calls(record: dict):
    content = record.get("message", {}).get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
            skill = block.get("input", {}).get("skill")
            if skill:
                yield skill


def count_invocations(projects_dir: Path) -> Counter:
    counts: Counter = Counter()
    if not projects_dir.exists():
        return counts
    for jsonl in projects_dir.rglob("*.jsonl"):
        try:
            for record in _iter_jsonl(jsonl):
                counts.update(_skill_calls(record))
        except OSError:
            continue
    return counts


def default_projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"
