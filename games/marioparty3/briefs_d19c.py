"""MainFS dir 19 (board UI), character / NPC pictures: player heads in all sizes, figures, NPC heads, name plates,
space signs and the board banners.

Everything is drawn from the shared icon library `icons.py` plus a few local drawings below (hand-written primitives,
colours picked by eye)."""
import numpy as np
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L
from . import icons as I
from .icons import RED, GREEN, BLUE, YEL, SKIN, CREAM, ORANGE, PURPLE, PINK, BROWN, TAN, GREY, STONE, dark, lite

B = {}
T = {}

PL = I.PLAYERS            # mario luigi peach yoshi wario dk waluigi daisy
NPC12 = ("koopa", "goomba", "toad", "bobomb", "boo", "whomp", "snifit", "piranha", "chain_chomp", "thwomp", "snowman", "bowser")


# ------------------------------------------------------------------ local drawings (not in the library)
def snifit(bg=None):
    """Red hooded creature with a black mask and a white cannon mouth, looking right."""
    return I._b(
        bg, E((0.42, 0.52), (0.4, 0.42), c=RED), P([(0.04, 0.3), (0.3, 0.2), (0.2, 0.6)], dark(RED)),
        E((0.56, 0.5), (0.3, 0.33), c=[24, 24, 30]),
        E((0.5, 0.36), (0.07, 0.09), c=W), E((0.72, 0.36), (0.06, 0.08), c=W),
        E((0.72, 0.68), (0.2, 0.19), c=W), E((0.75, 0.68), (0.1, 0.1), c=[60, 60, 70]),
        E((0.3, 0.26), (0.08, 0.05), c=lite(RED, 0.5), rot=-30))


def chomp_front(bg=None):
    """Chain Chomp seen from the front: black ball, white eyes, teeth along the bottom."""
    return I._b(
        bg, {"sphere": [0.5, 0.48, 0.46, 0.44], "c": [50, 50, 64]},
        E((0.34, 0.42), (0.08, 0.13), c=W), E((0.66, 0.42), (0.08, 0.13), c=W),
        E((0.35, 0.44), (0.035, 0.06), c=K), E((0.65, 0.44), (0.035, 0.06), c=K),
        P([(0.16, 0.78), (0.84, 0.78), (0.7, 0.96), (0.3, 0.96)], [190, 10, 30]),
        *[P([(x, 0.78), (x + 0.12, 0.78), (x + 0.06, 0.9)], W) for x in (0.2, 0.34, 0.48, 0.62)])


def skull_guy(bg=None):
    """White skull-masked creature with a red-spotted cap (19/196)."""
    return I._b(
        bg, E((0.5, 0.2), (0.3, 0.14), c=W), E((0.4, 0.14), (0.06, 0.04), c=RED), E((0.6, 0.14), (0.06, 0.04), c=RED),
        E((0.5, 0.5), (0.4, 0.36), c=[240, 240, 244]), R(0.32, 0.7, 0.68, 0.96, [240, 240, 244]),
        E((0.33, 0.48), (0.11, 0.13), c=K), E((0.67, 0.48), (0.11, 0.13), c=K), P([(0.5, 0.6), (0.44, 0.7), (0.56, 0.7)], K),
        E((0.5, 0.86), (0.1, 0.09), c=K))


def snowman_full(bg=None):
    """Two-ball snowman with a twig arm (19/198)."""
    return I._b(
        bg, L([(0.3, 0.5), (0.06, 0.4)], 0.04, [200, 150, 60]), E((0.5, 0.68), (0.38, 0.3), c=[226, 232, 246]),
        E((0.5, 0.32), (0.3, 0.28), c=W), E((0.4, 0.3), (0.04, 0.06), c=K), E((0.6, 0.3), (0.04, 0.06), c=K),
        E((0.5, 0.42), (0.06, 0.035), c=K))


