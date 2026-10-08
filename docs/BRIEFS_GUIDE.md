# Writing briefs for Mario Party 3 (how-to for a batch)

The clean ROM renders every image from `games/marioparty3/spec/textures.json` (size, format, a 4x4 colour
grid, a 2-bit alpha outline). That default is a blur. A **brief** replaces it with a picture we draw ourselves:
text re-typeset, faces, icons, digits. Run everything from the repo root (`D:/n64work/marioparty3-cleanroom`).

## Clean-room rule (non-negotiable)
- You may **look** at the retail picture on a dev contact sheet to learn *what it shows* (a red 7, the word
  "START", Toad's head) and roughly where things sit. You then **describe it in your own primitives**.
- Never copy retail pixels: no reading retail image data into a brief, no tracing by script, no palettes or
  coordinates extracted programmatically from retail images, no embedding of retail files. Briefs are hand-written
  shapes, colours picked by eye, and text typed by you.
- Do not write retail images, sheets or ROM data into the repo. Sheets go to `D:/n64work/mp3work/sheets/`.
- Never clone voices / never touch audio here.

## Files
- One module per batch: `games/marioparty3/briefs_<name>.py`, defining `B = {}` and `T = {}`. It is picked up
  automatically by `briefs.py` (do **not** edit `briefs.py`, `mp1_briefs.py`, `faces.py` or other batches' modules).
- Start it with:
  ```python
  import numpy as np
  from cleanroom.gfx import facepaint
  from . import mp1_briefs as M
  from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L
  B = {}
  T = {}
  ```
- Keys are `"<dir>/<file>/<image>"` exactly as printed on the sheets (e.g. `"19/99/p0"`).

## Two kinds of entries
- `T[key] = (text, top_rgb, bottom_rgb, edge_rgb, options)`: one line of stroke text with a vertical gradient
  and a dark edge, fitted to the image. Options: `th` (stroke thickness in px, ~1.0 for 12 px high, ~2 for 24,
  ~3 for 40), `pad`, `slant`, `align` ("left"), `edge_px`. The font has `A-Z a-z 0-9 ! " # % & ' ( ) * + , - . /
  : < = > ? [ ]` and space; for a zero in arcade-style digits use "O". See `typeset()` in `mp1_briefs.py`.
- `B[key] = brief(base_rgb, *ops)`: primitives in normalised coordinates (x right, y down, 0..1), drawn in order.
  Helpers: `E((cx, cy), (rx, ry), c=rgb, rot=deg)` ellipse, `P([(x, y), ...], rgb)` polygon,
  `L([(x, y), ...], width, rgb)` polyline, `R(x0, y0, x1, y1, rgb)` rectangle, and raw dicts for
  `{"arc": [cx, cy, rx, ry, a0, a1], "w": w, "c": rgb}` (degrees, 90 = down), `{"ring": [...], "w", "c"}`,
  `{"sphere": [cx, cy, rx, ry], "c"}`, `{"hl": [cx, cy, r]}`, `{"glow": [...], "c"}`, `{"clip": [cx, cy, rx, ry]}` /
  `{"clip": None}`, `{"outline": px, "c": rgb}` (darkens the kept alpha edge). Full list: header of
  `cleanroom/gfx/facepaint.py`. The kept alpha outline (silhouette) is applied automatically when the image has one.
- `B[key]` may also be a function `(w, h, d, alpha) -> RGBA float/uint8 array (h, w, 4)` for anything else
  (`d` = the spec entry, `alpha` = kept alpha as uint8 (h, w) or None). Useful helpers in `mp1_briefs.py`:
  `over(brief, "TEXT", top, bottom, edge, box=(x0, y0, x1, y1), th=...)` (text laid over a brief),
  `cutout(brief)` (our own silhouette: everything that differs from the base colour is opaque),
  `M._PORTRAIT["mario"|"luigi"|"peach"|"yoshi"|"wario"|"dk"]` (drawn busts on a dark backdrop),
  `M._SPACES`, `M._disc`, `M._checker`, `M._BOWSER_FACE` (board-space signs), `star_pts`.
  `games/marioparty3/faces.py` shows parametric drawing (one function per character, many expressions): prefer
  **functions and loops** over long hand-written tables when a directory repeats a theme (digits in 5 colours, the
  same icon in 4 sizes, 8 players).

## Looking (one sheet per question; images cost tokens)
- `PYTHONPATH=. python D:/n64work/mp3work/review.py <out.png> <dir>[/<lo>-<hi>][,<dir>/...] [cell px] [--todo] [--retail]`
  writes retail | ours pairs with their keys. `--todo` = only images without a brief, `--retail` = retail only.
  Use a cell of 40-64 px so a few hundred images fit one sheet; zoom (cell 120+) only on a handful.
- After writing briefs, render the same selection again **without** `--todo` and compare once. Fix what is
  unreadable or wrong; do not polish beyond "recognisable and readable".
- Quick sanity: `python -c "from games.marioparty3 import briefs; print(len(briefs.B), len(briefs.T))"`.

## What matters (in this order)
1. Text and digits inside pictures: must read correctly at game size. Same word, similar colours.
2. Faces / character heads / icons: recognisable (cap colour, moustache, shell, mushroom spots ...).
3. Meaningful signs (arrows, ?, !, stars, coins, hearts, buttons).
4. Leave plain surfaces, gradients, clouds, smoke, sparkles and repeating ground textures alone: the default
   rendering is fine for them. Leave Japanese text alone (unused in the USA game).

## Report back (short)
Module name, number of B/T entries, which key ranges are done, which you left on purpose (and why), anything odd.
