# SEUT errors and pre-export checklist

Codes are from `seut_errors.py` in SEUT 1.2.1 [HARD]. The Notifications panel (SEUT main panel, turns red
on error) shows them; `Delete Temporary Files` off keeps `*.mwm.log` for export failures.

## Contents
- Setup prerequisites and the Notifications panel
- When Blender crashes or the MCP connection drops
- Pre-export checklist
- Errors with a fix
- Warnings

## Setup prerequisites and the Notifications panel [HARD, wiki Installation Guide, Addon Preferences, Notifications]

- A working SEUT install needs: Blender 4.0+, the SEUT add-on, Havok Content Tools (for collision `.hkt`;
  Addon Preferences > Havok Standalone Filter Manager points at `hctStandAloneFilterManager.exe`), .NET
  Framework 3.5, the VC++ 2012 redistributable, the Space Engineers ModSDK, and at least 15 GB free for the
  Asset Directory. Game Directory and Asset Directory must be set, then "Update Textures from Game Files"
  (30+ minutes, Blender freezes meanwhile), then Assets and MWMBuilder each "Download & Install". If an
  export reports E012, E013 or missing textures, check these first. A "Rate Limit Exceeded" message from the
  asset or MwmBuilder download is GitHub throttling; wait 30 to 60 minutes.