def star_ghost(bg=None):
    """Pale purple star with eyes (19/466)."""
    c = [200, 170, 250]
    return I._b(
        bg, P(star_pts(0.5, 0.54, 0.52, 0.27), [110, 80, 190]), P(star_pts(0.5, 0.54, 0.44, 0.23), c),
        E((0.5, 0.56), (0.2, 0.18), c=lite(c, 0.6)), I.eyes(0.5, 0.52, 0.09, 0.04, 0.08, hl=False))


def bullet_bill():
    """Bullet Bill flying left (plain brief for the kept silhouette of 19/610)."""
    c = [70, 110, 160]
    return brief(
        c, R(0, 0, 1, 0.22, lite(c, 0.6)), R(0, 0.22, 1, 0.36, lite(c, 0.3)), R(0, 0.75, 1, 1, dark(c, 0.6)),
        R(0.8, 0, 0.87, 1, dark(c, 0.5)), E((0.2, 0.5), (0.34, 0.6), c=[20, 22, 34]),
        E((0.2, 0.36), (0.1, 0.16), c=W), E((0.17, 0.38), (0.05, 0.09), c=K), L([(0.08, 0.14), (0.32, 0.26)], 0.06, [20, 22, 34]),
        E((0.2, 0.74), (0.1, 0.1), c=[230, 40, 60]), E((0.4, 0.86), (0.1, 0.1), c=W))


def cloud_block(bg=None):
    """Blue angry block with a green tuft riding a white cloud with flowers (19/617)."""
    c = [50, 100, 230]
    return I._b(
        bg, R(0.44, 0.0, 0.56, 0.12, [80, 180, 60]), R(0.26, 0.1, 0.74, 0.62, dark(c, 0.6)), R(0.3, 0.14, 0.7, 0.6, c),
        I.weyes(0.5, 0.34, 0.1, 0.07, 0.06, pupil=0.5, look=(0.3, 0.2)), I.brows(0.5, 0.25, 0.1, 0.09, 0.04, 0.05),
        L([(0.4, 0.5), (0.6, 0.5)], 0.04, K),
        *[E((x, y), (r, r * 0.8), c=[200, 210, 236]) for x, y, r in ((0.2, 0.8, 0.2), (0.5, 0.84, 0.24), (0.8, 0.8, 0.2))],
        *[E((x, y), (r, r * 0.8), c=W) for x, y, r in ((0.2, 0.76, 0.19), (0.5, 0.78, 0.24), (0.8, 0.76, 0.19), (0.36, 0.66, 0.14), (0.66, 0.66, 0.14))],
        E((0.4, 0.78), (0.03, 0.045), c=K), E((0.6, 0.78), (0.03, 0.045), c=K),
        E((0.08, 0.62), (0.04, 0.04), c=RED), E((0.92, 0.62), (0.04, 0.04), c=RED))


def pokey(bg=None):
    """Stack of orange spiky balls with a face on the top one."""
    c = [250, 150, 20]
    ops = []
    for y in (0.82, 0.5, 0.18):
        ops += [E((0.5, y), (0.3, 0.17), c=dark(c, 0.75)), E((0.48, y - 0.01), (0.27, 0.15), c=c),
                P([(0.2, y - 0.04), (0.04, y), (0.2, y + 0.04)], W), P([(0.8, y - 0.04), (0.96, y), (0.8, y + 0.04)], W)]
    ops += I.eyes(0.5, 0.16, 0.1, 0.035, 0.06, hl=False) + [L([(0.4, 0.27), (0.6, 0.27)], 0.025, K)]
    return I._b(bg, ops)


def cactus(c=(40, 190, 60), bg=None, flower=None):
    c = list(c)
    ops = [L([(0.5, 0.98), (0.5, 0.2)], 0.3, dark(c, 0.7)), L([(0.5, 0.98), (0.5, 0.2)], 0.24, c),
           L([(0.5, 0.62), (0.16, 0.62), (0.16, 0.36)], 0.14, c), L([(0.5, 0.52), (0.84, 0.52), (0.84, 0.24)], 0.14, c),
           I.eyes(0.5, 0.36, 0.07, 0.03, 0.06, hl=False), {"arc": [0.5, 0.46, 0.08, 0.05, 20, 160], "w": 0.03, "c": K}]
    if flower:
        ops += [E((0.5 + dx, 0.1 + dy), (0.07, 0.06), c=list(flower)) for dx, dy in ((0, -0.06), (0.08, 0), (0, 0.06), (-0.08, 0))]
        ops += [E((0.5, 0.1), (0.04, 0.04), c=YEL)]
    return I._b(bg, ops)


