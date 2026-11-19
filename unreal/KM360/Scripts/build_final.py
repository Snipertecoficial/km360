# Final: o arco cresce de 235° até fechar 360° em volta do logo (recentra e abre o raio). 96 quadros.
# O arco muda de forma por quadro: uma malha por quadro (SM_Final_Arc_###), cada ator só fica na cena no seu
# quadro (keys constantes; fora dele vai para FAR). Letras + arcos giram juntos de -10° a +10°.
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)

CLIP, N = "final", 96
C0, C1 = K.ARC_C, (291.0, 303.75)          # centro: do logo -> centro das letras
R0, R1 = K.ARC_R, 362.0                     # raio (px do logo)
SHIFT = (C1[0] - K.LOGO_C[0]) * K.LOGO_S    # desloca o grupo p/ o anel terminar centrado

def state(f):
    e = K.ease(f / (N - 1))
    yaw = K.lerp(-10.0, 10.0, K.ease(f / (N - 1)))
    return e, yaw, (0.0, -SHIFT * e, 0.0)

with unreal.ScopedEditorTransaction("km build final"):
    D, EL = 540.0, 10.0
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * K.math.cos(K.math.radians(EL)), 0, D * K.math.sin(K.math.radians(EL))),
                                 lights=K.DEFAULT_LIGHTS + K.RIM_LIGHTS)
    blue = K.mat("K_Blue", "#1444A6", 1.0, 0.25)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)      # M cromado inalterado
    arcm = K.mat("Arc_Blue", "#2180F4", 1.0, 0.18)
    letters = K.place_mesh(unreal.load_asset("/Game/KM360/Meshes/SM_KM_Letters"), label="KM_Letters", materials=[blue, chrome])
    K.key_transform(seq, letters, N, lambda f: (state(f)[2], (0, 0, state(f)[1]), (1, 1, 1)))
    for f in range(N):
        e, yaw, off = state(f)
        closed = f == N - 1
        ramp = 0.30 * (1 - e)
        sm = K.arc_mesh(f"SM_Final_Arc_{f:03d}", 125.0, -110.0 - 125.0 * e, rmax=K.lerp(2.6, 3.0, e), depth_x=10.0,
                        mats=[arcm], ramp_a=ramp, ramp_b=ramp, closed=closed,
                        r=K.lerp(R0, R1, e), c=K.lerp(C0, C1, e), seg_per_deg=0.8)
        a = K.place_mesh(sm, loc=K.FAR, label=f"KM_Arc_{f:03d}", materials=[arcm])
        frames = sorted({0, f, min(N, f + 1)})
        K.key_transform(seq, a, N, lambda k, f=f, yaw=yaw, off=off: ((off if k == f else K.FAR), (0, 0, yaw), (1, 1, 1)),
                        frames=frames, constant=True)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
