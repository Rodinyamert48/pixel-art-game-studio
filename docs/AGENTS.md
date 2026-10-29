# The agent team

[Back to README](../README.md)

Nine roles: the Game Director (the skill, in your main Claude Code session) and eight subagents defined
in `.claude/agents/`. Each subagent file uses documented frontmatter (`name`, `description`, `tools`,
`model: inherit`) and a system prompt with responsibilities, ownership boundaries, expected inputs,
quality criteria, constraints, and a report format.

| Agent | Tools | Owns | Never touches |
| --- | --- | --- | --- |
| Game Director (skill) | your session's tools | `design/*.md`, briefs, integration, final verdict | — |
| `pixel-artist` | Read, Write, Edit, Glob, Grep, Bash | `ART_DIRECTION.md`, `art/specs/`, generated assets | maps, dialogue, UI, gameplay code |
| `npc-story-engineer` | Read, Write, Edit, Glob, Grep, Bash | `data/dialogue/`, `data/quests.json`, narrative locale strings | map topology, UI, gameplay code |
| `world-builder-level-design` | Read, Write, Edit, Glob, Grep, Bash | `data/maps/` (tiles, spawns, exits, anchors) | decor, art, dialogue |
| `world-builder-environmental-content` | Read, Write, Edit, Glob, Grep, Bash | `data/decor/` | map tiles, spawns, exits |
| `ui-engineer` | Read, Write, Edit, Glob, Grep, Bash | UI scenes/scripts, theme, UI strings | game rules, save format |
| `gameplay-engineer` | Read, Write, Edit, Glob, Grep, Bash | core systems, state, input, save/load, loaders | dialogue content, layouts, art |
| `qa-tester` | Read, Write, Edit, Glob, Grep, Bash | test files, defect reports | game source, data, assets |
| `bug-fixer` | Read, Write, Edit, Glob, Grep, Bash | files named in the accepted defect brief | anything else without saying so |

## Why every specialist can write

All eight produce files (data, code, assets, tests), so all need Write/Edit, and all need Bash to run
the validator, generator, or tests. Claude Code's `tools` field restricts *which* tools an agent has,
not *which paths* it may edit, so file ownership is enforced by the briefs, by each agent's
instructions, and by the Director's review of every diff. If you want hard path limits, add
permission rules in your Claude Code settings. No agent has the `Agent` tool, so specialists cannot
spawn further agents, and no agent sets `permissionMode`, so your own permission settings apply.

## How to invoke

- **Through the skill** (normal): `/pixel-art-game-studio <request>`. The Director decides which
  specialists to use and writes the briefs.
- **Automatic delegation**: Claude may pick an agent whose `description` matches your request.
- **By name**: "Use the qa-tester subagent to test the save system."
- **Guaranteed**: `@agent-qa-tester test the save system` (or pick it from the `@` menu).

Installed as a plugin, every agent name carries the plugin prefix, for example
`pixel-art-game-studio:qa-tester`, and the skill is `/pixel-art-game-studio:pixel-art-game-studio`.

When you call a specialist directly, give it the same information a brief would (task, allowed files,
how to verify); see the brief template in
[agent-coordination.md](../.claude/skills/pixel-art-game-studio/references/agent-coordination.md).

## World Builder split

Level Design decides where you *can* walk; Environmental Content decides what you *see* along the way.
Level Design hands over keep-clear zones; Environmental Content never edits map structure and asks for
changes through the Director. The validator reports reachability problems as either
`(Level Design)` or `(Environmental Content)`.

## QA Tester vs Bug Fixer

QA finds and proves problems and never edits game code. Bug Fixer resolves one confirmed defect at a
time, adds a regression test, and proves the fix with a rerun. Neither may weaken a test to get a pass.
