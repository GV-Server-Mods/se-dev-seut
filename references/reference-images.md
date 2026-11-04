# Modeling from reference images

Goal: turn a picture into measurable targets, build to the numbers, then check against the picture.

## 1. Read the reference before touching Blender

Look at the image and write down, in plain numbers where possible:

- Overall proportions (width : height : depth) and the one dimension the user fixed (a block grid size,
  a door height).
- Silhouette from each given view (front / side / top); say which views are missing.
- Primary forms, then secondary cuts, then small detail, in that order.
- Symmetry (which axes), repeating elements and their counts.
- Where the image is perspective (distorted) rather than orthographic; do not measure across perspective.

Ask for a missing side view or a scale cue when a dimension would otherwise be a guess.

### Ask for straight-on views first [SOFT, field-tested on a turret]

When the only reference is perspective concept art, ask the user before the blockout for straight-on front,
side and top views of the same design. An image generator can make them from the concept art. In a turret
build, four blockout rounds from two three-quarter views and camera fits still left the proportions wrong;
generated top and side views fixed the gunhouse, roof, front slope, rear section and roof gear in one round.

- Use generated views for shape and ratios, not exact sizes. Scale each to the dimensions already agreed
  (width, length, height; a different scale per axis is fine), and write the pixel-to-metre mapping down.
- Views from a generator disagree with each other and with the original art (a part's position, a length, a
  taper). List each disagreement, follow the user's choice, and record it in the build log.
- Check the blockout as outline overlays on each view from an orthographic camera at the same scale.

### Measure, do not eyeball [HARD, hit in two test runs]

A preview of a picture is scaled, and reading coordinates off it by eye can be off by 40%. In a test the
"tower is about as wide as the crate" impression was wrong: pixel measurement gave 110 px against the crate's
152 px (1.8 m against 2.5 m). Measure instead:

- Open the file with Pillow (`PIL.Image`) in a normal Python, or load it in Blender and read `image.pixels`
  with numpy. Scan a row or column and find where the object colour changes to the background, then take
  widths in pixels. Pillow is optional (`setup.md`); when it is missing, Blender's loader reads every common
  format including `.webp`, and on Windows PowerShell's `System.Drawing` reads PNG, JPG and TIF (not `.webp`).
- Get the scale from one known dimension (a 2.5 m crate drawn 152 px wide gives 60.8 px/m), then convert every
  other measurement; compare with the written labels.
- In Blender, set the image colour space to Non-Color (or read `pixels` and gamma-correct) before judging
  colours, and write an opaque copy for crops when the image has alpha, or it previews white.

When the drawing's written dimensions disagree with the drawn ones, or between views (a generated or sloppy
blueprint), go by the dimension the user fixed (grid size, cell count) and the drawn proportions, and list
every disagreement in the report so the user can correct the table.

### Perspective concept art [SOFT, used to plan a turret from a three-quarter view]

A three-quarter view still gives proportions:
- Take ratios only along one axis between features close together (a barrel's length against the gunhouse
  beside it), never across the depth of the picture.
- Take fixed dimensions from the grid and from the block the model replaces (cell count, pivot height, muzzle
  reach), and let the art set only what they leave open.
- Settle the rest on blockout renders from a Blender camera matched to the art's angle (line up the block's
  edges with the art's), compared side by side with `look(image=...)`.

### Enlarge small parts before reading them [HARD, a user rejected the pass read at full size]

A small part (a sensor dome, a sight, a side box) covers a few dozen pixels of the art, and read at that size
its basic form came out wrong: windows modelled on the outside of a dome where the art sets them in, and a
sight looking at the sky instead of forward. Crop the part from every view the art has, upscale each crop 3-4x
(Pillow, `Image.LANCZOS`) into one side-by-side sheet, and write down for each feature whether it is recessed or
raised, which way it faces, and its outline from each side, before modelling it.

## 2. Build a target table

Put the numbers in a short table (feature, size, position) and keep it in the conversation. Build from
the table; when the user corrects something, update the table first.

## 3. Get the image into Blender when it helps

- Orthographic references: add an Empty of type Image per view, aligned to the axis planes, scaled so a
  known dimension matches, placed behind the model, display opacity about 0.5. `look` through
  `view=[0,-1,0]` style directions to compare.
- Perspective photos: use as a visual guide only; compare with `look` at a similar angle.
- `look(image="<path>")` shows a reference file next to renders; useful for side-by-side checks.
- Remove reference empties (or move them to a hidden collection) before export.

## 4. Check loop

After each pass, `look` with `mode=angles` at the reference's angle, list what differs (proportion first,
then form, then detail), and fix the largest error. Stop at the level of detail the asset needs; game
blocks read at a distance, so silhouette and primary shapes matter more than micro detail.

## When a generator is tempting

Image-to-3D (Meshy, Tripo, Hunyuan3D via `generate_3d`) returns a triangulated, textured mesh of the
picture's subject. It will not match a grid, has no clean UV layout for shared atlases, and its textures
are baked and unique. Useful as a quick 3D shape reference to model over; not as the final mesh for a
game with a fixed material set. Ask the user before generating.
