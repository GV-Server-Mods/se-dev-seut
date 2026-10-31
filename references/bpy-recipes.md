# bpy recipes for SEUT (verified on SEUT 1.2.1, Blender 4.5)

Run these through `execute_blender_code`. Work in small steps and print what changed.

## Scene and collections [verified]

```python
import bpy
sc = bpy.data.scenes.new("tmp")
bpy.context.window.scene = sc
s = sc.seut
s.sceneType = 'mainScene'      # also 'subpart', 'character', 'character_animation', 'planet_editor' (read the enum, don't trust this list)
s.subtypeId = "MyBlock"        # ASCII only; renames the scene to "MyBlock"
s.gridScale = 'large'          # or 'small'
s.bBox_X, s.bBox_Y, s.bBox_Z = 1, 1, 1   # in grid cells, not metres
bpy.ops.scene.recreate_collections()
sc = bpy.data.scenes["MyBlock"]          # the scene was renamed
```

Collections created for a main scene (SubtypeId in brackets): `Main`, `Collision - Main`, `LOD1..LOD3`
(`LOD distance` 25 / 50 / 100 by default, each doubling), `BS1..BS3`, `BS1_LOD1`, plus the view layer
named `SEUT`. Find them by type, never by display name:

```python
def seut_col(sc, col_type, index=0, ref=None):
    for c in bpy.data.collections:
        if c.seut.scene is sc and c.seut.col_type == col_type and c.seut.type_index == index and (ref is None or c.seut.ref_col == ref):
            return c
main = seut_col(sc, 'main')
hkt  = seut_col(sc, 'hkt', 1, main)      # collision for Main has type_index 1
```

`col_type` values: `seut main hkt lod bs mountpoints mirroring render`. Data lives in `col.seut`
(`lod_distance`, `ref_col`, `type_index`).

## Mesh into Main, bevel, UV, material [verified]

```python
import bmesh
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.5)      # large cell
me = bpy.data.meshes.new("Armor"); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("Armor", me); main.objects.link(ob)
bpy.context.view_layer.objects.active = ob
# modifier_apply needs the object selected and active
```

Apply modifiers (Bevel, Mirror) before export or collision: unapplied modifiers on collision objects are
E034. Use `uv.smart_project` only as a starting point; real blocks need islands placed on atlas regions.

## Link a vanilla material [verified]

```python
path = r"C:\SE_Assets\Materials\Materials.blend"    # <SEUT Assets>\Materials; read the real path from preferences
with bpy.data.libraries.load(path, link=True) as (src, dst):
    dst.materials = [n for n in src.materials if n == "PaintedMetal_Colorable"]
ob.data.materials.append(bpy.data.materials["PaintedMetal_Colorable"])
```

Linked materials are read-only. Textures resolve relative to the library
(`//..\Textures\Models\Cubes\<name>.TIF`), so keep the library in `<SEUT Assets>\Materials`.
Preferences: `bpy.context.preferences.addons['space-engineers-utilities'].preferences` has `asset_path`,
`game_path`, `havok_path`, `mwmb_path`, `quick_tools`.

## Collision object [verified]

```python
col = bpy.data.objects.new("Collision1", bpy.data.meshes.new("c1"))
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.45); bm.to_mesh(col.data); bm.free()   # slightly under the block
hkt.objects.link(col)
bpy.context.view_layer.objects.active = col
bpy.ops.object.select_all(action='DESELECT'); col.select_set(True)
bpy.ops.rigidbody.object_add()
col.rigid_body.collision_shape = 'BOX'      # BOX, SPHERE, CAPSULE, CYLINDER, CONVEX_HULL only
```

Apply scale and rotation first, because the rigid body does not follow them afterwards.

## Export through the MCP [HARD, tested on SEUT 1.2.1, Blender 4.5]

`scene.export` polls for a 3D viewport in Object mode, which the MCP does not give by default, so override the
context. The .blend must be saved, and the Mod folder and Export Folder must exist (the folder must contain
`Models\`).

```python
s = scn.seut
s.mod_path = r"<mod folder>"; s.export_exportPath = r"<mod folder>\Models\Cubes\large"
s.export_sbc_type = 'none'            # 'update' / 'new' also write the CubeBlocks SBC
s.export_deleteLooseFiles = False     # keep *.mwm.log and *.hkt.*.log while debugging; True for the final run
win = bpy.context.window
area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
with bpy.context.temp_override(window=win, area=area, region=region, scene=scn):
    result = bpy.ops.scene.export()
```

- `export_sbc_type = 'new'` writes `Data\CubeBlocks\<SubtypeId>.sbc` (`I004`) [HARD, tested]: TypeId `CubeBlock`,
  Size from the bounding box, Model path, one `SteelPlate` x10 component, a placeholder icon
  (`AstronautBackpack.dds`), and `{LOC:DisplayName_<SubtypeId>}` / `{LOC:Description_<SubtypeId>}` names that
  show as raw text in game unless a localization file supplies them. No mount points or build-stage models are
  written. Edit the SBC for real blocks. [SOFT: whether this alone makes the block appear in the G menu.]
- A clean run ends with `I007` and leaves only `<SubtypeId>.mwm` when `export_deleteLooseFiles` is True.
- `{'FINISHED'}` is returned even when `E044` was reported. Read the Notifications output, and keep the logs
  to find the cause.
- Tools used: `FBXImporter.exe` ships inside the add-on (`tools\`), `MwmBuilder.exe` and Havok come from
  Addon Preferences. Havok warning `Calculated 'extra radius' for box shape is 0` is harmless.
- Check the result by searching the `.mwm` bytes: `Dummies` with your `detector_*` names and a `highlight`
  user property, `HavokCollisionGeometry`, and the material names.

## Operators seen in the addon source (signatures tested only where noted)

`scene.recreate_collections`, `scene.create_collection`, `scene.add_mountpoint_area`, `scene.add_dummy`,
`scene.add_preset_subpart`, `scene.add_custom_subpart`, `object.add_highlight_empty` (tested, see
`interaction-highlights.md`), `object.create_material`, `object.remapmaterials`, `wm.import_materials`,
`wm.convert_textures`, `scene.export` (tested, above), `scene.export_all_scenes`, `scene.export_materials`,
`scene.import_complete`,
`quicktools.add_bevels`, `quicktools.remove_bevels`, `quicktools.apply_transforms`,
`quicktools.mirror_apply`, `quicktools.origin_to_selected`, `quicktools.cut_and_solidify`,
`quicktools.apply_construction_material`, `scene.update_subpart_instances`.

Mirroring and mountpoint modes are toggles on `scene.seut` (`mirroringToggle`, `mountpointToggle`); the
wiki says turning the mode off saves the values. Not yet exercised through the MCP.
