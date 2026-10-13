"""Turns the last year of GitHub contributions into a pixel platformer level.

Each week is a column as tall as its active days. One or two empty weeks
make a pit, three or more a bridge. The dev and the cat run across it,
collect the coins and raise the flag. Built daily in CI:

    GITHUB_TOKEN=... python3 scripts/build_platformer.py --user dris1153
    python3 scripts/build_platformer.py --sample scripts/fixtures/contributions-sample.json
"""
import argparse
import json
import os
import sys
import urllib.request
from collections import namedtuple
from pathlib import Path

from pixel import CELL, MOON, Canvas, document, layer, pct, text_width

W, H = 300, 70
X0 = 18          # first column; the start platform fits the cat behind the dev
COL_W = 5
BLOCK_H = 4      # one block per active day
GROUND_Y = 64
FPS = 12
V = 1.75         # cells per frame
FLAG_S, CLEAR_S = 1.5, 2.5
CAT_LAG = 9      # cells the cat trails behind the dev

QUERY = """query($login: String!) {
  user(login: $login) { contributionsCollection { contributionCalendar {
    totalContributions
    weeks { contributionDays { date contributionCount contributionLevel } }
  } } }
}"""
RANK = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

Week = namedtuple("Week", "active total level")


# --- Data -------------------------------------------------------------------

