"""MainFS dirs 16-18: title screen, language flags, hand cursors, mode/game-setup banners and their model textures.

Everything is hand-written primitives and typed text (colours picked by eye); pictures come from `icons.py`.
Left alone on purpose: boot logos 17/0-17/2 (trademarks), 17/5 pattern, speech bubbles 17/7-17/13, plain masks,
gradient strips and palette textures."""
import numpy as np
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L
from . import icons as I

B = {}
T = {}

NAVY = [24, 16, 96]
_YEL = ([255, 246, 90], [250, 170, 0])
_FIRE = ([255, 240, 60], [250, 60, 10])


def _grad(top, bottom, *ops):
    return brief({"grad": [list(top), list(bottom)]}, *ops)


def _put(out, text, box, top, bottom, edge, own=False, **opt):
    """One typeset word blended into box (x0, y0, x1, y1; normalised) of an RGBA float picture.
    own=True also makes the text opaque where the picture was transparent."""
    h, w = out.shape[:2]
    x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(round(box[2] * w)), int(round(box[3] * h))
    g = typeset(x1 - x0, y1 - y0, text, top, bottom, edge, **opt)
    a = g[..., 3:] / 255
    reg = out[y0:y1, x0:x1]
    reg[..., :3] = reg[..., :3] * (1 - a) + g[..., :3] * a
    if own:
        reg[..., 3] = np.maximum(reg[..., 3], np.where(g[..., 3] >= 96, 255, 0))
    return out


def _words(base, *words, own=False):
    """Painter: a brief on the kept silhouette (or an empty picture when base is None) + typeset words.
    words = (text, box, top, bottom, edge, opts)."""
    def fn(w, h, d, alpha):
        if base is None:
            out = np.zeros((h, w, 4), np.float32)
        else:
            out = np.asarray(facepaint.render(base, w, h, alpha=alpha), np.float32)
        for text, box, top, bottom, edge, opt in words:
            _put(out, text, box, top, bottom, edge, own=own or base is None, **opt)
        return out
    return fn


# ------------------------------------------------------------------ 16: title screen
def _logo(w, h, d, alpha):
    """Game logo: our own lettering (one colour per letter) and a big golden 3 on the kept silhouette."""
    out = np.asarray(facepaint.render(_grad(NAVY, [250, 170, 30], R(0, 0, 1, 0.8, NAVY)), w, h, alpha=alpha), np.float32)
    cols = ["red", "grn", "blu", "red", "grn", "", "red", "blu", "grn", "blu", "red"]
    letters = "MARIO PARTY"
    x, unit = 0.012, 0.0775
    for ch, col in zip(letters, cols):
        lw = unit * {"M": 1.2, "I": 0.5, " ": 0.3}.get(ch, 1.0)
        if ch != " ":
            _put(out, ch, (x - 0.006, 0.32, x + lw + 0.006, 0.84), *M._RAINBOW[col], [16, 8, 60], th=4.6, pad=1)
        x += lw
    _put(out, "3", (0.795, 0.1, 1.0, 0.92), [255, 250, 110], [250, 190, 0], [120, 30, 10], th=6.0, pad=2, edge_px=1.5)
    return out


B["16/2/p0"] = _logo
_PS = brief(NAVY, R(0, 0.2, 1, 0.8, [20, 150, 140]), R(0, 0.28, 1, 0.72, [30, 40, 150]))
B["16/3/p0"] = _words(_PS, ("PRESS START", (0.18, 0.2, 0.82, 0.86), *_FIRE, [110, 10, 10], {"th": 1.7, "pad": 1}))
B["16/3/p1"] = _words(_PS, ("PRESS START", (0.05, 0.4, 0.95, 0.98), *_FIRE, [110, 10, 10], {"th": 1.7, "pad": 1}))
_NC = brief([10, 40, 240], R(0, 0, 1, 0.04, [230, 20, 20]), R(0, 0.96, 1, 1, [230, 20, 20]), R(0, 0, 0.006, 1, [230, 20, 20]),
            R(0.994, 0, 1, 1, [230, 20, 20]))
B["16/5/p0"] = _words(_NC, ("No Controller. Please turn the power OFF", (0.01, 0.03, 0.99, 0.5), W, W, [10, 10, 60], {"th": 0.8, "pad": 1}),
                      ("and insert a Controller into the 1P Socket.", (0.01, 0.5, 0.99, 0.97), W, W, [10, 10, 60], {"th": 0.8, "pad": 1}))


