# Shopee v2: "o cupom vira venda". Sacola branca laqueada no centro e um anel limpo (eco do anel 360)
# de moedas douradas e cupons picotados girando em volta. Com o scroll o anel gira e, um a um, moedas e
# cupons voam para dentro da sacola, que quica a cada chegada. Sem texto no render. 96 quadros.
# (v1, sacolinhas e moedas soltas em órbita, guardada fora do projeto.)
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)
m = K.math

CLIP, N = "shopee", 96
ORB, TILT = 62.0, 18.0
BAG_W, BAG_H, BAG_D = 40.0, 44.0, 15.0
MOUTH = (0.0, 0.0, BAG_H / 2 + 2.0)
KINDS = ["coin", "coupon", "coin", "coin", "coupon", "coin", "coin", "coupon", "coin", "coin", "coupon", "coin"]
T_POUR, GAP, FLY = 0.36, 0.047, 0.12   # quando começa a chuva, intervalo entre peças, duração do voo


def bag_mesh(name, w, h, d, mats):
    mb = K.new_mesh()
    K.extrude_poly(mb, K.rrect_pts(w, h, 0.09 * w), d, material_id=0, bevel=0.06 * w)
    for x0 in (-0.1 * d, 0.1 * d):  # alças: dois arcos de tubo sobre a boca
        hp = [(x0, 0.27 * w * m.cos(m.radians(a)), h / 2 + 0.27 * w * m.sin(m.radians(a)) - 0.02 * w) for a in range(0, 181, 6)]
        K.path_tube(mb, hp, 0.035 * w, sides=14, material_id=1, up_hint=(1, 0, 0))
    # selo redondo laranja na frente (dá volume e cor à face lisa; sem logo)
    K.extrude_poly(mb, K.circle_pts(7.5, 72, 0, -2.0), 0.9, material_id=2, bevel=0.3, center_depth=-d / 2 - 0.25)
    K.finish_mesh(mb, split_angle=30.0)
    return K.save_static_mesh(mb, name, mats)


def coupon_pts(w=22.0, h=12.5, r=1.6, notch=2.5):
    """Cupom: retângulo arredondado com meia-lua recortada no meio de cada lateral (sentido anti-horário)."""
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for k, (cx, cy, a0) in enumerate(corners):
        for j in range(7):
            a = m.radians(a0 + 90 * j / 6)
            pts.append((cx + r * m.cos(a), cy + r * m.sin(a)))
        if k == 1:   # lateral esquerda, descendo: meia-lua para dentro
            pts += [(-w / 2 + notch * m.sin(m.radians(t)), notch * m.cos(m.radians(t))) for t in range(10, 171, 20)]
        if k == 3:   # lateral direita, subindo
            pts += [(w / 2 - notch * m.sin(m.radians(t)), -notch * m.cos(m.radians(t))) for t in range(10, 171, 20)]
    return pts


def ring_pos(i, t):
    ang = m.radians(360.0 * i / len(KINDS) + 130.0 * t)
    x, y = ORB * m.cos(ang), ORB * m.sin(ang)
    z = x * m.sin(m.radians(TILT)) + 2.2 * m.sin(ang * 2 + i)   # frente (-X) desce, fundo sobe
    return (x * m.cos(m.radians(TILT)), y, z), ang


def depart(i):
    return T_POUR + i * GAP


def bag_yaw(t):
    return K.lerp(-24, 24, K.ease(t))


def bag_z(t):
    return -4 + 2.0 * m.sin(t * 2 * m.pi)


# cupons não somem: ficam espetados na boca da sacola (fim = sacola cheia de cupom)
SLOTS = {1: (-9.0, -12.0), 4: (-3.0, 6.0), 7: (3.5, -5.0), 10: (9.5, 10.0)}   # índice -> (posição na boca, inclinação)


def in_bag(i, t):
    off, lean = SLOTS[i]
    a = m.radians(bag_yaw(t))
    return (-off * m.sin(a), off * m.cos(a), bag_z(t) + BAG_H / 2 + 5.5), (90.0 + lean, 0, bag_yaw(t))


