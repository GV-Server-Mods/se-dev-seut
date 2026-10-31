# SEUT errors and pre-export checklist

Codes are from `seut_errors.py` in SEUT 1.2.1 [HARD]. The Notifications panel (SEUT main panel, turns red
on error) shows them; `Delete Temporary Files` off keeps `*.mwm.log` for export failures.

## Contents
- Pre-export checklist
- Errors with a fix
- Warnings

## Pre-export checklist

1. .blend saved (E008), SubtypeId set and unique in the file (E004, E018), ASCII names (E033).
2. Every mesh has a valid UV map with real coordinates (E032, E042, W002) and no empty meshes (W013). This
   includes highlight target meshes and collision meshes (collision UVs: E044).
3. Materials: no custom node trees (E053), texture paths contain `Textures\` (E007), valid resolutions (W004).
4. Collision: at most 10 objects (E022), modifiers applied (E034), rigid body shape allowed (E054), no
   external HKT plus objects (E055), all inside the bounding box.
4a. Each `detector_*` empty covers the whole mesh it highlights (aim areas smaller than the mesh leave dead
   spots in game; `references/interaction-highlights.md`).
5. Each exported collection has one unparented top-level object (E031); LOD indexes continuous (E006) and
   distances increasing (E011).
6. Paths: Export Folder contains `Models\` (E014), Mod folder set and model path inside it (E045),
   MwmBuilder and Havok paths valid in Addon Preferences (E012, E013).

## Errors with a fix

| Code | Meaning | Fix |
|---|---|---|
| E002 | SEUT collection missing, excluded or empty | Recreate Collections; include it in the view layer |
| E004 | no SubtypeId | set `scene.seut.subtypeId` |
| E005 | subpart instancing loop | remove the circular subpart link |
| E006 | collection indexes missing | restore the gap (e.g. LOD2 without LOD1) |
| E007 | texture path lacks `Textures\` | move TIF under a `Textures` folder |
| E008 | .blend unsaved | save |
| E011 | LOD distance order wrong | raise the higher LOD's distance |
| E012 / E013 | tool path invalid or wrong file | fix Addon Preferences |
| E014 | export path lacks `Models\` | set Export Folder inside `...\Models\` |
| E017 | FBX exporter RuntimeError | leave Edit Mode, export again |
| E018 | duplicate SubtypeId | rename |
| E022 | over 10 collision objects | merge into convex pieces |
| E023 | mirror empty rotation invalid | try another axis combination |
| E031 | collection has several top-level objects | parent them under one object |
| E032 / E042 | missing or broken UV map | unwrap; UV verts all at (0,0) means broken |
| E033 | non-ASCII characters | rename to ASCII |
| E034 | collision has unapplied modifiers | apply them |
| E037 | Havok `hctFilterManager.dll` not found | install Havok Content Tools 2013 |
| E039 / E050 | Assimp32.dll / VC++ redist missing | install .NET 3.5 SP1, VC++ 2012 x86 |
| E043 / E044 | MWM conversion failed | read `*.mwm.log` (turn `Delete Temporary Files` off first). Seen: `Mesh 'pc' has no UV map/channel` for `<SubtypeId>.hkt.fbx` means a collision mesh has no UVs or all UVs at (0,0): MwmBuilder builds the collision FBX too, so give collision meshes a real UV map (Blender's primitives have one). The main `.mwm` is still written, but without the collision |
| E045 | model path outside mod folder | fix Mod / Export paths |
| E046 | DDS conversion failed | check texture file and `texconv` |
| E053 | custom node tree | use SEUT material; change textures instead |
| E054 | rigid body shape COMPOUND | Box / Sphere / Capsule / Cylinder / Convex Hull |
| E055 | external HKT and objects both present | clear one |

Other codes (E001, E003, E009, E010, E015, E016, E019-E021, E024-E030, E035, E036, E038, E040, E041, E047-E049,
E051, E052) cover import, planets, animation, armatures and tool setup; read the message, it names the target.

## Warnings

| Code | Meaning |
|---|---|
| W001 / W020 | subpart grid size differs from parent / subpart empties cannot export to another grid |
| W002 | many UV verts at (0,0), shading may break |
| W004 | texture resolution not power of two |
| W005-W007 | empty without parent / parent has parent / highlight parent mismatch |
| W012 | DLC material: model must be DLC-locked |
| W013 | object without geometry |
| W014 / W019 | texture slot empty / texture unsupported by the technique |