def flame(c=(250, 110, 20), bg=None):
    c = list(c)
    return I._b(
        bg, P([(0.5, 0.04), (0.74, 0.4), (0.84, 0.66), (0.7, 0.92), (0.3, 0.92), (0.16, 0.66), (0.3, 0.42)], c),
        E((0.5, 0.68), (0.34, 0.27), c=c), E((0.5, 0.72), (0.2, 0.18), c=lite(c, 0.6)),
        I.eyes(0.5, 0.66, 0.09, 0.035, 0.07, hl=False))


I_EXTRA = {"snifit": snifit, "chomp_front": chomp_front, "skull_guy": skull_guy, "snowman_full": snowman_full,
           "star_ghost": star_ghost, "pokey": pokey, "cactus": cactus, "flame": flame, "cloud_block": cloud_block}


def head(who, bg=None):
    return I_EXTRA[who](bg=bg) if who in I_EXTRA else I.get(who, bg)


# ------------------------------------------------------------------ whole figures (32x32)
_SUIT = {            # who: (shirt, legs, shoes, skirt?)
    "mario": (RED, [40, 60, 220], BROWN, False), "luigi": (GREEN, [40, 60, 220], BROWN, False),
    "peach": ([250, 130, 200], [250, 130, 200], [250, 130, 200], True), "yoshi": ([60, 190, 50], W, [240, 120, 20], False),
    "wario": (YEL, [130, 40, 180], [40, 150, 60], False), "dk": ([150, 80, 30], [150, 80, 30], [226, 170, 110], False),
    "waluigi": (I.WAL, [30, 24, 70], [240, 130, 30], False), "daisy": (I.D_DRESS, I.D_DRESS, I.D_DRESS, True),
}


def figure(who, bg=None):
    """Small standing figure: the library head on a body in the character's colours."""
    shirt, legs, shoes, skirt = _SUIT[who]
    if skirt:
        body = [P([(0.14, 0.98), (0.36, 0.56), (0.64, 0.56), (0.86, 0.98)], shirt), E((0.5, 0.94), (0.36, 0.06), c=dark(shirt, 0.8)),
                L([(0.36, 0.64), (0.2, 0.76)], 0.08, W), L([(0.64, 0.64), (0.8, 0.76)], 0.08, W)]
    else:
        body = [E((0.34, 0.95), (0.15, 0.055), c=shoes), E((0.66, 0.95), (0.15, 0.055), c=shoes),
                L([(0.3, 0.66), (0.12, 0.8)], 0.11, shirt), L([(0.7, 0.66), (0.88, 0.8)], 0.11, shirt),
                E((0.12, 0.82), (0.07, 0.07), c=W if who != "dk" else shoes), E((0.88, 0.82), (0.07, 0.07), c=W if who != "dk" else shoes),
                R(0.3, 0.6, 0.7, 0.8, shirt), R(0.31, 0.72, 0.69, 0.93, legs)]
    return I._b(bg, body, I.place(I.head(who), (0.19, 0.0, 0.81, 0.62)))


