# Hero: turntable 360° do logo KM + arco. 120 quadros, 3°/quadro (0..357°), loop perfeito.
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)

CLIP, N = "hero", 120

with unreal.ScopedEditorTransaction("km build hero"):
    MAP = K.open_or_new_map(CLIP)
    cube = K.import_hdri(f"HDR_{CLIP}", f"{K.PROJ}/Saved/HDRI/HDR_{CLIP}.hdr")
    K.studio(cube, exposure_bias=0.0, lights=K.DEFAULT_LIGHTS + K.RIM_LIGHTS)  # + recorte frio (pedido do coordenador)
    blue = K.mat("K_Blue", "#1444A6", 1.0, 0.25)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.08)
    arcm = K.mat("Arc_Blue", "#2180F4", 1.0, 0.18)
    sm_letters = K.letters_mesh("SM_KM_Letters", [blue, chrome])
    sm_arc = K.arc_mesh("SM_KM_Arc", 125.0, -110.0, rmax=2.6, mats=[arcm])
    letters = K.place_mesh(sm_letters, label="KM_Letters", materials=[blue, chrome])
    arc = K.place_mesh(sm_arc, label="KM_Arc", materials=[arcm])

    D, EL = 540.0, 10.0
    cam = K.camera((-D * K.math.cos(K.math.radians(EL)), 0, D * K.math.sin(K.math.radians(EL))), (0, 0, 0), focal=50)
    seq = K.new_sequence(CLIP, N)
    K.bind_camera(seq, cam, N)
    spin = lambda f: ((0, 0, 0), (0, 0, 3.0 * f), (1, 1, 1))
    K.key_transform(seq, letters, N, spin)
    K.key_transform(seq, arc, N, spin)
    K.save_all(seq)
SEQ = seq
print("ok", MAP, sm_letters.get_path_name())
