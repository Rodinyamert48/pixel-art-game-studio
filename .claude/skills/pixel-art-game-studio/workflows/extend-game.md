# Workflow B: Extend an existing game

Example request: "Add a new forest region with two NPCs and a branching quest."

1. **Inspect** the project: engine and version, folder layout, scenes, scripts, `data/`, assets, tests.
   Read the authoritative design and architecture files. If none exist, write a short
   `design/TECHNICAL_ARCHITECTURE.md` that *describes what is already there* before changing anything.
2. **Baseline**: run the existing tests and smoke check and record the results. Pre-existing failures
   are not yours to hide and not yours to silently fix; list them.
3. **Smallest coherent change**: list exactly which files will be added and which will be modified.
   New content goes in new files where the architecture allows (a new map file, a new dialogue file).
4. **Conventions**: reuse existing naming, IDs, data formats, scene structure, UI components. Do not
   introduce a second dialogue format or a second save system.
5. **Plan with dependencies**, then update `GAME_DESIGN.md`, `IMPLEMENTATION_ROADMAP.md`, and
   `ACCEPTANCE_CRITERIA.md` for the new content.
6. **Implement in order**:
   1. Level Design: new map topology, exits, spawns, link from an existing map (edit the existing map's
      exits only).
   2. Environmental Content: decor placements for the new map.
   3. Pixel Artist: new assets following the existing `ART_DIRECTION.md` palette and scale.
   4. NPC & Story: NPC definitions, dialogue, quest data, locale keys.
   5. Gameplay Engineer: any new mechanic, quest hooks, persistence of new state (with save migration
      defaults so old saves still load).
   6. UI Engineer: only if new screens or UI states are needed; add new locale strings.
7. **Verify**: `validate_game_project.py`, focused tests for the new content, then the full suite once.
   Confirm the new region is reachable from the existing world and that the quest can be completed.
8. **Regressions**: compare with the baseline. Any new failure is a defect to fix before delivery.
9. **Report** what changed, what was verified, and what still needs a manual playtest.

Never rewrite a whole system because a feature was requested. If the existing system truly cannot
support the feature, explain why and propose the change before making it.
