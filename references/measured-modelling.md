# Measured modelling: a reference sheet, a silhouette check, a separate critic

For any blockout built from straight-on views. Two limits drive it [SOFT, modding community advice and turret
builds]. First, an agent's spatial reasoning and vision are too coarse to judge proportions from a render: it
reads a part as right when it is 10-30 cm off. Second, the agent that built a pass grades it kindly. So the
references become numbers, code **measures** every pass, and a **critic** that never saw the builder's reasoning
reviews it. The agent's eyes are for *what* is wrong, and the numbers say *where* and *by how much*.

Tool: `scripts/ortho_measure.py`. Its header holds the commands and the `sheet.json` format. It runs in a
background Blender, which ships numpy, so nothing needs installing. Tags as in SKILL.md.

## 1. Reference sheet (once, before the blockout)

1. Get straight-on views: front, side and top, plus the back and the other side when the design is not
   symmetric. Use the user's drawings, or an image generator working from the concept art
   (`reference-images.md`, "Ask for straight-on views first"). Each needs a plain background and no perspective,
   with labels and dimension lines clear of the object. Ask the generator for **no drop shadow and no ground
   shadow**. Generated concept art adds them by default, and a dark shadow joined to the object reads as part
   of it [HARD, generated turret art]. Failing that, cut each view out to a transparent PNG with any background remover
   (Windows 11 Paint has one), and the alpha becomes the outline. Loose arrows, brackets and captions drop out by
   themselves (`keep`).
2. Write the dimension table. It gives the model's outer extents (`bounds`, min and max per axis in Blender
   metres) and the fixed sizes (grid cells, pivot, muzzle reach).
3. Write `sheet.json` beside the views and run `sheet`. Open every `mask_<view>.png` over its `ref_<view>.png`:
   it must be the object's outline, solid. Shadows, ground lines or labels in it need `shadow`, a higher
   `threshold` or an `ignore` rectangle; a top view drawn turned needs `rotate`.
4. **Compare only what the art and the design share.** When the user has decided to depart from the art (a
   block-size square base under a round one, longer barrels), blank the art's version with `ignore`, leave the
   model's out with `check.exclude`, and set `bounds` to the shared parts. The views are scaled to fit their
   whole outline, so one departed part pulls every other part off scale and smears its error over the
   whole model [HARD, turret run: with the base in, front overlap was 71%; without it, 96%].
5. **Landmarks for the details inside the outline**: hatches, vents, grilles, panels, big decals, anything
   whose place on a face matters. For each, read a rough box off `grid_<view>.png` (a 0.5 m grid labelled each
   metre), write it under `landmarks` with the model parts it maps to, and run `sheet` again. Each edge snaps to
   the nearest clear line in the art. Check every cyan box sits on its detail; correct the rough box where it
   does not. Name the part that matches the art's detail, not a bigger one holding it: a panel object that
   includes its frame measures the frame.
6. Read `sheet_report.md` for the places where the views disagree:
   - **Stretch** over 3%: the view is not straight-on, or the bounds are wrong.
   - **Mirror pairs**: opposite views must have the same outline, mirrored.
   - **Shared edges, near misses**: one feature (a deck height, a tower top) drawn at two places in two
     views. Generated views get about nine features in ten consistent [SOFT, user report], and these are the rest.
7. Show the user each disagreement, with its report row and `edges_<view>.png` or
   `pair_<a>_<b>.png`, and the landmark boxes on `grid_<view>.png`. The user picks which view is
   right. Then fix the image, add an `ignore`, or change the table, and run `sheet` again.

Done when the user has signed off the sheet, landmark boxes included, and every flagged item is fixed or accepted. From then on the
signed-off sheet is the **source of truth**: it beats every picture, the concept art included.

When the views disagree too much to settle, a generated 3D proxy can stand in for them. `generate_3d` makes
one; Hyper3D takes up to five views and the table's proportions. Rendered in these same views, its outlines
agree by construction. It costs the user credit, its edges come out soft, and its unseen sides are invented.
The user decides [SOFT, not tried].

## 2. Every blockout pass

1. Build the pass from the table.
2. Run `check` with a label per pass, either in a background Blender on a copy of the .blend or in the live
   Blender through the MCP. It renders the `check.collections` straight-on at the sheet's scale and writes
   `report.md` and the overlays.
