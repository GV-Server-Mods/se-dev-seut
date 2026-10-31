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

## Not yet verified

- In-game checks still open: the armor-style UV density (about 0.05 UV/m is extrapolated), a second functional block for the 0.40 UV/m figure, LOD switching, build stages, and icon generation (SEUT does not make one).
- Confirmed in game by the owner (probe cube): the exported mod loads with no mod errors, the highlight outlines the linked mesh, a 2.5 m collision box matches the model, paint and vanilla materials work, the keypad panel maps correctly, and `IsAirTight` in the SBC clears the BuildInfo hint.
- Export of LODs, build stages and subparts; only a Main plus collision model was exported. The `new` SBC was generated but not loaded in game; `update` was not run.
- Mirroring and mountpoint operators driven from script.
- Atlas region descriptions for small pieces (Atlas2 labels, ButtonsAtlas, Atlas3); boxes are measured, the names were read by eye and need a second look.
- Dummy and preset subpart names; subpart workflow.
- Behaviour on SEUT 1.2.2-alpha / Blender 5.x.
