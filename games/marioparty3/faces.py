"""Character face textures of Mario Party 3, drawn from our own descriptions.

Every playable character's model has one face texture per expression (the same list for each character, see
EXPR_FILES). A face is described once per character as a function of the expression (eye state, brow tilt, mouth)
and rendered with cleanroom.gfx.facepaint. Nothing here comes from retail pixels: positions are our own layout of
"two eyes, brows, moustache / mouth" inside the texture square, chosen so the features land where the model's
UVs expect them.
"""
import numpy as np

from cleanroom.gfx import facepaint
from .mp1_briefs import E, L, P, R, K, W, brief

# expression = (eyes, brows, mouth)
#   eyes: open | half | closed | arc (smiling, closed) | x | dot;  brows: flat | angry | sad;  mouth: "" | open | o | grit
EXPR = {
    "normal": ("open", "flat", ""), "closed": ("closed", "flat", ""), "half": ("half", "flat", ""),
    "happy": ("open", "flat", "open"), "sad": ("half", "sad", ""), "angry": ("open", "angry", "grit"),
    "ko": ("x", "flat", ""), "surprise": ("open", "sad", "o"), "determined": ("open", "angry", ""),
    "happy_half": ("half", "flat", "open"), "happy_closed": ("arc", "flat", "open"),
    "cry": ("open", "sad", "open"), "blush": ("closed", "flat", "kiss"),
}
# file -> expression for the seven characters of dirs 2-8 (image key p0 unless listed)
EXPR_FILES = {"160/b7": "normal", "161/b7": "normal", "162/b7": "normal", "163/p0": "closed", "164/p0": "half",
              "164/p1": "closed", "164/p2": "closed", "165/p0": "happy", "166/p0": "sad", "167/p0": "angry",
              "168/p0": "ko", "169/p0": "surprise", "170/p0": "determined", "171/p0": "happy",
              "171/p1": "happy_half", "171/p2": "happy_closed"}
DAISY_FILES = {"0/b7": "normal", "1/b7": "normal", "2/b7": "normal", "3/b7": "normal", "26/p0": "closed",
               "27/p0": "half", "27/p1": "closed", "28/p0": "happy_closed", "29/p0": "closed", "30/p0": "closed",
               "31/p0": "cry", "32/p0": "blush", "33/p0": "blush", "34/p0": "closed", "35/p0": "cry",
               "36/p0": "surprise", "37/p0": "normal", "38/p0": "normal", "39/p0": "happy_closed",
               "39/p1": "happy_closed", "39/p2": "happy_closed"}


def mirror(ops):
    """Left-half primitives -> the same on the right half."""
    out = []
    for op in ops:
        o = dict(op)
        if "e" in o:
            o["e"] = [1 - o["e"][0]] + list(o["e"][1:])
            if "rot" in o:
                o["rot"] = -o["rot"]
        elif "poly" in o:
            o["poly"] = [(1 - x, y) for x, y in o["poly"]]
        elif "line" in o:
            o["line"] = [(1 - x, y) for x, y in o["line"]]
        elif "arc" in o:
            cx, cy, rx, ry, a0, a1 = o["arc"]
            o["arc"] = [1 - cx, cy, rx, ry, 180 - a1, 180 - a0]
        elif "rect" in o:
            x0, y0, x1, y1 = o["rect"]
            o["rect"] = [1 - x1, y0, 1 - x0, y1]
        out.append(o)
    return out


