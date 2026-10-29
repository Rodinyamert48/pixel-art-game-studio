# Contributing

[Back to README](../README.md)

Thank you for helping. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Good first contributions

- Native-speaker review of a translation in `docs/i18n/` (then update its `review` field in
  `docs/i18n/manifest.json` with what was reviewed; do not claim a review that did not happen).
- Engine-specific notes (Godot, MonoGame, web) in `references/architecture.md`, tested on a real project.
- New procedural primitives in `generate_sample_asset.py`, with tests.
- New checks in `validate_game_project.py`, with a failing fixture in the tests.

## Rules

1. Keep the separation: skill instructions, agents, scripts, and documentation each in their place.
   Do not duplicate long instruction blocks; reference them.
2. Scripts use the Python standard library only, unless a dependency brings clear value and is
   discussed first.
3. Only documented Claude Code frontmatter fields. Check the official docs for
   [skills](https://code.claude.com/docs/en/skills) and [subagents](https://code.claude.com/docs/en/sub-agents).
4. Never add fake badges, metrics, screenshots, or testimonials.
5. Change the English README or `docs/i18n/en.md` first; then update the translations or mark them as
   out of date in the manifest.
6. Tests must not touch real user configuration; use temporary directories.

## Before opening a pull request

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Describe what changed, why, and what you ran. If you could not test something, say so.

## Releasing

Before tagging a release, run the commands above, update the version in `pyproject.toml`, and note
user-visible changes in the pull request or release notes.