def _title(order, sky, hill, sun):
    """Title card in our own layout: sky, sun, clouds, confetti stars and the eight players in two rows on a hill."""
    ops = [{"glow": [sun[0], sun[1], 0.42, 0.5], "c": [255, 250, 200]}, E(sun, (0.085, 0.113), c=[255, 240, 120])]
    for cx, cy, s in ((0.14, 0.2, 1.0), (0.44, 0.1, 0.8), (0.9, 0.3, 0.9), (0.62, 0.3, 0.6)):
        ops += [E((cx, cy), (0.1 * s, 0.045 * s), c=W), E((cx - 0.05 * s, cy - 0.03 * s), (0.05 * s, 0.045 * s), c=W),
                E((cx + 0.04 * s, cy - 0.04 * s), (0.06 * s, 0.055 * s), c=W)]
    for i, (cx, cy) in enumerate(((0.06, 0.06), (0.3, 0.26), (0.56, 0.05), (0.74, 0.2), (0.95, 0.08), (0.2, 0.36), (0.84, 0.4))):
        c = ([255, 220, 0], [250, 90, 160], [90, 220, 90], [250, 140, 20])[i % 4]
        ops.append(P([(x, cy + (y - cy) * 4 / 3) for x, y in star_pts(cx, cy, 0.03, 0.013)], c))
    ops.append(E((0.5, 1.0), (1.3, 0.47), c=dark_hill(hill)))
    for i, who in enumerate(order[:4]):                 # back row
        ops += I.place(I.head(who), (0.1 + 0.2 * i, 0.39, 0.3 + 0.2 * i, 0.66))
    ops.append(E((0.5, 1.12), (1.4, 0.49), c=hill))
    ops += [E((0.07, 0.72), (0.03, 0.02), c=[250, 90, 120]), E((0.94, 0.7), (0.03, 0.02), c=[250, 230, 60])]
    for i, who in enumerate(order[4:]):                 # front row
        ops += I.place(I.head(who), (0.02 + 0.24 * i, 0.68, 0.26 + 0.24 * i, 1.0))
    b = _grad(sky[0], sky[1], *ops)

    def fn(w, h, d, alpha):                             # the notice is plain typed text
        out = np.asarray(facepaint.render(b, w, h, alpha=alpha), np.float32)
        return _put(out, "CLEAN ROOM BUILD: ALL ART REDRAWN", (0.01, 0.93, 0.99, 0.992), W, W, [10, 20, 40], th=0.9, pad=1)
    return fn


def dark_hill(c):
    return [int(v * 0.72) for v in c]


B["16/0/p0"] = _title(("luigi", "peach", "daisy", "waluigi", "mario", "yoshi", "dk", "wario"),
                      ([40, 130, 250], [170, 226, 255]), [70, 200, 60], (0.82, 0.14))
B["16/1/p0"] = _title(("wario", "daisy", "peach", "dk", "yoshi", "luigi", "mario", "waluigi"),
                      ([90, 80, 230], [255, 200, 170]), [60, 180, 80], (0.2, 0.16))

# ------------------------------------------------------------------ 17: flags, hand cursors, practice strips
_UK_B, _UK_R = [10, 30, 150], [220, 20, 40]
B["17/3/p0"] = brief(_UK_B, L([(0, 0), (1, 1)], 0.2, W), L([(0, 1), (1, 0)], 0.2, W), L([(0, 0), (1, 1)], 0.07, _UK_R),
                     L([(0, 1), (1, 0)], 0.07, _UK_R), R(0.39, 0, 0.61, 1, W), R(0, 0.33, 1, 0.67, W),
                     R(0.435, 0, 0.565, 1, _UK_R), R(0, 0.4, 1, 0.6, _UK_R))
B["17/4/p0"] = brief(W, R(0, 0, 0.3333, 1, [0, 40, 170]), R(0.6667, 0, 1, 1, [236, 30, 40]))
B["17/6/p0"] = brief([226, 10, 10], R(0, 0, 1, 0.3333, [10, 10, 10]), R(0, 0.6667, 1, 1, [255, 214, 0]))

