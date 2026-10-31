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
- Design style section: owner-supplied community ship-building advice, adapted, tagged SOFT.

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

- Crate 2 in game (owner): all tests passed except LOD. At 50 m the yellow conveyor-port frames were missing (first guessed to be `Decals` faces lost to a global decimate; a rebuild with decals protected still lost the ports at 50 m, and the real cause was that all `detector_*` meshes, which carry the yellow port frames and keypads, had been left out of both LODs; rebuilt with them included, not yet seen in game); a further, light-blue silhouette stage appeared beyond LOD2 and is unexplained. Vanilla `CargoContainerSmall` LODs read from the SDK (5 m near-full, 60 m 12-face box with a baked material).

## Not yet verified

- In-game checks still open: the armor-style UV density (about 0.05 UV/m is extrapolated), a second functional block for the 0.40 UV/m figure, LOD switching, build stages in game, the SEUT-rendered icon in game, inventory on a `CubeBlock` via entity components, and subparts/turrets.
- Confirmed in game by the owner (probe cube): the exported mod loads with no mod errors, the highlight outlines the linked mesh, a 2.5 m collision box matches the model, paint and vanilla materials work, the keypad panel maps correctly, and `IsAirTight` in the SBC clears the BuildInfo hint.
- Export of LODs, build stages and subparts; only a Main plus collision model was exported. The `new` SBC was generated but not loaded in game; `update` was not run.
- Mirroring and mountpoint operators driven from script.
- Atlas region descriptions for small pieces (Atlas2 labels, ButtonsAtlas, Atlas3); boxes are measured, the names were read by eye and need a second look.
- Dummy and preset subpart names; subpart workflow.
- Behaviour on SEUT 1.2.2-alpha / Blender 5.x.
