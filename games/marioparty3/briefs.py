"""Mario Party 3 briefs: our own descriptions of pictures the kept colour grid cannot carry (faces, icons, text).

Keys are spec keys "<dir>/<file>/<image>". B = facepaint briefs (or callables (w, h, d, alpha) -> RGBA),
T = typeset text strips (text, top colour, bottom colour, edge colour, options). The primitives and the character
parts drawn for Mario Party 1 (`mp1_briefs`, same characters) are reused; nothing here is derived from retail pixels.

    python -m games.marioparty3.briefs <out.png> <dir> [--cell 128]      # preview sheet of that directory's briefs
"""
import json
import os
import sys

import numpy as np

from cleanroom.decomp import gen as G
from cleanroom.gfx import facepaint
from . import mp1_briefs as M
from .mp1_briefs import E, L, P, R, K, W, brief, eye, typeset      # noqa: F401

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec")
B = {}
T = {}

# ------------------------------------------------------------------ character faces (dirs 2-9)
from . import faces      # noqa: E402

B.update({k: v for k, v in faces.table().items() if k not in ("6/162/b7", "6/163/p0")})

# ------------------------------------------------------------------ menu font sprites and word strips (dir 12)
_ORANGE = M._ORANGE
_ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_PUNCT = {27: "!", 28: "-", 29: "?", 30: "-", 31: "'", 33: ".", 36: ","}
_ACCENTS = "Ä:A\" Ö:O\" Ü:U\" ß:B À:A` Á:A' È:E` É:E' Ì:I` Í:I' Ò:O` Ó:O' Ù:U` Ú:U' Ñ:N~ à:a` â:a^ ä:a\" ç:c è:e` é:e' ê:e^ ë:e\" î:i^ ï:i\" ô:o^ ö:o\" ù:u` û:u^ ü:u\" á:a' ì:i` í:i' ò:o` ó:o' ú:u' ñ:n~".split()


