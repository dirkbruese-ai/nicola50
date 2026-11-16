"""Baut die Polaroid-Kacheln für die Intro-Animation (Foto + "With love from <Absender>" fest ins Bild geschrieben).
Aufruf: python3 tools/build_intro.py <auswahl.json>   mit [[bildpfad, absender], ...] (55 Stück, Pfade relativ zum Repo)
Schreibt img/intro/t/NN.jpg und intro.js (const INTRO_TILES)."""
import json, sys, os
from PIL import Image, ImageOps, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
F = R + "tools/fonts/"
W, P, BAND = 900, 34, 170           # Breite, Rand, Schriftfeld unten
H = W - 2 * P + P + BAND + P         # Foto quadratisch
sel = json.load(open(sys.argv[1]))
os.makedirs(R + "img/intro/t", exist_ok=True)
for f in os.listdir(R + "img/intro/t"): os.remove(R + "img/intro/t/" + f)
small = ImageFont.truetype(F + "InstrumentSans.ttf", 25)
out = []
for i, (src, by) in enumerate(sel, 1):
    im = ImageOps.exif_transpose(Image.open(os.path.join(R, src))).convert("RGB")
    side = W - 2 * P
    im = ImageOps.fit(im, (side, side), Image.LANCZOS, centering=(.5, .42))
    card = Image.new("RGB", (W, H), "#fffdf8"); card.paste(im, (P, P))
    d = ImageDraw.Draw(card); y = P + side + 26
    d.text((P + 4, y), "W I T H   L O V E   F R O M", font=small, fill="#6b6168")
    size = 78
    while True:
        big = ImageFont.truetype(F + "Caveat.ttf", size)
        if d.textlength(by, font=big) <= side - 8 or size <= 40: break
        size -= 4
    d.text((P + 2, y + 34), by, font=big, fill="#22508f")
    name = f"img/intro/t/{i:02d}.jpg"; card.save(R + name, quality=84, optimize=True, progressive=True)
    out.append(name)
open(R + "intro.js", "w").write("// erzeugt von tools/build_intro.py\nconst INTRO_TILES = " + json.dumps(out) + ";\n")
print(len(out), "Kacheln")
