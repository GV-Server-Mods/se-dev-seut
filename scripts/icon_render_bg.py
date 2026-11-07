"""SEUT-style block icon rendered in a background Blender, so no preview window opens in the user's Blender.

Rebuilds SEUT's icon rig (seut_icon_render.setup_icon_render, SEUT 1.2.1) with the data API from the scene's saved
SEUT render settings (renderZoom, renderDistance, renderEmptyLocation/Rotation, renderColorOverlay,
renderResolution), renders only the Main collection, and writes a PNG. Convert it with SEUT's texconv preset:
    texconv.exe <png> -ft DDS -f BC7_UNORM_SRGB -pmalpha -srgb -y -o <dir>
Subparts are not instanced (same as SEUT's renderer). The saved .blend is read, never written.

    blender.exe -b <file.blend> --python icon_render_bg.py -- <out.png> [resolution] [SubtypeId]
"""
import bpy, sys, math
from mathutils import Euler

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
RES = int(argv[1]) if len(argv) > 1 else None
SUB = argv[2] if len(argv) > 2 else None
sc = next(s for s in bpy.data.scenes if s.seut.sceneType == "mainScene" and (SUB is None or s.seut.subtypeId == SUB))
s = sc.seut
d = s.renderDistance
MAIN = "Main (%s)" % s.subtypeId

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

# SEUT's compositor tree, with a Composite node so write_still saves it
sc.use_nodes = True
t = sc.node_tree
t.nodes.clear()
N = lambda k: t.nodes.new(type=k)
rl, cc, bw, comb, rgb, mix, bc, comp = (N("CompositorNodeRLayers"), N("CompositorNodeColorCorrection"),
                                        N("CompositorNodeRGBToBW"), N("CompositorNodeCombineColor"),
                                        N("CompositorNodeRGB"), N("CompositorNodeMixRGB"),
                                        N("CompositorNodeBrightContrast"), N("CompositorNodeComposite"))
L = t.links.new
L(rl.outputs[0], cc.inputs[0])
L(cc.outputs[0], bw.inputs[0])
for i in range(3):
    L(bw.outputs[0], comb.inputs[i])
L(rl.outputs[1], comb.inputs[3])
L(comb.outputs[0], mix.inputs[1])
L(rgb.outputs[0], mix.inputs[2])
L(mix.outputs[0], bc.inputs[0])
L(bc.outputs[0], comp.inputs[0])
cc.midtones_gain, cc.shadows_gain = 2.0, 2.5
rgb.outputs[0].default_value = (0.23074, 0.401978, 0.514918, 1)
mix.blend_type = "COLOR"
bc.inputs[1].default_value = bc.inputs[2].default_value = 0.35
for n in (rgb, bw, comb):
    n.mute = s.renderColorOverlay

r = sc.render
r.resolution_x = r.resolution_y = RES or s.renderResolution
r.resolution_percentage = 100
r.engine = "BLENDER_EEVEE_NEXT"
r.film_transparent = True
r.use_compositing = True
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGBA"
r.filepath = OUT
bpy.ops.render.render(write_still=True, scene=sc.name)
print("ICON", OUT, r.resolution_x, s.renderZoom, d, tuple(s.renderEmptyRotation), s.renderColorOverlay)
