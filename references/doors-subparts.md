# Doors and animated subparts

Read this for any door, hatch, gate or other block whose parts move (the moving parts are subparts). For
turret subpart chains (rotor-style movement driven by the game) see `weapons-turrets.md`.

Sources: Chipstix213's two-part Advanced Door tutorial (auto-generated transcripts, so wording is uncertain),
checked against the decompiled game code (`MyObjectBuilder_AdvancedDoorDefinition`, `MyAdvancedDoorDefinition`,
`MyAdvancedDoor`). Nothing here has been built or loaded by this skill. Tags: [HARD] read in the game code,
[SOFT] video claim not yet reproduced.

## Contents
- The three door kinds
- Model side (Blender)
- Orientation quirk
- SBC side: advanced door definition
- Gotchas

## The three door kinds

- **Standard door** (`Door`): one or two parts slide left or right, chosen by the preset subpart name (`door left`,
  `door right`). Movement is hardcoded; the SBC only sets opening distance and speed [SOFT, video].
- **Sliding door** (`AirtightSlideDoor`): two parts slide and rotate into the edges, again by preset subpart
  names and hardcoded [SOFT, video].
- **Advanced door** (`AdvancedDoor`): any number of subparts, each with its own slide or rotate action, delays and
  sounds, all described in the SBC. There is no advanced door in the vanilla game data (a search of
  `Content\Data\CubeBlocks` finds none), so a modded one is the only working example [HARD].
- Nothing animated in Blender carries over to the game; animations in the video are only previews [SOFT].
  Space Engineers also has animated entity components (simple scripted slide and rotate, documented by Digi on the
  official modding wiki) that can be attached to any model [SOFT, not read].

## Model side (Blender) [SOFT, video; SEUT operators verified in source]

1. The main scene holds the door frame mesh and the dummies; everything else moves as subparts.
2. Each moving piece is its own scene of type **Subpart**, holding a mesh in its Main collection **and a
   collision object**. The video says the door does not work if any subpart lacks collision, even a tiny bolt
   that needs none. The game does create subpart physics from the subpart model's collision shapes
   [HARD, `MyAdvancedDoor`], so give every subpart at least one shape.
3. Link a subpart into the main scene with an empty: `Add Preset Subpart` (door left/right for standard doors) or
   `Add Custom Subpart` with your own name for an advanced door. Parent the empty to the main object, then pick
   the subpart scene in its properties.
4. Highlight and use: `detector_advanceddoor_<n>` only works on advanced doors; a `detector_terminal_<n>` empty
   opens any door type. A highlight empty can target a **subpart empty** instead of a mesh, which is how a
   door highlights its moving panels.
5. Subparts of an advanced door are all referenced to the main model's origin, so each subpart is modelled at
   its final position relative to the main origin and its empty sits at (0, 0, 0). To place a part off-centre,
   model it off-centre. Identical-looking parts (two mirrored locks) therefore need two separate meshes and
   scenes; they cannot be duplicates of one instance.
6. An advanced door can give subparts their own build stages (BS collections in the subpart scenes), where vanilla
   doors only use whole-door stages [SOFT, video].

## Orientation quirk [video and owner; SEUT source agrees, game result not tested]

The source backs this: SEUT exports subpart scenes with FBX `axis_forward = '-Z'` and main scenes with `'Z'`
(`seut_export_utils.py`), so a subpart is turned 180 degrees about the up axis relative to a main model. The
owner also saw backwards subparts on an earlier weapon model.


Main scenes treat Blender -Y as the block's front. A subpart scene's forward direction is +Y. Linking a subpart
the normal way therefore shows it turned the wrong way round; rotate the subpart empty 180 degrees about Z in
the main scene and it appears correctly. Check by `look` and then in game.

## SBC side: advanced door definition [HARD fields, SOFT XML element names]

SEUT writes a normal `CubeBlock` definition (mount points included). Change it to
`xsi:type="MyObjectBuilder_AdvancedDoorDefinition"` with `TypeId` `AdvancedDoor`, then add by hand:

- `ResourceSinkGroup`, `PowerConsumptionIdle`, `PowerConsumptionMoving`.
- `Subparts`: a list of subpart definitions. Each has `Name` (the subpart model file name without extension;
  the game loads `<directory of the main model>\<Name>.mwm`) and an optional `PivotPosition` (read from the
  model when absent). The video lists the empty names without the `subpart_` prefix. The first one defined is
  part ID 0, then 1, 2 and so on.
- `OpeningSequence`: a list of openings, each with:

| Field | Meaning |
|---|---|
| `ID` or `IDs` | Part index; `IDs` takes a list such as `0,2,4-6` (comma list and `a-b` ranges) |
| `Move` | `Slide` or `Rotate` (the only two) |
| `SequenceType` | `Linear` (the only value) |
| `Speed` | Movement speed; rotation speed is not in clear units, tune by eye |
| `SlideDirection` | Vector for slides. The video's cheat sheet: X sideways, Z forward/back, Y up/down in game space, which is Blender Y and Z swapped |
| `MaxOpen` | Metres for slides, degrees for rotations |
| `RotationAxis`, `PivotPosition`, `InvertRotation` | Rotation axis `X`, `Y` or `Z`, hinge point (needed unless the part rotates about the model centre), direction flip |
| `OpenDelay`, `CloseDelay` | Seconds. The sequence runs in reverse to close, so a part opened last is closed first unless its `CloseDelay` says otherwise |
| `OpenSound`, `CloseSound` | Sound names; separate sounds per stage are possible |

The same part ID can appear in several openings to combine a slide and a rotation (for example a lock turning
while a bolt slides). Scaling or hiding a part is not possible; parts only move [SOFT, video].

Element names inside the lists come from the object builder types (no `XmlArrayItem` renames were found, so the
items are probably `SubpartDefinition` and `Opening` elements); confirm against a working modded advanced door
before relying on them.

## Gotchas

- **Do not name a subpart scene (and so its `.mwm`) the same as its empty.** The advanced door system loads
  subparts by file name as well as by dummy, so identical names produce a duplicated, stationary ghost part
  with no collision [SOFT, video]. Use generic scene names (`subpart_1` to `subpart_8` in the video) and
  descriptive empty names.
- Every subpart needs collision (above), and subpart changes need a full game restart, not a model reload
  (`SKILL.md`, step 8).
- Keep a subpart scene on the same grid scale and export settings as the main scene (W001, W020).
