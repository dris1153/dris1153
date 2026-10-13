---
phase: 2
title: "Build contribution platformer"
status: pending
priority: P1
effort: "4h"
dependencies: [1]
---

# Phase 2: Build contribution platformer

## Overview
Add `scripts/build_platformer.py`. It turns the last year of contributions into a pixel platformer level: the dev and the cat run left to right, jump between week columns, collect coins and reach a flag. The script writes a single animated night-scene SVG.

## Requirements
- Functional:
  - Fetch the contribution calendar from GraphQL with `GITHUB_TOKEN` from the env and `--user <login>`, or read a fixture with `--sample <json>`.
  - Write the SVG to `--out` (default `dist/platformer.svg`).
  - Build the level from weeks (design A):
    - column height = active days (0–7)
    - a run of 1–2 empty weeks = a pit
    - a run of ≥3 empty weeks = a bridge
  - The dev and cat run with 2 run frames, switch to a jump sprite while airborne, and the cat trails the dev.
  - Coins sit above each column, stacked by the week's max contribution level (1–4), and pop when collected.
  - A `COINS 00000` counter ticks up to the total.
  - Static caption: `52 WEEKS · N CONTRIBUTIONS`.
  - At the end: flagpole, flag raise, and a `COURSE CLEAR!` banner.
- Non-functional:
  - stdlib only (`urllib`, `json`, `argparse`)
  - deterministic output: no randomness, stable formatting
  - SVG under 150KB
  - loop of 16–18s
  - only `opacity`/`transform` animated, using `step-end`/`steps()`
  - default (non-animated) state shows the full level, all coins, the final counter value and the caption

## Architecture

### Data
POST `https://api.github.com/graphql` with headers `Authorization: bearer $GITHUB_TOKEN` and `User-Agent: dris1153-profile`:
```graphql
query($login: String!) {
  user(login: $login) { contributionsCollection { contributionCalendar {
    totalContributions
    weeks { contributionDays { date contributionCount contributionLevel } }
  } } }
}
```
- Raise on HTTP errors and on a non-empty `errors` key. If `GITHUB_TOKEN` is missing, exit non-zero with a clear message.
- snk uses the same API with `GITHUB_TOKEN`, so public data needs no PAT.
- Map `contributionLevel` to a rank: `NONE`→0, `FIRST_QUARTILE`→1, `SECOND_QUARTILE`→2, `THIRD_QUARTILE`→3, `FOURTH_QUARTILE`→4.
- Reduce each week to `Week(active=#days count>0, total=sum count, level=max rank)`.
- `assert len(weeks) <= 54`.
- `--sample` reads the same JSON shape as the API response (`{"data":{"user":...}}`), so the fixture and live data share one parser.

### Layout (cells; 1 cell = 4px)
| Const | Value | Note |
|---|---|---|
| `W, H` | 300, 70 | 1200×280px, same width as the header |
| `X0` | 16 | first column x; the start platform covers 0..X0 so the cat fits behind the dev |
| `COL_W` | 5 | 54 weeks × 5 = 270 → the flag area is still ≥14 cells |
| `BLOCK_H` | 4 | 7 blocks = 28 cells max |
| `GROUND_Y` | 64 | ground strip is rows 64–69 |
| HUD | y=3 | `COINS 00000` on the left; caption right-aligned |

Drawing:
- Sky: `"1"`.
- Static stars: a fixed list of `"6"` pixels in the top 30 rows, avoiding the HUD.
- Moon: reuse `MOON`. Move `MOON` (and `STAR`, if used) from `build_assets.py` into `pixel.py`.
- Ground: `"3"` with a `"b"` top line, as in the header.
- Columns: brown `"4"` pillar blocks with a `"0"`/`"5"` mortar line every `BLOCK_H` rows, so the block count reads as "days active". Cap the top with a `"b"` grass line.
- Pits: cut the ground strip and fill the hole with `"0"`.
- Bridge: `"4"` planks on `GROUND_Y` with `"9"` highlights and a `"5"` rope post at each end.
- Flag area: solid ground; a pole (`"6"` with an `"a"` knob), plus a pennant `"8"`.

