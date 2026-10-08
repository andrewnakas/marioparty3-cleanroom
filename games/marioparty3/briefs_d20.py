"""MainFS dirs 20-25, 27-33: mini-game mode menus, instruction screens, results, save/option screens, item icons.

Everything is hand-written: words typed here, colours picked by eye, heads/items from the drawn library `icons.py`."""
import math

import numpy as np
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L
from . import icons as I

B = {}
T = {}

PL = I.PLAYERS                                   # mario luigi peach yoshi wario dk waluigi daisy
YEL = [255, 236, 0]
NAVY = [0, 0, 64]
RED, BLUE, GREEN = [226, 20, 16], [30, 70, 230], [30, 170, 40]
ITEMS15 = ["mushroom", "key", "poison_mushroom", "reverse_mushroom", "cellular_shopper", "warp_block", "plunder_chest",
           "bowser_phone", "glove", "lucky_lamp", "golden_mushroom"]


# ------------------------------------------------------------------ helpers
def _comp(out, g, x0, y0):
    h, w = g.shape[:2]
    reg = out[y0:y0 + h, x0:x0 + w]
    g = g[:reg.shape[0], :reg.shape[1]]
    a = g[..., 3:] / 255
    reg[..., :3] = reg[..., :3] * (1 - a) + g[..., :3] * a
    reg[..., 3] = np.maximum(reg[..., 3], g[..., 3])


# Our own small dot-matrix capitals (7 rows, mostly 4 columns) for words that must stay crisp at 6-14 px.
_PIX = {
    "A": ".##. #..# #..# #### #..# #..# #..#", "B": "###. #..# #..# ###. #..# #..# ###.", "C": ".### #... #... #... #... #... .###",
    "c": ".## #.. #.. #.. #.. #.. .##", "D": "###. #..# #..# #..# #..# #..# ###.", "E": "#### #... #... ###. #... #... ####",
    "F": "#### #... #... ###. #... #... #...", "G": ".### #... #... #.## #..# #..# .###", "H": "#..# #..# #..# #### #..# #..# #..#",
    "I": "### .#. .#. .#. .#. .#. ###", "|": "# # # # # # #", "J": "..## ...# ...# ...# ...# #..# .##.",
    "K": "#..# #.#. ##.. ##.. #.#. #..# #..#", "L": "#... #... #... #... #... #... ####", "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#..# ##.# ##.# #.## #.## #..# #..#", "O": ".##. #..# #..# #..# #..# #..# .##.", "P": "###. #..# #..# ###. #... #... #...",
    "Q": ".##. #..# #..# #..# #..# #.#. .#.#", "R": "###. #..# #..# ###. #.#. #..# #..#", "S": ".### #... #... .##. ...# ...# ###.",
    "T": "### .#. .#. .#. .#. .#. .#.", "U": "#..# #..# #..# #..# #..# #..# .##.", "V": "#...# #...# #...# #...# .#.#. .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# ##.## #...#", "X": "#..# #..# .##. .##. .##. #..# #..#", "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "#### ...# ..#. .#.. #... #... ####", "0": ".##. #..# #..# #..# #..# #..# .##.", "1": ".#. ##. .#. .#. .#. .#. ###",
    "2": ".##. #..# ...# ..#. .#.. #... ####", "3": "###. ...# ...# .##. ...# ...# ###.", "4": "..#. .##. #.#. #.#. #### ..#. ..#.",
    "5": "#### #... ###. ...# ...# #..# .##.", "6": ".##. #... #... ###. #..# #..# .##.", "7": "#### ...# ...# ..#. ..#. .#.. .#..",
    "8": ".##. #..# #..# .##. #..# #..# .##.", "9": ".##. #..# #..# .### ...# ...# .##.", ":": ". . # . . # .", ".": ". . . . . . #",
    "'": "# # . . . . .", "(": ".# #. #. #. #. #. .#", ")": "#. .# .# .# .# .# #.", "!": "# # # # # . #",
    "?": ".##. #..# ...# ..#. .#.. .... .#..", "-": "... ... ... ### ... ... ...", "+": "... ... .#. ### .#. ... ...",
    "x": "... ... #.# .#. #.# ... ...", " ": ".. .. .. .. .. .. ..",
}


def _pmask(text, sp=1):
    cols = []
    for i, ch in enumerate(text):
        g = np.array([[c == "#" for c in row] for row in _PIX[ch].split()], bool)
        if i:
            cols.append(np.zeros((7, sp), bool))
        cols.append(g)
    return np.concatenate(cols, 1)


def ptext(w, h, text, top, bottom, edge, ph=7, sx=1, sp=1, bold=False, align="centre", outline=True, dy=0):
    """RGBA float (h, w, 4): a word in the dot-matrix capitals, ph pixels high, columns repeated sx times;
    bold = strokes one pixel wider ("auto": when it still fits)."""
    def build(b):
        m = _pmask(text, sp + (1 if b and sx == 1 else 0))
        m = np.repeat(m[np.minimum(((np.arange(ph) + 0.5) * 7 / ph).astype(int), 6)], sx, 1)
        if b:
            m = np.pad(m, ((0, 0), (0, 1)))
            m[:, 1:] |= m[:, :-1]
        return m
    m = build(bool(bold))
    if bold == "auto" and m.shape[1] > w - 2:
        m = build(False)
    if m.shape[1] > w:                                    # last resort: drop columns
        m = m[:, (np.arange(w) * m.shape[1] / w).astype(int)]
    big = np.zeros((h, w), bool)
    x0 = 1 if align == "left" else (w - m.shape[1]) // 2
    x0 = max(0, min(x0, w - m.shape[1]))
    y0 = max(0, min((h - ph) // 2 + dy, h - ph))
    big[y0:y0 + ph, x0:x0 + m.shape[1]] = m[:h - y0]
    grown = big.copy()
    if outline:
        p = np.pad(big, 1)
        for ddy in (0, 1, 2):
            for ddx in (0, 1, 2):
                grown |= p[ddy:ddy + h, ddx:ddx + w]
    t = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1, ph - 1), 0, 1)[:, None, None]
    fill = np.asarray(top, np.float32) * (1 - t) + np.asarray(bottom, np.float32) * t
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = np.where(big[..., None], fill, np.asarray(edge, np.float32))
    out[..., 3] = grown * 255.0
    return out


def pic(base, *texts, keep=True):
    """Painter: base (brief / painter / None = transparent) with typeset words laid over it.
    texts: (text, (x0, y0, x1, y1), (top, bottom, edge), options)."""
    def fn(w, h, d, alpha):
        if base is None:
            out = np.zeros((h, w, 4), np.float32)
        elif callable(base):
            out = np.array(base(w, h, d, alpha), np.float32)
        else:
            out = np.array(facepaint.render(base, w, h, alpha=alpha if keep else None), np.float32)
        if out.shape[2] == 3:
            out = np.dstack([out, np.full((h, w), 255, np.float32)])
        for t, box, cols, opt in texts:
            x0, y0, x1, y1 = int(round(box[0] * w)), int(round(box[1] * h)), int(round(box[2] * w)), int(round(box[3] * h))
            _comp(out, (ptext if "ph" in opt else typeset)(x1 - x0, y1 - y0, t, *cols, **opt), x0, y0)
        if d.get("mode") == "rgba1":
            out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
        return out
    return fn


