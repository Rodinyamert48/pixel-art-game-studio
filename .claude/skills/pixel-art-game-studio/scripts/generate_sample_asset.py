#!/usr/bin/env python3
"""Deterministic procedural pixel-art generator (Python standard library only).

Reads a JSON asset spec (see workflows/generate-assets.md) and writes:
  <name>.png            horizontal sprite sheet, RGBA, alpha 0 or 255 only
  <name>.meta.json      frame size, frame count, scale, palette, bounding boxes, clipped pixels, sha256
  <name>.preview.png    (with --preview) 8x contact sheet on a checkerboard

Usage:
  python generate_sample_asset.py --spec art/specs/hero.json --out assets/sprites [--preview] [--force]
  python generate_sample_asset.py --demo --out /tmp/demo [--preview]

Exit codes: 0 ok, 1 invalid spec/arguments, 2 refused to overwrite a different existing file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

GENERATOR_ID = "pixel-art-game-studio/generate_sample_asset.py v1"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]{0,63}$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_FRAME = 256
MAX_FRAMES = 64
PREVIEW_SCALE = 8


class SpecError(ValueError):
    pass


# ---------------------------------------------------------------- PNG output

def encode_png(width: int, height: int, rgba_rows: list[bytes]) -> bytes:
    """Encode RGBA rows as a PNG with no metadata chunks, so output is byte-for-byte stable."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + row for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        head = fh.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG file")
    return struct.unpack(">II", head[16:24])


# ---------------------------------------------------------------- drawing

