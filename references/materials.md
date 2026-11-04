# SE materials and texture reuse

## Contents
- Texture types
- Techniques
- Reuse workflow (no baking)
- When a new material is unavoidable

## Texture types [HARD, wiki]

| Suffix | Content | RGB | Alpha |
|---|---|---|---|
| `_cm` | Color / Metalness | base color | metalness |
| `_ng` | Normal / Gloss | tangent normal map | gloss |
| `_add` | Additive | R = AO (white if none), G = emissive, B unused | paintability (whiter takes more paint) |
| `_alphamask` | Alpha mask | white opaque, black transparent | unused |

Transparent materials (GLASS, HOLO, SHIELD) use `_ca` (color + alpha, premultiplied recommended) and `_ng`.
DDS must be power-of-two sides, BC7 recommended. Blender cannot read BC7, so SEUT works from TIF and converts.

## Techniques [HARD, wiki]

`MESH` standard. `DECAL`, `DECAL_NOPREMULT`, `DECAL_CUTOUT` for decal-style surfaces. `ALPHA_MASKED`,
`FOLIAGE`. `GLASS`, `HOLO`, `SHIELD`: material name must equal a TransparentMaterials SubtypeId.
Of the 165 vanilla materials: 117 MESH, 19 DECAL_CUTOUT, 18 GLASS, 7 ALPHA_MASKED, 4 HOLO.

## Reuse workflow (no baking)

All 165 materials in `Materials.blend` are Blender assets tagged `is_vanilla` (checked), so they need no
new textures. Many vanilla blocks share atlases and tiling materials, which is what makes reuse work. So:

1. Choose by name from `vanilla-materials.md`. Armor and structural work usually wants the `*Colorable`
   family (paint colour comes from the ADD alpha channel) or a `PaintedMetal*` variant.
   `Atlas3_Colorable`, `Atlas4_Colorable`, `Atlas1Colorable` are the Cubes atlases;
   `PanelingColorable` / `Decals_Atlas_A_01` is the decal atlas.
2. Link the material from `<SEUT Assets>\Materials\Materials.blend` (`link=True`). Linked, not copied, so
   updates and the Vanilla flag follow it (`references/bpy-recipes.md`).
3. Lay out UVs: scale and place islands over the region of the atlas that has the look you want.
   To find regions, import a vanilla block that uses the atlas (SEUT `Import FBX`, `Complete Import`
   from `<game>\Content\Models\Cubes`) and read its UV islands, or open the TIF in `<SEUT Assets>\Textures\Models\Cubes`.
   Region boxes for the decal and detail atlases are in `references/atlas-regions.md` [SOFT: boxes found by
   script, small-piece descriptions read by eye].
4. Tiling materials (`PaintedMetal_*`, `RustyMetal`, `Rubber*`) take UVs scaled to texel density instead of
   an atlas region. Match vanilla neighbours; the SEUT `UV Grid Overlay` toggle shows texel density [HARD].
   Texture detail size is set by UV per metre: **fewer UVs per metre = bigger features** ("zoom in"). Do not
   take one vanilla number as the target, because each material's texture has its own baked scale.
   **Two scales exist in vanilla** [HARD, owner-observed, `PaintedMetal_Colorable` on a 2.5 m cube, all blocks
   wearing the same concrete skin]:
   - Deformable armor blocks have coarse detail. A probe at 0.145 UV/m looked about 2x too fine against light
     armor, 0.40 UV/m was far too fine, and 0.07 UV/m was still "a tad" too fine. For an armor-style block
     start at **about 0.05 UV/m** (a 2.5 m face spans about 0.13 of the tile) [SOFT: 0.05 is extrapolated].
   - Functional (non-armor) cube blocks have fine detail. A vanilla reinforced conveyor tube matched the
     0.40 UV/m probe by eye [owner], and the vanilla small cargo container's own model measures 0.495 UV/m
     [HARD, measured on its SEUT import]. For machines, panels, weapons and other functional blocks use
     **about 0.40 to 0.5 UV/m**.
   Pick the scale by what the block is, then adjust by eye against a vanilla block of the same kind wearing the
   same skin and colour. Box-project each face (`uv = (a, b) * D + 0.5`, using the two axes across the face's
   dominant normal); overlapping islands are fine on a tiling material.
   Vanilla armor does not use `PaintedMetal_Colorable` directly: `LargeBlockArmorBlock` builds each side from
   `Models\Cubes\Large\Armor\SquarePlate.mwm` (material `SquarePlate`, 4x2 pattern sheet, UV span 0.25 x 0.5
   per 2.5 m plate, 0.141 UV/m averaged) [HARD, SBC and SDK FBX]. Look up the model a vanilla block really
   uses in `Content\Data\CubeBlocks\*.sbc` before measuring it (`ArmorCenter` is not the armor cube).
5. If every material on the model is Vanilla, no textures need to ship with the mod [HARD, wiki].

W012: a DLC material forces the model to be DLC-locked; avoid DLC-tagged materials for public blocks.

## When a new material is unavoidable

Only if no vanilla material gives the look. Create it with `object.create_material`, set textures as TIF
under a `...\Textures\...` path (E007), Color Space Non-Color for NG, Alpha Channel Packed, then set
technique and parameters in the SEUT Shader Editor panel. Textures are authored outside Blender; baking
inside Blender is the last resort.

**A vanilla decal piece with changed values** (run on SEUT 1.2.1 and exported; not yet seen in game). Use it when
a vanilla piece has the right shape but the wrong colour, gloss or paint behaviour:
1. Crop a power-of-two window round the piece from each of the atlas's four TIFs (`_cm`, `_ng`, `_add`,
   `_alphamask`, under `<SEUT Assets>\Textures\Models\Cubes`) with a few clear pixels of margin, change what
   needs changing, and save them as TIFs in a folder whose path contains `\Textures\`, for example
   `<source>\Textures\Cubes\Large\<Name>_cm.tif`. Load and save the pixels as raw values (Non-Color), and edit
   colour in linear. Scale gloss by an offset rather than a multiply, which clips the bright scratches.
2. Copy a linked vanilla material of the same kind (`mat = linked.copy(); mat.name = ...;
   mat.asset_clear()` if it has asset data) and point its image nodes `CM`, `NG`, `ADD` and `ALPHAMASK` at the
   new TIFs, keeping each old image's colour space and alpha mode. The copy keeps SEUT's node names and
   technique. Map the decal quads to the piece's box inside the window.
3. At export SEUT writes a `Material` entry for a local material with each texture path cut at the last
   `\Textures\` and ending `.dds` (E007 if the path has no `\Textures\`), and converts each TIF that is not in
   its own Assets folder to `<mod path>\<that path>.dds` when the source is newer (I002) [HARD, SEUT source
   `export\seut_export_utils.py` and `seut_export_texture.py`; run]. A 64 px set came out with 7 mips: `_cm` and
   `_add` BC7 sRGB, `_ng` and `_alphamask` BC7 linear, as vanilla except vanilla's BC4 alpha mask.
4. Ship the DDS files in the mod at that path. In game, "Reload models" is enough for new texture files: the
   renderer loads a texture path the first time a material asks for it, and "Reload textures" re-reads only
   textures already loaded [HARD, `MyFileTextureManager.GetTexture` and `ReloadTextures`; not yet seen in game].