### Walk surface and track
- `surface[i]`:
  - `GROUND_Y - active*BLOCK_H` for a column
  - `GROUND_Y` for a bridge or the start/flag ground
  - `None` for a pit
- `y_at(x)` (feet position) is built from flat segments plus jump arcs:
  - **Up-step** (next surface higher): arc from `edge - 2` to `edge + 3`, apex = `min(y_a, y_b) - 6`.
  - **Down-step**: short hop from `edge` to `edge + 3`, apex = `y_a - 3`.
  - **Pit run**: arc from the last solid edge `- 2` to the first solid edge after the pit `+ 3`, apex = `min(y_a, y_b) - 8`.
  - Arc: quadratic Bézier in `t = (x - xa) / (xb - xa)`: `y = (1-t)²ya + 2(1-t)t·c + t²yb`, with `c = 2·apex - (ya+yb)/2`. Round to whole cells.
- `track(x_start, x_end, offset)` samples frames at `FPS = 12` with `V ≈ 1.75` cells/frame. It returns `[(frame, x, y, airborne)]` and is used for both actors:
  - the dev
  - the cat, with `offset = -10` (10 cells behind) and its own sprite height
- Timeline:
  - run ≈ 13s
  - then the flag (≈1.5s): the dev stops at the pole and the pennant slides up in 4 steps
  - then `COURSE CLEAR!` (≈2.5s)
  - `T` = total frames / FPS
  - everything snaps back at 0%

### CSS generation
- **Actor position:** one `@keyframes` per actor with `p%{transform:translate(Xpx,Ypx)}`.
  - Drop consecutive duplicate positions.
  - Format percent with ≤3 decimals, trimmed.
  - Element uses `animation: <name> Ts step-end infinite`, so each sampled position is held (no sub-pixel tweening).
  - Each actor needs an outer wrapper `<g>`: `layer()` already wraps animated content, because a CSS transform would otherwise override the inner `scale()`.
- **Run/jump swap:** opacity keyframes emitted only at airborne transitions (run layer and jump layer are inverses). Run frames A/B alternate inside the run layer with the existing `frame` pattern (period ≈0.33s).
- **Coins:** each column `i` with level>0 gets `@keyframes c{i}`:
  - visible until its collect time `p_i`
  - translateY up 2–3 steps over ~3 frames
  - then `opacity:0` until 100%
  - visible again at 0%
  - `p_i` is the first frame where the dev's x ≥ the column centre.
  - Per-column keyframes are required: one shared keyframe with delays cannot make every coin reappear at loop start.
  - With no animation, the coins simply stay visible.
- **Counter:**
  - 5 digit positions. Each position is a vertical strip of glyphs 0–9 (pitch 8 cells) inside a `<clipPath>` window 5×7 cells.
  - Keyframes `translateY(-digit*pitch px)` change only when that digit changes (cumulative total after each collected column). The value resets to 0 at 0%.
  - The default transform (class rule) shows the **final** total, and the animation overrides it while running.
  - Define `clipPath` rects in px at the root and apply `clip-path` to an unscaled wrapper `<g>`, because `Canvas.svg()` content sits inside `scale(4)`.
  - Fallback if this grows too complex: a static final total in the HUD (the caption already carries the number).
- **Flag/banner:**
  - Pennant: translateY keyframes with step-end during the flag window.
  - `COURSE CLEAR!` (scale 2, `"a"` with `"2"` shadow, centred):
    - `opacity:0` by default
    - keyframes visible only in the final window
    - visible only while animating — it is transient FX
- `document()` already adds the `prefers-reduced-motion` guard.

