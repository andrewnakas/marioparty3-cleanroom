"""Shared drawn icon library for Mario Party 3 briefs: character heads and items as facepaint briefs.

Everything here is hand-written primitives (colours picked by eye); nothing is derived from retail pixels.
Every function returns `brief(bg, *ops)` drawn to fill the unit square on a backdrop colour (default dark M.BG):

    from . import icons as I
    B[key] = I.head("toad")                              # opaque picture on the dark backdrop
    B[key] = I.cut(I.mushroom("golden"))                 # transparent surround (our own silhouette)
    B[key] = I.framed(I.item("key"))                     # white picture frame around it
    ops = I.place(I.head("mario"), (0.1, 0.1, 0.5, 0.5))  # the same drawing as ops inside a box of a bigger brief
    B[key] = I.cut(I.row(["mario", "star", "coin"]))     # several side by side

`HEADS` and `ITEMS` list the names accepted by `head()` / `item()`.
"""
import math

import numpy as np
from cleanroom.gfx import facepaint

from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, star_pts, GOLD, GOLD_D, GOLD_L

KEY = [44, 40, 64]            # backdrop used by cut(): dark so the antialiased fringe reads as an outline
RED, GREEN, BLUE, YEL = [228, 24, 20], [20, 160, 40], [30, 60, 230], [255, 222, 0]
SKIN, CREAM = [250, 190, 142], [244, 232, 204]
ORANGE, PURPLE, PINK, BROWN, TAN = [248, 132, 16], [124, 40, 200], [250, 120, 210], [150, 84, 36], [226, 180, 110]
GREY, STONE = [168, 168, 176], [130, 130, 140]


def dark(c, k=0.7):
    return [int(v * k) for v in c]


def lite(c, k=0.5):
    return [int(v + (255 - v) * k) for v in c]


def _b(bg, *ops):
    flat = []

    def add(o):
        if isinstance(o, (list, tuple)):
            for x in o:
                add(x)
        else:
            flat.append(o)
    add(ops)
    return brief(list(M.BG if bg is None else bg), *flat)


# ------------------------------------------------------------------ placing / framing / cutting
def place(b, box):
    """Ops of a brief (or a list of ops) moved into box = (x0, y0, x1, y1) of a bigger picture."""
    ops = b["ops"] if isinstance(b, dict) else b
    x0, y0, x1, y1 = box
    sx, sy = x1 - x0, y1 - y0
    X, Y = (lambda x: x0 + x * sx), (lambda y: y0 + y * sy)
    q4 = lambda v: [X(v[0]), Y(v[1]), v[2] * sx, v[3] * sy]
    out = []
    for op in ops:
        o = dict(op)
        if "outline" in o:
            continue
        for k in ("e", "ring", "sphere", "glow"):
            if k in o:
                o[k] = q4(o[k])
        if "clip" in o and o["clip"] is not None:
            o["clip"] = q4(o["clip"])
        if "hl" in o:
            o["hl"] = [X(o["hl"][0]), Y(o["hl"][1]), o["hl"][2] * sx]
        if "poly" in o:
            o["poly"] = [(X(x), Y(y)) for x, y in o["poly"]]
        if "line" in o:
            o["line"] = [(X(x), Y(y)) for x, y in o["line"]]
        if "arc" in o:
            o["arc"] = q4(o["arc"]) + list(o["arc"][4:6])
        if "rect" in o:
            r = o["rect"]
            o["rect"] = [X(r[0]), Y(r[1]), X(r[2]), Y(r[3])]
        if "eye" in o:
            e = dict(o["eye"])
            e["c"], e["r"] = [X(e["c"][0]), Y(e["c"][1])], [e["r"][0] * sx, e["r"][1] * sy]
            o["eye"] = e
        if "w" in o:
            o["w"] = o["w"] * sy
        out.append(o)
    return out


def boxed(b, box, bg=None):
    """The brief shrunk into a box of the unit square (e.g. to leave a margin)."""
    return _b(b["base"] if bg is None else bg, place(b, box))


def framed(b, frame=W, t=0.075, inset=0.0):
    """A picture frame (border of width t) around the brief; inset > 0 shrinks the picture inside it."""
    ops = place(b, (inset, inset, 1 - inset, 1 - inset)) if inset else list(b["ops"])
    return brief(b["base"], *ops, R(0, 0, 1, t, frame), R(0, 1 - t, 1, 1, frame), R(0, 0, t, 1, frame), R(1 - t, 0, 1, 1, frame))


def cut(b):
    """Painter with a transparent surround: M.cutout of the brief re-based on KEY (so black ink stays opaque)."""
    return M.cutout(dict(b, base=list(KEY)))


def row(names, bg=None, gap=0.02):
    """Several heads/items side by side (for wide pictures); names from HEADS / ITEMS or ready briefs."""
    n = len(names)
    ops = []
    for i, nm in enumerate(names):
        b = nm if isinstance(nm, dict) else get(nm)
        ops += place(b, (i / n + gap / 2, 0, (i + 1) / n - gap / 2, 1))
    return _b(bg, ops)


# ------------------------------------------------------------------ small parts
def eyes(cx, cy, dx, rx, ry, c=K, hl=True):
    """Two solid oval eyes (the tall black Mario-style ones) with a glint."""
    ops = []
    for s in (-1, 1):
        ops.append(E((cx + s * dx, cy), (rx, ry), c=c))
        if hl:
            ops.append(E((cx + s * dx - rx * 0.15, cy - ry * 0.45), (rx * 0.42, ry * 0.3), c=W))
    return ops


def weyes(cx, cy, dx, rx, ry, pupil=0.5, look=(0.0, 0.15), iris=K, white=W):
    """Two white eyes with pupils (look = offset of the pupil in eye radii, mirrored in x)."""
    ops = []
    for s in (-1, 1):
        ops.append(E((cx + s * dx, cy), (rx, ry), c=white))
        ops.append(E((cx + s * dx - s * look[0] * rx, cy + look[1] * ry), (rx * pupil, ry * pupil), c=iris))
    return ops


def brows(cx, cy, dx, half, tilt, w=0.05, c=K):
    """Angry brows: outer ends high, inner ends low (tilt < 0 for sad/kind)."""
    return [L([(cx + s * (dx + half), cy - tilt), (cx + s * (dx - half), cy + tilt)], w, c) for s in (-1, 1)]


def no_sign(cx, cy, r, w=0.05, c=RED):
    d = r * 0.7
    return [{"ring": [cx, cy, r, r], "w": w, "c": c}, L([(cx - d, cy - d), (cx + d, cy + d)], w, c)]


def qmark(cx, cy, s, c=W, w=None):
    w = s * 0.24 if w is None else w
    return [{"arc": [cx, cy - s * 0.42, s * 0.34, s * 0.3, 180, 440], "w": w, "c": c},
            L([(cx + s * 0.12, cy - s * 0.14), (cx, cy), (cx, cy + s * 0.14)], w, c), E((cx, cy + s * 0.5), (w * 0.6, w * 0.6), c=c)]


