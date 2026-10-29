# Workflow: Generate pixel-art assets

Owner: `pixel-artist`. Tool: `${CLAUDE_SKILL_DIR}/scripts/generate_sample_asset.py` (Python standard
library only, writes real PNG files).

## 1. Fix the art direction first

`design/ART_DIRECTION.md` must exist and define logical resolution, tile size, scale, palette (hex with
names), outline rule, light direction, animation frame counts and timing. See
[../references/art-direction.md](../references/art-direction.md). Every spec uses the palette names from
that file; a new color is an art-direction change, not a spec tweak.

## 2. Write one spec per asset

Specs live in the game project, e.g. `art/specs/hero_walk.json`. They are the editable source; PNGs are
build output. Format:

```json
{
  "name": "hero_walk",
  "frame": {"w": 16, "h": 16},
  "palette": {"outline": "#1f1a24", "skin": "#f2c29b", "shirt": "#3f7fbf", "pants": "#4a3b5c"},
  "base": [
    ["ellipse", 5, 2, 6, 6, "skin"],
    ["rect", 5, 8, 6, 4, "shirt"]
  ],
  "frames": [
    [["rect", 5, 12, 2, 3, "pants"], ["rect", 9, 12, 2, 3, "pants"]],
    [["rect", 5, 12, 2, 2, "pants"], ["rect", 9, 12, 2, 3, "pants"]]
  ],
  "outline": "outline"
}
```

Operations (coordinates in logical pixels, origin top-left, clipped to the frame):

| Op | Arguments |
| --- | --- |
| `px` | x, y, color |
| `rect` | x, y, w, h, color (filled) |
| `frame_rect` | x, y, w, h, color (1 px border) |
| `line` | x0, y0, x1, y1, color |
| `ellipse` | x, y, w, h, color (filled, inside the box) |
| `dither` | x, y, w, h, color (checkerboard, for texture and soft shading) |
| `mirror_x` | (no args) mirror the left half onto the right half |
| `shift` | dx, dy (move everything drawn so far; use for bobbing) |

`base` is drawn first in every frame, then that frame's ops, then the optional automatic `outline`
(drawn on transparent pixels that touch a filled pixel). `scale` (integer, default 1) enlarges the
output with nearest-neighbor only.

## 3. Generate, preview, inspect

```bash
python "${CLAUDE_SKILL_DIR}/scripts/generate_sample_asset.py" --spec art/specs/hero_walk.json --out assets/sprites --preview
```

Outputs: `hero_walk.png` (horizontal sprite sheet), `hero_walk.meta.json` (frame size, count, palette,
per-frame bounding boxes, clipped pixel counts, SHA-256), and with `--preview` a `hero_walk.preview.png` contact sheet at 8x on
a checkerboard. Same spec in, same bytes out. An existing file with different content is not
overwritten unless `--force` is given.

`--demo --out <dir>` writes three reference assets (walking character, tree, grass tile) to show the
style range of the primitives.

If the Read tool can display images in this environment, open the preview and critique it: silhouette
readable at 1x, palette respected, outline consistent, no stray pixels, animation frames aligned. If
not, state that visual review is still required.

## 4. Integrate and validate

- Import into the engine with nearest-neighbor filtering and no mipmaps (Godot: texture filter
  `Nearest`; MonoGame: `SamplerState.PointClamp`).
- Run `validate_game_project.py`: it checks that each `*.meta.json` matches its PNG (dimensions, frame
  count) and warns about frames where drawing was clipped at the frame edge (`clipped_pixels`).
- Never use downloaded asset packs or traced copies of existing games' art.
