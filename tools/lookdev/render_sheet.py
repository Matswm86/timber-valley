"""Render one strip of glTF/GLB models side by side, from the game camera pitch (~50 deg), in-game scale.

Usage: blender -b --python render_sheet.py -- spec.json
spec = {"out": "x.png", "cell": 3.0, "hmax": 4.5, "px_per_m": 60, "samples": 32,
        "items": [{"file": "...", "scale": 2.5}, ...]}
"""
import bpy, sys, json, math
from mathutils import Vector

spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
cell = spec.get("cell", 3.0)
n = len(spec["items"])
for i, it in enumerate(spec["items"]):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=it["file"])
    new = [o for o in bpy.data.objects if o not in before]
    s = it.get("scale", 1.0)
    # optional for rigged characters: "action" (+ "frame") to pose it, "hide" = object names (without .001 suffix) to hide
    for o in new:
        if o.type == "ARMATURE" and it.get("action"):
            ad = o.animation_data or o.animation_data_create()
            for t in list(ad.nla_tracks):
                ad.nla_tracks.remove(t)
            act = next(a for a in reversed(bpy.data.actions) if a.name.split(".")[0] == it["action"])
            ad.action = act
            if hasattr(ad, "action_slot") and act.slots:
                ad.action_slot = act.slots[0]
        if o.name.split(".")[0] in it.get("hide", []):
            o.hide_render = True
    for o in new:
        if o.parent is None or o.parent not in new:
            o.scale = o.scale * s
            o.location = Vector((i * cell - (n - 1) * cell / 2, 0, 0)) + o.location * s
            o.rotation_euler.z += it.get("rotz", 0.0)
width = n * cell
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
g = bpy.context.object; g.scale = (width + 10, cell * 6, 1)
gm = bpy.data.materials.new("ground"); gm.use_nodes = True
b = next(nd for nd in gm.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.20, 0.42, 0.10, 1)   # ~ the game's grass
b.inputs["Roughness"].default_value = 1.0
g.data.materials.append(gm)
# sun roughly like World.gd (pitch -52, yaw -38) + sky ambient
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(38), 0, math.radians(-38)))
sun = bpy.context.object; sun.data.energy = 3.0; sun.data.angle = math.radians(8); sun.data.color = (1.0, 0.93, 0.8)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
bg = next(nd for nd in w.node_tree.nodes if nd.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.55, 0.72, 0.95, 1); bg.inputs["Strength"].default_value = 0.9
hmax = spec.get("hmax", 4.0)
pitch = math.radians(spec.get("pitch", 50))
vert = cell * 0.9 * math.sin(pitch) + hmax * math.cos(pitch) + 0.4
bpy.ops.object.camera_add()
cam = bpy.context.object; sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = width
ppm = spec.get("px_per_m", 60)
sc.render.resolution_x = int(width * ppm); sc.render.resolution_y = int(vert * ppm)
# aim at a point so ground line sits near the bottom
aim = Vector((0, 0, 0)); d = Vector((0, -math.cos(pitch), math.sin(pitch)))
up = Vector((0, math.sin(pitch), math.cos(pitch)))
centre = aim + up * (vert / 2 - cell * 0.45 * math.sin(pitch) - 0.2)
cam.location = centre + d * 80
cam.rotation_euler = (math.pi / 2 - pitch, 0, 0)
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
sc.cycles.samples = spec.get("samples", 32); sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.frame_set(spec.get("frame", 1))
sc.render.filepath = spec["out"]
bpy.ops.render.render(write_still=True)
print("WROTE", spec["out"])