def eyeball(cx, cy, rx, ry, state, iris, lid, look=(0.0, 0.0), ow=0.022, lidc=K, pupil=0.4, irisr=0.66):
    """One eye. look is in eye radii."""
    if state in ("open", "half"):
        ix, iy = cx + look[0] * rx, cy + look[1] * ry
        ops = [E((cx, cy), (rx + ow, ry + ow), c=K), E((cx, cy), (rx, ry), c=W), {"clip": [cx, cy, rx, ry]},
               E((ix, iy), (rx * irisr, ry * irisr), c=iris), E((ix, iy), (rx * pupil, ry * pupil), c=K),
               E((ix - rx * 0.16, iy - ry * 0.2), (rx * 0.14, ry * 0.12), c=W)]
        if state == "half":
            ops += [R(cx - rx - 0.05, cy - ry - 0.05, cx + rx + 0.05, cy - ry * 0.05, lid), {"clip": None},
                    L([(cx - rx - ow, cy - ry * 0.05), (cx + rx + ow, cy - ry * 0.05)], 0.028, lidc)]
        else:
            ops.append({"clip": None})
        return ops
    if state == "closed":
        return [{"arc": [cx, cy - ry * 0.1, rx, ry * 0.45, 0, 180], "w": 0.03, "c": lidc}]
    if state == "arc":
        return [{"arc": [cx, cy + ry * 0.2, rx, ry * 0.5, 180, 360], "w": 0.035, "c": lidc}]
    if state == "x":
        r = min(rx, ry) * 0.8
        return [E((cx, cy), (rx + ow, ry + ow), c=K), E((cx, cy), (rx, ry), c=W),
                L([(cx - r, cy - r), (cx + r, cy + r)], 0.03, K), L([(cx + r, cy - r), (cx - r, cy + r)], 0.03, K)]
    return [E((cx, cy), (rx * 0.4 + ow, rx * 0.4 + ow), c=K), E((cx, cy), (rx * 0.4, rx * 0.4), c=W)]      # dot


def brow(pts, tilt, w, c=K):
    """Left brow (outer end first); tilt: angry lowers the inner end, sad raises it."""
    n = len(pts) - 1
    d = {"flat": 0.0, "angry": 0.07, "sad": -0.05}[tilt]
    return L([(x, y + d * (i / n) - d * 0.4) for i, (x, y) in enumerate(pts)], w, c)


def mouth_ops(kind, cx, cy, s=1.0, lip=(226, 60, 80)):
    if kind == "open":
        return [E((cx, cy), (0.11 * s, 0.075 * s), c=[110, 16, 24]), E((cx, cy + 0.035 * s), (0.07 * s, 0.035 * s), c=[250, 130, 150])]
    if kind == "o":
        return [E((cx, cy), (0.045 * s, 0.05 * s), c=[150, 20, 30])]
    if kind == "kiss":
        return [E((cx, cy), (0.05 * s, 0.03 * s), c=list(lip))]
    if kind == "grit":
        return [R(cx - 0.12 * s, cy - 0.035 * s, cx + 0.12 * s, cy + 0.035 * s, K),
                R(cx - 0.105 * s, cy - 0.022 * s, cx + 0.105 * s, cy + 0.022 * s, W),
                L([(cx, cy - 0.03 * s), (cx, cy + 0.03 * s)], 0.012, K)]
    return []


# ------------------------------------------------------------------ the eight characters

SKIN = [252, 190, 136]
BLUE = [40, 130, 230]


def mario(ex):
    eyes, brows, mouth = EXPR[ex]
    look = (0.0, 0.25) if ex == "sad" else (0.0, 0.0)
    left = [*eyeball(0.36, 0.4, 0.075, 0.15, eyes, BLUE, SKIN, look),
            brow([(0.2, 0.22), (0.27, 0.13), (0.36, 0.1), (0.44, 0.15)], brows, 0.05)]
    stache = P([(0.5, 0.58), (0.4, 0.55), (0.24, 0.57), (0.1, 0.52), (0.03, 0.6), (0.06, 0.72), (0.14, 0.8), (0.22, 0.77),
                (0.3, 0.86), (0.4, 0.82), (0.5, 0.88)], K)
    ops = left + mirror(left) + [stache, *mirror([stache])]
    ops += mouth_ops(mouth, 0.5, 0.93, 1.0)
    return brief(SKIN, *ops)


def luigi(ex):
    eyes, brows, mouth = EXPR[ex]
    cyan = [40, 190, 230]
    ops = [*eyeball(0.42, 0.42, 0.105, 0.2, eyes, cyan, SKIN, (0.15, 0.0)),
           *eyeball(0.68, 0.42, 0.105, 0.2, eyes, cyan, SKIN, (-0.15, 0.0)),
           brow([(0.26, 0.2), (0.34, 0.12), (0.46, 0.12)], brows, 0.035),
           *mirror([brow([(0.16, 0.2), (0.24, 0.12), (0.36, 0.12)], brows, 0.035)]),
           P([(0, 0.7), (0.16, 0.8), (0.4, 0.74), (0.56, 0.6), (0.62, 0.7), (0.5, 0.9), (0.24, 0.98), (0, 0.9)], K),
           P([(0.72, 0.84), (0.84, 0.76), (1, 0.74), (1, 1), (0.7, 1)], [112, 60, 20])]
    if mouth in ("open", "o"):
        ops += [P([(0, 0.93), (0.2, 0.98), (0.3, 0.97), (0.2, 1), (0, 1)], [210, 20, 30])]
    return brief(SKIN, *ops)


