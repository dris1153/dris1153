"""Builds the pixel-art SVGs in assets/ used by the profile README.

Everything is drawn on a 4px grid with the PICO-8 palette and a 5x7 bitmap
font (see pixel.py), so text stays editable here instead of being
hand-placed rects.

    python3 scripts/build_assets.py
"""
from pathlib import Path

from pixel import CELL, MOON, Canvas, document, flipbook, layer, text_width, timeline

ASSETS = Path(__file__).resolve().parent.parent / "assets"


# --- Sprites -------------------------------------------------------------

# Seen from behind, sitting on the hill and looking at the moon.
DEV = [
    ".....0000.....",
    "....055550....",
    "...05555550...",
    "...05555550...",
    "...05555550...",
    "....055550....",
    ".....0ff0.....",
    "...08888880...",
    "..0888888880..",
    "..0888888880..",
    "..0882222880..",
    "..0888888880..",
    ".011111111110.",
    ".011111111110.",
    "..0000000000..",
]

CAT = [
    ".0...0.",
    ".00.00.",
    ".05550.",
    ".05550.",
    "..050..",
    ".05550.",
    "0555550",
    "0555550",
    ".00000.",
]
CAT_TAIL_A = ["..00", ".050", "050.", "05..", "05..", "050.", ".000"]
CAT_TAIL_B = ["....", "....", "...0", "..05", ".050", "050.", "00.."]

CLOUD = [
    ".....6666.......",
    "...66666666..66.",
    ".6666666666666666",
    "66666666666666666",
    ".dddddddddddddd.",
]

STAR = [".a.", "aaa", ".a."]

BUBBLE = [
    "0000000000000",
    "0777777777770",
    "0777777777770",
    "0777777777770",
    "0777777777770",
    "0777777777770",
    "0777777777770",
    "0777777777770",
    "0000770000000",
    "....070......",
    "....00.......",
]
ICON_CODE = ["..8.....8..", ".8...8...8.", "8...8.....8", ".8.8.....8.", "..8.....8.."]
ICON_HEART = [".88.88.", "8888888", "8888888", ".88888.", "..888.."]
ICON_STAR = ["...a...", "..aaa..", "aaaaaaa", ".aaaaa.", "aa...aa"]




# --- Header --------------------------------------------------------------

