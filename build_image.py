#!/usr/bin/env python3
"""Draw the world-news infographic for Thursday 19 November 2026.

Builds a 1024x1024 newspaper-style front page with PIL and writes it to
entry.png next to this script. No network, no AI image generation: every
shape and every word is drawn by this code.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

NAVY = (27, 42, 74)
NAVY_LIGHT = (159, 179, 209)
RED = (192, 57, 43)
CREAM = (245, 241, 232)
INK = (30, 30, 30)
GREY = (90, 90, 90)
CARD_LINE = (208, 208, 208)
LEAD_BG = (253, 236, 234)
ALSO_BG = (232, 238, 245)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w, first_w=None):
    """Split text into lines that fit max_w (first line may use first_w)."""
    words = text.split()
    lines, cur, limit = [], "", first_w if first_w else max_w
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur, limit = word, max_w
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, color, max_w, leading, first_w=None):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(draw, text, fnt, max_w, first_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def rrect(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


# --- icons: each draws inside a square of side s at (x, y) ---

def icon_flags(d, x, y):
    rrect(d, [x, y, x + 118, y + 144], radius=12, fill=WHITE)
    for i, col in enumerate([(192, 57, 43), (37, 99, 235), (22, 163, 74)]):
        px = x + 26 + i * 32
        d.line([(px, y + 18), (px, y + 122)], fill=NAVY, width=4)
        d.polygon([(px, y + 18), (px + 22, y + 27), (px, y + 36)], fill=col)
    d.line([(x + 16, y + 122), (x + 102, y + 122)], fill=NAVY, width=4)


def icon_chart(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    for i, (bx, bh) in enumerate([(16, 22), (34, 34), (52, 48)]):
        d.rectangle([x + bx, y + 66 - bh, x + bx + 12, y + 66], fill=WHITE)
    d.line([(x + 12, y + 52), (x + 34, y + 40), (x + 54, y + 28), (x + 70, y + 16)],
           fill=WHITE, width=4)
    d.polygon([(x + 70, y + 16), (x + 58, y + 16), (x + 70, y + 28)], fill=WHITE)


def icon_tank(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    d.rounded_rectangle([x + 12, y + 36, x + 70, y + 56], radius=6, fill=WHITE)
    d.rectangle([x + 30, y + 26, x + 54, y + 38], fill=WHITE)
    d.line([(x + 52, y + 31), (x + 74, y + 27)], fill=WHITE, width=5)
    for cx in (22, 42, 62):
        d.ellipse([x + cx - 5, y + 58, x + cx + 5, y + 68], fill=WHITE)


def icon_scales(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    cx = x + s // 2
    d.ellipse([cx - 4, y + 10, cx + 4, y + 18], fill=WHITE)
    d.line([(cx, y + 16), (cx, y + 64)], fill=WHITE, width=4)
    d.line([(x + 16, y + 22), (x + 68, y + 22)], fill=WHITE, width=4)
    for px in (16, 68):
        d.line([(x + px, y + 22), (x + px, y + 42)], fill=WHITE, width=3)
        d.polygon([(x + px - 10, y + 42), (x + px + 10, y + 42), (x + px, y + 54)],
                  fill=WHITE)
    d.line([(cx - 14, y + 66), (cx + 14, y + 66)], fill=WHITE, width=4)


def icon_controller(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    d.rounded_rectangle([x + 10, y + 28, x + 74, y + 58], radius=12, fill=WHITE)
    d.line([(x + 26, y + 36), (x + 26, y + 50)], fill=bg, width=4)
    d.line([(x + 19, y + 43), (x + 33, y + 43)], fill=bg, width=4)
    for cx, cy in ((58, 38), (66, 46)):
        d.ellipse([x + cx - 3, y + cy - 3, x + cx + 3, y + cy + 3], fill=bg)


def icon_rocket(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    cx = x + s // 2
    d.polygon([(cx, y + 12), (cx + 12, y + 34), (cx + 12, y + 52),
               (cx - 12, y + 52), (cx - 12, y + 34)], fill=WHITE)
    d.ellipse([cx - 5, y + 30, cx + 5, y + 40], fill=bg)
    d.polygon([(cx - 12, y + 46), (cx - 21, y + 60), (cx - 12, y + 56)], fill=WHITE)
    d.polygon([(cx + 12, y + 46), (cx + 21, y + 60), (cx + 12, y + 56)], fill=WHITE)
    d.polygon([(cx - 6, y + 54), (cx + 6, y + 54), (cx, y + 70)],
              fill=(234, 88, 12))


def icon_euro(d, x, y, s, bg):
    rrect(d, [x, y, x + s, y + s], radius=14, fill=bg)
    f = font("DejaVuSans-Bold.ttf", 46)
    t = "\u20ac"
    tw = d.textlength(t, font=f)
    d.text((x + (s - tw) / 2, y + 16), t, font=f, fill=WHITE)


# --- the page ---

CARDS = [
    ("TECH", (37, 99, 235), "Anthropic's $81.3B IPO, the biggest ever",
     "Priced at $83 a share, valuing it near $1.5 trillion. Trading starts today.",
     icon_chart),
    ("MIDDLE EAST", (153, 27, 27), "Israeli tanks cross Gaza ceasefire line",
     "A rare ground raid beyond the Yellow Line sent displaced families fleeing.",
     icon_tank),
    ("LAW", (124, 58, 237), "UN court rules on Myanmar genocide case",
     "The court delivers its verdict in The Gambia's case over the 2017 crackdown.",
     icon_scales),
    ("GAMES", (22, 163, 74), "GTA VI rolls out worldwide",
     "Gamers enter Vice City as Grand Theft Auto VI begins its global launch.",
     icon_controller),
    ("SPACE", (14, 116, 144), "Voyager 1 reaches one light-day",
     "After 49 years in space, the probe is the first object one light-day from Earth.",
     icon_rocket),
    ("EUROPE", (194, 65, 12), "EU plans \u20ac45B loan for Ukraine",
     "A loan to cover Kyiv's budget, to be repaid once Russia pays reparations.",
     icon_euro),
]


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([8, 8, W - 8, H - 8], outline=NAVY, width=4)

    # masthead
    d.rectangle([24, 24, 1000, 128], fill=NAVY)
    d.ellipse([44, 44, 112, 112], outline=WHITE, width=3)
    d.ellipse([66, 44, 90, 112], outline=WHITE, width=2)
    d.line([(44, 78), (112, 78)], fill=WHITE, width=2)
    d.text((130, 38), "WORLD NEWS", font=font("DejaVuSerif-Bold.ttf", 62), fill=WHITE)
    d.text((132, 102), "THE DAY IN ONE IMAGE",
           font=font("DejaVuSans-Bold.ttf", 20), fill=NAVY_LIGHT)

    # date band
    d.rectangle([24, 140, 1000, 194], fill=RED)
    date = "THURSDAY, 19 NOVEMBER 2026"
    df = font("DejaVuSans-Bold.ttf", 34)
    d.text(((W - d.textlength(date, font=df)) / 2, 152), date, font=df, fill=WHITE)

    # lead story
    d.rectangle([24, 208, 1000, 388], fill=LEAD_BG, outline=RED, width=2)
    icon_flags(d, 40, 226)
    d.text((170, 224), "DIPLOMACY \u00b7 SHENZHEN",
           font=font("DejaVuSans-Bold.ttf", 20), fill=RED)
    d.text((170, 250), "Trump, Xi and Putin meet in Shenzhen",
           font=font("DejaVuSans-Bold.ttf", 34), fill=NAVY)
    block(d, 170, 300,
          "First three-way summit of the U.S., Chinese and Russian leaders, "
          "at the APEC meeting. Nuclear arms control tops the agenda.",
          font("DejaVuSans.ttf", 21), INK, 800, 28)

    # six cards, two columns by three rows
    col_x = [24, 508]
    row_y = [400, 560, 720]
    for i, (cat, col, head, body, icon) in enumerate(CARDS):
        cx = col_x[i % 2]
        cy = row_y[i // 2]
        rrect(d, [cx, cy, cx + 476, cy + 148], radius=12, fill=WHITE,
              outline=CARD_LINE, width=1)
        icon(d, cx + 14, cy + 14, 84, col)
        tx = cx + 110
        d.text((tx, cy + 12), cat, font=font("DejaVuSans-Bold.ttf", 16), fill=col)
        block(d, tx, cy + 36, head, font("DejaVuSans-Bold.ttf", 21), NAVY, 350, 25)
        block(d, tx, cy + 90, body, font("DejaVuSans.ttf", 16), GREY, 350, 21)

    # also strip
    rrect(d, [24, 880, 1000, 942], radius=10, fill=ALSO_BG)
    also = ("Van Gogh sells for a record $190.4m \u00b7 Canada rethinks its "
            "China ties \u00b7 Cyclone Akvan nears India's east coast")
    bf = font("DejaVuSans-Bold.ttf", 18)
    rf = font("DejaVuSans.ttf", 18)
    prefix = "Also: "
    pw = d.textlength(prefix, font=bf)
    d.text((40, 890), prefix, font=bf, fill=NAVY)
    y = 890
    first = True
    for line in wrap(d, also, rf, 930, first_w=930 - pw):
        x = 40 + (pw if first else 0)
        d.text((x, y), line, font=rf, fill=NAVY)
        y += 24
        first = False

    # source line
    src = ("Sources: Reuters \u00b7 Associated Press \u00b7 BBC \u00b7 "
           "The New York Times \u2014 19 November 2026")
    sf = font("DejaVuSans.ttf", 16)
    d.text(((W - d.textlength(src, font=sf)) / 2, 958), src, font=sf, fill=GREY)

    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