def calendar(doc):
    if doc.get("errors"):
        raise SystemExit(f"GraphQL errors: {doc['errors']}")
    return doc["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "dris1153-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return calendar(json.load(r))


def load(path):
    return calendar(json.loads(Path(path).read_text()))


def weeks(cal):
    out = []
    for w in cal["weeks"]:
        days = w["contributionDays"]
        out.append(Week(
            active=sum(d["contributionCount"] > 0 for d in days),
            total=sum(d["contributionCount"] for d in days),
            level=max(RANK[d["contributionLevel"]] for d in days),
        ))
    assert len(out) <= 54, len(out)
    return out


# --- Sprites (side view, facing right) ---------------------------------------

DEV_RUN_A = [
    "..0000..",
    ".055550.",
    ".0555ff0",
    ".055f0f0",
    "..0fff0.",
    ".088880.",
    "0f8888f0",
    ".088880.",
    ".011110.",
    "01.0.010",
    "00....00",
]
DEV_RUN_B = DEV_RUN_A[:8] + [
    ".011110.",
    "..0110..",
    "..0000..",
]
DEV_JUMP = [
    "f......f",
    "0.0000.0",
    "0055550f",
    ".0555ff0",
    ".055f0f0",
    "..0fff0.",
    ".088880.",
    ".088880.",
    ".011110.",
    ".010.10.",
    ".00..00.",
]
CAT_RUN_A = [
    "0......0.0",
    "05....0550",
    ".05555555a",
    ".05555550.",
    ".050..050.",
    ".00...00..",
]
CAT_RUN_B = CAT_RUN_A[:4] + [
    "..050050..",
    "..00.00...",
]
CAT_JUMP = [
    "0.......0.0",
    ".05....0550",
    "..05555555a",
    ".055555550.",
    "050.....050",
    "00.......00",
]
COIN = [".a.", "a97", "a97", ".9."]
PENNANT = ["8888", "88888", "888", "8"]
BANNER = "COURSE CLEAR!"


# --- Level ------------------------------------------------------------------

def level(ws):
    """Returns (kinds, surface) for every week: kinds are col/pit/bridge and
    surface is the y of the walkable top, or None over a pit."""
    kinds = []
    i = 0
    while i < len(ws):
        if ws[i].active:
            kinds.append("col")
            i += 1
            continue
        j = i
        while j < len(ws) and not ws[j].active:
            j += 1
        kinds += ["bridge" if j - i >= 3 else "pit"] * (j - i)
        i = j
    surface = [
        GROUND_Y - w.active * BLOCK_H if k == "col" else GROUND_Y if k == "bridge" else None
        for w, k in zip(ws, kinds)
    ]
    return kinds, surface


def surf_at(surface, x):
    """Walkable y of grid column x (start and flag ground included)."""
    if x < X0:
        return GROUND_Y
    i = (x - X0) // COL_W
    return surface[i] if i < len(surface) else GROUND_Y


def path(surface, w, x_end):
    """Feet y for every left-edge x of a sprite w cells wide, plus the set of
    airborne x. Walks the flat stretches and jumps arcs between them."""
    xs = range(x_end + 1)

    def body(x):  # highest top under the whole sprite: the clearance limit
        tops = [t for t in (surf_at(surface, c) for c in range(x, x + w)) if t is not None]
        return min(tops) if tops else None

    def feet(x):
        tops = [t for t in (surf_at(surface, c) for c in range(x + 2, x + w - 2)) if t is not None]
        return min(tops) if tops else None

    stand = {x: feet(x) for x in xs if feet(x) is not None and feet(x) == body(x)}
    runs = []  # (x_first, x_last, y) walkable stretches at least 2 wide
    for x in xs:
        if x in stand and runs and runs[-1][1] == x - 1 and runs[-1][2] == stand[x]:
            runs[-1][1] = x
        elif x in stand:
            runs.append([x, x, stand[x]])
    runs = [r for r in runs if r[1] > r[0] or r[1] == x_end]

    y, air = {}, set()
    for (a0, a1, ya), (b0, _, yb) in zip(runs, runs[1:] + [(None, None, None)]):
        for x in range(a0, a1 + 1):
            y[x] = ya
        if b0 is None:
            break
        gap = any(feet(x) is None for x in range(a1, b0))
        apex = min(ya, yb) - (8 if gap else 3 if yb > ya else 6)
        while True:
            arc = {x: jump(x, a1, b0, ya, yb, apex) for x in range(a1 + 1, b0)}
            if all(body(x) is None or arc[x] <= body(x) for x in arc):
                break
            apex -= 1
        y.update(arc)
        air.update(arc)
    return y, air


def jump(x, xa, xb, ya, yb, apex):
    t = (x - xa) / (xb - xa)
    c = 2 * apex - (ya + yb) / 2
    return round((1 - t) ** 2 * ya + 2 * (1 - t) * t * c + t * t * yb)


def track(walk, x_start, x_end, frames):
    """[(x, feet_y, state)] per frame; state is run, jump or stand."""
    y, air = walk
    out = []
    for f in range(frames):
        x = min(x_end, round(x_start + V * f))
        out.append((x, y[x], "stand" if x == x_end else "jump" if x in air else "run"))
    return out


# --- CSS --------------------------------------------------------------------

def keyframes(name, values, n):
    """values: one CSS declaration string per frame; only changes are kept."""
    out, prev = [], None
    for f, v in enumerate(values):
        if v != prev:
            out.append(f"{pct(f / n * 100)}%{{{v}}}")
            prev = v
    return f"@keyframes {name}{{{''.join(out)}}}"


def translate(x, y):
    return f"transform:translate({x * CELL}px,{y * CELL}px)"


# --- Scene ------------------------------------------------------------------

def counter_digits(value):
    return f"{min(value, 99999):05d}"


def build(cal):
    ws = weeks(cal)
    total = sum(w.total for w in ws)
    kinds, surface = level(ws)
    x_last = X0 + len(ws) * COL_W           # first cell after the last column
    dev_w, cat_w = len(DEV_RUN_A[0]), len(CAT_RUN_A[0])
    dev_start, dev_end = CAT_LAG, x_last + 1  # first spot clear of the last column
    pole_x = min(dev_end + dev_w + 1, W - 6)
    dev_walk = path(surface, dev_w, dev_end)
    cat_walk = path(surface, cat_w, dev_end)
    # the cat sits down on the last solid spot a few cells behind the dev
    cat_end = max(x for x in cat_walk[0] if x <= dev_end - CAT_LAG - 3 and x not in cat_walk[1])

    run_frames = round((dev_end - dev_start) / V) + 1
    flag_frames, clear_frames = round(FLAG_S * FPS), round(CLEAR_S * FPS)
    n = run_frames + flag_frames + clear_frames
    T = n / FPS
    dev = track(dev_walk, dev_start, dev_end, n)
    cat = track(cat_walk, 0, cat_end, n)
    # victory hop pose while the banner shows
    dev = [(x, y, "jump" if f >= run_frames + flag_frames else s) for f, (x, y, s) in enumerate(dev)]

    def sky(c):
        c.rect(0, 0, W, H, "1")
        for x, y in [(40, 20), (72, 14), (96, 26), (130, 16), (158, 24), (184, 14),
                     (210, 22), (236, 30), (290, 16), (22, 30), (114, 32), (196, 34)]:
            c.put(x, y, "6")
        c.sprite(98, 1, MOON)

    def ground(c):
        for x in range(W):
            i = (x - X0) // COL_W if X0 <= x < x_last else None
            k = kinds[i] if i is not None else "ground"
            if k == "ground" or k == "col":
                c.rect(x, GROUND_Y, 1, H - GROUND_Y, "3")
                c.put(x, GROUND_Y, "b")
            else:
                c.rect(x, GROUND_Y, 1, H - GROUND_Y, "0")
        for i, (w, k) in enumerate(zip(ws, kinds)):
            x = X0 + i * COL_W
            if k == "col":
                top = surface[i]
                c.rect(x, top, COL_W, GROUND_Y - top, "4")
                for b in range(w.active):
                    y = GROUND_Y - b * BLOCK_H - 1
                    c.rect(x, y, COL_W, 1, "5")
                    c.put(x + (b % 2) * 2 + 1, y - 2, "0")
                c.rect(x, top, COL_W, 1, "b")
            elif k == "bridge":
                c.rect(x, GROUND_Y, COL_W, 2, "4")
                for dx in range(0, COL_W, 2):
                    c.put(x + dx, GROUND_Y, "9")
                if i == 0 or kinds[i - 1] != "bridge":
                    c.rect(x - 1, GROUND_Y - 4, 1, 4, "5")
                if i == len(ws) - 1 or kinds[i + 1] != "bridge":
                    c.rect(x + COL_W, GROUND_Y - 4, 1, 4, "5")
        # flagpole
        c.rect(pole_x, GROUND_Y - 30, 1, 30, "6")
        c.rect(pole_x - 1, GROUND_Y - 32, 3, 2, "a")
        c.rect(pole_x - 1, GROUND_Y - 1, 3, 1, "5")

    caption = f"{len(ws)} WEEKS · {total} CONTRIBUTIONS"

    def hud(c):
        c.text(4, 3, "COINS", "a", shadow="0")
        c.text(W - 4 - text_width(caption), 3, caption, "7", shadow="0")

    css = []
    body = [layer(sky), layer(ground), layer(hud)]

    # coins: one stack per active column, popped when the dev passes its centre
    running, ticks = 0, []
    for i, w in enumerate(ws):
        if not w.level:
            continue
        cx = X0 + i * COL_W + COL_W // 2
        hit = next((f for f, (x, _, _) in enumerate(dev) if x + dev_w // 2 >= cx), n - 1)
        running += w.total
        ticks.append((hit, running))
        top = surface[i]

        def stack(c, cx=cx, top=top, lv=w.level):
            for k in range(lv):
                c.sprite(cx - 1, top - 7 - k * 5, COIN)

        vals = []
        for f in range(n):
            d = f - hit
            vals.append("transform:translateY(0);opacity:1" if d < 0 else
                        f"transform:translateY(-{(d + 1) * CELL}px);opacity:1" if d < 3 else
                        "opacity:0")
        css.append(f".c{i}{{animation:c{i} {T:g}s step-end infinite}}" + keyframes(f"c{i}", vals, n))
        body.append(layer(stack, f"c{i}"))

    # counter: per digit a strip of glyphs 0-9 behind a one-glyph window
    shown, value, k = [], 0, 0
    for f in range(n):
        while k < len(ticks) and ticks[k][0] <= f:
            value = ticks[k][1]
            k += 1
        shown.append(counter_digits(value))
    defs = []
    for d in range(5):
        x, y = 4 + 36 + d * 6, 3
        defs.append(f'<clipPath id="d{d}"><rect x="{x * CELL}" y="{y * CELL}" width="{5 * CELL}" height="{7 * CELL}"/></clipPath>')

        def strip(c, x=x, y=y):
            for g in range(10):
                c.text(x, y + g * 8, str(g), "7")

        final = int(counter_digits(total)[d])
        vals = [f"transform:translateY(-{int(s[d]) * 8 * CELL}px)" for s in shown]
        css.append(f".d{d}{{transform:translateY(-{final * 8 * CELL}px);animation:d{d} {T:g}s step-end infinite}}"
                   + keyframes(f"d{d}", vals, n))
        body.append(f'<g clip-path="url(#d{d})">{layer(strip, f"d{d}")}</g>')

    # flag: pennant climbs the pole in 4 steps during the flag window
    flag_top, flag_low = GROUND_Y - 30, GROUND_Y - 6
    vals = []
    for f in range(n):
        k = min(4, max(0, (f - run_frames) * 5 // flag_frames)) if f >= run_frames else 0
        vals.append(f"transform:translateY(-{(flag_low - flag_top) * k // 4 * CELL}px)")
    body.append(layer(lambda c: c.sprite(pole_x + 1, flag_low, PENNANT), "flag"))
    css.append(f".flag{{transform:translateY(-{(flag_low - flag_top) * CELL}px);animation:flag {T:g}s step-end infinite}}"
               + keyframes("flag", vals, n))

    # actors: an outer group moves, inner layers swap run/jump/stand poses
    def actor(name, frames, run_a, run_b, jump_s):
        h = len(run_a)
        x0, y0, _ = frames[0]
        css.append(f".{name}{{{translate(x0, y0 - h)};animation:{name} {T:g}s step-end infinite}}"
                   + keyframes(name, [translate(x, y - h) for x, y, _ in frames], n))
        for state in ("run", "jump", "stand"):
            vals = [f"opacity:{1 if s == state else 0}" for _, _, s in frames]
            css.append(f".{name}-{state}{{opacity:{1 if state == 'stand' else 0};animation:{name}-{state} {T:g}s step-end infinite}}"
                       + keyframes(f"{name}-{state}", vals, n))
        jh = len(jump_s)
        return (
            f'<g class="{name}">'
            f'<g class="{name}-run">{layer(lambda c: c.sprite(0, 0, run_a), "ra")}{layer(lambda c: c.sprite(0, 0, run_b), "rb")}</g>'
            f'<g class="{name}-jump">{layer(lambda c: c.sprite(0, h - jh, jump_s))}</g>'
            f'<g class="{name}-stand">{layer(lambda c: c.sprite(0, 0, run_a))}</g>'
            "</g>"
        )

    body.append(actor("cat", cat, CAT_RUN_A, CAT_RUN_B, CAT_JUMP))
    body.append(actor("dev", dev, DEV_RUN_A, DEV_RUN_B, DEV_JUMP))
    css.append(".ra{animation:ra .34s step-end infinite}.rb{animation:ra .34s step-end infinite -.17s}"
               "@keyframes ra{0%{opacity:1}50%{opacity:0}}")

    def banner(c):
        c.text((W - text_width(BANNER, 2)) // 2, 18, BANNER, "a", scale=2, shadow="2")

    vals = [f"opacity:{1 if f >= run_frames + flag_frames else 0}" for f in range(n)]
    body.append(layer(banner, "clear"))
    css.append(f".clear{{opacity:0;animation:clear {T:g}s step-end infinite}}" + keyframes("clear", vals, n))

    title = f"Contribution platformer: {len(ws)} weeks, {total} contributions"
    return document(W, H, title, f"<defs>{''.join(defs)}</defs>\n" + "\n".join(body), "".join(css)), T


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--user", help="GitHub login; needs GITHUB_TOKEN in the env")
    src.add_argument("--sample", help="API-shaped JSON fixture")
    ap.add_argument("--out", default="dist/platformer.svg")
    args = ap.parse_args()
    if args.user:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("GITHUB_TOKEN is not set")
        cal = fetch(args.user, token)
    else:
        cal = load(args.sample)
    svg, T = build(cal)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg)
    print(f"wrote {out} ({len(svg)} bytes, {T:g}s loop)")


if __name__ == "__main__":
    main()
