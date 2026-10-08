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

# ------------------------------------------------------------------ render

def paint(key, d):
    """Generator hook: RGBA uint8 for a briefed image, else None."""
    if key not in T and key not in B:
        return None
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
    keys = [k for k in keys if k in B or k in T]
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