# ------------------------------------------------------------------ the eight players
PLAYERS = ("mario", "luigi", "peach", "yoshi", "wario", "dk", "waluigi", "daisy")
WAL = [104, 24, 168]
D_HAIR, D_SKIN, D_DRESS = [206, 100, 24], [246, 180, 128], [255, 204, 0]


def waluigi(bg=None):
    return _b(
        bg, P([(0.2, 1), (0.28, 0.9), (0.72, 0.9), (0.8, 1)], WAL), R(0.4, 0.92, 0.6, 1, [30, 24, 60]),
        E((0.22, 0.47), (0.06, 0.09), c=SKIN), E((0.78, 0.47), (0.06, 0.09), c=SKIN),
        P([(0.26, 0.34), (0.74, 0.34), (0.72, 0.62), (0.58, 0.9), (0.5, 0.98), (0.42, 0.9), (0.28, 0.62)], SKIN),
        E((0.5, 0.25), (0.31, 0.19), c=WAL), R(0.19, 0.25, 0.81, 0.33, WAL), E((0.5, 0.35), (0.32, 0.06), c=dark(WAL)),
        E((0.5, 0.2), (0.1, 0.085), c=W), L([(0.47, 0.265), (0.47, 0.155), (0.55, 0.155)], 0.03, [250, 200, 0]),
        weyes(0.5, 0.48, 0.1, 0.065, 0.05, pupil=0.45, look=(0.3, 0.2)),
        R(0.34, 0.42, 0.66, 0.455, [150, 110, 200]), brows(0.5, 0.425, 0.1, 0.08, 0.035, 0.04),
        L([(0.5, 0.7), (0.38, 0.72), (0.28, 0.66), (0.25, 0.57)], 0.035), L([(0.5, 0.7), (0.62, 0.72), (0.72, 0.66), (0.75, 0.57)], 0.035),
        E((0.5, 0.61), (0.085, 0.075), c=[255, 150, 170]),
        P([(0.4, 0.77), (0.6, 0.77), (0.5, 0.85)], W))


def daisy(bg=None):
    return _b(
        bg, E((0.5, 0.52), (0.37, 0.38), c=D_HAIR), P([(0.1, 0.9), (0.16, 0.5), (0.84, 0.5), (0.9, 0.9), (0.7, 0.8), (0.3, 0.8)], D_HAIR),
        P([(0.24, 1), (0.3, 0.86), (0.7, 0.86), (0.76, 1)], D_DRESS), E((0.5, 0.9), (0.05, 0.04), c=[0, 170, 90]),
        E((0.5, 0.56), (0.23, 0.27), c=D_SKIN),
        P([(0.27, 0.52), (0.3, 0.32), (0.5, 0.26), (0.7, 0.32), (0.73, 0.52), (0.62, 0.4), (0.52, 0.36), (0.44, 0.42), (0.36, 0.38)], D_HAIR),
        P([(0.36, 0.23), (0.38, 0.08), (0.44, 0.16), (0.5, 0.05), (0.56, 0.16), (0.62, 0.08), (0.64, 0.23)], [250, 210, 0]),
        *[E((0.5 + 0.04 * dx, 0.165 + 0.04 * dy), (0.025, 0.028), c=W) for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0))],
        E((0.5, 0.165), (0.022, 0.024), c=[0, 170, 90]),
        weyes(0.5, 0.56, 0.09, 0.055, 0.07, pupil=0.62, look=(0, 0.1), iris=[30, 90, 210]),
        E((0.41, 0.57), (0.017, 0.028), c=K), E((0.59, 0.57), (0.017, 0.028), c=K),
        L([(0.34, 0.49), (0.41, 0.47), (0.47, 0.49)], 0.018), L([(0.53, 0.49), (0.59, 0.47), (0.66, 0.49)], 0.018),
        {"arc": [0.5, 0.71, 0.07, 0.04, 20, 160], "w": 0.025, "c": [220, 70, 60]},
        E((0.26, 0.66), (0.03, 0.035), c=W), E((0.74, 0.66), (0.03, 0.035), c=W))


# ------------------------------------------------------------------ other characters
def toad(spot=RED, cap=W, vest=BLUE, bg=None):
    return _b(
        bg, P([(0.28, 1), (0.33, 0.84), (0.67, 0.84), (0.72, 1)], vest), R(0.44, 0.86, 0.56, 1, SKIN),
        E((0.5, 0.68), (0.23, 0.2), c=SKIN), E((0.5, 0.35), (0.45, 0.33), c=cap),
        {"clip": [0.5, 0.35, 0.45, 0.33]}, E((0.5, 0.17), (0.17, 0.13), c=spot), E((0.1, 0.42), (0.11, 0.15), c=spot),
        E((0.9, 0.42), (0.11, 0.15), c=spot), {"clip": None},
        eyes(0.5, 0.67, 0.08, 0.03, 0.06), {"arc": [0.5, 0.76, 0.07, 0.04, 20, 160], "w": 0.022, "c": [150, 60, 40]})


def koopa(shell=GREEN, bg=None):
    y = M.KOOPA_Y
    return _b(
        bg, E((0.22, 0.92), (0.26, 0.22), c=shell), {"ring": [0.22, 0.92, 0.26, 0.22], "w": 0.05, "c": W},
        E((0.52, 0.5), (0.29, 0.36), c=y), E((0.68, 0.64), (0.25, 0.15), c=[255, 176, 20]),
        L([(0.5, 0.68), (0.72, 0.7), (0.9, 0.62)], 0.02, [190, 110, 0]),
        weyes(0.52, 0.3, 0.1, 0.09, 0.16, pupil=0.45, look=(-0.3, 0.2)))


def goomba(bg=None):
    c = [178, 98, 40]
    return _b(
        bg, E((0.5, 0.9), (0.24, 0.16), c=TAN), E((0.5, 0.44), (0.45, 0.36), c=c), E((0.5, 0.62), (0.34, 0.2), c=c),
        weyes(0.5, 0.46, 0.14, 0.085, 0.12, pupil=0.5, look=(0.3, 0.2)),
        brows(0.5, 0.33, 0.15, 0.13, 0.07, 0.07),
        L([(0.26, 0.7), (0.5, 0.66), (0.74, 0.7)], 0.03),
        P([(0.3, 0.7), (0.36, 0.69), (0.33, 0.58)], W), P([(0.64, 0.69), (0.7, 0.7), (0.67, 0.58)], W))


def boo(bg=None):
    return _b(
        bg, E((0.5, 0.5), (0.43, 0.43), c=[214, 220, 236]), E((0.47, 0.47), (0.4, 0.4), c=W),
        E((0.08, 0.6), (0.08, 0.11), c=W), E((0.92, 0.6), (0.08, 0.11), c=W),
        P([(0.26, 0.3), (0.46, 0.42), (0.44, 0.5), (0.3, 0.46)], K), P([(0.74, 0.3), (0.54, 0.42), (0.56, 0.5), (0.7, 0.46)], K),
        P([(0.24, 0.6), (0.5, 0.56), (0.76, 0.6), (0.66, 0.82), (0.34, 0.82)], [150, 0, 30]),
        E((0.5, 0.78), (0.13, 0.07), c=[250, 60, 80]),
        *[P([(x, 0.585), (x + 0.1, 0.575), (x + 0.05, 0.69)], W) for x in (0.27, 0.45, 0.63)])


