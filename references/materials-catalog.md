# Material behaviour catalog (paintable, decal, emissive)

How vanilla materials behave in game, so you can pick one by behaviour instead of by name.
Measured on SEUT assets 1.7.3 textures and SE game files; tags as in `SKILL.md`.

## Contents
- Reading the ADD texture
- Paintable (colorable) families
- Decal families
- Emissive materials and state-driven glow
- Emissive presets and colors
- Screens, glass, holo
- Picking a material
- Measured table for all 165 materials

## Reading the ADD texture [HARD, wiki; coverage measured]

`_add`: R = ambient occlusion, G = emissive mask, A = paintability (whiter takes more of the block's paint
colour). A texture can carry several of these at once, so one material can be partly paintable and partly
glowing. The table at the end shows the share of each texture that is paintable (alpha > 0.15) or emissive
(green > 0.15), measured at 128 x 128. A 4 x 4 ADD texture is a flat value for the whole material.

## Paintable (colorable) families

| Family | Technique | Behaviour |
|---|---|---|
| `PaintedMetal_Colorable`, `PaintedMetalScratched_Colorable`, `PaintedMetalColorableGlossy`, `PaintedMetal_Clean` | MESH | tiling metal, 100% paintable (flat ADD). Default for armor-style surfaces |
| `Atlas1Colorable`, `Atlas3_Colorable`, `Atlas4_Colorable` | DECAL_CUTOUT | cube detail atlases, 57-77% paintable; unpainted parts keep their own colour |
| `PanelingColorable`, `ButtonsAtlas_Colorable` | DECAL_CUTOUT | panelling and buttons decals, 45-82% paintable |
| `Doodads`, `InteriorWall`, `FabricColorable`, `SolarPanel_colorable`, `Stereolith`, `Monolith` | MESH | 79-100% paintable |
| `Grating`, `cockpit_*` | MESH | 68-78% paintable, with AO baked in |

Fixed-colour siblings share the same atlas and UVs but are not paintable: `*_Darker`, `*_VeryDark`, `*_Yellow`,
`*_Chrome`, `Atlas3_Darker`, `Atlas4_Chrome`. Swap between a Colorable and a fixed sibling without changing
UVs [SOFT, same atlas file names in the table].

Paint keeps a colour map's brightness: the painted value is the colour map's value plus half the paint's value
offset [HARD, `colorize_1` read in the export colorize shader; owner saw the result in game]. So a paintable
decal on painted metal stays as much lighter or darker as its colour map is. `PanelingColorable` uses the light
`Decals_Atlas_A_01_cm`: its bolt heads 1-11 measured 0.11-0.40 above `PaintedMetalColorable_cm` (linear value
over the alpha-solid pixels; head 10 the lightest) and showed as bright spots on painted plate, while the
`Atlas3_Colorable` and `Atlas1Colorable` pieces measured 0.05-0.14 below it. Compare the values before picking
a paintable decal for a painted surface. When no piece is close, copy the piece with its colour map scaled to the
plate's value (`materials.md`, "A vanilla decal piece with changed values").

Armor skins swap textures by material name, so keep vanilla material names unchanged on armor-style
surfaces; glass, holo and shield materials are excluded (wiki, Materials reference).

Each skin covers only the materials its definition lists [HARD, `Data\AssetModifiers\ArmorModifiers.sbc`].
`PaintedMetal_Colorable` is in every skin. `Doodads` (the vanilla airtight and cargo-container corners) is not in
Battered, Wartorn, Weldless, Corrugated or Plastic. `PaintedMetal_Darker`, `Chrome`, `Metal_Dull` and
`PaintedMetal_Yellow` are only in Frozen and Heavy Rust. Battered covers no decal sheet. So a kitbashed vanilla
part whose paint sits on another material keeps flat paint beside the skinned `PaintedMetal_Colorable` round it
[HARD, owner saw it in game under Battered]. Put every large painted area on `PaintedMetal_Colorable`. To keep a
vanilla part's own texture where it is unpainted, cut its faces along the colour-mask outline (the `_add` alpha)
in UV space, using lines through the outline's straight edges; let each piece vote on the mask, and move the
painted pieces to `PaintedMetal_Colorable`, box mapped. Carry the custom normals across the cuts, and weld the
cut points within 10 µm: rounding to 1 µm left cracks.