def lines(rows, x0, y0, pitch, hgt, cols, w_px, base=None, th=1.1):
    """Painter: left-aligned plain lines of text (pixel positions); rows may hold None for a blank line."""
    def fn(w, h, d, alpha):
        out = np.zeros((h, w, 4), np.float32)
        if base is not None:
            out[..., :3] = base
            out[..., 3] = 255
        for i, t in enumerate(rows):
            if t:
                _comp(out, typeset(w_px, hgt, t, *cols, th=th, align="left", edge_px=0.0 if base is None else 1.0), x0, y0 + i * pitch)
        return out
    return fn


def frame(c, t=0.06, asp=1.0):
    """Border of thickness t (fraction of the height); asp = width / height of the picture."""
    return [R(0, 0, 1, t, c), R(0, 1 - t, 1, 1, c), R(0, 0, t / asp, 1, c), R(1 - t / asp, 0, 1, 1, c)]


def label(bg, text, cols, fr=None, box=(0.0, 0.0, 1.0, 1.0), ft=0.1, asp=1.0, **opt):
    """Opaque strip: flat or {"grad"} backdrop, optional frame, one word."""
    return pic(brief(bg, *(frame(fr, ft, asp) if fr else [])), (text, box, cols, opt), keep=False)


def C(top, bottom=None, edge=K):
    return (top, top if bottom is None else bottom, edge)


ORANGE = C([255, 226, 40], [248, 120, 0], [72, 20, 124])        # menu capitals
PINKD = C([255, 120, 220], [240, 20, 150], [60, 10, 110])        # pink numbers
GOLDT = C([255, 250, 120], [226, 150, 0], K)                     # gold names
WHITE = C(W, W, NAVY)


def Z(n):
    """Digits with a round zero."""
    return str(n).replace("0", "O")


# ================================================================== dir 20: mini-game mode
for _i, _p in enumerate(["daisy", "mario", "peach", "luigi"]):
    B[f"20/6/b{7 + _i}"] = I.head(_p)
for _i, _p in enumerate(["dk", "wario", "waluigi", "yoshi"]):
    B[f"20/11/b{7 + _i}"] = I.head(_p)
for _i, _p in enumerate(PL):
    B[f"20/{20 + _i}/p0"] = I.head(_p)
T["20/28/p0"] = ("?", [120, 250, 60], [20, 170, 30], [200, 20, 10], {"th": 3.4, "pad": 3})

_INF = [{"ring": [0.3, 0.5, 0.2, 0.24], "w": 0.11, "c": [250, 60, 190]}, {"ring": [0.7, 0.5, 0.2, 0.24], "w": 0.11, "c": [250, 60, 190]}]
for _i, _t in enumerate(["2O", "35", "5O"]):
    T[f"20/8/b{7 + _i}"] = (_t, *PINKD, {"th": 3.0, "pad": 2, "edge_px": 1.5})
B["20/8/b10"] = brief([60, 10, 110], *_INF)
T["20/8/b11"] = ("?", *PINKD, {"th": 3.0, "pad": 3, "edge_px": 1.5})
B["20/8/b12"] = brief(YEL, E((0.5, 0.5), (0.47, 0.47), c=[226, 30, 20]), R(0.44, 0.03, 0.56, 0.2, W), R(0.44, 0.8, 0.56, 0.97, W),
                      R(0.03, 0.44, 0.2, 0.56, W), R(0.8, 0.44, 0.97, 0.56, W), E((0.5, 0.5), (0.32, 0.32), c=W), E((0.5, 0.5), (0.27, 0.27), c=[30, 90, 240]))
_PFRAME = [R(0.03, 0.03, 0.97, 0.97, [60, 10, 110]), R(0.08, 0.08, 0.92, 0.92, [250, 90, 200]), R(0.16, 0.16, 0.84, 0.84, [60, 10, 110])]
B["20/8/b13"] = pic(brief(YEL, *_PFRAME), ("1O", (0.16, 0.2, 0.84, 0.8), PINKD, {"th": 2.4}), keep=False)
for _i in range(9):
    B[f"20/36/p{_i}"] = pic(brief(YEL, *_PFRAME), (Z(10 + 5 * _i), (0.16, 0.2, 0.84, 0.8), PINKD, {"th": 2.4}), keep=False)
B["20/36/p9"] = brief(YEL, *_PFRAME, *I.place(_INF, (0.18, 0.2, 0.82, 0.8)))


# --- figures: red round players and blue square rivals on yellow
def _red(cx, cy, s=0.105):
    return [E((cx - 0.75 * s, cy + 0.95 * s), (0.5 * s, 0.32 * s), c=RED), E((cx + 0.75 * s, cy + 0.95 * s), (0.5 * s, 0.32 * s), c=RED),
            E((cx, cy), (s, s), c=RED), E((cx - 0.36 * s, cy - 0.25 * s), (0.13 * s, 0.3 * s), c=YEL), E((cx + 0.36 * s, cy - 0.25 * s), (0.13 * s, 0.3 * s), c=YEL),
            {"arc": [cx, cy + 0.15 * s, 0.5 * s, 0.4 * s, 20, 160], "w": 0.18 * s, "c": YEL}]


def _blue(cx, cy, s=0.105):
    c = [20, 50, 230]
    return [R(cx - s, cy - s, cx + s, cy + 0.6 * s, c), R(cx - s, cy + 0.5 * s, cx - 0.3 * s, cy + 1.4 * s, c), R(cx + 0.3 * s, cy + 0.5 * s, cx + s, cy + 1.4 * s, c),
            R(cx - 1.3 * s, cy - 0.2 * s, cx - s, cy + 0.7 * s, c), R(cx + s, cy - 0.2 * s, cx + 1.3 * s, cy + 0.7 * s, c),
            R(cx - 0.55 * s, cy - 0.6 * s, cx - 0.2 * s, cy - 0.1 * s, YEL), R(cx + 0.2 * s, cy - 0.6 * s, cx + 0.55 * s, cy - 0.1 * s, YEL)]


_TEAMS = {14: ([(0.2, 0.46), (0.5, 0.3), (0.8, 0.46)], [(0.5, 0.78)]), 15: ([(0.33, 0.36), (0.67, 0.36)], [(0.33, 0.78), (0.67, 0.78)]),
          16: ([(0.5, 0.27)], [(0.2, 0.55), (0.8, 0.55), (0.5, 0.8)]), 17: ([], [(0.5, 0.24), (0.2, 0.52), (0.8, 0.52), (0.5, 0.8)]),
          78: ([(0.68, 0.76)], [(0.32, 0.78)]), 79: ([], [(0.32, 0.78), (0.68, 0.78)])}
for _f, (_bl, _rd) in _TEAMS.items():
    for _i in range(8):
        _hop = 0.03 if _i in (4, 5) else 0.0            # the players hop in the middle frames
        B[f"20/{_f}/p{_i}"] = brief(YEL, *[o for p in _bl for o in _blue(*p)], *[o for (x, y) in _rd for o in _red(x, y - _hop)])

_ARROW = [248, 150, 0]
B["20/18/p0"] = brief(_ARROW, {"glow": [0.7, 0.5, 0.5, 0.4], "c": [255, 220, 60]}, {"outline": 1, "c": [60, 20, 110]})
B["20/19/p0"] = brief(_ARROW, {"glow": [0.3, 0.5, 0.5, 0.4], "c": [255, 220, 60]}, {"outline": 1, "c": [60, 20, 110]})
B["21/3/p0"] = brief(_ARROW, {"glow": [0.7, 0.5, 0.5, 0.4], "c": [255, 220, 60]}, {"outline": 1, "c": [60, 20, 110]})