def kid_mask(who, bg=None):
    """Koopa Kid (orange body, green spiked shell cap) wearing a player's face as a mask (19/199-206)."""
    o = [246, 130, 20]
    return I._b(
        bg, E((0.26, 0.92), (0.16, 0.07), c=o), E((0.74, 0.92), (0.16, 0.07), c=o),
        E((0.5, 0.66), (0.4, 0.3), c=o), L([(0.16, 0.56), (0.04, 0.76)], 0.12, o), L([(0.84, 0.56), (0.96, 0.76)], 0.12, o),
        E((0.5, 0.8), (0.2, 0.13), c=[250, 220, 150]),
        E((0.5, 0.2), (0.34, 0.17), c=[20, 140, 50]), P([(0.44, 0.08), (0.5, 0.0), (0.56, 0.08)], W),
        P([(0.2, 0.16), (0.14, 0.06), (0.28, 0.1)], W), P([(0.8, 0.16), (0.86, 0.06), (0.72, 0.1)], W),
        E((0.5, 0.46), (0.3, 0.27), c=K), {"clip": [0.5, 0.46, 0.27, 0.245]},
        I.place(I.head(who), (0.18, 0.1, 0.82, 0.78)), {"clip": None})


# ------------------------------------------------------------------ player heads
B["19/2/p0"] = I.framed(I.head("mario", bg=[150, 30, 40]), inset=0.05)
B["19/3/p0"] = I.framed(I.head("luigi", bg=[30, 50, 170]), inset=0.05)
for _i, _w in enumerate(PL):
    B[f"19/{54 + _i}/p0"] = I.head(_w)                      # 32x32 on the dark backdrop
    B[f"19/{547 + _i}/r"] = I.cut(I.head(_w))               # 16 px tokens
    B[f"19/{179 + _i}/b7"] = I.cut(figure(_w))              # 32x32 figures
    B[f"19/{199 + _i}/b7"] = I.cut(kid_mask(_w))            # Koopa Kid in a player mask
for _f, _w in zip(range(216, 226), ("mario", "luigi", "luigi", "peach", "yoshi", "wario", "dk", "waluigi", "waluigi", "daisy")):
    B[f"19/{_f}/p0"] = I.cut(I.head(_w))                    # 26x26
for _i, _w in enumerate(PL[:6]):
    B[f"19/{597 + _i}/p0"] = I.cut(I.head(_w))              # 18x18
_TILE = {"mario": ([232, 160, 130], [150, 40, 30]), "luigi": ([110, 150, 236], [20, 40, 130]),
         "peach": ([250, 150, 200], [214, 30, 130]), "yoshi": ([60, 170, 110], [240, 244, 240])}
for _i, (_w, (_bg, _fr)) in enumerate(_TILE.items()):
    B[f"19/{561 + _i}/c"] = I.framed(I.head(_w, bg=_bg), frame=_fr, t=0.08, inset=0.04)

# ------------------------------------------------------------------ NPC figures 19/187-198
_FIG = {187: "koopa", 188: "toad", 189: "bowser", 190: "goomba", 191: "chomp_front", 192: "bobomb", 193: "whomp", 194: "thwomp",
        195: "boo", 196: "skull_guy", 197: "piranha", 198: "snowman_full"}
for _f, _w in _FIG.items():
    B[f"19/{_f}/b7"] = I.cut(head(_w))

# ------------------------------------------------------------------ NPC heads
for _i, _w in enumerate(NPC12):
    B[f"19/{226 + _i}/p0"] = head(_w, bg=[6, 6, 10])        # 18x18 on black
    B[f"19/286/p{_i}"] = head(_w, bg=[6, 6, 10])            # 40x40 on black
    B[f"19/{294 + _i}/p0"] = I.cut(head(_w))                # 40x40 cut out
for _f, _w in ((463, "koopa"), (464, "toad"), (465, "boo"), (466, "star_ghost"), (526, "boo"), (595, "boo")):
    B[f"19/{_f}/p0"] = I.cut(head(_w))
B["19/610/p0"] = bullet_bill()
B["19/615/p0"] = brief([244, 246, 252], {"glow": [0.5, 1.0, 0.6, 0.4], "c": [206, 214, 236]},
                       E((0.43, 0.52), (0.03, 0.1), c=K), E((0.57, 0.52), (0.03, 0.1), c=K))
