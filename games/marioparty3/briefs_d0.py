"""MainFS dir 0 (common UI): framed 40x40 portraits of characters and items, item icons, hand cursors, coin bag.

All pictures come from the drawn library `icons.py` (hand-written primitives)."""
import numpy as np
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, typeset, over, cutout, star_pts, GOLD, GOLD_D, GOLD_L
from . import icons as I

B = {}
T = {}

# ------------------------------------------------------------------ 0/54-0/105: framed portraits (40x40)
# characters on a see-through backdrop: white frame + our own silhouette
_CUT = {
    54: I.koopa(), 55: I.thwomp(), 56: I.shy_guy(), 57: I.bobomb([226, 30, 30]), 58: I.whomp(),
    59: I.toad([70, 170, 150], [226, 226, 220], [240, 120, 30]), 60: I.koopa(), 61: I.toad(), 62: I.bowser(), 63: I.goomba(),
    64: I.boo(), 65: I.game_guy(), 66: I.baby_bowser(), 67: I.toad([160, 196, 250], [50, 110, 220]), 68: I.millennium_star(),
    69: I.snowman(), 70: I.pipe([80, 50, 230]), 71: I.pipe([250, 220, 0]), 72: I.pipe([250, 130, 0]), 73: I.pipe([250, 110, 220]),
    74: I.glove_guy(), 75: I.cone_guy(), 98: I.key(), 99: I.bigmouth(), 100: I.blooper(), 102: I.girl(),
}
for _f, _b in _CUT.items():
    B[f"0/{_f}/p0"] = I.cut(I.framed(_b, inset=0.06))
# pictures that fill the frame (items on black, creatures on their own backdrop)
_FULL = {
    76: I.disc_guy([20, 16, 16]), 77: I.mushroom(), 78: I.key(), 79: I.mushroom("poison"), 80: I.mushroom("reverse"),
    81: I.cellular_shopper(), 82: I.warp_block(), 83: I.plunder_chest(), 84: I.bowser_phone(), 85: I.glove(), 86: I.lucky_lamp(),
    87: I.mushroom("golden"), 88: I.boo_bell(), 89: I.spray(), 90: I.bowser_suit(), 91: I.magic_lamp(), 92: I.item_bag(),
    93: I.koopa_kard(), 94: I.barter_box(), 95: I.coin(face=True, c=[250, 170, 20]), 96: I.watch(), 97: I.koopa_kid_bag(),
    101: I.fish(bg=[20, 50, 110]), 103: I.mole([200, 120, 10]), 104: I.tree(bg=[20, 96, 30]), 105: I.evil_tree([60, 16, 110]),
}
for _f, _b in _FULL.items():
    B[f"0/{_f}/p0"] = I.framed(_b, inset=0.09)

# ------------------------------------------------------------------ 0/106-0/113: the players' hand cursors (3 poses each)
_HANDS = {106: ([255, 226, 226], None), 107: ([208, 240, 240], None), 108: (W, None), 109: ([40, 150, 30], None),
          110: (W, "W"), 111: ([214, 150, 60], None), 112: (W, "L"), 113: (W, None)}
for _f, (_c, _em) in _HANDS.items():
    for _i in range(3):
        B[f"0/{_f}/p{_i}"] = I.hand(_c, _em)
B["0/119/p0"] = I.hand(W)
B["0/48/p0"] = I.hand(W, cuff=(0.05, 0.7))            # glove pointing right, cuff on the left
B["0/136/p0"] = I.hand(W, cuff=(0.6, 0.95))           # hand pointing down-left

# ------------------------------------------------------------------ 0/114-0/124, 0/30: item icons (32x32, own silhouette)
_ICONS = {114: I.mushroom(), 115: I.key(), 116: I.winged_arrow(), 117: I.chest(), 118: I.bowser_bomb(), 120: I.warp_block(),
          121: I.mushroom("golden"), 122: I.boo_bell(), 123: I.bowser_suit(), 124: I.magic_lamp(), 30: I.coin_bag()}
for _f, _b in _ICONS.items():
    B[f"0/{_f}/p0"] = I.cut(_b)