def header():
    W, H = 300, 100
    HORIZON = 74
    DEV_X, CAT_X = 228, 258

    def sky(c):
        c.rect(0, 0, W, H, "1")
        # checker-dithered glow just above the horizon
        for y in range(HORIZON - 8, HORIZON):
            for x in range(W):
                if (x + y) % 2 == 0 and (y >= HORIZON - 4 or x % 4 == y % 4):
                    c.put(x, y, "2")

    def static_stars(c):
        for x, y in [(150, 8), (178, 30), (136, 46), (290, 50), (104, 4), (270, 4),
                     (196, 6), (232, 44), (140, 22), (6, 4), (60, 4), (164, 54), (284, 30)]:
            c.put(x, y, "6")

    def hills(c):
        # far ridge: stepped 2-cell columns in plum
        for x in range(0, W, 2):
            h = 2 + (x // 12) % 3 + (3 if 236 < x < 280 else 0) + (2 if 250 < x < 266 else 0)
            c.rect(x, HORIZON - h, 2, H, "2")
        # near ground with a rounded hill for the dev
        for x in range(W):
            top = 86 - (1 if (x // 16) % 2 else 0)
            dx = abs(x - 246)
            if dx < 34:
                top = min(top, 72 + (dx * dx) // 90)
            c.rect(x, top, 1, H - top, "3")
            c.put(x, top, "b")
        for x in range(9, W, 19):
            c.put(x, 85 if (x // 16) % 2 == 0 else 84, "b")

    def name(c):
        c.text(20, 12, "DRIS", "7", scale=4, shadow="2", offset=2)
        c.text(20, 46, "DUONG MINH TIEN", "f")
        c.text(20, 57, "UI · SHADERS · GAMES · AI TOOLS", "6")

    def dev(c):
        c.sprite(DEV_X, 42, DEV, scale=2)
        c.sprite(CAT_X, 54, CAT, scale=2)

    body = [
        layer(sky),
        layer(static_stars),
        layer(lambda c: c.sprite(0, 0, STAR), "twinkle", "animation-delay:0s;transform:translate(560px,60px)"),
        layer(lambda c: c.sprite(0, 0, STAR), "twinkle", "animation-delay:1.3s;transform:translate(880px,92px)"),
        layer(lambda c: c.sprite(0, 0, STAR), "twinkle", "animation-delay:2.1s;transform:translate(1150px,40px)"),
        layer(lambda c: c.sprite(0, 0, STAR), "twinkle", "animation-delay:.7s;transform:translate(700px,170px)"),
        layer(lambda c: c.sprite(150, 6, MOON, scale=2)),
        layer(lambda c: c.sprite(0, 0, CLOUD), "cloud", "--y:60px"),
        layer(lambda c: c.sprite(0, 0, CLOUD, scale=2), "cloud slow", "--y:128px"),
        layer(lambda c: c.rect(0, 0, 2, 1, "7"), "shoot"),
        layer(hills),
        layer(name),
        layer(lambda c: c.rect(118, 12, 4, 28, "8"), "blink"),
        layer(dev),
        layer(lambda c: c.sprite(CAT_X + 12, 58, CAT_TAIL_A, scale=2), "frame-a"),
        layer(lambda c: c.sprite(CAT_X + 12, 58, CAT_TAIL_B, scale=2), "frame-b"),
        layer(lambda c: c.sprite(DEV_X + 18, 16, BUBBLE, scale=2)),
        layer(lambda c: c.sprite(DEV_X + 20, 20, ICON_CODE, scale=2), "icon i1"),
        layer(lambda c: c.sprite(DEV_X + 24, 20, ICON_HEART, scale=2), "icon i2"),
        layer(lambda c: c.sprite(DEV_X + 24, 20, ICON_STAR, scale=2), "icon i3"),
    ]
    style = (
        ".blink{animation:blink 1.1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        ".twinkle{animation:twinkle 2.6s steps(1) infinite}"
        "@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.25}}"
        ".cloud{animation:cloud 60s steps(150) infinite;transform:translate(1220px,var(--y))}"
        ".cloud.slow{animation-duration:90s;animation-delay:-50s}"
        "@keyframes cloud{from{transform:translate(1220px,var(--y))}to{transform:translate(-160px,var(--y))}}"
        ".frame-a{animation:frame 1.6s steps(1) infinite}"
        ".frame-b{animation:frame 1.6s steps(1) infinite -.8s}"
        "@keyframes frame{0%{opacity:1}50%{opacity:0}}"
        ".icon{opacity:0;animation:icon 6s steps(1) infinite}"
        ".i2{animation-delay:2s}.i3{animation-delay:4s}"
        "@keyframes icon{0%{opacity:1}33.33%{opacity:0}}"
        ".shoot{opacity:0;animation:shoot 9s steps(24) infinite}"
        "@keyframes shoot{0%{opacity:1;transform:translate(700px,20px)}"
        "8%{opacity:1;transform:translate(560px,90px)}8.01%,100%{opacity:0;transform:translate(560px,90px)}}"
    )
    return document(W, H, "Dris (Duong Minh Tien): frontend, shaders, games, AI tools", "\n".join(body), style)


# --- Section headings -----------------------------------------------------

ICON_PERIOD = 4.8


def heading(label, frames, slots, delay, anchor="center"):
    icon = frames[0]
    w = text_width(label) + 30
    H = 15

    def plate(c):
        c.rect(1, 0, w - 2, H, "0")
        c.rect(0, 1, w, H - 2, "0")
        c.rect(1, 1, w - 2, H - 2, "d")
        c.rect(2, 2, w - 4, H - 4, "1")
        c.text(4 + len(icon[0]) + 4, 4, label, "7", shadow="0")

    icons, css = flipbook("ic", frames, 4, (H - len(icon)) // 2, ICON_PERIOD, slots, delay, anchor=anchor)
    return document(w, H, label.title(), "\n".join([layer(plate)] + icons), css)


# --- Footer ---------------------------------------------------------------

COIN_SPIN = [
    [".aa.", "a97a", "a97a", "a97a", "a99a", ".aa."],
    [".a.", "a7a", "a9a", "a9a", "a9a", ".a."],
    ["a", "7", "9", "9", "9", "a"],
    [".a.", "a7a", "a9a", "a9a", "a9a", ".a."],
]
FOOTER_PERIOD = 16
COUNTDOWN_S, GAME_OVER_S = 10, 12.5


def blink(start, end, on=.4, off=.25):
    """(t, opacity) points: visible-blinking from start to end, hidden elsewhere."""
    points, t = [(0, 0)], start
    while t < end:
        points += [(t, 1), (min(t + on, end), 0)]
        t += on + off
    return points


def footer():
    W, H = 300, 40
    LINE_Y = 21
    insert = "INSERT COIN TO CONTINUE"
    prompt = "CONTINUE? "
    over = "GAME OVER"
    prompt_x = (W - text_width(prompt + "0")) // 2
    digit_x = prompt_x + len(prompt) * 6

    def scene(c):
        c.rect(0, 0, W, H, "1")
        for x in range(W):
            c.rect(x, 30, 1, 10, "3")
            c.put(x, 30, "b")
        line = "THANKS FOR PLAYING!"
        c.text((W - text_width(line, 2)) // 2, 4, line, "a", scale=2, shadow="2")

    def digits(c):
        for n in range(10):
            c.text(digit_x, LINE_Y + n * 8, str(9 - n), "7")

    clip = (f'<clipPath id="digit"><rect x="{digit_x * CELL}" y="{LINE_Y * CELL}" '
            f'width="{5 * CELL}" height="{7 * CELL}"/></clipPath>')
    countdown = [(0, 1), (COUNTDOWN_S, 0)]
    coin_layers, coin_css = flipbook("spin", COIN_SPIN, (W - text_width(insert)) // 2 - 9, LINE_Y, .6,
                                     [(.15, .3, 1), (.3, .45, 2), (.45, .6, 3)])
    body = [
        layer(scene),
        layer(lambda c: c.text((W - text_width(insert)) // 2, LINE_Y, insert, "7"), "insert"),
        layer(lambda c: c.text((W - text_width(over)) // 2, LINE_Y, over, "8"), "over"),
        f'<g class="prompt">{layer(lambda c: c.text(prompt_x, LINE_Y, prompt, "7"))}'
        f'<g clip-path="url(#digit)">{layer(digits, "tick")}</g></g>',
        *coin_layers,
        layer(lambda c: c.sprite(270, 12, CAT, scale=2)),
        layer(lambda c: c.sprite(282, 16, CAT_TAIL_A, scale=2), "frame-a"),
        layer(lambda c: c.sprite(282, 16, CAT_TAIL_B, scale=2), "frame-b"),
    ]
    style = (
        timeline("insert", blink(GAME_OVER_S, FOOTER_PERIOD), FOOTER_PERIOD, 1)
        + timeline("over", blink(COUNTDOWN_S, GAME_OVER_S), FOOTER_PERIOD, 0)
        + timeline("prompt", countdown, FOOTER_PERIOD, 0)
        + timeline("tick", [(n, f"translateY(-{n * 8 * CELL}px)") for n in range(10)], FOOTER_PERIOD,
                   "translateY(0)", prop="transform")
        + coin_css
        + ".frame-a{animation:frame 1.6s steps(1) infinite}"
        ".frame-b{animation:frame 1.6s steps(1) infinite -.8s}"
        "@keyframes frame{0%{opacity:1}50%{opacity:0}}"
    )
    return document(W, H, "Thanks for playing! Insert coin to continue", f"<defs>{clip}</defs>\n" + "\n".join(body), style)


HEART_FRAMES = [
    [".00.00.", "0880880", "0888880", ".08880.", "..080.."],
    [".000.000.", "088808880", "088888880", "088888880", ".0888880.", "..08880..", "...080..."],
]
_CHEST_BODY = ["00099000", "04494440", "04444440", "00000000"]
CHEST_FRAMES = [
    [".000000.", "04444440"] + _CHEST_BODY,
    [".000000.", "04444440", "00000000", "01111110"] + _CHEST_BODY,
    [".000000.", "04444440", "00000000", "011a9110"] + _CHEST_BODY,
    [".00a900.", "044a9440", "00000000", "01111110"] + _CHEST_BODY,
]
_SCROLL = ["000000.", "0777770", ".077770", ".077770", ".077770", "0000000"]
SCROLL_FRAMES = [
    _SCROLL,
    _SCROLL[:1] + ["0755570"] + _SCROLL[2:],
    _SCROLL[:1] + ["0755570", ".077770", ".057770"] + _SCROLL[4:],
    _SCROLL[:1] + ["0755570", ".077770", ".055570"] + _SCROLL[4:],
]
_TROPHY = ["0000000", "0aaaaa0", ".0aaa0.", "..0a0..", "..0a0..", ".00000."]
TROPHY_FRAMES = [
    _TROPHY,
    ["0000000", "07aaaa0", ".0aaa0.", "..0a0..", "..0a0..", ".00000."],
    ["0000000", "0aa7aa0", ".07aa0.", "..0a0..", "..0a0..", ".00000."],
    ["0000000", "0aaaa70", ".0aa70.", "..070..", "..0a0..", ".00000."],
]

HEADINGS = {
    "h-about.svg": ("ABOUT ME", HEART_FRAMES, [(0, .15, 1), (.3, .45, 1)], 0),
    "h-inventory.svg": ("INVENTORY", CHEST_FRAMES, [(0, .15, 1), (.15, .35, 2), (.35, .6, 3), (.6, .8, 1)], 1.2, "bottom"),
    "h-quests.svg": ("QUEST LOG", SCROLL_FRAMES, [(0, .2, 1), (.2, .4, 2), (.4, .8, 3)], 2.4),
    "h-scores.svg": ("HIGH SCORES", TROPHY_FRAMES, [(0, .2, 1), (.2, .4, 2), (.4, .6, 3)], 3.6),
}

if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header())
    (ASSETS / "footer.svg").write_text(footer())
    for name, args in HEADINGS.items():
        (ASSETS / name).write_text(heading(*args))
    print("wrote", sorted(p.name for p in ASSETS.glob("*.svg")))
