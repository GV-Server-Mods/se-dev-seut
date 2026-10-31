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