def bowser(bg=None, kid=False):
    g, m = ([70, 170, 40], [240, 220, 150]) if kid else ([30, 140, 50], [246, 200, 110])
    hair = [226, 40, 20]
    ops = [
        P([(0.3, 0.3), (0.36, 0.04), (0.46, 0.2), (0.52, 0.0), (0.6, 0.2), (0.68, 0.06), (0.72, 0.3)], hair),
        P([(0.06, 0.1), (0.3, 0.26), (0.18, 0.4)], CREAM), P([(0.94, 0.1), (0.7, 0.26), (0.82, 0.4)], CREAM),
        E((0.5, 0.42), (0.34, 0.26), c=g), E((0.5, 0.7), (0.38, 0.25), c=m),
        weyes(0.5, 0.42, 0.13, 0.085, 0.08, pupil=0.5, look=(0.3, 0.2), iris=[170, 0, 20]),
        brows(0.5, 0.31, 0.13, 0.12, 0.05, 0.07, hair if not kid else K),
        E((0.42, 0.6), (0.025, 0.02), c=K), E((0.58, 0.6), (0.025, 0.02), c=K),
    ]
    if kid:
        ops += [L([(0.26, 0.74), (0.5, 0.8), (0.74, 0.74)], 0.03, [150, 70, 20]),
                P([(0.3, 0.76), (0.37, 0.78), (0.33, 0.66)], W), P([(0.63, 0.78), (0.7, 0.76), (0.67, 0.66)], W),
                P([(0.3, 1), (0.36, 0.92), (0.64, 0.92), (0.7, 1)], W)]
    else:
        ops += [P([(0.22, 0.7), (0.5, 0.74), (0.78, 0.7), (0.66, 0.9), (0.34, 0.9)], [130, 10, 20]),
                *[P([(x, 0.715), (x + 0.1, 0.725), (x + 0.05, 0.82)], W) for x in (0.26, 0.4, 0.52, 0.64)]]
    return _b(bg, ops)


def baby_bowser(bg=None):
    return bowser(bg, kid=True)


def shy_guy(hood=RED, mask=W, bow=None, bg=None):
    ops = [E((0.5, 0.52), (0.42, 0.46), c=hood), P([(0.14, 1), (0.22, 0.7), (0.78, 0.7), (0.86, 1)], hood),
           E((0.5, 0.5), (0.3, 0.34), c=mask), E((0.39, 0.42), (0.065, 0.11), c=K), E((0.61, 0.42), (0.065, 0.11), c=K),
           E((0.5, 0.68), (0.055, 0.06), c=K)]
    if bow:
        ops += [P([(0.5, 0.9), (0.3, 0.8), (0.3, 1)], bow), P([(0.5, 0.9), (0.7, 0.8), (0.7, 1)], bow), E((0.5, 0.9), (0.05, 0.05), c=dark(bow))]
    return _b(bg, ops)


def game_guy(bg=None):
    return shy_guy(RED, [255, 226, 30], [170, 90, 240], bg)


def bobomb(body=(34, 34, 44), bg=None):
    body = list(body)
    return _b(
        bg, E((0.32, 0.93), (0.15, 0.07), c=[250, 170, 20]), E((0.68, 0.93), (0.15, 0.07), c=[250, 170, 20]),
        L([(0.54, 0.16), (0.6, 0.05), (0.7, 0.04)], 0.04, [200, 180, 150]), R(0.4, 0.1, 0.6, 0.22, GREY),
        {"sphere": [0.5, 0.55, 0.38, 0.38], "c": lite(body, 0.25)},
        E((0.41, 0.52), (0.055, 0.12), c=W), E((0.59, 0.52), (0.055, 0.12), c=W),
        R(0.86, 0.5, 0.98, 0.56, GOLD), {"ring": [0.96, 0.53, 0.05, 0.07], "w": 0.03, "c": GOLD})


def thwomp(c=(40, 90, 230), eye=RED, bg=None):
    c = list(c)
    return _b(
        bg, P([(0.06, 0.2), (0.2, 0.06), (0.8, 0.06), (0.94, 0.2), (0.94, 0.84), (0.8, 0.96), (0.2, 0.96), (0.06, 0.84)], dark(c, 0.6)),
        P([(0.12, 0.22), (0.24, 0.12), (0.76, 0.12), (0.88, 0.22), (0.88, 0.8), (0.76, 0.9), (0.24, 0.9), (0.12, 0.8)], c),
        weyes(0.5, 0.42, 0.17, 0.1, 0.07, pupil=0.45, look=(0.3, 0.2), iris=eye),
        brows(0.5, 0.31, 0.17, 0.15, 0.07, 0.08),
        P([(0.24, 0.78), (0.3, 0.64), (0.7, 0.64), (0.76, 0.78)], K),
        *[R(x, 0.665, x + 0.08, 0.74, W) for x in (0.32, 0.41, 0.5, 0.59)])


def whomp(bg=None):
    return thwomp(STONE, RED, bg)


def piranha(bg=None):
    return _b(
        bg, L([(0.5, 0.7), (0.5, 1)], 0.1, GREEN), E((0.28, 0.92), (0.2, 0.07), c=GREEN), E((0.72, 0.92), (0.2, 0.07), c=GREEN),
        E((0.5, 0.4), (0.4, 0.37), c=RED), E((0.24, 0.22), (0.07, 0.07), c=W), E((0.3, 0.6), (0.07, 0.07), c=W),
        E((0.5, 0.1), (0.07, 0.05), c=W), E((0.16, 0.42), (0.05, 0.06), c=W),
        P([(0.5, 0.42), (0.96, 0.12), (0.98, 0.7)], W), P([(0.58, 0.42), (0.98, 0.2), (0.98, 0.62)], [120, 0, 20]),
        *[P([(x, 0.42 - (x - 0.58) * 0.52), (x + 0.1, 0.42 - (x + 0.1 - 0.58) * 0.52), (x + 0.06, 0.42 - (x - 0.58) * 0.2)], W) for x in (0.62, 0.74, 0.86)],
        *[P([(x, 0.42 + (x - 0.58) * 0.5), (x + 0.1, 0.42 + (x + 0.1 - 0.58) * 0.5), (x + 0.06, 0.42 + (x - 0.58) * 0.2)], W) for x in (0.62, 0.74, 0.86)])