B["19/617/p0"] = I.cut(cloud_block())
B["19/397/b8"] = I.boxed(I.head("bowser", bg=[166, 130, 214]), (0.1, 0.1, 0.9, 0.9))
B["19/397/b7"] = brief([250, 170, 240], *[P(star_pts(x, y, 0.13), [255, 226, 250]) for x, y in ((0.24, 0.3), (0.72, 0.22), (0.5, 0.74))])

# ghost / snowman faces (64x64, kept round silhouettes)
_SNOW = [{"glow": [0.6, 0.72, 0.5, 0.45], "c": [196, 204, 232]}, {"glow": [0.36, 0.3, 0.3, 0.26], "c": W}]
B["19/353/b7"] = brief([236, 240, 250], *_SNOW, {"arc": [0.35, 0.54, 0.08, 0.05, 20, 160], "w": 0.03, "c": K},
                       {"arc": [0.65, 0.54, 0.08, 0.05, 20, 160], "w": 0.03, "c": K}, L([(0.44, 0.74), (0.56, 0.74)], 0.03, K))
B["19/358/b7"] = brief([236, 240, 250], *_SNOW, E((0.34, 0.5), (0.06, 0.075), c=K), E((0.66, 0.5), (0.06, 0.075), c=K),
                       E((0.5, 0.7), (0.09, 0.05), c=K), E((0.32, 0.47), (0.02, 0.025), c=W), E((0.64, 0.47), (0.02, 0.025), c=W))
_GH = [130, 140, 226]
B["19/345/b7"] = brief(
    [24, 54, 177], E((0.36, 0.38), (0.3, 0.3), c=dark(_GH, 0.8)), E((0.35, 0.36), (0.27, 0.27), c=_GH),
    P([(0.5, 0.56), (0.72, 0.6), (0.52, 0.66)], _GH), E((0.1, 0.42), (0.06, 0.08), c=_GH),
    P([(0.22, 0.26), (0.36, 0.34), (0.34, 0.4), (0.24, 0.36)], K), P([(0.52, 0.26), (0.4, 0.34), (0.42, 0.4), (0.5, 0.36)], K),
    {"arc": [0.37, 0.5, 0.1, 0.05, 20, 160], "w": 0.025, "c": [40, 40, 110]},
    R(0.06, 0.8, 0.94, 0.84, ORANGE), R(0.06, 0.92, 0.94, 0.96, ORANGE), R(0.06, 0.8, 0.1, 0.96, ORANGE), R(0.9, 0.8, 0.94, 0.96, ORANGE),
    R(0.76, 0.68, 1, 0.71, ORANGE))

# ------------------------------------------------------------------ name plates 19/263-270 (98x38): head in a disc at the left
for _i, _w in enumerate(PL):
    B[f"19/{263 + _i}/p0"] = brief(W, R(0.12, 0.04, 0.47, 0.96, [10, 10, 16]), *I.place(I.head(_w), (0.15, 0.1, 0.43, 0.86)))

# ------------------------------------------------------------------ space signs
_LG = [150, 226, 130]


def _sign(bg, frame, inner, *ops):
    return I.framed(brief(bg, R(0.12, 0.12, 0.88, 0.88, inner), *ops), frame=frame, t=0.07)


# pale green mask with dark eye holes and a pink bow on top
B["19/556/c"] = _sign([30, 60, 150], W, [70, 160, 110], E((0.5, 0.6), (0.27, 0.25), c=_LG),
                      E((0.4, 0.58), (0.06, 0.08), c=[30, 90, 60]), E((0.6, 0.58), (0.06, 0.08), c=[30, 90, 60]),
                      E((0.5, 0.75), (0.04, 0.04), c=[30, 90, 60]),
                      P([(0.5, 0.28), (0.28, 0.16), (0.28, 0.4)], [250, 120, 170]), P([(0.5, 0.28), (0.72, 0.16), (0.72, 0.4)], [250, 120, 170]),
                      E((0.5, 0.28), (0.05, 0.05), c=[200, 60, 120]))
