# Agent coordination reference

## Roles (nine)

1. **Game Director** — the main Claude Code session following `SKILL.md`. Not a subagent.
2. `pixel-artist` 3. `npc-story-engineer` 4. `world-builder-level-design`
5. `world-builder-environmental-content` 6. `ui-engineer` 7. `gameplay-engineer`
8. `qa-tester` 9. `bug-fixer`

Subagents do not spawn further agents (their `tools` lists exclude `Agent`); all coordination flows
through the Director, which keeps one coherent source of truth.

## File ownership (default; record the project's version in PROJECT_CONVENTIONS.md)

| Area | Owner | Others may |
| --- | --- | --- |
| `design/*.md` | Director | propose edits in reports |
| `design/ART_DIRECTION.md`, `art/specs/`, `assets/` | Pixel Artist | read |
| `data/maps/` | Level Design | read |
| `data/decor/` | Environmental Content | read |
| `data/dialogue/`, `data/quests.json`, NPC definitions, `data/locale/` content | NPC & Story | UI adds UI strings to locale |
| UI scenes/scripts, theme | UI Engineer | read |
| Core systems, state, save, input, integration code | Gameplay Engineer | read |
| `tests/`, QA reports | QA Tester | Bug Fixer adds regression tests |
| Any file named in an accepted bug brief | Bug Fixer (for that brief only) | — |

## Delegation brief (copy and fill)

```
TASK: <ID, e.g. M2-LD-01>
AGENT: <agent name>
OBJECTIVE: <one sentence, observable outcome>
REQUIREMENTS: <bullets, with IDs from GAME_DESIGN / ACCEPTANCE_CRITERIA>
ALLOWED FILES: <paths the agent may create/modify>; everything else read-only
DEPENDS ON: <task IDs / interfaces that already exist>
EXPECTED OUTPUT: <files, data, tests>
ACCEPTANCE: <criteria the Director will check>
VERIFY WITH: <exact commands, e.g. python <skill>/scripts/validate_game_project.py .>
INTEGRATION NOTES: <IDs, signals, formats others rely on>
REFERENCES: <absolute paths to the skill reference files needed>
```

Pass absolute paths: subagents do not know where the skill was installed.

## Completion report (every agent returns this)

```
TASK: <ID>
STATUS: completed | partially completed | blocked | failed
FILES: created ... / modified ...
DECISIONS: ...
COMMANDS RUN: <command> -> <actual result summary>
VERIFICATION: <what passed, what failed, what was not run and why>
LIMITATIONS: ...
REMAINING WORK: ...
INTEGRATION WARNINGS: ...
```

A report that lists no commands has verified nothing. The Director inspects files and reruns cheap
checks before accepting.

## Parallel vs sequential

Parallel only when all hold: disjoint ALLOWED FILES, no interface being defined by one and consumed by
the other, no ordering dependency in the roadmap.

| Usually parallel | Always sequential |
| --- | --- |
| Asset generation + dialogue writing (palette fixed) | Architecture -> dependent systems |
| UI settings screen + new map topology | Map topology -> decor on that map |
| Two maps by Level Design in separate files | Dialogue format agreed -> UI dialogue integration |
| Review of docs + validation of scripts | Root-cause fix -> final regression run |
| | Integration -> end-to-end tests |

## Integration gates

After each batch: (1) read diffs, (2) run `validate_game_project.py`, (3) run the smoke check,
(4) run the tests of touched subsystems, (5) update roadmap status and `KNOWN_ISSUES.md`.

## Economy

- Do not call every agent for every task; pick the smallest set.
- Simple edits: Director does them directly.
- Briefs reference files instead of pasting large content.
- When subagents are unavailable, run the same briefs sequentially in the main session.
