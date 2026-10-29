# Installation

[Back to README](../README.md)

## Prerequisites

- [Claude Code](https://code.claude.com/docs/) (checked with 2.1.312).
- Python 3.9 or newer. No packages are needed. On some systems the command is `python3` or `py -3`.
- For real games: the engine you want (Godot 4, .NET SDK for MonoGame, Node.js for web, ...). The skill
  checks what is installed and asks before installing anything.

Get the repository by cloning your fork or copy (there is no official hosted URL configured in this
repository; replace the placeholder with yours):

```bash
git clone <your-fork-or-copy-url> pixel-art-game-studio
```

## Where Claude Code looks

| Scope | Skill | Agents |
| --- | --- | --- |
| Project | `<project>/.claude/skills/pixel-art-game-studio/SKILL.md` | `<project>/.claude/agents/*.md` |
| User (all projects) | `~/.claude/skills/pixel-art-game-studio/SKILL.md` | `~/.claude/agents/*.md` |

Project definitions take priority over user definitions with the same name.

## Three ways to use it

1. **Inside this repository.** Run `claude` in the repository root. The skill and agents are already in
   `.claude/`. Create games in a subfolder (for example `games/my-game/`) so they stay separate from the
   toolkit files.
2. **Project install** with the installer (below).
3. **User install** with the installer (below), available in every project.

## Installer

```bash
# Preview, then install into a game project
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game

# Preview, then install for your user account (~/.claude)
python scripts/install.py --scope user --dry-run
python scripts/install.py --scope user

# Any .claude directory explicitly
python scripts/install.py --dest /path/to/.claude --dry-run
```

What it does:

- Copies only `.claude/skills/pixel-art-game-studio/` and the eight agent files.
- Writes `skills/pixel-art-game-studio/.install-manifest.json` with a SHA-256 for each installed file.
- Re-running is safe: identical files are reported as `unchanged`.
- A destination file that exists but was not installed by this tool is a **conflict**: nothing is
  changed and the command exits with code 2. Move or rename your file and rerun.
- A previously installed file that differs needs `--update`. Before replacing, the old file is copied to
  `.claude/.pixel-art-game-studio-backups/<timestamp>/`. Local edits are backed up the same way and
  reported.
- Files that a newer version no longer ships are reported as `no longer shipped` and left in place.

Exit codes: `0` success, `1` error (bad path, unreadable manifest), `2` conflicts.

## Update

```bash
git pull
python scripts/install.py --scope project --project-dir ../my-game --update --dry-run
python scripts/install.py --scope project --project-dir ../my-game --update
```

## Uninstall

```bash
python scripts/install.py --scope project --project-dir ../my-game --uninstall --dry-run
python scripts/install.py --scope project --project-dir ../my-game --uninstall
```

Only files listed in the manifest **and unchanged since installation** are removed. Files you edited,
files you added inside the skill folder, your own agents, and your game are left alone. Backups are
kept; delete them yourself when you no longer need them.

## Manual installation

Copy two things into the target `.claude` directory (project or `~/.claude`):

```bash
mkdir -p <target>/.claude/skills <target>/.claude/agents
cp -r .claude/skills/pixel-art-game-studio <target>/.claude/skills/
cp .claude/agents/*.md <target>/.claude/agents/
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force <target>\.claude\skills, <target>\.claude\agents
Copy-Item -Recurse .claude\skills\pixel-art-game-studio <target>\.claude\skills\
Copy-Item .claude\agents\*.md <target>\.claude\agents\
```

Manual copies have no manifest, so the installer will treat them as conflicts later. Remove them
manually before switching to the installer.

## Verify

Start Claude Code in the project and type `/pixel-art-game-studio` (it appears in the `/` menu). Ask
"which subagents are available?" or run `/agents` to see where agent files are read from. If the
`.claude/agents/` directory was created after the session started, restart Claude Code.
