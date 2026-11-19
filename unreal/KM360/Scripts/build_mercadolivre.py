# Mercado Livre: caixas de envio cromadas/douradas numa esteira circular (curva) + barra de reputação de
# 5 segmentos que acendem em sequência até o verde. 96 quadros.
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "mercadolivre", 96
R_IN, R_OUT, R_MID = 58.0, 80.0, 69.0
NB = 6
BAR_Z, SEG_W, SEG_H, GAP = 44.0, 21.0, 8.5, 3.0
SEG_COLORS = ["#F23D4F", "#FF7A2F", "#FFB800", "#9BD84A", "#00A650"]   # termômetro ML: vermelho -> verde

def belt_angle(f):           # a esteira anda 100° no clipe (devagar, legível)
    return -100.0 * f / (N - 1)

def seg_fill(k, f):
    t = f / (N - 1)
    return max(0.0001, K.ease_out((t - (0.10 + k * 0.17)) / 0.14))

with unreal.ScopedEditorTransaction("km build mercadolivre"):
    D, EL = 470.0, 24.0
    at = (0, 0, 10)
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    gold = K.mat("ML_Gold", "#E9C04A", 1.0, 0.16)
    tape = K.mat("ML_Tape", "#B07A12", 1.0, 0.3)
    rubber = K.mat("ML_Belt", "#1B1B1E", 0.0, 0.32)
    slat = K.mat("ML_Slat", "#9A9A9E", 1.0, 0.25)
    glass = K.mat("Dark_Glass", "#0C0C10", 0.0, 0.05)
    leds = [K.mat(f"ML_Led{k}", "#000000", 0.0, 0.2, emissive=(c, 0.95), specular=0.0) for k, c in enumerate(SEG_COLORS)]

    # esteira fixa: borracha + 2 trilhos cromados
    mb = K.new_mesh()
    K.annulus(mb, R_IN, R_OUT, -3.0, 0.0, material_id=0)
    K.ring_tube(mb, R_IN - 1.6, 1.4, z=1.2, material_id=1)
    K.ring_tube(mb, R_OUT + 1.6, 1.4, z=1.2, material_id=1)
    K.place_mesh(K.save_static_mesh(mb, "SM_ML_Belt", [rubber, chrome]), label="KM_Belt", materials=[rubber, chrome])

    # ripas da esteira (giram com as caixas -> leitura do movimento)
    ms = K.new_mesh()
    for i in range(40):
        a = 360.0 * i / 40
        xf = unreal.Transform(unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, a), unreal.Vector(1, 1, 1))
        K.extrude_poly(ms, [(R_IN + 1.5, -0.6), (R_OUT - 1.5, -0.6), (R_OUT - 1.5, 0.6), (R_IN + 1.5, 0.6)], 0.35,
                       center_depth=0.175, up=True, xform=xf)
    K.finish_mesh(ms, split_angle=20.0)
    slats = K.place_mesh(K.save_static_mesh(ms, "SM_ML_Slats", [slat]), label="KM_Slats", materials=[slat])
    K.key_transform(seq, slats, N, lambda f: ((0, 0, 0), (0, 0, belt_angle(f)), (1, 1, 1)))

    # caixa de envio: corpo chanfrado + fita no topo
    mx = K.new_mesh()
    K.extrude_poly(mx, K.rrect_pts(20, 20, 1.2), 15.0, material_id=0, bevel=0.8, center_depth=7.5, up=True)
    K.extrude_poly(mx, [(-10.15, -2.4), (10.15, -2.4), (10.15, 2.4), (-10.15, 2.4)], 0.3, material_id=1,
                   center_depth=15.15, up=True)
    K.extrude_poly(mx, [(-2.4, -10.15), (2.4, -10.15), (2.4, 10.15), (-2.4, 10.15)], 0.3, material_id=1,
                   center_depth=15.2, up=True)
    K.finish_mesh(mx, split_angle=20.0)
    sm_box = K.save_static_mesh(mx, "SM_ML_Box", [chrome, tape])
    for i in range(NB):
        body = gold if i % 3 == 1 else chrome
        b = K.place_mesh(sm_box, label=f"KM_Box_{i}", materials=[body, tape])
        def fn(f, i=i):
            a = 360.0 * i / NB + belt_angle(f)
            r = m.radians(a)
            return ((R_MID * m.cos(r), R_MID * m.sin(r), 0.35), (0, 0, a + 90.0 + 8.0 * m.sin(i * 1.7)), (1, 1, 1))
        K.key_transform(seq, b, N, fn)

    # barra de reputação (de frente p/ câmera): moldura cromada + vidro escuro + LED que enche da esquerda
    frame_m = K.new_mesh()
    K.extrude_poly(frame_m, K.rrect_pts(SEG_W + 1.6, SEG_H + 1.6, (SEG_H + 1.6) / 2), 2.2, material_id=0, bevel=0.35)
    K.extrude_poly(frame_m, K.rrect_pts(SEG_W, SEG_H, SEG_H / 2), 2.2, material_id=1, center_depth=-0.25)
    K.finish_mesh(frame_m, split_angle=20.0)
    sm_seg = K.save_static_mesh(frame_m, "SM_ML_Segment", [chrome, glass])
    led_m = K.new_mesh()  # pivô na ponta esquerda (u=0): escala em Y = enchimento
    lw, lh = SEG_W - 1.6, SEG_H - 1.6
    K.extrude_poly(led_m, [(p[0] + lw / 2, p[1]) for p in K.rrect_pts(lw, lh, lh / 2)], 2.2, center_depth=-0.5)
    K.finish_mesh(led_m, smooth=True)
    sm_led = K.save_static_mesh(led_m, "SM_ML_Led", [leds[0]])
    total = 5 * SEG_W + 4 * GAP
    pitch = -EL * 0.8
    for k in range(5):
        yc = -total / 2 + SEG_W / 2 + k * (SEG_W + GAP)
        K.place_mesh(sm_seg, loc=(0, yc, BAR_Z), rot=(0, pitch, 0), label=f"KM_Seg_{k}", materials=[chrome, glass])
        led = K.place_mesh(sm_led, label=f"KM_Led_{k}", materials=[leds[k]])
        # pivô do LED na borda esquerda do segmento (no plano inclinado)
        y0 = yc - lw / 2
        K.key_transform(seq, led, N, lambda f, k=k, y0=y0: ((0, y0, BAR_Z), (0, pitch, 0), (1, seg_fill(k, f), 1)))
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
