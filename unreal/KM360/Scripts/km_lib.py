"""Biblioteca compartilhada (roda DENTRO do editor via PythonBridge).

import sys; sys.path.insert(0, "<Scripts>"); import km_lib, importlib; importlib.reload(km_lib)

Conteúdo: estúdio (HDRI no SkyLight + rect lights + PPV), materiais, malhas procedurais
(Geometry Script), LevelSequence (keys por quadro) e Movie Render Queue (PNG com alpha).
"""
import math
import os

import unreal

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = "/Game/KM360"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
GS = unreal

SECTION_COLORS = {
    "hero": "#1F4FE0", "problema": "#D62246", "mercadolivre": "#FFE600", "tiktokshop": "#25F4EE",
    "shein": "#FFFFFF", "shopee": "#EE4D2D", "resultados": "#19D27A", "final": "#1F4FE0",
}


# ---------------------------------------------------------------- cores
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(hex_or_rgb, a=1.0):
    if isinstance(hex_or_rgb, str):
        h = hex_or_rgb.lstrip("#")
        rgb = [srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    else:
        rgb = hex_or_rgb
    return unreal.LinearColor(rgb[0], rgb[1], rgb[2], a)


# ---------------------------------------------------------------- nível
def open_or_new_map(clip):
    path = f"{ROOT}/Maps/{clip}"
    if EAL.does_asset_exist(path):
        LES.load_level(path)
    else:
        LES.new_level(path, False)
    # limpa tudo o que foi criado por nós (rebuild idempotente)
    for a in EAS.get_all_level_actors():
        if a.actor_has_tag("KM"):
            EAS.destroy_actor(a)
    return path


def save_map():
    LES.save_current_level()


def spawn(cls, loc=(0, 0, 0), rot=(0, 0, 0), label=None):
    a = EAS.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(*rot))
    a.tags = [unreal.Name("KM")]
    if label:
        a.set_actor_label(label)
    return a


def look_rot(frm, to):
    d = [to[i] - frm[i] for i in range(3)]
    yaw = math.degrees(math.atan2(d[1], d[0]))
    pitch = math.degrees(math.atan2(d[2], math.hypot(d[0], d[1])))
    return unreal.Rotator(roll=0, pitch=pitch, yaw=yaw)


# ---------------------------------------------------------------- HDRI / estúdio
def import_hdri(name, file_path):
    dest = f"{ROOT}/HDRI"
    t = unreal.AssetImportTask()
    t.filename = file_path
    t.destination_path = dest
    t.destination_name = name
    t.automated = True
    t.replace_existing = True
    t.save = True
    AT.import_asset_tasks([t])
    return unreal.load_asset(f"{dest}/{name}")


