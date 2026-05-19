---
name: gsd-vault-bootstrap
description: Initialize or repair the baseline GSD vault scaffold for the active repository inside the shared Obsidian MCP vault root under projects/<vault-project-id>. Use when a repository needs its project namespace and home/atlas/knowledge/sessions/inbox structure, the scaffold is missing or incomplete, or a reset/repair is explicitly requested.
---

# GSD Vault Bootstrap

Use this skill only for vault scaffold initialization and repair.
It does not retrieve memory and it does not write session or decision notes.

## Namespace Resolution

Before creating, repairing, or verifying anything:

1. Resolve `<vault-project-id>` from the active repository:
   - Prefer `PROJECT.md` -> `GSD Vault Project ID`.
   - If missing, derive it from the repository root folder name.
   - Preserve the repository folder name except replace filesystem-invalid path characters with `-`.
2. Set the active project namespace to:

    projects/<vault-project-id>/

3. Treat every scaffold path as relative to that namespace.
4. Do not create scaffold files directly under the shared vault root.
5. If the namespace exists but appears to belong to a different repository, stop and ask the user for an explicit override.
6. After successful create or verify, ensure `PROJECT.md` records:
   - `GSD Vault Project ID`
   - `GSD Vault Namespace`
   - `Vault scaffold status`

## Source Of Truth
- Use [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md) as the exact structure and boundary contract.
- Use [`.planning/templates/vault-scaffold/`](../../../.planning/templates/vault-scaffold/) as the source for fixed home and atlas files.

## Primary Purpose
- Create or repair the minimum durable-vault scaffold that future GSD work can rely on.
- Keep the scope limited to structure, baseline paths, and scaffold integrity.

## Trigger Conditions
- A greenfield repository needs the baseline vault structure.
- The baseline vault structure is missing or materially incomplete.
- A reset or repair of the scaffold is explicitly requested.

## Non-Trigger Conditions
- The user only needs memory lookup.
- The user only needs durable writeback.
- The vault scaffold already exists and no structural repair is needed.
- The request is about planning, execution, verification, or orchestration rather than vault layout.

## Input Contract
- Repository path.
- Shared Obsidian MCP vault root availability.
- Current `GSD Vault Project ID` from `PROJECT.md`, if present.
- Derived repository folder name, if the project ID is missing.
- Requested bootstrap mode, such as create, repair, or verify-only.
- Active project namespace, which must resolve to `projects/<vault-project-id>/`.
- Minimum structural target, which must exist under `projects/<vault-project-id>/`:
  - `projects/<vault-project-id>/00-home/index.md`
  - `projects/<vault-project-id>/00-home/current priorities.md`
  - `projects/<vault-project-id>/atlas/project architecture.md`
  - `projects/<vault-project-id>/atlas/tech stack.md`
  - `projects/<vault-project-id>/atlas/database.md`
  - `projects/<vault-project-id>/atlas/deployment.md`
  - `projects/<vault-project-id>/knowledge/integrations/`
  - `projects/<vault-project-id>/knowledge/decisions/`
  - `projects/<vault-project-id>/knowledge/debugging/`
  - `projects/<vault-project-id>/knowledge/patterns/`
  - `projects/<vault-project-id>/knowledge/business/`
  - `projects/<vault-project-id>/sessions/`
  - `projects/<vault-project-id>/inbox/`

## Output Contract
- Scaffold-ready path list.
- Created-or-verified structure summary, including the fixed files and subdirectories above.
- Missing baseline elements, if any remain.
- A short repair note when the baseline could not be fully satisfied.

## Boundary Limits
- No retrieval summary.
- No session note writing.
- No decision note writing.
- No orchestration beyond scaffold initialization and repair.
- No changes to existing GSD workflow roles.
- No invention of alternate vault categories, extra fixed notes, or alternate filenames for the required home and atlas files.
- Vault bootstrap does not create, update, or repair `.planning/CONTEXT_INDEX.md`; context routing is repo-local and handled by `$gsd-refresh-context-index`.

## Handoff Rules
- If the scaffold is already sufficient, report that fact and stop.
- When bootstrapping, create or verify only the fixed scaffold and directories:
  - copy the fixed home and atlas notes from the scaffold templates
  - create the required `knowledge/` subdirectories
  - create empty `sessions/` and `inbox/` directories
- Do not create decision, debugging, integration, pattern, business, or session notes here.
- If broader memory behavior is needed, hand off to `gsd-memory-lookup` or `gsd-session-save` instead of expanding scope here.
