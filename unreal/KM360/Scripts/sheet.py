#!/usr/bin/env python3
"""Utilidades de pós (shell): verificação de alpha, preview composto, folha de contato, conversão WebP.
uso:
  sheet.py check <png...>                      -> alpha dos cantos / contagem de bordas
  sheet.py preview <out.png> <hex> <png...>     -> compõe sobre a cor e junta lado a lado (reduzido)
  sheet.py contact <clip> <hex> <dir_png>       -> Saved/Renders/<clip>_contact.png (8 quadros)
  sheet.py webp <clip> <dir_png> [q]            -> site/public/frames/<clip>/1x1/0001.webp...
"""
import glob
import os
import subprocess
import sys
from PIL import Image, ImageDraw

PROJ = "/Users/douglasnogueira/Desktop/KM 360"
RENDERS = f"{PROJ}/unreal/KM360/Saved/Renders"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def check(paths):
    for p in paths:
        im = Image.open(p)
        a = im.getchannel("A")
        w, h = im.size
        corners = [a.getpixel(c) for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        hist = a.histogram()
        bbox = a.getbbox()
        print(os.path.basename(p), im.mode, im.size, "corners", corners, "edge_px", sum(hist[1:255]),
              "opaque", hist[255], "bbox", bbox)


def comp(p, rgb, size=None):
    im = Image.open(p).convert("RGBA")
    bg = Image.new("RGBA", im.size, rgb + (255,))
    bg.alpha_composite(im)
    out = bg.convert("RGB")
    return out.resize(size) if size else out


def preview(out, hx, paths, size=600):
    ims = [comp(p, hexrgb(hx), (size, size)) for p in paths]
    sheet = Image.new("RGB", (size * len(ims), size), hexrgb(hx))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * size, 0))
    sheet.save(out)


def contact(clip, hx, d):
    files = sorted(glob.glob(f"{d}/*.png"))
    n = len(files)
    idx = [round(i * (n - 1) / 7) for i in range(8)]
    cell = 400
    sheet = Image.new("RGB", (cell * 4, cell * 2 + 30), hexrgb(hx))
    dr = ImageDraw.Draw(sheet)
    for k, i in enumerate(idx):
        im = comp(files[i], hexrgb(hx), (cell, cell))
        sheet.paste(im, ((k % 4) * cell, (k // 4) * cell))
        dr.text(((k % 4) * cell + 8, (k // 4) * cell + 6), f"{i + 1:04d}", fill=(255, 255, 255))
    dr.text((8, cell * 2 + 8), f"{clip}  {n} quadros  fundo {hx}", fill=(255, 255, 255))
    out = f"{RENDERS}/{clip}_contact.png"
    sheet.save(out)
    print(out)


def webp(clip, d, q=82):
    files = sorted(glob.glob(f"{d}/*.png"))
    out_dir = f"{PROJ}/site/public/frames/{clip}/1x1"
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(f"{out_dir}/*.webp"):
        os.remove(old)
    total = 0
    for i, f in enumerate(files, 1):
        o = f"{out_dir}/{i:04d}.webp"
        subprocess.run(["/opt/homebrew/bin/cwebp", "-quiet", "-q", str(q), "-alpha_q", "90", "-exact", f, "-o", o], check=True)
        total += os.path.getsize(o)
    print(f"{clip}: {len(files)} quadros, média {total / len(files) / 1024:.1f} KB, total {total / 1048576:.1f} MB -> {out_dir}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        check(sys.argv[2:])
    elif cmd == "preview":
        preview(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == "contact":
        contact(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "webp":
        webp(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 82)
