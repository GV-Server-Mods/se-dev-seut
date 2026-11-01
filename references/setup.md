# Setup from scratch, first model, testing in game

Read this when the user has not installed Blender or SEUT yet, when an export fails on a path or missing tool
(E012, E013, missing textures), or when they ask how to get a first block into the game.

Sources: the SEUT Installation Guide and Addon Preferences wiki pages, plus the YouTube series by
**Chipstix213** (SEUT setup for Blender, The First Model, The Next Steps), read from auto-generated
transcripts. The series used Blender 3.0; the wiki now says 4.0 or newer and this skill was tested on 4.5 with
SEUT 1.2.1, so menus differ a little. Transcript errors are likely, so only steps that agree with the wiki or the
add-on source are kept. Guide pages:
`spaceengineers.wiki.gg/wiki/Modding/Tutorials/Tools/SEUT/Installation_Guide` and
`.../Modding/Reference/Tools/SEUT/Addon_Preferences`.

## Contents
- What to check first
- Install order
- First-run configuration
- Checking the install works
- First model to game
- Testing in game

## What to check first

The agent cannot install Blender or Windows components for the user. Check what exists, then walk the user
through only what is missing:

1. Is Blender open and reachable (`get_addon_status`)? If there is no Blender MCP, this skill still helps
   with rules and file contents, but live modelling needs the MCP add-on.
2. Is SEUT enabled (a "SEUT" tab in the 3D viewport sidebar, N key)? Is the Space Engineers version 1
   game installed (Steam)?
3. Are the preferences set (below)? A model that exports fine but has grey or missing textures usually means
   the textures were never converted.

## Install order [HARD, wiki; video agrees]

1. **Space Engineers ModSDK**: Steam Library, enable the Tools filter, search "Space Engineers", install
   "Space Engineers ModSDK". Its `OriginalContent` folder holds the vanilla models as FBX, `.hkt` physics files
   and material XML; these are what `kitbash.md` imports.
2. **Havok Content Tools** (old software, link on the wiki page): install it like any other program and note
   the exact install folder. Do not move it afterwards, or collision export breaks.
3. **.NET Framework 3.5** and the **Visual C++ 2012 redistributable**, needed by the build tools.
4. **Blender** (4.0 or newer; 4.5 is what this skill was tested on).
5. **The SEUT zip** (latest release from the SEUT GitHub releases page). Do not extract it. In Blender:
   Edit > Preferences > Add-ons > Install (the install button is under the dropdown arrow on newer Blender),
   pick the zip, tick the add-on ("Scene: Space Engineers Utilities").
6. **Pillow** (optional): a Python library for reading and writing pictures, used by some recipes here
   (measuring a reference image, `scripts/annotate_atlas.py`, the icon fallback). Install it into a normal
   Python with `python -m pip install pillow`. Without it, Blender's image loader and, on Windows, PowerShell's
   `System.Drawing` cover the reading.

## First-run configuration [HARD, wiki Addon Preferences]

In the add-on preferences:

1. **Game Directory**: the Space Engineers folder, normally
   `C:\Program Files (x86)\Steam\steamapps\common\SpaceEngineers\`.
2. **Asset Directory**: an empty folder with at least 15 GB free, outside the game and ModSDK folders (the
   video author used a folder in Documents). SEUT stores converted textures and its material library here.
3. Open the Blender **System Console** (Window menu) first, then press **Update Textures from Game Files**.
   It converts every game texture and takes 30 minutes or more; Blender looks frozen meanwhile and the console
   shows progress.
4. **Assets** and **MwmBuilder**: press Download & Install on each and wait until both say up to date. A
   "Rate Limit Exceeded" message is GitHub throttling; wait 30 to 60 minutes.
5. **Havok Standalone Filter Manager**: point it at `hctStandAloneFilterManager.exe` in the Havok install
   folder (64-bit, so normally under `Program Files`, not `Program Files (x86)`).

## Checking the install works [HARD, video; matches the skill's own tests]

In the 3D viewport sidebar open the SEUT tab and press Initialize SEUT Scene. Delete the unneeded extra
collection if one appears. Then import a vanilla model from the ModSDK `OriginalContent\Models` folder
(for example the small cargo container; for a glass test, a hydrogen generator) with SEUT's FBX import, and
switch the viewport to material preview. It should look like the game, with textures and glass. If it is
grey, the texture conversion did not finish or the Asset Directory is wrong.

## First model to game [HARD for steps the skill has run; the rest from the video]

1. Create the scene: a Main scene type, a unique SubtypeId (changing it renames the scene and collections,
   which confirms SEUT noticed), grid scale, bounding box. The default collections are Main, Collision,
   BS1 to BS3, three LODs and one build-stage LOD; add more with Create Collection, rebuild the set with
   Recreate Collections.
2. Model, UV, collision, LODs, build stages (`modeling-rules.md`, `block-scenes.md`).
3. Mirroring and mountpoints (`modeling-rules.md`): turn the mode on, adjust, turn it off to save.
4. Export panel options: `Export All Scenes` or just the current one; `Delete Temporary Files`; the SBC mode
   none, update or new (the video author leaves it on update; details in `bpy-recipes.md`); the export size.
   Export size large to large, large to small (scales the model down and shrinks the box size for the small
   grid), or large to medium (no scaling). A normal large block exports large to large. Export Materials is
   an advanced option for adding materials to the asset manager.
5. Import options: Import FBX for one model (for example from the ModSDK), and `Import Complete` for a block
   with all its build-stage and LOD files in one step; pointing it at the parent model finds the rest.
6. Icon: `bpy-recipes.md` ("Icons") describes SEUT's icon render mode. DDS is the best format: it loads fast
   and uses less memory. Icon style: the blue filter is SEUT's default and matches today's vanilla icons; the
   owner says the Warfare III update (next month, written 2026-10) moves all vanilla icons to full colour, so
   prefer the full-colour option for new blocks.
7. Put the exported `Data` and `Models` folders (and `Textures` for the icon) in a mod folder under
   `%APPDATA%\SpaceEngineers\Mods\<ModName>`. The SBC `Icon` path must point at the `.dds`.
8. For real use replace the raw `{LOC:...}` or plain names with a localization file, which also makes the
   mod usable by non-English players.

## Testing in game [owner and video]

- A local mod shows with a small house symbol in the mod list. For a model test choose an empty world; the video
  author often uses a survival-style world with creative tools enabled, which makes build stages and
  inventories easier to see.
- In the advanced world settings switch off what a block test does not need (asteroids, weather, bounty
  contracts, respawn ships and similar) so the world loads faster. Space Engineers does not accept most model
  changes on the fly, so the video author reloads the world often.
- The owner's faster loop for simple model and texture changes: the Debug Draw "Reload models" and "Reload
  textures" buttons (Alt+F11 offline singleplayer); a full game restart is still needed for subpart, dummy and
  collision changes (`SKILL.md`, step 8).
- Search the block by name in the G menu, drag it to the toolbar, place it, check collision, and use a
  grinder to step through the build stages. A new block with no localization shows its raw `DisplayName`.
- Inventory size changes need a newly placed block, because blocks already in the world keep the inventory
  they were built with.
