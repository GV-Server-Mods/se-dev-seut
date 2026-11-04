# Sources and verification status

## Read in source or checked live (SEUT 1.2.1, Blender 4.5.10, SEUT assets 1.7.3)

- Collection schema, LOD defaults (25 / 50 / 100), `recreate_collections` behaviour: `seut_collections.py`.
- Grid factors 2.5 m / 0.5 m, bounding box drawing: `seut_bbox.py`.
- Error and warning catalog: `seut_errors.py`.
- Scene rename on SubtypeId, linking vanilla materials, `is_vanilla` tags, 165 materials: tested in Blender.
- A 2.5 m bevelled test block with collision box built and rendered through the MCP.

## From the Space Engineers wiki (spaceengineers.wiki.gg), fetched during this session

SEUT overview, Main Panel reference, Material tutorial, Material Library tutorial, Shader Editor reference,
Empty Properties reference, Collisions, Mountpoints and Mirroring tutorials, Materials reference.

## Added later

- Emissive mechanism and presets: `MyCubeBlock.cs`, block classes, `Content\Data\EmissiveColors.sbc`.
- Per-material paint and emissive coverage: measured from `C:\SE_Assets\Textures\Models` TIFs at 128 x 128.
- Highlights and Gatling turret structure: imported SDK FBX files into a throwaway scene.
- LOD distances: SDK `OriginalContent` model XMLs.
- WeaponCore and ToolCore wiki pages (Ash-LikeSnow): Weapon Block Types, Minimal Configuration, Required Files,
  Definition Fields, Turret Fields, Example Turret Definition.
- SEUT dummy and subpart presets: `empties` list in the add-on preferences module.
- Armor UV density: measured (triangle UV area / world area) on ModSDK `OriginalContent` FBX files: `SquarePlate` 0.141 UV/m, `ArmorCenter` 0.40 UV/m. `ArmorCenter` turned out not to be the armor cube's model (see `CubeBlocks_Armor.sbc`), so the 0.40 value was wrong to use; the working value comes from owner observation (about 2x coarser than 0.145).
- Terminal texture layout: read from `terminal_panel_cm.TIF` in the SEUT assets.
- Test cases `armor-cube-bevel-lods`, `beam-with-diagonal-brace` and `reference-blueprint-kitbash` (`evals/`): run by fresh agents reading only the skill, in the live Blender, with files and scene values checked afterwards (scene facts read back in Blender, `.mwm` contents searched byte-wise, the blueprint measured in pixels). All three passed every assertion; the gaps they reported became the multi-piece, collision, LOD, export, SBC, DLC-material, decal, detector and reference-measuring notes. Not run with a no-skill baseline. The owner loaded the probe cube in game; the case 1-3 blocks were not loaded in game when these notes were written.
- DLC material list: `asset_data.seut.is_dlc` read from `Materials.blend` with a background Blender (17 of 165).
- Highlight detector coverage: owner in-game test (aiming outside the empty gives no outline).
- Export recipe and E044 cause: ran `scene.export` on a scratch mod folder with SEUT 1.2.1, Blender 4.5, read `*.mwm.log`, `seut_ot_export.py` and `seut_mwmbuilder.py`.
- Atlas region maps: `_alphamask` textures from the SEUT assets (`Textures\Models\Cubes`), segmented by `scripts/extract_atlas_regions.py`, labelled from `scripts/annotate_atlas.py` previews.

- Case 3 in game (owner): terminal highlight correct; conveyor use checked in code (`MyConveyorLine`, `MyUseObjectInventory`); decal technique counts read from `Materials.blend`; X-panel relief read from the Atlas3 normal map and confirmed by the in-game screenshot; smooth-shading recipe run in Blender 4.5; kitbash import recipe run on `CargoContainerSmall.FBX` (`references/kitbash.md`).

