"""Print tri count, dims, materials of every glTF/GLB in a folder. Usage: blender -b --python survey.py -- <dir>"""
import bpy, sys, glob, os
d = sys.argv[sys.argv.index("--") + 1]
files = sorted(glob.glob(os.path.join(d, "*.gltf")) + glob.glob(os.path.join(d, "*.glb")))
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    tris = 0; mats = set(); mn = [1e9]*3; mx = [-1e9]*3; nmesh = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.context.scene.objects:
        if o.type != "MESH": continue
        nmesh += 1
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
        for m in o.data.materials:
            if m: mats.add(m.name)
        for c in o.bound_box:
            w = o.matrix_world @ __import__("mathutils").Vector(c)
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    print(f"SURVEY {os.path.basename(f):32s} tris={tris:6d} meshes={nmesh} size=({mx[0]-mn[0]:.2f},{mx[1]-mn[1]:.2f},{mx[2]-mn[2]:.2f}) zmin={mn[2]:.2f} mats={sorted(mats)}")
