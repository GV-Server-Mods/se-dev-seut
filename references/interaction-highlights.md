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
3. Resize the empty so it covers the **whole** highlighted mesh, with a small margin (see "Detector size"
   below). The highlight only shows while the reticle is inside the empty, so any part of the mesh outside it
   looks dead to the player.
4. Export, restart the game fully (a reload keeps the old data), aim at the area. A yellow square means the
   empty and mesh are not associated.

SEUT's operator needs `Main` to contain the object (E025), one selected object at a time (E009), and an
empty index unique per type. Source: `empties/seut_ot_add_highlight_empty.py`.

Run through the MCP on SEUT 1.2.1 / Blender 4.5 [HARD, tested]:

```python
ob.select_set(True); bpy.context.view_layer.objects.active = ob     # ob is in Main, parented to the root
bpy.ops.object.add_highlight_empty(detector_type="detector_terminal_", index=1)
```

- `detector_type` is the key from the table below, including the trailing underscore. The enum is dynamic, so
  introspecting `get_rna_type()` lists no items; pass the string.
- Result: object renamed `<name>_section_1`, empty `detector_terminal_1` in `Main`, same parent as the object,
  at the object's location, `empty_display_type` CUBE, display size 0.5. Its `highlight` property is already
  set to the object name, and `empty.seut.highlight_objects[0].obj` is the mesh. The info line is `I011`.
- Size the aim area with the empty's `scale` (half-extent = `empty_display_size * scale`); `dimensions` reads 0
  for empties. The new empty is only a starting size, so resize it to the mesh (next section).
- A duplicate `index` is not rejected: Blender appends `.001` to the name. Keep indices unique per type yourself.
  Object names are global to the .blend, not per scene: `detector_terminal_1` in another scene of the same file
  also forces `.001` here [HARD, hit in a test run]. Use an unused index, or rename the empty afterwards (the
  empty's `highlight` property names the mesh, not the empty, so a rename does not break the link). Exported
  dummies are named from the object, so make sure no `.001` suffix remains.
- Detectors exported on a plain `CubeBlock` (SEUT's generated SBC) show the outline in game [HARD, owner test],
  but opening a terminal or connecting a conveyor needs a block type that has that function (a TerminalBlock,
  cargo container, ConveyorSorter, and so on) [SOFT, not tested]. Change `TypeId` in the SBC when the block
  must actually work.
- Select the next target explicitly before each call; the operator works on the single selected object.

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

## Detector size [HARD, owner test]

The outline appears only while the aim ray is inside the detector empty, not while it is over the mesh. In a test
the empty was sized by eye and covered about 60% of the width and height of the panel mesh; aiming at the rest
of the panel did nothing, and players would expect the whole mesh to react.

- A CUBE empty spans `empty_display_size * scale` from its centre on each axis (half-extent). With the SEUT
  default display size 0.5 and scale 1, the empty is 1 m across.
- Size it from the mesh, not by eye: cover the mesh's full bounding box in the empty's own axes, plus a margin of
  about 1 cm on the face directions, and make it a little deeper than the mesh (a few cm each side) so the aim
  ray reliably enters it. Centre it on the mesh.
- For a mesh at an angle, or a curved port frame, cover the box that contains the whole mesh. A bigger empty
  only costs extra aim area.
- Keep the empty inside the block bounding box where the mesh allows it.

```python
def size_detector_to_mesh(empty, mesh, pad=0.01, depth_half=0.04, depth_axis=1):
    """Cover `mesh` (axis aligned with the empty) fully; depth_axis is the face normal (0 X, 1 Y, 2 Z)."""
    half = [d / 2 + pad for d in mesh.dimensions]
    half[depth_axis] = max(half[depth_axis], depth_half)
    empty.location = mesh.location
    empty.scale = [h / empty.empty_display_size for h in half]
```

Check it numerically before export: each of the mesh's dimensions must be at most twice the empty's
half-extent on that axis.

## In-game result [HARD, owner test]

A box mesh with the `Terminal` material plus `detector_terminal_1` loaded in game and the aimed panel outlined
correctly, so the empty-to-mesh link works. The `Terminal` texture, however, is a whole UI sheet, not a
tileable surface:

- `terminal_panel_cm` (512 px) holds a portrait keypad UI in its **left half**: u about 0.03 to 0.525 over the
  full height (top bar, circular display, 4x3 keypad, bottom bar); the right half is black.
- Mapping the whole quad to a middle slice (u 0.35-0.65) showed a stretched fragment with two keys. Map the
  panel to `u 0.03..0.525, v 0..1` and size the mesh to that portrait ratio (about 1 : 2, for example 0.2 x 0.4 m).
- A narrow lit strip does not fit that portrait mapping (it would stretch the keypad over a 1 : 7 strip). A test
  run mapped a strip to a small flat key area of the sheet (u 0.035-0.06, v 0.45-0.54) to get a plain lit
  patch [SOFT: not seen in game]. `Terminal` is a UI sheet; its emissive follows block state but is blue, not
  a colour you choose.
- General rule: a material that is a UI sheet or atlas needs a deliberate UV region; check its texture before
  mapping (`references/atlas-regions.md` lists the atlases; `Terminal` is not in it).

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
- Not yet exercised: export of a highlight, and the in-game aim test.
