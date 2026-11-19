#!/usr/bin/env python3
"""Gera HDRIs de estúdio procedurais (Radiance .hdr, lat-long 2:1) — roda no shell (stdlib).

Ambiente = cor da seção (gradiente: horizonte claro, topo médio, chão escuro)
+ softboxes brancos (faixas retangulares em lon/lat com borda suave).
Convenção de direção: lon 0 = centro da imagem; calibrada no editor via SkyLight.source_cubemap_angle.

Uso: python3 make_hdri.py <saida_dir> [nome=#hex ...]   (sem pares: gera todas as seções)
"""
import math
import os
import sys

W, H = 2048, 1024

SECTIONS = {
    "hero": "#1F4FE0", "problema": "#D62246", "mercadolivre": "#FFE600", "tiktokshop": "#25F4EE",
    "shein": "#FFFFFF", "shopee": "#EE4D2D", "resultados": "#19D27A", "final": "#1F4FE0",
}

# Calibrado no editor (esfera cromada, câmera em -X olhando +X): lon = yaw_mundo + 90.
# softboxes em coordenadas de MUNDO: (yaw_centro, lat_centro, largura, altura, intensidade, suavidade) em graus.
# yaw 180 = atrás da câmera (o que as faces frontais refletem); yaw 0 = atrás do objeto.
SOFTBOXES_YAW = [
    (180, 14, 64, 50, 3.5, 8),    # softbox frontal grande: faces frontais com gradiente branco->cor
    (180, 82, 400, 16, 2.0, 8),   # teto (bordas superiores)
    (90, 10, 10, 80, 10.0, 3),    # faixa vertical direita
    (-90, 10, 10, 80, 10.0, 3),   # faixa vertical esquerda
    (30, 15, 8, 70, 10.0, 3),     # rim traseira direita
    (-30, 15, 8, 70, 10.0, 3),    # rim traseira esquerda
    (0, 5, 40, 30, 4.0, 8),       # softbox traseiro
    (0, -3, 400, 10, 2.2, 5),     # anel de horizonte 360°: gradiente claro->cor nas faces em qualquer ângulo
    (150, 10, 7, 60, 8.0, 3),     # faixa frontal-direita
    (-150, 10, 7, 60, 8.0, 3),    # faixa frontal-esquerda
]
SOFTBOXES = [((y + 90 + 180) % 360 - 180, la, w, h, i, s) for (y, la, w, h, i, s) in SOFTBOXES_YAW]
DARK_FLAGS_YAW = [135, -135, 60, -60]  # bandas escuras verticais p/ contraste do cromo
DARK_FLAGS = [(y + 90 + 180) % 360 - 180 for y in DARK_FLAGS_YAW]


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    h = h.lstrip("#")
    return [srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]


def smooth_box(d, half, soft):
    """1 dentro, 0 fora, transição suave de largura `soft` (graus)."""
    x = (half - abs(d)) / max(soft, 1e-6) + 0.5
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return x * x * (3 - 2 * x)


def wrap(d):
    return (d + 180.0) % 360.0 - 180.0


def rgbe(r, g, b):
    m = max(r, g, b)
    if m < 1e-32:
        return 0, 0, 0, 0
    mant, ex = math.frexp(m)
    s = mant * 256.0 / m
    return int(r * s), int(g * s), int(b * s), ex + 128


def write_hdr(path, pixels):
    """pixels: lista de linhas, cada linha lista de (r,g,b) float. RLE novo, só literais (válido)."""
    with open(path, "wb") as f:
        f.write(b"#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n")
        f.write(f"-Y {H} +X {W}\n".encode())
        for row in pixels:
            enc = [rgbe(*p) for p in row]
            out = bytearray([2, 2, W >> 8, W & 255])
            for ch in range(4):
                data = bytes(e[ch] for e in enc)
                for i in range(0, W, 128):
                    chunk = data[i:i + 128]
                    out.append(len(chunk))
                    out += chunk
            f.write(out)


def make_env(path, color_hex, boxes=SOFTBOXES, white_boost=1.0, dark_k=None, flag=0.35):
    col = hex_lin(color_hex)
    lum = 0.2126 * col[0] + 0.7152 * col[1] + 0.0722 * col[2]
    # cores muito claras (branco/amarelo) precisam de zonas escuras p/ o cromo ter definição
    if dark_k is None:
        dark_k = 0.15 if lum > 0.5 else 0.25
    lons = [(x + 0.5) / W * 360.0 - 180.0 for x in range(W)]
    rows = []
    for y in range(H):
        lat = 90.0 - (y + 0.5) / H * 180.0
        # gradiente vertical: chão escuro, horizonte claro, topo médio
        if lat < 0:
            t = min(1.0, -lat / 35.0)
            g = 0.9 * (1 - t) + dark_k * t
        else:
            t = min(1.0, lat / 50.0)
            g = 0.9 * (1 - t) + 0.6 * t
        base = [c * g for c in col]
        # faixas de luz que valem para esta latitude
        active = []
        for (lc, la, wl, hl, inten, soft) in boxes:
            fy = smooth_box(lat - la, hl / 2.0, soft)
            if fy > 0:
                active.append((lc, wl / 2.0, inten * fy * white_boost, soft))
        row = []
        for lon in lons:
            r, gg, b = base
            # bandas escuras verticais (flags) para contraste do cromo
            band = 1.0
            for fl in DARK_FLAGS:
                band -= flag * smooth_box(wrap(lon - fl), 12, 10)
            r, gg, b = r * band, gg * band, b * band
            for (lc, hw, a, soft) in active:
                fx = smooth_box(wrap(lon - lc), hw, soft)
                if fx > 0:
                    v = a * fx
                    r += v
                    gg += v
                    b += v
            row.append((r, gg, b))
        rows.append(row)
    write_hdr(path, rows)


def make_calib(path):
    """Marcadores: vermelho lon 0, verde lon +90, azul lon -90, amarelo lon 180, branco no zênite."""
    marks = [(0, (8, 0, 0)), (90, (0, 8, 0)), (-90, (0, 0, 8)), (180, (8, 8, 0))]
    rows = []
    for y in range(H):
        lat = 90.0 - (y + 0.5) / H * 180.0
        row = []
        for x in range(W):
            lon = (x + 0.5) / W * 360.0 - 180.0
            p = [0.15, 0.15, 0.15] if lat > 0 else [0.04, 0.04, 0.04]
            if lat > 75:
                p = [6, 6, 6]
            for lc, c in marks:
                if abs(wrap(lon - lc)) < 12 and abs(lat) < 20:
                    p = list(c)
            row.append(tuple(p))
        rows.append(row)
    write_hdr(path, rows)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    pairs = [a.split("=", 1) for a in sys.argv[2:]]
    if pairs and pairs[0][0] == "calib":
        make_calib(os.path.join(out, "HDR_calib.hdr"))
        sys.exit(0)
    # fundo branco: chão quase preto + bandas escuras fortes, senão o cromo some no branco
    OPTS = {"shein": dict(dark_k=0.02, flag=0.9)}
    for name, hx in (pairs or SECTIONS.items()):
        make_env(os.path.join(out, f"HDR_{name}.hdr"), hx, **OPTS.get(name, {}))
        print("ok", name)
