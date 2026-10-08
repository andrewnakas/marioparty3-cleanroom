"""Briefs for MainFS dir 19 (board / menu UI), files 0-300: digits, word strips, space icons, option icons.

Everything here is typed / drawn by hand from what the pictures show; nothing is derived from retail pixels.
Left for the shared icon pass: character and NPC heads (19/2-3, 54-61, 179-206, 216-237, 263-270, 286, 294-300).
"""
import math

import numpy as np
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L

B = {}
T = {}
D = 19
PALE = [250, 246, 204]
NAVY = [10, 30, 120]


def _k(f, i=0):
    return f"{D}/{f}/p{i}"


def _fl(ops):
    out = []
    for o in ops:
        if isinstance(o, (list, tuple)) and not isinstance(o, dict):
            out += _fl(o)
        else:
            out.append(o)
    return out


def bf(base, *ops):
    return brief(base, *_fl(ops))


def words(base, *items, opaque=False):
    """Painter: optional brief backdrop plus several typeset words (text, box, (top, bottom, edge), options)."""
    def fn(w, h, d, alpha):
        if base is None:
            out = np.zeros((h, w, 4), np.float32)
        else:
            out = np.asarray(facepaint.render(base, w, h, alpha=alpha), np.float32).copy()
        for text, box, cols, opt in items:
            x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(round(box[2] * w)), int(round(box[3] * h))
            g = typeset(x1 - x0, y1 - y0, text, *cols, **opt)
            if opt.get("flip"):
                g = g[::-1]
            a = g[..., 3:] / 255
            out[y0:y1, x0:x1, :3] = out[y0:y1, x0:x1, :3] * (1 - a) + g[..., :3] * a
            if base is None:
                out[y0:y1, x0:x1, 3] = np.maximum(out[y0:y1, x0:x1, 3], g[..., 3])
        if base is None:
            out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
        elif opaque:
            out[..., 3] = 255
        return out
    return fn


def sign(base, text, cols, box=(0.2, 0.14, 0.8, 0.86), k=0.075, **opt):
    """A brief with one glyph over it; stroke thickness follows the picture size."""
    def fn(w, h, d, alpha):
        o = dict(opt)
        o.setdefault("pad", 0 if h < 24 else 1)
        return over(base, text, *cols, box, th=max(0.8, h * k), **o)(w, h, d, alpha)
    return fn


def frame(c, t=0.06, tx=None):
    tx = t if tx is None else tx
    return [R(0, 0, 1, t, c), R(0, 1 - t, 1, 1, c), R(0, 0, tx, 1, c), R(1 - tx, 0, 1, 1, c)]


