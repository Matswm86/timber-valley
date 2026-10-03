"""Shared bootstrap for build_m3.py, build_m4.py and build_m5.py (exec'd, not imported).

Pulls in everything from build_m2.py (which pulls in build_leftover.py -> m2_lib.py -> build_m1.py -> build_v3.py):
primitives in Godot coordinates (gb, gc, gl, gll, gseg, gpoly, gmove), the bake (albedo x height gradient x AO with a
ground plane), staged builds and run_plan. Adds:
  - accent(): build any earlier builder with the V3 teal swapped for another region accent (forklift, handcar stop, ...)
  - hull_loft(): a ship hull lofted through stations along Godot X (bow at +X), closed or open at the deck
  - conifer_tiers(): lumpy layered conifer crowns for redwood and frost fir
"""
import os

_m2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_m2.py")).read()
exec(compile(_m2.replace("run_plan(PLAN, f\"{REPO}/tools/lookdev/build_m2_report.json\", OUT_ROOT)", "pass"), "build_m2.py", "exec"))

WHITE = (0.97, 0.96, 0.93)
CHARCOAL = (0.24, 0.24, 0.25)


def accent(fn, a, ad):
    """Run a builder that uses mmats()['teal'/'teal_d'] (or the TEAL globals) with another accent pair."""
    def run():
        g = globals()
        old = g["TEAL"], g["TEAL_D"]
        g["TEAL"], g["TEAL_D"] = a, ad
        try:
            return fn()
        finally:
            g["TEAL"], g["TEAL_D"] = old
    return run