- The Notifications panel has three levels (INFO, WARNING, ERROR) with an ID and timestamp. Errors link to a
  wiki page per ID (`.../wiki/Modding/Tools/SEUT/Notifications/E0xx`). Hidden types are only filtered, not
  deleted. `Export SEUT Logs` saves the Blender System Console to a file and `Toggle System Console` shows
  problems the panel missed; use them before clearing notifications. The wiki lists E001 to E056 and W001 to
  W020 (this skill's table follows SEUT 1.2.1 source).

## When Blender crashes or the MCP connection drops [HARD for steps 1, 3 and 4 on Windows, Blender 4.5.10: tested by force-killing Blender and relaunching; the other steps SOFT]

Calls fail with "Connection to Blender lost" / WinError 10054, or `get_addon_status` stops answering.

1. **Record two things at the start of every session**, while Blender still answers:
   `bpy.app.binary_path` (the exact `blender.exe`, so nothing has to be guessed for a non-default install)
   and `bpy.data.filepath`. Also save the .blend before each risky script step; a crash loses the rest.
2. **Read the crash log**: `%TEMP%\<blend name>.crash.txt` (stack trace plus the last operators run). A
   trace through `pyrna_prop_collection_iter_next` means a loop over a live collection while data changed
   (`bpy-recipes.md`, "Moving parts between .blend files").
3. **Ask before restarting** unless the user already said to: it closes their other work and may need
   permission to start a process. If allowed, relaunch with the launcher beside the recorded path (see the
   `blender-launcher.exe` note below), for example
   `Start-Process "<folder of binary_path>\blender-launcher.exe" -ArgumentList '"<blend path>"'` (PowerShell).
   Only the saved state comes back; check `bpy.data.filepath` and the scene list, then redo anything after
   the last save. Tested: after `Stop-Process -Force` on `blender.exe`, the file reopened and the MCP answered
   again within about 20 seconds with no click, on an install where the add-on auto-starts its server
   (five times; `blender-launcher.exe` on the last two).
4. **Reconnect**: poll `get_addon_status` for a short while. If it never answers, the add-on's server is not
   auto-starting on this machine (some installs start it automatically, others do not). Tell the user to open the
   side panel (N) in Blender and press Start MCP Server, or enable the add-on's auto-start option if its
   preferences have one. Do not loop restarts.
- **A crash dialog blocks the MCP** [HARD, seen on Windows, Blender 4.5.10]: when Blender crashes, its error
  dialog stays open and the MCP call does not fail; it just waits for a result that never comes. If a call
  hangs, ask the user whether a Blender error window is open; once they close it or click Restart, read the
  crash log and go on from step 3.
- **Check which file reopened** [HARD, seen]: after a crash restart Blender may open an autosave from `%TEMP%`
  instead of the user's file. Compare `bpy.data.filepath` with the path recorded in step 1 and open the right
  one with `bpy.ops.wm.open_mainfile(filepath=...)`.
5. If the recorded path is missing (context lost too), look in `C:\Program Files\Blender Foundation\`,
   the Steam library (`steamapps\common\Blender`), or ask the user; do not search the whole drive.

- **Relaunch with `blender-launcher.exe`, not `blender.exe`** [HARD, tested on Windows 11, Blender 4.5.10]:
  `blender.exe` opens a console window (Windows Terminal on Windows 11) that stays open for the whole session.
  SEUT's tools (MwmBuilder, Havok) run for a fraction of a second and write their progress into that console's
  title bar (`MwmBuilder: 100.0%`), which makes it look like an MwmBuilder window. Closing that window closes
  Blender with no `.crash.txt`. `blender-launcher.exe` in the same folder starts Blender with no console at all,
  and exports still work. Derive its path from `bpy.app.binary_path` (same folder). If Blender was started
  with a console anyway, tell the user not to close it; `Toggle System Console` did not hide it here.
  A Blender that vanishes with no `.crash.txt` was probably closed by the user or by closing that console.

## Pre-export checklist

1. .blend saved (E008), SubtypeId set and unique in the file (E004, E018), ASCII names (E033).
2. Every mesh has a valid UV map with real coordinates (E032, E042, W002) and no empty meshes (W013). This
   includes highlight target meshes and collision meshes (collision UVs: E044).
3. Materials: no custom node trees (E053), texture paths contain `Textures\` (E007), valid resolutions (W004).
4. Collision: at most 10 objects (E022), modifiers applied (E034), rigid body shape allowed (E054), no
   external HKT plus objects (E055), all inside the bounding box.
4a. Each `detector_*` empty covers the whole mesh it highlights (aim areas smaller than the mesh leave dead
   spots in game; `references/interaction-highlights.md`).
5. Each exported collection has one unparented top-level object (E031); LOD indexes continuous (E006) and
   distances increasing (E011).
6. Paths: Export Folder contains `Models\` (E014), Mod folder set and model path inside it (E045),
   MwmBuilder and Havok paths valid in Addon Preferences (E012, E013).

## Errors with a fix

| Code | Meaning | Fix |
|---|---|---|
| E002 | SEUT collection missing, excluded or empty | Recreate Collections; include it in the view layer |
| E004 | no SubtypeId | set `scene.seut.subtypeId` |
| E005 | subpart instancing loop | remove the circular subpart link |
| E006 | collection indexes missing | restore the gap (e.g. LOD2 without LOD1) |
| E007 | texture path lacks `Textures\` | move TIF under a `Textures` folder |
| E008 | .blend unsaved | save |
| E011 | LOD distance order wrong | raise the higher LOD's distance |
| E012 / E013 | tool path invalid or wrong file | fix Addon Preferences |
| E014 | export path lacks `Models\` | set Export Folder inside `...\Models\` |
| E017 | FBX exporter RuntimeError | leave Edit Mode, export again |
| E018 | duplicate SubtypeId | rename |
| E022 | over 10 collision objects | merge into convex pieces |
| E023 | mirror empty rotation invalid | try another axis combination |
| E031 | collection has several top-level objects | parent them under one object |
| E032 / E042 | missing or broken UV map | unwrap; UV verts all at (0,0) means broken |
| E033 | non-ASCII characters | rename to ASCII |
| E034 | collision has unapplied modifiers | apply them |
| E037 | Havok `hctFilterManager.dll` not found | install Havok Content Tools 2013 |
| E039 / E050 | Assimp32.dll / VC++ redist missing | install .NET 3.5 SP1, VC++ 2012 x86 |
| E043 / E044 | MWM conversion failed | read `*.mwm.log` (turn `Delete Temporary Files` off first). Seen: `Mesh 'pc' has no UV map/channel` for `<SubtypeId>.hkt.fbx` means a collision mesh has no UVs or all UVs at (0,0): MwmBuilder builds the collision FBX too, so give collision meshes a real UV map (Blender's primitives have one). The main `.mwm` is still written, but without the collision |
| E045 | model path outside mod folder | fix Mod / Export paths |
| E046 | DDS conversion failed | check texture file and `texconv` |
| E053 | custom node tree | use SEUT material; change textures instead |
| E054 | rigid body shape COMPOUND | Box / Sphere / Capsule / Cylinder / Convex Hull |
| E055 | external HKT and objects both present | clear one |

Other codes (E001, E003, E009, E010, E015, E016, E019-E021, E024-E030, E035, E036, E038, E040, E041, E047-E049,
E051, E052) cover import, planets, animation, armatures and tool setup; read the message, it names the target.

## Warnings

| Code | Meaning |
|---|---|
| W001 / W020 | subpart grid size differs from parent / subpart empties cannot export to another grid |
| W002 | many UV verts at (0,0), shading may break |
| W004 | texture resolution not power of two |
| W005-W007 | empty without parent / parent has parent / highlight parent mismatch |
| W012 | DLC material: model must be DLC-locked |
| W013 | object without geometry |
| W014 / W019 | texture slot empty / texture unsupported by the technique |
