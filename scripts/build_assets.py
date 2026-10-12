"""Builds the pixel-art SVGs in assets/ used by the profile README.

Everything is drawn on a 4px grid with the PICO-8 palette and a 5x7 bitmap
font, so text stays editable here instead of being hand-placed rects.

    python3 scripts/build_assets.py
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CELL = 4  # px per grid cell

PAL = {
    "0": "#000000", "1": "#1d2b53", "2": "#7e2553", "3": "#008751",
    "4": "#ab5236", "5": "#5f574f", "6": "#c2c3c7", "7": "#fff1e8",
    "8": "#ff004d", "9": "#ffa300", "a": "#ffec27", "b": "#00e436",
    "c": "#29adff", "d": "#83769c", "e": "#ff77a8", "f": "#ffccaa",
}

FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10011 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 00000 00100",
    ",": "00000 00000 00000 00000 00000 00100 01000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    "?": "01110 10001 00001 00010 00100 00000 00100",
    ":": "00000 00100 00000 00000 00000 00100 00000",
    "-": "00000 00000 00000 01110 00000 00000 00000",
    "/": "00001 00010 00010 00100 01000 01000 10000",
    "&": "01100 10010 10100 01000 10101 10010 01101",
    "+": "00000 00100 00100 11111 00100 00100 00000",
    ">": "01000 00100 00010 00001 00010 00100 01000",
    "<": "00010 00100 01000 10000 01000 00100 00010",
    "*": "00000 10101 01110 11111 01110 10101 00000",
    "~": "00000 00000 01000 10101 00010 00000 00000",
    "|": "00100 00100 00100 00100 00100 00100 00100",
    "'": "00100 00100 00000 00000 00000 00000 00000",
    "·": "00000 00000 00000 00100 00000 00000 00000",
    "♥": "00000 01010 11111 11111 01110 00100 00000",
}


class Canvas:
    """Collects filled cells per colour and emits one <path> per colour."""

    def __init__(self):
        self.cells = {}

    def put(self, x, y, c):
        self.cells[(x, y)] = c

    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w):
                self.put(x + i, y + j, c)

    def sprite(self, x, y, rows, scale=1):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    self.rect(x + i * scale, y + j * scale, scale, scale, ch)

    def text(self, x, y, s, c, scale=1, shadow=None, offset=None):
        if shadow:
            o = offset or scale
            self.text(x + o, y + o, s, shadow, scale)
        for n, ch in enumerate(s):
            for j, row in enumerate(FONT[ch].split()):
                for i, bit in enumerate(row):
                    if bit == "1":
                        self.rect(x + (n * 6 + i) * scale, y + j * scale, scale, scale, c)

    def svg(self):
        by_colour = {}
        for (x, y), c in self.cells.items():
            by_colour.setdefault(c, set()).add((x, y))
        out = []
        for c, cells in by_colour.items():
            d = []
            for y in sorted({y for _, y in cells}):
                xs = sorted(x for x, yy in cells if yy == y)
                start = prev = xs[0]
                for x in xs[1:] + [None]:
                    if x is not None and x == prev + 1:
                        prev = x
                        continue
                    d.append(f"M{start} {y}h{prev - start + 1}v1h-{prev - start + 1}z")
                    if x is not None:
                        start = prev = x
            out.append(f'<path fill="{PAL[c]}" d="{"".join(d)}"/>')
        return f'<g transform="scale({CELL})">{"".join(out)}</g>'


def text_width(s, scale=1):
    return (len(s) * 6 - 1) * scale


def document(w, h, title, body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * CELL}" height="{h * CELL}" '
        f'viewBox="0 0 {w * CELL} {h * CELL}" shape-rendering="crispEdges" role="img" aria-label="{title}">\n'
        f"<title>{title}</title>\n<style>{style}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>\n"
        f"{body}\n</svg>\n"
    )


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

MOON = [
    "....0000....",
    "..00777700..",
    ".0777777770.",
    ".0777766770.",
    "077777677770",
    "077667777770",
    "077667777770",
    "077777777670",
    ".0777777770.",
    ".0776777770.",
    "..00777700..",
    "....0000....",
]

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


def layer(build, cls="", style=""):
    """Draws a layer; animated ones get a wrapper so CSS transforms don't
    replace the scale() on the inner group."""
    c = Canvas()
    build(c)
    if not cls and not style:
        return c.svg()
    attrs = (f' class="{cls}"' if cls else "") + (f' style="{style}"' if style else "")
    return f"<g{attrs}>{c.svg()}</g>"


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

def heading(label, icon):
    w = text_width(label) + 30
    H = 15

    def plate(c):
        c.rect(1, 0, w - 2, H, "0")
        c.rect(0, 1, w, H - 2, "0")
        c.rect(1, 1, w - 2, H - 2, "d")
        c.rect(2, 2, w - 4, H - 4, "1")
        c.sprite(4, (H - len(icon)) // 2, icon)
        c.text(4 + len(icon[0]) + 4, 4, label, "7", shadow="0")

    return document(w, H, label.title(), layer(plate))


# --- Footer ---------------------------------------------------------------

def footer():
    W, H = 300, 40

    def scene(c):
        c.rect(0, 0, W, H, "1")
        for x in range(W):
            c.rect(x, 30, 1, 10, "3")
            c.put(x, 30, "b")
        line = "THANKS FOR PLAYING!"
        c.text((W - text_width(line, 2)) // 2, 4, line, "a", scale=2, shadow="2")

    def coin(c):
        line = "INSERT COIN TO CONTINUE"
        c.text((W - text_width(line)) // 2, 21, line, "7")

    body = [
        layer(scene),
        layer(coin, "blink"),
        layer(lambda c: c.sprite(270, 12, CAT, scale=2)),
        layer(lambda c: c.sprite(282, 16, CAT_TAIL_A, scale=2), "frame-a"),
        layer(lambda c: c.sprite(282, 16, CAT_TAIL_B, scale=2), "frame-b"),
    ]
    style = (
        ".blink{animation:blink 1.4s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        ".frame-a{animation:frame 1.6s steps(1) infinite}"
        ".frame-b{animation:frame 1.6s steps(1) infinite -.8s}"
        "@keyframes frame{0%{opacity:1}50%{opacity:0}}"
    )
    return document(W, H, "Thanks for playing! Insert coin to continue", "\n".join(body), style)


HEART = [".00.00.", "0880880", "0888880", ".08880.", "..080.."]
SWORD = ["......00", ".....070", "....070.", "0..070..", ".0070...", "..00....", ".0.0....", "0......."]
CHEST = [".000000.", "04444440", "00099000", "04494440", "04444440", "00000000"]
SCROLL = ["000000.", "0777770", ".077770", ".077770", ".077770", "0000000"]
TROPHY = ["0000000", "0aaaaa0", ".0aaa0.", "..0a0..", "..0a0..", ".00000."]

HEADINGS = {
    "h-about.svg": ("ABOUT ME", HEART),
    "h-inventory.svg": ("INVENTORY", CHEST),
    "h-quests.svg": ("QUEST LOG", SCROLL),
    "h-scores.svg": ("HIGH SCORES", TROPHY),
}

if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header())
    (ASSETS / "footer.svg").write_text(footer())
    for name, (label, icon) in HEADINGS.items():
        (ASSETS / name).write_text(heading(label, icon))
    print("wrote", sorted(p.name for p in ASSETS.glob("*.svg")))
