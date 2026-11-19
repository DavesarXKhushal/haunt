from __future__ import annotations

import json

from haunt.report import build_report


def _write_skill(root, name, description="A real, long enough description for routing.", body=""):
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n", encoding="utf-8"
    )
    return skill_dir


def test_clean_skill_has_no_errors(tmp_path):
    _write_skill(tmp_path, "deploy")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert report.errors == []


def test_ghost_skill_flagged_without_usage(tmp_path):
    _write_skill(tmp_path, "deploy")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert [s.name for s in report.ghosts] == ["deploy"]


def test_usage_sidecar_clears_ghost_flag(tmp_path):
    _write_skill(tmp_path, "deploy")
    (tmp_path / ".usage.json").write_text(json.dumps({"deploy": {"use_count": 5}}), encoding="utf-8")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert report.ghosts == []


def test_broken_reference_detected(tmp_path):
    _write_skill(tmp_path, "deploy", body="See [the script](./scripts/push.sh).")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    codes = [f.code for f in report.findings]
    assert "broken-reference" in codes


def test_valid_reference_not_flagged(tmp_path):
    skill_dir = _write_skill(tmp_path, "deploy", body="See [the script](./scripts/push.sh).")
    (skill_dir / "scripts").mkdir()
    (skill_dir / "scripts" / "push.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert "broken-reference" not in [f.code for f in report.findings]


def test_missing_description_is_an_error(tmp_path):
    skill_dir = tmp_path / "bare"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: bare\n---\n\nbody\n", encoding="utf-8")
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert "missing-description" in [f.code for f in report.findings]


def test_duplicate_name_detected(tmp_path):
    _write_skill(tmp_path, "deploy")
    other = tmp_path / "legacy" / "deploy"
    other.mkdir(parents=True)
    (other / "SKILL.md").write_text(
        "---\nname: deploy\ndescription: A second definition of the same skill name.\n---\n", encoding="utf-8"
    )
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert "duplicate-name" in [f.code for f in report.findings]


def test_hallucinated_invocation_detected(tmp_path):
    (tmp_path / ".usage.json").write_text(
        json.dumps({"ghost-tool-that-was-deleted": {"use_count": 3}}), encoding="utf-8"
    )
    report = build_report(tmp_path, projects_dir=tmp_path / "nope")
    assert "hallucinated-invocation" in [f.code for f in report.findings]
