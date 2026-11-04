# Versioning & Release Policy for se-dev-seut

This project follows **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

To keep releases consistent across human maintainers and AI coding agents, all releases and tag updates follow the rules below.

---

## 1. Version Number Criteria

### A. PATCH (`1.0.0` -> `1.0.1`): Corrections & Documentation Polish
Bump the **Patch** number for backward-compatible corrections.

**Qualifying changes:**
- Fixing a wrong fact, name, path or snippet in `SKILL.md` or `references/`.
- Adding a newly seen SEUT error signature or gotcha to `references/errors.md`.
- Re-tagging a claim `[SOFT]` -> `[HARD]` (or back) after verifying it, without changing the guidance.
- Typos, broken links, formatting glitches in `README.md` and `references/`.

### B. MINOR (`1.0.0` -> `1.1.0`): New Coverage (Backward-Compatible)
Bump the **Minor** number when adding capability or coverage without breaking existing workflows.

**Qualifying changes:**
- A new reference guide (for example atlas region maps, animation, planets) or a new section in `SKILL.md`.
- Regenerating `references/vanilla-materials.md` and the table in `references/materials-catalog.md` after a SEUT asset update.
- Support for a new SEUT or Blender version, once re-verified against it.
- Verifying a previously unverified workflow (export, mirroring, mountpoints, in-game checks) and documenting it.

### C. MAJOR (`1.0.0` -> `2.0.0`): Breaking Changes
Bump the **Major** number when changes break paths or expectations that agents rely on.

**Qualifying changes:**
- Renaming or removing the skill or files in `references/` that other skills or agents link to.
- Dropping support for a SEUT or Blender version the skill previously targeted.
- Changing core guidance in a way that makes models built under the old guidance wrong.

---

## 2. Release & Tagging Checklist

1. **Verify against the install.** Open Blender with the SEUT version named in `references/sources.md` and re-run any
   recipe you changed in `references/bpy-recipes.md`. Do not tag changes you did not check.
2. **Keep shared content generic.** No server-specific profile names; server values only as labelled suggestions.
   Tag claims `[HARD]` (read in source or docs), `[SOFT]` (inferred or field-tested) or `[owner]` (seen in game
   or asked for by the user). One user's taste is not a rule: write it as a choice to ask about.
3. **Commit** with conventional messages and push (the git hooks run `sync-skills.ps1` to refresh the install clone):
   ```bash
   git add -A
   git commit -m "docs: add atlas region maps for the Atlas materials"
   git push origin main
   ```
4. **Tag the release** with an annotated tag and push it:
   ```bash
   git tag -a v1.1.0 -m "v1.1.0 - Atlas region maps"
   git push origin v1.1.0
   ```
5. **Publish a GitHub Release** with `gh release create v1.1.0 --title "..." --notes-file release_notes.md`.

---

## 3. Golden Rule on Published Tags
> [!IMPORTANT]
> **Never force-push or overwrite a published tag** once others may have cloned it. If a mistake is found right after a
> release, publish a Patch bump instead of moving the tag.
