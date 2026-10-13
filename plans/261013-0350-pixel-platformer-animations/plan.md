---
title: "Pixel platformer and animation polish"
description: "Replace the snake with a self-built contribution platformer and add pixel-art animation polish to headings, footer, header and an About dialogue."
status: pending
priority: P2
effort: 10h
branch: "claude/sleepy-ramanujan-3oewz2"
tags: [feature, frontend, infra]
blockedBy: []
blocks: []
created: "2026-10-13T03:51:44.266Z"
createdBy: "ck:plan"
source: skill
---

# Pixel platformer and animation polish

## Overview

Replace the snake with a self-built contribution platformer and add pixel-art animation polish to headings, footer, header and an About dialogue.

Source design (approved): [brainstorm report](../reports/brainstorm-261013-pixel-platformer-animations.md).
Mode: fast. The design was settled in the brainstorm and the codebase is small, so no research, red-team or validation pass was run.

Current state:
- `scripts/build_assets.py` (389 lines) holds the pixel engine and writes the static SVGs in `assets/`. The engine is `Canvas`, `PAL`, `FONT`, `document()` and `layer()`, drawing on a 4px `CELL` grid with the PICO-8 palette.
- `.github/workflows/profile-assets.yml` runs daily. It builds the stats cards and the snk snake into `dist/`, then publishes `dist/` to the `output` branch.

## Key decisions
- Level design A: week column height = active days (0–7). An empty week is a pit; 3+ empty weeks in a row become a bridge.
- One night-scene SVG for the platformer. No light/dark `<picture>` pair.
- Daily cron only. The platformer is built in CI; every other SVG is built locally and committed.
- **Default state = full content.** Animations run *from* zero (`fill-mode: backwards`, or a finite iteration count). With `prefers-reduced-motion`, on mobile and in static renderers, every SVG still shows its complete information.
- Animate only `opacity` and `transform` with `steps()`/`step-end`. No animated SVG filters. No animated geometry attributes (`width`, `x`), which avoids Safari gaps.
- Deferred: RPG character sheet, insert-coin issue game, hourly "live" header.

## Verification toolkit (all phases)
SVGs cannot be unit-tested meaningfully, so verify them visually with headless Chromium (pre-installed). Keep this helper in the session scratchpad and do not commit it:
```bash
npm i --prefix "$SCRATCH" playwright-core
# shot.mjs: goto file://<svg>; then for t in [...]:
#   document.getAnimations().forEach(a => { a.pause(); a.currentTime = t * 1000 })
#   page.screenshot(...)
# executablePath: /opt/pw-browsers/chromium-1194/chrome-linux/chrome
```
- Open the SVG directly (as a document) for time-seeking.
- Also render it once through `<img>` in an HTML page (`--allow-file-access-from-files`) to confirm it works in img context.
- Emulate `reducedMotion: 'reduce'` once per asset to check the default state.

## Phase order
1 → 2 → 3 is the critical path. 4 depends only on 1, so it can run in parallel with 2. 5 depends on 4 (it reuses the `flipbook` helper).

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Extract shared pixel module](./phase-01-extract-shared-pixel-module.md) | Pending |
| 2 | [Build contribution platformer](./phase-02-build-contribution-platformer.md) | Pending |
| 3 | [Wire workflow and README](./phase-03-wire-workflow-and-readme.md) | Pending |
| 4 | [Animate headings and footer](./phase-04-animate-headings-and-footer.md) | Pending |
| 5 | [Header life and about dialogue](./phase-05-header-life-and-about-dialogue.md) | Pending |

## Dependencies

No other plans exist, so there are no cross-plan dependencies. External: GitHub GraphQL API (`contributionCalendar`) and the `README_STATS_TOKEN || GITHUB_TOKEN` secret (already used by the workflow).