# --- difficulty pills
_LEVEL = [("EASY", [30, 90, 236]), ("NORMAL", [200, 100, 30]), ("HARD", [240, 40, 150]), ("SUPER HARD", [200, 0, 24])]
for _i, (_t, _c) in enumerate(_LEVEL[:3]):
    B[f"20/{29 + _i}/p0"] = pic(brief(_c, {"outline": 1, "c": W}), (_t, (0.06, 0.1, 0.94, 0.9), C(W, W, I.dark(_c, 0.4)), {"ph": 10, "bold": "auto", "sp": 1}))
B["20/32/p0"] = pic(brief(_LEVEL[3][1], {"outline": 1, "c": W}), ("SUPER", (0.0, 0.08, 1.0, 0.5), C(W, W, [80, 0, 10]), {"ph": 8}),
                    ("HARD", (0.0, 0.5, 1.0, 0.92), C(W, W, [80, 0, 10]), {"ph": 8}))
_STARCOL = [[30, 90, 236], [240, 130, 30], [240, 60, 150], [200, 10, 24]]
for _i, (_t, _c) in enumerate(_LEVEL[:3]):
    B[f"20/{89 + _i}/p0"] = pic(brief(W, P(star_pts(0.5, 0.52, 0.43), _STARCOL[_i]), R(0.1, 0.42, 0.9, 0.74, I.dark(_STARCOL[_i], 0.6)), {"outline": 1, "c": _STARCOL[_i]}),
                                (_t, (0.1, 0.42, 0.9, 0.74), C(W, W, I.dark(_STARCOL[_i], 0.3)), {"ph": 10, "bold": "auto"}))
B["20/92/p0"] = pic(brief(W, P(star_pts(0.5, 0.52, 0.43), _STARCOL[3]), R(0.14, 0.36, 0.86, 0.8, [120, 0, 10]), {"outline": 1, "c": _STARCOL[3]}),
                    ("SUPER", (0.14, 0.38, 0.86, 0.58), C(W, W, [60, 0, 0]), {"ph": 8}), ("HARD", (0.14, 0.58, 0.86, 0.79), C(W, W, [60, 0, 0]), {"ph": 8}))
_STRIP = [("EASY", {"grad": [[70, 130, 250], [170, 220, 255]]}), ("NORMAL", {"grad": [[40, 110, 60], [110, 200, 80]]}), ("HARD", {"grad": [[250, 120, 20], [255, 200, 60]]}),
          ("SUPER HARD", {"grad": [[230, 20, 110], [250, 80, 60]]}), ("?", {"grad": [[250, 90, 40], [220, 20, 20]]})]
for _i, (_t, _g) in enumerate(_STRIP):
    B[f"20/{95 + _i}/p0"] = label(_g, _t, C([24, 20, 120], None, W), ph=12, bold=True, sp=1)
B["20/87/p0"] = pic(brief([200, 20, 50], {"outline": 1, "c": W}), ("ALL EQUAL", (0.0, 0.0, 1.0, 1.0), C(W, W, [90, 0, 20]), {"ph": 14, "sx": 2}))
B["20/88/p0"] = pic(brief([30, 80, 236], {"outline": 1, "c": [120, 250, 240]}), ("|ND|V|DUAL", (0.0, 0.0, 1.0, 1.0), C(W, W, [0, 20, 110]), {"ph": 14, "sx": 2}))

# --- handicap / bonus panels
_PANEL = lambda c: brief(YEL, R(0.04, 0.2, 0.96, 0.82, K), R(0.07, 0.23, 0.93, 0.79, c))
_PR, _PB = [204, 0, 0], [20, 60, 236]
B["20/33/p0"] = pic(_PANEL(_PR), ("HANDICAP", (0.06, 0.3, 0.94, 0.72), C([255, 200, 230], None, [70, 0, 0]), {"ph": 13}), keep=False)
B["20/33/p1"] = pic(_PANEL(_PB), ("NO", (0.3, 0.25, 0.7, 0.5), C([120, 255, 220], None, [0, 10, 90]), {"ph": 9, "bold": True}),
                    ("HANDICAP", (0.06, 0.5, 0.94, 0.78), C([120, 255, 220], None, [0, 10, 90]), {"ph": 11}), keep=False)
B["20/34/p0"] = pic(_PANEL(_PR), ("BONUS", (0.06, 0.3, 0.94, 0.72), C([255, 190, 240], None, [70, 0, 0]), {"ph": 13, "bold": True}), keep=False)
B["20/34/p1"] = pic(_PANEL(_PB), ("NO", (0.3, 0.25, 0.7, 0.5), C([120, 255, 200], None, [0, 10, 90]), {"ph": 9, "bold": True}),
                    ("BONUS", (0.06, 0.5, 0.94, 0.78), C([120, 255, 200], None, [0, 10, 90]), {"ph": 11, "bold": True}), keep=False)

# --- stars with a number
_SMALLSTAR = [P(star_pts(0.34, 0.47, 0.3), GOLD_D), P(star_pts(0.34, 0.47, 0.24), GOLD), E((0.3, 0.45), (0.018, 0.045), c=K), E((0.38, 0.45), (0.018, 0.045), c=K)]
_NUM = C([255, 150, 30], [240, 70, 0], [50, 10, 10])
for _i in range(10):
    B[f"20/35/p{_i}"] = pic(brief(YEL, R(0.1, 0.24, 0.9, 0.96, [10, 30, 150]), R(0.13, 0.27, 0.87, 0.93, [20, 70, 240]), *_SMALLSTAR),
                            ("x", (0.3, 0.68, 0.52, 0.94), _NUM, {"th": 1.0}), (Z(_i), (0.5, 0.46, 0.88, 0.95), _NUM, {"th": 2.2}), keep=False)
    B[f"20/{37 + _i}/p0"] = pic(brief(GOLD_D, P(star_pts(0.5, 0.55, 0.5), GOLD), {"outline": 1, "c": [90, 70, 0]}),
                                (Z(_i), (0.22, 0.22, 0.8, 0.92), _NUM, {"th": 1.9}))