class Frame:
    """A grid of palette names (None = transparent)."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.grid: list[list[str | None]] = [[None] * w for _ in range(h)]
        self.clipped = 0  # pixels drawn outside the frame, reported in meta

    def set(self, x: int, y: int, color: str) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y][x] = color
        else:
            self.clipped += 1

    px = set  # the "px" spec operation

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def frame_rect(self, x, y, w, h, color):
        for xx in range(x, x + w):
            self.set(xx, y, color)
            self.set(xx, y + h - 1, color)
        for yy in range(y, y + h):
            self.set(x, yy, color)
            self.set(x + w - 1, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, x, y, w, h, color):
        # Pixel centers inside the ellipse inscribed in the w x h box.
        cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                nx, ny = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    self.set(xx, yy, color)

    def dither(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + yy) % 2 == 0:
                    self.set(xx, yy, color)

    def mirror_x(self):
        for row in self.grid:
            for xx in range(self.w // 2):
                row[self.w - 1 - xx] = row[xx]

    def shift(self, dx, dy):
        old = self.grid
        self.grid = [[None] * self.w for _ in range(self.h)]
        for yy, row in enumerate(old):
            for xx, c in enumerate(row):
                if c is not None:
                    self.set(xx + dx, yy + dy, c)

    def outline(self, color):
        filled = {(x, y) for y in range(self.h) for x in range(self.w) if self.grid[y][x] is not None}
        for x, y in sorted(filled):
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < self.w and 0 <= ny < self.h and (nx, ny) not in filled:
                    self.grid[ny][nx] = color

    def bbox(self):
        xs = [x for y in range(self.h) for x in range(self.w) if self.grid[y][x] is not None]
        ys = [y for y in range(self.h) for x in range(self.w) if self.grid[y][x] is not None]
        return [min(xs), min(ys), max(xs), max(ys)] if xs else None


OPS = {  # name -> (number of int args, takes color)
    "px": (2, True), "rect": (4, True), "frame_rect": (4, True), "line": (4, True),
    "ellipse": (4, True), "dither": (4, True), "mirror_x": (0, False), "shift": (2, False),
}


def apply_op(frame: Frame, op: list, palette: dict, where: str) -> None:
    if not isinstance(op, list) or not op or op[0] not in OPS:
        raise SpecError(f"{where}: unknown operation {op!r}; expected one of {sorted(OPS)}")
    name, args = op[0], op[1:]
    nints, has_color = OPS[name]
    if len(args) != nints + (1 if has_color else 0):
        raise SpecError(f"{where}: '{name}' takes {nints} numbers" + (" and a color" if has_color else ""))
    ints = args[:nints]
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in ints):
        raise SpecError(f"{where}: '{name}' coordinates must be integers")
    if has_color:
        color = args[-1]
        if color not in palette:
            raise SpecError(f"{where}: color '{color}' is not in the palette")
        if name in ("rect", "frame_rect", "ellipse", "dither") and (ints[2] < 1 or ints[3] < 1):
            raise SpecError(f"{where}: '{name}' width and height must be >= 1")
        getattr(frame, name)(*ints, color)
    else:
        getattr(frame, name)(*ints)


# ---------------------------------------------------------------- spec handling

def validate_spec(spec: dict) -> None:
    if not isinstance(spec, dict):
        raise SpecError("spec must be a JSON object")
    name = spec.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name):
        raise SpecError("'name' must be lowercase letters, digits, '_' or '-' (max 64 chars)")
    fr = spec.get("frame", {})
    w, h = fr.get("w"), fr.get("h")
    if not all(isinstance(v, int) and 1 <= v <= MAX_FRAME for v in (w, h)):
        raise SpecError(f"'frame.w' and 'frame.h' must be integers 1..{MAX_FRAME}")
    palette = spec.get("palette")
    if not isinstance(palette, dict) or not palette:
        raise SpecError("'palette' must be a non-empty object of name -> #rrggbb")
    for k, v in palette.items():
        if not isinstance(v, str) or not HEX_RE.match(v):
            raise SpecError(f"palette color '{k}' must be #rrggbb, got {v!r}")
    frames = spec.get("frames", [[]])
    if not isinstance(frames, list) or not 1 <= len(frames) <= MAX_FRAMES:
        raise SpecError(f"'frames' must be a list of 1..{MAX_FRAMES} op lists")
    if not isinstance(spec.get("base", []), list):
        raise SpecError("'base' must be a list of operations")
    if "outline" in spec and spec["outline"] not in palette:
        raise SpecError(f"outline color '{spec['outline']}' is not in the palette")
    scale = spec.get("scale", 1)
    if not isinstance(scale, int) or not 1 <= scale <= 16:
        raise SpecError("'scale' must be an integer 1..16")


def render(spec: dict) -> list[Frame]:
    validate_spec(spec)
    w, h, palette = spec["frame"]["w"], spec["frame"]["h"], spec["palette"]
    frames = []
    for i, ops in enumerate(spec.get("frames", [[]])):
        if not isinstance(ops, list):
            raise SpecError(f"frames[{i}] must be a list of operations")
        f = Frame(w, h)
        for j, op in enumerate(spec.get("base", [])):
            apply_op(f, op, palette, f"base[{j}]")
        for j, op in enumerate(ops):
            apply_op(f, op, palette, f"frames[{i}][{j}]")
        if "outline" in spec:
            f.outline(spec["outline"])
        frames.append(f)
    return frames


def _rgba(hex_color: str) -> bytes:
    return bytes.fromhex(hex_color[1:]) + b"\xff"


def sheet_png(frames: list[Frame], palette: dict, scale: int, checker: bool = False) -> bytes:
    fw, fh = frames[0].w, frames[0].h
    gap = 1 if checker else 0  # preview separates frames with a 1-cell gap
    width = (fw * len(frames) + gap * (len(frames) - 1)) * scale
    height = fh * scale
    colors = {k: _rgba(v) for k, v in palette.items()}
    clear, light, dark = b"\x00\x00\x00\x00", b"\xcc\xcc\xcc\xff", b"\x99\x99\x99\xff"
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            cell_x, ly = x // scale, y // scale
            fi, lx = divmod(cell_x, fw + gap)
            c = frames[fi].grid[ly][lx] if lx < fw else None
            if c is not None:
                row += colors[c]
            elif checker:
                row += light if ((x // 4) + (y // 4)) % 2 else dark
            else:
                row += clear
        rows.append(bytes(row))
    return encode_png(width, height, rows)


def write_if_allowed(path: Path, data: bytes, force: bool) -> str:
    """Write unless an existing different file would be replaced without --force."""
    if path.exists():
        if path.read_bytes() == data:
            return "unchanged"
        if not force:
            raise FileExistsError(str(path))
    path.write_bytes(data)
    return "written"


def generate(spec: dict, out_dir: Path, preview: bool = False, force: bool = False) -> dict:
    frames = render(spec)
    name, palette, scale = spec["name"], spec["palette"], spec.get("scale", 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = sheet_png(frames, palette, scale)
    meta = {
        "name": name,
        "generator": GENERATOR_ID,
        "frame": {"w": frames[0].w, "h": frames[0].h},
        "frames": len(frames),
        "scale": scale,
        "palette": palette,
        "bboxes": [f.bbox() for f in frames],
        "clipped_pixels": [f.clipped for f in frames],
        "sha256": hashlib.sha256(png).hexdigest(),
    }
    outputs = {name + ".png": png,
               name + ".meta.json": (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode()}
    if preview:
        outputs[name + ".preview.png"] = sheet_png(frames, palette, PREVIEW_SCALE, checker=True)
    # Check every target first so a refusal leaves no partial output.
    for fname, data in outputs.items():
        p = out_dir / fname
        if p.exists() and not force and p.read_bytes() != data:
            raise FileExistsError(str(p))
    return {fname: write_if_allowed(out_dir / fname, data, force) for fname, data in outputs.items()}


# ---------------------------------------------------------------- demo specs

DEMO_PALETTE = {
    "outline": "#1f1a24", "skin": "#f2c29b", "hair": "#6b3f2a", "shirt": "#3f7fbf",
    "shirt_dark": "#2c5a8c", "pants": "#4a3b5c", "trunk": "#7a4e2d", "leaf_dark": "#2f6b3a",
    "leaf": "#4f9a48", "leaf_light": "#8cc65a", "grass": "#5fa84f", "grass_dark": "#4a8c40",
    "flower": "#f4e07a",
}

DEMO_SPECS = [
    {
        "name": "demo_hero_walk", "frame": {"w": 16, "h": 16}, "palette": DEMO_PALETTE, "outline": "outline",
        "base": [["ellipse", 4, 2, 8, 6, "skin"], ["rect", 4, 2, 8, 2, "hair"], ["px", 6, 5, "outline"],
                 ["px", 9, 5, "outline"], ["rect", 5, 8, 6, 4, "shirt"], ["rect", 5, 11, 6, 1, "shirt_dark"]],
        "frames": [
            [["rect", 5, 12, 2, 3, "pants"], ["rect", 9, 12, 2, 3, "pants"]],
            [["rect", 5, 12, 2, 2, "pants"], ["rect", 9, 12, 2, 3, "pants"], ["shift", 0, -1]],
            [["rect", 5, 12, 2, 3, "pants"], ["rect", 9, 12, 2, 3, "pants"]],
            [["rect", 5, 12, 2, 3, "pants"], ["rect", 9, 12, 2, 2, "pants"], ["shift", 0, -1]],
        ],
    },
    {
        "name": "demo_tree_oak", "frame": {"w": 16, "h": 24}, "palette": DEMO_PALETTE, "outline": "outline",
        "base": [["rect", 6, 15, 4, 7, "trunk"], ["ellipse", 1, 2, 14, 14, "leaf_dark"],
                 ["ellipse", 2, 2, 11, 11, "leaf"], ["ellipse", 3, 3, 6, 5, "leaf_light"],
                 ["dither", 4, 9, 8, 4, "leaf_dark"]],
        "frames": [[]],
    },
    {
        "name": "demo_tile_grass", "frame": {"w": 16, "h": 16}, "palette": DEMO_PALETTE,
        "base": [["rect", 0, 0, 16, 16, "grass"], ["px", 2, 3, "grass_dark"], ["px", 11, 2, "grass_dark"],
                 ["px", 6, 9, "grass_dark"], ["px", 13, 12, "grass_dark"], ["px", 4, 13, "flower"],
                 ["px", 9, 6, "grass_dark"], ["px", 1, 10, "grass_dark"]],
        "frames": [[]],
    },
]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")  # Windows consoles may not encode every script
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--spec", type=Path, help="JSON asset spec")
    src.add_argument("--demo", action="store_true", help="generate the built-in demo assets")
    ap.add_argument("--out", type=Path, required=True, help="output directory (created if missing)")
    ap.add_argument("--preview", action="store_true", help="also write an 8x preview contact sheet")
    ap.add_argument("--force", action="store_true", help="replace existing files whose content differs")
    args = ap.parse_args(argv)

    try:
        specs = DEMO_SPECS if args.demo else [json.loads(args.spec.read_text(encoding="utf-8"))]
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read spec: {exc}", file=sys.stderr)
        return 1
    if args.out.exists() and not args.out.is_dir():
        print(f"error: --out {args.out} exists and is not a directory", file=sys.stderr)
        return 1
    for spec in specs:
        try:
            result = generate(spec, args.out, preview=args.preview, force=args.force)
        except SpecError as exc:
            print(f"error: invalid spec: {exc}", file=sys.stderr)
            return 1
        except FileExistsError as exc:
            print(f"error: {exc} exists with different content; rerun with --force to replace it", file=sys.stderr)
            return 2
        for fname, status in result.items():
            print(f"{status:9} {args.out / fname}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
