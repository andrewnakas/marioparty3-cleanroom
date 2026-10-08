# Mario Party 3 clean room: status

## State (2026-10-08, afternoon)
- **Published**: https://andrewnakas.github.io/marioparty3-cleanroom/ (repo `andrewnakas/marioparty3-cleanroom`,
  site on `gh-pages`, Pages status "built", ROM served). First publish = build with taint **0 failing**.
- Clean ROM = retail program + every picture and sound regenerated: 5570 MainFS images, 35 backgrounds (4037
  tiles), 78 stills, 782 waves. 32 MB. Our picture decoder replaces `lib/hvq`.
- Checked in headless Edge: boots, intro text, title card, file select, name entry, mode select.
  NOT yet checked: a board turn, a mini-game, sound level (headless runs are muted).
- Briefs (our own drawings / typeset text), about 2900 entries in `briefs*.py`, `faces.py`, `icons.py`:
  faces of the 8 players (all expressions), clothes/emblems, supporting cast faces, menu font sprites, dialog font
  (from its 2-bit outline), HUD digits, board UI (dir 19), title card + logo lettering, file/mode select headings,
  name-entry keyboard, results screens, item icons, mini-game signs/digits/faces (dirs 34-103).
- Backgrounds (boards, mini-game backdrops) and the 78 instruction stills are a smooth blur of the kept grid.

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
- Taint details: every MainFS file is stored by our own encoder (the retail encoder's token walk through zero
  runs repeats in every file); the dialog font's colour table is cut to 16 levels; the first 0x2C bytes of each
  HVQ-MPS header are kept layout; the colour grid of a sprite is alpha-weighted (no colour-key tint).
- A typed copyright line an agent put on the title card was replaced: we do not print others' notices on our art.
- Found after the first publish: FORM bitmaps of format 0x228 keep a second copy of the indices in the same
  chunk; the first published ROM still had 6 retail copies (32x32, 4-bit, under our palette). Fixed in
  `images._form_rebuild`, republished the same hour. Taint now also scans every stored BMP1 chunk; bitmaps of at
  most 4 palette entries are exempt (they are their own kept 2-bit outline). **User call**: say if those should
  be altered anyway.
- Voices: 44 lines in `voice_lines.json` (announcer, mario, luigi, peach, wario, waluigi, daisy); Yoshi and DK only
  make noises (resynthesised like other effects). "Good choice!" speakers, "Mario Party Three!" and "Miss!" are
  guesses (marked).
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
1. Play deeper headless (board turn, mini-game) and fix what is unreadable there.
2. Voices done as placeholders; confirm guessed speakers by ear.
3. Board backgrounds better than the blur.
4. Second look at briefs the agents flagged as weak (see "For the morning").

## For the morning
- To record voices: `D:/n64work/mp3work/practice/` (SCRIPT.txt + `practice_<who>_call_and_response.wav` for
  announcer, mario, luigi, peach, wario, waluigi, daisy). Lines marked (?) need a listen to confirm who speaks.
- Open https://andrewnakas.github.io/marioparty3-cleanroom/ : Enter = Start, X = A, arrows = stick. First load
  downloads a 32 MB ROM. Tell me what looks wrong first.
- Known rough spots: board / mini-game backgrounds and instruction pictures are a blur; sprite animations of
  Toad/Boo/Bob-omb etc. use one front drawing for every frame; emblems on mini-game player models are blurred;
  boot logos (N64, Nintendo, Hudson) are left blurred on purpose (trademarks are not redrawn).
- Things drawn by eye that need your check in game: Mario's cap emblem (mirrored half texture), dice face order
  in 100/11, which board space the signs 19/7, 19/88, 19/556-560 are, the name-entry keyboard cell positions.
