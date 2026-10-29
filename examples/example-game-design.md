# Example design: Lantern Hollow (condensed GAME_DESIGN.md)

[Back to README](../README.md) · Previous: [idea](example-game-idea.md) · Next: [example session](example-workflow.md)

An original setting written for this example. The real file in a game lives at `design/GAME_DESIGN.md`.

## Premise

You arrive in Lantern Hollow as its new lamplighter. Every night another lantern refuses to light.
The townsfolk each have a reason to hope, or fear, that the old lamplighter's disappearance and the
dying lanterns are connected.

**Core loop:** explore by day, talk and help, relight lanterns at dusk, learn a little more each night.

## NPCs

| id | Role | Wants | Secret |
| --- | --- | --- | --- |
| `mira` | Baker, first friend | Her late brother's lantern lit again | She kept his last letter unopened |
| `oskar` | Retired clockmaker | To be left alone | He built the lantern mechanism |
| `tavi` | Child who maps the forest | Someone to believe their "moving lights" | They are right |

## Areas

| map_id | Purpose | Connects to |
| --- | --- | --- |
| `town` | Hub, bakery, square with five lanterns | `forest` (east) |
| `forest` | Tavi's paths, the old lamplighter's camp | `town` (west) |

## Systems

Dialogue with choices and flags; relationships (-3..+5); quests (`reach`, `collect`, `talk`, `flag`);
small inventory (max 12 slots); day/night with dusk event; save/load (one slot plus backup).

## Milestones

- **M1** Town, Mira, quest `first_light`: talk to Mira, collect `lamp_oil` from the bakery shelf, light
  the square lantern, save, reload with quest completed.
- **M2** Forest, Tavi, day/night, quest `moving_lights` with two endings.
- **M3** Oskar, relationship screen, polish.

## Data sample (validated by `validate_game_project.py`)

`data/maps/town.json`

```json
{
  "id": "town",
  "tiles": ["##########",
            "#........#",
            "#........>",
            "##########"],
  "walkable": ".>",
  "spawns": {"default": [1, 1], "from_forest": [8, 2]},
  "exits": [{"at": [9, 2], "to": "forest", "spawn": "from_town"}],
  "npcs": [{"id": "mira", "at": [4, 1]}],
  "interactables": [{"id": "square_lantern", "at": [6, 2]}, {"id": "bakery_shelf", "at": [2, 2]}]
}
```

`data/dialogue/mira_first_light.json`

```json
{
  "id": "mira_first_light", "npc": "mira", "start": "hello",
  "nodes": {
    "hello": {"text": "dlg.mira_first_light.hello", "next": "ask"},
    "ask": {"text": "dlg.mira_first_light.ask", "choices": [
      {"text": "dlg.mira_first_light.ask.yes", "next": "thanks",
       "effects": {"start_quest": "first_light", "relationship": {"mira": 1}}},
      {"text": "dlg.mira_first_light.ask.why", "next": "story",
       "effects": {"set_flags": ["heard_brother_story"]}}]},
    "story": {"text": "dlg.mira_first_light.story", "next": "ask"},
    "thanks": {"text": "dlg.mira_first_light.thanks", "end": true}
  }
}
```

`data/quests.json`

```json
{"quests": [{
  "id": "first_light", "title": "quest.first_light.title",
  "objectives": [
    {"id": "oil", "type": "collect", "target": "lamp_oil"},
    {"id": "light", "type": "flag", "target": "square_lantern_lit"}],
  "rewards": {"items": {"honey_bun": 1}, "set_flags": ["first_light_done"], "relationship": {"mira": 1}}
}]}
```

`square_lantern_lit` is set by gameplay code when the player uses the lantern, so it is listed in
`data/flags.json`.

## Art direction summary

320x180, 16x16 tiles, 24-color palette with warm lantern yellows against blue-violet night ramps,
1 px dark outline on characters and props only, light from top-left by day and from lanterns at night.
