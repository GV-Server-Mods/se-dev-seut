---
name: se-dev-seut
description: >-
  Use this skill whenever you model, set up, check, or export a Space Engineers (version 1) block, subpart, or
  prop in Blender with the Space Engineers Utilities (SEUT) addon: SEUT scene and collection setup, grid scale and
  bounding box, armor and functional block geometry, UV layout, reusing vanilla SE materials and texture atlases
  instead of baking new textures, collision (HKT) objects, LODs and build stages, mountpoints, mirroring,
  subpart and dummy empties, turret and weapon models (ConveyorSorter, WeaponCore, ToolCore), interaction
  highlights, emissive and paintable materials, and SEUT error codes (E0xx / W0xx). Also covers driving a live
  Blender through the Blender MCP (execute_blender_code, look, get_scene_info): hard-surface modeling with
  bmesh and modifiers, working from reference images, and visual checking. Use it even when the user only says
  "make a block", "armor piece", "turret model", "SE model", "model this from the picture", "export to MWM",
  or "why does SEUT say E032", and not SEUT by name.
license: MIT
allowed-tools: Read
---

# SEUT block modeling (Space Engineers 1, Blender 4.x)

SEUT turns a Blender scene into an `.mwm` model plus an SBC block definition. The game ignores Blender's
look: shape, UVs, material *name*, collision, bounding box and empties are what ship. Model for those.

Tags: **[HARD]** read in SEUT source or the wiki. **[SOFT]** inferred or field-tested, verify before relying on it.
Everything below was checked against SEUT 1.2.1 on Blender 4.5 unless marked "unverified".

## Workflow

1. **Scene.** Create a Blender scene, set `scene.seut.sceneType = 'mainScene'`, `subtypeId`, `gridScale`
   (`'large'` or `'small'`), then `bpy.ops.scene.recreate_collections()`. Setting `subtypeId` renames the
   scene to match, so look the scene up again by its new name. Recipes: `references/bpy-recipes.md`.
2. **Size the block first.** Cell edge is 2.5 m (large) or 0.5 m (small) [HARD, `seut_bbox.py`].
   `bBox_X/Y/Z` are in cells. Origin is the block centre, so a 1x1x1 large block spans +-1.25 m.
   Keep the model in metres at export scale 1.0 unless the user says otherwise.
3. **Model into `Main (<SubtypeId>)`.** One top-level (unparented) object per exported collection
   [HARD, E031]; parent detail objects under it. Details: `references/modeling-rules.md`.
4. **UVs, then material.** Link a vanilla material from the SEUT material library and lay UVs onto its
   atlas. Do not bake. Details: `references/materials.md`.
5. **Collision** in `Collision - Main (...)`: at most 10 convex objects, inside the bounding box, rigid
   body shape Box / Sphere / Capsule / Cylinder / Convex Hull. `references/modeling-rules.md`.
6. **LODs and build stages** (`LOD1..3`, `BS1..3`), then mountpoints and mirroring if the block needs them.
7. **Check before export.** Run the checklist in `references/errors.md`; most failures are UVs,
   non-ASCII names, unapplied collision modifiers, or geometry outside the bounding box.
8. **Export** (`scene.export`) needs a saved .blend, a mod path and an `...\Models\...` export folder.
   Export has not been run in this skill's tests yet (unverified); say so rather than claiming it works.

## Driving the live Blender (MCP)

The user's real Blender session is the workspace, and every call changes their file. Work in small,
checkable steps and leave the scene tidy.

1. `get_addon_status` once (Blender version, add-on match), then `get_scene_info`.
2. Plan from dimensions and the reference before writing geometry. With a picture, read
   `references/reference-images.md` first: extract proportions into a dimension table, then build to it.
3. One change per script; print only what you need (names, counts, dimensions).
4. `look` after each meaningful change: `mode=angles` with `views` for shape, `shading=wireframe` for
   topology, `max_size` 400-512 for quick checks. Compare with the reference, fix the largest difference first.
5. Build new work in its own scene; do not delete or reshuffle the user's objects unless asked.

Script hygiene:
- Look shader nodes up by `type`, never by name (names are localized). Read enum values from `bl_rna`
  instead of hardcoding them.
- Prefer `bmesh` and the data API; operators like `modifier_apply` need the object active and selected.
- After `bmesh.to_mesh`, call `bm.free()`; return to Object Mode before reading mesh data.
- Setting a name-synced property (SEUT SubtypeId) renames the datablock; look it up again by its new name.
- Apply scale before rigid bodies, mirror modifiers or normal edits. Switch scenes with
  `bpy.context.window.scene = sc`; `look` shows the active scene.
- Never print a mesh's material list or every custom property of an imported FBX: tens of thousands of
  characters. Print counts, then a short slice.