Bare metals differ mostly in gloss, the `_ng` alpha (the `_cm` alpha is metalness) [HARD, mean of each texture]:
`Chrome` is fully metallic but only 38% gloss, with a smudged light colour map, so it reads as satin metal.
`Metal_Shiny` (`Aluminium_cm`, `AluminiumGlossy_ng`) is as light, clean and the glossiest at 87%; `BlackMetal` is a
dark metal (15% colour) at 55%; `Metal_Dull` 16%. The `_Chrome` decal sheets are about 30% gloss, so their pieces
read a little duller than a `Metal_Shiny` plate under them. Keen uses `Metal_Shiny` in 23 cube models and
`BlackMetal` in 15 (Cover Wall, Window Edge, Trapdoor and Basic Refinery have both), handy for a look in game
[HARD, search of `Content\Models\Cubes`]. A Blender preview on a plain backdrop shows little of the difference,
since the metal has nothing to reflect.
**The names mislead** [owner, seen in game]: `Metal_Shiny` looks far more like chrome than `Chrome` does, and
`Chrome` reads as brushed stainless steel. For a mirror-bright part (a polished rod, a reflector) pick
`Metal_Shiny`; for brushed or satin steel pick `Chrome` or a `_Chrome` decal sheet.

## Decal families

`DECAL_CUTOUT` materials draw on top of the surface behind them using an alpha mask. Use them for panel
lines, vents, hazard stripes, buttons, text, labels. Vanilla list: `Atlas1`, `Atlas1Colorable`, `Atlas2`,
`Atlas3_*`, `Atlas4_*`, `ButtonsAtlas_*`, `Decals`, `PanelingColorable`, `PanelingDarker`,
`PanelingDarkerNoReskin`, `TextAtlas`, `TextAtlasDark`. Decal quads need an offset from the base surface to
avoid z-fighting: about 1.5 mm (SKILL.md, "Decals before geometry"; `bpy-recipes.md`, "Decal offset").
`DECAL` and `DECAL_NOPREMULT` are other techniques for decal-style transparency (no vanilla library material
uses them). Technique count over the 165 library materials [HARD, read from `Materials.blend`]: `MESH` 119,
`DECAL_CUTOUT` 19, `GLASS` 18, `ALPHA_MASKED` 7 (`CargoNet`, `Fish`, `Grating`, `GratingMetallic`,
`IngotsAtlas`, `MonolithText`, `StereolithText`), `HOLO` 4.

**Decal materials are for flat quads only** [HARD, seen in game; cause SOFT]. A dome built from real geometry
with `ButtonsAtlas_Darker` rendered with broken transparency (parts of the dome were cut off by objects
that sit behind it, as if those were in front). Use a `MESH` material for any real 3D shape (a lamp dome,
knob, pipe), and put the decal only on a flat quad over a flat face. A decal quad must also sit fully
inside the face it is on: an LED decal that overhangs the edge of its panel hangs in the air (seen in
game), and a decal bigger than the open area of a framed face looks oversized.

Decal quad pitfalls [HARD, hit in a test run]: a new bmesh face has no normal until `bm.normal_update()`, and
`recalc_face_normals` flips an isolated quad arbitrarily, so check `face.normal` against the direction you
want and flip explicitly (`bmesh.ops.reverse_faces`); a quad facing into the block is invisible. A decal on
curved geometry (a dome) misrenders, see above. Model decals are depth-tested without writing depth [HARD,
`MyGBufferRenderPass.InitPartForDecal`], yet a test crate's top vent decal 0.025 m below its surface still
showed in game (not explained). So a wrong offset can go unnoticed: measure every gap with a ray cast.

## DLC materials (W012) [HARD, `asset_data.seut.is_dlc` in `Materials.blend`]

SEUT flags these 17 and prints W012 when a model uses one: `AquariumGlass`, `BraidedSteel`, `Console`, `Cooker`,
`Dirt`, `FabricBlack`, `FabricWhite`, `Fish`, `FoodDispenser`, `HydrogenThrusterCone`,
`HydrogenThrusterConePlates`, `HydrogenThrusterInjector`, `LabEquipmentScreen_01`, `Leather_Dark`,
`LightPanel_Light`, `PaintedMetal_Red`, `WarningSignsEaster`. W012 is a warning; the export goes on.
- **The game does not check materials** [HARD, `MySessionComponentDLC.HasDefinitionDLC`, `MyCubeGrid`]: DLC is
  checked only through the block definition's `<DLC>` tag, and these textures ship with the base game. An
  untagged block that uses one builds and renders for everyone.
