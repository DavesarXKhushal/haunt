"""Generates the static docs site from plain Python. No framework, no build step
beyond running this file; output is committed so Pages/Vercel serve plain HTML."""

from pathlib import Path

SITE = Path(__file__).parent
NAV = [
    ("Overview", [("index.html", "Introduction")]),
    ("Docs", [
        ("docs/quickstart.html", "Quickstart"),
        ("docs/cli-reference.html", "CLI reference"),
        ("docs/how-it-works.html", "How it works"),
    ]),
]


def shell(active_href: str, title: str, subtitle: str, body: str, depth: int = 0) -> str:
    prefix = "../" * depth
    sidebar = ""
    for group, links in NAV:
        sidebar += f'<div class="group"><div class="group-label">{group}</div>'
        for href, label in links:
            full = prefix + href
            cls = " active" if href == active_href else ""
            sidebar += f'<a class="link{cls}" href="{full}">{label}</a>'
        sidebar += "</div>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - haunt docs</title>
<link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
<div class="topbar">
  <a class="topbar-brand" href="{prefix}index.html"><span class="mark"></span>haunt</a>
  <div class="topbar-right">
    <a href="{prefix}docs/quickstart.html">Docs</a>
    <a class="gh" href="https://github.com/DavesarXKhushal/haunt">GitHub</a>
  </div>
</div>
<div class="layout">
  <nav class="sidebar">{sidebar}</nav>
  <main class="content">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    {body}
    <footer class="page-footer">github.com/DavesarXKhushal/haunt</footer>
  </main>
</div>
</body>
</html>
"""


PAGES = {}

PAGES["index.html"] = (0, "index.html", "Find the skills haunting your context window",
    "haunt audits a Claude Code skills directory against what actually happened, not against a guess.",
    """
<div class="hero">
<pre><span class="term-line-dim">$</span> haunt .claude/skills

haunt scanned 42 skill(s), matched against 310 real invocation(s)

  <span class="term-line-err">error  [broken-reference] deploy: ./scripts/push.sh does not resolve</span>
  <span class="term-line-warn">warn   [ghost-skill] onboarding-flow: never invoked in your session history</span>
  <span class="term-line-warn">warn   [ghost-skill] release-checklist: never invoked in your session history</span>

<span class="term-line-dim">4 of 42 installed skills have never been invoked.</span>
2 error(s), 2 warning(s).</pre>
</div>

<div class="btn-row">
  <a class="btn btn-primary" href="docs/quickstart.html">Get started</a>
  <a class="btn btn-ghost" href="https://github.com/DavesarXKhushal/haunt">View source</a>
</div>

<h2>The problem</h2>
<p>Every Claude Code skill linter checks structure: valid frontmatter, a description that isn't empty, a link that resolves. None of them check whether a skill has ever actually fired. A skill can read perfectly, pass every structural check, and still never once get invoked, while silently costing tokens whenever its description looks close enough to trigger consideration.</p>
<p>Nothing in the file itself tells you that. Your session transcripts do - haunt reads them directly.</p>

<h2>How it works</h2>
<div class="card-row">
  <div class="card">
    <h4>Static checks</h4>
    <p>Parses every SKILL.md's frontmatter and body: broken relative links, duplicate skill names, missing or thin descriptions.</p>
  </div>
  <div class="card">
    <h4>Real-usage cross-reference</h4>
    <p>Reads the JSONL transcripts Claude Code keeps in ~/.claude/projects, finds every Skill tool invocation, and matches it against what's installed.</p>
  </div>
</div>
<p>No LLM calls, no network access, no account required. Deterministic, offline, reads files already on disk.</p>

<h2>Verified against a real production agent</h2>
<p>We ran it against a live 379-skill agent built up over months of real daily use. Nobody had audited the whole tree end to end before.</p>
<div class="grid-cards">
  <div class="stat-card"><span class="num">379</span><span class="label">skills scanned</span></div>
  <div class="stat-card"><span class="num">42,639</span><span class="label">real invocations matched</span></div>
  <div class="stat-card"><span class="num">121</span><span class="label">never invoked once</span></div>
</div>
<p>One skill accounted for over 33,000 of those invocations by itself. The same run caught 10 broken file references and 24 descriptions too thin for an agent to route on.</p>
""")

PAGES["docs/quickstart.html"] = (1, "docs/quickstart.html", "Quickstart",
    "Install haunt and run your first audit in under a minute.",
    """
<h2>Install</h2>
<pre>pip install haunt</pre>
<p>Or run it with no install at all:</p>
<pre>uvx haunt /path/to/skills</pre>

<h2>Run it</h2>
<pre>haunt .claude/skills</pre>
<p>That scans every <code class="inline">SKILL.md</code> under the given directory, reads your Claude Code session transcripts from <code class="inline">~/.claude/projects</code>, and prints every finding: broken references, duplicate names, thin descriptions, and skills that have never been invoked.</p>

<div class="callout">
<strong>No telemetry under ~/.claude/projects?</strong> Some agent runtimes keep their own usage sidecar instead. Point haunt at it directly with <code class="inline">--usage-file</code>, documented on the <a href="cli-reference.html">CLI reference</a> page.
</div>

<h2>Read the output</h2>
<p>Each finding carries a level and a code:</p>
<ul>
  <li><strong>error</strong> - something is actually broken: a dead link, a duplicate name, a missing description, or an invocation of a skill that no longer exists.</li>
  <li><strong>warn</strong> - a ghost skill, or a description too thin for an agent to route on reliably. Worth a look, not necessarily a bug.</li>
</ul>