for _i, _cuff in enumerate(((0.78, 0.2), (0.72, 0.9), (0.72, 0.9), (0.75, 0.8))):
    B[f"17/14/p{_i}"] = I.hand(W, cuff=_cuff)


def _hand_tag(text, box, top, bottom, edge, th):
    """Pointing glove on the kept silhouette with the player's number (or COM) in the player's colour."""
    hand = I.hand(W, cuff=(0.8, 0.3))

    def fn(w, h, d, alpha):
        out = np.asarray(hand(w, h, d, alpha), np.float32)
        return _put(out, text, box, top, bottom, edge, own=True, th=th, pad=1)
    return fn


for _i, (_t, _col, _edge) in enumerate((("1", "red", [80, 0, 0]), ("2", "blu", [0, 10, 90]), ("3", "yel", [110, 40, 0]),
                                        ("4", "grn", [0, 60, 0]))):
    B[f"17/15/p{_i}"] = _hand_tag(_t, (0.24, 0.0, 0.76, 0.6), *M._RAINBOW[_col], _edge, 1.9)
B["17/15/p4"] = _hand_tag("COM", (0.0, 0.0, 1.0, 0.56), [120, 240, 255], [0, 150, 230], [0, 30, 90], 1.4)

_PRAC = ([255, 226, 60], [250, 130, 0], [90, 20, 150])
T["17/16/p0"] = ("PRACTICE", *_PRAC, {"th": 1.6, "pad": 1})


def _quit_practice(w, h, d, alpha):
    out = np.zeros((h, w, 4), np.float32)
    _put(out, "QUIT", (0.0, 0, 0.26, 1), *_PRAC, own=True, th=1.6, pad=1)
    _put(out, "PRACTICE", (0.31, 0, 0.85, 1), *_PRAC, own=True, th=1.6, pad=1)
    x0, x1 = int(0.875 * w), w - 1                     # the R button: a grey key
    out[2:h - 1, x0:x1] = [150, 150, 160, 255]
    out[3:h - 2, x0 + 1:x1 - 1, :3] = [196, 196, 206]
    _put(out, "R", (0.885, 0.12, 0.99, 0.95), W, [230, 230, 240], [60, 60, 80], th=1.3, pad=1)
    return out


B["17/17/p0"] = _quit_practice

# ------------------------------------------------------------------ 18: mode select / game setup
T["18/19/p0"] = ("EASY SET", [90, 255, 70], [0, 200, 20], [20, 20, 110], {"th": 1.6, "pad": 1})
B["18/16/p0"] = _words(brief([90, 20, 170]), ("VS", (0, 0, 1, 1), [240, 255, 60], [120, 220, 0], [50, 0, 110], {"th": 1.5, "pad": 1}))
B["18/17/p0"] = brief([236, 20, 30], {"outline": 1, "c": [110, 0, 10]})
B["18/18/p0"] = brief([20, 70, 250], {"outline": 1, "c": [0, 10, 110]})


def _pill(top, bottom, text, tcol, edge, th=1.5):
    """Rounded banner (kept silhouette) with a glossy band and one line of text."""
    base = _grad(top, bottom, R(0.03, 0.1, 0.97, 0.2, I.lite(top, 0.55)), {"outline": 1, "c": [70, 70, 110]})
    box = (0.03, 0.16, 0.97, 0.88) if len(text) > 11 else (0.04, 0.06, 0.96, 0.97)       # long words: lower, so less squeezed
    return _words(base, (text, box, *tcol, edge, {"th": th, "pad": 1}))


