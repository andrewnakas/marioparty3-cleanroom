# Taint report

clean ROM sha1 `f2738a96107830bff3d9f509997de5c14ee2ba4c` (32 MB) vs the retail USA ROM.
Window 16 B, failing run >= 32 B.

| scan | retail windows indexed | clean streams with coincidences | longest shared run | failing |
|---|---|---|---|---|
| textures | 12034862 | 594 | 30 B | 0 |
| bitmap chunks | 1171590 | 1940 | 24 B | 0 |
| pictures | 20244809 | 109 | 27 B | 0 |
| samples | 26645414 | 42 | 21 B | 0 |
| raw image | 17610399 | 0 | 0 B | 0 |

| region | bytes | differing |
|---|---|---|
| header checksum | 8 | 8 |
| picture decoder (ours, over lib/hvq) + entry jump | 13072 | 1130 |
| HVQ table setup (returns at once) | 8 | 7 |
| MainFS | 13310512 | 13109809 |
| backgrounds | 6246368 | 5948129 |
| audio (samples, codebooks, loop states) | 6798912 | 5972819 |
| tail (free in retail) | 1058176 | 0 |

- bytes differing outside those regions: **0**
- audio bytes differing outside sample data / codebooks / loop states: **0**
- waves whose stored bytes equal retail: **0** of 782
- images whose pixels equal retail (more than 4 byte values): **0**

Kept facts (not scanned): the program (boot, code, overlays: what the matching decomp builds), text banks, model geometry and motion (1197 FORM files without their bitmaps and palettes, 1589 MTNX motions, 103 other layout/path files), model bitmaps of at most 4 palette entries (they are their own 2-bit outline), background metadata (tile counts, camera), sequences, envelopes, key maps, loop points, effect tables.

**0 failing.**