- **Keen's rule is policy** [HARD, ModSDK `OriginalContent\Models\readme.txt`]: content that contains DLC content
  "in its original form or a derivative form" must carry the DLC's `<DLC>` tag in the SBC; mods that break it
  are removed. The text says content and assets, never materials; a texture painted from scratch is not a DLC
  asset, one traced or edited from DLC art is the risky case.
- **Six also ship on vanilla blocks with no DLC tag** [HARD, vanilla MWM scan and `CubeBlocks_*.sbc`]:
  `PaintedMetal_Red` (Refill Station, Irrigation System, Prototech Drill), `BraidedSteel` (short suspensions,
  Refill Station), `FabricBlack` and `FabricWhite` (the free Bed), `Console` (Food Processor) and
  `WarningSignsEaster` (the free Easter warning signs). Whether that makes them usable without a tag is the
  user's call: tell them, don't decide.
- **Free stand-ins**: `PaintedMetal_Colorable` painted dark red for `PaintedMetal_Red` (same normal map; Red is
  less metallic), `FabricColorable` painted for the two fabrics, the free glass textures with an own tint for
  `AquariumGlass`, `Emissive` for `LightPanel_Light` (41 vanilla lights use it). For a small red lamp, a red
  region from `ButtonsAtlas_*` on a flat decal quad (never on a 3D dome). A local copy of a flagged material
  that still points at the same textures only hides W012. Re-read the flag with a background Blender
(`blender -b Materials.blend --python ...`) after SEUT asset updates.

## Emissive materials and state-driven glow

### Which materials the game drives [HARD, `MyCubeBlock.cs` and block classes]

The game finds glowing parts **by material name**. Blocks set colour and emissivity on the material whose
name matches:

| Material name | Driven by |
|---|---|
| `Emissive` and `Display` | default for every block with an emissive preset (`GetDefaultEmissiveParts`) |
| `Emissive0`..`Emissive3` | air vent, oxygen farm, solar panel (4 segments), upgrade modules (`Emissive` + index) |
| `Emissive2`, `Emissive3` | medical room; hydrogen engine uses `Emissive2` |
| `Emissive<N>` per button | button panel, one material per button |
| `Emissive` | heat vent (plus `EmissiveSpotlight` as a light dummy, not a material) |

To get state-driven glow, name the material exactly like that and give the block an `EmissiveColorPreset`.
Vanilla library materials with these names: `Emissive`, `Emissive0..4`, `EmissiveAtlas`, `EmissiveAtlas0`
(glow comes from the green channel of `EmissiveAtlas*_add`, 100% emissive).

### What the state does

`SetEmissiveState(state)` looks up the block's preset, takes the state's `EmissiveColor` and `Emissivity`
(0..1) and applies them to every default part. So one material named `Emissive` changes colour and
brightness as the block goes Working / Disabled / Damaged / Warning. The exact blend with the CM texture is
not verified; the wiki says the glow colour comes from CM at the same location [SOFT].

**Subparts follow the state too** [HARD, `MyCubeBlock.SetEmissiveState` calls `SetEmissivePartsForSubparts`,
which walks every subpart recursively; seen in game on a WeaponCore turret built on a vanilla turret type]: an
`Emissive` face on an azimuth or elevation subpart changed colour with power on and off, with no WeaponCore
emissive definition. So moving parts can carry state lights without script work.

**Glow needs real geometry**: no decal sheet glows except `TextAtlas` (faintly). Put `Emissive` on a real
face (a lens recessed in a bezel, a window plate), not on a decal quad.