def chain_chomp(bg=None):
    return _b(
        bg, *[{"ring": [0.08 + 0.1 * i, 0.9 - 0.06 * i, 0.07, 0.07], "w": 0.03, "c": GREY} for i in range(3)],
        {"sphere": [0.56, 0.48, 0.42, 0.42], "c": [60, 60, 76]},
        P([(0.3, 0.52), (0.98, 0.4), (0.9, 0.76), (0.6, 0.88)], [190, 10, 30]),
        *[P([(x, 0.53 - (x - 0.3) * 0.17), (x + 0.13, 0.53 - (x + 0.13 - 0.3) * 0.17), (x + 0.07, 0.65 - (x - 0.3) * 0.1)], W) for x in (0.36, 0.52, 0.68, 0.82)],
        *[P([(x, 0.84 - (x - 0.5) * 0.36), (x + 0.12, 0.84 - (x + 0.12 - 0.5) * 0.36), (x + 0.04, 0.72 - (x - 0.5) * 0.3)], W) for x in (0.56, 0.7, 0.82)],
        E((0.6, 0.26), (0.1, 0.11), c=W), E((0.63, 0.28), (0.045, 0.055), c=K),
        E((0.84, 0.3), (0.07, 0.08), c=W), E((0.86, 0.32), (0.03, 0.04), c=K))


def snowman(bg=None):
    return _b(
        bg, E((0.5, 0.56), (0.45, 0.43), c=[190, 206, 232]), E((0.47, 0.52), (0.42, 0.4), c=[244, 248, 255]),
        E((0.34, 0.42), (0.065, 0.08), c=K), E((0.66, 0.42), (0.065, 0.08), c=K), E((0.5, 0.66), (0.1, 0.06), c=K),
        E((0.32, 0.39), (0.02, 0.025), c=W), E((0.64, 0.39), (0.02, 0.025), c=W))


def tumble(bg=None):
    """Dice-headed host: a white die with a face on the front and pips on the top and side."""
    return _b(
        bg, P([(0.36, 1), (0.4, 0.86), (0.6, 0.86), (0.64, 1)], [60, 90, 220]),
        P([(0.1, 0.26), (0.36, 0.06), (0.92, 0.1), (0.7, 0.3)], [226, 230, 240]),
        P([(0.7, 0.3), (0.92, 0.1), (0.9, 0.66), (0.7, 0.88)], [176, 182, 204]),
        P([(0.1, 0.26), (0.7, 0.3), (0.7, 0.88), (0.12, 0.84)], W),
        E((0.52, 0.18), (0.07, 0.035), c=RED), E((0.81, 0.36), (0.03, 0.045), c=K), E((0.81, 0.66), (0.03, 0.045), c=K),
        eyes(0.4, 0.5, 0.11, 0.045, 0.09),
        {"arc": [0.4, 0.66, 0.12, 0.07, 20, 160], "w": 0.03, "c": K},
        E((0.18, 0.36), (0.035, 0.035), c=RED), E((0.62, 0.78), (0.035, 0.035), c=RED))


def millennium_star(bg=None):
    c = [206, 206, 240]
    return _b(
        bg, P(star_pts(0.5, 0.54, 0.52, 0.25), [140, 140, 190]), P(star_pts(0.5, 0.54, 0.46, 0.22), c),
        *[L([(0.5, 0.54), p], 0.012, W) for p in star_pts(0.5, 0.54, 0.44, 0.2)[::2]],
        eyes(0.5, 0.5, 0.09, 0.035, 0.06), brows(0.5, 0.41, 0.09, 0.07, 0.03, 0.035, [90, 90, 140]),
        P([(0.5, 0.6), (0.32, 0.58), (0.16, 0.72), (0.38, 0.76), (0.5, 0.69), (0.62, 0.76), (0.84, 0.72), (0.68, 0.58)], W),
        {"hl": [0.38, 0.3, 0.04]})


def blooper(bg=None):
    return _b(
        bg, *[E((x, 0.86), (0.07, 0.14), c=[226, 230, 240]) for x in (0.2, 0.4, 0.6, 0.8)],
        P([(0.5, 0.02), (0.84, 0.3), (0.88, 0.72), (0.12, 0.72), (0.16, 0.3)], W),
        R(0.14, 0.44, 0.86, 0.66, K), weyes(0.5, 0.55, 0.16, 0.1, 0.08, pupil=0.4, look=(0, 0)))


def fish(c=(40, 110, 220), bg=None):
    c = list(c)
    return _b(
        bg, P([(0.02, 0.86), (0.2, 0.62), (0.26, 0.9)], dark(c)), P([(0.5, 0.3), (0.62, 0.08), (0.72, 0.3)], dark(c)),
        E((0.56, 0.52), (0.42, 0.26), c=c, rot=-20), E((0.56, 0.62), (0.34, 0.14), c=[226, 232, 240], rot=-20),
        E((0.76, 0.34), (0.05, 0.05), c=W), E((0.77, 0.34), (0.025, 0.025), c=K),
        L([(0.62, 0.62), (0.8, 0.56), (0.94, 0.46)], 0.02, K),
        *[P([(x, 0.62 - (x - 0.62) * 0.4), (x + 0.07, 0.62 - (x + 0.07 - 0.62) * 0.4), (x + 0.035, 0.7 - (x - 0.62) * 0.4)], W) for x in (0.66, 0.75, 0.84)])


def mole(bg=None):
    c = [236, 150, 20]
    return _b(
        bg, E((0.5, 0.56), (0.46, 0.46), c=c), E((0.5, 0.74), (0.4, 0.24), c=W),
        R(0.2, 0.34, 0.8, 0.44, K), E((0.34, 0.42), (0.13, 0.09), c=K), E((0.66, 0.42), (0.13, 0.09), c=K),
        E((0.5, 0.58), (0.12, 0.08), c=[120, 60, 30]),
        L([(0.5, 0.66), (0.5, 0.78)], 0.02, GREY), {"arc": [0.5, 0.76, 0.14, 0.06, 20, 160], "w": 0.02, "c": GREY},
        *[L([(0.5 + s * 0.3, 0.66 + d), (0.5 + s * 0.52, 0.62 + d * 2)], 0.015, K) for s in (-1, 1) for d in (0, 0.06)])


def tree(leaf=(40, 150, 40), trunk=(226, 176, 110), angry=False, bg=None):
    leaf, trunk = list(leaf), list(trunk)
    ops = [P([(0.2, 1), (0.28, 0.5), (0.72, 0.5), (0.8, 1)], trunk),
           *[E((x, y), (0.2, 0.17), c=dark(leaf, 0.75)) for x, y in ((0.2, 0.36), (0.8, 0.36), (0.5, 0.42))],
           *[E((x, y), (0.2, 0.17), c=leaf) for x, y in ((0.26, 0.2), (0.74, 0.2), (0.5, 0.14), (0.5, 0.3), (0.14, 0.3), (0.86, 0.3))],
           *[E((x, y), (0.07, 0.06), c=lite(leaf, 0.35)) for x, y in ((0.3, 0.16), (0.62, 0.12), (0.76, 0.26), (0.44, 0.3))],
           eyes(0.5, 0.66, 0.1, 0.035, 0.055), E((0.5, 0.76), (0.07, 0.05), c=dark(trunk, 0.8)),
           {"arc": [0.5, 0.82, 0.14, 0.06, 20, 160], "w": 0.025, "c": dark(trunk, 0.5)}]
    if angry:
        ops += brows(0.5, 0.57, 0.1, 0.08, 0.04, 0.04)
    return _b(bg, ops)


