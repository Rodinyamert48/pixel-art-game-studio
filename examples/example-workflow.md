# Example session: building milestone 1 of Lantern Hollow

[Back to README](../README.md) · Previous: [design](example-game-design.md)

An illustration of how the Game Director runs the workflow. Command results below are examples of the
report format, not recorded output.

## 1. Discovery

The Director lists the directory (empty), checks `python --version`, `godot --version`, and
`dotnet --version`, and records what exists. If Godot is missing it says so and proposes how to install
it, waiting for permission.

## 2. Contract

It writes the seven `design/` documents in one pass: short, mostly tables. Milestone M1 criteria:

| ID | Criterion | Verification |
| --- | --- | --- |
| M1-1 | Game starts to the town map | headless smoke run |
| M1-2 | Talking to Mira and choosing "yes" starts `first_light` | integration test |
| M1-3 | Collecting `lamp_oil` then lighting the lantern completes the quest | integration test |
| M1-4 | Save, quit, load restores quest state and position | save round-trip test |
| M1-5 | All data valid | `validate_game_project.py` with 0 errors |

## 3. Foundation (sequential)

Brief `M1-GP-01` to `gameplay-engineer`: project, input map, `GameState`, map loader, movement,
collision, run and smoke commands. The Director inspects the diff and runs the smoke command itself.

## 4. Parallel batch

Once the data formats exist, three independent briefs run at the same time:

- `M1-LD-01` to `world-builder-level-design`: `data/maps/town.json` (allowed files: `data/maps/`).
- `M1-ST-01` to `npc-story-engineer`: Mira, her dialogue, `first_light`, locale strings
  (allowed: `data/dialogue/`, `data/quests.json`, `data/items.json`, `data/locale/`).
- `M1-PA-01` to `pixel-artist`: `ART_DIRECTION.md`, player and Mira walk cycles, town tiles, lantern
  (allowed: `design/ART_DIRECTION.md`, `art/specs/`, `assets/`).

Then, sequentially: `M1-EC-01` (decor after topology), `M1-UI-01` (dialogue box after the dialogue
runner API), `M1-GP-02` (dialogue runner, quests, save/load integration).

## 5. QA and fixes

`qa-tester` maps M1-1..M1-5 to tests, runs them, and reports, for example:

```
ID: BUG-003
TITLE: Quest stays active after lighting the lantern if lamp_oil was collected before the quest started
SEVERITY: High   CLASSIFICATION: confirmed   SUBSYSTEM: quests
STEPS: 1. Pick up lamp_oil  2. Talk to Mira, choose yes  3. Light the lantern
EXPECTED: first_light completed   ACTUAL: objective "oil" still 0/1
EVIDENCE: tests/test_quests.gd::test_item_collected_before_quest_start FAILED
VERIFY FIX BY: same test passes; full quest suite passes
```

`bug-fixer` finds the root cause (objectives only count `item_added` events after activation, ignoring
the current inventory), evaluates inventory on activation, adds the regression test, reruns the suite.

## 6. Release check and report

The Director runs the release check and reports: what M1 contains, how to run it, each command and
its result, open issues (for example a Low severity text overflow in a long German string), and what
still needs a human playtest (feel of movement, art taste).
