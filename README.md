# se-dev-seut: Space Engineers block modeling skill (Blender + SEUT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Space Engineers](https://img.shields.io/badge/Space%20Engineers-v1-blue.svg)](https://www.spaceengineersgame.com/)

An agent skill that helps AI coding assistants model Space Engineers (version 1) blocks in Blender with the
[Space Engineers Utilities (SEUT)](https://github.com/enenra/space-engineers-utilities) add-on, including
driving a live Blender through the Blender MCP.

It is not affiliated with Keen Software House or the SEUT authors. Facts come from SEUT's source, the
Space Engineers wiki, the ModSDK content, and checks run in Blender 4.5 with SEUT 1.2.1. Every claim in the
references is tagged **[HARD]** (read in source or docs), **[SOFT]** (inferred, verify first) or **[owner]**
(seen in game or asked for by the person a model was built for), and `references/sources.md` lists what is
still unverified. Export through the Blender MCP was tested end to end (model, LODs, build stages, subparts,
collision, SBC, icon), and three blocks built with the skill were loaded in game: a test cube, a kitbashed
cargo crate and a WeaponCore gatling turret with subparts.

## What it covers

- SEUT scene, collection, grid, bounding box, mountpoint and mirroring setup, scripted through `bpy`.
- Collision rules, LOD and build-stage layout, subparts and dummies, turret and weapon models for
  ConveyorSorter blocks (WeaponCore, ToolCore).
- Reusing the 165 vanilla SEUT materials instead of baking textures, with a catalog of which materials are
  paintable, decal-style, or emissive and how emissive states drive glow.
- Interaction highlights (terminal, inventory, conveyor port) tied to real model parts.
- The SEUT error and warning catalog with a pre-export checklist.
- Working in a live Blender: look-and-fix loop, hard-surface building order, matching reference images.

## Files

| File | Scope |
| :--- | :--- |
| [`SKILL.md`](./SKILL.md) | Workflow, rules that fail silently, Blender MCP guidance, index of references |
| `references/pipeline.md` | Stage order of a whole build, builder scripts vs the .blend, the freeze |
| `references/bpy-recipes.md` | Verified `bpy` snippets for SEUT scenes, materials and collision |
| `references/modeling-rules.md` | Geometry, collision, LODs, empties, mountpoints, mirroring |
| `references/block-scenes.md` | Ideal scene layout, vanilla LOD distances, build stages |
| `references/doors-subparts.md` | Doors and animated subparts, advanced door definition fields |
| `references/characters-and-animation.md` | Outline for characters, creatures and handheld weapon animation controllers |
| `references/weapons-turrets.md` | Sorter turrets, subpart chains, muzzle and camera dummies |
| `references/interaction-highlights.md` | Highlight empties and the vanilla small cargo container example |
| `references/materials.md`, `materials-catalog.md`, `vanilla-materials.md` | Texture types, behaviour catalog, all 165 materials |
| `references/setup.md` | Installing Blender, SEUT, Havok and the ModSDK from scratch, first model, testing in game |
| `references/kitbash.md` | Import recipe for reusing vanilla model parts, tested |
| `references/atlas-regions.md` | UV boxes for each piece of the vanilla decal atlases (JSON copy: `atlas-regions.json`) |
| `scripts/` | Blender and Pillow scripts that regenerate the atlas region maps; `rebuild_check.py`, the whole-model drift check |
| `references/errors.md` | SEUT error codes and fixes |
| `references/hard-surface.md`, `reference-images.md` | Modeling technique and working from pictures |
| `references/sources.md` | Provenance and verification status |

## Versioning

Semantic Versioning; see [VERSIONING.md](./VERSIONING.md) for what counts as a patch, minor or major change and
the release checklist.

## Installation

Clone into your agent's skills folder, for example for Claude Code:

```bash
git clone https://github.com/GV-Server-Mods/se-dev-seut.git ~/.claude/skills/se-dev-seut
```

The Blender sections assume the [Blender MCP](https://mcp-for-blender.com/) add-on and a SEUT install; the
vanilla material paths assume SEUT's default asset folder, read from the add-on preferences.

## Credits

- Space Engineers Utilities (SEUT) belongs to its authors; the add-on's behaviour here was read from its
  source and the Space Engineers wiki.
- The install steps, first-model workflow, icon render and entity-component notes in `references/setup.md`
  draw on the YouTube tutorial series by **Chipstix213** (SEUT setup for Blender, The First Model, The Next
  Steps, Advanced Door parts 1 and 2, Custom Character, weapon animation controller), as do
  `references/doors-subparts.md` and `references/characters-and-animation.md`. The tip about exporting a grid
  from the game with Ctrl+Alt+E comes from the owner and credits Brd. Thank you for the walkthroughs.

## License

MIT, see [LICENSE](./LICENSE).
