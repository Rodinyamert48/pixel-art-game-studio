# Troubleshooting

[Back to README](../README.md)

| Problem | What to do |
| --- | --- |
| `/pixel-art-game-studio` does not appear | Check that `SKILL.md` is at `.claude/skills/pixel-art-game-studio/SKILL.md` (project) or `~/.claude/skills/pixel-art-game-studio/SKILL.md` (user) and that its first line is `---`. |
| Agents are not used or "not found" | Check `.claude/agents/` or `~/.claude/agents/`. If that directory was created after the session started, restart Claude Code. Without agents the skill still works, sequentially. |
| Installer exits with code 2 | A file it wants to write already exists and was not installed by it (conflict), or it differs and needs `--update`. Read the plan it printed. |
| Installer says the manifest is unreadable | Fix or delete `skills/pixel-art-game-studio/.install-manifest.json` in the target. Deleting it makes the installer treat existing files as conflicts. |
| `python` is not recognized | Use `python3` or `py -3`, or install Python 3.9+. |
| The game engine is missing | The skill reports it and asks before installing. Data, assets, and engine-free logic are still checked. |
| Pixel art looks blurry | Use nearest-neighbor filtering, integer scaling, no mipmaps. |
| Generator refuses to write | An existing file differs. Inspect it; use `--force` only if replacing is intended. |
| Validator reports "unreachable" | The message names the responsible role: Level Design (walls, NPC placement) or Environmental Content (blocking decor). |
| Validator reports "flag that nothing sets" | A dialogue choice or quest requires a flag no data sets. Add the effect, list code-set flags in `data/flags.json`, or remove the branch. |
| Tests fail after editing docs | Run `python scripts/validate_repository.py` to see broken links or missing sections. |

For issues Claude itself may hit while working, see the skill's
[troubleshooting reference](../.claude/skills/pixel-art-game-studio/references/troubleshooting.md).
