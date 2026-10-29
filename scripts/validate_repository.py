#!/usr/bin/env python3
"""Validate the Pixel Art Game Studio repository itself.

Checks: required files, SKILL.md and agent frontmatter against documented Claude Code fields,
the eight agents and their tool lists, Python syntax, internal Markdown links, no unverifiable
badges, a sane .gitignore, and (unless --skip-translations) the translation gate.

Usage: python scripts/validate_repository.py [--root DIR] [--skip-translations]
Exit codes: 0 pass, 1 problems found.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_translations  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = ".claude/skills/pixel-art-game-studio"
AGENTS = ["pixel-artist", "npc-story-engineer", "world-builder-level-design", "world-builder-environmental-content",
          "ui-engineer", "gameplay-engineer", "qa-tester", "bug-fixer"]
REQUIRED_FILES = [
    f"{SKILL}/SKILL.md",
    *[f"{SKILL}/workflows/{n}.md" for n in ("create-game", "extend-game", "test-and-fix", "generate-assets", "release-check")],
    *[f"{SKILL}/references/{n}.md" for n in ("architecture", "art-direction", "game-systems", "agent-coordination",
                                              "quality-standards", "troubleshooting")],
    f"{SKILL}/scripts/validate_game_project.py", f"{SKILL}/scripts/generate_sample_asset.py",
    *[f".claude/agents/{a}.md" for a in AGENTS],
    "scripts/install.py", "scripts/validate_repository.py", "scripts/check_translations.py",
    "README.md", "LICENSE", ".gitignore", "pyproject.toml", "docs/i18n/manifest.json",
    *[f"docs/{n}.md" for n in ("ARCHITECTURE", "INSTALLATION", "AGENTS", "WORKFLOWS", "TESTING", "TROUBLESHOOTING",
                               "CONTRIBUTING", "CODE_OF_CONDUCT")],
    *[f"examples/{n}.md" for n in ("example-game-idea", "example-game-design", "example-workflow")],
]
# Documented Claude Code built-in tool names that a subagent may reasonably be granted.
KNOWN_TOOLS = {"Read", "Write", "Edit", "Glob", "Grep", "Bash", "PowerShell", "WebFetch", "WebSearch", "NotebookEdit"}
MODELS = {"inherit", "sonnet", "opus", "haiku", "fable"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", "build", "dist"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def frontmatter(text: str) -> dict[str, str] | None:
    """Parse simple `key: value` YAML frontmatter. Returns None if the file does not start with ---."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return None  # no closing ---


def walk(root: Path, suffix: str):
    for p in sorted(root.rglob(f"*{suffix}")):
        if not (set(p.relative_to(root).parts) & SKIP_DIRS):
            yield p


def check_skill(root: Path) -> list[str]:
    path = root / SKILL / "SKILL.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        return ["SKILL.md: frontmatter must start on line 1 with --- and be closed with ---"]
    problems = []
    if fm.get("name") != "pixel-art-game-studio":
        problems.append("SKILL.md: name must be 'pixel-art-game-studio' (matches its directory)")
    desc = fm.get("description", "")
    if not desc:
        problems.append("SKILL.md: description is required for automatic discovery")
    if len(desc) + len(fm.get("when_to_use", "")) > 1536:
        problems.append("SKILL.md: description + when_to_use exceed the 1,536-character listing limit")
    if len(text.splitlines()) > 500:
        problems.append("SKILL.md: longer than the recommended 500 lines; move detail to references/")
    return problems


