# Testing

[Back to README](../README.md)

## Repository checks

Run from the repository root. All use the Python standard library only.

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/check_translations.py
```

| Suite | What it proves |
| --- | --- |
| `tests/test_installer.py` | project/user/explicit destinations, dry run writes nothing, idempotent reinstall, unmanaged conflicts untouched, backups on update, uninstall keeps user files, invalid paths rejected, corrupt manifest not overwritten. All in temporary directories; the real `~/.claude` is never used. |
| `tests/test_repository_validation.py` | the real repository passes; broken copies (bad agent name, `Agent` tool, missing agent, frontmatter not on line 1, broken link, syntax error, badge) fail |
| `tests/test_translation_manifest.py` | exactly the 16 required languages; real translations pass; copied English, wrong script, MSA/Egyptian mix-up, missing section, placeholder, missing selector link all fail |
| `tests/test_asset_generator.py` | valid PNG output, palette-only pixels with binary alpha, determinism, no overwrite without `--force`, clipping reported, invalid specs rejected |
| `tests/test_game_project_validation.py` | a fixture game passes cleanly; broken exits, walled-off NPCs, blocking decor, missing dialogue nodes, impossible branches, unknown items and locale keys, asset size mismatches are caught |

`validate_repository.py` checks required files, `SKILL.md` and agent frontmatter, agent tool lists,
Python syntax of every `.py` file, internal Markdown links (outside code blocks), the absence of
unconfigured badges, `.gitignore` sanity, and runs the translation gate.

## What the translation gate can and cannot do

It checks structure: every file present, every section marker present with real prose, prose in the
expected writing system, language marker words present, English function words rare, few lines copied
from English, links back to the README, `dir="rtl"` for right-to-left languages. It cannot judge
accuracy or fluency. Native-speaker review is still needed.

## Game projects

For games built with the skill, the QA Tester discovers the engine's own tools. The data contract is
always checkable:

```bash
python .claude/skills/pixel-art-game-studio/scripts/validate_game_project.py path/to/game
python .claude/skills/pixel-art-game-studio/scripts/validate_game_project.py path/to/game --strict --json
```

Strategy, severity model, and defect format:
[quality-standards.md](../.claude/skills/pixel-art-game-studio/references/quality-standards.md).