- Rebuilt antenna crate (`TestAntennaCrate`): kitbashed from `CargoContainerSmall.FBX`, exported with 11 detectors, 5 collision shapes, LODs; warnings read from `TestAntennaCrate.mwm.log`. Debug-draw behaviour read in `MyDebugRenderComponentCubeBlock` / `MyDebugRenderComponentTerminal`.

- Wiki Models reference (`spaceengineers.wiki.gg/wiki/Modding/Reference/Models`) and SEUT Interaction Highlights tutorial, fetched later: LOD, dummy, collision and highlight rules in `modeling-rules.md` and `interaction-highlights.md`. The wiki's "Advanced 3D Models" guide is only a pointer to the SEUT page; the official SE2 art guide was not used (different game).
- Design style (now `design-detailing.md`): owner-supplied community ship-building advice, adapted, tagged SOFT,
  plus owner feedback from the gatling turret build. Turret-only points stay in `turret-design.md`. One
  user's personal style calls were later taken out again; where a choice is a matter of taste, the files now
  say to ask the user.
- Kitbash material bug: first recipe lost per-face materials (owner screenshot of the all-yellow port); fixed and re-checked by counting faces per material on the re-imported port frame.

- SEUT wiki hub (`Modding/Tools/Space_Engineers_Utilities`, Tutorials and Reference) all pages now read except the three YouTube videos and the Planet Editor (planet modding, out of scope): Installation Guide, Addon Preferences, Notifications (overview and panel), and Add and Context Menu were read late and folded into `errors.md` and `bpy-recipes.md`.
- Step 4 tests on scratch block `S4Test` (SEUT 1.2.1): MountPoints, BuildProgressModels, MirroringX/Y, `update` mode and the icon path read from the generated SBC; icon rendered and converted to DXT5 DDS. Not yet seen in game.
- Port frame material: the owner saw the vanilla yellow frame clean and the kitbashed one with scratched edges; swapped to `PaintedMetal_Yellow` and re-exported; cause not established (`kitbash.md`).

- Chipstix213's YouTube tutorial series (SEUT setup for Blender 3.0, The First Model, The Next Steps), supplied by the owner as auto-generated transcripts (speech-to-text errors likely, so only claims that make sense against the add-on or game data were kept): install order, first-model workflow, export size options, local test mod folder, world settings for fast testing, icon render mode, inventory through entity components. Credited in `README.md` and `references/setup.md`. SEUT's icon renderer then read in `seut_icon_render.py` and run on `S4Test`; this corrected the earlier claim that SEUT makes no icon. Entity component and container XML checked against the game's `EntityComponents.sbc` and `EntityContainers.sbc` (LockerRoom blocks).

- Chipstix213's Advanced Door (parts 1 and 2), Custom Character and weapon animation controller videos (auto-generated transcripts): `doors-subparts.md` and `characters-and-animation.md`. Advanced door fields checked in the decompiled `MyObjectBuilder_AdvancedDoorDefinition` / `MyAdvancedDoor` (opening fields, `IDs` syntax, subpart model loaded by name beside the main model, subpart physics from collision shapes; no vanilla advanced door exists in `CubeBlocks`); `E051` weight-painting groups and `rotate_character` found in the SEUT source. Not built or loaded in game. Ctrl+Alt+E in-game export tip: owner, credits Brd.

- Subpart, dummy, mirroring and mountpoint operators run from script on scratch scenes `SPTurret` and `SPBarrel` (`bpy-recipes.md`): operator parenting bug found in source and seen in the run; `linkedScene` update callback read in `seut_object.py`; Blender 4.5.10 crashed once when `linkedScene` was set while another object was active (owner supplied `ProbeExport.crash.txt`); safe recipe then exported both scenes and the `subpart_Barrel` dummy with `file = SPBarrel` was found in the main `.mwm`; mirroring and mountpoint modes toggled and the SBC read back. In-game behaviour untested.

