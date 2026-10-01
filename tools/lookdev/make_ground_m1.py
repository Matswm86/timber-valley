"""Ground tiles for M1, rendered top-down from own procedural Blender materials (own work, CC0).
Soft and low-contrast on purpose (DESIGN.md: colour, not detail): one tile = 4 x 4 m at 512 px.

  /home/mm/.local/bin/blender -b --python tools/lookdev/make_ground_m1.py
writes tools/lookdev/_render/ground/<name>_raw.png; then run tools/lookdev/make_ground_m1.sh for
`um sprite seamless` + `um sprite tile-preview` into assets/textures/ground/.
"""
import bpy, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = f"{REPO}/tools/lookdev/_render/ground"


def lin(c):
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1,)


# (sRGB) base A, base B, spot colour, spot scale, spot size, fleck colour, fleck scale, fleck size
TILES = {
    # V1 meadow: World.gd grass_a (0.27,0.54,0.14) / grass_b (0.38,0.63,0.17)
    "grass_v1": dict(a=(0.27, 0.54, 0.14), b=(0.38, 0.63, 0.17), spot=(0.42, 0.68, 0.2), sscale=5.0, ssize=0.28,
                     fleck=(0.22, 0.46, 0.12), fscale=9.0, fsize=0.16),
    # V2 Birch Bend: lighter spring green, a few pale fallen birch leaves
    "grass_birch": dict(a=(0.40, 0.64, 0.20), b=(0.52, 0.73, 0.25), spot=(0.58, 0.78, 0.30), sscale=5.0, ssize=0.28,
                        fleck=(0.86, 0.84, 0.46), fscale=7.0, fsize=0.07),
    # dirt path: World.gd dirt (0.86,0.72,0.5) / dirt_dark (0.78,0.63,0.42), soft pebbles
    "dirt_path": dict(a=(0.78, 0.63, 0.42), b=(0.86, 0.72, 0.5), spot=(0.92, 0.8, 0.6), sscale=8.0, ssize=0.13,
                      fleck=(0.70, 0.56, 0.38), fscale=5.0, fsize=0.12),
}


def material(name, t):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    L.new(em.outputs[0], out.inputs[0])
    tc = N.new("ShaderNodeTexCoord")
    # tileable coordinates: the tile's UV square wrapped onto a flat 4D torus (cos u, sin u, cos v | W = sin v),
    # so every noise/voronoi below repeats exactly at the tile edge. K converts "features per metre" scales.
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sep.inputs[0])
    trig = {}
    for axis in ("X", "Y"):
        ang = N.new("ShaderNodeMath"); ang.operation = "MULTIPLY"; ang.inputs[1].default_value = 6.283185
        L.new(sep.outputs[axis], ang.inputs[0])
        for op in ("COSINE", "SINE"):
            t_ = N.new("ShaderNodeMath"); t_.operation = op; L.new(ang.outputs[0], t_.inputs[0]); trig[axis + op] = t_.outputs[0]
    torus = N.new("ShaderNodeCombineXYZ")
    L.new(trig["XCOSINE"], torus.inputs[0]); L.new(trig["XSINE"], torus.inputs[1]); L.new(trig["YCOSINE"], torus.inputs[2])
    torus_w = trig["YSINE"]
    K = 4.0 / 6.283185

    def coords(node, seed=0.0):
        if hasattr(node, "noise_dimensions"):
            node.noise_dimensions = "4D"
        if seed:
            add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"; add.inputs[1].default_value = (seed, seed * 0.7, seed * 1.3)
            L.new(torus.outputs[0], add.inputs[0]); L.new(add.outputs[0], node.inputs["Vector"])
        else:
            L.new(torus.outputs[0], node.inputs["Vector"])
        L.new(torus_w, node.inputs["W"])

    # large soft two-tone patches
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9 * K; nz.inputs["Detail"].default_value = 1.5
    coords(nz)
    r0 = N.new("ShaderNodeValToRGB"); L.new(nz.outputs["Fac"], r0.inputs["Fac"])
    r0.color_ramp.elements[0].position = 0.35; r0.color_ramp.elements[0].color = lin(t["a"])
    r0.color_ramp.elements[1].position = 0.65; r0.color_ramp.elements[1].color = lin(t["b"])
    col = r0.outputs["Color"]

    def spots(col, scale, size, rgb, seed, soft=0.08):
        # soft round spots from Voronoi F1 distance, jittered so they are not a grid
        vo = N.new("ShaderNodeTexVoronoi"); vo.voronoi_dimensions = "4D"; vo.inputs["Scale"].default_value = scale * K
        vo.inputs["Randomness"].default_value = 1.0
        coords(vo, seed)
        r = N.new("ShaderNodeValToRGB"); L.new(vo.outputs["Distance"], r.inputs["Fac"])
        r.color_ramp.elements[0].position = size - soft; r.color_ramp.elements[0].color = (1, 1, 1, 1)
        r.color_ramp.elements[1].position = size; r.color_ramp.elements[1].color = (0, 0, 0, 1)
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
        L.new(r.outputs["Color"], mx.inputs["Factor"]); L.new(col, mx.inputs["A"]); mx.inputs["B"].default_value = lin(rgb)
        # only ~60% strength: spots tint the ground, they do not print on it
        mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"; mx2.inputs["Factor"].default_value = 0.55
        L.new(col, mx2.inputs["A"]); L.new(mx.outputs["Result"], mx2.inputs["B"])
        return mx2.outputs["Result"]

    col = spots(col, t["sscale"], t["ssize"], t["spot"], 1.3, soft=0.12)
    col = spots(col, t["fscale"], t["fsize"], t["fleck"], 7.9, soft=0.05)
    L.new(col, em.inputs["Color"])
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, t in TILES.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.use_denoising = False; sc.cycles.filter_width = 0.5  # no background bleed at the tile edge
        sc.render.resolution_x = sc.render.resolution_y = 512
        sc.view_settings.view_transform = "Standard"
        sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
        bpy.ops.mesh.primitive_plane_add(size=4.0)
        pl = bpy.context.object; pl.data.materials.append(material(name, t))
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
        cam.data.type = "ORTHO"; cam.data.ortho_scale = 4.0; cam.location = (0, 0, 5); sc.camera = cam
        sc.render.filepath = f"{OUT}/{name}_raw.png"
        bpy.ops.render.render(write_still=True)
        print("GROUND", name)


main()
