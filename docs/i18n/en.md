# Pixel Art Game Studio

[← Main README](../../README.md) · English (source document for all translations)

<!-- section: overview -->
## Overview

Pixel Art Game Studio is a Claude Code skill plus a team of eight specialist subagents for building
original 2D pixel-art games. You describe the game you imagine, what you dislike about the current
result, and what to change next. Claude plans the work, writes the code, generates the graphics, runs
the tests, fixes the bugs it can reproduce, and reports only what it actually verified.

It is made for cozy narrative adventures, life and farming simulators, dialogue-heavy RPGs, top-down
exploration games, and puzzle games, but works for other original 2D ideas too. Four parts stay
separate: the **skill** (instructions), the **agents** (specialists), the **scripts** (deterministic
tools), and **your game** (its own project directory).

<!-- section: features -->
## Features

- A Game Director workflow that turns a loose idea into a short design and a minimum playable loop.
- Eight specialists with clear ownership, limited tool lists, and structured reports.
- Procedural pixel art: JSON specs become real PNG sprite sheets, metadata, and previews. The same
  spec always produces the same bytes.
- A data contract for maps, decor, dialogue, quests, items, and translations, with a validator that
  finds unreachable exits, impossible dialogue branches, and missing text keys.
- QA with severity levels, reproducible defect reports, and verified fixes with regression tests.
- A safe installer with dry runs, conflict detection, backups, and a careful uninstaller.

<!-- section: agents -->
## The agent team

There are nine roles. The **Game Director** is the skill itself, running in your main Claude Code
session: it keeps the design, writes task briefs, checks every result, and decides when something is
done. The eight subagents are:

| Agent | Responsibility |
| --- | --- |
| `pixel-artist` | art direction, asset specs, generated sprites and tiles |
| `npc-story-engineer` | characters, branching dialogue, flags, quests |
| `world-builder-level-design` | map layout, collision, spawns, exits |
| `world-builder-environmental-content` | decoration, points of interest, region atmosphere |
| `ui-engineer` | menus, HUD, dialogue box, inventory and save screens |
| `gameplay-engineer` | movement, game state, inventory, quests, saving |
| `qa-tester` | tests, test runs, defect reports |
| `bug-fixer` | root-cause fixes with regression tests |

More detail: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Architecture

The Director is the skill, not a subagent, because it must see your requests and hold one source of
truth (`design/GAME_DESIGN.md`, `ART_DIRECTION.md`, and five more short documents). Specialists receive
briefs, work on the files they own, and report back; they cannot spawn further agents. Game content
lives in an engine-independent `data/` folder, so story, level, and environment work can happen in
parallel and be checked without starting the engine. If subagents are unavailable, the Director does
the same steps itself, one after another. See [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Prerequisites

- Claude Code (checked with version 2.1.312).
- Python 3.9 or newer; no extra packages are needed.
- For real games, the engine you choose, such as Godot 4 or the .NET SDK for MonoGame. The skill
  checks what is installed and asks before installing anything.

<!-- section: installation -->
## Installation

Clone the repository, then choose how to install. Preview every change with `--dry-run` first:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

The project scope writes to `<project>/.claude/`, the user scope to `~/.claude/`. Existing files that
the installer did not create are never replaced. Use `--update` to refresh an installation (old files
are backed up) and `--uninstall` to remove only unchanged files that it installed. You can also run
Claude Code directly inside this repository, or copy the folders by hand. All options are in
[INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Quick start

Open Claude Code in your project folder and type:

```text
/pixel-art-game-studio Create an original cozy top-down pixel-art game with a small town, a forest, three NPCs, branching dialogue, a day/night cycle, and saving.
```

The Director chooses sensible defaults, writes a short design, and builds a small playable version
first. To call one specialist directly, mention it, for example `@agent-qa-tester`.

<!-- section: examples -->
## Example prompts

```text
/pixel-art-game-studio Add a misty marsh region with two NPCs and a quest with two endings.
/pixel-art-game-studio The town feels empty. Add detail and small discoveries, but keep the paths clear.
/pixel-art-game-studio Inspect this game, run all available tests, and fix reproducible bugs.
```

You can write your requests in any language. A full example is in [examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Workflows

- **Create a game**: from idea to delivery in 14 stages, starting with a minimum playable loop.
- **Extend a game**: inspect the existing project, make the smallest coherent change, check for
  regressions.
- **Test and fix**: run real tests, report defects, fix confirmed ones with a bounded number of retries.
- **Generate assets**: art direction first, then specs, PNG files, and previews.
- **Release check**: a verdict backed by evidence: ready, ready with known issues, or not ready.

Overview: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Testing and bug fixing

The QA tester discovers which tools the game really has, turns acceptance criteria into tests, runs
them, and writes defect reports with severity, steps, and evidence. The bug fixer reproduces each
defect, fixes the root cause, adds a regression test, and runs the checks again. Weakening or deleting
tests is never allowed. To test this repository itself:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Details: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Limitations

- It does not create finished commercial games by itself; expect a working base that grows with your
  feedback.
- Without an installed engine, only data, assets, and engine-free logic can be verified.
- Structural checks cannot judge whether art looks good or a game feels fun; that needs a human.
- Translations are machine-assisted and waiting for review by native speakers.

<!-- section: troubleshooting -->
## Troubleshooting

If the skill does not appear, check that `SKILL.md` is in `.claude/skills/pixel-art-game-studio/`. If
the agents are not found, restart Claude Code after creating `.claude/agents/`. If the installer exits
with code 2, it found a file it did not create; read the plan it printed. More answers are in
[TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Contributing

Contributions are welcome, especially reviews of these translations by native speakers. Read
[CONTRIBUTING.md](../CONTRIBUTING.md) and the [Code of Conduct](../CODE_OF_CONDUCT.md) before opening a
pull request.

<!-- section: license -->
## License

Pixel Art Game Studio is released under the [MIT License](../../LICENSE). The games you make with it
belong to you.
