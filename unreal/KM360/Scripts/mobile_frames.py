#!/usr/bin/env python3
"""Gera a versão mobile (720 px) dos quadros: site/public/frames/<clip>/1x1 -> 1x1m,
e o crop.json do clipe (caixa do objeto somando todos os quadros, de 0 a 1), que o site usa
para desenhar só o objeto, sem a margem transparente do render.

Uso: python3 mobile_frames.py [clip ...]   (sem argumentos: todos os clipes)
Rode de novo sempre que um clipe for re-renderizado.
"""
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

FRAMES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "site", "public", "frames")
SIZE, Q, AQ = 720, 78, 85
PAD = 0.02  # folga em volta do objeto (fração do quadro)


def crop_box(paths: list[str]) -> dict:
    box = None
    for path in paths:
        b = Image.open(path).getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    w, h = Image.open(paths[0]).size
    x0, y0 = max(0.0, box[0] / w - PAD), max(0.0, box[1] / h - PAD)
    x1, y1 = min(1.0, box[2] / w + PAD), min(1.0, box[3] / h + PAD)
    return {"x": round(x0, 4), "y": round(y0, 4), "w": round(x1 - x0, 4), "h": round(y1 - y0, 4)}


def convert(src: str, dst: str) -> int:
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        Image.open(src).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS).save(tmp.name)
        subprocess.run(["cwebp", "-quiet", "-q", str(Q), "-alpha_q", str(AQ), tmp.name, "-o", dst], check=True)
    return os.path.getsize(dst)


def main(clips: list[str]) -> None:
    root = os.path.abspath(FRAMES)
    for clip in clips or sorted(os.listdir(root)):
        src_dir, dst_dir = os.path.join(root, clip, "1x1"), os.path.join(root, clip, "1x1m")
        if not os.path.isdir(src_dir):
            continue
        names = sorted(f for f in os.listdir(src_dir) if f.endswith(".webp"))
        with open(os.path.join(root, clip, "crop.json"), "w") as fh:
            json.dump(crop_box([os.path.join(src_dir, n) for n in names]), fh)
        os.makedirs(dst_dir, exist_ok=True)
        for old in os.listdir(dst_dir):  # sem sobras de um render anterior com mais quadros
            if old not in names:
                os.remove(os.path.join(dst_dir, old))
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
            sizes = list(pool.map(lambda n: convert(os.path.join(src_dir, n), os.path.join(dst_dir, n)), names))
        print(f"{clip:13} {len(names):4} quadros  {sum(sizes) / len(sizes) / 1024:5.1f} KB/q  {sum(sizes) / 1048576:5.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1:])
