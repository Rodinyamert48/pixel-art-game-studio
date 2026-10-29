"""Repository validator tests: the real repository passes, and broken copies are caught."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from _util import REPO, load

validate_repository = load(REPO / "scripts" / "validate_repository.py")


class RepositoryValidationTest(unittest.TestCase):
    def test_real_repository_passes(self):
        self.assertEqual(validate_repository.validate(REPO), [])

    def test_frontmatter_parser(self):
        fm = validate_repository.frontmatter("---\nname: x\ndescription: \"hello\"\n---\nbody")
        self.assertEqual(fm, {"name": "x", "description": "hello"})
        self.assertIsNone(validate_repository.frontmatter("\n---\nname: x\n---"))
        self.assertIsNone(validate_repository.frontmatter("---\nname: x\n"))


class BrokenCopyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))

    def tearDown(self):
        self.tmp.cleanup()

    def problems(self):
        return validate_repository.validate(self.root, translations=False)

    def test_baseline_copy_passes(self):
        self.assertEqual(self.problems(), [])

    def test_agent_with_agent_tool_or_bad_name(self):
        p = self.root / ".claude/agents/bug-fixer.md"
        p.write_text(p.read_text(encoding="utf-8").replace("tools: Read,", "tools: Agent, Read,")
                     .replace("name: bug-fixer", "name: bug:fixer"), encoding="utf-8")
        text = "\n".join(self.problems())
        self.assertIn("must not spawn agents", text)
        self.assertIn("invalid name", text)

    def test_missing_agent_and_frontmatter(self):
        (self.root / ".claude/agents/ui-engineer.md").unlink()
        skill = self.root / ".claude/skills/pixel-art-game-studio/SKILL.md"
        skill.write_text("\n" + skill.read_text(encoding="utf-8"), encoding="utf-8")
        text = "\n".join(self.problems())
        self.assertIn("ui-engineer", text)
        self.assertIn("SKILL.md: frontmatter", text)

    def test_broken_link_and_syntax_error(self):
        (self.root / "docs/TESTING.md").write_text("[gone](NOPE.md)\n", encoding="utf-8")
        (self.root / "scripts/bad.py").write_text("def x(:\n", encoding="utf-8")
        text = "\n".join(self.problems())
        self.assertIn("broken link: NOPE.md", text)
        self.assertIn("bad.py: syntax error", text)

    def test_links_in_code_blocks_ignored(self):
        (self.root / "docs/TESTING.md").write_text("```\n[x](missing.md)\n```\n", encoding="utf-8")
        self.assertEqual(self.problems(), [])

    def test_plugin_manifest_must_match_agents_and_version(self):
        manifest = self.root / ".claude-plugin/plugin.json"
        text = manifest.read_text(encoding="utf-8")
        data = json.loads(text)
        data["agents"].remove("./.claude/agents/bug-fixer.md")
        data["version"] = "9.9.9"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        text = "\n".join(self.problems())
        self.assertIn("agents must list exactly", text)
        self.assertIn("differs from pyproject.toml", text)

    def test_badge_rejected(self):
        readme = self.root / "README.md"
        readme.write_text("![ci](https://img.shields.io/badge/ci-passing-green)\n" + readme.read_text(encoding="utf-8"),
                          encoding="utf-8")
        self.assertTrue(any("badges" in p for p in self.problems()))


if __name__ == "__main__":
    unittest.main()
