"""Taint report: the clean ROM against the retail ROM (run in the dirty room; reads both).

    python -m games.marioparty3.taint <retail rom> <clean rom> [report.md]

Four content scans (cleanroom.taint: 16-byte windows, runs >= FAIL_RUN bytes fail), like against like:
  textures   every MainFS image as RGBA bytes (retail vs clean, decoded from their containers)
  pictures   every pre-rendered background tile / still as RGBA bytes (retail: HVQ decoded by the game's own
             decoder in the dirty room; clean: our CRQ pictures decoded)
  samples    every wave: decoded PCM and the stored sample bytes
  raw        the clean image from the first asset byte to the end, against the retail *stored* bytes of every
             image file, picture tile and sample (proves no retail payload is still lying in the image); the
             compressed layout tables of the image packs (kept structure) are blanked first
and a map of where the two images differ, which must stay inside the regenerated regions.
Kept facts are listed, not scanned.
"""
import hashlib
import sys

import numpy as np

from cleanroom import taint
from . import audio, hvq_dirty, hvqfs, images, mainfs, romtool

ASSETS_START = mainfs.ROM_OFFSET


def _rgba(px):
    """RGBA5551 words (h, w) -> RGBA8888 bytes, the same expansion the dirty decoder cache uses."""
    out = np.empty(px.shape + (4,), np.uint8)
    out[..., 0] = ((px >> 11) & 31) * 255 // 31
    out[..., 1] = ((px >> 6) & 31) * 255 // 31
    out[..., 2] = ((px >> 1) & 31) * 255 // 31
    out[..., 3] = 255
    return out.tobytes()


def _index(streams, flush=6_000_000):
    """taint.build_index with bounded memory: unique-merge every few million windows."""
    acc, pend, npend = np.zeros(0, np.uint64), [], 0
    for _, s in streams:
        h, per = taint._hashes(s)
        pend.append(h[~per])
        npend += len(pend[-1])
        if npend > flush:
            acc, pend, npend = np.unique(np.concatenate([acc] + pend)), [], 0
    return np.unique(np.concatenate([acc] + pend))


def _image_streams(dirs):
    for d, files in enumerate(dirs):
        for f, e in enumerate(files):
            for im in images.find(e["raw"]) or ():
                yield f"{d}/{f}/{im.key}", im.rgba.astype(np.uint8).tobytes()
            if (d, f) in images.GLYPH4:
                yield f"{d}/{f}/glyphs", e["raw"][images.GLYPH4[(d, f)]:]


def _scan(name, retail_streams, clean_streams, out):
    index = _index(retail_streams)
    hits = taint.scan(index, clean_streams)
    bad = [h for h in hits if h[3] >= taint.FAIL_RUN]
    worst = max((h[3] for h in hits), default=0)
    out.append((name, len(index), len(hits), worst, bad))
    return bad


def _chunks(buf, start, size=1 << 21):
    for o in range(start, len(buf), size):
        yield f"rom@{o:#x}", bytes(buf[o:o + size + taint.WINDOW - 1])


def _without_pack_tables(clean):
    """Copy of the clean image with the compressed header + entry table + tile map of every ImgPack blanked.

    Those sections are container layout (kept). Compressed, two packs with the same layout give the same LZ tokens,
    which would show up as a shared run although no pixel is involved."""
    import struct
    out = bytearray(clean)
    u32 = lambda o: struct.unpack_from(">I", clean, o)[0]
    base = mainfs.ROM_OFFSET
    n = 0
    for d in range(u32(base)):
        doff = base + u32(base + 4 + 4 * d)
        for f in range(u32(doff)):
            foff = doff + u32(doff + 4 + 4 * f)
            size, kind = u32(foff), u32(foff + 4)
            if kind == 0 or size < 0x2C:
                continue
            hd = mainfs.HDR[kind]
            head, _ = mainfs.decompress(kind, clean, foff + hd, 0x20)
            if struct.unpack_from(">I", head, 0)[0] not in (0x20, 0x1B):
                continue
            images_off = struct.unpack_from(">I", head, 8)[0]
            if not 0x20 <= images_off <= size:
                continue
            _, used = mainfs.decompress(kind, clean, foff + hd, images_off)
            out[foff + hd:foff + hd + used] = bytes(used)
            n += 1
    return bytes(out), n


