---
phase: 4
title: "Animate headings and footer"
status: completed
priority: P2
effort: "2h"
dependencies: [1]
---

# Phase 4: Animate headings and footer

## Overview
Bring the 4 section-heading icons to life with short, rare loops, and turn the footer line into a CONTINUE countdown with a spinning coin. Add a reusable `flipbook` helper (phase 5 uses it too).

## Requirements
- Functional:
  - **Heart** (ABOUT ME): 2 beats.
  - **Chest** (INVENTORY): lid opens, a coin pops out, lid closes.
  - **Scroll** (QUEST LOG): lines get written in.
  - **Trophy** (HIGH SCORES): a diagonal shine sweeps across.
  - Each icon is active ~0.8s, then rests ~4s. Delays are staggered 0 / 1.2 / 2.4 / 3.6s so the icons never beat in unison.
  - **Footer**, line 2 cycles over 16s:
    - 0–10s: `CONTINUE? N`, counting N down from 9 to 0
    - 10–12.5s: `GAME OVER`, blinking
    - 12.5–16s: `INSERT COIN TO CONTINUE`, blinking
  - A 4-frame coin spins next to the line.
- Non-functional:
  - Default (reduced-motion) state = today's look: rest icons and an `INSERT COIN TO CONTINUE` line.
  - Plate sizes and text positions are unchanged.

## Architecture

`pixel.py` gets a new helper:
```python
def flipbook(name, frames, x, y, period, slots, delay=0, scale=1):
    """Frame 0 is the rest pose, shown whenever no slot is active (and with
    reduced motion). slots: [(start_s, end_s, frame_index)] within period."""
    # returns (layers: list[str], css: str)
```
- Frame 0's layer: visible by default. Its keyframes hide it during every slot.
- Frame k≥1's layer: `opacity:0` by default. `@keyframes {name}{k}` shows it only during its slots.
- Every layer uses `animation: {name}{k} {period}s step-end infinite {delay}s`.
- Percentages come from seconds via the shared `pct()` formatter. If phase 2 defined `pct()` locally, move it into `pixel.py` now.
- Sprites with transparent pixels are fine because only one frame is visible at a time.

`heading(label, icon_frames, slots, delay)`:
- The plate layout uses `len(frames[0][0])`, so text stays put.
- Larger frames (the big heart) are drawn centred on frame 0's box, with a −1 cell offset.

Frames:
- **Heart:** `HEART`, then `HEART_BIG` (9×7). Slots: big 0–.15, rest, big .3–.45. Period 4.8s.
- **Chest:**
  - frames: `CHEST`, `CHEST_OPEN`, `CHEST_OPEN_COIN_LOW`, `CHEST_OPEN_COIN_HIGH`
  - sequence: open → coin low → coin high → open → closed, over ~0.9s
  - the coin may poke above the icon box but must stay within the plate's inner area (rows 2..12)
- **Scroll:** `SCROLL` (blank), then the same with 1, 2 and 3 `"5"` lines. Lines appear one by one, hold, then reset to blank.
- **Trophy:** `TROPHY`, then 3 frames with `"7"` glint pixels moving along a diagonal.

Footer (`footer()`):
- The current `coin` blink layer becomes the `INSERT COIN TO CONTINUE` layer:
  - default visible
  - keyframes hide it outside 12.5–16s and blink it inside that window
- `CONTINUE?` text layer: `opacity:0` by default, visible 0–10s.
- Digit:
  - one vertical strip of glyphs 9→0 inside a `clipPath` window
  - `transform: translateY` with `steps(10)` over 10s, wrapped in a group that is visible only 0–10s
  - this is one animated element instead of 10 layers
  - use the same clipPath technique as the phase 2 counter, and share a helper if one exists
- `GAME OVER`: `opacity:0` by default, visible and blinking 10–12.5s.
- Centre each phrase independently with `text_width`.
- Coin: `flipbook("coin", [COIN_FULL, COIN_MID, COIN_EDGE, COIN_MID], ...)` with period 0.6s, placed left of line 2. Reuse the `COIN` sprite from phase 2 as `COIN_FULL` if the size fits (move it to `pixel.py`).
- Cat and tail: unchanged.

## Related Code Files
- Modify:
  - `scripts/pixel.py` (`flipbook`, maybe `pct`, and `COIN` if shared)
  - `scripts/build_assets.py`
  - `assets/h-about.svg`, `assets/h-inventory.svg`, `assets/h-quests.svg`, `assets/h-scores.svg`, `assets/footer.svg` (regenerated)

## Implementation Steps
1. Add `flipbook()` (and `pct()` if not yet shared) to `pixel.py`.
2. Draw the new icon frames. Change the `HEADINGS` values to `(label, frames, slots, delay)` and update `heading()`.
3. Rebuild. Screenshot each heading at t = 0, .1, .35, .6, 2s plus delay offsets, and under reduced motion. Confirm the plate and text are pixel-identical to before at rest.
4. Rework `footer()` per the Architecture. Rebuild and take screenshots at t = 0, 4.5, 9.5, 11, 13, 15.9s and under reduced motion (it must equal the current footer except for the coin's rest frame).
5. Check `wc -c assets/*.svg` sizes (expected a few KB each).

## Success Criteria
- [x] Each heading animates ~0.8s, then rests. Staggered delays are visible when all 4 are shown on one page.
- [x] At rest and under reduced motion, headings match the current look.
- [x] The footer cycles countdown → GAME OVER → INSERT COIN cleanly, with no overlapping text in any frame.
- [x] Under reduced motion the footer shows `INSERT COIN TO CONTINUE` and the coin at rest.

## Risk Assessment
- **Visual noise:** 4 headings plus the footer coin. Mitigated by the long rest and staggering. If the coin spin feels busy, slow it to a 1.2s period.
- **Countdown off by one or digits misaligned:** the clip window must exactly match one glyph cell. Verify with screenshots at whole seconds.
- **The animated-heading arg change touches `HEADINGS`:** keep `__main__` output names identical so the README needs no change.
