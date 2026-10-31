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

### Measure, do not eyeball [HARD, hit in two test runs]

A preview of a picture is scaled, and reading coordinates off it by eye can be off by 40%. In a test the
"tower is about as wide as the crate" impression was wrong: pixel measurement gave 110 px against the crate's
152 px (1.8 m against 2.5 m). Measure instead:

- Open the file with Pillow (`PIL.Image`) in a normal Python, or load it in Blender and read `image.pixels`
  with numpy. Scan a row or column and find where the object colour changes to the background, then take
  widths in pixels.
- Get the scale from one known dimension (a 2.5 m crate drawn 152 px wide gives 60.8 px/m), then convert every
  other measurement; compare with the written labels.
- In Blender, set the image colour space to Non-Color (or read `pixels` and gamma-correct) before judging
  colours, and write an opaque copy for crops when the image has alpha, or it previews white.

When the drawing's written dimensions disagree with the drawn ones, or between views (a generated or sloppy
blueprint), go by the dimension the user fixed (grid size, cell count) and the drawn proportions, and list
every disagreement in the report so the user can correct the table.

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