**`EmissiveAtlas` layout** (the texture behind `Emissive`) [HARD, read from the textures]: the top half
(v > 0.5) is fine horizontal scan lines; the bottom half is a grungy bright patch. The emissive mask (ADD
green) is even over the whole sheet, so the CM sets how bright it looks. For a plain lens, map the face into
the brightest plain area, about u 0.40-0.50, v 0.26-0.32; a face left on default UVs can land on the scan
lines and render striped. For a long glow strip, map like vanilla instead of squeezing it into that small
patch: Keen's `Emissive` faces are even in pixels, about 300-450 texture pixels per metre (Beacon about 305,
Conveyor Sorter about 450). The sheet is 1024 x 2048, so that is twice as many UV per metre along u as along v
(Beacon 0.30 u and 0.15 v per metre) [HARD, measured on the SDK FBX files]. A small patch stretched 10:1 along
a 3 m strip looked smeared [owner]. For a plain glow, lay the strip's length along u through the bright disc
of the lower half (centre about u 0.49, v 0.26); for a scan-line glow, lay it along v in the top half, so the
lines run across the strip. The scan-line half tiles along v: 64 lines on a 16 pixel period, its first and last
rows matching, so a long strip can repeat it for denser lines (two tiles of v 0.5 to 1.0 over a 3 m strip show
no join) [HARD, read from the CM and rendered]. A preview of the ADD or NG channels shows the scan lines soft and light; in game
they take the CM's colours, which are high contrast [HARD, read from the textures].

Other emissive materials are static unless named as above: `LightPanel_Light`, `ScreenArea*`,
`CockpitScreen_*`, `EmissiveColorable` (flat, fully paintable and emissive), `FoodDispenser`,
`LCD_Economy_Graph_4`.

## Emissive presets and colors [HARD, `Content\Data\EmissiveColors.sbc`]

Block SBC field: `<EmissiveColorPreset>Name</EmissiveColorPreset>`. Set it whenever the model has `Emissive`
faces [HARD, `MyCubeBlock`, `MyEmissiveColorPresets.LoadPresetState`]: without it the generic block code never
refreshes the lamps on working, functional or model changes (that runs only when `UsesEmissivePreset`, which
needs a preset), and a block class that sets states itself falls back to the `Default` colours (the timer
block uses `Timer`). States the game uses: Working, Disabled, Damaged, Warning, Alternative, Locked, Autolock,
Constraint (event controller adds State0, State1).

| Preset | States (colour, emissivity) | Vanilla blocks using it |
|---|---|---|
| `Default` | Damaged black 0 / Disabled red 0.5 / Working green 1 / Warning yellow 1 | 133 |
| `Extended` | Default + Alternative light blue 1 | 86 |
| `ConnectBlock` | Damaged black 0 / Disabled red 0.5 / Working gray 1 / Constraint yellow 1 / Locked green 1 / Autolock light blue 1 | 19 |
| `Timer` | Damaged black 0 / Disabled red 0.5 / Working green 1 / Warning light blue 1 / Alternative blue 1 / Locked yellow 1 | 8 |
| `Basic` | Damaged black 0 / Disabled white 0.5 / Working white 1 / Warning white 1 | 5 |
| `Welder` | Working red 1 / Disabled black 0 | 4 |
| `JumpDrive` | Damaged black 0 / Disabled red 1 / Working green 1 / Warning yellow 1 | 4 |
| `GravityBlock` | Damaged black 0 / Disabled red 0.5 / Working green 1 | 4 |
| `Beacon` | Working light yellow 1 / Disabled dark gray 0 | 4 |
| `EventController` | Damaged black / Disabled red 0.5 / Working green / State0 light blue / State1 blue | 2 |
| `UnpoweredOccupancy` | Damaged black 0 / Disabled white 0.5 / Working white 1 / Warning white 1 / Alternative light blue 1 | not counted |

Colours (RGB): Red 255,0,0; Orange 255,128,0; Green 10,255,0; Black 0,0,0; White 255,255,255; Yellow 255,255,0;
LightBlue 0,255,255; Blue 0,0,255; Gray 128,128,128; LightYellow 255,255,128; DarkGray 30,30,30.
**Fixed-colour lamps** [format HARD, from `EmissiveColors.sbc` and `MyDefinitionManager.InitEmissiveColorPresets`;
not tested in a mod]: a mod adds its own colour and preset in an `.sbc` under `Data`, with SubtypeIds of its
own, and names the preset in the block's `EmissiveColorPreset`:

