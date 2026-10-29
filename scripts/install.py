#!/usr/bin/env python3
"""Install, update, or remove Pixel Art Game Studio (skill + 8 subagents) safely.

Destinations follow the documented Claude Code locations:
  --scope project --project-dir DIR   ->  DIR/.claude/skills/... and DIR/.claude/agents/...
  --scope user                        ->  ~/.claude/skills/...   and ~/.claude/agents/...
  --dest CLAUDE_DIR                   ->  CLAUDE_DIR/skills/...  and CLAUDE_DIR/agents/...

Safety rules:
  - Only the skill directory and the eight agent files are copied; nothing else from the repository.
  - Existing files that this installer did not create are never replaced (reported as conflicts).
  - Files it did create are replaced only with --update, after a backup copy is made.
  - --uninstall removes only files recorded in the install manifest whose content is unchanged.
  - --dry-run prints the plan and changes nothing.

Exit codes: 0 success, 1 error, 2 conflicts (nothing was changed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

SKILL_NAME = "pixel-art-game-studio"
AGENTS = [
    "pixel-artist", "npc-story-engineer", "world-builder-level-design",
    "world-builder-environmental-content", "ui-engineer", "gameplay-engineer", "qa-tester", "bug-fixer",
]
MANIFEST = f"skills/{SKILL_NAME}/.install-manifest.json"
BACKUP_DIR = ".pixel-art-game-studio-backups"
REPO_ROOT = Path(__file__).resolve().parent.parent
IGNORED_PARTS = {"__pycache__", ".pytest_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


class InstallError(Exception):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(repo: Path = REPO_ROOT) -> dict[str, Path]:
    """Map destination-relative paths (posix) to source files. Raises if the source is incomplete."""
    claude = repo / ".claude"
    skill = claude / "skills" / SKILL_NAME
    if not (skill / "SKILL.md").is_file():
        raise InstallError(f"source skill not found at {skill}")
    files = {}
    for p in sorted(skill.rglob("*")):
        if p.is_file() and not (set(p.relative_to(skill).parts) & IGNORED_PARTS) and p.suffix not in IGNORED_SUFFIXES:
            if p.name == Path(MANIFEST).name:
                continue
            files[p.relative_to(claude).as_posix()] = p
    for name in AGENTS:
        p = claude / "agents" / f"{name}.md"
        if not p.is_file():
            raise InstallError(f"source agent definition missing: {p}")
        files[f"agents/{name}.md"] = p
    return files


def resolve_claude_dir(scope: str | None, project_dir: Path | None, dest: Path | None, home: Path | None = None) -> Path:
    if dest is not None:
        target = dest.expanduser()
    elif scope == "user":
        target = (home or Path.home()) / ".claude"
    elif scope == "project":
        if project_dir is None:
            raise InstallError("--scope project requires --project-dir")
        project_dir = project_dir.expanduser()
        if not project_dir.is_dir():
            raise InstallError(f"project directory does not exist: {project_dir}")
        target = project_dir / ".claude"
    else:
        raise InstallError("choose --scope project, --scope user, or --dest")
    target = target.resolve()
    if target.exists() and not target.is_dir():
        raise InstallError(f"destination exists and is not a directory: {target}")
    if not target.parent.is_dir():
        raise InstallError(f"parent directory does not exist: {target.parent}")
    if target == (REPO_ROOT / ".claude").resolve():
        raise InstallError("destination is this repository's own .claude directory; nothing to install")
    return target


def read_manifest(claude_dir: Path) -> dict[str, str]:
    path = claude_dir / MANIFEST
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        files = data["files"]
        if not isinstance(files, dict):
            raise TypeError
        return {str(k): str(v) for k, v in files.items()}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise InstallError(f"install manifest {path} is unreadable ({exc}); fix or remove it manually") from exc


def plan_install(sources: dict[str, Path], claude_dir: Path, update: bool) -> list[tuple[str, str]]:
    """Return [(action, rel)] where action is create, unchanged, update, update-modified, conflict, needs-update."""
    manifest = read_manifest(claude_dir)
    plan = []
    for rel, src in sources.items():
        dst = claude_dir / rel
        if dst.exists() and not dst.is_file():
            plan.append(("conflict", rel))
        elif not dst.exists():
            plan.append(("create", rel))
        elif sha256(dst) == sha256(src):
            plan.append(("unchanged", rel))
        elif rel not in manifest:
            plan.append(("conflict", rel))
        elif not update:
            plan.append(("needs-update", rel))
        else:
            plan.append(("update" if sha256(dst) == manifest[rel] else "update-modified", rel))
    for rel in sorted(set(manifest) - set(sources)):
        plan.append(("stale", rel))
    return plan


def apply_install(plan, sources, claude_dir: Path, out=print) -> Path | None:
    backup_root = None
    manifest = read_manifest(claude_dir)
    for action, rel in plan:
        dst = claude_dir / rel
        if action in ("update", "update-modified"):
            if backup_root is None:
                backup_root = claude_dir / BACKUP_DIR / time.strftime("%Y%m%d-%H%M%S")
            bk = backup_root / rel
            bk.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, bk)
        if action in ("create", "update", "update-modified"):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sources[rel], dst)
        if action in ("create", "update", "update-modified", "unchanged"):
            manifest[rel] = sha256(dst)
    mpath = claude_dir / MANIFEST
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps({"tool": SKILL_NAME, "files": dict(sorted(manifest.items()))}, indent=2) + "\n",
                     encoding="utf-8")
    return backup_root


def plan_uninstall(claude_dir: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(claude_dir)
    if not manifest:
        raise InstallError(f"no {SKILL_NAME} install manifest in {claude_dir}; nothing to remove")
    plan = []
    for rel, digest in sorted(manifest.items()):
        p = claude_dir / rel
        if not p.is_file():
            plan.append(("missing", rel))
        elif sha256(p) == digest:
            plan.append(("remove", rel))
        else:
            plan.append(("keep-modified", rel))
    return plan


def apply_uninstall(plan, claude_dir: Path) -> None:
    for action, rel in plan:
        if action == "remove":
            (claude_dir / rel).unlink()
    (claude_dir / MANIFEST).unlink()
    skill_dir = claude_dir / "skills" / SKILL_NAME
    # Remove only directories that became empty; anything the user added stays.
    for d in sorted((p for p in skill_dir.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    if skill_dir.is_dir() and not any(skill_dir.iterdir()):
        skill_dir.rmdir()


LABELS = {
    "create": "create", "unchanged": "unchanged", "update": "update (backup first)",
    "update-modified": "update, LOCAL EDITS backed up", "conflict": "CONFLICT (not installed by this tool)",
    "needs-update": "differs (rerun with --update)", "stale": "no longer shipped (left in place)",
    "remove": "remove", "keep-modified": "keep (modified locally)", "missing": "already missing",
}


def main(argv=None, home: Path | None = None, out=print) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # Windows consoles may not encode every script
    ap = argparse.ArgumentParser(description="Install Pixel Art Game Studio into a Claude Code configuration.")
    ap.add_argument("--scope", choices=["project", "user"])
    ap.add_argument("--project-dir", type=Path, help="project root for --scope project")
    ap.add_argument("--dest", type=Path, help="explicit .claude directory (overrides --scope)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--update", action="store_true", help="replace previously installed files (with backup)")
    mode.add_argument("--uninstall", action="store_true", help="remove unmodified installed files")
    ap.add_argument("--dry-run", action="store_true", help="show the plan without changing anything")
    args = ap.parse_args(argv)

    try:
        claude_dir = resolve_claude_dir(args.scope, args.project_dir, args.dest, home)
        out(f"Target: {claude_dir}{'  (dry run)' if args.dry_run else ''}")
        if args.uninstall:
            plan = plan_uninstall(claude_dir)
        else:
            sources = source_files()
            plan = plan_install(sources, claude_dir, args.update)
        for action, rel in plan:
            out(f"  {LABELS[action]:38} {rel}")
        blocked = [rel for action, rel in plan if action in ("conflict", "needs-update")]
        if blocked:
            out(f"{len(blocked)} file(s) block installation; nothing was changed.")
            if any(a == "conflict" for a, _ in plan):
                out("Conflicting files were not created by this installer. Move or rename them, then rerun.")
            return 2
        if args.dry_run:
            out("Dry run complete; no files were changed.")
            return 0
        if args.uninstall:
            apply_uninstall(plan, claude_dir)
            kept = sum(1 for a, _ in plan if a == "keep-modified")
            out(f"Uninstalled.{f' {kept} locally modified file(s) kept.' if kept else ''}")
        else:
            backup = apply_install(plan, sources, claude_dir)
            if backup:
                out(f"Backups of replaced files: {backup}")
            out("Installed. Restart Claude Code if the agents directory did not exist when the session started.")
        return 0
    except InstallError as exc:
        out(f"error: {exc}")
        return 1
    except OSError as exc:
        out(f"error: file operation failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
