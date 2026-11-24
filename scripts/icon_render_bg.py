"""SEUT-style block icon rendered in a background Blender, so no preview window opens in the user's Blender.

Rebuilds SEUT's icon rig (seut_icon_render.setup_icon_render, SEUT 1.2.1) with the data API from the scene's saved
SEUT render settings (renderZoom, renderDistance, renderEmptyLocation/Rotation, renderColorOverlay,
renderResolution), renders only the Main collection, and writes a PNG. Convert it with SEUT's texconv preset:
    texconv.exe <png> -ft DDS -f BC7_UNORM_SRGB -pmalpha -srgb -y -o <dir>
The saved .blend is read, never written, so the options below change only this render.

    blender.exe -b <file.blend> --python icon_render_bg.py -- <out.png> [resolution] [SubtypeId] [--subparts] [--fit [FILL]]

--subparts   instance every subpart empty to its subpart scene's Main collection, so a turret shows whole
             (SEUT's own renderer shows the base only).
--fit FILL   ignore the saved zoom and empty location: centre the model and scale it so its longest side fills FILL
             of the frame (above 0, at most 1; default 0.9, Keen's icons fill about 0.77), measured from small test
             renders. The saved rotation still sets the angle.

Works on Blender 4.x (scene.node_tree compositor, as SEUT) and 5.x (compositing_node_group; the Composite and
MixRGB nodes are gone; the engine is BLENDER_EEVEE again). The Render Layers node is pointed at the icon scene:
left alone it renders the file's active scene, which in a turret file can be a subpart scene ("no camera").
"""
import bpy, sys, math, os
from mathutils import Euler, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
pos, FIT, i = [], None, 0
while i < len(argv):                       # positional args; flags and the --fit value are skipped
    a = argv[i]
    if a == "--fit":
        FIT = 0.9
        if i + 1 < len(argv):
            try:
                FIT = float(argv[i + 1]); i += 1
            except ValueError:
                pass
    elif not a.startswith("--"):
        pos.append(a)
    i += 1
OUT = pos[0]
RES = int(pos[1]) if len(pos) > 1 else None
SUB = pos[2] if len(pos) > 2 else None
B5 = bpy.app.version >= (5, 0, 0)

if FIT is not None and not 0 < FIT <= 1:
    sys.exit("--fit FILL is a fraction of the frame, above 0 and at most 1 (got %g)" % FIT)

sc = next(s for s in bpy.data.scenes if s.seut.sceneType == "mainScene" and (SUB is None or s.seut.subtypeId == SUB))
# The other scenes stay: --subparts needs the subpart scenes, and the Render Layers node is pointed at this scene
# below (left alone it renders the file's active scene: "Cannot render, no camera").
s = sc.seut
d = s.renderDistance
MAIN = "Main (%s)" % s.subtypeId

if "--subparts" in argv:
    mains = {c.seut.scene.name: c for c in bpy.data.collections
             if getattr(c.seut, "col_type", "") == "main" and c.seut.scene is not None}
    for o in bpy.data.objects:
        ls = getattr(o.seut, "linkedScene", None) if o.type == "EMPTY" else None
        if ls is not None and ls.name in mains:
            o.instance_type = "COLLECTION"
            o.instance_collection = mains[ls.name]


col = bpy.data.collections.new("Render (icon bg)")
sc.collection.children.link(col)


def obj(name, data, loc, rot, parent):
    o = bpy.data.objects.new(name, data)
    col.objects.link(o)
    o.location, o.rotation_euler, o.parent = loc, Euler(rot), parent
    return o