def yoshi(ex):
    eyes, brows, mouth = EXPR[ex]
    green, dark = [0, 150, 16], [0, 104, 10]
    base = [P([(0, 0), (1, 0), (1, 0.1), (0.8, 0.2), (0.5, 0.14), (0.2, 0.2), (0, 0.1)], dark)]
    if eyes in ("closed", "arc"):
        lids = [E((0.38, 0.64), (0.2, 0.34), c=dark), E((0.62, 0.64), (0.2, 0.34), c=dark),
                E((0.38, 0.62), (0.18, 0.31), c=green), E((0.62, 0.62), (0.18, 0.31), c=green),
                {"arc": [0.38, 0.72, 0.13, 0.08, 0, 180], "w": 0.03, "c": dark}, {"arc": [0.62, 0.72, 0.13, 0.08, 0, 180], "w": 0.03, "c": dark}]
        return brief(green, *base, *lids)
    white = [E((0.38, 0.64), (0.2, 0.34), c=dark), E((0.62, 0.64), (0.2, 0.34), c=dark),
             E((0.38, 0.64), (0.18, 0.32), c=W), E((0.62, 0.64), (0.18, 0.32), c=W)]
    if eyes == "x":
        pup = [{"arc": [0.5, 0.64, 0.1, 0.1, 0, 300], "w": 0.03, "c": [130, 130, 150]},
               {"arc": [0.5, 0.64, 0.05, 0.05, 90, 400], "w": 0.03, "c": [130, 130, 150]}]
    else:
        dy = 0.08 if ex == "sad" else 0.0
        pup = []
        for cx in (0.44, 0.56):
            pup += [E((cx, 0.64 + dy), (0.05, 0.15), c=K), E((cx, 0.7 + dy), (0.03, 0.07), c=[30, 60, 230]),
                    E((cx - 0.012, 0.56 + dy), (0.016, 0.04), c=W)]
    ops = base + white + pup
    if eyes == "half":
        ops += [{"clip": [0.5, 0.64, 0.4, 0.34]}, R(0, 0.2, 1, 0.56, green), {"clip": None}, L([(0.2, 0.56), (0.8, 0.56)], 0.03, dark)]
    if brows == "angry":
        ops += [P([(0.18, 0.28), (0.5, 0.5), (0.82, 0.28), (0.82, 0.2), (0.18, 0.2)], green), L([(0.2, 0.3), (0.5, 0.5), (0.8, 0.3)], 0.03, dark)]
    return brief(green, *ops)


def _wario_side(ex):
    """Upright half of the face as the model wraps it (texture is this, turned a quarter)."""
    eyes, brows, mouth = EXPR[ex]
    lid = [120, 170, 240]
    look = (0.0, 0.0)
    left = [E((0.24, 0.3), (0.2, 0.2), c=lid), *eyeball(0.24, 0.34, 0.15, 0.13, eyes, [30, 30, 30], lid, look, pupil=0.3, irisr=0.3),
            brow([(0.04, 0.2), (0.2, 0.06), (0.42, 0.14)], brows, 0.07)]
    ops = left + mirror(left)
    red = [226, 30, 30]
    ops += [R(0.04, 0.66, 0.96, 0.94, K), R(0.07, 0.69, 0.93, 0.91, W), R(0.04, 0.66, 0.12, 0.94, red), R(0.88, 0.66, 0.96, 0.94, red)]
    if mouth in ("open", "o"):
        ops += [R(0.2, 0.74, 0.8, 0.86, [200, 20, 30])]
    return brief(SKIN, *ops)


def wario(ex):
    def paint(w, h, d, alpha):
        up = facepaint.render(_wario_side(ex), h, w)
        return np.ascontiguousarray(up.transpose(1, 0, 2)[::-1])
    return paint


