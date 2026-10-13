"""Pixel-art SVG engine shared by the asset builders: PICO-8 palette, 5x7
bitmap font, 4px grid."""

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


def pct(v):
    """Keyframe percentage with at most 3 decimals and no trailing zeros."""
    return f"{v:.3f}".rstrip("0").rstrip(".")


def document(w, h, title, body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * CELL}" height="{h * CELL}" '
        f'viewBox="0 0 {w * CELL} {h * CELL}" shape-rendering="crispEdges" role="img" aria-label="{title}">\n'
        f"<title>{title}</title>\n<style>{style}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>\n"
        f"{body}\n</svg>\n"
    )


def layer(build, cls="", style=""):
    """Draws a layer; animated ones get a wrapper so CSS transforms don't
    replace the scale() on the inner group."""
    c = Canvas()
    build(c)
    if not cls and not style:
        return c.svg()
    attrs = (f' class="{cls}"' if cls else "") + (f' style="{style}"' if style else "")
    return f"<g{attrs}>{c.svg()}</g>"