- Quick tools, build stage, mountpoint area edits and `update_subpart_instances` probed on `SPTurret` (`bpy-recipes.md`, "Quick tools"): `add_bevels` hard-coded width and `apply_transforms` rigid-body removal read in `seut_quicktools_operators.py` and confirmed by running; `cut_and_solidify` and `apply_construction_material` run and the BS1 export read back (SBC and files); mirror_apply and origin_to_selected read only.

- SEUT importer (`scene.import`, `seut_ot_import.py`) run on `CargoContainerSmall.FBX` into a throwaway scene and compared with the raw FBX import: object, slot and material counts, root scale, highlight links, per-face materials of the port frame, keypad frame, text banner and grey frame, and an unmodified export (W007 from cross-scene name clashes). This explains the owner's clean-vanilla observation; in-game result of the importer's output not checked.

- Small-grid scene exported twice on a scratch scene (default flags, then small flags) and the SBC read back; `mirror_apply` and `origin_to_selected` run on a scratch mesh.

- Second antenna crate `TestAntennaCrate2` rebuilt from SEUT's importer in a fresh .blend: custom parts, collision shapes and the tower terminal detector appended from the first crate, LOD1/LOD2 built by script, exported and installed beside the first crate (`bpy-recipes.md`, "Moving parts between .blend files, LODs from script"). Two Blender crashes traced to iterating a live collection while mutating data (`Crate2.crash.txt`). Export log: 4 identical-UV warnings, source not found. Not yet seen in game; its icon is a copy of the first crate's.

- `scene.import_complete` and `scene.export_all_scenes` run on the crate 2 files (`bpy-recipes.md`): import and size-identical round trip worked, `export_all_scenes` worked with one scene and crashed Blender twice with two (`Crate2.crash.txt`, depsgraph trace). The crash checklist in `errors.md` was then used for real: kill, relaunch from `bpy.app.binary_path`, MCP reconnected on its own, three times. Crate 2's icon rendered with SEUT's renderer (full colour, DX10 BC7 128 x 128, 22,020 bytes) and read back with Pillow; framing was good with the default zoom of 70.

- Crate 2 in game (owner): all tests passed except LOD. At 50 m the yellow conveyor-port frames were missing (first guessed to be `Decals` faces lost to a global decimate; a rebuild with decals protected still lost the ports at 50 m, and the real cause was that all `detector_*` meshes, which carry the yellow port frames and keypads, had been left out of both LODs; rebuilt with them included: the owner confirmed in game that the LODs look right); the light-blue silhouette seen beyond LOD2 was only the time of day and lighting changing, not a model stage. Vanilla `CargoContainerSmall` LODs read from the SDK (5 m near-full, 60 m 12-face box with a baked material).

- Icon render of a three-scene WeaponCore turret (Blender 4.5.10): subparts missing until instanced by hand, `update_subpart_instances` crash on nested subparts, a crash on the fourth render-and-close of a session (`%TEMP%\GatlingTurret.crash.txt`), the crash dialog hanging the MCP, and a Temp autosave reopening after the restart (`bpy-recipes.md` icons step 4, `errors.md`).

- Planning a replacement model for a large twin-barrel WeaponCore turret (design doc written before any modelling): gaps found by a fresh agent reading only the skill, then checked before editing. Subpart orientation: SEUT export axes (`seut_export_utils.py`), an earlier SEUT-built gatling turret's `.blend` read with a background Blender against its exported `.mwm` dummies, and game code (`MyLargeTurretBase.RotateModels`, `MyDoor`, `MyAdvancedDoor`; WeaponCore `WeaponController.AimBarrel`). `.mwm` layout for `scripts/mwm_dummies.py`: `MyModelImporter` (`LoadTagData`, `ReadIndexDictionary`, `ReadDummies`); detector box size from `MyUseObjectsComponent.RecreatePhysics` and `MyOrientedBoundingBoxD`. Recoil: WeaponCore `SessionAnimationMgr.cs` and a shipped turret's `.mwm` files. Subpart highlights: `MyHudSelectedObject.ComputeHighlightIndices`, SEUT `seut_empties.py`. Emissive presets: `MyEmissiveColorPresets.LoadPresetState`, `MyCubeBlock.UsesEmissivePreset`, `EmissiveColors.sbc`. Superfiring: WeaponCore `WeaponTracking.RayCheckTest`, `WeaponTypes.cs`. Weld bead: crops of the A_01 and A_02 colour, normal and alpha textures read with PowerShell `System.Drawing`. `CargoContainerLarge` part names: its SDK FBX. Not seen in game.

