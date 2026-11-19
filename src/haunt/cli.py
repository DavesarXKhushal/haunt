from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .report import build_report

RED, YELLOW, DIM, BOLD, RESET = "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"


def _color(enabled: bool, code: str, text: str) -> str:
    return f"{code}{text}{RESET}" if enabled else text


def _print_text(report, color: bool) -> None:
    print(f"{_color(color, BOLD, 'haunt')} scanned {len(report.skills)} skill(s), "
          f"matched against {sum(report.invocations.values())} real invocation(s)\n")
    for f in report.errors:
        tag = _color(color, RED, "error")
        print(f"  {tag}  [{f.code}] {f.skill}: {f.message}")
    for f in report.warnings:
        tag = _color(color, YELLOW, "warn ")
        print(f"  {tag}  [{f.code}] {f.skill}: {f.message}")
    ghosts = report.ghosts
    print(f"\n{len(ghosts)} of {len(report.skills)} installed skills have never been invoked:")
    for s in ghosts[:25]:
        print(f"  {_color(color, DIM, '-')} {s.name}")
    if len(ghosts) > 25:
        print(f"  {_color(color, DIM, f'... and {len(ghosts) - 25} more')}")
    print(f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s).")


def _print_json(report) -> None:
    print(json.dumps({
        "skill_count": len(report.skills),
        "invocation_count": sum(report.invocations.values()),
        "ghosts": [s.name for s in report.ghosts],
        "findings": [f.__dict__ for f in report.findings],
    }, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="haunt", description="Find the skills haunting your context window.")
    parser.add_argument("path", nargs="?", default=".", help="skills directory to scan (default: .)")
    parser.add_argument("--projects", type=Path, default=None, help="Claude Code projects dir (default: ~/.claude/projects)")
    parser.add_argument("--usage-file", type=Path, default=None, help="usage.json sidecar (default: <path>/.usage.json if present)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--fail-on-ghosts", action="store_true", help="exit 1 if any ghost skill is found")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"haunt: {root} does not exist", file=sys.stderr)
        return 2

    report = build_report(root, args.projects, args.usage_file)
    if args.json:
        _print_json(report)
    else:
        _print_text(report, color=sys.stdout.isatty())

    if report.errors:
        return 1
    if args.fail_on_ghosts and report.ghosts:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