def evil_tree(bg=None):
    return tree([110, 30, 170], [50, 110, 220], True, bg)


def girl(hair=(110, 40, 170), bg=None):
    """Purple-haired lady with a pale face (dir 0 file 102)."""
    hair = list(hair)
    skin = [250, 214, 200]
    return _b(
        bg, E((0.46, 0.4), (0.4, 0.4), c=hair), P([(0.06, 0.4), (0.3, 0.3), (0.3, 1), (0.1, 1)], hair),
        P([(0.3, 0), (0.5, 0.02), (0.36, 0.2)], [40, 170, 60]),
        P([(0.36, 1), (0.42, 0.84), (0.72, 0.84), (0.8, 1)], [240, 130, 200]),
        E((0.56, 0.56), (0.25, 0.3), c=skin), P([(0.3, 0.5), (0.4, 0.26), (0.8, 0.3), (0.82, 0.44), (0.56, 0.34)], hair),
        E((0.52, 0.5), (0.04, 0.065), c=K), E((0.7, 0.5), (0.04, 0.065), c=K), E((0.61, 0.72), (0.05, 0.035), c=[240, 80, 150]))


def bigmouth(bg=None):
    """Pale pink creature with a wide open red mouth and a red gem on top (dir 0 file 99)."""
    c = [236, 210, 226]
    return _b(
        bg, P([(0.4, 0.14), (0.5, 0.02), (0.6, 0.14)], RED), E((0.5, 0.56), (0.47, 0.4), c=c),
        E((0.5, 0.6), (0.38, 0.24), c=[190, 10, 30]), E((0.5, 0.7), (0.26, 0.1), c=[250, 90, 90]),
        *[R(x, 0.38, x + 0.09, 0.47, W) for x in (0.2, 0.31, 0.42, 0.53, 0.64, 0.75)],
        *[R(x, 0.76, x + 0.09, 0.84, W) for x in (0.25, 0.36, 0.47, 0.58, 0.69)],
        E((0.3, 0.26), (0.035, 0.035), c=K), E((0.7, 0.26), (0.035, 0.035), c=K))


def pipe(c=(40, 60, 230), bg=None):
    """Warp pipe with eyes."""
    c = list(c)
    return _b(
        bg, R(0.16, 0.3, 0.84, 1, c), R(0.16, 0.3, 0.3, 1, lite(c, 0.35)), R(0.72, 0.3, 0.84, 1, dark(c)),
        R(0.06, 0.1, 0.94, 0.4, c), E((0.5, 0.12), (0.44, 0.1), c=lite(c, 0.3)), E((0.5, 0.13), (0.34, 0.065), c=dark(c, 0.45)),
        R(0.06, 0.36, 0.94, 0.41, dark(c)), eyes(0.5, 0.62, 0.1, 0.045, 0.1))


def glove_guy(bg=None):
    """White glove with eyes (dir 0 file 74)."""
    return _b(bg, glove(bg)["ops"], eyes(0.5, 0.62, 0.07, 0.03, 0.07, hl=False))


def cone_guy(bg=None):
    """Green cone with eyes and a yellow crossbar (dir 0 file 75)."""
    return _b(
        bg, L([(0.14, 0.82), (0.86, 0.82)], 0.07, [240, 200, 20]), L([(0.2, 0.7), (0.2, 0.94)], 0.05, [240, 200, 20]),
        L([(0.8, 0.7), (0.8, 0.94)], 0.05, [240, 200, 20]),
        P([(0.5, 0.02), (0.74, 0.98), (0.26, 0.98)], [0, 150, 110]), P([(0.5, 0.02), (0.44, 0.98), (0.26, 0.98)], [20, 60, 180]),
        eyes(0.5, 0.56, 0.06, 0.03, 0.09, hl=False))


def disc_guy(bg=None):
    """Orange disc with eyes on a yellow/black hazard burst (dir 0 file 76)."""
    return _b(
        bg, *[P([(0.5, 0.5), (0.5 + 0.8 * math.cos(math.radians(a)), 0.5 + 0.8 * math.sin(math.radians(a))),
                 (0.5 + 0.8 * math.cos(math.radians(a + 22)), 0.5 + 0.8 * math.sin(math.radians(a + 22)))], [250, 210, 20])
              for a in range(0, 360, 45)],
        {"ring": [0.5, 0.5, 0.46, 0.46], "w": 0.07, "c": RED}, E((0.5, 0.5), (0.3, 0.34), c=[250, 110, 0]),
        E((0.42, 0.4), (0.1, 0.08), c=[255, 170, 80]), eyes(0.5, 0.5, 0.1, 0.045, 0.11, hl=False))


# ------------------------------------------------------------------ items
MUSHROOMS = {            # kind: (cap, spot, stem, angry)
    "red": (RED, W, CREAM, False), "golden": ([250, 204, 0], [255, 250, 190], [250, 214, 60], False),
    "poison": ([110, 40, 200], [90, 220, 90], CREAM, True), "reverse": ([30, 170, 50], W, CREAM, False),
    "green": ([0, 150, 44], [236, 240, 120], CREAM, False), "blue": ([60, 130, 240], [190, 220, 255], CREAM, False),
    "orange": ([250, 130, 20], W, CREAM, False), "pink": ([250, 120, 190], W, CREAM, False),
}


def mushroom(kind="red", bg=None, cap=None, spot=None):
    """Mushroom item; kind from MUSHROOMS (red, golden, poison, reverse, green, blue, orange, pink) or cap/spot colours."""
    c, s, stem, angry = MUSHROOMS.get(kind, MUSHROOMS["red"])
    c, s = (c if cap is None else list(cap)), (s if spot is None else list(spot))
    ops = [E((0.5, 0.76), (0.27, 0.21), c=stem), E((0.5, 0.4), (0.47, 0.35), c=c),
           {"clip": [0.5, 0.4, 0.47, 0.35]}, E((0.5, 0.24), (0.19, 0.15), c=s), E((0.08, 0.48), (0.1, 0.14), c=s),
           E((0.92, 0.48), (0.1, 0.14), c=s)]
    if kind == "reverse":      # red U-turn arrows on the spots
        ops += [{"arc": [0.5, 0.25, 0.1, 0.08, 150, 400], "w": 0.05, "c": RED}, P([(0.36, 0.2), (0.48, 0.3), (0.34, 0.36)], RED),
                E((0.08, 0.48), (0.05, 0.07), c=RED), E((0.92, 0.48), (0.05, 0.07), c=RED)]
    ops += [{"clip": None}, E((0.34, 0.2), (0.06, 0.035), c=lite(c, 0.5), rot=-30)]
    if angry:
        ops += [P([(0.3, 0.74), (0.46, 0.8), (0.44, 0.86), (0.32, 0.84)], K), P([(0.7, 0.74), (0.54, 0.8), (0.56, 0.86), (0.68, 0.84)], K)]
    else:
        ops += eyes(0.5, 0.8, 0.08, 0.032, 0.075, hl=False)
    return _b(bg, ops)


