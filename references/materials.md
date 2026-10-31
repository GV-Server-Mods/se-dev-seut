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
   Measured on the vanilla large armor block (`ArmorCenter.FBX`, PaintedMetal_Colorable): **0.40 UV per metre**,
   so a 2.5 m face spans about one full UV tile. A first probe at 0.145 UV per metre looked too coarse next to
   armor in game; the owner estimated "about 2x" and the measurement gave 2.8x [HARD, measured and
   owner-observed]. Box-project each face (`uv = (a, b) * 0.40 + 0.5`, using the two axes across the face's
   dominant normal); overlapping islands are fine on a tiling material.
5. If every material on the model is Vanilla, no textures need to ship with the mod [HARD, wiki].

W012: a DLC material forces the model to be DLC-locked; avoid DLC-tagged materials for public blocks.

## When a new material is unavoidable

Only if no vanilla material gives the look. Create it with `object.create_material`, set textures as TIF
under a `...\Textures\...` path (E007), Color Space Non-Color for NG, Alpha Channel Packed, then set
technique and parameters in the SEUT Shader Editor panel. Textures are authored outside Blender; baking
inside Blender is the last resort.
