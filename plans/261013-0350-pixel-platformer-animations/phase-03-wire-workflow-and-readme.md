---
phase: 3
title: "Wire workflow and README"
status: completed
priority: P1
effort: "0.5h"
dependencies: [2]
---

# Phase 3: Wire workflow and README

## Overview
Swap the snk snake for the platformer: build it in the daily workflow, publish it to the `output` branch, and point the README at it.

## Requirements
- Functional:
  - The workflow builds `dist/platformer.svg` and publishes it along with the 4 stats cards.
  - The snake files are no longer produced or referenced.
- Non-functional:
  - Daily cron unchanged. No new actions or dependencies; `ubuntu-latest` ships `python3`.

## Architecture
In `.github/workflows/profile-assets.yml`, replace the `Generate contribution snake` step (and its root/dist comment) with:
```yaml
      - name: Build contribution platformer
        run: python3 scripts/build_platformer.py --user ${{ github.repository_owner }} --out dist/platformer.svg
        env:
          GITHUB_TOKEN: ${{ secrets.README_STATS_TOKEN || secrets.GITHUB_TOKEN }}
```
- The step order no longer matters, because there is no root-owned `dist/` from the Docker action.
- The repo must be checked out for `scripts/`. The current workflow has **no `actions/checkout` step**: the stats action and snk don't need one. Add `- uses: actions/checkout@v4` as the first step.
- `peaceiris/actions-gh-pages` replaces the branch contents by default (`keep_files: false`), so the old snake SVGs disappear from `output` on the first run.

In `README.md`, under HIGH SCORES, replace the snake `<picture>` block with:
```html
<p align="center">
  <img src="https://raw.githubusercontent.com/dris1153/dris1153/output/platformer.svg" width="100%" alt="dris1153's contribution graph as a pixel platformer level: each week is a column as tall as the days with commits, and a developer and a cat run across it collecting coins" />
</p>
```

## Related Code Files
- Modify:
  - `.github/workflows/profile-assets.yml`
  - `README.md`

## Implementation Steps
1. Edit the workflow:
   - Add the checkout step.
   - Replace the snk step with the platformer step.
   - Drop the snk-specific comment.
2. Edit the README snake block as above.
3. Lint the YAML: `python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1]))" .github/workflows/profile-assets.yml`. If PyYAML is missing, do a careful manual review of indentation.
4. Run `grep -n "snake\|snk" README.md .github/workflows/profile-assets.yml` and expect no hits.
5. After merge to `main`, the `push` trigger runs the workflow. Confirm it is green and that `output/platformer.svg` exists. If it fails, the old README still references a missing file only until the fix lands, so act quickly.

## Success Criteria
- [x] The workflow YAML parses and has a checkout step followed by the platformer step. Snk is gone.
- [x] The README has no snake references, and the platformer `<img>` has descriptive alt text.
- [ ] Post-merge run is green and `output` contains `platformer.svg` and the 4 stats SVGs.

## Risk Assessment
- **Broken image between merge and the first workflow run (~1–2 min):** acceptable. Optionally trigger `workflow_dispatch` right after merge.
- **Camo cache serving the old content for a few minutes:** harmless.
- **Missing checkout step makes the script path fail:** covered by step 1. Verify it in the first run log.