3. Fix the deepest rows first. An "extra" row names the part that sticks out. A "missing" row names the
   part beside the gap. A landmark row gives how far the part's centre sits from the art's and how much bigger
   or smaller it is. When most landmarks of one view share one offset, suspect the view (a lean, a cut line, a
   stretch) before moving parts; the report prints that median.
4. When the reference is wrong in a place and the user says so, add an `accept` range with the reason, in
   their words.

Done when `check` says **PASS**: no outline difference deeper than the tolerance outside the accepted ranges,
and no landmark further off than its tolerance.
Suggested tolerance: 5 cm on a large grid block, 1-2 cm on a small one [SOFT].

## 3. The critic (after each PASS, before the user sees the pass)

Start a separate agent with fresh context: the Agent tool in Claude Code, a new thread elsewhere. Give it only:
the concept art, the sheet's views, the dimension table, `report.md`, `overlays.png`, `board_<view>.png`,
`detail_<n>.png`, and renders of the model at the art's angles plus close-ups of each part group. Brief:

```
You review a 3D model pass against its references. You did not build it; your job is to find differences.
1. Every row of report.md is measured: restate each one with its size.
2. board_<view>.png and detail_<n>.png show the art and the model side by side at one scale, on a grid in
   metres (the model's parts in flat colours). Read positions off the grid. Compare them, then the renders
   with the concept art, for what an outline cannot show: parts inside the outline (panels, vents, hatches,
   sights), raised against recessed, which way each part faces, how parts overlap, counts of repeated parts,
   symmetry, and parts present in one and absent in the other.
3. Give a size only when it comes from the report, the table or the grid; otherwise describe the difference.
Answer with a list, worst first: what, where (view and world range, or part), how big, evidence (report row or
image), confidence (high, medium, low), and whether the reference itself is unclear there.
```

The builder fixes every high-confidence item and goes round again. When the check passes and the critic's list
holds nothing high, the pass goes to the user (`pipeline.md`, the blockout gate).

## What it does not see

- Details inside the outline that have no landmark, and for those that do, anything beyond their box in one
  view: shape, depth (a recess against a raised plate), what overlaps what. The table, the boards and detail
  crops, and the critic cover these. Below about 10 cm, generated art is mostly decoration; there the table,
  the block grid and the decal atlas sizes decide, not pixels.
- Parts outside `check.collections`. A subpart scene counts only when it is instanced into a listed collection.
- Views of the same axis family can agree in outline and still place a feature differently in depth. Only a
  third view, or the user, settles that.

Tested [HARD, run on Blender 4.5.10]: a synthetic block with planted errors in a background Blender. The check
found a barrel 30 cm short, a roof 10 cm low and an extra antenna, each with its part named. The sheet step
found the two planted art mistakes: a tower drawn 10 cm wider in the back view, and a tower top 25 cm off
between the front and side views. A check of four 1 px = 1 cm views took about 6 s.

Real art [HARD, run]: generated front, side and top views of a finished turret, checked at 2 cm/px with the base
excluded, in about 7 s. Annotation marks dropped out. `shadow` cleared the light shadows but left the dark ones
under the barrels as false "missing" rows. The overlays and rows did locate real differences: the position of a
sensor dome, the hull's front slope, and the barrels. The side view was 23% off the model's proportions,
because of a departure the user had chosen (longer barrels). That is the case step 1.4 handles. A rear view
the generator drew a few degrees off-axis still matched the model at 96%, as the straight front view did.
Its lean showed as 4% more stretch than the front and as 20-25 cm differences along both sloped sides in the
front/back pair; the side face it showed sat inside the outline. The same pair found the two views placing a
roof dome about 55 cm apart.

Landmarks [HARD, run]: on the synthetic block, rough boxes 5-8 cm off snapped onto the true edges to the
centimetre, and the check reported each planted error exactly: a hatch 15 cm off-centre and 10 cm short, a roof
panel 10 cm long, a decal quad 2 cm off inside a joined two-piece mesh, a part missing. On the real turret's rear
view, four landmarks shared a median offset of 12 cm sideways and 18 cm up, which is that view's lean and base
cut line. Their detail crops showed a real difference: the art's centre box straddles a feed tube, the model's
sits above it. A landmark naming a panel object that included its frame came out 94 cm too tall (step 1.5).
