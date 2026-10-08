"""Mario Party 3 (USA) MainFS: directory/file container with per-file compression.

Layout (big endian), from the PartyPlanner64 documentation:
    u32 dir_count, u32 dir_offset[dir_count]             (relative to the fs start)
    dir: u32 file_count, u32 file_offset[file_count]     (relative to the dir start)
    file: u32 decompressed_size, u32 compression_type, payload
Compression types used by MP3: 1 LZSS (1 KB ring), 2/4 LZ with 32-bit code words (12-byte header), 5 RLE.

    python -m games.marioparty3.mainfs <rom>      # census + identity/round-trip check
"""
import ctypes
import os
import struct
import sys

ROM_OFFSET = 0x557E20     # start of MainFS in the USA ROM (lui/addiu at 0x3619E/0x361A6)
ROM_END = 0x1209850       # start of the next container (text strings; then HVQ backgrounds at 0x128CC60)
HDR = {0: 8, 1: 8, 5: 8, 2: 12, 3: 12, 4: 12}     # types 2-4 repeat the decompressed size after the type

_dll = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "native", "mplz.dll"))
for _n in ("mp_dec1", "mp_enc1", "mp_dec5", "mp_enc5", "mp_dec2", "mp_enc2"):
    getattr(_dll, _n).restype = ctypes.c_int


def decompress(kind, data, pos, size):
    """Return (bytes, compressed_size)."""
    if kind == 0:
        return bytes(data[pos:pos + size]), size
    out = ctypes.create_string_buffer(size + 8)
    # the decoder may read a little past the end of the stream: hand it a bounded copy
    src = bytes(data[pos:pos + size * 2 + 64]) + bytes(8)
    fn = {1: _dll.mp_dec1, 5: _dll.mp_dec5, 2: _dll.mp_dec2, 3: _dll.mp_dec2, 4: _dll.mp_dec2}[kind]
    used = fn(src, out, size)
    return out.raw[:size], used


def compress(kind, raw):
    if kind == 0:
        return bytes(raw)
    out = ctypes.create_string_buffer(len(raw) * 2 + 64)
    fn = {1: _dll.mp_enc1, 5: _dll.mp_enc5, 2: _dll.mp_enc2, 3: _dll.mp_enc2, 4: _dll.mp_enc2}[kind]
    n = fn(bytes(raw), len(raw), out)
    return out.raw[:n]


def read(rom, base=ROM_OFFSET):
    """Return dirs[d][f] = dict(kind, raw, comp)."""
    u32 = lambda o: struct.unpack_from(">I", rom, o)[0]
    dirs = []
    for d in range(u32(base)):
        doff = base + u32(base + 4 + 4 * d)
        files = []
        for f in range(u32(doff)):
            foff = doff + u32(doff + 4 + 4 * f)
            size, kind = u32(foff), u32(foff + 4)
            h = HDR[kind]
            raw, used = decompress(kind, rom, foff + h, size)
            files.append({"kind": kind, "raw": raw, "comp": bytes(rom[foff + h:foff + h + used]),
                          "hdr": bytes(rom[foff + 8:foff + h])})
        dirs.append(files)
    return dirs


def stills(dirs):
    """(dir, file) of every HVQS picture: file f holds the picture, file f + 1 its 'HVQ-MPS 1.1' header."""
    return [(d, f - 1) for d, files in enumerate(dirs) for f, e in enumerate(files) if e["raw"][:8] == b"HVQ-MPS "]


def pack_dir(files):
    """One directory blob; files carry 'kind' and either 'comp' (kept as is) or only 'raw' (compressed here)."""
    out = bytearray(4 + 4 * len(files))
    struct.pack_into(">I", out, 0, len(files))
    for f, e in enumerate(files):
        struct.pack_into(">I", out, 4 + 4 * f, len(out))
        comp = e.get("comp")
        if comp is None:
            comp = compress(e["kind"], e["raw"])
        out += struct.pack(">II", len(e["raw"]), e["kind"]) + (struct.pack(">I", len(e["raw"])) if HDR[e["kind"]] == 12 else b"") + comp
        if len(out) & 1:
            out += b"\0"
    return bytes(out)


def table(offsets):
    """Directory table; offsets are relative to the start of the table (directories may live anywhere after it)."""
    return struct.pack(">I", len(offsets)) + b"".join(struct.pack(">I", o) for o in offsets)


def pack(dirs):
    """Contiguous image (retail layout)."""
    blobs = [pack_dir(files) for files in dirs]
    pos, offs = 4 + 4 * len(dirs), []
    for b in blobs:
        offs.append(pos)
        pos += len(b)
    return table(offs) + b"".join(blobs)


def main(argv):
    rom = open(argv[1], "rb").read()
    dirs = read(rom)
    nfiles = sum(len(d) for d in dirs)
    kinds = {}
    raw_total = comp_total = 0
    for d in dirs:
        for e in d:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
            raw_total += len(e["raw"])
            comp_total += len(e["comp"])
    print(f"mainfs: {len(dirs)} dirs, {nfiles} files, kinds {kinds}, raw {raw_total >> 10} KB, comp {comp_total >> 10} KB")
    same = pack(dirs)
    span = ROM_END - ROM_OFFSET
    print(f"identity repack: {len(same)} bytes of span {span}, equal={same == rom[ROM_OFFSET:ROM_OFFSET + len(same)]}")
    bad = worse = ours = 0
    for d in dirs:
        for e in d:
            if e["kind"] != 0:
                c = compress(e["kind"], e["raw"])
                back, _ = decompress(e["kind"], c + bytes(64), 0, len(e["raw"]))
                bad += back != e["raw"]
                ours += len(c)
            else:
                ours += len(e["raw"])
    print(f"own encoder: round-trip failures {bad}, total {ours >> 10} KB vs retail {comp_total >> 10} KB")
    print("files per dir:", " ".join(f"{i}:{len(d)}" for i, d in enumerate(dirs)))


if __name__ == "__main__":
    main(sys.argv)
