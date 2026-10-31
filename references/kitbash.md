# Kitbash from vanilla models first

When a block should look like a vanilla one (a cargo-style crate, a conveyor frame, a terminal panel, a
door, an armor edge), start from the vanilla model's own parts instead of modelling similar shapes from
scratch. Three reasons [owner request, SOFT]: the parts already carry Keen's bevels, UV density, material
choices and shading; it takes far fewer agent steps than rebuilding them; and the result matches the game's
look without effort. Model from scratch only for shapes that no vanilla part covers.

A model that reuses a vanilla part may reuse only parts, not the whole file: copy the pieces you need
(frame corners, port frame, terminal panel, handle) and leave the rest. Vanilla models are Keen's assets; for
a server mod that is shared or published, check the owner is happy with that [ask, do not assume].

## Where the parts are

`<ModSDK>\OriginalContent\Models\Cubes\large\*.FBX` and `...\small\*.FBX`, each with an `.xml` that lists
the materials and LODs (`C:\Program Files (x86)\Steam\steamapps\common\SpaceEngineersModSDK` on a Steam
install). Find the model a block uses by looking up its SubtypeId in `Content\Data\CubeBlocks\*.sbc` and
reading `<Model>`. Do not guess from the block's name (`ArmorCenter` is not the armor cube).
`CargoContainerSmall` has 55 meshes and 12 empties under one root, about 2.49 m across: six
`LargeConveyorFrame_00n` corner/frame meshes, six `detector_conveyor_section_00n` port frames, six
`detector_terminal_section_00n` panels, and the rest. Read `interaction-highlights.md` for its detectors.

## Import recipe [HARD, tested on SEUT 1.2.1 / Blender 4.5]

Import into a throwaway scene, keep what you want, and clean up. A raw import is messy: it gives every
mesh a slot for every material in the file (about 100), creates the materials as plain local copies, and
leaves thousands of unused materials behind.

```python
import bpy, io, contextlib
FBX = r"<ModSDK>\OriginalContent\Models\Cubes\large\CargoContainerSmall.FBX"
MAT = r"C:\SE_Assets\Materials\Materials.blend"          # <SEUT Assets>\Materials
before = set(bpy.data.objects.keys())
tmp = bpy.data.scenes.new("kb_tmp"); bpy.context.window.scene = tmp
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    bpy.ops.import_scene.fbx(filepath=FBX)                # prints thousands of lines otherwise
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
meshes = [o for o in new if o.type == 'MESH']

# 1. drop the unused material slots on every mesh
for o in meshes:
    me = o.data
    used = sorted({p.material_index for p in me.polygons})
    mats = [me.materials[i] for i in used]
    remap = {old: new_i for new_i, old in enumerate(used)}
    for p in me.polygons: p.material_index = remap[p.material_index]
    me.materials.clear()
    for m in mats: me.materials.append(m)

# 2. swap the local copies for the linked vanilla materials (names match)
names = sorted({m.name for o in meshes for m in o.data.materials if m and not m.library})
with bpy.data.libraries.load(MAT, link=True) as (src, dst):
    dst.materials = [n for n in names if n in src.materials]
linked = {m.name: m for m in bpy.data.materials if m.library}
for o in meshes:
    for i, m in enumerate(o.data.materials):
        if m and not m.library and m.name in linked: o.data.materials[i] = linked[m.name]
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
```

Result in the test: 13 materials used, all 97 slots remapped to linked library materials, none missing,
3131 data blocks purged.

3. Move the parts you keep into the block. The imported root has scale 0.01 (the meshes are in cm), so
   unparent each kept object keeping its world transform, then apply scale:
   `mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw`, then select it and
   `bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`. Link it into `Main (...)`
   with `main.objects.link(o)` and unlink it from the throwaway scene. World size is true metres
   afterwards (a `LargeConveyorFrame` piece measures 2.0 x 0.28 x 2.0 m).
4. Reparent the kept parts under your block's single root object (E031), delete the throwaway scene
   (`bpy.data.scenes.remove`) and purge orphans again.
5. Rename or delete vanilla empties you copy. Their names carry over (`detector_conveyor_5`, and `.001`
   suffixes when the name already exists), and object names are global to the file.

## Kitbash rules

- Take the shell parts first (frames, corners, bevelled edge pieces, port frames, panels, handles), then
  add only what the design needs on top. Keep the vanilla part's materials and UVs as they are.
- Scale a vanilla part only when it must fit a different size, and keep the scale uniform so bevels and
  UV density stay consistent.
- The vanilla parts bring their own bevels and smooth shading. Anything you add yourself must be bevelled
  and smooth shaded the same way (`modeling-rules.md`, "Geometry and shading"), or it will look like a
  different game next to them.
- Vanilla detector empties and their linked meshes come along with the container parts. Keep the pairs
  together, rename them to unused indices, and check each empty covers its mesh
  (`interaction-highlights.md`, "Detector size").
- State in the report which vanilla parts were reused and which shapes had to be built new.

## Not yet tested

- Whether SEUT's own importer (`scene.import_complete`) is a better route than the raw import above. It
  only takes a file path, and no run has compared the two.
- Exporting a block made from kitbashed parts in game (the model exports like any other; only the look was
  not checked).