- Roof parts of the same turret (a turned sensor dome, a periscope pod, side sensor boxes; Blender 4.5.10): the material index clamp and the exact boolean's one-shell need were hit in runs; the faceted-cylinder outline seam was measured by ray cast; the enlarged-crop reading came after the user rejected a pass read at full size. Not seen in game.

- Shading round on the same turret (Blender 4.5.10): the owner saw a smeared ridge side, soft folds on the
  gunhouse and bustle, and streaked port braces in solid view. Each was measured with the shading check
  (`bpy-recipes.md`), fixed, and measured again, and the views were matched with a Workbench render from the
  owner's viewport. Zero-area faces traced to `bisect_plane` on a convex hull. The fold bevel was rejected
  because decals lie on the folds (2-4 mm drop measured). Not seen in game.
- `pipeline.md`: the stage order and the builder/editor rule came from the same build, where in-place fixes
  had been mirrored into builders that were no longer rerun (owner: "this two sources of truth thing hurts my
  head"). The decal-carrying parts were found by counting decal vertices near each heavy part with
  `BVHTree.find_nearest`; the drift check was run on a rebuilt part, matched it, and flagged a 1 cm shift.
  `scripts/rebuild_check.py` was run on a copy of the same turret in a background Blender (4.5.10): 177 of 183
  objects matched at first; after the fixes it found, the saved file matched its rebuild in all 183 under
  several `PYTHONHASHSEED` values. The face order that varied between sessions was traced by hashing one
  part's face list after each build stage: the input to `bmesh.ops.bevel` was the same every time, its output
  order was not. That a set of BMesh elements is ordered by memory address is inferred, not traced.

## Not yet verified

- In-game checks still open: a turret run by the game's own turret code without WeaponCore (its aiming, barrel
  and muzzle dummies, manual-control camera), subpart facing on a WeaponCore `ConveyorSorter` turret, and
  mirroring. Each matters only when a block of that kind is built. Turret details: `weapons-turrets.md`,
  "Unverified".
- Confirmed in game by the owner on the gatling turret (a vanilla `LargeMissileTurret` type driven by
  WeaponCore; azimuth, elevation and spinning barrel subparts, two LODs per scene): it places and mounts, builds
  through its three stages, and tracks and fires with the subpart facing and dummies set up as in
  `weapons-turrets.md`.
- Confirmed in game by the owner on crate 2 (SEUT importer, LODs by script, SEUT-rendered icon): clean vanilla materials, highlights, conveyor and terminal use, collision, the 11 dummies after a full restart, LOD switching, the icon. LOD levels: a hand-built LOD must keep every material of Main, including the vanilla `detector_*` meshes.
- Confirmed in game by the owner (probe cube): the exported mod loads with no mod errors, the highlight outlines the linked mesh, a 2.5 m collision box matches the model, paint and vanilla materials work, the keypad panel maps correctly, and `IsAirTight` in the SBC clears the BuildInfo hint.
- Atlas region names: every atlas was re-catalogued at full resolution and its boxes and groupings checked against owner markup, but the piece names were read by eye; the X-panel triangle depths come from edge steepness in the normal map.
- Dummy and subpart presets other than the vanilla-type turret names the gatling used; ToolCore subparts.
- Behaviour on SEUT 1.2.2-alpha / Blender 5.x.
