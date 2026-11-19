#!/usr/bin/env python3
"""One-off: draw static/og.png (1200x630). Needs Pillow (not required for the build)."""
from PIL import Image, ImageDraw, ImageFont
import glob
W, H = 1200, 630
im = Image.new("RGB", (W, H), "#0a0c12")
d = ImageDraw.Draw(im)
for i in range(H):  # simple dusk gradient
    t = i / H
    d.line([(0, i), (W, i)], fill=(int(10 + 60 * t), int(12 + 8 * t), int(18 + 55 * t)))
d.polygon([(W - 330, 520), (W - 190, 150), (W - 50, 520)], fill="#ff4fa3")
d.polygon([(W - 260, 520), (W - 190, 330), (W - 120, 520)], fill="#27d3e6")
fonts = glob.glob("/usr/share/fonts/**/*Bold*.ttf", recursive=True) or glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
def f(sz):
    return ImageFont.truetype(fonts[0], sz) if fonts else ImageFont.load_default()
d.text((70, 150), "GTA 6", font=f(120), fill="#ffffff")
d.text((70, 285), "Setup Builder", font=f(84), fill="#ff4fa3")
d.text((70, 410), "Budget-based console, display, headset", font=f(36), fill="#c3c9dc")
d.text((70, 455), "and storage picks. Prices checked on Amazon.in.", font=f(36), fill="#c3c9dc")
d.text((70, 560), "Independent site. Not affiliated with Rockstar Games.", font=f(26), fill="#8e96ad")
im.save("static/og.png", optimize=True)