# green shell with plate lines and three dark spots
B["19/557/c"] = _sign([30, 60, 150], [120, 220, 120], [60, 130, 130], E((0.5, 0.52), (0.33, 0.33), c=[40, 110, 60]),
                      E((0.5, 0.52), (0.28, 0.28), c=_LG), L([(0.5, 0.24), (0.5, 0.8)], 0.03, [40, 110, 60]),
                      L([(0.22, 0.56), (0.78, 0.56)], 0.03, [40, 110, 60]),
                      E((0.5, 0.36), (0.07, 0.07), c=[30, 90, 60]), E((0.36, 0.68), (0.07, 0.07), c=[30, 90, 60]),
                      E((0.64, 0.68), (0.07, 0.07), c=[30, 90, 60]))
# sleepy yellow face under a red crossed ribbon
B["19/560/c"] = _sign([40, 140, 90], W, [70, 170, 110], E((0.5, 0.66), (0.26, 0.2), c=[250, 200, 40]),
                      L([(0.24, 0.16), (0.6, 0.6)], 0.11, [240, 70, 40]), L([(0.76, 0.16), (0.4, 0.6)], 0.11, [240, 70, 40]),
                      E((0.5, 0.42), (0.07, 0.07), c=[250, 200, 40]),
                      {"arc": [0.4, 0.64, 0.06, 0.04, 20, 160], "w": 0.03, "c": [130, 80, 0]},
                      {"arc": [0.6, 0.64, 0.06, 0.04, 20, 160], "w": 0.03, "c": [130, 80, 0]})


def _half(fill, *ops, border=(244, 236, 200)):
    """Left half (16x32) of an octagonal space sign whose centre is the right edge; the kept alpha cuts the octagon."""
    return brief(list(border), P([(1.0, 0.07), (0.56, 0.07), (0.16, 0.22), (0.16, 0.78), (0.56, 0.93), (1.0, 0.93)], fill), *ops)


_SB = [40, 70, 200]
B["19/535/r"] = _half([40, 150, 80], E((1.0, 0.5), (0.62, 0.3), c=_SB), {"arc": [1.0, 0.5, 0.4, 0.2, 90, 300], "w": 0.05, "c": _LG},
                      {"arc": [1.0, 0.52, 0.18, 0.09, 90, 300], "w": 0.04, "c": _LG})
B["19/536/r"] = _half([40, 150, 80], E((1.0, 0.5), (0.66, 0.33), c=_SB), E((1.0, 0.5), (0.5, 0.25), c=_LG),
                      E((0.72, 0.42), (0.1, 0.05), c=[30, 90, 60]), E((0.8, 0.62), (0.1, 0.05), c=[30, 90, 60]))
B["19/538/r"] = _half([40, 150, 80], E((1.0, 0.5), (0.66, 0.33), c=_SB), E((1.0, 0.5), (0.5, 0.25), c=_LG),
                      L([(0.5, 0.5), (1.0, 0.5)], 0.03, [30, 90, 60]), E((0.74, 0.4), (0.09, 0.045), c=[30, 90, 60]),
                      E((0.74, 0.61), (0.09, 0.045), c=[30, 90, 60]))
B["19/541/r"] = _half([40, 150, 80], E((1.0, 0.5), (0.66, 0.33), c=_SB), P(star_pts(1.0, 0.5, 0.26, 0.11, aspect=2.0), YEL))
B["19/542/r"] = _half([214, 30, 30], E((1.0, 0.5), (0.6, 0.3), c=[120, 0, 10]), E((0.66, 0.42), (0.12, 0.05), c=K, rot=20),
                      E((0.8, 0.62), (0.14, 0.04), c=K), border=(250, 220, 190))
B["19/543/r"] = _half([60, 190, 80], R(0.72, 0.36, 1.0, 0.8, _SB), E((0.9, 0.24), (0.18, 0.07), c=_SB))
B["19/540/r"] = brief([84, 74, 82], P(star_pts(0.5, 0.52, 0.3, 0.14), [120, 108, 116]))