with unreal.ScopedEditorTransaction("km build shopee v2"):
    D, EL = 395.0, 10.0
    at = (0, 0, 3)
    # sem os painéis de recorte: na laca branca eles achatavam a sacola numa mancha
    MAP, seq, cam = K.setup_clip(CLIP, N, (-D * m.cos(m.radians(EL)), 0, at[2] + D * m.sin(m.radians(EL))), at,
                                 lights=K.DEFAULT_LIGHTS)
    pearl = K.mat("Shopee_Pearl", "#EDE5DB", 0.0, 0.2, specular=0.6)
    badge = K.mat("Shopee_Badge", "#D8361A", 0.0, 0.3, specular=0.5)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    gold = K.mat("Shopee_Gold2", "#FFC93C", 1.0, 0.22)
    paper = K.mat("Shopee_Coupon", "#FFF6E8", 0.0, 0.35, specular=0.4)
    dots = K.mat("Shopee_CouponDots", "#EE4D2D", 0.0, 0.4)

    sm_bag = bag_mesh("SM_Shopee_BagBig2", BAG_W, BAG_H, BAG_D, [pearl, chrome, badge])

    mc = K.new_mesh()  # moeda: disco chanfrado + miolo em relevo nas duas faces
    K.extrude_poly(mc, K.circle_pts(8.0, 72), 2.4, bevel=0.55, bevel_sub=1)
    K.extrude_poly(mc, K.circle_pts(5.4, 72), 3.0, bevel=0.3)
    K.finish_mesh(mc, split_angle=25.0)
    sm_coin = K.save_static_mesh(mc, "SM_Shopee_Coin2", [gold])

    mk = K.new_mesh()  # cupom com picote laranja
    K.extrude_poly(mk, coupon_pts(), 1.4, bevel=0.35)
    for v in range(-4, 5, 2):
        K.extrude_poly(mk, K.circle_pts(0.5, 16, -4.5, float(v)), 1.7, material_id=1)
    K.finish_mesh(mk, split_angle=35.0)
    sm_coupon = K.save_static_mesh(mk, "SM_Shopee_Coupon", [paper, dots])

    # sacola: balança o giro e quica (achata e estica) a cada peça que entra
    arrivals = [depart(i) + FLY for i in range(len(KINDS))]

    def fn_bag(f):
        t = f / (N - 1)
        q = sum(max(0.0, 1 - abs(t - a) / 0.03) for a in arrivals)
        sz = 1 - 0.06 * q
        sx = 1 + 0.03 * q
        return ((0, 0, bag_z(t) - BAG_H / 2 * (1 - sz)), (0, 0, bag_yaw(t)), (sx, sx, sz))
    bag = K.place_mesh(sm_bag, label="KM_BagBig", materials=[pearl, chrome, badge])
    K.key_transform(seq, bag, N, fn_bag)

    for i, kind in enumerate(KINDS):
        sm, mats = (sm_coin, [gold]) if kind == "coin" else (sm_coupon, [paper, dots])
        a = K.place_mesh(sm, label=f"KM_Ring_{i}_{kind}", materials=mats)
        a.static_mesh_component.set_editor_property("affect_distance_field_lighting", False)

        def fn(f, i=i, kind=kind):
            t = f / (N - 1)
            t0 = depart(i)
            (x, y, z), ang = ring_pos(i, min(t, t0))
            if kind == "coin":
                rot = (0, 10.0 * m.sin(ang + i), 420.0 * t + 30 * i)
            else:
                rot = (8.0 * m.sin(ang * 2 + i), -12.0, 25.0 * m.sin(ang + i) + 15 * t)
            s = 1.0
            if t > t0 and kind == "coupon":  # voa e fica espetado na boca
                u = min(1.0, (t - t0) / FLY)
                e = K.ease(u)
                end, end_rot = in_bag(i, t)
                x, y, z = K.lerp((x, y, z), end, e)
                z += 14.0 * m.sin(m.pi * e)
                rot = K.lerp(rot, end_rot, e)
            elif t > t0:  # moeda: voo em arco até a boca, encolhendo ao entrar
                u = min(1.0, (t - t0) / FLY)
                e = K.ease(u)
                x, y, z = K.lerp((x, y, z), MOUTH, e)
                z += 16.0 * m.sin(m.pi * e)
                s = 0.001 if u >= 1.0 else max(0.001, 1 - 0.75 * e ** 2)
                rot = (rot[0], rot[1] + 90 * e, rot[2] + 180 * e)
            return ((x, y, z), rot, (s, s, s))
        K.key_transform(seq, a, N, fn)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
