from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    body: str
    broken_links: list[str] = field(default_factory=list)


def _parse_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return "", ""
    block = match.group(1)
    name = NAME_RE.search(block)
    desc = DESC_RE.search(block)
    return (name.group(1).strip("\"'") if name else ""), (desc.group(1).strip("\"'") if desc else "")


def _resolve_link(skill_dir: Path, target: str) -> bool:
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return True
    clean = target.split("#", 1)[0]
    return (skill_dir / clean).exists()


def load_skill(skill_md: Path) -> Skill:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    name, description = _parse_frontmatter(text)
    skill_dir = skill_md.parent
    body = FRONTMATTER_RE.sub("", text, count=1)
    broken = [m for m in LINK_RE.findall(body) if not _resolve_link(skill_dir, m)]
    return Skill(name=name or skill_dir.name, description=description, path=skill_md, body=body, broken_links=broken)


def discover_skills(root: Path) -> list[Skill]:
    skip = {".git", "node_modules", ".archive", "__pycache__"}
    skills = []
    for skill_md in root.rglob("SKILL.md"):
        if skip & set(skill_md.parts):
            continue
        skills.append(load_skill(skill_md))
    return sorted(skills, key=lambda s: s.name)
