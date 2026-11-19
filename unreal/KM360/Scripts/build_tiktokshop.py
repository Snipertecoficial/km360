# TikTok Shop: 5 celulares 9:16 (moldura cromada, tela de vidro escuro com UI emissiva rosa/ciano) orbitando,
# com corações 3D rosa-cromados subindo pelo meio. 96 quadros.
import importlib
import random
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "tiktokshop", 96
NP, ORB = 5, 60.0
NH = 12
rnd = random.Random(7)
HEARTS = [dict(p=j / NH, x=rnd.uniform(-14, 14), y=rnd.uniform(-30, 30), sw=rnd.uniform(4, 9), ph=rnd.uniform(0, 6.28),
               s=rnd.uniform(0.75, 1.15), wob=rnd.uniform(10, 25)) for j in range(NH)]

def orbit(f):
    return 144.0 * f / (N - 1)

with unreal.ScopedEditorTransaction("km build tiktokshop"):
    D, EL = 420.0, 10.0
    at = (0, 0, 4)
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    glass = K.mat("Dark_Glass", "#0C0C10", 0.0, 0.05)
    pink_ui = K.mat("TT_PinkUI", "#000000", 0.0, 0.15, emissive=("#FE2C55", 0.9), specular=0.0)
    cyan_ui = K.mat("TT_CyanUI", "#000000", 0.0, 0.15, emissive=("#25F4EE", 0.9), specular=0.0)
    heart_m = K.mat("TT_Heart", "#FE2C55", 1.0, 0.14)

    S = 1.45  # escala do celular (9:16)
    ph = K.new_mesh()  # celular: frente = -X (para a câmera quando yaw=0)
    K.extrude_poly(ph, K.rrect_pts(18 * S, 32 * S, 2.8 * S), 1.8 * S, material_id=0, bevel=0.55)
    K.extrude_poly(ph, K.rrect_pts(16.4 * S, 30.4 * S, 2.1 * S), 1.6 * S, material_id=1, center_depth=-0.25 * S)
    K.extrude_poly(ph, K.rrect_pts(13.0 * S, 13.0 * S, 1.6 * S, cy=4.5 * S), 1.6 * S, material_id=2, center_depth=-0.27 * S)
    K.extrude_poly(ph, K.rrect_pts(13.0 * S, 3.4 * S, 1.7 * S, cy=-6.8 * S), 1.6 * S, material_id=3, center_depth=-0.27 * S)
    K.extrude_poly(ph, K.rrect_pts(9.0 * S, 1.3 * S, 0.65 * S, cy=-10.6 * S), 1.6 * S, material_id=2, center_depth=-0.27 * S)
    K.finish_mesh(ph, split_angle=20.0)
    sm_phone = K.save_static_mesh(ph, "SM_TT_Phone", [chrome, glass, pink_ui, cyan_ui])

    hm = K.new_mesh()
    K.extrude_poly(hm, K.heart_pts(17.0), 3.6, bevel=0.7)
    K.finish_mesh(hm, split_angle=20.0)
    sm_heart = K.save_static_mesh(hm, "SM_TT_Heart", [heart_m])

    for i in range(NP):
        a = K.place_mesh(sm_phone, label=f"KM_Phone_{i}", materials=[chrome, glass, pink_ui, cyan_ui])
        def fn(f, i=i):
            ang = 360.0 * i / NP + orbit(f) + 180.0   # i=0 começa de frente p/ câmera (-X)
            r = m.radians(ang)
            z = 7.0 * m.sin(r * 2 + i)
            return ((ORB * m.cos(r), ORB * m.sin(r), z), (4.0 * m.sin(r + i), -4.0, ang + 180.0), (1, 1, 1))
        K.key_transform(seq, a, N, fn)

    for j, h in enumerate(HEARTS):
        a = K.place_mesh(sm_heart, label=f"KM_Heart_{j:02d}", materials=[heart_m])
        def fn(f, h=h):
            u = (f / (N - 1) * 1.6 + h["p"]) % 1.0
            sc = h["s"] * K.ease(u / 0.18) * K.ease((1 - u) / 0.22)
            z = -62.0 + 128.0 * u
            y = h["y"] + h["sw"] * m.sin(u * 6.0 + h["ph"])
            return ((h["x"], y, z), (0, 0, h["wob"] * m.sin(u * 5.0 + h["ph"])), (max(sc, 0.001),) * 3)
        K.key_transform(seq, a, N, fn)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