# ------------------------------------------------------------------ digit sets and counters
_DIG = ["O", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
_ORANGE_D = ([255, 232, 70], [250, 120, 0], [150, 30, 0])
_BLUE_D = ([130, 225, 255], [20, 90, 240], [10, 20, 120])
for _i, _c in enumerate(_DIG):
    T[_k(119, _i)] = (_c, *_ORANGE_D, {"th": 1.3, "pad": 1})
    T[_k(120, _i)] = (_c, *_BLUE_D, {"th": 1.3, "pad": 1})
for _i, _c in enumerate(_DIG + ["x", "+", "-"]):
    T[_k(207, _i)] = (_c, W, [225, 230, 240], K, {"th": 0.8, "pad": 1})
    T[_k(208, _i)] = (_c, [255, 150, 70], [236, 80, 20], [80, 20, 0], {"th": 0.8, "pad": 1})
T[_k(209)] = ("COM", W, [225, 230, 240], K, {"th": 0.8, "pad": 1})
T[_k(121)] = ("1P", [255, 70, 40], [200, 0, 0], W, {"th": 1.5, "slant": 0.2, "pad": 2})
T[_k(122)] = ("2P", [80, 150, 255], [10, 40, 220], W, {"th": 1.5, "slant": 0.2, "pad": 2})
for _i in range(4):
    T[_k(158 + _i)] = (str(_i + 1), [255, 70, 90], [230, 30, 60], [250, 150, 40], {"th": 3.4, "pad": 3, "edge_px": 1.5})
_PINK_N = ([255, 200, 235], [240, 90, 170], [30, 0, 130])
for _i, (_t, _cols) in enumerate((("O", ([140, 255, 225], [40, 220, 150], [30, 0, 130])), ("1O", _PINK_N), ("2O", _PINK_N),
                                  ("3O", _PINK_N), ("5O", ([255, 250, 60], [250, 170, 0], [50, 0, 130])))):
    T[_k(276, _i)] = (_t, *_cols, {"th": 3.2 if len(_t) == 1 else 2.2, "pad": 3, "edge_px": 2.0})


def _mask_digit(ch):
    """Intensity mask: a white field with the digit cut out dark (19/138)."""
    def fn(w, h, d, alpha):
        g = _real_typeset(w, h, ch, W, W, W, th=1.8, pad=2, edge_px=0.0)
        v = 255 - np.clip(g[..., 3], 0, 255)
        return np.dstack([v, v, v, v])
    return fn


for _i, _c in enumerate(_DIG):
    B[_k(138, _i)] = _mask_digit(_c)


def _rank(i, th_big, th_small):
    big = [([255, 250, 150], [250, 190, 0]), ([230, 250, 255], [110, 190, 240]), ([255, 255, 255], [236, 60, 40]),
           ([150, 230, 110], [40, 150, 40])][i]
    return words(None, (str(i + 1), (0, 0, 0.72, 1), (*big, K), {"th": th_big, "pad": 1}),
                 (["st", "nd", "rd", "th"][i], (0.42, 0.42, 1, 1), ([255, 190, 60], [250, 110, 0], K), {"th": th_small, "pad": 0}))


for _i in range(4):
    B[_k(272, _i)] = _rank(_i, 2.0, 0.9)

_RANKC = ([214, 50, 40], [214, 180, 50], [70, 170, 60], [60, 110, 220])
B[_k(49)] = words(
    bf([40, 30, 30], *[[R(0.04, _i / 4 + 0.012, 0.96, (_i + 1) / 4 - 0.012, _RANKC[_i])] for _i in range(4)]),
    *[(_t, (0.1, _i / 4 + 0.03, 0.9, (_i + 1) / 4 - 0.03), (_a, _b, K), {"th": 2.4, "pad": 2})
      for _i, (_t, _a, _b) in enumerate((("1st", [255, 250, 150], [250, 190, 0]), ("2nd", W, [190, 200, 220]),
                                         ("3rd", [255, 190, 110], [220, 110, 30]), ("4th", [200, 220, 255], [120, 150, 220])))])


# numbered tiles (the pictures between the numbers are a spinning swirl)
def _tile(rim, face, text, cols, flip=False, star=None, th=2.3):
    b = bf(rim, R(0.1, 0.1, 0.9, 0.9, face), [P(star_pts(0.5, 0.55, 0.36), star)] if star else [])
    return words(b, (text, (0.12, 0.12, 0.88, 0.88), cols, {"th": th, "pad": 1, "flip": flip}), opaque=True)


def _swirl(rim, face, ink, rot):
    arcs = [{"arc": [0.5, 0.5, 0.2, 0.2, rot + a, rot + a + 115], "w": 0.12, "c": ink} for a in (0, 120, 240)]
    return bf(rim, R(0.1, 0.1, 0.9, 0.9, face), E((0.5, 0.5), (0.13, 0.13), c=ink), arcs)


_real_typeset = typeset


def typeset(w, h, text, top, bottom, edge, flip=False, **opt):      # noqa: F811  (accepts the "flip" option of words())
    return _real_typeset(w, h, text, top, bottom, edge, **opt)


for _f, _rim, _face, _ink, _cols in (
        (253, [20, 50, 140], [150, 180, 240], [10, 30, 90], ([150, 30, 150], [100, 0, 110], [60, 0, 70])),
        (256, [170, 10, 20], [250, 190, 200], [120, 0, 10], ([30, 130, 60], [0, 80, 40], [0, 40, 20]))):
    _n = 0
    for _i in range(10):
        if _i % 3 == 2:
            _n += 1
            B[_k(_f, _i)] = _tile(_rim, _face, str(_n), _cols)
        else:
            B[_k(_f, _i)] = _swirl(_rim, _face, _ink, _i * 50)
for _i in range(10):
    B[_k(254, _i)] = _tile([200, 160, 40], [250, 240, 170], "1O" if _i == 9 else str(_i + 1),
                           ([70, 170, 255], [10, 60, 220], [10, 20, 110]), star=[232, 206, 120])
    # the countdown tiles 10..1 are stored upside down
    B[_k(255, _i)] = _tile([20, 30, 130], [140, 130, 230], "1O" if _i == 0 else str(10 - _i),
                           ([255, 220, 40], [250, 130, 0], [130, 50, 0]), flip=True, star=[120, 110, 215])


# ------------------------------------------------------------------ word strips
def _strip(f, text, top, bottom, edge=K, **opt):
    T[_k(f)] = (text, top, bottom, edge, opt)


_BOARD = {
    "CHILLY WATERS": ([255, 255, 255], [70, 130, 250], [10, 20, 110]),
    "DEEP BLOOBER SEA": ([130, 240, 255], [20, 90, 230], [10, 10, 100]),
    "SPINY DESERT": ([255, 230, 60], [240, 70, 10], [110, 10, 0]),
    "WOODY WOODS": ([240, 255, 80], [30, 180, 30], [0, 60, 10]),
    "CREEPY CAVERN": ([120, 230, 255], [120, 60, 220], [20, 10, 90]),
    "WALUIGI'S ISLAND": ([230, 190, 255], [130, 40, 220], [40, 0, 90]),
}
for _i, (_t, _c) in enumerate(_BOARD.items()):
    _strip(28 + _i, _t, *_c, th=2.8, pad=2, edge_px=1.5)
_DUEL = {
    "GATE GUY": ([170, 130, 255], [70, 20, 200], [20, 0, 80]),
    "ARROWHEAD": ([150, 255, 90], [0, 160, 30], [0, 50, 10]),
    "PIPESQUEAK": ([255, 240, 60], [240, 90, 10], [110, 10, 0]),
    "BLOWHARD": ([255, 190, 230], [230, 30, 140], [90, 0, 50]),
    "MR. MOVER": ([255, 100, 50], [190, 0, 0], [70, 0, 0]),
    "BACKTRACK": ([140, 245, 255], [0, 120, 230], [0, 30, 100]),
}
for _i, (_t, _c) in enumerate(_DUEL.items()):
    _strip(40 + _i, _t, *_c, th=3.0, pad=2, edge_px=1.5)
    _strip(171 + _i, _t, *_c, th=1.3, pad=1)

_GREEN = ([150, 255, 90], [20, 190, 40], [10, 60, 20])
_MODES = ["LITE PLAY", "STANDARD PLAY", "FULL PLAY", "CUSTOM PLAY"]
for _i, _t in enumerate(_MODES):
    _strip(114 + _i, _t, *_GREEN, th=1.7, pad=2)
_strip(124, "STORY PLAY", *_GREEN, th=1.7, pad=2)


def _plate(text, box=(0.04, 0.1, 0.96, 0.9), th=1.6, extra=None):
    """Intensity plate: white frame, grey fill, white lettering."""
    def fn(w, h, d, alpha):
        v = np.full((h, w), 96, np.float32)
        v[:2] = v[-2:] = 255
        v[:, :2] = v[:, -2:] = 255
        x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(round(box[2] * w)), int(round(box[3] * h))
        g = _real_typeset(x1 - x0, y1 - y0, text, W, W, W, th=th, pad=1, edge_px=0.0)
        v[y0:y1, x0:x1] = np.maximum(v[y0:y1, x0:x1], np.clip(g[..., 3], 0, 255))
        if extra:
            extra(v, w, h)
        return np.dstack([v, v, v, v])
    return fn


def _turn_slots(v, w, h):
    for a, b in ((0.47, 0.64), (0.74, 0.91)):       # two number windows and a slash between them
        v[int(h * 0.22):int(h * 0.78), int(w * a):int(w * b)] = 40
    for y in range(int(h * 0.2), int(h * 0.8)):
        x = int(w * 0.72 - (y - h * 0.2) / (h * 0.6) * w * 0.06)
        v[y, x:x + 2] = 255


for _i, _t in enumerate(_MODES):
    B[_k(132 + _i)] = _plate(_t)
B[_k(139)] = _plate("STORY PLAY")
B[_k(136)] = _plate("TURN", box=(0.05, 0.12, 0.45, 0.88), th=2.4, extra=_turn_slots)
B[_k(137)] = _plate("INFINITE TURNS", box=(0.04, 0.12, 0.96, 0.88), th=2.4)

_strip(162, "COM", [150, 240, 110], [20, 140, 40], K, th=1.5)
_strip(163, "EASY", [220, 245, 255], [40, 120, 230], K, th=1.7)
_strip(164, "NORMAL", [245, 255, 60], [90, 190, 20], K, th=1.5)
_strip(165, "HARD", [255, 225, 40], [240, 60, 0], K, th=1.7)
B[_k(166)] = words(None, ("SUPER", (0, 0, 1, 0.52), ([255, 190, 40], [250, 100, 0], K), {"th": 1.3, "pad": 1}),
                   ("HARD", (0, 0.48, 1, 1), ([255, 140, 20], [230, 30, 0], K), {"th": 1.3, "pad": 1}))
_strip(247, "ACTION TIME", [255, 70, 40], [80, 230, 60], K, th=2.6, slant=0.25, pad=3)
_strip(248, "READY", [255, 255, 100], [60, 220, 90], [20, 20, 120], th=1.7)
_strip(249, "GOOD", [110, 235, 255], [20, 60, 240], [10, 10, 90], th=1.7)
_strip(250, "MISS", [255, 100, 60], [220, 20, 120], [60, 0, 40], th=1.7)
_strip(257, "POWER UP!", [255, 90, 60], [220, 10, 10], W, th=2.2, pad=2)
_strip(258, "POWER DOWN!", [60, 200, 180], [0, 110, 120], W, th=2.2, pad=2)
B[_k(259)] = over(bf([255, 222, 40], {"outline": 1, "c": [30, 40, 200]}), "HAPPENING", [255, 170, 40], [240, 90, 0], [30, 30, 150],
                  (0.06, 0.14, 0.94, 0.86), th=2.6, pad=2)
_strip(291, "ATTACK!", [255, 150, 0], [255, 235, 60], [30, 30, 200], th=2.2, slant=0.35, pad=3)
for _i, _c in enumerate("BATLE!"):
    T[_k(289, _i)] = (_c, [255, 150, 0], [255, 235, 60], [30, 30, 200], {"th": 3.4, "slant": 0.4, "pad": 5})
B[_k(287)] = over(bf([150, 195, 250]), "ROULETTE", [90, 170, 255], [10, 60, 220], W, (0.02, 0.06, 0.98, 0.94), th=2.8, pad=3, edge_px=1.5)
B[_k(288)] = over(bf([250, 160, 170]), "ROULETTE", [255, 100, 80], [210, 10, 20], W, (0.02, 0.06, 0.98, 0.94), th=2.8, pad=3, edge_px=1.5)
B[_k(70)] = over(bf([90, 220, 250], [R(x / 20, 0, x / 20 + 0.02, 1, [70, 200, 235]) for x in range(20)]), "RESULTS",
                 [255, 130, 210], [230, 30, 150], [90, 0, 90], (0.1, 0.06, 0.9, 0.94), th=2.6, pad=2)

# "<player> START" (two lines)
_NAMES = (("MARIO", ([255, 90, 60], [210, 10, 10], W), ([120, 130, 255], [50, 40, 210], W)),
          ("LUIGI", ([90, 170, 255], [20, 60, 220], W), None), ("PEACH", ([255, 150, 210], [240, 50, 150], W), None),
          ("YOSHI", ([240, 255, 80], [40, 190, 40], W), None), ("WARIO", ([200, 140, 255], [120, 40, 220], W), None),
          ("DK", ([255, 190, 60], [240, 100, 0], W), None), ("WALUIGI", ([200, 190, 230], [90, 70, 150], W), None),
          ("DAISY", ([255, 240, 80], [250, 150, 0], W), None))
for _i, (_t, _c, _c2) in enumerate(_NAMES):
    B[_k(238 + _i)] = words(None, (_t, (0, 0, 1, 0.53), _c, {"th": 3.6, "pad": 3, "edge_px": 1.5}),
                            ("START", (0, 0.47, 1, 1), _c2 or _c, {"th": 3.6, "pad": 3, "edge_px": 1.5}))

# WIN / LOSE / DRAW on a red (1st set) or blue (2nd set) panel
_PANEL = {"red": [204, 50, 46], "yel": [226, 190, 50], "grn": [70, 180, 60], "blu": [50, 100, 214]}


def _panel(c):
    dark = [int(v * 0.72) for v in c]
    return [R(0, 0, 1, 0.07, [120, 80, 40]), frame([20, 20, 30], 0.03, 0.02)] + [R(x / 16, 0.08, x / 16 + 0.02, 1, dark) for x in range(1, 16)]


for _f, _c in ((99, "red"), (102, "blu")):
    for _i, (_t, _cols) in enumerate((("WIN", ([255, 250, 120], [250, 140, 0], [110, 20, 0])),
                                      ("LOSE", ([255, 255, 255], [40, 190, 150], [0, 70, 60])),
                                      ("DRAW", ([255, 170, 230], [230, 30, 170], [80, 0, 80])))):
        B[_k(_f + _i)] = over(bf(_PANEL[_c], _panel(_PANEL[_c])), _t, *_cols, (0.06, 0.16, 0.94, 0.9), th=2.3, pad=3, edge_px=1.5)

# board banners with the name as a caption (150x50); 131 (everyone) has no caption
_CAP = {"th": 1.8, "pad": 1}
B[_k(125)] = words(bf([150, 205, 250], frame([40, 200, 190], 0.08, 0.03)),
                   ("CHILLY", (0.1, 0.1, 0.58, 0.52), _BOARD["CHILLY WATERS"], _CAP), ("WATERS", (0.1, 0.5, 0.6, 0.92), _BOARD["CHILLY WATERS"], _CAP))
B[_k(126)] = words(bf([40, 100, 210], frame([20, 40, 200], 0.08, 0.03)),
                   ("DEEP BLOOBER SEA", (0.02, 0.5, 0.98, 0.96), ([255, 255, 255], [130, 220, 255], [10, 10, 100]), _CAP))
B[_k(127)] = words(bf([226, 120, 40], frame([230, 60, 20], 0.08, 0.03), R(0.03, 0.1, 0.56, 0.9, [250, 220, 60])),
                   ("SPINY", (0.08, 0.1, 0.5, 0.52), ([255, 90, 50], [210, 20, 10], W), _CAP), ("DESERT", (0.06, 0.5, 0.56, 0.92), ([255, 90, 50], [210, 20, 10], W), _CAP))
B[_k(128)] = words(bf([70, 160, 60], frame([200, 220, 40], 0.08, 0.03)),
                   ("WOODY WOODS", (0.08, 0.06, 0.96, 0.52), (W, [220, 250, 200], [0, 70, 10]), _CAP))
B[_k(129)] = words(bf([90, 84, 140], frame([220, 220, 40], 0.08, 0.03)),
                   ("CREEPY", (0.04, 0.1, 0.5, 0.52), _BOARD["CREEPY CAVERN"], _CAP), ("CAVERN", (0.04, 0.5, 0.52, 0.92), _BOARD["CREEPY CAVERN"], _CAP))
B[_k(130)] = words(bf([110, 50, 170], frame([90, 40, 230], 0.08, 0.03)),
                   ("WALUIGI'S", (0.03, 0.1, 0.6, 0.52), ([255, 240, 90], [250, 170, 0], [50, 0, 100]), _CAP),
                   ("ISLAND", (0.14, 0.5, 0.6, 0.92), ([255, 240, 90], [250, 170, 0], [50, 0, 100]), _CAP))

B[_k(275)] = words(bf([40, 200, 70], R(0.03, 0.52, 1, 1, [236, 30, 140]),
                      P(star_pts(0.22, 0.76, 0.2, 0.09, aspect=72 / 168), [255, 240, 60])),
                   ("BATTLE FOR", (0.03, 0.04, 0.97, 0.5), ([255, 200, 60], [250, 110, 0], [150, 0, 80]), {"th": 2.6, "pad": 2}),
                   ("COINS", (0.42, 0.5, 0.98, 0.98), ([170, 255, 90], [30, 190, 40], [0, 60, 10]), {"th": 2.8, "pad": 2}))
B[_k(277)] = over(bf([40, 80, 220], P(star_pts(0.5, 0.5, 0.62, 0.2, rot=-45, aspect=0.9), [250, 160, 20]),
                     P(star_pts(0.5, 0.5, 0.5, 0.26, rot=-90, aspect=0.9), [40, 80, 220]), E((0.5, 0.5), (0.3, 0.3), c=[60, 120, 240])),
                  "VS", [150, 255, 110], [20, 180, 50], [200, 0, 130], (0.14, 0.2, 0.86, 0.84), th=4.2, pad=3, edge_px=2.0, slant=0.15)


# ------------------------------------------------------------------ space icons
def _octa(r, cx=0.5, cy=0.5):
    return [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]


def _oct(fill, rim, *sign_ops, ring=W, bg=PALE):
    lite = [min(255, v + 70) for v in fill]
    return bf(bg, P(_octa(0.53), rim), P(_octa(0.46), ring), P(_octa(0.4), fill), E((0.42, 0.4), (0.2, 0.17), c=lite), *sign_ops)


def _sq(*sign_ops, rim=None):
    ops = [R(0, 0, 1, 1, rim), R(0.1, 0.1, 0.9, 0.9, PALE), R(0.17, 0.17, 0.83, 0.83, _SG)] if rim else \
        [frame([170, 170, 150], 0.03), R(0.1, 0.1, 0.9, 0.9, _SG)]
    return bf(PALE, ops, E((0.45, 0.42), (0.26, 0.24), c=[120, 215, 100]), *sign_ops)


_SG = [70, 180, 60]            # sign green
_LG = [150, 245, 130]          # light green figure
_BLUE_SP, _RED_SP = ([40, 60, 230], [30, 10, 110]), ([236, 30, 30], [150, 0, 0])
_QCOL = ([50, 110, 230], [10, 40, 150], [0, 10, 60])
_TOAD = [E((0.5, 0.7), (0.2, 0.15), c=_LG), E((0.5, 0.42), (0.31, 0.24), c=_LG), E((0.5, 0.3), (0.1, 0.07), c=NAVY),
         E((0.28, 0.46), (0.07, 0.08), c=NAVY), E((0.72, 0.46), (0.07, 0.08), c=NAVY),
         E((0.43, 0.7), (0.03, 0.055), c=NAVY), E((0.57, 0.7), (0.03, 0.055), c=NAVY)]
_GUY = [E((0.5, 0.44), (0.25, 0.28), c=_LG), E((0.4, 0.4), (0.065, 0.09), c=NAVY), E((0.6, 0.4), (0.065, 0.09), c=NAVY),
        E((0.5, 0.58), (0.04, 0.05), c=NAVY), P([(0.5, 0.8), (0.3, 0.72), (0.3, 0.9)], [250, 110, 130]),
        P([(0.5, 0.8), (0.7, 0.72), (0.7, 0.9)], [250, 110, 130])]
_GOOMBA = [E((0.5, 0.48), (0.33, 0.25), c=_LG), E((0.36, 0.8), (0.13, 0.07), c=_LG), E((0.64, 0.8), (0.13, 0.07), c=_LG),
           L([(0.26, 0.34), (0.46, 0.46)], 0.06, NAVY), L([(0.74, 0.34), (0.54, 0.46)], 0.06, NAVY),
           E((0.39, 0.5), (0.045, 0.06), c=NAVY), E((0.61, 0.5), (0.045, 0.06), c=NAVY), L([(0.36, 0.64), (0.64, 0.64)], 0.035, NAVY)]
_OR = [250, 150, 30]
_FIGURE = [E((0.5, 0.28), (0.13, 0.12), c=_OR), L([(0.5, 0.36), (0.5, 0.6)], 0.2, _OR),
           L([(0.4, 0.42), (0.24, 0.34), (0.36, 0.2)], 0.09, _OR), L([(0.6, 0.42), (0.76, 0.34), (0.64, 0.2)], 0.09, _OR),
           L([(0.46, 0.56), (0.72, 0.84)], 0.11, _OR), L([(0.54, 0.56), (0.28, 0.84)], 0.11, [250, 90, 30])]
_UTURN = [{"arc": [0.44, 0.48, 0.17, 0.2, 180, 360], "w": 0.12, "c": NAVY}, L([(0.27, 0.48), (0.27, 0.82)], 0.12, NAVY),
          P([(0.44, 0.5), (0.78, 0.5), (0.61, 0.8)], NAVY)]
_STARSIGN = [E((0.5, 0.52), (0.27, 0.27), c=NAVY), P(star_pts(0.5, 0.54, 0.22), [250, 226, 80])]
_BOWSER = [E((0.5, 0.52), (0.36, 0.32), c=[236, 30, 20]), P([(0.14, 0.14), (0.34, 0.3), (0.22, 0.46)], [236, 30, 20]),
           P([(0.86, 0.14), (0.66, 0.3), (0.78, 0.46)], [236, 30, 20]), E((0.38, 0.46), (0.07, 0.045), c=K, rot=25),
           E((0.62, 0.46), (0.07, 0.045), c=K, rot=-25),
           P([(0.3, 0.64), (0.38, 0.7), (0.44, 0.64), (0.5, 0.7), (0.56, 0.64), (0.62, 0.7), (0.7, 0.64), (0.64, 0.78), (0.36, 0.78)], K)]
_QBOX = (0.2, 0.14, 0.8, 0.86)

# square signs (36x36) and their 16x16 versions with a blue rim
B[_k(4)] = sign(_sq(), "?", _QCOL, _QBOX, 0.09)
B[_k(5)] = _sq(_UTURN)
B[_k(6)] = _sq(_TOAD)
B[_k(7)] = _sq(_FIGURE)
B[_k(8)] = _sq(_GUY)
B[_k(92)] = sign(_sq(rim=NAVY), "?", _QCOL, _QBOX, 0.1)
B[_k(93)] = _sq(_TOAD, rim=NAVY)
B[_k(94)] = _sq(_FIGURE, rim=NAVY)
B[_k(95)] = _sq(_GUY, rim=NAVY)
B[_k(96)] = _sq(_UTURN, rim=NAVY)
B[_k(97)] = bf([150, 30, 120], R(0.1, 0.1, 0.9, 0.9, [250, 200, 60]), R(0.17, 0.17, 0.83, 0.83, [250, 90, 120]),
               [{**o, "c": [230, 20, 20]} if isinstance(o, dict) and "arc" in o else o for o in
                [{"arc": [0.44, 0.48, 0.17, 0.2, 180, 360], "w": 0.12, "c": K}]],
               L([(0.27, 0.48), (0.27, 0.82)], 0.12, [230, 20, 20]), P([(0.44, 0.5), (0.78, 0.5), (0.61, 0.8)], [230, 20, 20]))
# octagon spaces: 40x40 (10-16, 19), 64x64 (17), 16x16 (81-89)
for _f in (10, 81):
    B[_k(_f)] = _oct(_BLUE_SP[0], _BLUE_SP[1])
for _f in (11, 82):
    B[_k(_f)] = _oct(_RED_SP[0], _RED_SP[1])
for _f in (12, 17, 83):
    B[_k(_f)] = sign(_oct(_SG, NAVY), "?", _QCOL, _QBOX, 0.09)
for _f in (13, 84):
    B[_k(_f)] = sign(_oct(_SG, NAVY), "!", _QCOL, _QBOX, 0.1)
for _f in (14, 85):
    B[_k(_f)] = _oct([20, 10, 10], [150, 0, 0], _BOWSER, ring=[236, 30, 20])
for _f in (15, 87):
    B[_k(_f)] = _oct(_SG, NAVY, _TOAD)
for _f in (16, 89):
    B[_k(_f)] = _oct(_SG, NAVY, _GUY)
for _f in (19, 86):
    B[_k(_f)] = _oct(_SG, NAVY, _GOOMBA)
B[_k(88)] = _oct(_SG, NAVY, _STARSIGN)

# coins, stars, hearts
_COIN_D = [200, 130, 0]


def _coin(*ops):
    return bf(GOLD, {"ring": [0.5, 0.5, 0.4, 0.4], "w": 0.05, "c": _COIN_D}, E((0.36, 0.32), (0.1, 0.06), c=GOLD_L, rot=-30), *ops,
              {"outline": 1, "c": [120, 60, 0]})


def _star_eyes(cx=0.5, cy=0.52, s=1.0):
    return [E((cx - 0.085 * s, cy), (0.035 * s, 0.09 * s), c=K), E((cx + 0.085 * s, cy), (0.035 * s, 0.09 * s), c=K)]


B[_k(18)] = _coin(P(star_pts(0.5, 0.52, 0.3), _COIN_D), P(star_pts(0.5, 0.52, 0.23), GOLD_L))
for _f in (78, 212):
    B[_k(_f)] = _coin(P(star_pts(0.5, 0.53, 0.26), _COIN_D))
B[_k(79)] = sign(_coin(), "G", ([130, 60, 0], [110, 40, 0], [130, 60, 0]), (0.2, 0.14, 0.82, 0.88), 0.065, edge_px=0.0)
B[_k(80)] = sign(_coin(), "M", ([130, 60, 0], [110, 40, 0], [130, 60, 0]), (0.16, 0.14, 0.86, 0.88), 0.065, edge_px=0.0)
B[_k(77)] = bf(GOLD, E((0.44, 0.4), (0.12, 0.08), c=GOLD_L, rot=-30), _star_eyes(0.5, 0.52, 1.1), {"outline": 1, "c": GOLD_D})
B[_k(261)] = bf([228, 228, 246], E((0.5, 0.56), (0.2, 0.18), c=W), L([(0.36, 0.5), (0.45, 0.54)], 0.04, [90, 90, 150]),
                L([(0.64, 0.5), (0.55, 0.54)], 0.04, [90, 90, 150]), {"arc": [0.5, 0.72, 0.09, 0.06, 180, 360], "w": 0.035, "c": [90, 90, 150]},
                {"outline": 1, "c": [150, 150, 210]})
_SPIN = [1.0, 0.75, 0.25, 0.75, 1.0, 0.75, 0.25, 0.75]
for _i in range(8):          # spinning star: eyes on the front frames only
    _back = _i in (3, 4, 5)
    B[_k(273, _i)] = bf([236, 190, 0] if _back else GOLD, [] if _back or _i in (2, 6) else _star_eyes(0.5 + (0.06 if _i == 1 else -0.06 if _i == 7 else 0), 0.55, 1.1 * _SPIN[_i] ** 0.5),
                        [] if _back else [E((0.42, 0.34), (0.08 * _SPIN[_i], 0.06), c=GOLD_L)], {"outline": 1, "c": GOLD_D})
    _dark = _i in (2, 3, 6, 7)   # spinning coin: the lit side and the shaded side
    _c, _cd = ([150, 70, 0], [90, 30, 0]) if _dark else (GOLD, _COIN_D)
    _ax = [1.0, 0.6, 0.5, 1.0, 1.0, 0.6, 0.35, 1.0][_i]
    B[_k(274, _i)] = bf(_c, {"ring": [0.5, 0.5, 0.4 * _ax, 0.4], "w": 0.05, "c": _cd},
                        [P(star_pts(0.5, 0.53, 0.24, aspect=_ax), _cd)] if _ax > 0.5 else [], {"outline": 1, "c": [90, 30, 0]})


def _heart(cx, cy, s, c, ax=1.0):
    lite = [min(255, v + 90) for v in c]
    return [E((cx - 0.23 * s * ax, cy - 0.14 * s), (0.27 * s * ax, 0.27 * s), c=c), E((cx + 0.23 * s * ax, cy - 0.14 * s), (0.27 * s * ax, 0.27 * s), c=c),
            P([(cx - 0.47 * s * ax, cy), (cx + 0.47 * s * ax, cy), (cx, cy + 0.52 * s)], c),
            E((cx - 0.26 * s * ax, cy - 0.22 * s), (0.1 * s * ax, 0.07 * s), c=lite, rot=-30)]


_HPINK = [255, 60, 170]
B[_k(90)] = bf(_HPINK, E((0.32, 0.3), (0.12, 0.08), c=[255, 170, 220], rot=-30), {"outline": 1, "c": [150, 0, 80]})
B[_k(210)] = bf([255, 110, 170], E((0.32, 0.3), (0.12, 0.08), c=[255, 190, 220], rot=-30), {"outline": 1, "c": K})
for _f, _c in ((112, "red"), (113, "blu")):
    B[_k(_f)] = bf(_PANEL[_c], _panel(_PANEL[_c]), _heart(0.25, 0.52, 0.62, [120, 0, 70], 40 / 70), _heart(0.25, 0.52, 0.54, _HPINK, 40 / 70))
for _i, _c in enumerate(("red", "yel", "grn", "blu")):
    B[_k(62 + _i)] = bf(_PANEL[_c], _panel(_PANEL[_c]), P(star_pts(0.25, 0.54, 0.4, aspect=40 / 70), GOLD_D),
                        P(star_pts(0.25, 0.54, 0.33, aspect=40 / 70), GOLD), E((0.22, 0.54), (0.016, 0.07), c=K), E((0.28, 0.54), (0.016, 0.07), c=K))
    B[_k(66 + _i)] = bf(_PANEL[_c], _panel(_PANEL[_c]), E((0.24, 0.5), (0.2, 0.4), c=[120, 60, 0]), E((0.24, 0.5), (0.18, 0.36), c=[250, 190, 30]),
                        P(star_pts(0.24, 0.52, 0.24, aspect=40 / 86), _COIN_D))
# heart meter: empty, then one more facet lit per frame until whole
_HDARK = [70, 54, 96]
for _i in range(6):
    _ops = []
    for _w in range(5):
        _a0, _a1 = math.radians(-90 - 72 * _w), math.radians(-90 - 72 * (_w + 1))
        _ops.append(P([(0.5, 0.52), (0.5 + math.cos(_a0), 0.52 + math.sin(_a0)), (0.5 + math.cos(_a1), 0.52 + math.sin(_a1))],
                      _HPINK if _w < _i else _HDARK))
    for _w in range(5):
        _a0 = math.radians(-90 - 72 * _w)
        _ops.append(L([(0.5, 0.52), (0.5 + math.cos(_a0), 0.52 + math.sin(_a0))], 0.03, [150, 0, 90] if 0 < _w < _i or (_w == 0 and _i == 5) else [30, 20, 50]))
    B[_k(215, _i)] = bf(_HDARK, _ops, {"outline": 1, "c": [30, 20, 50]})
B[_k(98)] = bf(GOLD, R(0, 0.72, 1, 0.84, GOLD_D), E((0.5, 0.56), (0.07, 0.09), c=[236, 30, 30]), E((0.26, 0.6), (0.05, 0.07), c=[40, 90, 230]),
               E((0.74, 0.6), (0.05, 0.07), c=[40, 90, 230]), E((0.4, 0.4), (0.07, 0.12), c=GOLD_L), {"outline": 1, "c": GOLD_D})

# arrows: a right arrow whose stripes cycle through the rainbow
_CYCLE = ([250, 226, 20], [250, 140, 0], [236, 20, 20], [140, 20, 170], [30, 40, 220], [100, 110, 170], [150, 150, 70], [30, 170, 60])


def _hy(x):       # half height of the arrow at x
    return 0.2 if x < 0.42 else 0.4 * (0.94 - x) / 0.52


for _i in range(8):
    _xs = [0.1, 0.28, 0.42, 0.62, 0.94]
    _ops = [P([(0.02, 0.24), (0.36, 0.24), (0.36, 0.0), (1.0, 0.5), (0.36, 1.0), (0.36, 0.76), (0.02, 0.76)], [10, 60, 20]),
            P([(0.06, 0.28), (0.4, 0.28), (0.4, 0.07), (0.96, 0.5), (0.4, 0.93), (0.4, 0.72), (0.06, 0.72)], W)]
    for _s in range(4):
        _a, _b = _xs[_s], _xs[_s + 1]
        _ha, _hb = (0.4 if _s == 2 else _hy(_a)), _hy(_b)
        _ops.append(P([(_a, 0.5 - _ha), (_b, 0.5 - _hb), (_b, 0.5 + _hb), (_a, 0.5 + _ha)], _CYCLE[(7 - _i + _s) % 8]))
    B[_k(46, _i)] = bf(W, _ops)
for _f, _c in ((282, [0, 0, 250]), (283, [250, 0, 0])):       # turn pointers
    B[_k(_f)] = bf(W, P([(0.14, 0.12), (0.86, 0.12), (0.86, 0.48), (0.5, 0.86), (0.14, 0.48)], _c))

# button prompts
B[_k(251, 0)] = sign(bf([0, 190, 255], E((0.5, 0.5), (0.5, 0.5), c=[0, 30, 160]), E((0.5, 0.5), (0.42, 0.42), c=[0, 190, 255])),
                     "A", ([200, 250, 255], [120, 230, 255], [0, 60, 200]), (0.18, 0.12, 0.82, 0.88), 0.06)
B[_k(251, 1)] = sign(bf([20, 40, 230], E((0.5, 0.5), (0.5, 0.5), c=K), E((0.5, 0.5), (0.44, 0.44), c=W), E((0.5, 0.5), (0.36, 0.36), c=[20, 40, 230])),
                     "A", (W, W, [10, 20, 150]), (0.18, 0.12, 0.82, 0.88), 0.06)

# ------------------------------------------------------------------ option icons with captions (48x48)
_OUT = {"outline": 2, "c": [0, 200, 30]}
_CAPC = {"cyan": ([120, 240, 255], [20, 90, 230]), "mag": ([255, 110, 220], [150, 20, 200]), "grn": ([120, 250, 170], [0, 160, 110]),
         "org": ([255, 200, 60], [240, 90, 20]), "pur": ([210, 150, 255], [120, 40, 220]), "red": ([255, 200, 60], [240, 30, 90]),
         "lime": ([160, 255, 120], [20, 190, 200])}


def _cap(text, col, box, th=1.4):
    return (text, box, (*_CAPC[col], [20, 10, 120]), {"th": th, "pad": 1})


def _book_open(c):
    dark = [int(v * 0.8) for v in c]
    return [P([(0.1, 0.55), (0.3, 0.1), (0.6, 0.2), (0.45, 0.72)], c), P([(0.45, 0.72), (0.6, 0.2), (0.95, 0.3), (0.85, 0.75)], dark)]


def _book(c, star, x=0.0, y=0.0, s=1.0):
    dark = [int(v * 0.7) for v in c]
    q = lambda px, py: (x + px * s, y + py * s)
    return [P([q(0.2, 0.62), q(0.42, 0.06), q(0.92, 0.2), q(0.74, 0.74)], dark), P([q(0.14, 0.58), q(0.36, 0.04), q(0.86, 0.16), q(0.68, 0.7)], c),
            P(star_pts(x + 0.5 * s, y + 0.37 * s, 0.17 * s), star)]


_BUBBLE = [E((0.52, 0.34), (0.44, 0.3), c=[20, 150, 50]), P([(0.02, 0.36), (0.2, 0.26), (0.2, 0.46)], [20, 150, 50]),
           E((0.52, 0.34), (0.34, 0.2), c=[250, 248, 210]), R(0.22, 0.2, 0.82, 0.48, [250, 248, 210]),
           [E((0.28 + 0.12 * i, y), (0.025, 0.025), c=[20, 40, 200]) for i in range(5) for y in (0.28, 0.4)]]


def _walker(c):
    return [E((0.52, 0.18), (0.13, 0.13), c=c), L([(0.5, 0.3), (0.5, 0.62)], 0.16, c), L([(0.5, 0.36), (0.3, 0.52)], 0.08, c),
            L([(0.5, 0.36), (0.72, 0.5)], 0.08, c), L([(0.5, 0.6), (0.34, 0.92)], 0.1, c), L([(0.5, 0.6), (0.7, 0.9)], 0.1, c)]


_SAVE = [E((0.55, 0.36), (0.4, 0.3), c=[30, 60, 210]), P([(0.36, 0.14), (0.8, 0.2), (0.7, 0.5), (0.3, 0.42)], W),
         {"ring": [0.55, 0.36, 0.4, 0.3], "w": 0.04, "c": [250, 200, 40]}]
_LOW = (0.08, 0.62, 0.92, 0.98)
_BG = [70, 70, 90]
B[_k(141)] = words(bf(_BG, _book_open([240, 232, 200]), _OUT), _cap("SHOW", "cyan", _LOW))
B[_k(142)] = words(bf(_BG, _book([250, 130, 20], [220, 50, 80]), _OUT), _cap("HIDE", "mag", _LOW))
B[_k(143)] = words(bf(_BG, _book_open([200, 235, 235]), _OUT), _cap("SHOW", "cyan", (0.0, 0.46, 0.78, 0.76)), _cap("COM", "org", (0.42, 0.72, 1.0, 1.0)))
B[_k(144)] = words(bf(_BG, _book([150, 110, 250], [230, 150, 240]), _OUT), _cap("HIDE", "mag", (0.0, 0.46, 0.7, 0.76)), _cap("COM", "org", (0.42, 0.72, 1.0, 1.0)))
B[_k(145)] = words(bf(_BG, _BUBBLE, _OUT), _cap("FAST", "cyan", _LOW))
B[_k(146)] = words(bf(_BG, _BUBBLE, _OUT), _cap("NORMAL", "grn", (0.0, 0.64, 1.0, 0.98), 1.1))
B[_k(147)] = words(bf(_BG, _BUBBLE, _OUT), _cap("SLOW", "mag", _LOW))
_MID = (0.06, 0.52, 0.94, 0.86)
B[_k(148)] = words(bf(_BG, _walker([250, 20, 230]), _OUT), _cap("FAST", "cyan", _MID))
B[_k(149)] = words(bf(_BG, _walker([250, 226, 20]), _OUT), _cap("NORMAL", "grn", (0.0, 0.54, 1.0, 0.86), 1.1))
B[_k(150)] = words(bf(_BG, _walker([20, 220, 250]), _OUT), _cap("SLOW", "mag", _MID))
B[_k(151)] = words(bf(_BG, _SAVE, _OUT), _cap("EVERY", "org", (0.0, 0.44, 0.82, 0.74)), _cap("TURN", "org", (0.24, 0.7, 1.0, 1.0)))
B[_k(152)] = words(bf(_BG, _SAVE, P([(0.1, 0.1), (0.5, 0.2), (0.4, 0.34), (0.7, 0.44), (0.2, 0.5), (0.34, 0.32)], [250, 230, 20]), _OUT),
                   _cap("THIS", "mag", (0.0, 0.44, 0.7, 0.74)), _cap("TURN", "mag", (0.24, 0.7, 1.0, 1.0)))
B[_k(153)] = words(bf(_BG, _SAVE, _OUT), _cap("DON'T", "pur", (0.0, 0.44, 0.82, 0.74)), _cap("SAVE", "pur", (0.24, 0.7, 1.0, 1.0)))
B[_k(177)] = words(bf(_BG, _book([240, 60, 70], [250, 150, 170], 0.3, 0.2, 0.7), _book([250, 190, 40], [250, 230, 120], 0.16, 0.26, 0.6),
                      _book([70, 200, 110], [20, 150, 60], 0.02, 0.0, 0.78), _OUT), _cap("ALL", "lime", (0.2, 0.66, 0.8, 1.0)))
B[_k(178)] = words(bf(_BG, _book([240, 60, 70], [250, 150, 170], 0.26, 0.1, 0.74), _OUT), _cap("EASY", "red", (0.12, 0.66, 0.9, 1.0)))


# controller pictures
def _pad(y=0.0, s=1.0):
    g, gd = [160, 160, 170], [110, 110, 122]
    q = lambda px, py: (px, y + py * s)
    r = lambda rx, ry: (rx, ry * s)
    return [E(q(0.5, 0.36), r(0.44, 0.24), c=g), E(q(0.2, 0.62), r(0.13, 0.32), c=g), E(q(0.8, 0.62), r(0.13, 0.32), c=g),
            E(q(0.5, 0.64), r(0.1, 0.3), c=g), E(q(0.5, 0.56), r(0.075, 0.075), c=gd), E(q(0.5, 0.56), r(0.04, 0.04), c=[200, 200, 206]),
            R(0.2, y + 0.3 * s, 0.24, y + 0.44 * s, gd), R(0.15, y + 0.35 * s, 0.29, y + 0.39 * s, gd),
            E(q(0.5, 0.3), r(0.035, 0.035), c=[230, 20, 20]), E(q(0.66, 0.42), r(0.04, 0.04), c=[30, 60, 230]),
            E(q(0.6, 0.34), r(0.04, 0.04), c=[30, 170, 60]),
            [E(q(0.76 + dx, 0.3 + dy), r(0.025, 0.025), c=[250, 210, 30]) for dx, dy in ((0, -0.06), (0, 0.06), (-0.06, 0), (0.06, 0))],
            {"outline": 2, "c": [10, 40, 150]}]


B[_k(140)] = bf(_BG, _pad(), {"outline": 1, "c": [0, 200, 30]})
B[_k(170)] = bf(_BG, _pad())
B[_k(157)] = bf(_BG, _pad(), L([(0.06, 0.06), (0.94, 0.94)], 0.13, [240, 0, 0]), L([(0.94, 0.06), (0.06, 0.94)], 0.13, [240, 0, 0]),
                {"outline": 1, "c": [0, 200, 30]})
B[_k(155)] = bf(_BG, P([(0.38, 0.04), (0.72, 0.42), (0.52, 0.42), (0.52, 0.62), (0.26, 0.62), (0.26, 0.42), (0.08, 0.42)], [240, 20, 20]),
                R(0.3, 0.56, 0.84, 0.96, [30, 60, 200]), P([(0.56, 0.96), (0.56, 0.6), (0.84, 0.6), (0.84, 0.8)], [250, 220, 40]),
                P([(0.3, 0.72), (0.56, 0.96), (0.3, 0.96)], [240, 120, 20]), _OUT)
B[_k(154)] = bf([30, 190, 60], R(0, 0, 1, 0.56, [170, 220, 250]), R(0.3, 0.3, 0.7, 0.62, W), R(0.22, 0.4, 0.34, 0.62, W), R(0.66, 0.4, 0.78, 0.62, W),
                P([(0.4, 0.3), (0.5, 0.08), (0.6, 0.3)], [230, 30, 40]), P([(0.2, 0.42), (0.28, 0.26), (0.36, 0.42)], [230, 30, 40]),
                P([(0.64, 0.42), (0.72, 0.26), (0.8, 0.42)], [230, 30, 40]), R(0.45, 0.48, 0.55, 0.62, [60, 40, 90]),
                P(star_pts(0.5, 0.82, 0.13), [30, 60, 200]), {"outline": 2, "c": [0, 150, 40]})
B[_k(156)] = bf(W, L([(0.3, 0.3), (0.5, 0.5)], 0.03, [150, 150, 170]), L([(0.42, 0.22), (0.6, 0.42)], 0.03, [150, 150, 170]),
                L([(0.2, 0.42), (0.4, 0.6)], 0.03, [150, 150, 170]), {"outline": 1, "c": K})
B[_k(211)] = bf(W, L([(0.3, 0.6), (0.7, 0.6)], 0.06, [150, 150, 170]), {"outline": 1, "c": K})