```xml
<EmissiveColors>
  <EmissiveColor>
    <Id><TypeId>MyObjectBuilder_EmissiveColorDefinition</TypeId><SubtypeId>MyMod_Amber</SubtypeId></Id>
    <ColorDefinition><R>255</R><G>150</G><B>0</B><A>255</A></ColorDefinition>
  </EmissiveColor>
</EmissiveColors>
<EmissiveColorStatePresets>
  <EmissiveColorStatePreset>
    <Id><TypeId>MyObjectBuilder_EmissiveColorStatePresetDefinition</TypeId><SubtypeId>MyMod_AmberLamp</SubtypeId></Id>
    <EmissiveStates>
      <EmissiveState StateName="Working" EmissiveColorName="MyMod_Amber" DisplayColorName="White" Emissivity="1" />
      <EmissiveState StateName="Disabled" EmissiveColorName="MyMod_Amber" DisplayColorName="White" Emissivity="0.2" />
      <EmissiveState StateName="Damaged" EmissiveColorName="Black" DisplayColorName="Black" Emissivity="0" />
    </EmissiveStates>
  </EmissiveColorStatePreset>
</EmissiveColorStatePresets>
```

Both lists go inside the file's `<Definitions>` root. One preset serves the whole block, so every `Emissive`
face shows the same colour; for a lamp in the player's paint colour use `EmissiveColorable` (above) instead.

## Screens, glass, holo

`ScreenArea*` / `TransparentScreenArea*` mark LCD surfaces (the rotated variants orient the screen).
`GLASS`, `HOLO`, `SHIELD` materials must match a TransparentMaterials SubtypeId [HARD, wiki]; the library has
18 GLASS and 4 HOLO materials. `Terminal` is the keypad / terminal panel look (MESH, 50% emissive).

For glass the player should see through, use `WindowRectangularOutside` (the window blocks' outer glass,
reflectivity 0.1), not `GlassOutside` (0.7, otherwise the same settings): it read as a dark mirror that hid the
parts behind it [HARD, values in `TransparentMaterials.sbc`; owner saw `GlassOutside` in game; the swap is not
yet seen in game]. Both textures are a faint dirt rim round a clear middle, one per pane, so map each pane's face
to the whole 0..1 square (`RectangularWindowDirtInside` is 1:2, long side along V).

## Picking a material

1. Surface detail (lines, vents, stripes, labels, buttons): decal first (`PanelingColorable`, `Atlas*`,
   `ButtonsAtlas_*`, `TextAtlas`).
2. Main body: a Colorable tiling material (`PaintedMetal_Colorable`, or the Scratched / Glossy variant).
3. Fixed-colour accents: `*_Darker`, `*_VeryDark`, `*_Yellow`, `*_Chrome` of the same atlas.
4. Glowing indicators that follow block state: a material named `Emissive` (or `Emissive0..3` where the block
   class drives them) plus an `EmissiveColorPreset`.
5. Static light panels and screens: the dedicated materials above.
6. Only if nothing fits: a new material (`materials.md`).

## Measured table for all 165 materials