<h2>Wire it into CI</h2>
<pre>- name: Audit skills
  run: uvx haunt .claude/skills --fail-on-ghosts</pre>
<p><code class="inline">--fail-on-ghosts</code> makes the whole run exit non-zero the moment any installed skill has zero real invocations, so a dead skill gets caught in review instead of sitting in the tree for months.</p>

<div class="page-nav">
  <a href="cli-reference.html">Next: CLI reference →</a>
</div>
""")

PAGES["docs/cli-reference.html"] = (1, "docs/cli-reference.html", "CLI reference",
    "Every flag and every check haunt runs.",
    """
<h2>Usage</h2>
<pre>haunt [path] [options]</pre>
<p><code class="inline">path</code> defaults to the current directory.</p>

<h2>Flags</h2>
<table>
<tr><th>Flag</th><th>Effect</th></tr>
<tr><td><code class="inline">--projects &lt;dir&gt;</code></td><td>Claude Code transcripts directory (default: <code class="inline">~/.claude/projects</code>)</td></tr>
<tr><td><code class="inline">--usage-file &lt;file&gt;</code></td><td>a <code class="inline">.usage.json</code> sidecar (<code class="inline">{skill: {use_count}}</code>), for runtimes that keep one instead of transcripts</td></tr>
<tr><td><code class="inline">--json</code></td><td>machine-readable output, for scripts and CI</td></tr>
<tr><td><code class="inline">--fail-on-ghosts</code></td><td>non-zero exit when any skill has zero real invocations</td></tr>
</table>

<h2>Checks</h2>
<table>
<tr><th>Check</th><th>Source</th><th>What it finds</th></tr>
<tr><td><code class="inline">ghost-skill</code></td><td>transcripts</td><td>installed, zero invocations in your session history</td></tr>
<tr><td><code class="inline">hallucinated-invocation</code></td><td>transcripts</td><td>invoked by name, no matching SKILL.md exists</td></tr>
<tr><td><code class="inline">broken-reference</code></td><td>static</td><td>a relative link in a skill body that doesn't resolve</td></tr>
<tr><td><code class="inline">duplicate-name</code></td><td>static</td><td>two SKILL.md files resolve to the same skill name</td></tr>
<tr><td><code class="inline">missing-description</code></td><td>static</td><td>frontmatter has no description at all</td></tr>
<tr><td><code class="inline">thin-description</code></td><td>static</td><td>description too short for an agent to route on</td></tr>
</table>

<h2>Exit codes</h2>
<ul>
  <li><strong>0</strong> - no errors (ghosts allowed unless <code class="inline">--fail-on-ghosts</code> is set)</li>
  <li><strong>1</strong> - at least one error-level finding, or ghosts found with <code class="inline">--fail-on-ghosts</code></li>
  <li><strong>2</strong> - the given path doesn't exist</li>
</ul>

<div class="page-nav">
  <a href="quickstart.html">← Quickstart</a>
  <a href="how-it-works.html">Next: How it works →</a>
</div>
""")

PAGES["docs/how-it-works.html"] = (1, "docs/how-it-works.html", "How it works",
    "Two data sources, zero network calls, zero LLM calls.",
    """
<h2>Static analysis</h2>
<p>haunt walks the given directory for every <code class="inline">SKILL.md</code>, parses its YAML frontmatter and markdown body with plain regular expressions, and checks:</p>
<ul>
  <li>every relative link in the body resolves to a real file</li>
  <li>the frontmatter has a non-empty, non-trivial <code class="inline">description</code></li>
  <li>no two files resolve to the same skill <code class="inline">name</code></li>
</ul>

<h2>Real-usage cross-reference</h2>
<p>This is the part that's different from every other skill linter. Claude Code already writes a JSONL transcript of every session to <code class="inline">~/.claude/projects/&lt;project&gt;/&lt;session&gt;.jsonl</code>. Each line is a message; an assistant message that calls a skill contains a <code class="inline">tool_use</code> block with <code class="inline">name: "Skill"</code> and an <code class="inline">input.skill</code> field naming it.</p>
<p>haunt reads every transcript under that directory, counts how many times each skill name was actually invoked, and cross-references that count against what's installed:</p>
<ul>
  <li>a skill with <strong>zero</strong> invocations is a ghost - loaded into context on relevant turns, never used</li>
  <li>an invocation of a name with <strong>no matching SKILL.md</strong> is a hallucinated invocation - the agent called something that used to exist, or never did</li>
</ul>

<h2>The usage.json fallback</h2>
<p>Not every agent runtime writes Claude Code's own transcript format. Some keep a simpler sidecar file instead - a flat <code class="inline">{skill_name: {"use_count": N}}</code> map. haunt reads one of these automatically if it finds <code class="inline">.usage.json</code> next to the scanned directory, or you can point it at one explicitly with <code class="inline">--usage-file</code>.</p>

<h2>Why no LLM calls</h2>
<p>Every check here is a deterministic fact about files that already exist on disk: a link resolves or it doesn't, a name is duplicated or it isn't, a skill was invoked N times or zero times. There is nothing here that benefits from a model's judgment, and adding one would only add cost, latency, and a source of non-determinism to a tool whose entire value is that the same input always produces the same answer.</p>

<div class="page-nav">
  <a href="cli-reference.html">← CLI reference</a>
</div>
""")


def main():
    for href, (depth, active, title, subtitle, body) in PAGES.items():
        out = SITE / href
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(shell(active, title, subtitle, body, depth=depth), encoding="utf-8")
        print("wrote", out)


if __name__ == "__main__":
    main()