def diff_map(retail, clean, regions):
    """-> (rows, stray): differing byte counts per region, and differing bytes outside every region."""
    n = min(len(retail), len(clean))
    a, b = np.frombuffer(retail[:n], np.uint8), np.frombuffer(clean[:n], np.uint8)
    diff = a != b
    covered = np.zeros(n, bool)
    rows = []
    for name, lo, hi in regions:
        covered[lo:hi] = True
        rows.append((name, lo, hi, int(diff[lo:hi].sum())))
    stray = np.nonzero(diff & ~covered)[0]
    return rows, stray


def main(argv):
    retail, clean = open(argv[1], "rb").read(), open(argv[2], "rb").read()
    assert hashlib.sha1(retail).hexdigest() != hashlib.sha1(clean).hexdigest()
    rdirs, cdirs = mainfs.read(retail), mainfs.read(clean)
    results = []
    stills = mainfs.stills(rdirs)

    # 1. textures
    bad = list(_scan("textures", _image_streams(rdirs), _image_streams(cdirs), results))

    # 2. pictures
    def retail_pics():
        for b in range(len(hvqfs.read(retail))):
            yield f"bg/{b}", hvq_dirty.bg(b).tobytes()
        for d, f in stills:
            yield f"still/{d}/{f}", hvq_dirty.fs(d, f).tobytes()

    def clean_pics():
        for b, files in enumerate(hvqfs.read(clean)):
            assert all(t[:7] == b"HVQSCRQ" for t in files[2:]), "retail picture left in the clean ROM"
            assert not any(files[1][hvqfs.HEAD_KEEP:]), "retail decoder tables left in the clean ROM"
            yield f"bg/{b}", b"".join(_rgba(hvqfs.uncrq(t[4:])) for t in files[2:])
        for d, f in stills:
            assert cdirs[d][f]["raw"][:3] == b"CRQ", "retail still left in the clean ROM"
            assert not any(cdirs[d][f + 1]["raw"][hvqfs.HEAD_KEEP:]), "retail decoder tables left in the clean ROM"
            yield f"still/{d}/{f}", _rgba(hvqfs.uncrq(cdirs[d][f]["raw"]))

    bad += _scan("pictures", retail_pics(), clean_pics(), results)

    # 3. samples
    rw, cw = audio.waves(retail), audio.waves(clean)
    assert [(w["pos"], w["len"]) for w in rw] == [(w["pos"], w["len"]) for w in cw]

    def smp(rom, ws):
        for w in ws:
            yield "pcm/" + w["name"], audio.decode(rom, w).astype("<i2").tobytes()
            yield "bytes/" + w["name"], bytes(rom[w["pos"]:w["pos"] + w["len"]])

    bad += _scan("samples", smp(retail, rw), smp(clean, cw), results)

    # 4. retail stored payloads anywhere in the clean image
    def stored():
        for d, files in enumerate(rdirs):
            for f, e in enumerate(files):
                if images.kind(e["raw"]) in ("pack", "raw32", "ci8", "hvqhead") or (d, f) in stills:
                    yield f"{d}/{f}", e["comp"]
        for b, files in enumerate(hvqfs.read(retail)):
            yield f"bg/{b}", b"".join(files[1:])
        for w in rw:
            yield w["name"], bytes(retail[w["pos"]:w["pos"] + w["len"]])

    masked, npacks = _without_pack_tables(clean)
    bad += _scan("raw image", stored(), _chunks(masked, ASSETS_START), results)

    # where the images differ
    regions = [("header checksum", 0x10, 0x18),
               ("picture decoder (ours, over lib/hvq) + entry jump", hvqfs.CODE_ROM, hvqfs.DECODE_ROM + 8),
               ("HVQ table setup (returns at once)", hvqfs.SETUP_ROM, hvqfs.SETUP_ROM + 8),
               ("MainFS", mainfs.ROM_OFFSET, mainfs.ROM_END),
               ("backgrounds", hvqfs.ROM_OFFSET, hvqfs.ROM_END),
               ("audio (samples, codebooks, loop states)", hvqfs.ROM_END, romtool.FREE_START),
               ("tail (free in retail)", romtool.FREE_START, max(len(retail), len(clean)))]
    rows, stray = diff_map(retail, clean, regions)
    # inside audio only sample bytes, codebooks and loop states may differ
    allowed = np.zeros(len(retail), bool)
    for w in rw:
        allowed[w["pos"]:w["pos"] + w["len"]] = True
        if w["book"]:
            allowed[w["book"]["pos"] + 8:w["book"]["pos"] + 136] = True
        if w["loop"] and w["type"] == 0:
            allowed[w["loop"]["pos"] + 12:w["loop"]["pos"] + 44] = True
    lo, hi = hvqfs.ROM_END, romtool.FREE_START
    a, b = np.frombuffer(retail[lo:hi], np.uint8), np.frombuffer(clean[lo:hi], np.uint8)
    audio_stray = int(((a != b) & ~allowed[lo:hi]).sum())
    same_samples = sum(retail[w["pos"]:w["pos"] + w["len"]] == clean[w["pos"]:w["pos"] + w["len"]] for w in rw)
    same_images = sum(1 for (k, s), (_, t) in zip(_image_streams(rdirs), _image_streams(cdirs)) if s == t and len(set(s)) > 4)

    kept = {k: sum(1 for files in rdirs for e in files if images.kind(e["raw"]) == k) for k in ("mtnx", "other", "form")}
    lines = ["# Taint report", "",
             f"clean ROM sha1 `{hashlib.sha1(clean).hexdigest()}` ({len(clean) >> 20} MB) vs the retail USA ROM.",
             f"Window {taint.WINDOW} B, failing run >= {taint.FAIL_RUN} B.", "",
             "| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |",
             "|---|---|---|---|---|"]
    for name, nidx, nhits, worst, b in results:
        lines.append(f"| {name} | {nidx} | {nhits} | {worst} B | {len(b)} |")
    lines += ["", "| region | bytes | differing |", "|---|---|---|"]
    for name, lo, hi, nd in rows:
        lines.append(f"| {name} | {hi - lo} | {nd} |")
    lines += ["", f"- bytes differing outside those regions: **{len(stray)}**",
              f"- audio bytes differing outside sample data / codebooks / loop states: **{audio_stray}**",
              f"- waves whose stored bytes equal retail: **{same_samples}** of {len(rw)}",
              f"- images whose pixels equal retail (more than 4 byte values): **{same_images}**", "",
              "Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds), "
              "text banks, model geometry and motion "
              f"({kept['form']} FORM files without their bitmaps and palettes, {kept['mtnx']} MTNX motions, "
              f"{kept['other'] - len(images.GLYPH4)} other layout/path files), "
              "background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables."]
    failing = len(bad) + len(stray) + audio_stray + same_samples + same_images
    lines += ["", f"**{failing} failing.**"]
    if bad:
        lines += ["", "Failing streams:"] + [f"- {h[0]} at {h[1]}: run {h[3]} B" for h in sorted(bad, key=lambda h: -h[3])[:300]]
    if len(argv) > 3:
        open(argv[3], "w").write("\n".join(lines) + "\n")
    for name, nidx, nhits, worst, b in results:
        print(f"taint {name}: {nhits} coincidences, longest {worst} B, {len(b)} failing")
    print(f"diff: stray {len(stray)}, audio stray {audio_stray}, retail-equal waves {same_samples}, images {same_images}")
    print(f"taint: {failing} failing")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
