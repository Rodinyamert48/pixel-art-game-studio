"""Procedural asset generator tests: real PNG output, determinism, validation, overwrite safety."""
import contextlib
import io
import json
import tempfile
import unittest
import zlib
from pathlib import Path

from _util import SKILL_SCRIPTS, load

gen = load(SKILL_SCRIPTS / "generate_sample_asset.py")

SPEC = {
    "name": "test_box", "frame": {"w": 8, "h": 8},
    "palette": {"ink": "#101010", "fill": "#40a040"},
    "base": [["rect", 2, 2, 4, 4, "fill"]],
    "frames": [[], [["shift", 1, 0]]],
    "outline": "ink",
}


def decode_rgba(png: bytes):
    """Minimal decoder for the generator's own output (filter 0, RGBA8, single IDAT)."""
    w = h = 0
    pos, idat = 8, b""
    while pos < len(png):
        length = int.from_bytes(png[pos:pos + 4], "big")
        kind = png[pos + 4:pos + 8]
        data = png[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h = int.from_bytes(data[:4], "big"), int.from_bytes(data[4:8], "big")
        elif kind == b"IDAT":
            idat += data
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = w * 4 + 1
    return w, h, [raw[y * stride + 1:(y + 1) * stride] for y in range(h)]


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


class GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_sheet_meta_and_preview(self):
        result = gen.generate(SPEC, self.out, preview=True)
        self.assertEqual(set(result), {"test_box.png", "test_box.meta.json", "test_box.preview.png"})
        w, h = gen.read_png_size(self.out / "test_box.png")
        self.assertEqual((w, h), (16, 8))
        meta = json.loads((self.out / "test_box.meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["frames"], 2)
        self.assertEqual(meta["bboxes"][0], [1, 1, 6, 6])
        self.assertEqual(meta["clipped_pixels"], [0, 0])

    def test_pixels_are_palette_colors_with_binary_alpha(self):
        gen.generate(SPEC, self.out)
        w, h, rows = decode_rgba((self.out / "test_box.png").read_bytes())
        allowed = {bytes.fromhex("101010ff"), bytes.fromhex("40a040ff"), b"\x00\x00\x00\x00"}
        for row in rows:
            for x in range(w):
                self.assertIn(row[x * 4:x * 4 + 4], allowed)
        self.assertEqual(rows[3][3 * 4:3 * 4 + 4], bytes.fromhex("40a040ff"))
        self.assertEqual(rows[0][0:4], b"\x00\x00\x00\x00")

    def test_deterministic_and_idempotent(self):
        gen.generate(SPEC, self.out)
        first = (self.out / "test_box.png").read_bytes()
        result = gen.generate(SPEC, self.out)
        self.assertEqual(result["test_box.png"], "unchanged")
        self.assertEqual((self.out / "test_box.png").read_bytes(), first)

    def test_refuses_to_overwrite_different_file(self):
        target = self.out / "test_box.png"
        target.write_bytes(b"user art")
        with self.assertRaises(FileExistsError):
            gen.generate(SPEC, self.out)
        self.assertEqual(target.read_bytes(), b"user art")
        self.assertFalse((self.out / "test_box.meta.json").exists(), "no partial output on refusal")
        self.assertEqual(quiet(gen.main, ["--spec", str(self._spec_file()), "--out", str(self.out)]), 2)
        gen.generate(SPEC, self.out, force=True)
        self.assertNotEqual(target.read_bytes(), b"user art")

    def test_clipping_is_reported(self):
        spec = dict(SPEC, name="clip", base=[["rect", 6, 0, 4, 2, "fill"]], frames=[[]])
        meta = gen.generate(spec, self.out) and json.loads((self.out / "clip.meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["clipped_pixels"], [4])

    def test_invalid_specs(self):
        bad = [
            dict(SPEC, name="../escape"),
            dict(SPEC, palette={"ink": "red"}),
            dict(SPEC, base=[["rect", 0, 0, 2, 2, "nocolor"]]),
            dict(SPEC, base=[["spray", 1, 1]]),
            dict(SPEC, base=[["rect", 0, 0, 2]]),
            dict(SPEC, frame={"w": 0, "h": 8}),
            dict(SPEC, outline="missing"),
        ]
        for spec in bad:
            with self.assertRaises(gen.SpecError, msg=str(spec)):
                gen.render(spec)

    def test_demo_cli(self):
        self.assertEqual(quiet(gen.main, ["--demo", "--out", str(self.out), "--preview"]), 0)
        for name in ("demo_hero_walk", "demo_tree_oak", "demo_tile_grass"):
            self.assertTrue((self.out / f"{name}.png").is_file())
            meta = json.loads((self.out / f"{name}.meta.json").read_text(encoding="utf-8"))
            self.assertEqual(sum(meta["clipped_pixels"]), 0, name)

    def _spec_file(self):
        p = self.out / "spec.json"
        p.write_text(json.dumps(SPEC), encoding="utf-8")
        return p


if __name__ == "__main__":
    unittest.main()
