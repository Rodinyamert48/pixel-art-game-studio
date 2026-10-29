# Workflows

[Back to README](../README.md)

The skill chooses a workflow from your request and the state of the project. The full procedures live
in the skill so Claude reads them only when needed.

| Workflow | When | Key gates |
| --- | --- | --- |
| [Create a game](../.claude/skills/pixel-art-game-studio/workflows/create-game.md) | No game in the directory | design docs exist; foundation launches; minimum playable loop verified by QA |
| [Extend a game](../.claude/skills/pixel-art-game-studio/workflows/extend-game.md) | A game exists | baseline recorded; smallest coherent change; no regressions vs baseline |
| [Test and fix](../.claude/skills/pixel-art-game-studio/workflows/test-and-fix.md) | "Test this", "fix the bugs" | confirmed defects only; regression test per fix; max 3 attempts per defect |
| [Generate assets](../.claude/skills/pixel-art-game-studio/workflows/generate-assets.md) | Art requests | art direction fixed first; specs saved; previews reviewed or flagged |
| [Release check](../.claude/skills/pixel-art-game-studio/workflows/release-check.md) | "Is it done?", milestones | verdict Ready / Ready with known issues / Not ready, with evidence |

## Minimum playable loop first

Every new game first gets one small, complete loop: enter an area, move, talk to an NPC, make a choice,
finish a small task, see a result, save, reload. Everything else extends a loop that already works.

## Parallel vs sequential

The Director runs specialists in parallel only when their files do not overlap and neither defines an
interface the other consumes. Map topology always comes before decoration; data formats before UI
integration; fixes before the final regression run.

## Giving feedback

You do not need to speak in tasks. "The forest is too dark", "Mira should be grumpier at first", "the
inventory is confusing" are enough. The Director turns feedback into changes to the design documents
and briefs for the right specialists.
