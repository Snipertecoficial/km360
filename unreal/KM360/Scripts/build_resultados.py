# Resultados: 14 colunas cromadas em arco de 300° (motivo 360) sobem em sequência, alturas crescentes,
# sobre um anel cromado; o conjunto gira devagar (-18° -> +18°). 96 quadros.
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "resultados", 96
NC, RAD, COL_R = 14, 60.0, 5.2
H0, H1 = 16.0, 92.0

def col_angle(i):  # yaw: baixas na frente (não tapam), sobe pela esquerda e fundo, maior no fundo-direita
    return 120.0 + i * 300.0 / (NC - 1)

def height(i):
    return H0 + (H1 - H0) * (i / (NC - 1)) ** 1.25

def grow(i, f):
    t = f / (N - 1)
    a = 0.05 + i * 0.042
    return max(0.035, K.ease_out((t - a) / 0.32))

def spin(f):
    return K.lerp(-18.0, 18.0, K.ease(f / (N - 1)))

with unreal.ScopedEditorTransaction("km build resultados"):
    D, EL = 430.0, 27.0
    at = (0, 0, 34)
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    green = K.mat("Res_Green", "#19D27A", 1.0, 0.18)

    mc = K.new_mesh()  # coluna unitária: 100 cm, base em z=0 (escala Z = altura/100)
    K.extrude_poly(mc, K.circle_pts(COL_R, 64), 100.0, bevel=0.6, center_depth=50.0, up=True)
    K.finish_mesh(mc, split_angle=20.0)
    sm_col = K.save_static_mesh(mc, "SM_Res_Column", [chrome])

    mb = K.new_mesh()  # anel-base duplo
    K.ring_tube(mb, RAD, 1.3, z=0.6)
    K.ring_tube(mb, RAD + 9.0, 0.7, z=0.4)
    K.ring_tube(mb, RAD - 9.0, 0.7, z=0.4)
    sm_base = K.save_static_mesh(mb, "SM_Res_Base", [chrome])
    base = K.place_mesh(sm_base, label="KM_Base", materials=[chrome])
    K.key_transform(seq, base, N, lambda f: ((0, 0, 0), (0, 0, spin(f)), (1, 1, 1)))

    for i in range(NC):
        mat_i = green if i == NC - 1 else chrome   # última coluna (a maior) em verde metálico: destaque
        a = K.place_mesh(sm_col, label=f"KM_Col_{i:02d}", materials=[mat_i])
        def fn(f, i=i):
            yaw = m.radians(col_angle(i) + spin(f))
            return ((RAD * m.cos(yaw), RAD * m.sin(yaw), 0.0), (0, 0, col_angle(i) + spin(f)),
                    (1, 1, height(i) / 100.0 * grow(i, f)))
        K.key_transform(seq, a, N, fn)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
