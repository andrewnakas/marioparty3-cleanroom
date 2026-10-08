# Mario Party 3 — clean room web build

Play: **https://andrewnakas.github.io/marioparty3-cleanroom/**

Mario Party 3 (N64) running in the browser with **every picture and every sound regenerated**: textures,
sprites, fonts, pre-rendered board and minigame backgrounds, instrument samples, sound effects and voices.
The game program is the one the [mariopartyrd/marioparty3](https://github.com/mariopartyrd/marioparty3)
decompilation builds; it runs in the mupen64plus-next core of [EmulatorJS](https://github.com/EmulatorJS/EmulatorJS).

Controls: arrow keys move · `X` A · `C` B · `Z` Z · `S` R · `Q` L · `Enter` Start · `I J K L` C buttons ·
gamepads work too. Saves are kept in the browser.

## What is kept, what is generated

The decomp keeps every asset as a binary blob, so this project reads the ROM **once, in a "dirty room" step**
(`games/marioparty3/extract_spec.py`), keeps only coarse facts (`games/marioparty3/spec/`), and builds every
asset again from those facts (`games/marioparty3/generate.py`):

| Asset (count) | Kept fact | Generated |
|---|---|---|
| Textures and sprites in MainFS (5570 images in about 3000 files) | format, size, a 4×4 colour grid (16×16 from 128 px), a 2-bit alpha outline | colour from the grid; intensity masks from their 2-bit outline; faces, fonts, digits, icons and text strips drawn again from our own descriptions (`briefs*.py`, `faces.py`) |
| Pre-rendered backgrounds (35 pictures, 4037 tiles) and stills (78) | tile layout and camera, one 4×4 colour grid per 64×48 tile (16×16 per still) | a smooth picture of the grid, stored in our own picture format and drawn by our own decoder, which replaces the game's HVQ decoder (`lib/hvq`) |
| Instrument and effect samples (782 waves) | length, loop points, a coarse spectral outline, one median pitch | resynthesised, encoded with our own VADPCM codebook, in place |
| Music | the note sequences (scope: melodies kept) | played by the resynthesised instruments |
| Program, text, model geometry and motion, layout tables | as built by the decomp | — |

`games/marioparty3/taint.py` compares the clean ROM with the retail one: decoded textures, decoded backgrounds,
decoded samples, and the stored bytes of every retail asset against the whole clean image; shared runs of
32 bytes or more fail. It also maps every differing byte to a regenerated region. Result: [TAINT.md](TAINT.md).

No ROM is in this repository. The published site carries the clean ROM only.

## Build (Windows, Git Bash)

Needs Python 3 with numpy/Pillow/py7zr/unicorn, [Zig](https://ziglang.org) (host C compiler and the MIPS build of
the picture decoder), and your own Mario Party 3 (USA) ROM (sha1 `6beb80ff822b96bcf85dcdb512e8b2b7969d8259`).

    sh games/marioparty3/native/build.sh                       # codecs + the N64 picture decoder
    python -m games.marioparty3.extract_spec <rom> tex         # dirty room: spec/ (already in the repo)
    python -m games.marioparty3.generate <rom> clean.z64       # clean ROM
    python -m games.marioparty3.taint <rom> clean.z64 TAINT.md

Formats: MainFS, ImgPack and the audio tables follow the [PartyPlanner64](https://github.com/PartyPlanner64/PartyPlanner64)
documentation; `docs/DECOMP_PLAYBOOK.md` describes the method shared with the other clean-room ports.
