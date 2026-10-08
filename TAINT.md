# Taint report

clean ROM sha1 `9e27e9f04a95f3df164b07fe747f7dd9ce906182` (32 MB) vs the retail USA ROM.
Window 16 B, failing run >= 32 B.

| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |
|---|---|---|---|---|
| textures | 12034862 | 878 | 41 B | 5 |
| pictures | 20244809 | 109 | 27 B | 0 |
| samples | 26645414 | 40 | 21 B | 0 |
| raw image | 17661705 | 6 | 53 B | 4 |

| region | bytes | differing |
|---|---|---|
| header checksum | 8 | 8 |
| picture decoder (ours, over lib/hvq) + entry jump | 13072 | 1130 |
| HVQ table setup (returns at once) | 8 | 7 |
| MainFS | 13310512 | 13140585 |
| backgrounds | 6246368 | 5948129 |
| audio (samples, codebooks, loop states) | 6798912 | 5980650 |
| tail (free in retail) | 1058176 | 0 |

- bytes differing outside those regions: **0**
- audio bytes differing outside sample data / codebooks / loop states: **0**
- waves whose stored bytes equal retail: **0** of 782
- images whose pixels equal retail (more than 4 byte values): **0**

Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds), text banks, model geometry and motion (1197 FORM files without their bitmaps and palettes, 1589 MTNX motions, 103 other layout/path files), background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables.

**9 failing.**

Failing streams:
- rom@0xb57e20 at 974541: run 53 B
- rom@0x1157e20 at 1265540: run 42 B
- rom@0x1357e20 at 29668: run 42 B
- 24/5/p5 at 451: run 41 B
- 83/3/p0 at 2529: run 39 B
- rom@0x557e20 at 71427: run 37 B
- 24/5/p0 at 46: run 34 B
- 24/5/p3 at 186: run 34 B
- 24/5/p11 at 558: run 33 B
