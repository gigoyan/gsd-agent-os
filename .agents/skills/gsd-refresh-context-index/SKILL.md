---
name: gsd-refresh-context-index
description: Create or refresh the repo-local CONTEXT_INDEX.md task-routing guide so Codex can plan, execute, verify, quick-task, and orchestrate with minimal relevant context instead of broad repository scanning. Use after gsd-map-codebase or gsd-deep-map-codebase, when repository structure changes, when agents repeatedly inspect too many files, or before non-trivial work if the context index is missing, placeholder, stale, or insufficient for the active task.
---

# GSD Refresh Context Index

Build or refresh the compact repository navigation guide used by GSD agents to minimize unnecessary scanning.

This skill does not implement features, verify phases, write vault memory, or replace `CODEBASE_MAP.md`.
Its only job is to produce a precise routing index for future GSD work.

## Source Of Truth

- Use [`.planning/templates/context-index-template.md`](../../../.planning/templates/context-index-template.md) as the output structure.
- Use [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) as the first repository understanding source when available.
- Use [PROJECT.md](../../../PROJECT.md), [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), and [`.planning/STATE.md`](../../../.planning/STATE.md) as workflow context.
- Use Project Idea Document, Technical Specification, and stack-selection/configuration-package artifacts when they exist and are current.
- Use direct repo inspection only to verify or fill routing gaps, not to perform a new exhaustive mapping pass unless the existing map is insufficient.
- Treat actual repo evidence as stronger than the existing context index. If `.planning/CONTEXT_INDEX.md` conflicts with observed files, commands, or current planning artifacts, refresh the index rather than following stale routing.
- Treat `GSD-BLUEPRINT` guidance blocks in `PROJECT.md` and `.planning/CODEBASE_MAP.md` as workflow instructions, not application or repository content to route.

## Primary Purpose

- Create or refresh [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md).
- Turn existing repository knowledge into task-routing guidance.
- Tell future agents where to start, what to inspect next, what usually changes, how to validate, and what to avoid.
- Reduce token usage from repeated broad file discovery.

## Trigger Conditions

- `.planning/CONTEXT_INDEX.md` is missing, placeholder, stale, or incomplete.
- `gsd-map-codebase` or `gsd-deep-map-codebase` has completed and routing guidance needs to be generated.
- The repository structure, module boundaries, commands, validation paths, or stack changed.
- A prior planning, execution, verification, quick-task, or run-milestone flow scanned too broadly.
- A phase or milestone needs targeted context routing before work begins.
- The user explicitly asks to optimize agent navigation, reduce token usage, or build a context index.

## Non-Trigger Conditions

- The repository has not started and has no meaningful structure.
- The user only needs project bootstrap.
- The user only needs durable vault memory lookup or save.
- The current task is trivial and the relevant file is already explicitly known.
- The request is to implement, verify, or plan a feature rather than improve routing.

## Input Contract

- Current repository path.
- Current task or reason for refresh.
- Current `.planning/CODEBASE_MAP.md`, if present.
- Existing `.planning/CONTEXT_INDEX.md`, if present.
- Known active milestone or phase, if refresh is task-specific.
- Relevant repo evidence needed to fill routing gaps.
- Known command capability notes from `.planning/tool-capabilities.md`, if present.

## Output Contract

- Updated [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md).
- A concise summary of:
  - routing rows added or changed
  - module cards added or changed
  - validation paths added or changed
  - do-not-scan boundaries added or changed
  - stale or unknown sections that remain
- No code implementation.
- No durable vault write.
- No milestone or phase creation.

## Workflow

1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md), and existing [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md) if present.
2. Read [`.planning/templates/context-index-template.md`](../../../.planning/templates/context-index-template.md).
3. If the repository has no meaningful structure yet, do not create a fake detailed index. Create only the placeholder or stop with an explicit note that the context index should be created after structure exists.
4. Determine refresh scope:
   - full index refresh
   - targeted module refresh
   - task-specific routing refresh
   - validation-path refresh
   - command/tool capability refresh
5. Prefer existing mapped knowledge from the project-owned content in `CODEBASE_MAP.md`. Ignore any `GSD-BLUEPRINT` guidance block as application content. Use direct repo inspection only where routing guidance is missing, stale, or contradicted.
6. Extract task-routing rows for common task types that are real for this repository. Do not keep irrelevant generic rows as if they are confirmed.
7. Create or update module routing cards for the main modules, services, apps, packages, or workflow areas. Keep each card compact.
8. Create or update the validation matrix from actual repo commands, test locations, and known check surfaces.
9. Create or update search recipes for common discovery tasks in this repository.
10. Add do-not-scan boundaries for generated files, vendor folders, unrelated apps, unrelated services, build outputs, migrations, or other areas that should not be inspected unless task-relevant.
11. Preserve evidence status:
    - `Confirmed` for directly observed repo facts or explicit user decisions.
    - `Suggested` for best routes inferred from structure but not fully proven.
    - `Unknown` for missing, contradictory, or unverified routing.
12. Write [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md) using the template.
13. Update [`.planning/STATE.md`](../../../.planning/STATE.md) only if this refresh is part of an active GSD workflow and the state needs to record the index refresh result.
14. End with a compact summary and, only when needed, a `Next-Step Prompt` that returns to the interrupted GSD action.

## Routing Content Rules

- Keep the index compact. Prefer tables and short module cards over long prose.
- Make the index useful for action, not just explanation.
- Every routing row should answer:
  - start here
  - inspect next
  - usually changes
  - validation path
  - avoid unless needed
- Every module card should answer:
  - responsibility
  - main paths
  - entry points
  - common change types
  - local validation
  - avoid touching unless
- Every validation row should distinguish fast targeted checks from broader checks.
- Search recipes must describe a narrow search path, not broad repository scanning.

## Boundary Rules

- Do not write durable project memory.
- Do not update Obsidian vault notes.
- Exclude reusable GSD workflow assets from application task routing unless the active task is to modify GSD itself. In application repositories, `.agents/skills/**`, `.planning/templates/**`, and `.gsd/**` are workflow infrastructure, not application modules.
- Do not treat blueprint guidance blocks in `PROJECT.md` or `.planning/CODEBASE_MAP.md` as application content, architecture evidence, module boundaries, or validation paths.
- Do not replace `CODEBASE_MAP.md`.
- Do not create milestones, phases, or verification files.
- Do not invent module boundaries that repo evidence does not support.
- Do not promote `Suggested` routing to `Confirmed` without repo evidence or explicit user confirmation.
- Do not hardcode environment-specific absolute paths unless they are already project-local facts and necessary for routing.
- Do not include secrets, tokens, credentials, or private keys.
- Do not include raw command logs or large file inventories.

## Staleness Rules

Mark the context index as `stale` or `partial` when:

- major folders, services, modules, or packages changed
- build, test, lint, or run commands changed
- validation strategy changed
- stack or framework changed
- the active task repeatedly required files outside the expected routing row
- verification found the routing guidance misleading or incomplete
- the index still contains placeholders for important project areas

## Completion Check

- `.planning/CONTEXT_INDEX.md` exists.
- The index has a status, last refresh note, source basis, routing matrix, module cards, validation matrix, search recipes, and do-not-scan boundaries.
- The index helps future agents choose minimal context for common task types.
- Evidence status is preserved as `Confirmed`, `Suggested`, or `Unknown`.
- No durable vault memory was written.
- No implementation, verification, milestone planning, or orchestration was performed by this skill.
