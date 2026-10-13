---
phase: 1
title: "Extract shared pixel module"
status: completed
priority: P2
effort: "0.5h"
dependencies: []
---

# Phase 1: Extract shared pixel module

## Overview
Move the pixel engine out of `scripts/build_assets.py` into `scripts/pixel.py` so the new platformer builder can reuse it. This is a pure refactor: the generated assets must stay byte-identical.

## Requirements
- Functional: `python3 scripts/build_assets.py` writes exactly the same `assets/*.svg` bytes as before.
- Non-functional: standard library only. Keep the existing code style: module docstring, terse comments, no type hints.

## Architecture
`scripts/pixel.py` gets the engine:
- `CELL`, `PAL`, `FONT`
- `class Canvas`
- `text_width()`, `document()`, `layer()`

`scripts/build_assets.py` keeps:
- the `ASSETS` path
- every sprite constant
- `header()`, `heading()`, `footer()`, `HEADINGS` and `__main__`

It imports what it uses: `from pixel import Canvas, document, layer, text_width` (add others only if referenced).

`import pixel` works without packaging because Python puts the script's directory (`scripts/`) on `sys.path[0]`.

Shared sprites stay in `build_assets.py` for now. Phase 2 moves `STAR`/`MOON` into `pixel.py` only if it actually reuses them, so a sprite moves only once a second file needs it.

## Related Code Files
- Create: `scripts/pixel.py`
- Modify: `scripts/build_assets.py`

## Implementation Steps
1. Create `scripts/pixel.py`.
   - Docstring: "Pixel-art SVG engine shared by the asset builders: PICO-8 palette, 5x7 bitmap font, 4px grid."
   - Move `CELL`, `PAL`, `FONT`, `Canvas`, `text_width`, `document` and `layer` verbatim.
2. In `build_assets.py`:
   - Delete the moved code and add the import.
   - Update the module docstring to mention `pixel.py`.
3. Verify:
   - Run `python3 scripts/build_assets.py && git diff --exit-code assets/`. It must exit 0.
   - Run `grep -n "PAL\|FONT\|CELL" scripts/build_assets.py` to confirm no dangling references.

## Success Criteria
- [x] `git diff --exit-code assets/` passes after a rebuild.
- [x] `build_assets.py` has no engine code left. `pixel.py` does not import from `build_assets`.

## Risk Assessment
- Low. The only risk is a missed name, which shows up immediately as a `NameError` at build time.