def _accented(base, mark, opt):
    """Letter with a diacritic drawn above it (the stroke font has plain letters only)."""
    def paint_(w, h, d, alpha):
        top, bottom, edge = _ORANGE
        out = np.zeros((h, w, 4), np.float32)
        body = typeset(w, h - (5 if mark and base.isupper() else 3 if mark else 0), base, top, bottom, edge, **opt)
        out[h - body.shape[0]:] = body
        if mark:
            from PIL import Image, ImageDraw
            s = 4
            im = Image.new("L", (w * s, h * s), 0)
            dr = ImageDraw.Draw(im)
            cx, y0, y1 = w * s / 2, 1.2 * s, (4.2 if base.isupper() else 5.5) * s
            lw = int(1.6 * s)
            if mark == '"':
                for dx in (-2.6, 2.6):
                    dr.ellipse([cx + dx * s - 1.2 * s, y0, cx + dx * s + 1.2 * s, y0 + 2.4 * s], fill=255)
            elif mark == "`":
                dr.line([cx - 2.5 * s, y0, cx + 1.5 * s, y1], fill=255, width=lw)
            elif mark == "'":
                dr.line([cx + 2.5 * s, y0, cx - 1.5 * s, y1], fill=255, width=lw)
            elif mark == "^":
                dr.line([cx - 3.5 * s, y1, cx, y0, cx + 3.5 * s, y1], fill=255, width=lw)
            else:
                dr.line([cx - 4 * s, y1 - s, cx - 1.5 * s, y0, cx + 1.5 * s, y1 - s, cx + 4 * s, y0], fill=255, width=lw)
            m = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
            grown = np.maximum.reduce([np.roll(np.roll(m, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
            col = np.asarray(edge, np.float32) * (1 - m[..., None]) + np.asarray(top, np.float32) * m[..., None]
            a = np.clip(grown, 0, 1)[..., None]
            out[..., :3] = out[..., :3] * (1 - a) + col * a
            out[..., 3] = np.maximum(out[..., 3], grown * 255)
        out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
        return out
    return paint_


def _flipped(ch, opt):
    def paint_(w, h, d, alpha):
        out = typeset(w, h, ch, *_ORANGE, **opt)[::-1].copy()
        out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
        return out
    return paint_


for _i, _ch in enumerate(_ABC):
    T[f"12/{_i}/p0"] = (_ch, *_ORANGE, {"th": 1.3})
    T[f"12/{37 + _i}/p0"] = (_ch.lower(), *_ORANGE, {"th": 1.3})
    T[f"12/{63 + _i}/p0"] = (_ch, *_ORANGE, {"th": 2.0, "pad": 2})
for _f, _ch in _PUNCT.items():
    T[f"12/{_f}/p0"] = (_ch, *_ORANGE, {"th": 1.3})
for _f, _ch in ((90, "!"), (91, "-"), (92, "?"), (93, "-"), (94, "'"), (96, ".")):
    T[f"12/{_f}/p0"] = (_ch, *_ORANGE, {"th": 2.0, "pad": 2})
B["12/34/p0"] = _flipped("?", {"th": 1.3})
B["12/35/p0"] = _flipped("!", {"th": 1.3})
for _i, _a in enumerate(_ACCENTS):
    _base, _mark = _a[2], _a[3:]
    B[f"12/{97 + _i}/p0"] = _accented(_base, _mark, {"th": 1.3})
for _i in range(10):
    T[f"12/134/p{_i}"] = ("O" if _i == 0 else str(_i), *_ORANGE, {"th": 1.3})
    T[f"12/135/p{_i}"] = ("O" if _i == 0 else str(_i), *_ORANGE, {"th": 2.0, "pad": 2})
for _i, _ch in enumerate("x+-="):
    T[f"12/140/p{_i}"] = (_ch, *_ORANGE, {"th": 1.3})
    T[f"12/141/p{_i}"] = (_ch, *_ORANGE, {"th": 2.0, "pad": 2})
_WHITE = ([255, 255, 255], [255, 255, 255], [255, 255, 255])
_RED = ([255, 120, 60], [220, 20, 10], [250, 240, 200])
T["12/143/p0"] = ("PAUSE", *_ORANGE, {"th": 1.2})
for _f, _t, _th in ((144, "FINISH", 3.2), (146, "TIME UP", 3.2), (148, "GOAL", 3.2), (150, "DRAW", 3.2), (152, "GAME OVER", 2.2)):
    T[f"12/{_f}/p0"] = (_t, *_RED, {"th": _th, "pad": 2})
    T[f"12/{_f + 1}/p0"] = (_t, *_WHITE, {"th": _th, "pad": 2})


# ------------------------------------------------------------------ common UI (dir 0)
over, cutout, star_pts = M.over, M.cutout, M.star_pts
_GREEN = ([150, 255, 60], [40, 200, 20], [40, 10, 110])
for _i, _t in enumerate(["O", "1", "2", "3", "4", "5", "6", "7", "8", "9", "'", '"', "m", "cm"]):
    T[f"0/50/p{_i}"] = (_t, *_GREEN, {"th": 1.0, "pad": 0})


def _button(c, dark, text=None, tc=W):
    b = brief(c, E((0.5, 0.5), (0.5, 0.5), c=dark), E((0.5, 0.5), (0.42, 0.42), c=c), E((0.38, 0.32), (0.14, 0.08), c=[min(255, v + 80) for v in c], rot=-30))
    return over(b, text, tc, tc, dark, (0.2, 0.16, 0.8, 0.86), th=0.7, pad=0, edge_px=0.0) if text else b


def _cbutton(pts):
    y, d = [250, 196, 20], [150, 90, 0]
    return brief(y, E((0.5, 0.5), (0.5, 0.5), c=d), E((0.5, 0.5), (0.42, 0.42), c=y), P(pts, d))


B["0/52/p0"] = _button([40, 80, 230], [10, 20, 120], "A")
B["0/52/p1"] = _button([30, 170, 60], [0, 80, 20], "B")
B["0/52/p2"] = _cbutton([(0.5, 0.24), (0.76, 0.66), (0.24, 0.66)])
B["0/52/p3"] = _cbutton([(0.76, 0.5), (0.34, 0.76), (0.34, 0.24)])
B["0/52/p4"] = _cbutton([(0.24, 0.5), (0.66, 0.76), (0.66, 0.24)])
B["0/52/p5"] = _cbutton([(0.5, 0.76), (0.76, 0.34), (0.24, 0.34)])
B["0/52/p6"] = over(brief([150, 150, 160], R(0, 0, 1, 0.08, [70, 70, 80]), R(0, 0.92, 1, 1, [70, 70, 80]), R(0, 0, 0.08, 1, [70, 70, 80]), R(0.92, 0, 1, 1, [70, 70, 80])),
                    "Z", W, W, [50, 50, 60], (0.2, 0.16, 0.8, 0.86), th=0.7, pad=0, edge_px=0.0)
B["0/52/p7"] = brief([120, 120, 130], E((0.5, 0.78), (0.4, 0.2), c=[70, 70, 80]), R(0.42, 0.3, 0.58, 0.8, [200, 200, 210]),
                     E((0.5, 0.26), (0.26, 0.2), c=[230, 230, 236]), E((0.5, 0.26), (0.14, 0.1), c=[150, 150, 160]))
B["0/52/p8"] = brief(M.GOLD, E((0.5, 0.5), (0.34, 0.48), c=M.GOLD_D), E((0.5, 0.5), (0.26, 0.4), c=M.GOLD), R(0.46, 0.26, 0.54, 0.74, M.GOLD_D))
B["0/52/p9"] = brief(M.GOLD, P(star_pts(0.5, 0.54, 0.5), M.GOLD_D), P(star_pts(0.5, 0.54, 0.4), M.GOLD), E((0.43, 0.5), (0.03, 0.08), c=K), E((0.57, 0.5), (0.03, 0.08), c=K))
B["0/52/p10"] = _button([226, 40, 40], [120, 0, 0], "S")
B["0/52/p11"] = over(brief([150, 150, 160], R(0, 0, 1, 0.08, [70, 70, 80]), R(0, 0.92, 1, 1, [70, 70, 80]), R(0, 0, 0.08, 1, [70, 70, 80]), R(0.92, 0, 1, 1, [70, 70, 80])),
                     "R", W, W, [50, 50, 60], (0.2, 0.16, 0.8, 0.86), th=0.7, pad=0, edge_px=0.0)


def _quit(w, h, d, alpha):
    out = np.zeros((h, w, 4), np.float32)
    g = typeset(int(w * 0.62), h, "QUIT", [170, 255, 80], [40, 190, 20], [20, 40, 10], th=1.5, pad=1)
    out[:, :g.shape[1]] = g
    r = typeset(h, h - 2, "R", W, W, [50, 50, 60], th=1.2, pad=1)
    x0 = int(w * 0.66)
    out[1:h - 1, x0:x0 + h, :3] = [150, 150, 160]
    out[1:h - 1, x0:x0 + h, 3] = 255
    a = r[..., 3:] / 255
    out[1:h - 1, x0:x0 + h, :3] = out[1:h - 1, x0:x0 + h, :3] * (1 - a) + r[..., :3] * a
    out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
    return out


B["0/148/p0"] = _quit


# ------------------------------------------------------------------ per-directory modules (briefs_*.py: B and T dicts)
import glob as _glob
import importlib as _importlib

for _p in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "briefs_*.py"))):
    try:
        _mod = _importlib.import_module("." + os.path.basename(_p)[:-3], __package__)
    except Exception as _err:      # a batch being edited must not break the dev sheets of the others
        if not os.environ.get("MP3_BRIEFS_LENIENT"):
            raise
        print(f"briefs: skipped {os.path.basename(_p)}: {_err!r}", file=sys.stderr)
        continue
    B.update(getattr(_mod, "B", {}))
    T.update(getattr(_mod, "T", {}))


# ------------------------------------------------------------------ render

# MP3 images that are the same picture as one already briefed for Mario Party 1 (same size and format, coarse
# grids within 5 levels: `mp1_map.json`, made by comparing the two specs) use that brief.
MP1 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mp1_map.json")))


def paint(key, d):
    """Generator hook: RGBA uint8 for a briefed image, else None."""
    if key not in T and key not in B:
        return M.paint(MP1[key], d) if key in MP1 else None
    w, h = d["w"], d["h"]
    if key in T:
        text, top, bottom, edge, opt = T[key]
        out = typeset(w, h, text, top, bottom, edge, **opt)
        if "alpha2" not in d:                     # opaque picture: our text on black
            out[..., :3] *= out[..., 3:] / 255
            out[..., 3] = 255
        elif d["mode"] == "rgba1":
            out[..., 3] = np.where(out[..., 3] >= 96, 255, 0)
        return np.clip(out, 0, 255).astype(np.uint8)
    b = B.get(key)
    if b is None:
        return None
    alpha = G.unpack_alpha2(d["alpha2"], w, h) if "alpha2" in d else None
    if callable(b):
        return np.clip(b(w, h, d, alpha), 0, 255).astype(np.uint8)
    out = facepaint.render(b, w, h, grid=d.get("grid"), alpha=alpha, seed=G.h32("brief", key))
    return np.clip(out, 0, 255).astype(np.uint8)


def main(argv):
    from PIL import Image, ImageDraw
    out, sel = argv[1], argv[2]
    cell = int(argv[argv.index("--cell") + 1]) if "--cell" in argv else 128
    tex = json.load(open(os.path.join(SPEC, "textures.json")))
    keys = sorted((k for k in tex if k.split("/")[0] == sel.split("/")[0] and k.startswith(sel) or k.split("/")[0] == sel),
                  key=lambda k: (int(k.split("/")[1]), k.split("/")[2][0], int(k.split("/")[2][1:]) if k.split("/")[2][1:].isdigit() else 0))
    keys = [k for k in keys if k in B or k in T or k in MP1]
    cols = max(1, 1600 // (cell + 6))
    rows = (len(keys) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + 6), max(1, rows) * (cell + 12)), (24, 24, 28))
    dr = ImageDraw.Draw(sheet)
    for i, k in enumerate(keys):
        d = tex[k]
        im = Image.fromarray(paint(k, d), "RGBA")
        bg = Image.new("RGBA", im.size, (70, 70, 90, 255))
        bg.alpha_composite(im)
        s = min(cell / im.width, cell / im.height)
        x, y = (i % cols) * (cell + 6), (i // cols) * (cell + 12)
        dr.text((x + 1, y), k.split("/", 1)[1], fill=(255, 255, 0))
        sheet.paste(bg.convert("RGB").resize((int(im.width * s), int(im.height * s)), Image.NEAREST), (x, y + 11))
    sheet.save(out)
    print(f"briefs: {out} {sheet.size}, {len(keys)} painted in dir {sel} ({len(B)} briefs, {len(T)} typeset in all)")


if __name__ == "__main__":
    main(sys.argv)