_MATCH = ([255, 226, 50], [250, 120, 0])
B["18/27/p0"] = _pill([40, 110, 255], [0, 40, 200], "3-WIN MATCH", _MATCH, [70, 20, 0])
B["18/28/p0"] = _pill([60, 240, 60], [0, 170, 10], "5-WIN MATCH", _MATCH, [70, 20, 0])
B["18/29/p0"] = _pill([255, 70, 50], [210, 0, 0], "7-WIN MATCH", _MATCH, [70, 20, 0])
B["18/30/p0"] = _pill([170, 255, 190], [90, 220, 130], "4-PLAYER GAME", ([255, 130, 150], [240, 40, 90]), [30, 20, 110], 1.0)
B["18/31/p0"] = _pill([190, 190, 255], [130, 130, 240], "1 vs 3 GAME", ([255, 255, 170], [250, 220, 60]), [30, 20, 110])
B["18/32/p0"] = _pill([255, 190, 200], [250, 130, 150], "2 vs 2 GAME", ([200, 255, 220], [110, 240, 160]), [30, 20, 110])
B["18/33/p0"] = _pill([110, 210, 240], [50, 150, 210], "BATTLE GAME", ([250, 220, 255], [220, 150, 250]), [30, 20, 110], 1.3)
B["18/34/p0"] = _pill([255, 150, 240], [240, 90, 210], "DUEL GAME", ([120, 190, 255], [30, 90, 230]), [20, 10, 90])
B["18/59/p0"] = _pill([250, 250, 255], [130, 130, 150], "WINNINGS", (W, [214, 214, 226]), [40, 40, 60])
B["18/60/p0"] = _pill([255, 236, 90], [170, 110, 0], "COIN COUNT", ([255, 250, 120], [250, 200, 0]), [70, 40, 0])
for _f in range(35, 44):                                 # player/slot grids: green rules (kept silhouette)
    B[f"18/{_f}/p0"] = brief([20, 214, 30])

for _i, _c in enumerate(([250, 160, 40], [250, 200, 50], [255, 232, 80], [255, 222, 60], [250, 200, 50], [250, 170, 40])):
    B[f"18/44/p{_i}"] = brief(_c, {"glow": [0.45, 0.42, 0.3, 0.3], "c": I.lite(_c, 0.6)}, {"outline": 1, "c": [130, 60, 0]})
for _i, _who in enumerate(I.PLAYERS):                    # 18/45-18/52: portraits in player order
    B[f"18/{45 + _i}/p0"] = I.head(_who)


def _records(w, h, d, alpha):
    """MINI-GAME RECORDS board: title pill, a panel with a mushroom-person outline, footer bar with small icons."""
    ink, panel, bar = [150, 40, 20], [128, 100, 20], [236, 100, 0]
    ops = [R(0.14, 0.03, 0.86, 0.135, [240, 130, 20]), E((0.14, 0.0825), (0.03, 0.0525), c=[240, 130, 20]),
           E((0.86, 0.0825), (0.03, 0.0525), c=[240, 130, 20]),
           R(0.12, 0.155, 0.89, 0.845, panel), {"clip": [0.505, 0.5, 0.42, 0.37]},
           {"ring": [0.49, 0.47, 0.29, 0.32], "w": 0.014, "c": ink}, {"ring": [0.49, 0.27, 0.13, 0.1], "w": 0.012, "c": ink},
           {"ring": [0.26, 0.5, 0.07, 0.14], "w": 0.012, "c": ink}, {"ring": [0.72, 0.5, 0.07, 0.14], "w": 0.012, "c": ink},
           E((0.5, 0.7), (0.135, 0.16), c=panel), {"ring": [0.5, 0.7, 0.135, 0.16], "w": 0.012, "c": ink},
           E((0.46, 0.66), (0.012, 0.03), c=ink), E((0.54, 0.66), (0.012, 0.03), c=ink),
           {"arc": [0.5, 0.72, 0.06, 0.05, 20, 160], "w": 0.012, "c": ink}, {"clip": None},
           R(0.06, 0.875, 0.95, 0.985, bar), E((0.06, 0.93), (0.035, 0.055), c=bar), E((0.95, 0.93), (0.03, 0.055), c=bar),
           R(0.075, 0.895, 0.16, 0.965, [250, 170, 30]), R(0.81, 0.905, 0.935, 0.965, [250, 200, 60])]
    ops += I.place(I.chest(), (0.015, 0.025, 0.105, 0.125)) + I.place(I.pipe([30, 170, 60]), (0.02, 0.135, 0.1, 0.245))
    ops += I.place(I.mushroom(), (0.09, 0.895, 0.145, 0.965)) + I.place(I.chest(), (0.815, 0.905, 0.87, 0.965))
    ops += I.place(I.pipe([30, 170, 60]), (0.875, 0.905, 0.93, 0.965))
    out = np.asarray(facepaint.render(_grad([255, 206, 30], [250, 176, 10], *ops), w, h, alpha=alpha), np.float32)
    return _put(out, "MINI-GAME RECORDS", (0.13, 0.048, 0.87, 0.124), [90, 240, 80], [0, 160, 40], [20, 30, 110], th=1.0, pad=1)