def wario_front(ex):
    """The simple model's whole face (files 162, 163): eyes, zigzag moustache, grin."""
    eyes = EXPR[ex][0]
    left = [*eyeball(0.3, 0.3, 0.1, 0.09, eyes, [30, 30, 30], SKIN, pupil=0.35, irisr=0.35),
            brow([(0.12, 0.22), (0.26, 0.1), (0.44, 0.2)], "angry", 0.06)]
    zig = P([(0.5, 0.5), (0.36, 0.44), (0.26, 0.54), (0.16, 0.44), (0.06, 0.56), (0.02, 0.5), (0.04, 0.7), (0.14, 0.62), (0.24, 0.72),
             (0.36, 0.6), (0.5, 0.66)], K)
    ops = left + mirror(left) + [E((0.5, 0.44), (0.1, 0.08), c=[250, 150, 140]), zig, *mirror([zig]),
                                 P([(0.14, 0.7), (0.86, 0.7), (0.76, 0.92), (0.24, 0.92)], K),
                                 P([(0.18, 0.72), (0.82, 0.72), (0.74, 0.88), (0.26, 0.88)], W)]
    ops += [L([(x, 0.72), (x, 0.88)], 0.012, K) for x in (0.34, 0.5, 0.66)]
    return brief(SKIN, *ops)


def dk(ex):
    eyes, brows, mouth = EXPR[ex]
    fur, tan = [128, 52, 12], [250, 196, 132]
    ops = [P([(0, 0.46), (0.5, 0.4), (0.84, 0.34), (0.84, 1), (0, 1)], tan), P([(0.84, 0.56), (1, 0.52), (1, 0.92), (0.84, 0.94)], tan),
           {"arc": [0.93, 0.74, 0.05, 0.1, 60, 300], "w": 0.02, "c": [190, 120, 60]},
           P([(0.46, 0.2), (1, 0.2), (1, 0.34), (0.84, 0.34), (0.5, 0.4)], tan)]
    if eyes in ("open", "half", "x", "dot"):
        ops += [*eyeball(0.64, 0.1, 0.1, 0.075, eyes, [30, 20, 10], fur, pupil=0.45, irisr=0.45),
                *eyeball(0.9, 0.1, 0.1, 0.075, eyes, [30, 20, 10], fur, pupil=0.45, irisr=0.45)]
    else:
        ops += [{"arc": [0.64, 0.12, 0.09, 0.06, 180, 360], "w": 0.028, "c": K}, {"arc": [0.9, 0.12, 0.09, 0.06, 180, 360], "w": 0.028, "c": K}]
    if brows == "angry":
        ops += [L([(0.5, 0.0), (0.76, 0.08)], 0.05, K), L([(1, 0.0), (0.8, 0.08)], 0.05, K)]
    line = [150, 80, 30]
    if mouth in ("open", "grit"):
        ops += [P([(0.06, 0.68), (0.4, 0.74), (0.72, 0.64), (0.6, 0.86), (0.36, 0.92), (0.14, 0.84)], [120, 20, 20]),
                P([(0.1, 0.7), (0.4, 0.76), (0.68, 0.67), (0.66, 0.72), (0.4, 0.8), (0.12, 0.75)], W)]
    elif ex in ("sad", "ko", "surprise"):
        ops += [L([(0.1, 0.8), (0.24, 0.74), (0.4, 0.8), (0.56, 0.74), (0.7, 0.8)], 0.025, line)]
    else:
        ops += [{"arc": [0.4, 0.62, 0.34, 0.16, 20, 160], "w": 0.03, "c": line}]
    ops += [E((0.3, 0.5), (0.025, 0.02), c=line), E((0.5, 0.49), (0.025, 0.02), c=line)]
    return brief(fur, *ops)


