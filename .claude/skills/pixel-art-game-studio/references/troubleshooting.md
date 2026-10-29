# Troubleshooting reference (for Claude while working)

| Symptom | Likely cause | Action |
| --- | --- | --- |
| A specialist agent is not offered / "agent not found" | Agent files not installed, or `.claude/agents/` was created after the session started | Check `.claude/agents/` or `~/.claude/agents/`; ask the user to restart Claude Code; meanwhile run the phase yourself |
| `${CLAUDE_SKILL_DIR}` appears literally | Variable not expanded in this context | Use the directory that contains `SKILL.md` (project: `.claude/skills/pixel-art-game-studio`, user: `~/.claude/skills/pixel-art-game-studio`) |
| `python` not found | Python missing or named `python3`/`py` | Try `python3` or `py -3`; scripts need Python 3.9+ and no packages |
| `godot` not found | Engine not installed or not on PATH | Report it; ask before installing; data validation and unit-testable logic still work |
| Headless Godot hangs | Main scene waits for input or never quits | Run with a timeout; add a `--quit` path or a test runner that calls `get_tree().quit()` |
| Blurry pixel art | Linear filtering or non-integer scaling | Nearest filter, integer scale, disable mipmaps |
| Asset generator refuses to write | Existing file differs from new output | Inspect the difference; pass `--force` only if replacing is intended |
| Validator: "unreachable" | Walls, NPCs, or blocking decor cut off a tile | Ask Level Design (topology) or Environmental Content (decor) depending on cause |
| Validator: "flag never set" | Branch requires a flag nothing sets | Add the effect that sets it, list it in `data/flags.json` if code sets it, or remove the branch |
| Save from older version crashes | Missing field without default | Add migration/default in the loader plus a regression test |
| Two agents edited the same file | Brief ownership overlapped | Stop, reconcile by reading both changes, re-run checks, tighten ALLOWED FILES |
| Tests pass but the game is broken | Tests cover logic, not integration | Add an integration or smoke test that reproduces the issue |
