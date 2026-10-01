"""Close-up and game-camera renders of character GLBs (Idle frame 0), for the player face review.
  blender -b --python tools/lookdev/render_heads.py -- out_dir name=path.glb ...
Writes <out>/<name>_face.png (front close-up) and <out>/<name>_game.png (game camera pitch, on grass)."""
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
os.makedirs(out, exist_ok=True)


def lin(c):
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


for spec in args[1:]:
    name, path = spec.split("=", 1)
    for view in ("face", "game"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        try:
            pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "OPTIX"; pr.get_devices()
            for d in pr.devices: d.use = d.type == "OPTIX"
            sc.cycles.device = "GPU"
        except Exception:
            pass
        sc.cycles.samples = 32; sc.cycles.use_denoising = True
        sc.view_settings.view_transform = "Standard"
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
        bg.inputs[0].default_value = (*lin((0.62, 0.74, 0.92)), 1); bg.inputs[1].default_value = 0.85
        bpy.ops.import_scene.gltf(filepath=path)
        rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
        if rig.animation_data and "Idle" in bpy.data.actions:
            rig.animation_data.action = bpy.data.actions["Idle"]
        for o in bpy.data.objects:
            if o.name.startswith("Axe"):
                o.hide_render = True
        sc.frame_set(1)
        bpy.context.view_layer.update()
        zs = [ (o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == "MESH" for c in o.bound_box]
        H = max(zs)
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
        sun.data.energy = 3.2; sun.data.color = lin((1.0, 0.93, 0.8)); sun.rotation_mode = "QUATERNION"
        sun.rotation_quaternion = (-Vector((0.379, 0.485, -0.788))).to_track_quat("Z", "Y")
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
        cam.data.type = "ORTHO"; cam.rotation_mode = "QUATERNION"
        if view == "face":
            sc.render.resolution_x = sc.render.resolution_y = 400
            tgt = Vector((0, 0, H * 0.68)); d = Vector((0, -1, 0.12)).normalized()
            cam.data.ortho_scale = H * 0.5
        else:
            sc.render.resolution_x = sc.render.resolution_y = 300
            bpy.ops.mesh.primitive_plane_add(size=20)
            gm = bpy.data.materials.new("g"); gm.use_nodes = True
            next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (*lin((0.45, 0.66, 0.25)), 1)
            bpy.context.object.data.materials.append(gm)
            tgt = Vector((0, 0, H * 0.5)); d = Vector((0, -6.6, 8.4)).normalized()
            cam.data.ortho_scale = H * 1.6
        cam.location = tgt + d * 10
        cam.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
        sc.render.filepath = f"{out}/{name}_{view}.png"
        bpy.ops.render.render(write_still=True)