### Fixture
`scripts/fixtures/contributions-sample.json` is synthetic, deterministic and API-shaped, with 53 weeks. It must cover:
- a partial first week (starts on a Wednesday) and a partial last week
- a 1-week pit and a 2-week pit
- a 4-week empty run (bridge)
- a 0→7 step and a 7→1 drop
- a full `FOURTH_QUARTILE` week
- `totalContributions` that matches the sum of the counts

Write it once with a throwaway generator in the scratchpad and commit only the JSON.

## Related Code Files
- Create:
  - `scripts/build_platformer.py`
  - `scripts/fixtures/contributions-sample.json`
- Modify:
  - `scripts/pixel.py` (receives `MOON`, and `STAR` if reused)
  - `scripts/build_assets.py` (import those sprites from `pixel`)

## Implementation Steps
1. Write the fixture JSON (see Fixture).
2. Data layer: `fetch(login, token)` and `load(path)` both return the calendar dict; `weeks(calendar)` returns `list[Week]`. Keep CLI parsing in `main()`.
3. Level builder: `segments(weeks)` returns per-column kinds (`col`/`pit`/`bridge`) with `surface` values. Draw the static scene on a `Canvas` (sky, stars, moon, ground, columns, pits, bridge, flag area, HUD caption).
4. New sprites, side view, facing right:
   - `DEV_RUN_A`, `DEV_RUN_B`, `DEV_JUMP` (~8×11): hair `"5"`, skin `"f"`, shirt `"8"`, pants `"1"`, outline `"0"`, matching the header palette.
   - `CAT_RUN_A`, `CAT_RUN_B`, `CAT_JUMP` (~9×6).
   - `COIN` (3×4, `"a"`/`"9"`/`"7"`) and `PENNANT`.
5. Track: `y_at`, `track()` and the timeline constants. Unit-check in a scratch run that x is monotonic, that y never goes below a surface at a solid column, and that the dev lands on every column top.
6. CSS emitters: `actor_css(name, frames)`, `airborne_css`, `coin_css(i, p)`, `counter_css`, `flag_css`, `banner_css`, plus a small `pct()` formatter.
7. Assemble the SVG with `document()` and `layer()`. Bump the `MOON` import and remove it from `build_assets.py`. Re-run `build_assets.py` and confirm `assets/` is unchanged.
8. Verify:
   - `python3 scripts/build_platformer.py --sample scripts/fixtures/contributions-sample.json --out "$SCRATCH/platformer.svg"`
   - `wc -c` must be < 150000.
   - Run twice and `cmp` the outputs (determinism).
   - Take screenshots at t = 0, 3, 7, 11, 14, 16s and under reduced-motion (see plan.md toolkit), and render through `<img>`.
   - Check: lands on tops, no clipping through pillars, coins vanish as passed, counter = total at the flag, banner only at the end.
9. Optional live check if a token is available: `GITHUB_TOKEN=... python3 scripts/build_platformer.py --user dris1153`.

## Success Criteria
- [ ] The fixture build produces a valid SVG under 150KB with a loop of 16–18s, and two runs are byte-identical.
- [ ] Screenshots show correct landings, pits, the bridge, coin pops, the counter reaching the total and the flag sequence.
- [ ] The reduced-motion render shows the full level, all coins, the final counter and the caption, with no banner.
- [ ] Works in an `<img>` context (headless Chromium). If Firefox is available, open it there too.
- [ ] `assets/` is unchanged after `build_assets.py` (only the sprite moved).

## Risk Assessment
- **Jump arcs look wrong (floaty or clipping):** tune the `JUMP_*` constants with screenshots and keep the arc maths in one function.
- **Pillars too tall to read:** 7×4 = 28 cells max is fine. If the scene feels cramped, drop `BLOCK_H` to 3.
- **Counter complexity:** documented fallback is a static total.
- **Large keyframe CSS:** ~200 positions × 2 actors ≈ 16KB plus coins ≈ 10KB, which is well under budget. If not, lower FPS to 10.
- **API shape drift or a token without scope:** fail loudly. The workflow then skips publishing and the previous `output` stays live.