# --- hearts made of five pieces (n of them pink)
def _heart(n, bg=None, scale=2.7):
    def fn(w, h, d, alpha):
        ss = 4
        ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
        u = ((xs + 0.5) / (w * ss) - 0.5) * scale
        v = -((ys + 0.5) / (h * ss) - 0.46) * scale
        f = (u * u + v * v - 1) ** 3 - u * u * v ** 3
        rim, inside = f < 0.0, f < -0.12
        ang = (np.degrees(np.arctan2(-u, v + 0.1)) + 360) % 360          # counter-clockwise from the top
        seg = (ang // 72).astype(int)
        seam = np.minimum(ang % 72, 72 - ang % 72) < 2.5
        img = np.zeros((h * ss, w * ss, 3), np.float32)
        img[:] = W if bg is None else bg
        shade = np.clip(1.0 + 0.25 * (v - u) / 2, 0.8, 1.2)[..., None]
        pink, dead = np.asarray([250, 60, 140], np.float32), np.asarray([70, 60, 90], np.float32)
        img[rim] = [120, 10, 60]
        body = np.where((seg < n)[..., None], pink, dead) * shade
        img[inside] = body[inside]
        img[inside & seam] *= 0.7
        out = np.zeros((h, w, 4), np.float32)
        out[..., :3] = img.reshape(h, ss, w, ss, 3).mean((1, 3))
        out[..., 3] = 255 if alpha is None else alpha
        return out
    return fn


B["20/10/b7"] = _heart(5, YEL)
for _i in range(5):
    B[f"20/{47 + _i}/p0"] = _heart(_i + 1, None, 3.3)
    B[f"20/52/p{_i}"] = _heart(_i + 1, YEL)

# --- small heads of the partners, pointers, player tags
_NPC = [I.koopa(), I.goomba(), I.toad(), I.bobomb(), I.boo(), I.whomp(), I.shy_guy(), I.piranha(), I.chain_chomp(), I.thwomp(), I.snowman(), I.baby_bowser()]
for _i, _b in enumerate(_NPC):
    B[f"20/{54 + _i}/p0"] = I.cut(_b)
_TAG = [("1P", C([255, 90, 60], [200, 0, 0], [60, 0, 20])), ("2P", C([110, 170, 255], [20, 50, 230], [0, 0, 80])), ("3P", C([255, 240, 80], [240, 150, 0], [90, 20, 0])),
        ("4P", C([120, 250, 80], [0, 160, 20], [0, 50, 10])), ("COM", C([120, 250, 250], [0, 170, 220], [20, 0, 90]))]
for _i, (_t, _c) in enumerate(_TAG):
    if _i < 4:
        T[f"20/{67 + _i}/p0"] = (_t, *_c, {"th": 2.0, "pad": 1})
        B[f"20/66/p{_i}"] = pic(I.hand(W, cuff=(0.3, 0.9)), (_t[0], (0.3, 0.0, 0.85, 0.52), _c, {"th": 2.0}))
    else:
        B["20/71/p0"] = pic(None, ("COM", (0.0, 0.0, 1.0, 1.0), _c, {"ph": 14, "sx": 2, "bold": True}))
        B["20/66/p4"] = pic(I.hand(W, cuff=(0.3, 0.9)), ("COM", (0.0, 0.0, 1.0, 0.5), _c, {"ph": 12, "sx": 2}))

# --- the six boards (framed pictures)
_CACTUS = I._b([240, 200, 110], R(0.42, 0.2, 0.58, 0.95, [30, 150, 50]), E((0.5, 0.2), (0.08, 0.08), c=[30, 150, 50]), L([(0.26, 0.4), (0.26, 0.6), (0.44, 0.6)], 0.1, [30, 150, 50]),
                L([(0.74, 0.3), (0.74, 0.5), (0.56, 0.5)], 0.1, [30, 150, 50]), E((0.46, 0.45), (0.02, 0.05), c=K), E((0.54, 0.45), (0.02, 0.05), c=K), E((0.82, 0.14), (0.1, 0.1), c=[250, 120, 20]))
_BOARDS = [I.snowman(bg=[150, 210, 250]), I.blooper(bg=[20, 80, 200]), _CACTUS, I.tree(bg=[110, 170, 230]), I.thwomp(bg=[80, 60, 110]), I.waluigi(bg=[60, 170, 60])]
for _i, _b in enumerate(_BOARDS):
    B[f"20/{72 + _i}/p0"] = I.framed(_b, inset=0.06)

# --- card signs: ALL / EASY
_CARD_G = [P([(0.12, 0.2), (0.6, 0.06), (0.74, 0.56), (0.26, 0.7)], [10, 110, 40]), P([(0.17, 0.23), (0.57, 0.11), (0.69, 0.53), (0.29, 0.65)], [60, 210, 110]),
           P(star_pts(0.43, 0.38, 0.15), [20, 150, 60])]
_CARD_R = [P([(0.4, 0.2), (0.86, 0.14), (0.92, 0.62), (0.46, 0.68)], [120, 10, 10]), P([(0.45, 0.24), (0.82, 0.19), (0.87, 0.58), (0.5, 0.63)], [240, 70, 60]),
           P(star_pts(0.66, 0.41, 0.14), [250, 150, 140])]
_SKY = [R(0.08, 0.08, 0.92, 0.92, [150, 200, 250])]
_ALL, _EASY = C([150, 255, 120], [20, 180, 40], [10, 30, 110]), C([255, 230, 60], [250, 130, 0], [150, 10, 20])
B["20/80/p0"] = pic(brief(YEL, *_SKY, *_CARD_R, *_CARD_G), ("ALL", (0.2, 0.6, 0.8, 0.96), _ALL, {"th": 1.8}), keep=False)
B["20/80/p1"] = pic(brief(YEL, *_SKY, *_CARD_R), ("EASY", (0.1, 0.6, 0.9, 0.96), _EASY, {"th": 1.6}), keep=False)
B["20/106/p0"] = pic(brief(K, *_CARD_R, *_CARD_G), ("ALL", (0.2, 0.6, 0.8, 0.98), _ALL, {"th": 1.8}), keep=False)
B["20/107/p0"] = pic(brief(K, *_CARD_R), ("EASY", (0.1, 0.6, 0.9, 0.98), _EASY, {"th": 1.6}), keep=False)

# --- six framed heads, partner panel
_GRID = []
for _i, _p in enumerate(PL[:6]):
    _x, _y = 0.05 + (_i % 3) * 0.31, 0.07 + (_i // 3) * 0.45
    _GRID += [R(_x, _y, _x + 0.28, _y + 0.41, W), R(_x + 0.015, _y + 0.022, _x + 0.265, _y + 0.388, [16, 14, 20])] + I.place(I.head(_p), (_x + 0.03, _y + 0.03, _x + 0.25, _y + 0.38))
B["20/93/p0"] = brief([20, 60, 30], *_GRID)
B["20/53/p0"] = pic(brief([40, 20, 250], {"outline": 1, "c": W}), ("PARTNER", (0.03, 0.0, 0.4, 0.17), C(W, W, [20, 10, 120]), {"ph": 10, "sx": 2}))

# ================================================================== dir 21: mini-game list (records)
for _i, _p in enumerate(PL[:6]):
    B[f"21/{4 + _i}/p0"] = I.head(_p)
_RANK = [("S", [250, 90, 0], [255, 240, 40]), ("A", [90, 220, 40], W), ("B", [20, 140, 90], [250, 150, 60]), ("C", [30, 50, 110], [170, 190, 150]),
         ("D", [0, 130, 90], [90, 120, 250]), ("E", [0, 90, 60], [190, 120, 230]), ("F", [24, 64, 44], [150, 110, 60])]
for _i, (_t, _bg, _fg) in enumerate(_RANK):
    B[f"21/{10 + _i}/p0"] = pic(brief(_bg, {"glow": [0.5, 0.5, 0.22, 0.6], "c": I.lite(_bg, 0.45)}, *frame(W, 0.09, 3.5)),
                                (_t, (0.36, 0.1, 0.64, 0.9), C(_fg, _fg, I.dark(_bg, 0.3)), {"th": 2.6}), keep=False)
_BOARDN = ["CHILLY WATERS", "DEEP BLOOBER SEA", "SPINY DESERT", "WOODY WOODS", "CREEPY CAVERN", "WALUIGI'S ISLAND"]
_GAMEN = ["GATE GUY", "ARROWHEAD", "PIPESQUEAK", "BLOWHARD", "MR. MOVER", "BACKTRACK"]
_LBL = C([255, 200, 40], [250, 150, 20], [70, 30, 0])
for _i, _t in enumerate(_BOARDN):
    B[f"21/{17 + _i}/p0"] = label([90, 130, 240], _t, _LBL, fr=W, asp=4.67, ph=12, bold="auto")
for _i, _t in enumerate(_GAMEN):
    B[f"21/{23 + _i}/p0"] = label([30, 160, 50], _t, _LBL, fr=W, asp=4.67, ph=12, bold="auto")
B["21/30/p0"] = label([230, 20, 150], "STARDUST BATTLE", C([255, 240, 60], None, [90, 0, 60]), fr=W, asp=4.67, ph=12, bold="auto")
B["21/29/p0"] = brief(YEL, {"outline": 1, "c": [200, 170, 0]})

# ================================================================== dir 22: name capitals, small white capitals
_ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_CAP = C([255, 150, 0], [255, 226, 40], [72, 20, 150])
for _i, _ch in enumerate(_ABC):
    T[f"22/{_i}/p0"] = (_ch, *_CAP, {"th": 1.7, "pad": 1})
    T[f"22/{38 + _i}/p0"] = (_ch, W, W, W, {"th": 0.85, "pad": 1, "edge_px": 0.0})
T["22/74/p0"] = ("3", *_CAP, {"th": 1.7, "pad": 1})
B["22/64/p0"] = pic(None, ("'", (0.0, 0.0, 1.0, 0.9), C(W, W, W), {"th": 1.0, "edge_px": 0.0}))
B["22/65/p0"] = pic(None, ('"', (0.0, 0.0, 1.0, 0.9), C(W, W, W), {"th": 1.0, "edge_px": 0.0}))
B["22/66/p0"] = pic(brief(W, L([(0.62, 0.62), (0.97, 0.95)], 0.09, [230, 20, 120])), ("HVQ", (0.03, 0.08, 0.97, 0.92), C(K, K, W), {"th": 5.0, "edge_px": 0.0}))

# ================================================================== dir 23: instruction screens
_TEAL, _BROWN = [0, 130, 150], [176, 116, 44]
_PINKT, _GREENT = C([255, 120, 170], [240, 50, 110], [20, 40, 80]), C([190, 255, 90], [70, 200, 30], [40, 40, 10])
_dim = lambda cs: tuple(I.dark(c, 0.55) for c in cs)
_RKEY = [R(0.3, 0.14, 0.72, 0.86, [70, 70, 80]), R(0.32, 0.18, 0.7, 0.8, [160, 160, 172])]
_RTXT = ("R", (0.4, 0.2, 0.62, 0.8), C(W, W, [60, 60, 70]), {"th": 1.2})
_RIM = {"outline": 1, "c": [90, 220, 250]}
B["23/9/p0"] = pic(brief(_TEAL, _RIM), ("START", (0.1, 0.12, 0.9, 0.88), _PINKT, {"th": 1.15}))
B["23/9/p1"] = pic(brief(I.dark(_TEAL, 0.7), E((0.5, 0.5), (0.2, 0.46), c=[150, 40, 30]), _RIM), ("START", (0.1, 0.12, 0.9, 0.88), _dim(_PINKT), {"th": 1.15}))
B["23/9/p2"] = pic(brief(_TEAL, E((0.5, 0.5), (0.23, 0.5), c=[120, 0, 0]), E((0.5, 0.48), (0.21, 0.46), c=[230, 30, 20]), _RIM),
                   ("START", (0.2, 0.2, 0.8, 0.8), C(W, W, [150, 0, 0]), {"ph": 8}))
for _f, _t in ((10, "PRACTICE"), (15, "QUIT")):
    _bx = (0.08, 0.12, 0.92, 0.88) if _f == 10 else (0.2, 0.1, 0.8, 0.9)
    B[f"23/{_f}/p0"] = pic(brief(_BROWN, _RIM), (_t, _bx, _GREENT, {"th": 1.1}))
    B[f"23/{_f}/p1"] = pic(brief(I.dark(_BROWN, 0.75), _RIM), (_t, _bx, _dim(_GREENT), {"th": 1.1}))
    B[f"23/{_f}/p2"] = pic(brief(_BROWN, *_RKEY, _RIM), _RTXT)
B["23/11/p0"] = pic(brief([30, 30, 200], E((0.62, 0.5), (0.055, 0.4), c=[150, 80, 0]), E((0.62, 0.48), (0.045, 0.33), c=[250, 170, 20]), {"outline": 1, "c": [60, 200, 90]}),
                    ("NEXT", (0.66, 0.0, 0.98, 1.0), C([255, 250, 80], None, [20, 10, 90]), {"ph": 11, "bold": True}))
_HELP = ["GAME RULES", "CONTROLS", "ADVICE", "CONTROLS(1)", "CONTROLS(2)", None, "CONTROLS(3)", "CONTROLS(4)"]
_HC = C([170, 255, 230], [90, 220, 250], [0, 0, 70])
for _i, _t in enumerate(_HELP):
    if _t:
        B[f"23/12/p{_i}"] = label([30, 40, 200], _t, _HC, ph=11, bold="auto")
B["23/12/p5"] = pic(brief([30, 40, 200]), ("ITEM", (0.0, 0.0, 1.0, 0.5), _HC, {"ph": 7, "outline": False}), ("EXPLANATION", (0.0, 0.5, 1.0, 1.0), _HC, {"ph": 7, "outline": False}), keep=False)
B["23/13/p0"] = pic(brief([40, 40, 190], {"outline": 1, "c": [60, 200, 90]}), ("PRACTICE", (0.2, 0.0, 0.8, 1.0), C([90, 240, 230], None, [0, 0, 60]), {"ph": 11, "sp": 2}))
B["23/14/p0"] = pic(brief([100, 190, 40], {"outline": 1, "c": [230, 30, 120]}), ("COIN BATTLE", (0.3, 0.0, 0.97, 1.0), C([240, 50, 30], None, [40, 60, 0]), {"ph": 12, "bold": True, "sp": 2}))
# card backs with a star
_BACK = [([40, 200, 110], [130, 240, 170]), ([230, 120, 170], [250, 170, 200]), ([80, 110, 220], [130, 160, 250]), ([60, 180, 200], [120, 90, 200]),
         ([220, 110, 210], [70, 90, 220]), ([240, 150, 70], [240, 200, 140]), ([220, 120, 60], [190, 110, 70]), ([245, 210, 60], [255, 236, 130])]
for _i, (_c, _s) in enumerate(_BACK):
    B[f"23/{16 + _i}/b8"] = brief(_c, *frame(I.lite(_c, 0.5), 0.06), {"ring": [0.5, 0.5, 0.42, 0.4], "w": 0.03, "c": I.dark(_c, 0.8)},
                                  P(star_pts(0.5, 0.52, 0.3, aspect=1.33), I.dark(_s, 0.6)), P(star_pts(0.5, 0.52, 0.25, aspect=1.33), _s))
for _i, _p in enumerate(PL):
    B[f"23/{46 + _i}/b7"] = I.cut(I.head(_p))
for _i, _n in enumerate(ITEMS15 + ["bowser_suit", "spray", "boo_bell", "magic_lamp"]):
    B[f"23/{56 + _i}/b8"] = I.cut(I.item(_n))

# ================================================================== dir 24: results
_GREY = [170, 170, 176]
_DO, _DB = C([255, 200, 20], [250, 130, 0], [80, 20, 150]), C([110, 200, 255], [30, 90, 236], [20, 20, 120])
_SYM = [Z(i) for i in range(10)] + ["+", "x"]
for _i, _t in enumerate(_SYM):
    B[f"24/5/p{_i}"] = pic(brief(W), (_t, (0.04, 0.27, 0.96, 0.73), _DO, {"th": 2.5, "edge_px": 1.6, "pad": 2}), keep=False)
    B[f"24/6/p{_i}"] = pic(brief(W), (_t, (0.04, 0.27, 0.96, 0.73), _DB, {"th": 2.5, "edge_px": 1.6, "pad": 2}), keep=False)
B["24/0/b7"] = pic(brief(W, *frame(_GREY, 0.05)), ("O", (0.08, 0.27, 0.92, 0.73), _DO, {"th": 2.5, "edge_px": 1.6, "pad": 2}), keep=False)
B["24/1/b7"] = I.framed(I.coin(bg=W), frame=_GREY, inset=0.06)
B["24/2/b7"] = I.framed(I.star(bg=W), frame=_GREY, inset=0.06)
B["24/4/b7"] = I.head("mario")
_RANKC = [C([255, 240, 60], [250, 140, 0], [90, 20, 130]), C([230, 230, 255], [120, 110, 200], [50, 20, 110]), C([250, 190, 110], [180, 90, 30], [70, 20, 90]),
          C([200, 160, 250], [110, 60, 190], [30, 60, 20])]
_ORD = ["1st", "2nd", "3rd", "4th"]
B["24/3/b7"] = pic(brief(W, *frame(_GREY, 0.03)), ("1st", (0.1, 0.2, 0.9, 0.9), _RANKC[0], {"th": 3.2, "edge_px": 1.5}), keep=False)
for _i in range(4):
    B[f"24/7/p{_i}"] = pic(brief(W, *frame(_GREY, 0.04)), (_ORD[_i], (0.06, 0.16, 0.94, 0.84), _RANKC[_i], {"th": 3.2, "edge_px": 1.5}), keep=False)
    T[f"27/{1 + _i}/b7"] = (_ORD[_i], *_RANKC[_i], {"th": 3.0, "edge_px": 1.5, "pad": 2})
B["24/7/p4"] = pic(brief(W, *frame(_GREY, 0.04)), ("WON!", (0.06, 0.2, 0.94, 0.8), C([255, 250, 60], [250, 200, 0], [80, 20, 130]), {"th": 2.6, "edge_px": 1.5}), keep=False)
for _i, _p in enumerate(PL):
    for _j in range(3):
        B[f"24/8/p{_i * 3 + _j}"] = I.framed(I.head(_p), frame=[236, 236, 240], inset=0.07)
T["24/9/p0"] = ("RESULTS", [255, 250, 80], [250, 190, 0], [30, 60, 220], {"th": 3.2, "edge_px": 1.5, "pad": 2})
T["24/10/p0"] = ("RESULTS", W, W, W, {"th": 3.2, "edge_px": 1.5, "pad": 2})

# ================================================================== dir 25 / 27: coins, ranking board
_COINF = [brief(GOLD, {"ring": [0.5, 0.5, 0.4, 0.4], "w": 0.06, "c": GOLD_D}, P(star_pts(0.5, 0.52, 0.26), GOLD_D), E((0.34, 0.3), (0.1, 0.06), c=GOLD_L, rot=-30), {"outline": 1, "c": [150, 100, 0]}),
          brief(GOLD, {"glow": [0.6, 0.6, 0.4, 0.5], "c": GOLD_D}, E((0.4, 0.3), (0.08, 0.1), c=GOLD_L), {"outline": 1, "c": [150, 100, 0]}),
          brief(GOLD, R(0.4, 0, 0.6, 1, GOLD_L), {"outline": 1, "c": [150, 100, 0]}),
          brief(GOLD, {"glow": [0.4, 0.6, 0.4, 0.5], "c": GOLD_D}, E((0.6, 0.3), (0.08, 0.1), c=GOLD_L), {"outline": 1, "c": [150, 100, 0]})]
for _i in range(4):
    B[f"25/9/p{_i}"] = _COINF[_i]
    B[f"33/36/b{7 + _i}"] = _COINF[_i]
    B[f"33/38/p{_i}"] = _COINF[_i]
for _i, _c in enumerate(([255, 0, 0], [190, 200, 50], [210, 110, 50], [50, 80, 200])):
    B[f"27/{1 + _i}/b9"] = brief(W, E((0.3, 0.42), (0.21, 0.21), c=_c), E((0.75, 0.62), (0.11, 0.11), c=_c))
_SCORE = C([250, 90, 30], [236, 60, 10], K)
for _i, _t in enumerate([Z(i) for i in range(10)] + ["x", "+", "-"]):
    B[f"27/7/p{_i}"] = pic(brief([255, 250, 214]), (_t.replace("O", "0"), (0.0, 0.0, 1.0, 1.0), _SCORE, {"ph": 8, "sx": 2, "bold": True, "outline": False}), keep=False)

# ================================================================== dir 28: chance time / lottery signs
_DISC = [[250, 150, 160], [140, 190, 240], [250, 180, 220], [120, 220, 110], [200, 150, 230], [250, 180, 110], [190, 190, 200], [250, 200, 120]]
for _i, _p in enumerate(PL):
    B[f"28/2/p{_i}"] = brief(W, {"glow": [0.5, 0.5, 0.75, 0.75], "c": _DISC[_i]}, *I.place(I.head(_p), (0.06, 0.06, 0.94, 0.94)))
_PRIZE = [(None, [250, 170, 90]), ("3O", [226, 20, 30]), ("2O", [30, 170, 60]), ("1O", [40, 90, 236]), ("1", K)]
for _i, (_t, _c) in enumerate(_PRIZE):
    _base = brief(W, {"glow": [0.5, 0.5, 0.75, 0.75], "c": I.lite(_c, 0.5)}, *I.place(I.coin(), (0.1, 0.1, 0.9, 0.9) if _t is None else (0.0, 0.0, 0.7, 0.7)))
    B[f"28/3/p{_i}"] = _base if _t is None else pic(_base, (_t, (0.34, 0.4, 1.0, 1.0), C(_c, _c, W), {"th": 2.0, "edge_px": 1.2}), keep=False)
for _i, (_t, _c) in enumerate([(None, [250, 170, 90]), ("3", [226, 20, 30]), ("2", [30, 170, 60]), ("1", K)]):
    _base = brief(W, {"glow": [0.5, 0.5, 0.75, 0.75], "c": I.lite(_c, 0.5)}, *I.place(I.star(), (0.08, 0.06, 0.92, 0.9) if _t is None else (0.0, 0.0, 0.72, 0.72)))
    B[f"28/3/p{5 + _i}"] = _base if _t is None else pic(_base, (_t, (0.5, 0.36, 1.0, 1.0), C(_c, _c, W), {"th": 2.2, "edge_px": 1.2}), keep=False)
B["28/4/p0"] = brief([250, 60, 200], {"glow": [0.4, 0.35, 0.4, 0.3], "c": [255, 150, 230]}, {"ring": [0.42, 0.5, 0.1, 0.1], "w": 0.03, "c": [90, 0, 90]},
                     L([(0.36, 0.56), (0.48, 0.44)], 0.03, [90, 0, 90]), {"outline": 1, "c": [70, 0, 80]})
B["28/6/p0"] = pic(None, ("CHANCE TIME", (0.0, 0.0, 1.0, 1.0), C([255, 110, 200], [190, 90, 250], [255, 190, 20]), {"ph": 28, "sx": 4, "bold": True}))
B["28/7/p0"] = pic(brief([30, 120, 240], *frame([20, 60, 180], 0.06)), ("?", (0.1, 0.06, 0.9, 0.94), C(W, W, [20, 60, 180]), {"th": 3.4}), keep=False)
for _i, _p in enumerate(["mario", "peach", "luigi"]):
    B[f"28/9/b{7 + _i}"] = I.head(_p, bg=[10, 20, 240])
B["28/11/b7"] = pic(brief([255, 230, 0], R(0.05, 0.05, 0.95, 0.95, [240, 90, 10]), P([(0.05, 0.05), (0.5, 0.5), (0.95, 0.05)], [250, 130, 30])),
                    ("!", (0.2, 0.08, 0.8, 0.92), C(W, W, [150, 40, 0]), {"th": 5.5}), keep=False)

# ================================================================== dir 29: ending (superstar)
_SEVEN = [[150, 110, 220], [60, 190, 90], [240, 150, 50], [250, 130, 180], [236, 20, 30], [80, 200, 240], [150, 150, 156]]
_STAMP = [[190, 160, 230], [70, 170, 90], [236, 150, 50], [250, 160, 190], [226, 20, 40], [60, 180, 236], [60, 60, 66]]
for _i in range(7):
    B[f"29/{3 + _i}/b7"] = brief(K, P(star_pts(0.5, 0.55, 0.46), _SEVEN[_i]), E((0.43, 0.52), (0.035, 0.085), c=K), E((0.57, 0.52), (0.035, 0.085), c=K),
                                E((0.4, 0.34), (0.05, 0.03), c=I.lite(_SEVEN[_i], 0.6), rot=-30))
    _sp = star_pts(0.5, 0.52, 0.36)
    B[f"29/{11 + _i}/p0"] = brief(W, {"ring": [0.5, 0.5, 0.48, 0.48], "w": 0.035, "c": _STAMP[_i]}, L(_sp + [_sp[0], _sp[1]], 0.035, _STAMP[_i]),
                                 E((0.45, 0.5), (0.022, 0.05), c=_STAMP[_i]), E((0.55, 0.5), (0.022, 0.05), c=_STAMP[_i]))
T["29/30/p0"] = ("IS THE SUPERSTAR!", *GOLDT, {"th": 2.4, "slant": 0.12, "pad": 2})
for _i, _t in enumerate(["MARIO", "LUIGI", "PEACH", "YOSHI", "WARIO", "DK", "WALUIGI", "DAISY"]):
    T[f"29/{31 + _i}/p0"] = (_t, *GOLDT, {"th": 3.4, "pad": 2, "edge_px": 1.5})

# ================================================================== dir 30: language flags, corrupted-save notice
_third = lambda a, b, c: brief(b, R(0, 0, 1 / 3, 1, a), R(2 / 3, 0, 1, 1, c))
B["30/0/p0"] = _third([0, 50, 160], W, [230, 30, 50])                         # France
B["30/1/p0"] = _third([0, 140, 70], W, [210, 30, 50])                         # Italy
B["30/2/p0"] = brief([255, 200, 0], R(0, 0, 1, 0.25, [200, 10, 30]), R(0, 0.75, 1, 1, [200, 10, 30]), E((0.3, 0.5), (0.06, 0.13), c=[180, 30, 30]),
                     R(0.25, 0.36, 0.35, 0.42, [200, 150, 0]))                 # Spain
B["30/3/p0"] = brief([220, 0, 0], R(0, 0, 1, 1 / 3, [10, 10, 10]), R(0, 2 / 3, 1, 1, [255, 206, 0]))   # Germany
_UR, _UB = [204, 16, 40], [0, 36, 125]
B["30/4/p0"] = brief(_UB, L([(0, 0), (1, 1)], 0.2, W), L([(0, 1), (1, 0)], 0.2, W), L([(0, 0), (1, 1)], 0.07, _UR), L([(0, 1), (1, 0)], 0.07, _UR),
                     R(0.4, 0, 0.6, 1, W), R(0, 0.34, 1, 0.66, W), R(0.44, 0, 0.56, 1, _UR), R(0, 0.4, 1, 0.6, _UR))        # United Kingdom
B["30/7/p0"] = lines(["Since your saved data was corrupted,", "all data has been erased.", None, "Der Speicherstand ist fehlerhaft.", "Alle Daten werden geloscht!", None,
                      "Sauvegarde corrompue.", "Les donnees ont ete effacees.", None, None, "Press any Button to start the game.", None,
                      "Drucke eine Taste, um", "das Spiel zu starten.", None, "Appuie sur un bouton pour lancer le jeu."],
                     28, 22, 12, 11, C(W, W, K), 284, base=[0, 0, 0], th=0.9)

# ================================================================== dir 31: file select, name entry
_GOLDF = [250, 190, 20]
for _f, _t, _c in ((1, "STORY MODE", [30, 60, 220]), (2, "PARTY MODE", [200, 20, 20])):
    B[f"31/{_f}/p0"] = pic(brief([0, 0, 80], *frame(_GOLDF, 0.04), R(0.05, 0.03, 0.95, 0.19, _c), R(0.04, 0.19, 0.96, 0.215, _GOLDF)),
                           (_t, (0.05, 0.03, 0.95, 0.19), C([255, 240, 40], [255, 200, 0], I.dark(_c, 0.35)), {"ph": 12, "bold": True}))
_NB = brief(NAVY)
for _i, _t in enumerate(["EASY", "NORMAL", "HARD"]):
    B[f"31/3/p{_i}"] = pic(_NB, ("LEVEL: " + _t, (0.0, 0.0, 1.0, 0.78), WHITE, {"ph": 10, "align": "left", "outline": False}), keep=False)
B["31/3/p3"] = pic(_NB, ("LEVEL:", (0.0, 0.0, 0.44, 0.78), WHITE, {"ph": 10, "align": "left", "outline": False}), ("SUPER", (0.44, 0.0, 0.84, 0.5), WHITE, {"ph": 7, "outline": False}),
                   ("HARD", (0.62, 0.5, 1.0, 1.0), WHITE, {"ph": 7, "outline": False}), keep=False)
for _i, _p in enumerate(PL):
    B[f"31/4/p{_i}"] = I.framed(I.head(_p), inset=0.06)
    B[f"33/{_i}/p0"] = I.cut(I.head(_p))
    B[f"33/{8 + _i}/p0"] = I.cut(I.head(_p))


def _small(text, cols=WHITE, **o):
    return pic(_NB, (text, (0.0, 0.0, 1.0, 1.0), cols, dict({"ph": 7, "outline": False}, **o)), keep=False)


B["31/5/p0"] = _small("CLEARED THROUGH")
B["31/6/p0"] = _small("TURN", ph=8)
for _i in range(10):
    B[f"31/7/p{_i}"] = pic(None, (str(_i), (0.0, 0.0, 1.0, 1.0), C(W, W, W), {"ph": 8, "bold": True, "outline": False}))
B["31/8/p0"] = _small("cOM", ph=6)
B["31/9/p0"] = _small("NO DATA")
for _i in range(6):
    B[f"31/10/p{_i}"] = _small(_GAMEN[_i])
    B[f"31/11/p{_i}"] = _small(_BOARDN[_i])
B["31/12/p0"] = _small("BATTLE ROYAL MAP", C([110, 240, 255], None, NAVY), align="left")
B["31/12/p1"] = _small("DUEL MAP", C([255, 90, 110], None, NAVY), align="left")
B["31/39/p0"] = _small("INFINITE TURNS")
B["31/40/p0"] = brief(NAVY, L([(0.2, 0.9), (0.8, 0.1)], 0.16, [240, 150, 0]))
for _f, _t, _c in ((14, "COPY", [70, 50, 210]), (15, "ERASE", [226, 40, 130])):
    B[f"31/{_f}/p0"] = pic(brief([70, 66, 84], R(0.1, 0.36, 0.9, 0.66, [44, 40, 56])), (_t, (0.08, 0.34, 0.92, 0.68), C([120, 116, 130], None, [30, 28, 40]), {"ph": 11, "bold": True}))
    B[f"31/{_f}/p1"] = pic(brief(_c, R(0.1, 0.36, 0.9, 0.66, I.dark(_c, 0.5))), (_t, (0.08, 0.34, 0.92, 0.68), C(W, W, I.dark(_c, 0.3)), {"ph": 11, "bold": True}))
    B[f"31/{_f}/p2"] = pic(brief(I.lite(_c, 0.55), R(0.1, 0.36, 0.9, 0.66, W)), (_t, (0.08, 0.34, 0.92, 0.68), C(I.dark(_c, 0.6), None, W), {"ph": 11, "bold": True}))
B["31/19/p0"] = brief([250, 60, 130], *frame([255, 170, 200], 0.08), P([(0.2, 0.5), (0.5, 0.22), (0.5, 0.38), (0.8, 0.38), (0.8, 0.62), (0.5, 0.62), (0.5, 0.78)], W))
B["31/20/p0"] = label([226, 0, 0], "DONE", C(W, W, [70, 0, 0]), fr=[250, 120, 110], ft=0.08, asp=1.86, ph=10)
_HEAD = C([255, 236, 40], [250, 150, 0], [20, 60, 200])
B["31/28/p0"] = pic(None, ("SELECT A FILE", (0.0, 0.0, 1.0, 1.0), _HEAD, {"ph": 14, "sx": 2, "bold": True}))
B["31/29/p0"] = pic(None, ("SELECT A MODE", (0.0, 0.0, 1.0, 1.0), _HEAD, {"ph": 14, "sx": 2, "bold": True}))
T["31/30/p0"] = ("COPY", *_HEAD, {"th": 2.0, "pad": 1})
T["31/31/p0"] = ("ERASE", *_HEAD, {"th": 2.0, "pad": 1})
B["31/33/p0"] = pic(brief([190, 10, 50], {"outline": 1, "c": W}), ("NEW", (0.18, 0.12, 0.82, 0.88), C(W, [255, 190, 210], [90, 0, 20]), {"th": 1.8}))
for _i in range(3):
    T[f"31/{45 + _i}/b7"] = (str(_i + 1), [255, 250, 60], [250, 210, 0], [50, 10, 90], {"th": 3.6, "edge_px": 2.0, "pad": 3})


def _keyboard(w, h, d, alpha):
    """Name-entry panel (letters): 13 columns, 12 px apart; capitals, small letters, digits, back arrow and DONE."""
    base = brief([0, 0, 64], *frame([236, 236, 250], 0.03, 2.12), R(0.69, 0.79, 0.755, 0.94, [150, 30, 80]), P([(0.7, 0.865), (0.722, 0.82), (0.722, 0.85), (0.745, 0.85), (0.745, 0.88), (0.722, 0.88), (0.722, 0.91)], [200, 200, 210]),
                 R(0.832, 0.79, 0.94, 0.94, [130, 10, 20]))
    out = np.array(facepaint.render(base, w, h, alpha=alpha), np.float32)
    rows = ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "abcdefghijklm", "nopqrstuvwxyz", "1234567890.-"]
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            g = typeset(12, 12, "O" if ch == "0" else ch, W, W, [0, 0, 64], th=1.0, pad=1)
            _comp(out, g, 43 + 12 * c, int(round(17.3 + 13.1 * r)))
    _comp(out, ptext(26, 13, "DONE", [200, 200, 210], [200, 200, 210], [130, 10, 20], ph=9), 201, 92)
    return out


B["31/23/p0"] = _keyboard

# ================================================================== dir 32: save-data notices (full screen, white text)
_NOTE = lambda rows, y: lines(rows, 56, y, 24, 19, C(W, W, W), 250, th=1.3)
B["32/0/p0"] = _NOTE(["All saved data was", "corrupted, so it has", "been erased.", None, "Press any button to", "begin a game."], 50)
for _i, _t in enumerate(["Data in File 1 was", "Data in File 2 was", "Data in File 3 was", "Some saved data was"]):
    B[f"32/{1 + _i}/p0"] = _NOTE([_t, "corrupted, so it has", "been erased.", None, "Press any button."], 61)

# ================================================================== dir 33: board HUD (heads, hands, coins, items)
_HANDS = [([255, 226, 226], None), ([208, 240, 240], None), (W, None), ([40, 150, 30], None), (W, "W"), ([214, 150, 60], None), (W, "L"), (W, None)]
for _i, (_c, _em) in enumerate(_HANDS):
    B[f"33/{16 + _i}/p0"] = I.hand(_c, _em)
B["33/24/p0"] = brief([110, 0, 10], E((0.5, 0.5), (0.25, 0.25), c=[60, 0, 0]), {"outline": 1, "c": [150, 150, 156]})
B["33/25/p0"] = brief([226, 20, 20], E((0.5, 0.5), (0.24, 0.24), c=[255, 200, 40]), {"outline": 1, "c": [130, 0, 20]})
B["33/26/p0"] = brief([250, 150, 20], P(star_pts(0.5, 0.52, 0.34), [255, 236, 60]), {"outline": 1, "c": [200, 60, 90]})
T["33/27/p0"] = ("x", [255, 180, 30], [250, 130, 0], [80, 20, 150], {"th": 1.9, "pad": 1})
for _i, _c in enumerate(([236, 30, 40], [40, 100, 240], [240, 40, 200], [60, 200, 50], [130, 70, 230], [250, 140, 30], [150, 150, 156], [240, 230, 40])):
    B[f"33/{28 + _i}/b7"] = brief(_c, E((0.5, 0.5), (0.46, 0.46), c=I.lite(_c, 0.75)), E((0.5, 0.5), (0.4, 0.4), c=_c), P(star_pts(0.5, 0.52, 0.34), W))
B["33/37/b7"] = I.cut(I.coin_bag())
B["33/39/p0"] = I.cut(I.coin_bag())
_CLOUD = [E((0.42, 0.52), (0.035, 0.12), c=K), E((0.58, 0.52), (0.035, 0.12), c=K), {"outline": 1, "c": [60, 150, 240]}]
B["33/40/p0"] = brief(W, *_CLOUD)
B["33/41/b8"] = brief(W, *_CLOUD)
B["33/42/p0"] = I.cut(I.toad())
_ALLITEMS = ITEMS15 + ["boo_bell", "spray", "bowser_suit", "magic_lamp", "item_bag", "koopa_kard", "barter_box", None, "watch", "koopa_kid_bag"]
for _i, _n in enumerate(_ALLITEMS):
    _b = I.coin(face=True, c=[250, 170, 20]) if _n is None else I.item(_n)          # None: the lucky charm (a smiling medal)
    B[f"33/{45 + _i}/p0"] = I.cut(_b)
    if _i < 16:
        B[f"33/44/p{_i}"] = I.cut(_b)
