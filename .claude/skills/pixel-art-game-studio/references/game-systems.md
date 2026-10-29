# Game systems reference

Implement only what the design requires. This file defines the **data contract** that
`scripts/validate_game_project.py` checks, plus the runtime patterns the Gameplay Engineer follows.
IDs are `snake_case`. Coordinates are `[x, y]` tile positions, origin top-left.

## Maps (`data/maps/<map_id>.json`) — owner: Level Design

```json
{
  "id": "town",
  "tiles": ["##########",
            "#........#",
            "#........>",
            "##########"],
  "walkable": ".>",
  "spawns": {"default": [2, 1], "from_forest": [8, 2]},
  "exits": [{"at": [9, 2], "to": "forest", "spawn": "from_town"}],
  "npcs": [{"id": "mira", "at": [5, 1]}],
  "interactables": [{"id": "notice_board", "at": [3, 2]}]
}
```

- All rows have equal length. `walkable` lists the characters the player can stand on (default `"."`).
- NPCs and interactables block their own tile; they are reachable when an adjacent tile is reachable.
- Exits must be on walkable tiles and point to an existing map and an existing spawn in it.
- Validation: flood fill from all spawns must reach every exit, NPC, and interactable, including after
  blocking decor is applied.

## Decor (`data/decor/<map_id>.json`) — owner: Environmental Content

```json
{"map": "town", "placements": [{"asset": "tree_oak", "at": [1, 1], "blocking": true}]}
```

Decor never sits on a spawn, exit, NPC, or interactable tile, and blocking decor must not cut off
anything the flood fill needs. Environmental Content never edits `tiles`, `exits`, or `spawns`; if a
structural change is needed it asks Level Design via the Director.

## Dialogue (`data/dialogue/<dialogue_id>.json`) — owner: NPC & Story

```json
{
  "id": "mira_intro",
  "npc": "mira",
  "start": "greet",
  "nodes": {
    "greet":  {"text": "dlg.mira_intro.greet", "next": "ask"},
    "ask":    {"text": "dlg.mira_intro.ask", "choices": [
                {"text": "dlg.mira_intro.ask.help", "next": "thanks",
                 "effects": {"set_flags": ["agreed_to_help"], "relationship": {"mira": 1},
                             "start_quest": "lost_cat"}},
                {"text": "dlg.mira_intro.ask.later", "next": "bye"},
                {"text": "dlg.mira_intro.ask.bell", "next": "thanks",
                 "requires_flags": ["has_bell"], "effects": {"take_items": {"cat_bell": 1}}}]},
    "thanks": {"text": "dlg.mira_intro.thanks", "end": true},
    "bye":    {"text": "dlg.mira_intro.bye", "end": true}
  }
}
```

- Each node has exactly one of `next`, `choices`, or `"end": true`.
- `text` values are locale keys, never literal strings.
- `effects` (on nodes or choices): `set_flags`, `clear_flags`, `relationship` (npc -> delta),
  `start_quest`, `give_items` / `take_items` (item -> count).
- Choice conditions: `requires_flags`, `forbids_flags`. A required flag must be set somewhere (dialogue
  effects, quest rewards, or `data/flags.json`), otherwise the branch is impossible.
- Validation: start exists, all `next` targets exist, no unreachable nodes (warning), known quests,
  items, and locale keys.

## Quests (`data/quests.json`) — owner: NPC & Story (data), Gameplay (runtime)

```json
{"quests": [{
  "id": "lost_cat", "title": "quest.lost_cat.title", "requires_flags": [],
  "objectives": [
    {"id": "search", "type": "reach",   "target": "forest"},
    {"id": "bell",   "type": "collect", "target": "cat_bell", "count": 1},
    {"id": "return", "type": "talk",    "target": "mira"}],
  "rewards": {"items": {"apple": 2}, "set_flags": ["cat_returned"], "relationship": {"mira": 2}}
}]}
```

Objective types: `reach` (map id), `collect` (item id), `talk` (npc id), `flag` (flag id). Runtime
states: `inactive -> active -> completed` (or `failed` / `cancelled` if the design needs it).
Objectives are evaluated on events (`item_added`, `map_entered`, `dialogue_finished`, `flag_set`),
not every frame.

## Items (`data/items.json`) and flags (`data/flags.json`)

```json
{"items": [{"id": "apple", "name": "item.apple.name", "max_stack": 99},
           {"id": "cat_bell", "name": "item.cat_bell.name", "max_stack": 1}]}
```
```json
{"flags": ["day_2_started"]}
```

Inventory rules: stacks capped at `max_stack`; adding beyond capacity returns the remainder instead
of dropping it silently; every change emits an `inventory_changed` event that UI listens to.

## Localization (`data/locale/<lang>.json`)

Flat `key -> string`. `en.json` is the reference locale; every key used in data must exist there.
Other locales missing keys produce warnings. UI must handle strings 40% longer than English.

## Runtime patterns

- **State owner**: one object (`GameState` autoload / service) holds flags, relationships, inventory,
  quest states, current map, time. Systems change it through methods that emit events.
- **Movement and collision**: tile-based collision from `walkable`; interaction = facing tile check;
  input actions, not raw keys.
- **Transitions**: exit -> fade -> load map -> place at spawn -> emit `map_entered`.
- **Dialogue runner**: walks nodes, filters choices by conditions, applies effects through `GameState`,
  never touches UI nodes directly (UI subscribes to `dialogue_line` / `dialogue_choices`).
- **Time** (if needed): minutes advance on a timer; `day_started` event runs daily processing; NPC
  schedules are tables `time -> map, position`.
- **Save/load**: JSON snapshot `{"version": N, "state": {...}}`; write to a temp file then rename;
  keep the previous save as `.bak`; on load validate types, fill missing fields with defaults,
  migrate older versions, and refuse (with a message) rather than crash on corrupted files. Never
  overwrite a save slot without the player's action.
- **Settings**: separate file from saves; volume, window scale, key bindings if in scope.

Tests every project should have: save/load round trip, corrupted save rejected, quest completes via
its events, inventory stack limits, dialogue choice effects applied, map transition lands on spawn.