B["18/15/p0"] = _records


def _star_panel():
    """18/26: blue backdrop with a dark panel, one big star and a ring of small ones."""
    panel = [14, 44, 150]
    ops = [R(0.09, 0.32, 0.91, 0.97, panel), P(star_pts(0.5, 0.64, 0.24, 0.1), [40, 140, 110])]
    for i, (cx, cy) in enumerate(((0.5, 0.29), (0.31, 0.37), (0.69, 0.37), (0.22, 0.55), (0.78, 0.55), (0.25, 0.78),
                                  (0.75, 0.76), (0.35, 0.92), (0.66, 0.92), (0.5, 0.97))):
        ops.append(P(star_pts(cx, cy, 0.035, 0.015), [40, 150, 110] if cy < 0.6 else [30, 80, 190]))
    return _grad([0, 220, 255], [10, 20, 250], *ops)


B["18/26/p0"] = _star_panel()

# model textures
B["18/24/b8"] = brief([252, 236, 214], E((0.5, 0.5), (0.46, 0.46), c=[244, 110, 120]), E((0.5, 0.5), (0.39, 0.39), c=[226, 206, 250]),
                      P(star_pts(0.5, 0.52, 0.4, 0.19), [250, 226, 130]), P(star_pts(0.5, 0.52, 0.29, 0.14), [246, 140, 130]),
                      P(star_pts(0.5, 0.52, 0.17, 0.08), [240, 150, 200]))
for _k in ("18/3/b9", "18/53/b9"):                      # gold star (kept silhouette)
    B[_k] = brief([255, 222, 20], {"glow": [0.55, 0.3, 0.4, 0.25], "c": [255, 250, 150]}, {"glow": [0.7, 0.85, 0.5, 0.3], "c": [226, 150, 0]},
                  {"outline": 1, "c": [150, 80, 0]})
B["18/4/b10"] = brief([240, 10, 20], *[E((0.125 + 0.25 * (_x + 0.5 * (_y % 2)), 0.1 + 0.2 * _y), (0.07, 0.07), c=W)
                                        for _y in range(5) for _x in range(-1, 4)])
B["18/5/b7"] = brief(W, E((0.52, 0.27), (0.17, 0.17), c=[236, 10, 20]), E((0.52, 0.75), (0.17, 0.17), c=[236, 10, 20]))


def _flame(top, mid):
    """Fire spirit on a soft backdrop: flame tongues, glowing body, two eyes."""
    return _grad(top, W, R(0, 0.55, 1, 1, mid), {"glow": [0.5, 0.56, 0.6, 0.16], "c": I.lite(mid, 0.6)}, R(0, 0.93, 1, 1, W),
                 P([(0.5, 0.36), (0.6, 0.5), (0.7, 0.44), (0.78, 0.74), (0.22, 0.74), (0.26, 0.52), (0.4, 0.58)], [250, 110, 10]),
                 E((0.5, 0.74), (0.3, 0.14), c=[250, 130, 10]), E((0.5, 0.75), (0.22, 0.105), c=[255, 214, 50]),
                 P([(0.5, 0.52), (0.6, 0.68), (0.4, 0.68)], [255, 190, 40]),
                 E((0.42, 0.76), (0.035, 0.035), c=K), E((0.58, 0.76), (0.035, 0.035), c=K))


for _k in ("18/21/b7", "18/22/b8"):
    B[_k] = _flame([110, 130, 250], [200, 200, 255])
for _k in ("18/21/b8", "18/22/b9"):
    B[_k] = _flame([170, 130, 250], [240, 80, 220])


def _door(bg, door, line):
    return brief(bg, E((0.5, 0.45), (0.3, 0.33), c=line), R(0.2, 0.45, 0.8, 0.95, line), E((0.5, 0.46), (0.25, 0.28), c=door),
                 R(0.25, 0.46, 0.75, 0.9, door), R(0.25, 0.55, 0.75, 0.59, line), E((0.72, 0.57), (0.06, 0.06), c=[255, 226, 40]))


