# Shein v2: "a coleção entra na vitrine". Arara preta laqueada com 5 cabides de frente (face-out);
# com o scroll, as peças (casaco, camiseta, vestido, blusa) entram uma a uma nos cabides com um pulo
# e balançam. Cores das peças = cores das seções do site. A arara gira de leve para mostrar o 3D. 96 quadros.
# (v1, arara vazia com cabides deslizando, guardada fora do projeto.)
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "shein", 96
HALF, LEG, RAIL_R = 66.0, 76.0, 2.2


def chaikin(pts, it=3):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            out.append(tuple(0.75 * x + 0.25 * y for x, y in zip(a, b)))
            out.append(tuple(0.25 * x + 0.75 * y for x, y in zip(a, b)))
        out.append(pts[-1])
        pts = out
    return pts


def resample(pts, step):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(m.dist(a, b) / step))
        for k in range(1, n + 1):
            out.append(tuple(x + (y - x) * k / n for x, y in zip(a, b)))
    return out


def back_out(u):
    u = min(1.0, max(0.0, u))
    c1 = 1.70158
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def mirror(half):
    """Contorno simétrico: metade direita (de cima, no centro, descendo) + espelho."""
    return half + [(-u, v) for (u, v) in reversed(half) if u != 0]


# Silhuetas no plano do cabide (u = ao longo do trilho, v = altura; 0 = centro do trilho).
TEE = mirror([(0, -8.6), (4.2, -6.6), (13.8, -11.8), (20.5, -19.5), (17.2, -23.2), (12.6, -19.2), (13.2, -44)])
BLOUSE = mirror([(0, -10.0), (4.0, -6.8), (11.8, -10.4), (14.4, -15.2), (12.6, -20.0), (13.6, -36)])
DRESS = mirror([(0, -11.5), (5.2, -7.2), (9.6, -9.8), (11.2, -19.0), (8.4, -28.0), (19.0, -62.0), (9.5, -63.2), (0, -63.6)])
# manga colada no corpo: um recorte fino na axila faz o chanfro disparar um vértice (virava "orelha")
COAT = mirror([(0, -11.0), (4.4, -7.0), (14.6, -11.8), (18.6, -17.0), (19.6, -50.0), (15.4, -51.0), (14.0, -56.0)])

# peça, cor (seção do site), posição no trilho
LOOKS = [
    ("coat", COAT, "#1C1C20", -44.0),     # preto
    ("tee", TEE, "#D62246", -22.0),       # vermelho (problema)
    ("dress", DRESS, "#1F4FE0", 0.0),     # azul KM (hero)
    ("blouse", BLOUSE, "#19D27A", 22.0),  # verde (resultados)
    ("dress2", DRESS, "#6A3DF0", 44.0),   # roxo (provas)
]


def scene_yaw(t):
    return K.lerp(-14.0, 10.0, K.ease(t))


def rot_z(p, deg):
    a = m.radians(deg)
    return (p[0] * m.cos(a) - p[1] * m.sin(a), p[0] * m.sin(a) + p[1] * m.cos(a), p[2])


with unreal.ScopedEditorTransaction("km build shein v2"):
    D, EL = 380.0, 6.0
    at = (0, 0, -37)
    # sem os painéis de recorte (feitos para metal): no tecido eles lavavam a cor
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at,
                                 lights=K.DEFAULT_LIGHTS)
    black = K.mat("Shein_Black", "#17171B", 1.0, 0.14)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)

    # arara: pés -> poste -> curva -> trilho -> curva -> poste -> pés (um tubo só) + bases
    rail_pts = chaikin([(0, -HALF, -LEG), (0, -HALF, -3), (0, -HALF, 0), (0, -HALF + 3, 0),
                        (0, HALF - 3, 0), (0, HALF, 0), (0, HALF, -3), (0, HALF, -LEG)], 4)
    mr = K.new_mesh()
    K.path_tube(mr, resample(rail_pts, 1.0), RAIL_R, sides=24, up_hint=(1, 0, 0))
    for y in (-HALF, HALF):
        K.extrude_poly(mr, K.circle_pts(11.0, 64, 0, y), 1.4, bevel=0.45, center_depth=-LEG - 0.7, up=True)
    K.finish_mesh(mr, split_angle=35.0)
    rack = K.place_mesh(K.save_static_mesh(mr, "SM_Shein_Rail", [black]), label="KM_Rail", materials=[black])
    K.key_transform(seq, rack, N, lambda f: ((0, 0, 0), (0, 0, scene_yaw(f / (N - 1))), (1, 1, 1)))

    # cabide de frente, no plano YZ (o gancho passa por cima do trilho)
    hook = [(3.0 * m.cos(m.radians(a)), 3.0 * m.sin(m.radians(a))) for a in range(210, -61, -10)]
    body = [(0.4, -6.4), (14.6, -13.6), (15.5, -14.8), (14.6, -15.5), (-14.6, -15.5), (-15.5, -14.8), (-14.6, -13.6), (-0.5, -6.7)]
    hp = resample(chaikin([(0, y, z) for (y, z) in hook + [(1.2, -4.0)] + body], 3), 0.6)
    mh = K.new_mesh()
    K.path_tube(mh, hp, 0.55, sides=14, up_hint=(1, 0, 0))
    sm_hanger = K.save_static_mesh(mh, "SM_Shein_Hanger2", [chrome])

    for i, (kind, poly, color, y) in enumerate(LOOKS):
        fabric = K.mat(f"Fab_{i}", color, 0.0, 0.62, specular=0.2)
        mg = K.new_mesh()
        K.extrude_poly(mg, poly, 2.6, bevel=0.8, bevel_sub=2)
        if kind == "coat":  # botões cromados na frente
            for v in (-28.0, -36.0, -44.0):
                K.extrude_poly(mg, K.circle_pts(0.95, 24, 0, v), 0.7, material_id=1, bevel=0.2, center_depth=-1.45)
        K.finish_mesh(mg, split_angle=40.0)
        mats = [fabric, chrome] if kind == "coat" else [fabric]
        sm_g = K.save_static_mesh(mg, f"SM_Shein_Look_{i}", mats)
        g = K.place_mesh(sm_g, label=f"KM_Look_{i}", materials=mats)
        h = K.place_mesh(sm_hanger, label=f"KM_Hanger_{i}", materials=[chrome])

        x = -1.8 if i % 2 == 0 else 1.8          # peças vizinhas em profundidades diferentes (sem z-fight)
        t0 = -0.22 + i * 0.19                   # as duas primeiras já estão na arara no quadro 0

        def pose(f, i=i, x=x, y=y, t0=t0):
            t = f / (N - 1)
            a = t - t0
            swing = 7.0 * m.exp(-a / 0.1) * m.sin(2 * m.pi * a / 0.18) if a > 0 else 0.0
            roll = swing + 0.6 * m.sin(2 * m.pi * 1.5 * t + i)
            yaw = scene_yaw(t)
            return rot_z((x, y, 0.0), yaw), roll, yaw, t

        def fn_look(f, pose=pose, t0=t0):
            loc, roll, yaw, t = pose(f)
            s = max(0.001, back_out((t - t0) / 0.2))
            return (loc, (roll, 0, yaw), (s, s, s))

        def fn_hanger(f, pose=pose):
            loc, roll, yaw, _ = pose(f)
            return (loc, (roll, 0, yaw), (1, 1, 1))

        K.key_transform(seq, g, N, fn_look)
        K.key_transform(seq, h, N, fn_hanger)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
