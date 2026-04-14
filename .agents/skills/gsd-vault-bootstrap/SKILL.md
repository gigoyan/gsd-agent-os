---
name: gsd-vault-bootstrap
description: Initialize or repair the baseline vault scaffold for a project. Use when a repository needs the home/atlas/knowledge/sessions/inbox structure, the scaffold is missing or materially incomplete, or a reset/repair of the baseline vault layout is explicitly requested.
---

# GSD Vault Bootstrap

Use this skill only for vault scaffold initialization and repair.
It does not retrieve memory and it does not write session or decision notes.

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
- Current vault assumptions or existing vault path.
- Requested bootstrap mode, such as create, repair, or verify-only.
- Minimum structural target, which must map to the exact baseline:
  - `00-home/index.md`
  - `00-home/current priorities.md`
  - `atlas/project architecture.md`
  - `atlas/tech stack.md`
  - `atlas/database.md`
  - `atlas/deployment.md`
  - `knowledge/integrations/`
  - `knowledge/decisions/`
  - `knowledge/debugging/`
  - `knowledge/patterns/`
  - `knowledge/business/`
  - `sessions/`
  - `inbox/`

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

## Handoff Rules
- If the scaffold is already sufficient, report that fact and stop.
- When bootstrapping, create or verify only the fixed scaffold and directories:
  - copy the fixed home and atlas notes from the scaffold templates
  - create the required `knowledge/` subdirectories
  - create empty `sessions/` and `inbox/` directories
- Do not create decision, debugging, integration, pattern, business, or session notes here.
- If broader memory behavior is needed, hand off to `gsd-memory-lookup` or `gsd-session-save` instead of expanding scope here.
