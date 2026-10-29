"""Installer tests. Every test uses temporary directories; the real ~/.claude is never touched."""
import tempfile
import unittest
from pathlib import Path

from _util import REPO, load

install = load(REPO / "scripts" / "install.py")


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.project = self.root / "my-game"
        self.project.mkdir()
        self.claude = self.project / ".claude"
        self.log = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *args, home=None):
        self.log.clear()
        return install.main(list(args), home=home or self.root / "fakehome", out=self.log.append)

    def project_args(self, *extra):
        return ["--scope", "project", "--project-dir", str(self.project), *extra]

    def test_source_contains_only_skill_and_agents(self):
        files = install.source_files()
        self.assertIn("skills/pixel-art-game-studio/SKILL.md", files)
        self.assertEqual(sum(1 for k in files if k.startswith("agents/")), 8)
        self.assertTrue(all(k.startswith(("skills/pixel-art-game-studio/", "agents/")) for k in files))
        self.assertFalse(any("__pycache__" in k for k in files))

    def test_project_install_and_idempotent_rerun(self):
        self.assertEqual(self.run_main(*self.project_args()), 0)
        self.assertTrue((self.claude / "skills/pixel-art-game-studio/SKILL.md").is_file())
        self.assertTrue((self.claude / "agents/qa-tester.md").is_file())
        self.assertTrue((self.claude / install.MANIFEST).is_file())
        self.assertEqual(self.run_main(*self.project_args()), 0)
        self.assertTrue(all(line.strip().startswith("unchanged") for line in self.log[1:-1]), self.log)

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.run_main(*self.project_args("--dry-run")), 0)
        self.assertFalse(self.claude.exists())

    def test_user_scope_uses_given_home(self):
        home = self.root / "home"
        home.mkdir()
        self.assertEqual(self.run_main("--scope", "user", home=home), 0)
        self.assertTrue((home / ".claude/agents/bug-fixer.md").is_file())

    def test_unmanaged_conflict_is_preserved(self):
        agent = self.claude / "agents" / "qa-tester.md"
        agent.parent.mkdir(parents=True)
        agent.write_text("my own agent", encoding="utf-8")
        self.assertEqual(self.run_main(*self.project_args()), 2)
        self.assertEqual(agent.read_text(encoding="utf-8"), "my own agent")
        self.assertFalse((self.claude / "skills").exists(), "nothing may be installed when a conflict exists")
        self.assertEqual(self.run_main(*self.project_args("--update")), 2, "--update must not take over unmanaged files")

    def test_update_backs_up_local_edits(self):
        self.run_main(*self.project_args())
        skill_md = self.claude / "skills/pixel-art-game-studio/SKILL.md"
        skill_md.write_text("locally edited", encoding="utf-8")
        self.assertEqual(self.run_main(*self.project_args()), 2, "plain install must not overwrite")
        self.assertEqual(self.run_main(*self.project_args("--update")), 0)
        self.assertNotEqual(skill_md.read_text(encoding="utf-8"), "locally edited")
        backups = list((self.claude / install.BACKUP_DIR).rglob("SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "locally edited")

    def test_uninstall_keeps_user_content(self):
        self.run_main(*self.project_args())
        mine = self.claude / "agents" / "my-agent.md"
        mine.write_text("keep me", encoding="utf-8")
        notes = self.claude / "skills/pixel-art-game-studio/my-notes.md"
        notes.write_text("keep me too", encoding="utf-8")
        edited = self.claude / "agents/ui-engineer.md"
        edited.write_text("edited", encoding="utf-8")
        self.assertEqual(self.run_main(*self.project_args("--uninstall")), 0)
        self.assertTrue(mine.is_file())
        self.assertTrue(notes.is_file())
        self.assertTrue(edited.is_file(), "locally modified files are kept")
        self.assertFalse((self.claude / "agents/qa-tester.md").exists())
        self.assertFalse((self.claude / "skills/pixel-art-game-studio/SKILL.md").exists())

    def test_uninstall_without_manifest_fails(self):
        self.assertEqual(self.run_main(*self.project_args("--uninstall")), 1)

    def test_invalid_destinations(self):
        afile = self.root / "file.txt"
        afile.write_text("x", encoding="utf-8")
        self.assertEqual(self.run_main("--dest", str(afile)), 1)
        self.assertEqual(self.run_main("--scope", "project", "--project-dir", str(self.root / "missing")), 1)
        self.assertEqual(self.run_main("--scope", "project"), 1)
        self.assertEqual(self.run_main("--dest", str(REPO / ".claude")), 1)

    def test_corrupt_manifest_is_reported_not_overwritten(self):
        self.run_main(*self.project_args())
        manifest = self.claude / install.MANIFEST
        manifest.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.run_main(*self.project_args("--update")), 1)
        self.assertEqual(manifest.read_text(encoding="utf-8"), "{not json")


if __name__ == "__main__":
    unittest.main()