B["18/22/b7"] = _door([0, 0, 60], [10, 10, 110], [0, 0, 150])
B["18/55/b7"] = _door([70, 0, 0], [170, 16, 20], [226, 40, 40])
_TRI = [P([(0.25 * _x, 0.5 * _y), (0.25 * _x + 0.25, 0.5 * _y), (0.25 * _x + (0.25 if (_x + _y) % 2 else 0), 0.5 * _y + 0.5)], W)
        for _y in range(2) for _x in range(3)]
for _k in ("18/21/b11", "18/23/b8"):                     # pennant triangles + a tan trim strip
    B[_k] = brief(K, *_TRI, R(0.75, 0, 1, 0.42, [204, 164, 104]), R(0.75, 0.42, 1, 0.47, K), R(0.75, 0.47, 1, 0.74, [246, 216, 164]),
                  R(0.75, 0.74, 1, 0.78, K), R(0.75, 0.78, 1, 1, [252, 236, 216]))
B["18/53/b12"] = brief(K, R(0.5, 0, 1, 0.5, W), R(0, 0.5, 0.5, 1, W))
for _k in ("18/25/b10", "18/56/b10", "18/57/b12"):       # spotlight: silver housing, yellow lens
    B[_k] = brief([226, 226, 232], {"glow": [0.75, 0.75, 0.4, 0.4], "c": [120, 120, 136]}, E((0.38, 0.56), (0.2, 0.26), c=[40, 40, 50]),
                  E((0.38, 0.56), (0.15, 0.2), c=[255, 226, 20]), E((0.34, 0.5), (0.06, 0.08), c=[255, 250, 170]),
                  {"outline": 1, "c": [30, 30, 40]})
B["18/57/b10"] = brief([236, 20, 30], {"glow": [0.5, 0.5, 0.4, 0.4], "c": [255, 110, 110]}, P(star_pts(0.5, 0.5, 0.24, 0.11), [255, 240, 150]),
                       R(0, 0, 0.07, 1, K), R(0.07, 0, 0.14, 1, W), R(0.86, 0, 0.93, 1, W), R(0.93, 0, 1, 1, K))
_TEAL = [90, 226, 200]


def _coin(cx, cy, rx, ry, star=False):
    ops = [E((cx, cy + ry * 0.35), (rx, ry), c=[170, 96, 0]), E((cx, cy), (rx, ry), c=[250, 190, 10]),
           E((cx, cy), (rx * 0.8, ry * 0.8), c=[255, 226, 60])]
    if star:
        ops.append(P(star_pts(cx, cy, rx * 0.6, rx * 0.27), [250, 180, 0]))
    return ops


B["18/57/b7"] = brief(_TEAL, E((0.5, 0.52), (0.42, 0.42), c=[110, 70, 0]),
                      *[o for _a in ((0.3, 0.4, 0.2, 0.07), (0.3, 0.52, 0.2, 0.07), (0.72, 0.7, 0.2, 0.08), (0.34, 0.78, 0.2, 0.09),
                                     (0.56, 0.86, 0.2, 0.08)) for o in _coin(*_a)],
                      E((0.6, 0.4), (0.3, 0.3), c=[170, 96, 0]), E((0.6, 0.38), (0.28, 0.28), c=[250, 190, 10]),
                      E((0.6, 0.38), (0.22, 0.22), c=[255, 226, 60]), P(star_pts(0.6, 0.39, 0.17, 0.08), [250, 176, 0]))
B["18/58/b7"] = brief([200, 110, 0], *[o for _y in (0.72, 0.5, 0.28) for o in _coin(0.5, _y, 0.46, 0.2)],
                      {"ring": [0.5, 0.28, 0.33, 0.13], "w": 0.03, "c": [226, 150, 0]}, E((0.3, 0.22), (0.1, 0.035), c=[255, 250, 170]))
_GG = I.game_guy(bg=[110, 70, 0])
B["18/57/b11"] = brief(_TEAL, E((0.5, 0.52), (0.44, 0.44), c=[110, 70, 0]), *I.place(_GG, (0.14, 0.2, 0.92, 0.98)),
                       E((0.22, 0.2), (0.17, 0.08), c=[250, 200, 20], rot=-30), E((0.16, 0.16), (0.07, 0.05), c=[170, 110, 0], rot=-30),
                       L([(0.3, 0.26), (0.46, 0.44)], 0.05, [250, 200, 20]))