def studio(cubemap, exposure_bias=0.0, sky_intensity=1.0, lights=None, cubemap_angle=0.0):
    """SkyLight com cubemap da seção (aparece só em reflexos/ambiente) + PPV + rect lights."""
    sky = spawn(unreal.SkyLight, label="KM_SkyLight")
    sc = sky.light_component
    sc.set_mobility(unreal.ComponentMobility.MOVABLE)
    sc.set_editor_property("source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    sc.set_editor_property("cubemap", cubemap)
    sc.set_editor_property("cubemap_resolution", 1024)
    sc.set_editor_property("source_cubemap_angle", cubemap_angle)
    sc.set_editor_property("intensity", sky_intensity)
    sc.set_editor_property("real_time_capture", False)
    sc.set_editor_property("lower_hemisphere_is_black", False)
    sc.recapture_sky()

    ppv = spawn(unreal.PostProcessVolume, label="KM_PPV")
    ppv.set_editor_property("unbound", True)
    ppv.set_editor_property("priority", 10.0)
    s = ppv.settings
    def ov(name, value):
        s.set_editor_property("override_" + name, True)
        s.set_editor_property(name, value)
    ov("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    ov("auto_exposure_apply_physical_camera_exposure", False)
    ov("auto_exposure_bias", exposure_bias)
    ov("bloom_intensity", 0.0)
    ov("vignette_intensity", 0.0)
    ov("motion_blur_amount", 0.0)
    ov("scene_fringe_intensity", 0.0)
    ov("lens_flare_intensity", 0.0)
    ov("film_grain_intensity", 0.0)
    ov("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.LUMEN)
    ov("reflection_method", unreal.ReflectionMethod.LUMEN)
    ov("lumen_reflection_quality", 4.0)
    ov("lumen_final_gather_quality", 2.0)
    ov("lumen_scene_detail", 2.0)
    ov("lumen_max_roughness_to_trace_reflections", 0.6)
    ppv.settings = s

    for i, L in enumerate(lights or []):
        rl = spawn(unreal.RectLight, loc=L["loc"], label=f"KM_Rect{i}")
        rl.set_actor_rotation(look_rot(L["loc"], L.get("at", (0, 0, 0))), False)
        c = rl.light_component
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
        c.set_editor_property("intensity", L.get("i", 20.0))
        c.set_editor_property("source_width", L.get("w", 200.0))
        c.set_editor_property("source_height", L.get("h", 60.0))
        c.set_editor_property("attenuation_radius", 5000.0)
        c.set_editor_property("barn_door_angle", 88.0)
        c.set_editor_property("cast_shadows", L.get("shadows", True))
        col = L.get("color", (255, 255, 255))
        c.set_editor_property("light_color", unreal.Color(col[2], col[1], col[0], 255))  # Color é BGRA
    return sky, ppv


def camera(loc, at=(0, 0, 0), focal=50.0, label="KM_Camera"):
    cam = spawn(unreal.CineCameraActor, loc=loc, label=label)
    cam.set_actor_rotation(look_rot(loc, at), False)
    cc = cam.get_cine_camera_component()
    fb = cc.filmback
    fb.sensor_width = 24.0
    fb.sensor_height = 24.0
    cc.filmback = fb
    cc.set_editor_property("current_focal_length", focal)
    fs = cc.focus_settings
    fs.focus_method = unreal.CameraFocusMethod.DISABLE
    cc.focus_settings = fs
    return cam


# ---------------------------------------------------------------- materiais
def _master_metal():
    path = f"{ROOT}/Materials/M_Metal"
    if EAL.does_asset_exist(path):
        return unreal.load_asset(path)
    m = AT.create_asset("M_Metal", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    def vparam(name, val, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", val)
        return e
    def sparam(name, val, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", val)
        return e
    MEL.connect_material_property(vparam("BaseColor", unreal.LinearColor(0.8, 0.8, 0.8, 1), 0), "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(sparam("Metallic", 1.0, 200), "", unreal.MaterialProperty.MP_METALLIC)
    MEL.connect_material_property(sparam("Roughness", 0.1, 300), "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(sparam("Specular", 0.5, 400), "", unreal.MaterialProperty.MP_SPECULAR)
    em = vparam("Emissive", unreal.LinearColor(0, 0, 0, 1), 500)
    MEL.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    return m


def mat(name, color, metallic=1.0, rough=0.1, emissive=None, specular=0.5):
    """MaterialInstance de M_Metal. color: hex sRGB ou lista linear."""
    parent = _master_metal()
    path = f"{ROOT}/Materials/MI_{name}"
    mi = unreal.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(
        f"MI_{name}", f"{ROOT}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    MEL.set_material_instance_vector_parameter_value(mi, "BaseColor", lin(color))
    MEL.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    MEL.set_material_instance_scalar_parameter_value(mi, "Roughness", rough)
    MEL.set_material_instance_scalar_parameter_value(mi, "Specular", specular)
    if emissive is not None:
        col, k = emissive
        c = lin(col)
        MEL.set_material_instance_vector_parameter_value(mi, "Emissive", unreal.LinearColor(c.r * k, c.g * k, c.b * k, 1))
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi)
    return mi


# ---------------------------------------------------------------- malhas
# Convenção 2D -> mundo: polígonos desenhados em (u=direita, v=cima), extrudados na profundidade.
# Mundo UE: câmera olha +X, então u -> +Y, v -> +Z, profundidade -> X.
Q_UV_TO_WORLD = unreal.Quat(0.5, 0.5, 0.5, 0.5)  # local X->Y, Y->Z, Z->X


def new_mesh():
    return unreal.DynamicMesh()


def prim_opts(material_id=0, per_face=True):
    o = unreal.GeometryScriptPrimitiveOptions()
    o.polygroup_mode = (unreal.GeometryScriptPrimitivePolygroupMode.PER_FACE if per_face
                        else unreal.GeometryScriptPrimitivePolygroupMode.SINGLE_GROUP)
    o.material_id = material_id
    return o


def extrude_poly(mesh, pts_uv, depth, material_id=0, bevel=0.0, bevel_sub=0, center_depth=0.0, xform=None, up=False):
    """Extruda polígono 2D (u,v) em profundidade `depth` (centrado em center_depth), com chanfro opcional.
    Retorna nova malha anexada a `mesh` (in-place)."""
    part = new_mesh()
    poly = [unreal.Vector2D(u, v) for (u, v) in pts_uv]
    # O ear-clipping do Geometry Script só triangula polígonos côncavos certo com área "negativa" (horária
    # em u,v); no sentido oposto ele dobra triângulos (o K virava cunha). Triangula horário e depois inverte.
    if _signed_area(pts_uv) > 0:
        poly.reverse()
    t = unreal.Transform(unreal.Vector(0, 0, -depth / 2.0 + center_depth), unreal.Rotator(0, 0, 0), unreal.Vector(1, 1, 1))
    GS.GeometryScript_Primitives.append_simple_extrude_polygon(part, prim_opts(material_id), t, poly, depth, 0, True)
    if GS.GeometryScript_MeshQueries.get_mesh_volume_area(part)[1] < 0:
        GS.GeometryScript_Normals.flip_normals(part)
    if bevel > 0:
        bo = unreal.GeometryScriptMeshBevelOptions()
        bo.bevel_distance = bevel
        bo.subdivisions = bevel_sub
        bo.round_weight = 1.0
        bo.infer_material_id = False
        bo.set_material_id = material_id
        GS.GeometryScript_MeshModeling.apply_mesh_polygroup_bevel(part, bo)
    if not up:  # up=True: polígono no plano XY do mundo, extrudado em +Z (colunas, caixas)
        tr = unreal.Transform()
        tr.rotation = Q_UV_TO_WORLD
        GS.GeometryScript_MeshTransforms.transform_mesh(part, tr)
    if xform is not None:
        GS.GeometryScript_MeshTransforms.transform_mesh(part, xform)
    GS.GeometryScript_MeshEdits.append_mesh(mesh, part, unreal.Transform())
    return mesh


def _signed_area(p):
    return 0.5 * sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def append_buffers(mesh, verts, normals, tris, material_id=0, uvs=None):
    b = unreal.GeometryScriptSimpleMeshBuffers()
    b.vertices = [unreal.Vector(*v) for v in verts]
    b.normals = [unreal.Vector(*n) for n in normals]
    b.uv0 = [unreal.Vector2D(*uv) for uv in (uvs or [(0, 0)] * len(verts))]
    b.triangles = [unreal.IntVector(*t) for t in tris]
    GS.GeometryScript_MeshEdits.append_buffers_to_mesh(mesh, b, material_id)
    return mesh


def tube_along(path_pts, radii, sides=24, closed=False, up_hint=(0, 0, 1)):
    """Tubo de seção circular ao longo de uma polilinha 3D com raio por ponto. Retorna (verts, normals, tris).
    Normais analíticas (suaves). Tampas arredondadas não incluídas (raio -> ~0 nas pontas)."""
    n = len(path_pts)
    verts, norms, tris, uvs = [], [], [], []
    def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    def nrm(a):
        l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
        return (a[0] / l, a[1] / l, a[2] / l)
    # frames por transporte paralelo
    tans = []
    for i in range(n):
        if closed:
            t = sub(path_pts[(i + 1) % n], path_pts[(i - 1) % n])
        else:
            t = sub(path_pts[min(i + 1, n - 1)], path_pts[max(i - 1, 0)])
        tans.append(nrm(t))
    up = up_hint
    nprev = nrm(cross(tans[0], up))
    if abs(sum(nprev)) < 1e-6 and all(abs(c) < 1e-6 for c in nprev):
        nprev = nrm(cross(tans[0], (1, 0, 0)))
    frames = []
    for i in range(n):
        t = tans[i]
        b = nrm(cross(t, nprev))
        nn = nrm(cross(b, t))
        frames.append((nn, b))
        nprev = nn
    for i in range(n):
        p = path_pts[i]
        nn, b = frames[i]
        r = radii[i]
        for k in range(sides):
            a = 2 * math.pi * k / sides
            d = (nn[0] * math.cos(a) + b[0] * math.sin(a), nn[1] * math.cos(a) + b[1] * math.sin(a),
                 nn[2] * math.cos(a) + b[2] * math.sin(a))
            verts.append((p[0] + d[0] * r, p[1] + d[1] * r, p[2] + d[2] * r))
            norms.append(d)
            uvs.append((i / max(1, n - 1), k / sides))
    segs = n if closed else n - 1
    for i in range(segs):
        i2 = (i + 1) % n
        for k in range(sides):
            k2 = (k + 1) % sides
            a, b_, c, d = i * sides + k, i * sides + k2, i2 * sides + k2, i2 * sides + k
            tris.append((a, b_, c))
            tris.append((a, c, d))
    if not closed:  # tampas em leque
        for ring, sgn in ((0, -1), (n - 1, 1)):
            t = tans[ring]
            ci = len(verts)
            verts.append(path_pts[ring])
            norms.append((t[0] * sgn, t[1] * sgn, t[2] * sgn))
            uvs.append((ring / max(1, n - 1), 0.5))
            for k in range(sides):
                a, b_ = ring * sides + k, ring * sides + (k + 1) % sides
                tris.append((ci, b_, a) if sgn < 0 else (ci, a, b_))
    return verts, norms, tris, uvs


def append_outward(mesh, verts, normals, tris, material_id=0, uvs=None):
    """Anexa buffers garantindo winding para fora (volume > 0) sem inverter as normais analíticas."""
    probe = new_mesh()
    append_buffers(probe, verts, normals, tris)
    _, vol = GS.GeometryScript_MeshQueries.get_mesh_volume_area(probe)
    if vol < 0:
        tris = [(a, c, b) for (a, b, c) in tris]
    return append_buffers(mesh, verts, normals, tris, material_id, uvs)


def finish_mesh(mesh, split_angle=None, smooth=False):
    if smooth:
        GS.GeometryScript_Normals.recompute_normals(mesh, unreal.GeometryScriptCalculateNormalsOptions())
    elif split_angle is not None:
        so = unreal.GeometryScriptSplitNormalsOptions()
        so.split_by_opening_angle = True
        so.opening_angle_deg = split_angle
        GS.GeometryScript_Normals.compute_split_normals(mesh, so, unreal.GeometryScriptCalculateNormalsOptions())
    return mesh


def save_static_mesh(mesh, name, materials):
    path = f"{ROOT}/Meshes/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    o = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    o.enable_recompute_normals = False
    o.enable_recompute_tangents = True
    o.enable_collision = False
    sm, outcome = GS.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, path, o)
    # materiais por slot
    for i, mi in enumerate(materials):
        sm.set_material(i, mi)
    # distance field e Lumen precisam de build settings padrão; garante DF resolution razoável
    try:
        bs = sm.get_editor_property("source_models")
    except Exception:
        pass
    EAL.save_loaded_asset(sm)
    return sm


DF = {"on": True}  # affect_distance_field_lighting (Lumen scene) p/ malhas novas


def place_mesh(sm, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), label=None, materials=None):
    a = spawn(unreal.StaticMeshActor, loc=loc, rot=rot, label=label)
    c = a.static_mesh_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_static_mesh(sm)
    c.set_editor_property("affect_distance_field_lighting", DF["on"])
    a.set_actor_scale3d(unreal.Vector(*scale))
    for i, mi in enumerate(materials or []):
        c.set_material(i, mi)
    return a


# ---------------------------------------------------------------- sequência
def new_sequence(clip, n_frames, fps=30):
    path = f"{ROOT}/Seq/{clip}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    seq = AT.create_asset(clip, f"{ROOT}/Seq", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(fps, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(n_frames)
    return seq


def bind_camera(seq, cam, n_frames):
    b = seq.add_possessable(cam)
    track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    sec = track.add_section()
    sec.set_range(0, n_frames)
    sec.set_camera_binding_id(seq.get_portable_binding_id(seq, b) if hasattr(seq, "get_portable_binding_id") else seq.get_binding_id(b))
    return b


def key_transform(seq, actor, n_frames, fn, step=1, frames=None, constant=False):
    """fn(frame) -> (loc(x,y,z), rot(roll,pitch,yaw), scale(x,y,z)). Keys lineares (ou constantes) por quadro."""
    b = seq.add_possessable(actor)
    tr = b.add_track(unreal.MovieScene3DTransformTrack)
    sec = tr.add_section()
    sec.set_range(-60, n_frames + 1)
    chans = sec.get_channels_by_type(unreal.MovieSceneScriptingDoubleChannel)
    lin_i = unreal.MovieSceneKeyInterpolation.CONSTANT if constant else unreal.MovieSceneKeyInterpolation.LINEAR
    if frames is None:
        frames = list(range(0, n_frames + 1, step))
        if frames[-1] != n_frames:
            frames.append(n_frames)
    for f in frames:
        loc, rot, scl = fn(f)
        vals = list(loc) + list(rot) + list(scl)
        for ch, v in zip(chans, vals):
            ch.add_key(unreal.FrameNumber(f), float(v), 0.0, unreal.MovieSceneTimeUnit.DISPLAY_RATE, lin_i)
    return b


def save_all(seq=None):
    if seq is not None:
        EAL.save_loaded_asset(seq)
    save_map()


# ---------------------------------------------------------------- render (MRQ)
RENDER = {"state": "idle", "clip": None, "ok": None}
CVARS = {
    "r.Lumen.Reflections.DownsampleFactor": 1,
    "r.Lumen.Reflections.MaxRoughnessToTrace": 0.6,
    "r.Lumen.Reflections.Temporal": 1,
}


def set_df(on):
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.actor_has_tag("KM"):
            a.static_mesh_component.set_editor_property("affect_distance_field_lighting", on)


def recapture():
    for a in EAS.get_all_level_actors():
        if isinstance(a, unreal.SkyLight):
            a.light_component.recapture_sky()


def render(clip, map_path, seq, out_dir, start=None, end=None, temporal=8, warmup=48, res=1200, step=1):
    recapture()
    save_map()
    qs = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    q = qs.get_queue()
    q.delete_all_jobs()
    job = q.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.job_name = clip
    job.sequence = unreal.SoftObjectPath(seq.get_path_name())
    job.map = unreal.SoftObjectPath(unreal.load_asset(map_path).get_path_name())
    cfg = job.get_configuration()
    o = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    o.output_directory = unreal.DirectoryPath(out_dir)
    o.output_resolution = unreal.IntPoint(res, res)
    o.file_name_format = "{frame_number}"
    o.zero_pad_frame_numbers = 4
    o.override_existing_output = True
    o.output_frame_step = step
    if start is not None:
        o.use_custom_playback_range = True
        o.custom_start_frame = start
        o.custom_end_frame = end
    d = cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    d.accumulator_includes_alpha = True
    png = cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    png.write_alpha = True
    aa = cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.temporal_sample_count = temporal
    aa.spatial_sample_count = 1
    aa.override_anti_aliasing = True
    aa.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_TSR
    aa.render_warm_up_count = warmup
    aa.engine_warm_up_count = warmup
    aa.render_warm_up_frames = True
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
    cv = cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    for k, v in CVARS.items():
        cv.add_or_update_console_variable(k, v)
    RENDER.update(state="rendering", clip=clip, ok=None)

    def _done(executor, success):
        RENDER.update(state="done", ok=bool(success))
    ex = qs.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
    ex.on_executor_finished_delegate.add_callable(_done)
    RENDER["executor"] = ex
    return ex


def render_status():
    qs = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    return f"{RENDER['state']} clip={RENDER['clip']} ok={RENDER['ok']} is_rendering={qs.is_rendering()}"


# ---------------------------------------------------------------- logo KM 360
# Medidas tiradas de logooficial.jpg (px do recorte 270,300 -> 1050,870; v para baixo).
LOGO_S = 0.25                 # cm por px
LOGO_C = (391.0, 290.0)       # eixo de giro (centro da composição K..arco)
K_POLY = [(22.5, 92.5), (76, 92.5), (76, 257.6), (262.5, 111), (322.5, 111), (76, 304.7), (76, 482.5), (22.5, 482.5)]
LEG_POLY = [(121.8, 322.5), (164.2, 290), (372.5, 515), (300, 515)]
M_POLY = [(277.5, 182.5), (419, 342.5), (560, 182.5), (560, 484), (522.5, 484), (522.5, 270),
          (415, 390), (306, 270), (306, 437.7), (277.5, 407)]
ARC_C = (492.0, 284.5)
ARC_R = 262.0
LETTER_DEPTH = 14.0


def lp(u, v):
    return ((u - LOGO_C[0]) * LOGO_S, (LOGO_C[1] - v) * LOGO_S)


def letters_mesh(name="SM_KM_Letters", mats=None, depth=LETTER_DEPTH, bevel=0.9):
    """K (azul, slot 0) + perna da K e M (cromo, slot 1)."""
    m = new_mesh()
    extrude_poly(m, [lp(*p) for p in K_POLY], depth, material_id=0, bevel=bevel)
    extrude_poly(m, [lp(*p) for p in LEG_POLY], depth, material_id=1, bevel=bevel)
    extrude_poly(m, [lp(*p) for p in M_POLY], depth, material_id=1, bevel=bevel)
    finish_mesh(m, split_angle=20.0)
    return save_static_mesh(m, name, mats or [])


def arc_points(start_deg, end_deg, depth_x=0.0, seg_per_deg=1.0, r=None, c=None):
    cy, cz = lp(*(c or ARC_C))
    R = (r or ARC_R) * LOGO_S
    n = max(2, int(abs(end_deg - start_deg) * seg_per_deg) + 1)
    pts = []
    for i in range(n):
        th = math.radians(start_deg + (end_deg - start_deg) * i / (n - 1))
        pts.append((depth_x, cy + R * math.cos(th), cz + R * math.sin(th)))
    return pts


def taper(n, rmax, ramp_a=0.30, ramp_b=0.30, rmin=0.12):
    out = []
    for i in range(n):
        t = i / (n - 1)
        a = min(1.0, t / ramp_a) if ramp_a > 0 else 1.0
        b = min(1.0, (1 - t) / ramp_b) if ramp_b > 0 else 1.0
        a = a * a * (3 - 2 * a)
        b = b * b * (3 - 2 * b)
        out.append(max(rmin, rmax * a * b))
    return out


def arc_mesh(name, start_deg=125.0, end_deg=-110.0, rmax=2.0, depth_x=0.0, mats=None, ramp_a=0.30, ramp_b=0.30,
             closed=False, sides=32, r=None, c=None, seg_per_deg=1.0):
    pts = arc_points(start_deg, end_deg, depth_x, seg_per_deg, r, c)
    if closed:
        pts = pts[:-1]
        radii = [rmax] * len(pts)
    else:
        radii = taper(len(pts), rmax, ramp_a, ramp_b)
    v, nrm, t, uv = tube_along(pts, radii, sides=sides, closed=closed, up_hint=(1, 0, 0))
    m = new_mesh()
    append_outward(m, v, nrm, t, uvs=uv)
    return save_static_mesh(m, name, mats or [])


# ---------------------------------------------------------------- setup comum de clipe
def setup_clip(clip, n, cam_loc, cam_at=(0, 0, 0), focal=50.0, lights=None, exposure=0.0, hdri=None):
    path = open_or_new_map(clip)
    cube = import_hdri(f"HDR_{hdri or clip}", f"{PROJ}/Saved/HDRI/HDR_{hdri or clip}.hdr")
    studio(cube, exposure_bias=exposure, lights=lights if lights is not None else DEFAULT_LIGHTS + RIM_LIGHTS)
    cam = camera(cam_loc, cam_at, focal=focal)
    seq = new_sequence(clip, n)
    bind_camera(seq, cam, n)
    return path, seq, cam


DEFAULT_LIGHTS = [
    dict(loc=(-260, -320, 300), i=12.0, w=220, h=80),   # key alto-esquerda
    dict(loc=(250, 330, 160), i=10.0, w=60, h=260),      # rim traseira-direita
]
# luz de recorte (pedido do coordenador): painéis frios grandes de lado/por trás + topo/base.
# Em metal, o recorte aparece nos chanfros: chanfro lateral reflete ±Y, superior +Z, inferior -Z.
RIM_LIGHTS = [
    dict(loc=(60, -340, 20), i=300.0, w=400, h=300, color=(222, 234, 255), shadows=False),   # lado/trás esquerda
    dict(loc=(60, 340, 20), i=300.0, w=400, h=300, color=(222, 234, 255), shadows=False),    # lado/trás direita
    dict(loc=(40, 0, 340), i=220.0, w=400, h=300, color=(232, 240, 255), shadows=False),     # topo
    dict(loc=(0, 0, -320), i=120.0, w=400, h=300, color=(222, 234, 255), shadows=False),     # base
]
FAR = (0, 0, -100000)


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * t for x, y in zip(a, b))
    return a + (b - a) * t


# ---------------------------------------------------------------- formas 2D
def circle_pts(r, n=64, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def rrect_pts(w, h, r, seg=8, cx=0.0, cy=0.0):
    pts = []
    for (qx, qy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + qx + r * math.cos(a), cy + qy + r * math.sin(a)))
    return pts


def heart_pts(size, n=72):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32.0, (y + 2.5) * size / 32.0))
    # remove pontos quase duplicados (bico e reentrância)
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-3 * size:
            out.append(p)
    return out


def annulus(mesh, r_in, r_out, z0, z1, seg=128, material_id=0):
    """Anel plano (esteira): topo, base, parede interna e externa com normais duras."""
    v, n, t, uv = [], [], [], []
    def ring(r, z, nrm_fn):
        base = len(v)
        for i in range(seg + 1):
            a = 2 * math.pi * i / seg
            v.append((r * math.cos(a), r * math.sin(a), z))
            n.append(nrm_fn(a))
            uv.append((i / seg, z))
        return base
    def strip(b0, b1, flip):
        for i in range(seg):
            a, b_, c, d = b0 + i, b0 + i + 1, b1 + i + 1, b1 + i
            t.extend([(a, c, b_), (a, d, c)] if flip else [(a, b_, c), (a, c, d)])
    up = lambda a: (0, 0, 1)
    dn = lambda a: (0, 0, -1)
    out = lambda a: (math.cos(a), math.sin(a), 0)
    inn = lambda a: (-math.cos(a), -math.sin(a), 0)
    strip(ring(r_in, z1, up), ring(r_out, z1, up), False)
    strip(ring(r_in, z0, dn), ring(r_out, z0, dn), True)
    strip(ring(r_out, z0, out), ring(r_out, z1, out), False)
    strip(ring(r_in, z0, inn), ring(r_in, z1, inn), True)
    return append_outward_parts(mesh, v, n, t, uv, material_id)


def append_outward_parts(mesh, v, n, t, uv, material_id=0):
    """Como append_outward, mas para malhas com várias partes (checa volume total)."""
    return append_outward(mesh, v, n, t, material_id, uv)


def ring_tube(mesh, radius, tube_r, z=0.0, seg=160, sides=20, material_id=0):
    pts = [(radius * math.cos(2 * math.pi * i / seg), radius * math.sin(2 * math.pi * i / seg), z) for i in range(seg)]
    v, n, t, uv = tube_along(pts, [tube_r] * seg, sides=sides, closed=True, up_hint=(0, 0, 1))
    return append_outward(mesh, v, n, t, material_id, uv)


def path_tube(mesh, pts, tube_r, sides=16, material_id=0, closed=False, up_hint=(1, 0, 0)):
    v, n, t, uv = tube_along(pts, [tube_r] * len(pts) if not callable(tube_r) else [tube_r(i) for i in range(len(pts))],
                             sides=sides, closed=closed, up_hint=up_hint)
    return append_outward(mesh, v, n, t, material_id, uv)


def subtract(mesh, tool, xform=None):
    o = unreal.GeometryScriptMeshBooleanOptions()
    GS.GeometryScript_MeshBooleans.apply_mesh_boolean(mesh, unreal.Transform(), tool, xform or unreal.Transform(),
                                                      unreal.GeometryScriptBooleanOperation.SUBTRACT, o)
    return mesh