| Material | Technique | Measured behaviour (share of ADD texture) |
|---|---|---|
| AquariumGlass | GLASS | no ADD texture |
| ArmsDamaged | MESH | paint 13%, emissive 3% |
| Astronaut_Damaged | MESH | paint 33% |
| AstronautStatue | MESH | fixed color |
| Atlas1 | DECAL_CUTOUT | fixed color |
| Atlas1Colorable | DECAL_CUTOUT | paint 57% |
| Atlas2 | DECAL_CUTOUT | fixed color |
| Atlas3_Chrome | DECAL_CUTOUT | fixed color |
| Atlas3_Colorable | DECAL_CUTOUT | paint 77% |
| Atlas3_Darker | DECAL_CUTOUT | fixed color |
| Atlas4_Chrome | DECAL_CUTOUT | no ADD texture |
| Atlas4_Colorable | DECAL_CUTOUT | paint 56% |
| Atlas4_Darker | DECAL_CUTOUT | no ADD texture |
| Atlas4_VeryDark | DECAL_CUTOUT | no ADD texture |
| Atlas4_Yellow | DECAL_CUTOUT | no ADD texture |
| ATM_Keyboard | MESH | emissive 100% |
| ATM_Numpad | MESH | emissive 100% |
| ATM_Screen | MESH | emissive 100% |
| BlackMattePlastic | MESH | no ADD texture |
| BlackMetal | MESH | no ADD texture |
| BlueFrostedMetal | MESH | no ADD texture |
| BraidedSteel | MESH | fixed color |
| ButtonsAtlas_Colorable | DECAL_CUTOUT | paint 82% |
| ButtonsAtlas_Darker | DECAL_CUTOUT | fixed color |
| CameraLens | MESH | no ADD texture |
| CargoNet | ALPHA_MASKED | fixed color |
| Chrome | MESH | no ADD texture |
| ClangCola | MESH | fixed color |
| ClothBag | MESH | fixed color |
| ClothStripe | MESH | fixed color |
| Cockpit | MESH | paint 68% |
| CockpitFighter_Interior | MESH | paint 64%, emissive 36% |
| CockpitFighterGlassInside | GLASS | no ADD texture |
| CockpitFighterGlassOutside | GLASS | no ADD texture |
| CockpitGlassInside | GLASS | no ADD texture |
| CockpitGlassOutside | GLASS | no ADD texture |
| CockpitIndustrialGlassInside | GLASS | no ADD texture |
| CockpitIndustrialGlassOutside | GLASS | no ADD texture |
| CockpitLarge | MESH | emissive 22% |
| CockpitScreen_01 | MESH | emissive 100% |
| CockpitScreen_02 | MESH | emissive 100% |
| CockpitScreen_03 | MESH | emissive 100% |
| CockpitScreen_04 | MESH | emissive 100% |
| CockpitScreen_05 | MESH | emissive 100% |
| CockpitScreen_06 | MESH | emissive 100% |
| CockpitScreen_07 | MESH | emissive 100% |
| CockpitScreen_08 | MESH | emissive 100% |
| CockpitScreen_09 | MESH | emissive 100% |
| CockpitScreen_10 | MESH | emissive 100% |
| CockpitSmall | MESH | paint 78%, emissive 2% |
| Console | MESH | emissive 6% |
| Construction | MESH | no ADD texture |
| ContractsScreen_01 | MESH | emissive 100% |
| ContractsScreen_02 | MESH | emissive 100% |
| Conveyor | MESH | fixed color |
| Conveyor_Yellow | MESH | fixed color |
| Cooker | MESH | emissive 7% |
| CosmicCoffee | MESH | fixed color |
| Decals | DECAL_CUTOUT | fixed color |
| Dirt | MESH | fixed color |
| Doodads | MESH | paint 79% |
| Emissive | MESH | emissive 100% |
| Emissive0 | MESH | emissive 100% |
| Emissive1 | MESH | emissive 100% |
| Emissive2 | MESH | emissive 100% |
| Emissive3 | MESH | emissive 100% |
| Emissive4 | MESH | emissive 100% |
| EmissiveAtlas | MESH | emissive 100% |
| EmissiveAtlas0 | MESH | emissive 100% |
| EmissiveAtlasUnlit | MESH | emissive 100% |
| EmissiveColorable | MESH | paint 100%, emissive 100% |
| EmissiveSpotlight | MESH | no ADD texture |
| ExhaustPipe | MESH | no ADD texture |
| FabricBlack | MESH | no ADD texture |
| FabricColorable | MESH | paint 100% |
| FabricWhite | MESH | no ADD texture |
| Fish | ALPHA_MASKED | no ADD texture |
| FoodDispenser | MESH | emissive 100% |
| FoodPackaging | MESH | no ADD texture |
| FrostedGlass | GLASS | no ADD texture |
| FrostedGlassLarger | GLASS | no ADD texture |
| GenericGlass | GLASS | no ADD texture |
| GlassInside | GLASS | no ADD texture |
| GlassOutside | GLASS | no ADD texture |
| Grating | ALPHA_MASKED | paint 70% |
| GratingMetallic | ALPHA_MASKED | fixed color |
| HydrogenThrusterCone | MESH | no ADD texture |
| HydrogenThrusterConePlates | MESH | no ADD texture |
| HydrogenThrusterInjector | MESH | no ADD texture |
| HydrogenThrusterNozzle | MESH | fixed color |
| IngotsAtlas | ALPHA_MASKED | no ADD texture |
| InteriorWall | MESH | paint 100% |
| LabEquipmentScreen_01 | MESH | emissive 99% |
| Leather_Dark | MESH | fixed color |
| LightPanel_Light | MESH | emissive 100% |
| Metal_Dull | MESH | no ADD texture |
| Metal_Shiny | MESH | no ADD texture |
| MetalMilitary | MESH | fixed color |
| MetalMilitary_Scratched | MESH | fixed color |
| Monolith | MESH | paint 100% |
| MonolithText | ALPHA_MASKED | paint 100% |
| PaintedMetal_Clean | MESH | paint 100% |
| PaintedMetal_Colorable | MESH | paint 100% |
| PaintedMetal_Darker | MESH | no ADD texture |
| PaintedMetal_Red | MESH | no ADD texture |
| PaintedMetal_VeryDark | MESH | no ADD texture |
| PaintedMetal_Yellow | MESH | no ADD texture |
| PaintedMetalColorableGlossy | MESH | paint 100% |
| PaintedMetalScratched_Colorable | MESH | paint 100% |
| PaintedMetalScratched_Darker | MESH | no ADD texture |
| PaintedMetalScratched_VeryDark | MESH | no ADD texture |
| PaintedMetalScratched_Yellow | MESH | no ADD texture. Worn edges; the vanilla cargo container's port frame looks clean in game, so prefer `PaintedMetal_Yellow` there (`kitbash.md`) |
| PanelingColorable | DECAL_CUTOUT | paint 45% |
| PanelingDarker | DECAL_CUTOUT | fixed color |
| PanelingDarkerNoReskin | DECAL_CUTOUT | fixed color |
| PlantedSoil | MESH | no ADD texture |
| PlasticPink | MESH | no ADD texture |
| PlasticWhite | MESH | no ADD texture |
| Plushie | MESH | paint 56% |
| PlushieSE2 | MESH | paint 52% |
| ProgrammingBlock | MESH | emissive 53% |
| Prototech | MESH | fixed color |
| Prototech_Atlas | MESH | fixed color |
| Prototech_Clean | MESH | fixed color |
| RightArmDamaged | MESH | paint 13% |
| Rubber | MESH | no ADD texture |
| RubberDry | MESH | no ADD texture |
| RubberScratched | MESH | no ADD texture |
| RubberWheels | MESH | no ADD texture |
| RubberWheelsScratched | MESH | no ADD texture |
| RustyMetal | MESH | fixed color |
| RustyMetalScratched | MESH | fixed color |
| SabiroidPlushie | MESH | ADD not measured |
| ScreenArea | MESH | emissive 100% |
| ScreenArea180 | MESH | emissive 100% |
| ScreenArea270 | MESH | emissive 100% |
| ScreenArea90 | MESH | emissive 100% |
| Seat | MESH | fixed color |
| SmallTires | MESH | fixed color |
| SmallTiresMotion | MESH | fixed color |
| SolarPanel | MESH | no ADD texture |
| SolarPanel_colorable | MESH | paint 98% |
| StatuePlaque | MESH | fixed color |
| Stereolith | MESH | paint 100% |
| StereolithText | ALPHA_MASKED | paint 100% |
| StoreScreen_01 | MESH | emissive 100% |
| StoreScreen_02 | MESH | emissive 100% |
| Terminal | MESH | emissive 50% |
| TextAtlas | DECAL_CUTOUT | emissive 21% |
| TextAtlasDark | DECAL_CUTOUT | emissive 21% |
| TextureAtlas | MESH | paint 12% |
| ThrusterCones | MESH | no ADD texture |
| TransparentScreenArea | HOLO | no ADD texture |
| TransparentScreenArea180 | HOLO | no ADD texture |
| TransparentScreenArea270 | HOLO | no ADD texture |
| TransparentScreenArea90 | HOLO | no ADD texture |
| TransparentScreenArea_Outside | GLASS | no ADD texture |
| VendingScreen_01 | MESH | emissive 100% |
| WarningSigns1 | MESH | fixed color |
| WarningSignsEaster | MESH | fixed color |
| WindowInside | GLASS | no ADD texture |
| WindowRectangularInside | GLASS | no ADD texture |
| WindowRectangularOutside | GLASS | no ADD texture |
| WindowTriangularInside | GLASS | no ADD texture |
| WindowTriangularOutside | GLASS | no ADD texture |
