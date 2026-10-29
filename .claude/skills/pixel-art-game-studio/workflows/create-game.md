# Workflow A: Create a new game

Use when the working directory has no game yet. Each stage ends with a gate; do not skip a gate.

## Stage 1: Interpret the request

Extract into a short list (write unknowns as chosen defaults, marked `default`):

- Genre, audience, camera (top-down by default), platform (desktop by default).
- Core loop in one sentence ("explore, talk, help villagers, unlock the next area").
- Controls (keyboard + gamepad by default; mouse for menus).
- Required systems (dialogue, quests, inventory, time, farming, shops, save).
- Narrative needs (branching, endings, relationships).
- Scope (number of regions and NPCs for the first milestone).
- Deployment goal (local run, desktop export, web export).

Do not ask the user about anything that has a reasonable default. Ask only about blockers.

## Stage 2: Select the technology

Score candidates against: 2D support, target platform, language, how well Claude Code can build and
test it from the command line, UI toolkit, asset pipeline, export options, and **what is installed**.

| Situation | Default |
| --- | --- |
| Narrative/exploration game, desktop or web, engine available | Godot 4 (GDScript), headless checks via `godot --headless` |
| Code-first C#, strong testing needs | MonoGame + xUnit (`dotnet test`) |
| Browser-only, no engine installed | TypeScript + a 2D canvas library, tested with the project's test runner |
| Python-only environment | pygame-ce, tested with `unittest` |

Record the choice and the reason in `TECHNICAL_ARCHITECTURE.md`. If the chosen engine is not installed,
say so, propose the install command, and wait for permission before installing anything.

## Stage 3: Design (keep it to one or two screens of text)

Create `design/` with the seven source-of-truth documents (templates in
[../references/architecture.md](../references/architecture.md)). `GAME_DESIGN.md` covers premise, world,
loop, player abilities, progression, main NPCs, required areas, systems, UI needs, controls, milestones.
`ART_DIRECTION.md` is written by the Pixel Artist in Stage 7 but the resolution and scale are fixed now.

**Gate:** documents exist, milestone 1 (minimum playable loop) has explicit acceptance criteria.

## Stage 4: Technical foundation

Director or Gameplay Engineer, sequentially:

1. Create the engine project, folder layout, and `data/` folder (contract in
   [../references/game-systems.md](../references/game-systems.md)).
2. Main scene, input map, player placeholder (a generated 16x16 sprite is fine), tile collision.
3. A run command and a smoke check recorded in `PROJECT_CONVENTIONS.md`.

**Gate:** the smoke check runs and exits cleanly (or the blocker is documented).

## Stage 5: Minimum playable loop

One area, one NPC, one dialogue with one choice, one small task, one visible result, save and reload.
This is a vertical slice through every layer; prefer doing it with at most two specialists in sequence
(Gameplay Engineer, then NPC & Story Engineer) rather than all eight.

**Gate:** QA Tester verifies milestone 1 criteria with real commands.

## Stage 6-10: Systems, art, world, narrative, UI

Plan tasks from the roadmap and delegate with briefs. Typical dependency order:

```
Gameplay interfaces (events, state, save schema)
  ├── Level Design: maps, exits, spawns ──> Environmental Content: decor placements
  ├── NPC & Story: dialogue + quests data ──> UI: dialogue box, quest log
  └── Pixel Artist: art direction + assets (parallel with data work once palette is fixed)
```

Safe parallel pairs: Pixel Artist assets + Story dialogue data; Level Design for region B + UI settings
screen. Unsafe: Level Design and Environmental Content on the same map at once.

After each specialist returns, run `validate_game_project.py` and the engine smoke check before
accepting.

## Stage 11: Integration

Verify the cross-system paths listed in [../references/quality-standards.md](../references/quality-standards.md)
(world/navigation, controls/collision, NPC/dialogue, dialogue/progression, quests/inventory,
UI/state, save/load, assets/animation).

## Stage 12: QA and fixes

Follow [test-and-fix.md](test-and-fix.md).

## Stage 13: Polish

Visual consistency against `ART_DIRECTION.md`, readable text at native resolution, input feedback,
loading behavior, accessibility basics (rebindable keys if in scope, no color-only information).

## Stage 14: Delivery

Run [release-check.md](release-check.md) and produce the final report described in `SKILL.md` §8.
