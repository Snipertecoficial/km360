# Teste de pipeline: HDRI de calibração no SkyLight + esfera cromada + render MRQ 3 quadros com alpha.
import importlib
import sys
sys.path.insert(0, "/Users/douglasnogueira/Desktop/KM 360/unreal/KM360/Scripts")
import km_lib as K
importlib.reload(K)

with unreal.ScopedEditorTransaction("km calib"):
    MAP = K.open_or_new_map("calib")
    cube = K.import_hdri("HDR_calib", f"{K.PROJ}/Saved/HDRI/HDR_calib.hdr")
    print("cubemap:", type(cube).__name__ if cube else None)
    K.studio(cube, exposure_bias=0.0)
    chrome = K.mat("Chrome", "#D7D5D6", 1.0, 0.05)
    sphere = unreal.load_asset("/Engine/BasicShapes/Sphere")
    K.place_mesh(sphere, loc=(0, 0, 0), scale=(1.5, 1.5, 1.5), label="Sphere", materials=[chrome])
    cam = K.camera((-600, 0, 0), (0, 0, 0), focal=50)
    seq = K.new_sequence("calib", 3)
    K.bind_camera(seq, cam, 3)
    K.save_all(seq)
SEQ = seq
print("ok", MAP)
