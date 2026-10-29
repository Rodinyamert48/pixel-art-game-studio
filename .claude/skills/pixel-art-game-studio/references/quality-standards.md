# Quality standards reference

## Test layers for a game project

| Layer | What | Typical tool |
| --- | --- | --- |
| Data validation | maps, decor, dialogue, quests, items, locale, asset meta | `validate_game_project.py` |
| Smoke | game starts, loads first scene, quits | `godot --headless --path . --quit`, run with timeout |
| Unit | pure logic: inventory, quest evaluation, dialogue runner, save serializer, time | engine test runner, xUnit, unittest, vitest |
| Integration | systems together: dialogue effect starts quest, collecting item completes objective, transition lands on spawn | engine test scenes / scripted input |
| Gameplay state | scripted sequences of actions reach expected flags | same as integration |
| Save/load | round trip equality, old-version migration, corrupted file rejected, no silent overwrite | unit + integration |
| UI state | screens open/close, focus moves, buttons call the right command | engine UI tests where practical |
| Build/export | `godot --headless --export-release <preset> <path>`, `dotnet publish` | only if presets exist |
| Regression | one test per fixed meaningful bug | all of the above |

Discover what the project actually has. If nothing exists, the QA Tester adds the smallest runner that
works with the installed engine and documents the command in `PROJECT_CONVENTIONS.md`.

## Cross-system integration checklist

World <-> navigation · Controls <-> collision · NPCs <-> dialogue · Dialogue <-> progression flags ·
Quests <-> inventory · UI <-> game state · Save/load <-> every persistent system · Assets <-> animation.

## Unusual sequences to try

Interact during a transition; open the menu during dialogue; save mid-quest then reload; collect an item
twice; finish objectives out of order; spam the interact key; quit during save; load a save from before
a new feature existed.

## Defect report format

```
ID: BUG-<number>
TITLE: <short, specific>
SEVERITY: Critical | High | Medium | Low | Enhancement
CLASSIFICATION: confirmed | suspected | unverified | blocked-by-tooling | manual-playtest-required
SUBSYSTEM: <movement, dialogue, quests, save, UI, assets, ...>
PRECONDITIONS: <state, save file, settings>
STEPS: 1. ... 2. ...
EXPECTED: ...
ACTUAL: ... (observed, not guessed)
EVIDENCE: <log excerpt, failing test name, file:line>
REGRESSION RISK: <what else could break when fixing>
VERIFY FIX BY: <test or steps>
```

## Severity model

- **Critical**: game cannot start, data is lost, or core progression is irreparably blocked.
- **High**: major gameplay, progression, or saving functionality broken.
- **Medium**: a meaningful feature fails but a workaround exists.
- **Low**: minor visual, usability, or nonessential issue.
- **Enhancement**: not a defect.

## Honesty rules

- Do not claim visual inspection without having viewed an image.
- Do not claim gameplay testing without executing the game or its logic.
- A passing data validator does not mean the game is fun, readable, or bug-free.
- Report skipped checks with the reason.
