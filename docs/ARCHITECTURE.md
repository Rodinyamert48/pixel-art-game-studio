# Architecture

[Back to README](../README.md)

## Components

| Component | Path | Purpose |
| --- | --- | --- |
| Skill | `.claude/skills/pixel-art-game-studio/SKILL.md` | Entry point. Defines the Game Director: discovery, contracts, build order, delegation, safety, validation, reporting. |
| Workflows | `.claude/skills/pixel-art-game-studio/workflows/` | Step-by-step procedures, read on demand. |
| References | `.claude/skills/pixel-art-game-studio/references/` | Architecture, art direction, data contracts, coordination, quality, troubleshooting. |
| Skill scripts | `.claude/skills/pixel-art-game-studio/scripts/` | `generate_sample_asset.py`, `validate_game_project.py` (stdlib Python). |
| Subagents | `.claude/agents/*.md` | Eight specialists with frontmatter `name`, `description`, `tools`, `model`. |
| Repository scripts | `scripts/` | Installer, repository validator, translation checker. |
| Tests | `tests/` | `unittest` suites for every script. |
| Docs | `docs/`, `docs/i18n/` | Guides and 16 translations. |

## Why the Director is the skill, not an agent

Claude Code subagents work in their own context and return a result to the main conversation. The
coordinator must see the user's requests, keep the source of truth, and integrate results, so it is the
main session following `SKILL.md`. Specialist `tools` lists exclude `Agent`, so they cannot create a
second, hidden delegation layer.

## Progressive loading

Claude Code loads the skill's `description` for discovery and the body of `SKILL.md` when the skill is
used. Supporting files are read only when `SKILL.md` points to them for the current task, which keeps
small requests cheap. `SKILL.md` stays well under the documented 500-line guidance.

## Data flow in a game project

```
user request -> Director -> design/*.md (source of truth)
                         -> briefs -> specialists -> data/, art/specs/, assets/, src/, tests/
                         <- reports <- specialists
             -> validate_game_project.py + engine checks + tests -> report to user
```

The engine-agnostic `data/` contract (defined in
[game-systems.md](../.claude/skills/pixel-art-game-studio/references/game-systems.md)) is what lets the
story, level, and environment specialists work in parallel without editing engine code, and what lets
QA check content without launching the game.

## Ownership

Each area has exactly one writer per task; see
[agent-coordination.md](../.claude/skills/pixel-art-game-studio/references/agent-coordination.md).
The two World Builder roles are split by file: topology in `data/maps/`, decoration in `data/decor/`.
The validator attributes reachability errors to the responsible role.

## Sequential fallback

If subagents cannot be used, the Director performs each specialist's brief itself, in dependency order,
using the agent files as checklists. Results and reports keep the same format.
