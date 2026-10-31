# Characters and handheld weapon animation (outline)

Read this only when the request is a playable or NPC character, an animal-style creature, or the animation
controller for a handheld weapon. This skill's main job is blocks; this file is an outline, not a tested recipe.

Sources: Chipstix213's Custom Character tutorial and handheld weapon animation controller walkthrough (auto-generated
transcripts, so numbers and wording may be off); the SEUT error and export code was checked where noted.
Everything is [SOFT] unless it says [HARD]. Nothing here was built or loaded by this skill.

## Character mods (Blender side)

- Start from Keen's skeleton. In the ModSDK (`Content\Models\Characters\Astronaut`) there are male and female
  skeleton FBX files. Importing one switches the SEUT scene type to **character**, which has no build-stage
  collections and fewer LODs [SOFT, video; SEUT also has a `character_animation` scene type, HARD].
- The helmet and the head (which also holds the eyes) are separate meshes; delete what you will not use and
  keep the armature.
- Rules for Keen's skeleton: do not move bones, do not rename bones. The mesh must fit the bones, and bone names
  drive the animation system. If your character differs a lot, add extra bones and use layered animation
  (a separate topic).
- Meshes are weight painted to the bones. Parenting with automatic weights is enough for a first test.
  Duplicating an arm piece: separate it, mirror it, and rename the copied vertex group to the matching bone
  (for example `left forearm` to `right forearm`) so it follows the other arm.
- Use more than one material when the mesh is the whole character, and use the vanilla suit material names if
  you want suit colour changes to keep working (renaming a material breaks that link even with the same
  textures) [SOFT].
- Collision: provide none and use the astronaut's ragdoll HKT as an **external HKT** (the male
  astronaut HKT from the ModSDK, or the female one when using the female controller); SEUT copies it into the
  export [SOFT].
- **Rotate character** export option: on for playable characters (Keen's models carry a 180 degree rotation
  on all parts, and this compensates), off for animals and creatures [HARD, `seut_export_utils.py` applies it
  for character scenes].
- Error `E051` "invalid weight painting" [HARD]: SEUT adds vertex groups `Problematic - Ungrouped` and a
  weightless group to the offending object. Select them to find vertices that are in no group or have zero
  weight, assign them to the right bone group, delete the two helper groups, and export again. Splitting the
  character into several meshes makes the bad part easy to find.

## Character mods (data side) [SOFT, video]

- Copy the vanilla character definition and change only the subtype, display name and model path (keep subtype
  and name matching, since non-player characters look at the name field). The definition also holds footprint
  decals, ragdoll use, the dropped-bag inventory, movement and collision values, jetpack dummies and thrust,
  suit and temperature use, first-person material hiding, bone sets and weak points (head shot bones), sound
  definitions and turret target offsets. Leave bone-related entries as they are.
- An entity container with the same subtype as the character points it at the default components (stats,
  target locking, survival buffs). Health and other stats live in the stats SBC.
- Test by choosing the new character from the medbay suit-change menu in a creative world. Most vanilla
  animations then play, including the rifle hold, if proportions are close to the astronaut's.

## Handheld weapon animation controller [SOFT, video; not Blender work]

- Use the ModSDK's animation controller tool to open and edit controllers. Start from the example mod's
  controller files for the male and female astronaut (the female one has an extra weapon pin state machine, so
  it needs duplicated nodes).
- Give every layer and state machine a unique suffix for your mod, but keep the prefixes. Change the weapon
  nodes and the transitions leading to them to your weapon's definition ID; the transition from the hip
  rotation node uses a small blend time (0.2 s in the video). Node and transition names must match the weapon
  definition. The point of reusing the example is compatibility between weapon mods.
