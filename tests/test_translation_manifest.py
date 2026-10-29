"""Translation gate tests: the real docs pass, and the gate rejects common failure modes."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from _util import REPO, load

ct = load(REPO / "scripts" / "check_translations.py")


class RealTranslationsTest(unittest.TestCase):
    def test_real_translations_pass(self):
        self.assertEqual(ct.check(REPO), [])

    def test_manifest_has_exact_language_set(self):
        manifest = json.loads((REPO / "docs/i18n/manifest.json").read_text(encoding="utf-8"))
        codes = [l["code"] for l in manifest["languages"]]
        self.assertEqual(len(codes), 16)
        self.assertEqual(sorted(codes), sorted(ct.REQUIRED_CODES))
        for must in ("en", "de", "zh-CN", "ja", "tr"):
            self.assertIn(must, codes)
        for lang in manifest["languages"]:
            self.assertTrue((REPO / "docs/i18n" / lang["file"]).is_file(), lang["file"])
            self.assertIn("review", lang)


class BrokenTranslationsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(REPO / "docs", self.root / "docs")
        shutil.copy(REPO / "README.md", self.root / "README.md")
        self.i18n = self.root / "docs" / "i18n"

    def tearDown(self):
        self.tmp.cleanup()

    def test_baseline_copy_passes(self):
        self.assertEqual(ct.check(self.root), [])

    def test_english_copied_into_translation_fails(self):
        shutil.copy(self.i18n / "en.md", self.i18n / "es.md")
        text = "\n".join(ct.check(self.root))
        self.assertIn("es (es.md)", text)
        self.assertTrue("untranslated" in text or "identical" in text)

    def test_missing_file_and_section(self):
        (self.i18n / "tr.md").unlink()
        de = self.i18n / "de.md"
        de.write_text(de.read_text(encoding="utf-8").replace("<!-- section: license -->", ""), encoding="utf-8")
        text = "\n".join(ct.check(self.root))
        self.assertIn("tr (tr.md): file missing", text)
        self.assertIn("de (de.md): missing section marker 'license'", text)

    def test_wrong_script_detected(self):
        # Simplified Chinese content in the Japanese file has no kana markers.
        shutil.copy(self.i18n / "zh-CN.md", self.i18n / "ja.md")
        self.assertTrue(any(p.startswith("ja (ja.md)") for p in ct.check(self.root)))

    def test_msa_and_egyptian_are_distinguished(self):
        shutil.copy(self.i18n / "ar.md", self.i18n / "arz.md")
        self.assertTrue(any(p.startswith("arz (arz.md)") and "marker" in p for p in ct.check(self.root)))

    def test_duplicate_language_and_selector(self):
        manifest = json.loads((self.i18n / "manifest.json").read_text(encoding="utf-8"))
        manifest["languages"].append(dict(manifest["languages"][1]))
        (self.i18n / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        readme = self.root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("docs/i18n/pcm.md", "docs/i18n/x.md"), encoding="utf-8")
        text = "\n".join(ct.check(self.root))
        self.assertIn("more than once", text)
        self.assertIn("no link to docs/i18n/pcm.md", text)

    def test_placeholder_rejected(self):
        (self.i18n / "hi.md").write_text("# TODO\n", encoding="utf-8")
        self.assertTrue(any(p.startswith("hi (hi.md)") and "prose characters" in p for p in ct.check(self.root)))


if __name__ == "__main__":
    unittest.main()
