# Pipeline: stage order and the source of truth

The order of a whole block build, from design doc to icon, and how an agent that models through scripts keeps one
source of truth. The how of each stage is in the file it points to. Tags as in SKILL.md.

## Contents
- Stage order
- Builders, editors and the freeze
- Telling the user where the job stands

## Stage order

Each stage ends at a **gate**: the user signs it off from renders (`design-detailing.md`, "Workflow" step 2).
A gate **locks** what later stages build on, so going back past it redoes their work. A plain armour block
needs only stages 1, 2 and 7 to 13.

1. **Design doc.** Done when the user confirms intent, size, mount faces, parts table, decal table, the
   interaction points (terminals, inventories, keypads, conveyor ports) with the fixed part that carries each,
   and the gates (`design-detailing.md`, "Workflow").
2. **Blockout.** Done when the silhouette is signed off at the reference's angle and in orthographic views
   (`reference-images.md`). Locks proportions and pivots; going back moves every detail on the moved parts.
3. **Kitbash check.** Each part marked vanilla or custom (`kitbash.md`).
4. **Detail, one part group at a time** (`design-detailing.md`, `hard-surface.md`). Locks shapes and bevels.
   Each interaction point's mesh is built with the part that carries it, as its own object with its detector
   (SKILL.md, "Interaction points highlight real geometry").
5. **Shading check.** Done when no flat face wider than about 4 cm shades more than 1-2 degrees off its own normal
   (`bpy-recipes.md`, "Shading check"). Some fixes add or move geometry, so this comes before decals.
6. **Triangle trim of the parts that will carry decals** (`bpy-recipes.md`, "Triangle budget"). Decals are laid
   onto the surface, so cutting segments or bevel steps under them afterwards means laying them again. To find
   which heavy parts carry decals, count decal vertices within 6 mm of each part (`BVHTree.find_nearest`)
   [HARD, run]. Parts with none (hoses, handles, pipes, fittings) wait for stage 10.
7. **Decal pass**, one decal group at a time from a contact sheet (SKILL.md, "Decals before geometry").
8. **Freeze** (next section). Locks every shape: a change after this is hand work, done by editors.
9. **Split into subpart scenes** if anything moves (`weapons-turrets.md`, `doors-subparts.md`).
10. **LODs, buried-face cull, build stages** (`block-scenes.md`; `bpy-recipes.md`, "Buried faces" and "Moving
    parts between .blend files, LODs from script"). Apply the modifiers first: the cull reads the final surface.
    Trim the parts without decals here too. Every LOD keeps every material of Main.
11. **Collision, mountpoints, mirroring, interaction points** (`modeling-rules.md`, `interaction-highlights.md`).
    Interaction points are done when each detector covers its whole mesh (`errors.md`, check 4a), each conveyor
    detector sits in the cell it connects, facing out, and every detector is on a fixed part (`turret-design.md`).
12. **Export and in-game test** (SKILL.md steps 7 and 8, `errors.md`). Done when the user has loaded it in game
    and aimed at every interaction point up to the rim of its mesh: the outline shows, the terminal or inventory
    opens, and a conveyor placed against each port connects.
13. **Icon** (`bpy-recipes.md`, "Icons" under "Export through the MCP").

## Builders, editors and the freeze

Through the MCP every change is a script, and scripts come in two kinds:

- A **builder** makes a part from nothing, from a table of numbers, and replaces whatever was there. While a part
  has a builder, the builder is that part's source of truth.
- An **editor** reads the part as it is in the .blend and changes it in place, as a tool used by hand would:
  delete these faces, mark these edges sharp, lay decals onto this surface, run a check. What editors make lives
  in the .blend, which is then the source of truth.

One part gets one source. An editor's change to a built part is lost at the next rebuild, and copying the fix
into the builder afterwards leaves two copies that drift apart [HARD, a large turret: in-place fixes mirrored
into builders that had not been rebuilt for many rounds; owner: "this two sources of truth thing hurts my head"].

Builders suit an agent while the shape is still changing: a script says what a part is and why, survives a
context compaction, diffs in git (a .blend is binary), and moves a part and everything on it from one number.
They stay worth it only under four rules:

1. **One builder per part** (or mirrored pair), rerunnable on its own, that also lays that part's decals again.
   One long build of the whole block, whose steps reset each other when run out of order, stops being run and
   then stops matching the file [HARD, same turret].
2. **Fixes go into the builder**, then rebuild that part. The built mesh is output, never edited.
3. **Drift check at every gate**: build each part into a fresh bmesh in the object's local space and compare it
   with the saved mesh. [HARD, run: matched its saved part, and flagged a 1 cm shift.]

   ```python
   def drift(me, bm, tol=1e-5):         # True when the builder still makes the saved mesh
       key = lambda co: tuple(round(c / tol) for c in co)
       return len(bm.faces) == len(me.polygons) and \
           sorted(key(v.co) for v in bm.verts) == sorted(key(v.co) for v in me.vertices)
   ```

   For the whole model, `scripts/rebuild_check.py` runs the full rebuild on a copy in a background Blender and
   compares every object with the saved file (shape, materials, modifiers, sharp edges, UVs), leaving the user's
   open file untouched. [HARD, run on a large turret: 177 of 183 objects matched; it found a fix made only in the
   .blend and decals left off a surface that an edit had moved.] The rebuild must also repeat: run the check
   several times with `PYTHONHASHSEED` set to different values (each run is a fresh Blender session), and every
   run must match the saved file. Two things broke that on the same turret [HARD, run]:
   - A builder that ray-casts against the scene (laying decals onto surfaces) saw its own previous output and
     parts not yet rebuilt. Build what it tests against first, and delete its old output before it runs.
   - `bmesh.ops.bevel` made the same faces in a different order in each session, and seam strips laid along the
     faces followed that order (tips moved up to 1.5 mm). Sort the faces by position before writing the mesh:
     `rank = {f: i for i, f in enumerate(sorted(bm.faces, key=key))}`, then `bm.faces.sort(key=lambda f:
     rank[f])` (the sort key must return a number).

   Build geometry lists for bmesh operators with `list(dict.fromkeys(...))`, not through a set: a set of mesh
   elements is ordered by memory address [SOFT: not shown to change the output on that turret].
4. **Freeze at stage 8 at the latest**: save a checkpoint (commit the .blend) and write in the build log that the
   builders are retired. From then on, editors only. A new part made later by code is built once into the
   .blend; the old builders are never rerun over it. Modifiers stay live until stage 10, which applies them for
   the cull and LODs; a finish pass rerun over applied bevels would bevel them twice.

Freeze earlier when the builders cannot keep rules 1 to 3, and ask the user first: a freeze trades cheap
changes by number for one simple source. Scripts that only read or edit the current model (decal layers, a
finish pass that sets materials, bevels and normals, clearance checks, renders) keep working after the freeze.
An edit that moves a surface lays that surface's decals again in the same step [HARD, run: a cleanup that moved
a bevelled surface left its seam decals up to 14 mm off it].

## Telling the user where the job stands

Many users have never modelled in 3D. At each gate, and whenever they ask what is next, say in plain words:
which stage this is, what signing it off locks, what the next stage is, and whether the model is still built by
builders or frozen. Name stages, not scripts or functions.
