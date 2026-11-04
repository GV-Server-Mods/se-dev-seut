"""Drift check for a model built by scripts: rebuild a copy and compare every object with the saved file.

Run it on a copy, in a background Blender, so the user's open file is never touched:

    copy model.blend check.blend
    blender -b check.blend --python rebuild_check.py -- <out_dir> <text.py:function> [<scene>]

<text.py:function> names the rebuild entry point in a text block saved in the .blend (for example
`build_all.py:run`); it must rebuild every scripted part. Save the file in the pose the rebuild leaves it in.
Writes <out_dir>/rebuild_report.txt and the rebuilt copy <out_dir>/rebuilt.blend. Every object in the scene (all
scenes when none is given) is compared: type, parent, collections, hide flags, face and vertex counts, materials,
modifiers and their main settings, smooth faces, sharp edges, UVs, custom properties, and the farthest any vertex
moved (in both directions, world space). "Identical" means all equal and no vertex moved more than 0.1 mm.
To prove the rebuild repeats, run the check again on rebuilt.blend: every object must come out identical.
"""
import bpy, sys, os, time, hashlib, traceback
from mathutils import kdtree

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT, ENTRY = ARGS[0], ARGS[1]
SCENES = [bpy.data.scenes[ARGS[2]]] if len(ARGS) > 2 else list(bpy.data.scenes)
KEYS = ("width", "segments", "angle_limit", "limit_method", "weight", "keep_sharp", "mode", "harden_normals",
        "offset_type", "profile", "use_clamp_overlap", "miter_outer")


def mod_sig(m):
    sig = [m.type, m.show_viewport, m.show_render]
    for k in KEYS:
        if hasattr(m, k):
            v = getattr(m, k)
            sig.append((k, round(v, 5) if isinstance(v, float) else str(v)))
    return sig


def digest(items):
    return hashlib.md5(repr(sorted(items)).encode()).hexdigest()[:10]


def snap():
    out = {}
    for sc in SCENES:
        for o in sc.objects:
            d = dict(type=o.type, parent=o.parent.name if o.parent else None,
                     mw=[round(x, 5) for r in o.matrix_world for x in r],
                     cols=sorted(c.name for c in o.users_collection), hide=(o.hide_viewport, o.hide_render))
            if o.type == 'MESH':
                me, mw = o.data, o.matrix_world
                d.update(faces=len(me.polygons), nverts=len(me.vertices), verts=[tuple(mw @ v.co) for v in me.vertices],
                         mats=[m.name if m else None for m in me.materials], mods=[mod_sig(m) for m in o.modifiers],
                         smooth=sum(p.use_smooth for p in me.polygons),
                         matidx=digest([(p.material_index, round(p.area, 4)) for p in me.polygons]))
                sh = me.attributes.get("sharp_edge")
                d["sharp"] = sum(1 for a in sh.data if a.value) if sh else 0
                uv = me.uv_layers.active
                d["uv"] = digest([(round(l.uv.x, 4), round(l.uv.y, 4)) for l in uv.data]) if uv else None
                d["props"] = sorted(o.keys())
            out[(sc.name, o.name)] = d
    return out


def far(a, b):
    if not a or not b:
        return 0.0 if not a and not b else float("inf")
    kd = kdtree.KDTree(len(b))
    for i, v in enumerate(b):
        kd.insert(v, i)
    kd.balance()
    return max(kd.find(v)[2] for v in a)


before = snap()
text, func = ENTRY.split(":")
t0 = time.time()
try:
    getattr(bpy.data.texts[text].as_module(), func)()
    status = f"ok    {ENTRY}  {time.time() - t0:.1f} s"
except Exception:
    status = f"FAIL  {ENTRY}\n" + traceback.format_exc()
after = snap()

gone, new = sorted(set(before) - set(after)), sorted(set(after) - set(before))
same, changed = [], []
for k in sorted(set(before) & set(after)):
    b, a = before[k], after[k]
    diffs = []
    for key in ("type", "parent", "cols", "hide", "faces", "nverts", "mats", "mods", "smooth", "matidx", "sharp", "uv",
                "props"):
        if b.get(key) != a.get(key):
            diffs.append(f"{key} {b.get(key)} -> {a.get(key)}" if key in ("faces", "nverts", "smooth", "sharp")
                         else ("modifiers" if key == "mods" else key))
    if b["type"] == 'MESH':
        move = max(far(a["verts"], b["verts"]), far(b["verts"], a["verts"]))
        if move > 1e-4:
            diffs.append(f"moved up to {move * 1000:.1f} mm")
    elif b["mw"] != a["mw"]:
        diffs.append("transform")
    (changed.append(f"{k[0]} / {k[1]}: " + "; ".join(diffs)) if diffs else same.append(k))
name = lambda k: f"{k[0]} / {k[1]}"
lines = [status, "", f"Objects: saved {len(before)}, after rebuild {len(after)}", f"Identical: {len(same)}",
         f"Different: {len(changed)}", f"Only in the saved file (a rebuild would lose them): {len(gone)}",
         f"Only after the rebuild: {len(new)}", "", "== Different"] + changed
lines += ["", "== Only in the saved file"] + [name(k) for k in gone] + ["", "== Only after the rebuild"]
lines += [name(k) for k in new]
with open(os.path.join(OUT, "rebuild_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "rebuilt.blend"))
print("\n".join(lines[:8]))