- Study vanilla imports in a throwaway scene, then delete the scene, objects, meshes, images and unused
  materials (materials only drop after their meshes are removed). Raw `bpy.ops.import_scene.fbx` makes
  thousands of junk material slots; SEUT's importer is cleaner.

Hard-surface build order and bmesh and modifier snippets: `references/hard-surface.md`.

Asset libraries (`search_assets`, `import_asset`) and generators (`generate_3d`: Tripo, Hunyuan3D, Hyper3D,
Meshy) are off until the user enables them, and generation can cost credit. Generated meshes are triangulated
with unique baked textures at arbitrary scale, so they do not fit SE's grid or shared atlases; use them as
shape reference at most, and ask before spending credit.

## Rules that fail silently or late

- **UV-less or all-at-(0,0) UVs crash the game** [HARD, E032/E042]. Every mesh needs a real UV map.
- **ASCII only** in SubtypeId, material and object names [HARD, E033] or no MWM is written.
- **Collision outside the bounding box** makes the game fall back to cube collision [HARD, wiki].
- **Concave collision** gets filled in by Havok; split it into convex pieces [HARD, wiki].
- **Collision shapes ignore rotation.** Apply transforms, then add the rigid body; redo it after any edit
  [HARD, wiki]. Collision loads at game start, so restart the game to see changes.
- **Custom shader node trees are ignored** and flagged (E053). Appearance comes from texture files plus
  the SEUT technique and parameters only [HARD].
- **One collision model per block.** Separate Main and BS collision models misbehave [HARD, wiki].
- **Mountpoint areas** are axis aligned, unrotated, trimmed to the bounding box, and never diagonal [HARD].
- **Mirroring is rotation based**, 90-degree steps from Keen's fixed list; an asymmetric block needs a
  separate mirror-model scene [HARD, wiki].

## Reusing SE textures

The user wants to reuse existing SE textures rather than bake new ones. SEUT already ships 165 linkable
vanilla materials in `<SEUT Assets>\Materials\Materials.blend` (marked Vanilla, no new DDS files needed).
Pick a material from `references/vanilla-materials.md`, link it (`link=True`), and move UV islands over the
atlas region you want. A model that uses only vanilla textures ships no textures of its own.

## Decals before geometry (owner preference)

Before modelling a surface detail in 3D (panel line, vent, hazard stripe, label, rivet row, button),
check whether a vanilla decal material already gives that look: `DECAL_CUTOUT` materials such as
`PanelingColorable`, `Atlas*`, `ButtonsAtlas_*`, `TextAtlas`, `Decals`. Use a decal quad on the surface when
one fits, and spend real geometry only on shape that has to read in the silhouette, catch light at
grazing angles, or affect collision. Decals cost almost nothing in triangles and keep blocks cheap and
consistent with vanilla. Say which decal you chose and why geometry was needed when you skip one.
Decal quads sit just off the surface (not coplanar) to avoid z-fighting [SOFT, confirm the offset used by
vanilla blocks before fixing a number].

## Interaction points highlight real geometry (owner preference)

Terminals, inventories, keypads and conveyor ports get a detector empty linked to a separate mesh
(the screen panel, keypad or port frame), so aiming at them outlines that part instead of a bare box.
Model the part as its own object, then use `add_highlight_empty`. Details and the vanilla small cargo
container breakdown: `references/interaction-highlights.md`.

## Reference files

| File | Read it when |
|---|---|
| `references/hard-surface.md` | building geometry: blockout, cuts, bevels, topology checks, bmesh snippets |
| `references/reference-images.md` | the user supplies a picture, blueprint or photo to match |
| `references/bpy-recipes.md` | scripting scenes, collections, materials, collision through the Blender MCP |
| `references/modeling-rules.md` | geometry, bevels and normals, collision, LOD, build stages, empties, mountpoints, mirroring |
| `references/materials.md` | picking or creating materials, texture types, techniques, atlas UV workflow |
| `references/materials-catalog.md` | choosing a material by behaviour: paintable, decal, or emissive and state-driven glow; emissive presets and colours |
| `references/vanilla-materials.md` | choosing one of the 165 vanilla materials by name |
| `references/block-scenes.md` | laying out Main, LODs, build stages and collision for a complete block; vanilla LOD distances |
| `references/weapons-turrets.md` | turrets, weapons or tools (ConveyorSorter, WeaponCore, ToolCore): subpart chain, muzzle and camera dummies |
| `references/interaction-highlights.md` | any terminal, inventory, keypad, conveyor port or door interaction point |
| `references/errors.md` | any SEUT error or warning, and the pre-export checklist |
| `references/sources.md` | where each fact came from, and what is still unverified |
