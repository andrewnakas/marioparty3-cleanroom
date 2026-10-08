# Mario Party 3 clean room: status

## State (2026-10-08)
- Pipeline adapted from the finished Mario Party 1 clean room (`D:/n64work/marioparty-cleanroom`); first dev ROM
  (regenerated textures + samples, retail pictures) boots in headless Edge.
- Not published yet. Next gate: full clean ROM (pictures too) boots, taint 0 failing.

## Decisions (logged as made)
- ROM `Mario Party 3 (USA).z64` sha1 6beb80ff… (from `D:/Mario Party 3 (USA).zip`) = the decomp's target.
- **Work dir = `D:/n64work/mp3work`** (rom, build, devsite, sheets, shots, work/hvq cache). `D:/n64work/marioparty3`
  already belongs to another (Codex) workspace with a matching rebuild; left untouched. C: has 8 GB free: nothing
  is written there.
- **Web route = 3: clean ROM + WASM N64 emulator** (EmulatorJS 4.2.3 + mupen64plus_next, `ports/ejs`), same as
  Mario Party 1. Why: no PC port exists; the decomp (mariopartyrd/marioparty3) is splat + gcc 2.7.2 with ~all
  assets as binary blobs inside MainFS, so there is nothing to compile for the web and nothing the decomp extracts
  per file. The matching rebuild (Codex tree) proves the program is what the decomp builds.
- **Clean ROM = retail program + regenerated assets** written by our own tools:
  - MainFS at 0x557E20 (104 dirs, 4767 files; compression 1 = LZSS, 2/4 = LZ with 32-bit code words and a 12-byte
    header, 5 = RLE; own encoders for all, round-trip checked). 5570 images: ImgPack 1754 files, FORM 1197,
    RAW32 33, CI8 ("type 5", dir 19) 11, two 4-bit glyph sheets (0/43, 0/44).
  - Pictures are `HVQ-MPS 1.1`: 35 backgrounds (4072 tiles) at 0x128CC60 and 78 stills in MainFS dir 23 (file
    pairs picture + header). Dirty side decodes them once with the game's own `lib/hvq` under Unicorn
    (`hvq_dirty.py`). Clean side: decode entry `func_800698E8` jumps to our CRQ decoder (same signature), table
    setup `func_80069E68` returns at once, header files keep 0x2C bytes (magic, sizes, offsets) and are zero after.
  - Audio: MBF0 (131 sequences, B1 bank file, 237 waves) at 0x1881C40 and SBF0 (545 waves) at 0x1A56870; samples
    replaced in place, own 4-predictor codebook, loop states recomputed. FXD0 kept (settings).
- Kept as facts: program, text banks (0x1209850..0x128CC60, six languages), model geometry/motion (FORM without
  bitmaps/palettes, MTNX), layout tables, background metadata, sequences, envelopes, key maps, loop points.
- ROM-DB: the core's "Mario Party 3 (U) [f1]" hack slot is pointed at our ROM's MD5 (EEPROM 16 KB, rumble).
- Dev server port 8223, CDP port 9353. Headless runs are muted.

## Tools
- Build + check + publish: `sh tools/publish.sh [push "msg"]` (refuses unless `taint: 0 failing`).
- `games/marioparty3/`: `mainfs.py`, `images.py`, `hvqfs.py`, `audio.py`, `romtool.py`, `extract_spec.py` (dirty),
  `generate.py` (clean), `briefs.py` (MP3 briefs; `mp1_briefs.py` = primitives + character parts reused),
  `taint.py`, `look.py` (boot + contact sheet), `atlas.py` (retail|clean sheets).

## Next
1. Full clean ROM, taint, publish.
2. Readable text: glyph sheets, HUD digits, text strips inside textures.
3. Faces / portraits / icons via briefs.
4. Voices: placeholder TTS + practice pack.

## For the morning
- (filled in as things land)
