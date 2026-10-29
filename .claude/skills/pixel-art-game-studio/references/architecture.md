# Architecture reference

## Separation of concerns

| Thing | Lives in | Changes when |
| --- | --- | --- |
| This skill (instructions, references, scripts) | `.claude/skills/pixel-art-game-studio/` | The toolkit is updated |
| Specialist subagents | `.claude/agents/*.md` | The toolkit is updated |
| The game | The user's project directory | Every task |
| The game's source of truth | `<game>/design/*.md` | Requirements or interfaces change |

Never write game files into the skill directory, and never store per-game decisions in the skill.

## Recommended game layout (adapt to the engine's conventions)

```
<game>/
├── design/                 # source-of-truth documents (below)
├── data/                   # engine-agnostic content, validated by validate_game_project.py
│   ├── maps/<map_id>.json
│   ├── decor/<map_id>.json
│   ├── dialogue/<dialogue_id>.json
│   ├── quests.json
│   ├── items.json
│   ├── flags.json          # optional: flags set by code rather than data
│   └── locale/<lang>.json
├── art/specs/<asset>.json  # procedural asset sources
├── assets/                 # generated PNG + .meta.json (build output of art/specs)
├── src/ or scenes/ scripts/  # engine code
└── tests/
```

Keeping content in `data/` lets narrative, level, and environment specialists work without touching
engine code, lets QA validate content without running the engine, and makes localization possible.
If an existing project already stores content another way, keep its way and document it.

## Engine notes

**Godot 4** (default for narrative 2D): scenes per region, an autoload `GameState` for flags,
relationships, inventory, quests, time; `TileMapLayer` built from `data/maps`; `Control` nodes with a
shared `Theme` for UI; JSON loaded with `FileAccess` + `JSON.parse_string`. Checks:
`godot --headless --path <game> --quit` (startup), `godot --headless --path <game> --script res://tests/run_tests.gd`
(a small test runner script) or an installed test addon. Set project texture filter to Nearest and
stretch mode `canvas_items`/`viewport` with integer scaling.

**MonoGame** (code-first C#): `Game1` with a scene stack, systems as plain classes with no MonoGame
dependency so they can be unit-tested with xUnit; `SamplerState.PointClamp`; render to a fixed
low-resolution `RenderTarget2D` and scale by an integer. Checks: `dotnet build`, `dotnet test`.

**Web (TypeScript + canvas library)** and **pygame-ce** are reasonable when the engines above are not
available. Keep game logic in modules that can be tested without a window.

Whatever the engine: one place owns game state, systems talk through a small event or signal API,
UI reads state and sends commands but never mutates state directly, and save data is a plain
serializable snapshot of that state.

## Source-of-truth templates

Keep each document short. Prefer tables and IDs over prose.

### GAME_DESIGN.md
```
# <Title>
Premise (2-3 sentences) · World · Core loop (1 sentence) · Player abilities · Progression
## NPCs        id | role | want | secret
## Areas       map_id | purpose | connects to
## Systems     dialogue, quests, inventory, time, ...   (only what the game uses)
## Milestones  M1 minimum playable loop, M2 ..., each linked to ACCEPTANCE_CRITERIA.md
```
### TECHNICAL_ARCHITECTURE.md
```
Engine + version · Language · Target platforms · Logical resolution and scale
Module map (system -> files) · State owner · Event/signal list · Save format + version
Data contract location (data/) · External dependencies (with reason)
```
### ART_DIRECTION.md
See art-direction.md for the required fields.
### PROJECT_CONVENTIONS.md
```
Folder layout · Naming (snake_case IDs, file names) · ID registry rules
Input map (action -> keys/buttons) · Run command · Test commands · Build/export command
File ownership table (area -> agent)
```
### IMPLEMENTATION_ROADMAP.md
```
| Task ID | Milestone | Description | Owner | Depends on | Status |
```
### ACCEPTANCE_CRITERIA.md
```
| ID | Milestone | Criterion (observable) | Verification (test name or manual step) | Status |
```
### KNOWN_ISSUES.md
```
| Issue ID | Severity | Title | Status | Evidence | Next step |
```