def check_agents(root: Path) -> list[str]:
    problems = []
    agent_dir = root / ".claude" / "agents"
    present = sorted(p.stem for p in agent_dir.glob("*.md")) if agent_dir.is_dir() else []
    if sorted(AGENTS) != present:
        problems.append(f".claude/agents must contain exactly {sorted(AGENTS)}, found {present}")
    for name in AGENTS:
        path = agent_dir / f"{name}.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        tag = f"agents/{name}.md"
        if fm is None:
            problems.append(f"{tag}: frontmatter must start on line 1 with --- and be closed")
            continue
        n = fm.get("name", "")
        if n != name:
            problems.append(f"{tag}: name '{n}' should equal the file name '{name}'")
        if not n or ":" in n or n.startswith("-") or len(n) > 256:
            problems.append(f"{tag}: invalid name (required, no ':', not starting with '-', max 256)")
        if not fm.get("description"):
            problems.append(f"{tag}: description is required")
        tools = [t.strip() for t in fm.get("tools", "").split(",") if t.strip()]
        if not tools:
            problems.append(f"{tag}: tools must be listed explicitly (no unrestricted default)")
        for t in tools:
            if t == "Agent" or t.startswith("Agent("):
                problems.append(f"{tag}: specialists must not spawn agents; the Game Director coordinates")
            elif t not in KNOWN_TOOLS:
                problems.append(f"{tag}: unknown tool '{t}'")
        if fm.get("model", "inherit") not in MODELS and not fm.get("model", "").startswith("claude-"):
            problems.append(f"{tag}: unsupported model '{fm.get('model')}'")
        if "permissionMode" in fm and fm["permissionMode"] == "bypassPermissions":
            problems.append(f"{tag}: bypassPermissions is not allowed")
        body = text.split("---", 2)[2] if text.count("---") >= 2 else ""
        if len(body.strip()) < 500:
            problems.append(f"{tag}: system prompt body is too short to define the role")
    return problems


def check_python(root: Path) -> list[str]:
    problems = []
    for p in walk(root, ".py"):
        try:
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        except SyntaxError as exc:
            problems.append(f"{p.relative_to(root)}: syntax error line {exc.lineno}: {exc.msg}")
    return problems


def check_links(root: Path) -> list[str]:
    problems = []
    for md in walk(root, ".md"):
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            resolved = (md.parent / rel).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                problems.append(f"{md.relative_to(root)}: link leaves the repository: {target}")
                continue
            if not resolved.exists():
                problems.append(f"{md.relative_to(root)}: broken link: {target}")
    return problems


def check_presentation(root: Path) -> list[str]:
    problems = []
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        if re.search(r"shields\.io|badgen\.net|badge\.svg", text):
            problems.append("README.md: badges are not allowed until the services they describe are configured")
        for a in AGENTS:
            if a not in text:
                problems.append(f"README.md: agent '{a}' is not mentioned")
    agents_doc = root / "docs" / "AGENTS.md"
    if agents_doc.is_file():
        text = agents_doc.read_text(encoding="utf-8")
        for a in AGENTS:
            if a not in text:
                problems.append(f"docs/AGENTS.md: agent '{a}' is not documented")
    gi = root / ".gitignore"
    if gi.is_file():
        bad = {".claude", ".claude/", "*.md", "*.py", "docs", "docs/", "scripts/", "tests/", "*.json"}
        for line in gi.read_text(encoding="utf-8").splitlines():
            if line.strip() in bad:
                problems.append(f".gitignore: '{line.strip()}' would exclude required source files")
    return problems


def validate(root: Path = REPO_ROOT, translations: bool = True) -> list[str]:
    problems = [f"missing required file: {f}" for f in REQUIRED_FILES if not (root / f).is_file()]
    problems += check_skill(root) + check_agents(root) + check_python(root) + check_links(root) + check_presentation(root)
    if translations:
        problems += [f"translations: {p}" for p in check_translations.check(root)]
    return problems


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # Windows consoles may not encode every script
    ap = argparse.ArgumentParser(description="Validate the Pixel Art Game Studio repository.")
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--skip-translations", action="store_true")
    args = ap.parse_args(argv)
    problems = validate(args.root.resolve(), not args.skip_translations)
    for p in problems:
        print(f"FAIL {p}")
    print(f"repository: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
