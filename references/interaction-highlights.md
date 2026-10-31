# Interaction highlights (terminal, inventory, keypad, ports)

Default style: every interaction point should highlight a real part of the model (the screen panel,
keypad, port or hatch), never just show a floating rectangle. A detector empty with no linked mesh draws
the plain yellow-square box; a detector empty linked to a mesh outlines that mesh when the player aims at it.

## Contents
- How it works
- Build steps
- Detector types
- Vanilla example: LargeBlockSmallContainer
- Rules and gotchas

## How it works [HARD, SEUT source and wiki]

- A detector empty (name starts with `detector_`) defines the area the crosshair must hit. Its size is the
  aim area.
- Its custom property `highlight` names the mesh object(s) to outline, `;` separated. SEUT writes it at export
  from the empty's `seut.highlight_objects` list.
- The outline colour is global (Environment definition `ContourHighlightColor`); it cannot be set per block.
  Text panel blocks default to outer-edge-only outline (wiki, UseObjects page not read).

## Build steps

1. Model the interactive part as its own object inside `Main`, parented under the block's single root object.
   Give it the real look (for example the vanilla `Terminal` material for a terminal panel).
2. Select that object, `bpy.ops.object.add_highlight_empty(detector_type=<key>, index=N)`
   (UI: Add > Empty > Add Highlight Empty). It creates the empty at the object, parents it to the same
   parent, links it, and renames the object to `<original>_section_<N>`.
3. Resize the empty to cover the face the player should aim at (slightly generous, inside the bounding box).
4. Export, restart the game fully (a reload keeps the old data), aim at the area. A yellow square means the
   empty and mesh are not associated.

SEUT's operator needs `Main` to contain the object (E025), one selected object at a time (E009), and an
empty index unique per type. Source: `empties/seut_ot_add_highlight_empty.py`.

## Detector types (SEUT 1.2.1 `empties['highlight_empties']`)

| Key (empty name prefix) | Use | Indexed |
|---|---|---|
| `detector_terminal_` | terminal access; on doors it toggles open/closed | yes |
| `detector_inventory_` | inventory access without conveyor function | yes |
| `detector_conveyor_` / `detector_conveyor_small_` | large / small conveyor port; overlap neighbour's origin to connect | yes |
| `detector_textpanel_` | LCD text panel; crashes on a non-LCD block | yes |
| `dummy_detector_panel_button_` | single button panel | yes |
| `detector_cockpit_` | enterable block | yes |
| `detector_door_` / `detector_advanceddoor_` | sliding door / advanced door only | yes |
| `detector_block_` | medical station regen area | yes |
| `detector_cryopod_` | cryopod | yes |
| `detector_wardrobe` | wardrobe; moves player into the empty, add collision 0.95 m below | no (extras `_1`, `_2`) |
| `detector_forageable` | forageable item; link the object that disappears when foraged | no |

## Vanilla example: LargeBlockSmallContainer [verified by import]

Model `Models\Cubes\Large\CargoContainerSmall.mwm`, SDK FBX at
`<ModSDK>\OriginalContent\Models\Cubes\large\CargoContainerSmall.FBX` (+ `.xml` listing materials and LODs).

- One root object `CargoContainerSmall`; 55 meshes and 12 empties are all parented to it.
- 6 `detector_terminal_*` empties and 6 `detector_conveyor_*` empties, one pair per face.
- Each empty's `highlight` property names its own mesh: `detector_terminal_section_001..006` and
  `detector_conveyor_section_001..006`. The terminal section is a small separate mesh (about
  0.15 x 0.03 x 0.25 m, 20 vertices); the conveyor sections are the port frames.
- Terminal empties are box-shaped (about 0.2 x 0.1 x 0.3 in FBX units, scaled), conveyor empties are
  larger squares covering the port.
- Materials listed in its XML: PaintedMetal_Colorable, PaintedMetalScratched_Colorable, Terminal,
  PaintedMetal_Yellow, Metal_Dull, Conveyor, Chrome, TextAtlas, Doodads, PaintedMetal_Darker, Decals.
  So decals (`TextAtlas`, `Decals`) and shared materials carry the detail, as the decal-first rule wants.
- Vanilla names differ from SEUT's `_section_<N>` scheme; SEUT's importer keeps the vanilla names.

## Rules and gotchas

- Parent the empty and its target to the same object (W007), and keep all parts under one root.
- Never raw-import vanilla FBX with `bpy.ops.import_scene.fbx` for study: it creates thousands of junk
  material slots. Use SEUT's importer (`scene.import_complete` / Import FBX) or import into a throwaway
  file and purge afterwards.
- Subpart objects: a highlight on a subpart needs the empty inside that subpart's scene [SOFT, untested].
- Not yet exercised through the MCP: running `add_highlight_empty`, export, and in-game aim test.