# 8x8 mini signs: blue glyph on green (kept at 8 px, so only the coarse shape counts)
_MG, _MB = [60, 200, 90], [20, 40, 230]
_MINI = {
    586: [{"ring": [0.5, 0.56, 0.24, 0.3], "w": 0.16, "c": _MB}],
    587: [L([(0.72, 0.24), (0.32, 0.24), (0.32, 0.5), (0.7, 0.5), (0.7, 0.78), (0.28, 0.78)], 0.15, _MB)],
    588: [R(0.42, 0.42, 0.6, 0.88, _MB), R(0.42, 0.14, 0.6, 0.3, _MB)],
    589: [L([(0.3, 0.22), (0.7, 0.22), (0.7, 0.5), (0.5, 0.5), (0.5, 0.62)], 0.15, _MB), R(0.42, 0.76, 0.6, 0.9, YEL)],
    591: [R(0.2, 0.3, 0.4, 0.5, _MB), R(0.6, 0.3, 0.8, 0.5, _MB), L([(0.2, 0.62), (0.2, 0.8), (0.8, 0.8), (0.8, 0.62)], 0.14, _MB)],
    592: [R(0.2, 0.26, 0.4, 0.46, _MB), R(0.6, 0.26, 0.8, 0.46, _MB), R(0.36, 0.6, 0.66, 0.9, RED)],
}
for _f, _ops in _MINI.items():
    B[f"19/{_f}/r"] = brief(_MG, *_ops)
B["19/593/r"] = brief([214, 30, 30], L([(0.14, 0.2), (0.44, 0.36)], 0.13, K), L([(0.86, 0.2), (0.56, 0.36)], 0.13, K),
                      R(0.22, 0.42, 0.4, 0.56, K), R(0.6, 0.42, 0.78, 0.56, K), R(0.3, 0.72, 0.72, 0.84, K))


# ------------------------------------------------------------------ board banners (100x46) and the NPC strip (150x50)
def _strip(names, w, h, bg, frame, fill=0.8):
    """Heads in square cells side by side on a framed backdrop."""
    n = len(names)
    cw = min(0.94 / n, fill * h / w)             # cell width in x units so that cells are square
    ch = cw * w / h
    x0 = 0.5 - cw * n / 2
    ops = []
    for i, nm in enumerate(names):
        b = nm if isinstance(nm, dict) else head(nm)
        ops += I.place(b, (x0 + i * cw + 0.004, 0.5 - ch / 2, x0 + (i + 1) * cw - 0.004, 0.5 + ch / 2))
    tx, ty = 2.5 / w, 2.5 / h
    return brief(list(bg), *ops, R(0, 0, 1, ty, frame), R(0, 1 - ty, 1, 1, frame), R(0, 0, tx, 1, frame), R(1 - tx, 0, 1, 1, frame))


_BANNER = {
    105: (["snowman", "snowman_full", "snowman"], [20, 60, 150], [60, 220, 200]),
    106: (["fish", "blooper", "fish"], [20, 40, 130], [40, 60, 240]),
    107: (["pokey", cactus(flower=[230, 60, 220]), "cactus"], [150, 170, 30], [250, 130, 20]),
    108: (["evil_tree", "tree"], [30, 110, 40], [240, 220, 20]),
    109: ([flame([70, 150, 250]), "flame", "thwomp", "whomp"], [110, 30, 40], [240, 220, 20]),
    110: (["piranha", "piranha", "waluigi"], [30, 60, 130], [140, 60, 230]),
    111: (["koopa", "thwomp", "bowser", "boo", "chain_chomp"], [130, 20, 30], [230, 30, 40]),
}
for _f, (_names, _bg, _fr) in _BANNER.items():
    B[f"19/{_f}/p0"] = _strip(_names, 100, 46, _bg, _fr)
B["19/131/p0"] = _strip(["koopa", "toad", "thwomp", "boo", "bowser", "snowman", "chain_chomp"], 150, 50, [130, 20, 30], [230, 30, 40])
