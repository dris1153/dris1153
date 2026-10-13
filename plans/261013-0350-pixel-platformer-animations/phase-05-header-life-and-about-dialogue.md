---
phase: 5
title: "Header life and about dialogue"
status: pending
priority: P2
effort: "3h"
dependencies: [4]
---

# Phase 5: Header life and about dialogue

## Overview
Add 4 small signs of life to the header scene, and a new RPG dialogue-box SVG for the About section with a typewriter greeting and a talking portrait.

## Requirements
- Functional, header (at most 4 new features; existing animations untouched):
  1. **Fireflies:** 4 single-cell `"a"`/`"b"` lights drifting and blinking low over the ground, on distinct periods.
  2. **Cat ear twitch:** a double twitch every ~7s.
  3. **Laptop glow:** a faint `"c"` flicker beside the dev's lap. Drop it if it doesn't read as screen light in screenshots.
  4. **Meteor shower:** a burst of 3 meteors every ~30s, in addition to the existing 9s shooting star.
- Functional, `assets/about-dialogue.svg`:
  - A box with a `TIEN` name tab.
  - A front-facing portrait (scale 2).
  - 3 lines that type in once per page load.
  - The mouth flaps while typing.
  - A blinking `▼` after typing ends.
- Non-functional:
  - Default/reduced-motion state:
    - header: unchanged scene
    - dialogue: all text visible, mouth closed, `▼` visible
  - Only `opacity`/`transform` animated.
  - The header stays a single file under ~40KB (check the current size first).

## Architecture

### Header (`header()` in `build_assets.py`)
- **Fireflies:**
  - 4 layers, each 1 cell.
  - Drift: keyframes over 5–6 waypoints with step-end at ~4fps, which reads as a pixel hop.
  - Blink: stacked opacity keyframes, so each firefly is a wrapper and an inner group, because an element runs only one transform animation.
  - Periods 5.3 / 6.1 / 7.7 / 8.9s, chosen to avoid sync.
  - Region x 20–200, y 76–84 (ridge/ground boundary). Confirm contrast in screenshots and stay away from the name text.
- **Cat ear twitch:**
  - Split the cat so its ears can be swapped: draw `CAT` without its two ear rows in the `dev` layer.
  - `flipbook("ears", [CAT_EARS, CAT_EARS_TWITCH], ...)` with slots .0–.15 and .3–.45, period 7s.
  - The footer cat stays a full static `CAT`.
- **Laptop glow:**
  - 2–3 `"c"` cells at each side of the dev's lap (around DEV rows 10–12, i.e. y ≈ 52–54).
  - Opacity flicker keyframes (.35/.8/.5) with step-end, period ~2.3s.
- **Meteor shower:**
  - 3 layers, each a head (`"7"`) plus a 3-cell trail (`"6"`, `"d"`).
  - Each has its own translate keyframes in a 30s cycle: active for ~0.8s, staggered 0.35s.
  - Paths cross the upper-right sky (x 150→300, y 0→40) so they never pass over `DRIS`.
  - `opacity:0` outside the active window, and by default.

### Dialogue (`dialogue()` in `build_assets.py`)
- `W, H = 300, 44` (1200×176px).
- Box:
  - outer `"0"` border
  - inner frame `"7"` with a `"6"` shade
  - fill `"1"`
  - name tab: a heading-style plate at top-left reading `TIEN`
- Portrait: new `FACE` sprite, 16×16, front-facing:
  - hair `"5"`/`"0"`, skin `"f"`, eyes `"0"`, shirt `"8"`, matching the header dev
  - drawn at scale 2 in a framed slot (x 6..40)
  - `MOUTH_CLOSED`/`MOUTH_OPEN` overlays
- Text: scale 1, x = 46, lines at y = 8 / 18 / 28, at most 40 chars per line. Suggested wording:
  1. `HI, I'M TIEN - DRIS ON THE INTERNET.`
  2. `WELCOME TO MY CORNER OF GITHUB.`
  3. `GRAB A SNACK AND LOOK AROUND!`

  All glyphs already exist in `FONT`. Do not reuse the HTML paragraph's facts, to avoid duplication.
- **Typewriter** (Safari-safe, no animated geometry):
  - Each line gets a `"1"` cover over the text. The cover sits inside a group with a static `clip-path` limited to the line's box.
  - The cover animates `transform: translateX(0)` → `translateX(line_px)` with `steps(n_chars)`.
  - Timing: 0.05s per char; start delays chained line after line (+0.3s pause); iteration count 1; `animation-fill-mode: backwards`.
  - The default transform is `translateX(line_px)`, so the text is revealed when there is no animation.
- **Mouth:** the open-mouth layer runs `opacity` keyframes (on/off at 8fps) for `iteration-count = typing_seconds / 0.25`. The default is `opacity:0`, so the mouth is closed.
- **▼:** a 5×3 sprite at bottom-right that blinks with `steps(1)` infinitely. The delay is the typing end, and it is visible by default.
- Write the file from `__main__` as `assets/about-dialogue.svg`.

### README
- Insert under the `h-about.svg` heading:

  ```html
  <img src="./assets/about-dialogue.svg" width="100%" alt="Tien says: Hi, I'm Tien - Dris on the internet. Welcome to my corner of GitHub. Grab a snack and look around!" />
  ```
- Drop the paragraph's first sentence ("Hi, I'm Tien — Dris on the internet."), since the dialogue and its alt text now carry it. The rest of the paragraph and the table stay unchanged.

## Related Code Files
- Modify:
  - `scripts/build_assets.py`
  - `README.md`
  - `assets/header.svg` (regenerated)
- Create: `assets/about-dialogue.svg` (generated)

## Implementation Steps
1. Header:
   - Measure the current `header.svg` size.
   - Add the features one at a time: fireflies → ear twitch → meteor shower → laptop glow.
   - Screenshot after each, at several t values (0, 2, 7.1, 15, 30.2s), and judge noise.
   - Remove any feature that reads as noise. Laptop glow is the first candidate.
2. Dialogue:
   - Draw `FACE` and the mouths, then build `dialogue()`.
   - Screenshot at t = 0, .5, 1.5, 3, 5s and under reduced motion. Verify the full text, the closed mouth and `▼` in that state.
3. Render through `<img>` in headless Chromium to confirm clip-path and transforms work in img context. If Safari or WebKit is unavailable, note that in the PR.
4. Update the README (dialogue img plus the trimmed paragraph).
5. Run `python3 scripts/build_assets.py` and commit the regenerated assets.

## Success Criteria
- [ ] The header has ≤4 new animated features; the existing star, cloud, tail, bubble and meteor animations are unchanged.
- [ ] Screenshots show no feature overlapping `DRIS` or the subtitle text.
- [ ] The dialogue types once per load and the mouth stops when the text completes.
- [ ] Under reduced motion all three lines and `▼` are visible.
- [ ] The README renders the dialogue above the trimmed paragraph and the alt text reads naturally.

## Risk Assessment
- **Header becomes busy:** cap at 4 features, with an explicit noise review and veto per feature.
- **Typewriter cover misaligned:** the cover must cover exactly the glyph cells (6 cells per char, 7 rows plus 1 for safety). Steps(n) means each step reveals one char.
- **Text in an image is not selectable:** acceptable for a greeting. Facts stay in HTML and the alt text carries the greeting.
- **Splitting the header cat into body and ears** could shift pixels: compare a rest-frame screenshot against the current header.
