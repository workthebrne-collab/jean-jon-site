"""Regenerate web logo assets from the source PNG.
Usage: python3 _build/mklogo.py [path/to/source.png]"""
import sys, os, subprocess
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "logo-src.png")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img", "brand")

im = Image.open(SRC).convert("RGBA")
im = im.crop(im.getbbox())                      # trim transparent margin

W = 480                                          # retina-ready header width
H = round(im.size[1] * W / im.size[0])
dark = im.resize((W, H), Image.LANCZOS)


INK, ON_DARK = (0x2A, 0x23, 0x20), (0xFD, 0xFA, 0xF7)   # match CSS tokens

def tint(img, rgb, path):
    out = img.copy(); p, o = img.load(), out.load()
    for y in range(H):
        for x in range(W):
            o[x, y] = (rgb[0], rgb[1], rgb[2], p[x, y][3])
    out.save(path)

tint(dark, INK, "/tmp/_logo-dark.png")
tint(dark, ON_DARK, "/tmp/_logo-white.png")

for name in ("dark", "white"):
    subprocess.run(["cwebp", "-quiet", "-q", "92", "-alpha_q", "100",
                    f"/tmp/_logo-{name}.png",
                    "-o", os.path.join(OUT, f"logo-{name}.webp")], check=True)

S, pad = 180, 14                                 # square favicon, full wordmark
sc = min((S - 2 * pad) / im.size[0], (S - 2 * pad) / im.size[1])
r = im.resize((round(im.size[0] * sc), round(im.size[1] * sc)), Image.LANCZOS)
c = Image.new("RGBA", (S, S), (0xFB, 0xF7, 0xF2, 255))
c.alpha_composite(r, ((S - r.size[0]) // 2, (S - r.size[1]) // 2))
c.convert("RGB").save(os.path.join(OUT, "favicon.png"))
print("logo assets regenerated")
