# Art direction reference

Every game gets `design/ART_DIRECTION.md`, owned by the Pixel Artist and approved by the Director. All
asset specs, UI themes, and decor choices must follow it.

## Required fields

| Field | Example default (cozy top-down) |
| --- | --- |
| Logical resolution | 320x180 (scales to 1280x720 at 4x, 1920x1080 at 6x) |
| Tile size | 16x16 |
| Character size | 16x16 body box, 16x24 for taller characters |
| Portrait size | 48x48 |
| Render scale | Integer only; nearest-neighbor; no mipmaps; pixel snap on |
| Palette | 16-32 named colors, hex, grouped by ramp (e.g. `grass_dark`, `grass`, `grass_light`) |
| Outline | 1 px, darkest color of the object's ramp or shared `outline`; none on ground tiles |
| Light | Top-left; highlight on top/left edges, shadow on bottom/right |
| Shading | 2-3 tones per material ramp; dithering only for large surfaces |
| Animation | Walk 4 frames at 8 fps per direction; idle 2 frames at 2 fps; frames in horizontal sheets |
| Proportions | Head about 40% of body height for chibi style; consistent across all NPCs |
| Environment density | Leave the player path readable: at most about 30% of a screen covered by decor |
| UI style | Panels from palette darks with 1 px light inner border; pixel font at 1x logical size |
| Transparency | Fully transparent or fully opaque pixels only (alpha 0 or 255) |
| File naming | `<category>_<name>[_<variant>].png`, snake_case, e.g. `npc_mira_walk.png` |

## Consistency rules

- One palette per game; regions may use sub-palettes (forest leans green ramps, town warm wood).
- Hue-shift ramps: shadows shift toward blue/purple, highlights toward yellow, rather than pure black/white.
- Keep silhouettes distinct: each NPC differs from others in at least two of shape, dominant color,
  accessory.
- Readability first: interactables need contrast with the ground tile they stand on.
- No fractional scaling, no rotation of pixel art at runtime, no smoothing filters.
- Distinct regions need distinct tile sets, not recolors of one tree.

## Procedural construction

Build from primitives (see `workflows/generate-assets.md`): blocks of color (`rect`, `ellipse`), detail
(`px`, `line`), texture (`dither`), symmetry (`mirror_x`), motion (`shift` per frame), and automatic
outline. Compose distinct objects from these rather than one algorithm for everything:

- Characters: head ellipse, body rect, limb rects that change per frame, `shift` 1 px for bobbing.
- Trees: trunk rect, layered ellipses for canopy in three ramp tones, highlight `px` clusters top-left.
- Ground tiles: base fill, sparse `px` noise, never a strong pattern that tiles visibly.
- Buildings: walls rect, roof as stacked `line`s, door and windows as framed rects.
- Icons: 16x16, centered, strong outline, one highlight.

Seeded variation is appropriate for ground noise and decor variants. Keep seeds in the spec so the same
spec always produces the same pixels.

## Review checklist

- [ ] Uses only palette colors (meta lists palette; validator flags off-palette art only through review)
- [ ] Reads clearly at 1x
- [ ] Outline and light direction match other assets
- [ ] Animation frames share a baseline; no jitter except intended bobbing
- [ ] No drawing clipped at the frame edge (validator warns on `clipped_pixels`)
- [ ] Looks original; no resemblance to a specific existing game's characters or tiles

Algorithmic checks verify structure only. Artistic quality needs a human (or image-capable model) look.