def key(bg=None, face=True, c=GOLD):
    """Skeleton key (the MP3 one has a square head with angry eyes)."""
    ops = [L([(0.52, 0.5), (0.52, 0.94)], 0.13, GOLD_D), L([(0.5, 0.5), (0.5, 0.93)], 0.1, c),
           R(0.55, 0.66, 0.74, 0.74, c), R(0.55, 0.82, 0.7, 0.9, c),
           P([(0.26, 0.12), (0.34, 0.04), (0.66, 0.04), (0.74, 0.12), (0.74, 0.46), (0.66, 0.54), (0.34, 0.54), (0.26, 0.46)], GOLD_D),
           P([(0.29, 0.13), (0.36, 0.07), (0.64, 0.07), (0.71, 0.13), (0.71, 0.44), (0.64, 0.5), (0.36, 0.5), (0.29, 0.44)], c)]
    if face:
        ops += eyes(0.5, 0.33, 0.09, 0.04, 0.075, hl=False) + brows(0.5, 0.2, 0.09, 0.08, 0.035, 0.045)
    else:
        ops += [E((0.5, 0.29), (0.1, 0.1), c=list(M.BG if bg is None else bg))]
    return _b(bg, ops)


def star(bg=None, face=True, c=GOLD):
    ops = [P(star_pts(0.5, 0.54, 0.52, 0.26), GOLD_D), P(star_pts(0.5, 0.54, 0.45, 0.22), c), E((0.4, 0.34), (0.06, 0.035), c=GOLD_L, rot=-30)]
    if face:
        ops += eyes(0.5, 0.5, 0.07, 0.03, 0.075, hl=False)
    return _b(bg, ops)


def coin(bg=None, face=False, c=GOLD):
    ops = [E((0.5, 0.5), (0.44, 0.46), c=GOLD_D), E((0.5, 0.5), (0.39, 0.41), c=c),
           {"ring": [0.5, 0.5, 0.31, 0.33], "w": 0.035, "c": GOLD_D}, E((0.36, 0.3), (0.08, 0.05), c=GOLD_L, rot=-30)]
    if face:
        ops += eyes(0.5, 0.44, 0.09, 0.035, 0.07, GOLD_D, hl=False) + [{"arc": [0.5, 0.56, 0.14, 0.1, 20, 160], "w": 0.04, "c": RED}]
    else:
        ops += [L([(0.5, 0.36), (0.5, 0.64)], 0.07, GOLD_D)]
    return _b(bg, ops)


def chest(bg=None, emblem=None):
    """Treasure chest; emblem = colour of a lightning flash on the lid (plunder chest)."""
    wood, band = [176, 96, 40], [250, 200, 40]
    ops = [R(0.08, 0.44, 0.92, 0.9, wood), P([(0.08, 0.46), (0.14, 0.2), (0.86, 0.2), (0.92, 0.46)], lite(wood, 0.15)),
           L([(0.08, 0.46), (0.92, 0.46)], 0.035, dark(wood, 0.5)),
           R(0.08, 0.82, 0.92, 0.9, band), R(0.2, 0.2, 0.3, 0.9, band), R(0.7, 0.2, 0.8, 0.9, band),
           R(0.43, 0.4, 0.57, 0.6, [120, 150, 220]), E((0.5, 0.5), (0.03, 0.04), c=K)]
    if emblem:
        ops.append(P([(0.52, 0.16), (0.4, 0.33), (0.5, 0.33), (0.46, 0.44), (0.62, 0.27), (0.52, 0.27), (0.58, 0.16)], emblem))
    return _b(bg, ops)


def plunder_chest(bg=None):
    return chest(bg, [255, 240, 60])


def bag(c=TAN, tie=(150, 90, 30), bg=None, emblem="star"):
    """Tied sack; emblem "star" (coin bag), "shroom" (item bag: white with red spots and a face) or None."""
    c, tie = list(c), list(tie)
    ops = [P([(0.34, 0.06), (0.5, 0.14), (0.66, 0.06), (0.6, 0.3), (0.4, 0.3)], c),
           E((0.5, 0.64), (0.4, 0.34), c=dark(c, 0.8)), E((0.48, 0.62), (0.37, 0.31), c=c),
           L([(0.36, 0.3), (0.64, 0.3)], 0.07, tie)]
    if emblem == "star":
        ops += [E((0.5, 0.64), (0.2, 0.2), c=dark(c, 0.75)), P(star_pts(0.5, 0.65, 0.17), lite(c, 0.3))]
    elif emblem == "shroom":
        ops += [{"clip": [0.48, 0.62, 0.37, 0.31]}, E((0.48, 0.42), (0.14, 0.1), c=RED), E((0.16, 0.6), (0.1, 0.12), c=RED),
                E((0.8, 0.6), (0.1, 0.12), c=RED), {"clip": None}, E((0.48, 0.76), (0.15, 0.13), c=SKIN),
                *eyes(0.48, 0.74, 0.05, 0.02, 0.045, hl=False)]
    return _b(bg, ops)


def coin_bag(bg=None):
    return bag(bg=bg)


def item_bag(bg=None):
    return bag(W, [0, 170, 150], bg, "shroom")


def koopa_kid_bag(bg=None):
    """Orange sack with a blue tie showing Koopa Kid's face (dir 0 file 97)."""
    b = bag([240, 120, 20], [40, 80, 230], bg, None)
    return _b(bg, b["ops"], place(bowser(kid=True), (0.24, 0.36, 0.74, 0.92)))


def lamp(c=(250, 190, 20), bg=None, sign=False):
    """Genie lamp (gold = magic lamp; blue with a no-sign = lucky lamp)."""
    c = list(c)
    ops = [P([(0.4, 0.86), (0.44, 0.74), (0.6, 0.74), (0.64, 0.86)], dark(c)), E((0.52, 0.9), (0.2, 0.05), c=c),
           {"ring": [0.8, 0.54, 0.12, 0.13], "w": 0.05, "c": c},
           P([(0.04, 0.4), (0.14, 0.36), (0.3, 0.52), (0.36, 0.66), (0.2, 0.58)], c),
           E((0.52, 0.6), (0.28, 0.17), c=c), E((0.52, 0.44), (0.12, 0.05), c=dark(c)), E((0.52, 0.36), (0.045, 0.06), c=c),
           E((0.44, 0.54), (0.1, 0.04), c=lite(c, 0.6), rot=-10)]
    if sign:
        ops += [E((0.52, 0.6), (0.11, 0.11), c=W)] + no_sign(0.52, 0.6, 0.11, 0.04)
    return _b(bg, ops)


def magic_lamp(bg=None):
    return lamp(bg=bg)


def lucky_lamp(bg=None):
    return lamp([40, 130, 240], bg, True)


