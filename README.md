# haunt

**Find the skills haunting your context window.**

`haunt` audits a Claude Code / Agent Skills directory against what actually
happened, not against a guess. It cross-references every installed
`SKILL.md` against your own session transcripts and tells you which skills
are loaded into context on every relevant turn and never once invoked,
which invocations reference a skill that no longer exists, and which
references inside your skills are already broken.

Every other skill linter checks structure: valid frontmatter, a
description that isn't empty, a link that resolves. `haunt` does that too,
but its real claim is different — it is the only one that checks your
skills against *what actually ran*, using the transcripts Claude Code
already writes to `~/.claude/projects`.

## Why this exists

We ran it against the Hermes agent that runs LocalHost — 379 installed skills,
built up over months of real daily use.

```
haunt scanned 379 skill(s), matched against 42,639 real invocation(s)

121 of 379 installed skills have never been invoked.
29 error(s), 137 warning(s).
```

One skill, `meeting-intelligence`, accounts for over 33,000 of those
invocations by itself. A hundred and twenty-one others — nearly a third of
everything installed — have a polished `SKILL.md`, a plausible
description, a reasonable name, and have never once fired. The run also
caught ten broken file references and twenty-four descriptions too thin
for an agent to reliably route on, in a tree nobody had audited end to
end before. Every one of those skills still loads into the model's
context on the turns where its description looks relevant, burning
tokens for a skill nobody is using. Nothing in the file itself tells you
that. The transcripts do.

## Install

```
pip install haunt
```

or run it without installing:

```
uvx haunt /path/to/skills
```

## Use

```
haunt .claude/skills
```

```
haunt scanned 42 skill(s), matched against 310 real invocation(s)

  error  [broken-reference] deploy: ./scripts/push.sh does not resolve
  error  [duplicate-name] review: also defined at skills/legacy/review/SKILL.md
  warn   [thin-description] notes: description is too short for an agent to route on
  warn   [ghost-skill] onboarding-flow: installed, loaded into context, never invoked in your session history

4 of 42 installed skills have never been invoked.
  - onboarding-flow
  - release-checklist
  - db-migration-helper
  - legacy-review

2 error(s), 2 warning(s).
```

Flags:

| Flag | Effect |
|---|---|
| `--projects <dir>` | Claude Code transcripts directory (default: `~/.claude/projects`) |
| `--usage-file <file>` | a `.usage.json` sidecar (`{skill: {use_count}}`), if your runtime keeps one (default: `<path>/.usage.json`) |
| `--json` | machine-readable output for CI |
| `--fail-on-ghosts` | non-zero exit when any skill has zero real invocations |

## What it checks

| Check | Source | What it finds |
|---|---|---|
| `ghost-skill` | transcripts | installed, zero invocations in your session history |
| `hallucinated-invocation` | transcripts | invoked by name, but no matching `SKILL.md` exists |
| `broken-reference` | static | a relative link in a skill body that doesn't resolve |
| `duplicate-name` | static | two `SKILL.md` files resolve to the same skill name |
| `missing-description` / `thin-description` | static | frontmatter too thin for an agent to route on |

## How it works

No LLM calls, no network access, no account. `haunt` reads your `SKILL.md`
files directly and reads the JSONL transcripts Claude Code already keeps
locally, looking for `tool_use` blocks where `name` is `"Skill"`. Everything
runs offline, deterministically, against files already on your disk.

## CI

```yaml
- name: Audit skills
  run: uvx haunt .claude/skills --fail-on-ghosts
```

## License

MIT
