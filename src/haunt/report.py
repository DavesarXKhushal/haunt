from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .scanner import Skill, discover_skills
from .transcripts import count_from_usage_sidecar, count_invocations, default_projects_dir


@dataclass
class Finding:
    level: str  # "error" | "warn" | "info"
    code: str
    skill: str
    message: str


@dataclass
class Report:
    skills: list[Skill]
    invocations: Counter
    findings: list[Finding] = field(default_factory=list)

    @property
    def ghosts(self) -> list[Skill]:
        return [s for s in self.skills if self.invocations.get(s.name, 0) == 0]

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warn"]


def _check_duplicates(skills: list[Skill]) -> list[Finding]:
    seen: dict[str, Path] = {}
    findings = []
    for skill in skills:
        if skill.name in seen and seen[skill.name] != skill.path:
            findings.append(Finding("error", "duplicate-name", skill.name,
                                     f"also defined at {seen[skill.name]}"))
        seen.setdefault(skill.name, skill.path)
    return findings


def _check_broken_links(skills: list[Skill]) -> list[Finding]:
    return [Finding("error", "broken-reference", s.name, f"{link} does not resolve")
            for s in skills for link in s.broken_links]


def _check_description(skills: list[Skill]) -> list[Finding]:
    findings = []
    for s in skills:
        if not s.description:
            findings.append(Finding("error", "missing-description", s.name, "no description in frontmatter"))
        elif len(s.description) < 20:
            findings.append(Finding("warn", "thin-description", s.name,
                                     "description is too short for an agent to route on"))
    return findings


def _check_ghosts(skills: list[Skill], invocations: Counter) -> list[Finding]:
    return [Finding("warn", "ghost-skill", s.name,
                     "installed, loaded into context, never invoked in your session history")
            for s in skills if invocations.get(s.name, 0) == 0]


def _check_hallucinated(skills: list[Skill], invocations: Counter) -> list[Finding]:
    installed = {s.name for s in skills}
    return [Finding("error", "hallucinated-invocation", name,
                     f"invoked {count}x but no SKILL.md with this name is installed")
            for name, count in invocations.items() if name not in installed]


def build_report(root: Path, projects_dir: Path | None = None, usage_file: Path | None = None) -> Report:
    skills = discover_skills(root)
    invocations = count_invocations(projects_dir or default_projects_dir())
    sidecar = usage_file or (root / ".usage.json")
    invocations.update(count_from_usage_sidecar(sidecar))
    findings = [
        *_check_duplicates(skills),
        *_check_broken_links(skills),
        *_check_description(skills),
        *_check_ghosts(skills, invocations),
        *_check_hallucinated(skills, invocations),
    ]
    return Report(skills=skills, invocations=invocations, findings=findings)