def boo_bell(bg=None):
    c = [200, 150, 250]
    return _b(
        bg, L([(0.62, 0.36), (0.8, 0.08)], 0.09, [70, 50, 140]),
        P([(0.5, 0.26), (0.72, 0.4), (0.7, 0.86), (0.2, 0.8), (0.3, 0.44)], c), E((0.45, 0.82), (0.27, 0.1), c=dark(c, 0.8), rot=8),
        E((0.42, 0.92), (0.06, 0.06), c=[250, 220, 80]), E((0.42, 0.5), (0.07, 0.1), c=lite(c, 0.6), rot=20))


def warp_block(bg=None):
    """Multicolour ? block (cube seen from a corner)."""
    return _b(
        bg, P([(0.5, 0.04), (0.92, 0.2), (0.52, 0.4), (0.08, 0.22)], [250, 230, 40]), P([(0.5, 0.04), (0.92, 0.2), (0.72, 0.3), (0.5, 0.2)], [80, 220, 80]),
        P([(0.08, 0.22), (0.52, 0.4), (0.52, 0.96), (0.1, 0.76)], RED), P([(0.08, 0.5), (0.52, 0.68), (0.52, 0.96), (0.1, 0.76)], [250, 130, 20]),
        P([(0.52, 0.4), (0.92, 0.2), (0.9, 0.74), (0.52, 0.96)], [40, 90, 240]), P([(0.72, 0.3), (0.92, 0.2), (0.9, 0.74), (0.72, 0.85)], [130, 50, 220]),
        qmark(0.3, 0.6, 0.3), qmark(0.72, 0.56, 0.24, [200, 230, 255]))


def glove(bg=None):
    """Open white glove (dueling glove)."""
    g = [226, 226, 236]
    return _b(
        bg, R(0.36, 0.84, 0.72, 0.98, g),
        *[L([(x0, 0.56), (x1, y1)], 0.14, W) for x0, x1, y1 in ((0.34, 0.26, 0.2), (0.46, 0.44, 0.1), (0.6, 0.62, 0.12), (0.7, 0.8, 0.24))],
        L([(0.3, 0.72), (0.1, 0.52)], 0.14, W), E((0.52, 0.66), (0.26, 0.24), c=W),
        L([(0.36, 0.84), (0.72, 0.84)], 0.025, GREY), *[L([(x, 0.46), (x, 0.56)], 0.015, GREY) for x in (0.4, 0.53, 0.65)])


def phone(body=(250, 200, 160), keys=(120, 170, 230), top="shroom", bg=None):
    """Tilted handset with a keypad: cellular shopper (orange mushroom top) / bowser phone (green, horns)."""
    body, keys = list(body), list(keys)
    ops = [P([(0.42, 0.16), (0.92, 0.7), (0.6, 0.99), (0.1, 0.46)], dark(body, 0.7)),
           P([(0.42, 0.22), (0.86, 0.7), (0.6, 0.93), (0.16, 0.46)], body)]
    for i in range(3):
        for j in range(3):
            ops.append(E((0.36 + 0.1 * i + 0.13 * j, 0.47 - 0.085 * i + 0.14 * j), (0.04, 0.04), c=keys))
    if top == "shroom":
        ops += [E((0.68, 0.22), (0.22, 0.17), c=[250, 130, 20], rot=35), E((0.72, 0.16), (0.07, 0.05), c=W), E((0.56, 0.3), (0.05, 0.04), c=W)]
    else:
        ops += [P([(0.24, 0.3), (0.12, 0.06), (0.36, 0.2)], YEL), P([(0.56, 0.12), (0.7, 0.02), (0.64, 0.24)], YEL),
                E((0.4, 0.26), (0.12, 0.05), c=RED, rot=-35)]
    return _b(bg, ops)


def cellular_shopper(bg=None):
    return phone(bg=bg)


def bowser_phone(bg=None):
    return phone([30, 150, 50], [250, 130, 20], "horns", bg)


def bowser_suit(bg=None):
    """Green Bowser mask with yellow horns and red eyes."""
    g = [30, 160, 50]
    return _b(
        bg, P([(0.06, 0.04), (0.34, 0.3), (0.18, 0.46), (0.04, 0.3)], YEL), P([(0.94, 0.04), (0.66, 0.3), (0.82, 0.46), (0.96, 0.3)], YEL),
        E((0.5, 0.5), (0.34, 0.36), c=g), E((0.5, 0.8), (0.28, 0.17), c=[250, 210, 40]),
        P([(0.42, 0.14), (0.5, 0.0), (0.58, 0.14)], RED),
        P([(0.22, 0.4), (0.46, 0.5), (0.44, 0.58), (0.26, 0.54)], RED), P([(0.78, 0.4), (0.54, 0.5), (0.56, 0.58), (0.74, 0.54)], RED),
        brows(0.5, 0.42, 0.15, 0.13, 0.06, 0.05), E((0.44, 0.76), (0.025, 0.02), c=K), E((0.56, 0.76), (0.025, 0.02), c=K))


def watch(bg=None, digit=True):
    """Stopwatch (wacky watch) with a 5 on the dial."""
    o = [250, 120, 0]
    ops = [R(0.44, 0.02, 0.56, 0.16, GREY), R(0.36, 0.0, 0.64, 0.07, [210, 210, 220]), L([(0.76, 0.2), (0.86, 0.12)], 0.07, GREY),
           E((0.5, 0.56), (0.42, 0.42), c=[90, 150, 240]), E((0.5, 0.56), (0.33, 0.33), c=[20, 30, 120])]
    if digit:
        ops += [L([(0.62, 0.38), (0.42, 0.38), (0.4, 0.54), (0.5, 0.52)], 0.07, o), {"arc": [0.5, 0.64, 0.12, 0.12, -90, 150], "w": 0.07, "c": o}]
    else:
        ops += [E((0.5, 0.56), (0.28, 0.28), c=W), L([(0.5, 0.56), (0.5, 0.36)], 0.04), L([(0.5, 0.56), (0.64, 0.6)], 0.04)]
    return _b(bg, ops)


def koopa_kard(bg=None):
    c = [250, 210, 30]
    return _b(
        bg, P([(0.06, 0.52), (0.74, 0.12), (0.96, 0.44), (0.28, 0.9)], dark(c, 0.7)), P([(0.1, 0.52), (0.72, 0.17), (0.9, 0.44), (0.3, 0.84)], c),
        E((0.5, 0.5), (0.24, 0.15), c=W, rot=-28), E((0.5, 0.48), (0.2, 0.12), c=[30, 160, 40], rot=-28),
        L([(0.36, 0.54), (0.64, 0.4)], 0.02, [10, 90, 20]), L([(0.44, 0.4), (0.56, 0.56)], 0.02, [10, 90, 20]))