def hull_loft(stations, mats, K=6, deck=True, transom=True, smooth=True):
    """Hull through stations along Godot X. stations: [(x, half_beam, y_deck, y_keel, fullness)], stern first, bow last.
    mats: function(face_centre_y_godot, is_deck) -> material. Section = superellipse from the port deck edge down to the keel
    and up to the starboard deck edge (K segments). Returns one object."""
    bm = bmesh.new()
    rings = []
    for (x, hw, yd, yk, full) in stations:
        ring = []
        for k in range(K + 1):
            t = math.pi * k / K
            c, s = math.cos(t), math.sin(t)
            lat = hw * (abs(c) ** (1.0 / full)) * (1 if c >= 0 else -1)
            y = yd - (yd - yk) * (s ** (1.0 / full))
            ring.append(bm.verts.new(gpos(x, y, lat)))
        rings.append(ring)
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(K):
            faces.append(bm.faces.new((a[k], b[k], b[k + 1], a[k + 1])))
    caps = []
    if deck:
        top = [r[0] for r in rings] + [r[K] for r in reversed(rings)]
        caps.append(bm.faces.new(top))
    if transom:
        caps.append(bm.faces.new(list(rings[0])))
        caps.append(bm.faces.new(list(rings[-1])))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("hull"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("hull", me); bpy.context.collection.objects.link(ob)
    used = []
    for p in ob.data.polygons:
        cy = p.center.z   # Blender z = Godot y
        is_deck = p.normal.z > 0.85
        m = mats(cy, is_deck)
        if m.name not in [u.name for u in used]:
            used.append(m); ob.data.materials.append(m)
        p.material_index = [u.name for u in used].index(m.name)
        p.use_smooth = smooth and not is_deck and abs(p.normal.x) < 0.95
    return ob


def lobe_base(ob, z_max, amp, lobes=4, phase=0.3):
    """Buttress flare: push trunk vertices below z_max (Blender z) out in `lobes` lobes."""
    for v in ob.data.vertices:
        if v.co.z < z_max:
            a = math.atan2(v.co.y, v.co.x)
            k = 1.0 + amp * (1 - v.co.z / z_max) * (0.6 + 0.4 * math.cos(lobes * a + phase))
            v.co.x *= k; v.co.y *= k
    return ob


def conifer_tiers(tiers, mats, rnd, offset=0.03, seg=8, rings=5, amp=0.12, flat=0.62):
    """Layered lumpy crown: tiers [(z, r)] in Blender coords; each tier a flattened blob nudged sideways."""
    p = []
    for i, (z, r) in enumerate(tiers):
        az = rnd.uniform(0, 6.28)
        d = offset * rnd.uniform(0.5, 1.0)
        p.append(blob(1.0, (d * math.cos(az), d * math.sin(az), z), (r, r * rnd.uniform(0.9, 1.0), r * flat),
                      mats[i % len(mats)], i * 1.7 + 0.4, seg=seg, rings=rings, amp=amp))
    return p


def gtube(points, r, mat, sides=5, cap=True):
    """One continuous tube through Godot points (constant radius), rings oriented by parallel transport so the
    quads never twist (the inherited tube() flips its ring frame on sharp turns, which breaks the UV unwrap)."""
    P = [Vector(gpos(*q)) for q in points]
    n = len(P)
    T = [(P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n)]
    a = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    U = [T[0].cross(a).normalized()]
    for i in range(1, n):
        u = U[-1] - T[i] * U[-1].dot(T[i])
        U.append(u.normalized() if u.length > 1e-6 else U[-1])
    bm = bmesh.new()
    rings = []
    for p_, t, u in zip(P, T, U):
        w = t.cross(u).normalized()
        rings.append([bm.verts.new(p_ + r * (math.cos(2 * math.pi * k / sides) * u + math.sin(2 * math.pi * k / sides) * w)) for k in range(sides)])
    for ra, rb in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((ra[k], ra[(k + 1) % sides], rb[(k + 1) % sides], rb[k]))
    if cap:
        bm.faces.new(list(reversed(rings[-1])))
        bm.faces.new(list(rings[0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("gtube"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("gtube", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat); _smooth(ob)
    return ob


def _section(x, hw, yd, yk, full, K):
    out = []
    for k in range(K + 1):
        t = math.pi * k / K
        c, s = math.cos(t), math.sin(t)
        lat = hw * (abs(c) ** (1.0 / full)) * (1 if c >= 0 else -1)
        out.append((x, yd - (yd - yk) * (s ** (1.0 / full)), lat))
    return out


def hull_open(stations, thick, outer_mat, inner_mat, rim_mat, K=6):
    """Open planked hull (no deck), closed solid shell `thick` thick: outer skin, inner skin, rim along the gunwale and
    the two end bands. Same stations as hull_loft. outer_mat(face_centre_y) -> material."""
    bm = bmesh.new()
    outer = [[bm.verts.new(gpos(*q)) for q in _section(x, hw, yd, yk, f, K)] for (x, hw, yd, yk, f) in stations]
    inner = [[bm.verts.new(gpos(*q)) for q in _section(x, max(hw - thick, 0.004), yd, yk + thick, f, K)] for (x, hw, yd, yk, f) in stations]
    kinds = {}
    n = len(stations)
    for i in range(n - 1):
        for k in range(K):
            kinds[bm.faces.new((outer[i][k], outer[i + 1][k], outer[i + 1][k + 1], outer[i][k + 1]))] = "out"
            kinds[bm.faces.new((inner[i][k + 1], inner[i + 1][k + 1], inner[i + 1][k], inner[i][k]))] = "in"
        for k in (0, K):
            kinds[bm.faces.new((outer[i][k], inner[i][k], inner[i + 1][k], outer[i + 1][k]))] = "rim"
    for i in (0, n - 1):
        for k in range(K):
            kinds[bm.faces.new((outer[i][k], outer[i][k + 1], inner[i][k + 1], inner[i][k]))] = "rim"
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    order = list(bm.faces)
    kind_list = [kinds.get(f, "rim") for f in order]
    me = bpy.data.meshes.new("hullopen"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("hullopen", me); bpy.context.collection.objects.link(ob)
    mats = []
    for p, kd in zip(ob.data.polygons, kind_list):
        m = inner_mat if kd == "in" else (rim_mat if kd == "rim" else outer_mat(p.center.z))
        if m.name not in [u.name for u in mats]:
            mats.append(m); ob.data.materials.append(m)
        p.material_index = [u.name for u in mats].index(m.name)
        p.use_smooth = kd != "rim"
    return ob


def deck_strip(stations, inset, dy, thick, mat):
    """Deck following the sheer: quads between the port and starboard deck edges (inset from the hull side) at yd + dy."""
    bm = bmesh.new()
    top = [(bm.verts.new(gpos(x, yd + dy, max(hw - inset, 0.003))), bm.verts.new(gpos(x, yd + dy, -max(hw - inset, 0.003))))
           for (x, hw, yd, yk, f) in stations]
    bot = [(bm.verts.new(gpos(x, yd + dy - thick, max(hw - inset, 0.003))), bm.verts.new(gpos(x, yd + dy - thick, -max(hw - inset, 0.003))))
           for (x, hw, yd, yk, f) in stations]
    for i in range(len(stations) - 1):
        bm.faces.new((top[i][0], top[i + 1][0], top[i + 1][1], top[i][1]))
        bm.faces.new((bot[i][1], bot[i + 1][1], bot[i + 1][0], bot[i][0]))
        for s in (0, 1):
            bm.faces.new((top[i][s], bot[i][s], bot[i + 1][s], top[i + 1][s]))
    for i in (0, len(stations) - 1):
        bm.faces.new((top[i][0], top[i][1], bot[i][1], bot[i][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("deck"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("deck", me); bpy.context.collection.objects.link(ob)
    _assign(ob, mat)
    return ob


# Tighter unwrap for M3-M5: island gaps 3 px instead of 15 px, bake margin 12 px. Thin parts (ribs, rails, rigging)
# then get enough texels; with the old gaps some 2 x 2 px islands caught no texel centre and baked black.
_bv3 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_v3.py")).read()
_bm = _bv3[_bv3.index("def bake_model("):_bv3.index("def finish_material(")]
_bm = _bm.replace("island_margin=0.03", "island_margin=0.006").replace("margin = 6", "margin = 12").replace("margin=6", "margin=12")
exec(compile(_bm, "build_v3.py:bake_model (m345 margins)", "exec"), globals())
