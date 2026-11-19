---
name: haunt
description: Use when auditing a Claude Code skills directory for unused ("ghost") skills, broken file references, duplicate names, or thin descriptions before shipping or reviewing a skill library. Runs the haunt CLI and summarizes findings.
---

# haunt

Audits an Agent Skills directory (`SKILL.md` files) against real usage.
Cross-references installed skills with session transcripts to find which
ones have never been invoked, plus static checks for broken references,
duplicate names, and thin descriptions.

## When to use this

- Before shipping a skill library to a team, to catch dead weight.
- When a skills directory has grown past a dozen or so entries and nobody
  has audited it end to end.
- When a skill's description seems right but the agent never seems to
  pick it -- this checks whether it has ever fired at all.

## How to run it

```
uvx haunt <path-to-skills-dir> --json
```

Read the JSON output, summarize for the user:

- total skills scanned and total real invocations matched
- every `error`-level finding (broken references, duplicate names,
  missing descriptions, hallucinated invocations) -- these need a fix
- the ghost-skill list -- these need a decision: fix the description,
  merge it into something that does fire, or archive it

Do not silently delete or archive anything. Report the findings and let
the user decide; `haunt` is read-only by design.
