# Problema: 20 etiquetas de preço cromadas (tag com furo) caem girando em caos e, ao longo do clipe,
# desaceleram e se organizam numa grade perfeita 5x4 de frente para a câmera. 96 quadros.
import importlib
import random
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "problema", 96
COLS, ROWS, SX, SZ = 5, 4, 21.0, 30.0
rnd = random.Random(11)
FINAL_ROT = (0.0, 0.0, 22.0)   # grade toda girada 22°: faces pegam gradiente do estúdio (cromo, não branco chapado)
TAGS = []
for i in range(COLS * ROWS):
    c, r = i % COLS, i // COLS
    TAGS.append(dict(
        grid=(0.0, (c - (COLS - 1) / 2) * SX, ((ROWS - 1) / 2 - r) * SZ),
        p0=(rnd.uniform(-35, 35), rnd.uniform(-66, 66), rnd.uniform(-5, 62)),
        v=rnd.uniform(70, 115), drift=rnd.uniform(-25, 25),
        r0=(rnd.uniform(-180, 180), rnd.uniform(-180, 180), rnd.uniform(-180, 180)),
        w=(rnd.uniform(-700, 700), rnd.uniform(-500, 500), rnd.uniform(-600, 600)),
        d=0.28 + 0.16 * ((c + r * 0.7) / (COLS + ROWS * 0.7)) + rnd.uniform(0, 0.05),
    ))

def tag_xf(tg, f):
    t = f / (N - 1)
    w = K.ease((t - tg["d"]) / 0.42)
    x0, y0, z0 = tg["p0"]
    chaos_p = (x0, y0 + tg["drift"] * t, z0 - tg["v"] * t)
    chaos_r = tuple(a + b * t for a, b in zip(tg["r0"], tg["w"]))
    return K.lerp(chaos_p, tg["grid"], w), K.lerp(chaos_r, FINAL_ROT, w)

with unreal.ScopedEditorTransaction("km build problema"):
    D, EL = 440.0, 6.0
    at = (0, 0, 2)
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    rose = K.mat("Tag_RoseGold", "#E8B4A0", 1.0, 0.12)

    # etiqueta: retângulo com topo chanfrado (frente = -X), furo por subtração booleana
    tag_poly = [(-7.5, -12.0), (7.5, -12.0), (7.5, 7.0), (3.6, 12.0), (-3.6, 12.0), (-7.5, 7.0)]
    mt = K.new_mesh()
    K.extrude_poly(mt, tag_poly, 1.1, bevel=0.35)
    hole = K.new_mesh()
    K.extrude_poly(hole, K.circle_pts(1.7, 48, 0.0, 8.0), 4.0)
    K.subtract(mt, hole)
    ring = K.new_mesh()  # ilhós cromado em volta do furo
    K.extrude_poly(ring, K.circle_pts(2.6, 48, 0.0, 8.0), 1.5, bevel=0.3)
    K.subtract(ring, hole)
    K.GS.GeometryScript_MeshEdits.append_mesh(mt, ring, unreal.Transform())
    K.finish_mesh(mt, split_angle=25.0)
    sm_tag = K.save_static_mesh(mt, "SM_Problema_Tag", [chrome])

    for i, tg in enumerate(TAGS):
        mat_i = rose if i in (2, 7, 13, 16) else chrome
        a = K.place_mesh(sm_tag, label=f"KM_Tag_{i:02d}", materials=[mat_i])
        a.static_mesh_component.set_editor_property("affect_distance_field_lighting", False)
        K.key_transform(seq, a, N, lambda f, tg=tg: (*tag_xf(tg, f), (1, 1, 1)))
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