empty = obj("Icon Render", None, tuple(s.renderEmptyLocation), tuple(s.renderEmptyRotation), None)
empty.scale = (d, d, d)
cam_data = bpy.data.cameras.new("ICON")
cam_data.lens = s.renderZoom
sc.camera = obj("ICON", cam_data, (0.0, -15.0, 0.0), (math.radians(90), 0, 0), empty)
for name, kind, loc, rot, e in (("Key Light", "POINT", (-12.5, -12.5, 5.0), (0, 0, 0), 7500.0),
                                 ("Fill Light", "POINT", (10.0, -10.0, -2.5), (0, 0, 0), 5000.0),
                                 ("Rim Light", "SPOT", (0.0, 15.0, 0.0), (math.radians(-90), 0, 0), 10000.0)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = e * d
    obj(name, ld, loc, rot, empty)


def walk(lc):
    """Exclude every layer collection except Main, its parents and the rig."""
    keep = lc.name in (MAIN, col.name) or any(c.name == MAIN for c in lc.collection.children_recursive)
    lc.exclude = not keep
    if keep and lc.name != MAIN:
        for c in lc.children:
            walk(c)


for c in sc.view_layers[0].layer_collection.children:
    walk(c)
for o in sc.collection.objects:
    o.hide_render = True

r = sc.render
try:
    r.engine = "BLENDER_EEVEE_NEXT"        # Blender 4.2 - 4.5
except TypeError:
    r.engine = "BLENDER_EEVEE"             # 5.x
r.film_transparent = True
r.resolution_percentage = 100
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGBA"


def alpha_box(path, n):
    """alpha bounding box of a rendered n x n PNG as fractions (u0, u1, v0, v1), v from the bottom"""
    im = bpy.data.images.load(path, check_existing=False)
    px = im.pixels[:]
    bpy.data.images.remove(im)
    xs, ys = [], []
    for y in range(n):
        hit = [x for x, a in enumerate(px[(y * n) * 4 + 3:((y + 1) * n) * 4:4]) if a > 0.02]
        if hit:
            xs += (hit[0], hit[-1]); ys.append(y)
    if not xs:
        return None
    return min(xs) / n, (max(xs) + 1) / n, min(ys) / n, (max(ys) + 1) / n


if FIT:
    # Small test renders without compositing; each one moves the empty across the view by the box's offset and
    # scales the lens by the fill error. Instanced subparts are measured as they render.
    N = 128
    tmp = os.path.splitext(OUT)[0] + "_fit_tmp.png"
    r.resolution_x = r.resolution_y = N
    r.use_compositing = False
    r.filepath = tmp
    for _ in range(8):
        bpy.ops.render.render(write_still=True, scene=sc.name)
        box = alpha_box(tmp, N)
        if box is None:
            break
        u0, u1, v0, v1 = box
        du, dv, ext = (u0 + u1) / 2 - 0.5, (v0 + v1) / 2 - 0.5, max(u1 - u0, v1 - v0)
        if abs(du) < 0.006 and abs(dv) < 0.006 and abs(ext - FIT) < 0.012:
            break
        sc.view_layers[0].update()
        mw = sc.camera.matrix_world
        right, up = mw.col[0].xyz.normalized(), mw.col[1].xyz.normalized()
        width = 2 * (mw.translation - empty.matrix_world.translation).length * (cam_data.sensor_width / 2) / cam_data.lens
        empty.location = Vector(empty.location) + right * du * width + up * dv * width
        cam_data.lens *= FIT / ext
    if os.path.exists(tmp):
        os.remove(tmp)

# SEUT's compositor tree. 4.x: scene.node_tree with a Composite node so write_still saves it. 5.x: a compositor
# node group with a Group Output; MixRGB became the generic Mix node (Factor 1, as the compositor MixRGB default).
if B5:
    t = bpy.data.node_groups.new("Icon (bg)", "CompositorNodeTree")
    t.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    sc.compositing_node_group = t
else:
    sc.use_nodes = True
    t = sc.node_tree
    t.nodes.clear()
N_ = lambda k: t.nodes.new(type=k)
rl, cc, bw, comb, rgb, bc = (N_("CompositorNodeRLayers"), N_("CompositorNodeColorCorrection"),
                             N_("CompositorNodeRGBToBW"), N_("CompositorNodeCombineColor"),
                             N_("CompositorNodeRGB"), N_("CompositorNodeBrightContrast"))
rl.scene = sc                              # else it renders the file's active scene (a subpart scene in a turret file)
L = t.links.new
L(rl.outputs[0], cc.inputs[0])
L(cc.outputs[0], bw.inputs[0])
for i in range(3):
    L(bw.outputs[0], comb.inputs[i])
L(rl.outputs[1], comb.inputs[3])
if B5:
    mix, out = N_("ShaderNodeMix"), N_("NodeGroupOutput")
    mix.data_type = "RGBA"
    mix.blend_type = "COLOR"
    mix.inputs[0].default_value = 1.0
    ins = [x for x in mix.inputs if x.enabled]           # Factor, A, B
    L(comb.outputs[0], ins[1])
    L(rgb.outputs[0], ins[2])
    L(next(x for x in mix.outputs if x.enabled), bc.inputs[0])
    L(bc.outputs[0], out.inputs[0])
    gains = [x for x in cc.inputs if x.name == "Gain"]   # master, highlights, midtones, shadows
    gains[2].default_value, gains[3].default_value = 2.0, 2.5
else:
    mix, comp = N_("CompositorNodeMixRGB"), N_("CompositorNodeComposite")
    mix.blend_type = "COLOR"
    L(comb.outputs[0], mix.inputs[1])
    L(rgb.outputs[0], mix.inputs[2])
    L(mix.outputs[0], bc.inputs[0])
    L(bc.outputs[0], comp.inputs[0])
    cc.midtones_gain, cc.shadows_gain = 2.0, 2.5
rgb.outputs[0].default_value = (0.23074, 0.401978, 0.514918, 1)
bc.inputs[1].default_value = bc.inputs[2].default_value = 0.35
for n in (rgb, bw, comb):
    n.mute = s.renderColorOverlay

r.resolution_x = r.resolution_y = RES or s.renderResolution
r.use_compositing = True
r.filepath = OUT
bpy.ops.render.render(write_still=True, scene=sc.name)
box = alpha_box(OUT, r.resolution_x) if FIT else None
fill = "" if box is None else " fill %.2f, centre offset %+.3f %+.3f" % (
    max(box[1] - box[0], box[3] - box[2]), (box[0] + box[1]) / 2 - 0.5, (box[2] + box[3]) / 2 - 0.5)
print("ICON", OUT, r.resolution_x, round(cam_data.lens, 1), d, tuple(s.renderEmptyRotation), s.renderColorOverlay, fill)