def _lady(skin, iris, ex, lip, mouth_y):
    eyes, brows, mouth = EXPR[ex]
    lash = [20, 14, 30]
    cx, cy, rx, ry = 0.24, 0.38, 0.105, 0.14
    if eyes in ("open", "half"):
        left = [*eyeball(cx, cy, rx, ry, eyes, iris, skin, (0.2, 0.05), ow=0.0, pupil=0.36, irisr=0.72),
                {"arc": [cx, cy, rx + 0.01, ry + 0.01, 180, 360], "w": 0.035, "c": lash},
                L([(cx - rx, cy - 0.02), (cx - rx - 0.06, cy - 0.09)], 0.022, lash), L([(cx - rx + 0.02, cy - 0.08), (cx - rx - 0.02, cy - 0.15)], 0.02, lash)]
    elif eyes == "arc":
        left = [{"arc": [cx, cy + 0.03, rx, ry * 0.5, 180, 360], "w": 0.03, "c": lash}]
    elif eyes == "x":
        left = [{"arc": [cx, cy, rx, ry * 0.4, 0, 180], "w": 0.03, "c": lash}]
    else:
        left = [{"arc": [cx, cy - 0.02, rx, ry * 0.5, 0, 180], "w": 0.03, "c": lash},
                L([(cx - rx, cy + 0.01), (cx - rx - 0.05, cy + 0.05)], 0.02, lash)]
    left.append(brow([(0.1, 0.2), (0.2, 0.15), (0.34, 0.17)], brows, 0.016, [150, 90, 50]))
    ops = left + mirror(left)
    if ex == "blush":
        ops += [E((0.2, 0.62), (0.12, 0.07), c=[250, 150, 150]), E((0.8, 0.62), (0.12, 0.07), c=[250, 150, 150])]
    if ex == "cry":
        ops += [E((0.9, 0.56), (0.03, 0.06), c=[150, 210, 250])]
    if mouth == "open":
        ops += [P([(0.4, mouth_y - 0.03), (0.6, mouth_y - 0.03), (0.5, mouth_y + 0.08)], [200, 30, 60])]
    elif mouth == "o":
        ops += [E((0.5, mouth_y), (0.04, 0.045), c=[200, 30, 60])]
    elif mouth == "kiss":
        ops += [E((0.5, mouth_y), (0.05, 0.035), c=lip)]
    else:
        ops += [E((0.5, mouth_y), (0.065, 0.02), c=lip), E((0.5, mouth_y + 0.02), (0.04, 0.015), c=[min(255, v + 30) for v in lip])]
    return brief(skin, *ops)


def peach(ex):
    return _lady([255, 206, 178], [40, 90, 220], ex, [240, 90, 150], 0.88)


def daisy(ex):
    return _lady([250, 172, 124], [40, 90, 220], ex, [226, 110, 90], 0.84)


def waluigi(ex):
    eyes, brows, mouth = EXPR[ex]
    skin, lid = [216, 142, 84], [150, 170, 230]
    cx, cy = 0.3, 0.33
    left = [E((cx, cy - 0.03), (0.17, 0.13), c=lid), *eyeball(cx, cy, 0.14, 0.09, eyes, [30, 30, 30], lid, (0.3, 0.1), pupil=0.3, irisr=0.3),
            P([(0.06, 0.1), (0.3, 0.14), (0.5, 0.3), (0.5, 0.2), (0.34, 0.06), (0.1, 0.02)], K),
            L([(0.1, 0.52), (0.2, 0.6), (0.14, 0.72)], 0.02, [150, 84, 40])]
    if brows != "angry" and eyes in ("closed", "arc"):
        left[2] = P([(0.06, 0.16), (0.3, 0.18), (0.5, 0.24), (0.5, 0.16), (0.3, 0.08), (0.08, 0.08)], K)
    ops = left + mirror(left)
    ops += [R(0.2, 0.68, 0.8, 0.9, K), R(0.23, 0.71, 0.77, 0.87, W), L([(0.23, 0.79), (0.77, 0.79)], 0.014, K)]
    ops += [L([(x, 0.71), (x, 0.87)], 0.012, K) for x in (0.34, 0.45, 0.55, 0.66)]
    if mouth in ("open", "o"):
        ops += [R(0.3, 0.75, 0.7, 0.83, [190, 20, 30])]
    return brief(skin, *ops)


WHO = {2: mario, 3: luigi, 4: yoshi, 5: wario, 6: dk, 7: peach, 8: waluigi, 9: daisy}


def table():
    """{spec key: brief or callable} for every face texture."""
    out = {}
    for d, fn in WHO.items():
        for fk, ex in (DAISY_FILES if d == 9 else EXPR_FILES).items():
            if d == 5 and fk.split("/")[0] in ("162", "163"):
                out[f"{d}/{fk}"] = wario_front(ex)
            else:
                out[f"{d}/{fk}"] = fn(ex)
    return out
