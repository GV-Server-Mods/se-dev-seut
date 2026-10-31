# se-dev-seut: Space Engineers block modeling skill (Blender + SEUT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Space Engineers](https://img.shields.io/badge/Space%20Engineers-v1-blue.svg)](https://www.spaceengineersgame.com/)

An agent skill that helps AI coding assistants model Space Engineers (version 1) blocks in Blender with the
[Space Engineers Utilities (SEUT)](https://github.com/enenra/space-engineers-utilities) add-on, including
driving a live Blender through the Blender MCP.

It is not affiliated with Keen Software House or the SEUT authors. Facts come from SEUT's source, the
Space Engineers wiki, the ModSDK content, and checks run in Blender 4.5 with SEUT 1.2.1. Every claim in the
references is tagged **[HARD]** (read in source or docs) or **[SOFT]** (inferred, verify first), and
`references/sources.md` lists what is still unverified. Export and in-game behaviour have not been tested yet.

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
| `references/bpy-recipes.md` | Verified `bpy` snippets for SEUT scenes, materials and collision |
| `references/modeling-rules.md` | Geometry, collision, LODs, empties, mountpoints, mirroring |
| `references/block-scenes.md` | Ideal scene layout, vanilla LOD distances, build stages |
| `references/weapons-turrets.md` | Sorter turrets, subpart chains, muzzle and camera dummies |
| `references/interaction-highlights.md` | Highlight empties and the vanilla small cargo container example |
| `references/materials.md`, `materials-catalog.md`, `vanilla-materials.md` | Texture types, behaviour catalog, all 165 materials |
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

## License

MIT, see [LICENSE](./LICENSE).