def barter_box(bg=None):
    """Red box with a white up-arrow and a purple strap."""
    return _b(
        bg, P([(0.5, 0.06), (0.9, 0.26), (0.9, 0.74), (0.5, 0.96), (0.1, 0.74), (0.1, 0.26)], [200, 20, 30]),
        P([(0.5, 0.06), (0.9, 0.26), (0.5, 0.46), (0.1, 0.26)], [240, 70, 70]), L([(0.5, 0.46), (0.5, 0.96)], 0.02, [120, 0, 10]),
        P([(0.5, 0.12), (0.72, 0.27), (0.58, 0.3), (0.58, 0.38), (0.42, 0.38), (0.42, 0.3), (0.28, 0.27)], W),
        P([(0.3, 0.44), (0.44, 0.62), (0.36, 0.62), (0.36, 0.78), (0.24, 0.72), (0.24, 0.58), (0.16, 0.56)], W),
        L([(0.06, 0.6), (0.5, 0.8), (0.94, 0.6)], 0.07, [130, 70, 190]))


def spray(bg=None):
    """Boo repellant: yellow spray can with a no-ghost sign."""
    return _b(
        bg, R(0.4, 0.04, 0.6, 0.16, [210, 210, 220]), R(0.34, 0.14, 0.66, 0.24, GREY),
        R(0.22, 0.22, 0.78, 0.96, [250, 220, 20]), R(0.22, 0.22, 0.32, 0.96, [255, 244, 140]), R(0.7, 0.22, 0.78, 0.96, [200, 160, 0]),
        E((0.5, 0.6), (0.2, 0.22), c=W), E((0.5, 0.6), (0.1, 0.11), c=[200, 206, 226]),
        E((0.46, 0.57), (0.02, 0.03), c=K), E((0.54, 0.57), (0.02, 0.03), c=K), *no_sign(0.5, 0.6, 0.21, 0.05))


def bowser_bomb(bg=None):
    """Dark green ball with a red Bowser emblem and a stem (dir 0 file 118)."""
    return _b(
        bg, L([(0.56, 0.2), (0.66, 0.04)], 0.06, [120, 80, 30]), {"sphere": [0.5, 0.58, 0.4, 0.4], "c": [20, 130, 70]},
        E((0.5, 0.6), (0.17, 0.15), c=RED), P([(0.3, 0.4), (0.42, 0.5), (0.34, 0.58)], RED), P([(0.7, 0.4), (0.58, 0.5), (0.66, 0.58)], RED),
        E((0.44, 0.57), (0.03, 0.02), c=K, rot=25), E((0.56, 0.57), (0.03, 0.02), c=K, rot=-25), R(0.42, 0.65, 0.58, 0.68, K))


def winged_arrow(bg=None):
    """Red arrow pointing right with white wings and eyes (dir 0 file 116)."""
    return _b(
        bg, P([(0.3, 0.3), (0.04, 0.14), (0.12, 0.3), (0.02, 0.36), (0.14, 0.44), (0.3, 0.5)], W),
        P([(0.2, 0.36), (0.56, 0.36), (0.56, 0.14), (0.98, 0.56), (0.56, 0.98), (0.56, 0.76), (0.2, 0.76)], dark(RED, 0.6)),
        P([(0.24, 0.41), (0.6, 0.41), (0.6, 0.25), (0.91, 0.56), (0.6, 0.87), (0.6, 0.71), (0.24, 0.71)], RED),
        eyes(0.68, 0.56, 0.06, 0.03, 0.08, hl=False))


# ------------------------------------------------------------------ registry
HEADS = {
    "waluigi": waluigi, "daisy": daisy, "toad": toad, "koopa": koopa, "goomba": goomba, "boo": boo, "bowser": bowser,
    "baby_bowser": baby_bowser, "koopa_kid": baby_bowser, "shy_guy": shy_guy, "game_guy": game_guy, "bobomb": bobomb,
    "thwomp": thwomp, "whomp": whomp, "piranha": piranha, "chain_chomp": chain_chomp, "snowman": snowman, "tumble": tumble,
    "millennium_star": millennium_star, "blooper": blooper, "fish": fish, "mole": mole, "tree": tree, "evil_tree": evil_tree,
    "girl": girl, "bigmouth": bigmouth, "pipe": pipe, "glove_guy": glove_guy, "cone_guy": cone_guy, "disc_guy": disc_guy,
}
ITEMS = {
    "mushroom": mushroom, "golden_mushroom": lambda bg=None: mushroom("golden", bg), "poison_mushroom": lambda bg=None: mushroom("poison", bg),
    "reverse_mushroom": lambda bg=None: mushroom("reverse", bg), "key": key, "star": star, "coin": coin, "chest": chest,
    "plunder_chest": plunder_chest, "coin_bag": coin_bag, "item_bag": item_bag, "koopa_kid_bag": koopa_kid_bag, "magic_lamp": magic_lamp,
    "lucky_lamp": lucky_lamp, "boo_bell": boo_bell, "warp_block": warp_block, "glove": glove, "dueling_glove": glove,
    "cellular_shopper": cellular_shopper, "bowser_phone": bowser_phone, "bowser_suit": bowser_suit, "watch": watch, "wacky_watch": watch,
    "koopa_kard": koopa_kard, "barter_box": barter_box, "spray": spray, "boo_repellant": spray, "bowser_bomb": bowser_bomb,
    "winged_arrow": winged_arrow,
}


def head(who, bg=None):
    """Bust/head of a player (PLAYERS) or of any character in HEADS, on the backdrop bg."""
    if who in M._PORTRAIT:
        return _b(bg, list(M._PORTRAIT[who]["ops"]))
    return HEADS[who](bg=bg)


def item(name, bg=None):
    return ITEMS[name](bg=bg)


def get(name, bg=None):
    """Head or item by name."""
    return head(name, bg) if name in M._PORTRAIT or name in HEADS else item(name, bg)


# ------------------------------------------------------------------ hand cursors (for images with a kept hand silhouette)
def hand(c=W, emblem=None, cuff=(0.72, 0.8), bg=None):
    """Painter (not a brief) for a hand-shaped kept silhouette: glove colour, soft shading towards the cuff, dark edge, optional emblem
    ("W" purple zigzag, "L" yellow inverted L) on the back of the hand."""
    c = list(c)
    ops = [{"glow": [cuff[0], cuff[1], 0.5, 0.5], "c": dark(c, 0.72)}, {"glow": [0.36, 0.34, 0.3, 0.3], "c": lite(c, 0.5)}]
    if emblem == "W":
        ops.append(L([(0.4, 0.46), (0.46, 0.58), (0.52, 0.48), (0.58, 0.6), (0.66, 0.5)], 0.045, [110, 40, 200]))
    elif emblem == "L":
        ops += [R(0.44, 0.42, 0.62, 0.66, [250, 220, 40]), L([(0.5, 0.62), (0.5, 0.47), (0.58, 0.47)], 0.04, [150, 110, 0])]
    b, edge_c = brief(c, *ops), dark(c, 0.2)

    def fn(w, h, d, alpha):
        out = facepaint.render(b, w, h, alpha=alpha)
        if alpha is not None:                 # 1 px dark edge just inside the visible part of the kept silhouette
            a = np.asarray(alpha) >= 128
            pad = np.pad(a, 1)
            inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
            out[a & ~inner, :3] = edge_c
        return out
    return fn
