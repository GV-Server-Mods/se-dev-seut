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
- Export recipe and E044 cause: ran `scene.export` on a scratch mod folder with SEUT 1.2.1, Blender 4.5, read `*.mwm.log`, `seut_ot_export.py` and `seut_mwmbuilder.py`.
- Atlas region maps: `_alphamask` textures from the SEUT assets (`Textures\Models\Cubes`), segmented by `scripts/extract_atlas_regions.py`, labelled from `scripts/annotate_atlas.py` previews.

## Not yet verified

- In-game checks still open: the armor-style UV density (about 0.05 UV/m is extrapolated), a second functional block for the 0.40 UV/m figure, LOD switching, build stages, and icon generation (SEUT does not make one).
- Confirmed in game by the owner (probe cube): the exported mod loads with no mod errors, the highlight outlines the linked mesh, a 2.5 m collision box matches the model, paint and vanilla materials work, the keypad panel maps correctly, and `IsAirTight` in the SBC clears the BuildInfo hint.
- Export of LODs, build stages and subparts; only a Main plus collision model was exported. The `new` SBC was generated but not loaded in game; `update` was not run.
- Mirroring and mountpoint operators driven from script.
- Atlas region descriptions for small pieces (Atlas2 labels, ButtonsAtlas, Atlas3); boxes are measured, the names were read by eye and need a second look.
- Dummy and preset subpart names; subpart workflow.
- Behaviour on SEUT 1.2.2-alpha / Blender 5.x.
