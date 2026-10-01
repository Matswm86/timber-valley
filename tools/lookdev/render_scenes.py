"""Review renders that look like the game camera: Godot sun (rotation (-52, -38, 0), warm), sky-blue ambient,
grass ground with real shadows, orthographic camera at the game pitch (offset (0, 8.4, 6.6) -> 51.8 deg),
looking from +Z (Godot). Scenes can combine several GLBs (Godot positions / Y rotation / scale).

  /home/mm/.local/bin/blender -b --python tools/lookdev/render_scenes.py -- scenes.json
scenes.json: [{"out": "x.png", "ground": [r, g, b], "size": 600, "parts": [{"glb": "...", "pos": [x, y, z],
              "rot_y": 0, "scale": [sx, sy, sz]}], "pad": 1.15, "boxes": [{"size": [x, y, z], "pos": [...], "rgb": [...]}]}]
"""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
scenes = json.load(open(args[0]))


def lin(c):
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def gpos(x, y, z):
    return Vector((x, -z, y))


def setup_gpu(sc):
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "OPTIX"
        sc.cycles.device = "GPU"
    except Exception as e:  # noqa: BLE001
        print("CPU render:", e)


for s in scenes:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    setup_gpu(sc)
    sc.cycles.samples = s.get("samples", 32)
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = s.get("size", 600)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (*lin((0.62, 0.74, 0.92)), 1)
    bg.inputs[1].default_value = s.get("ambient", 0.85)
    objs = []
    for p in s["parts"]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=p["glb"])
        new = [o for o in bpy.data.objects if o not in before]
        if p.get("keep"):   # only these node names (BuildSite stages: "stage1".."stageN")
            for o in list(new):
                if o.type == "MESH" and o.name.split(".")[0] not in p["keep"]:
                    new.remove(o); bpy.data.objects.remove(o, do_unlink=True)
        root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)
        for o in new:
            if o.parent is None:
                o.parent = root
        sx, sy, sz = p.get("scale", [1, 1, 1]) if isinstance(p.get("scale", 1), list) else [p.get("scale", 1)] * 3
        root.matrix_world = (Matrix.Translation(gpos(*p.get("pos", [0, 0, 0]))) @ Matrix.Rotation(math.radians(p.get("rot_y", 0)), 4, "Z")
                             @ Matrix.Diagonal((sx, sz, sy, 1)))
        objs += [o for o in new if o.type == "MESH"]
    for b in s.get("boxes", []):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.object
        o.scale = (b["size"][0], b["size"][2], b["size"][1]); o.location = gpos(*b["pos"])
        m = bpy.data.materials.new("box"); m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (*lin(b["rgb"]), 1); bsdf.inputs["Roughness"].default_value = 0.9
        o.data.materials.append(m); objs.append(o)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (mn + mx) / 2
    # ground
    bpy.ops.mesh.primitive_plane_add(size=400, location=(ctr.x, ctr.y, 0))
    gm = bpy.data.materials.new("ground"); gm.use_nodes = True
    gb = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    gb.inputs["Base Color"].default_value = (*lin(s.get("ground", (0.45, 0.66, 0.25))), 1)
    gb.inputs["Roughness"].default_value = 1.0
    bpy.context.object.data.materials.append(gm)
    # sun: Godot rotation (-52, -38, 0) -> light travels along (0.379, -0.788, -0.485) in Godot = (0.379, 0.485, -0.788) Blender
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy = s.get("sun", 3.2); sun.data.color = lin((1.0, 0.93, 0.8)); sun.data.angle = math.radians(4)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = (-Vector((0.379, 0.485, -0.788))).to_track_quat("Z", "Y")
    # camera
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"
    d = Vector((0, -6.6, 8.4)).normalized()
    cam.location = ctr + d * 60
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
    cam.data.clip_end = 500
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    cp = [inv @ p for p in pts]
    w = max(p.x for p in cp) - min(p.x for p in cp); h = max(p.y for p in cp) - min(p.y for p in cp)
    cx = (max(p.x for p in cp) + min(p.x for p in cp)) / 2; cy = (max(p.y for p in cp) + min(p.y for p in cp)) / 2
    cam.location = cam.matrix_world @ Vector((cx, cy, 0))
    cam.data.ortho_scale = max(w, h) * s.get("pad", 1.15)
    sc.render.filepath = s["out"]
    os.makedirs(os.path.dirname(s["out"]), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", s["out"])
