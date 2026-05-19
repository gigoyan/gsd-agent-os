---
name: gsd-sync-blueprint
description: Safely install or update reusable GSD blueprint assets into a project repository using the blueprint manifest while preserving project-owned runtime artifacts. Use when a project repo needs the latest GSD skills, templates, contracts, managed AGENTS.md blocks, or when updating from a newer blueprint version.
---

# GSD Sync Blueprint

Sync reusable GSD blueprint assets into a project repository without overwriting project-specific runtime information.

## Source Of Truth

- Use `.gsd/blueprint-manifest.json` from the blueprint source repository.
- Use `.planning/templates/blueprint-distribution-contract.md` for ownership and sync safety rules.
- Use `.gsd/blueprint.lock.json` in the target project repository when present.

## Primary Purpose

- Install or update reusable GSD workflow assets.
- Preserve project-owned runtime artifacts.
- Replace only blueprint-owned files.
- Update only marked managed blocks in approved mixed files.
- For hybrid starter surfaces, create missing files but update only reusable guidance blocks when files already exist.
- Report all changes clearly.

## Trigger Conditions

- User asks to update GSD in a project repository from the blueprint.
- User asks to install GSD into a repository.
- Blueprint skills, templates, contracts, or reusable guidance changed.
- Project repository has an older `.gsd/blueprint.lock.json`.
- User wants to apply changes such as new skills, Obsidian integration updates, context-index updates, or workflow rule changes across repositories.

## Non-Trigger Conditions

- User wants to execute project work.
- User wants to plan a milestone.
- User wants to edit project-specific artifacts.
- User wants to update Obsidian vault memory.
- User wants to generate project-local `.codex` configuration after stack selection.

## Input Contract

- Blueprint source path.
- Target project repository path.
- Sync mode: `install`, `update`, or `audit-only`.
- Optional target blueprint version or commit.
- Optional allowlist of files or categories to sync.
- Optional explicit approval for managed-block replacement.

## Output Contract

- Sync plan before changes when changes are non-trivial.
- Files created.
- Files replaced.
- Managed blocks updated.
- Bootstrap-then-managed-block guidance blocks updated.
- Files preserved.
- Files skipped.
- Conflicts or unresolved ownership.
- Updated `.gsd/blueprint.lock.json` when install or update succeeds.
- Verification checks run.

## Workflow

1. Read the blueprint manifest from `.gsd/blueprint-manifest.json`.
2. Read the blueprint distribution contract.
3. Read the target project `.gsd/blueprint.lock.json` if it exists.
4. Classify the sync as:
   - `install`: target project has no lock or no GSD files.
   - `update`: target project already has GSD installed.
   - `audit-only`: report drift without changing files.
5. For each manifest entry, determine the effective action:
   - `README.md`: always treat the target project README as project-owned; never create, overwrite, replace, or managed-block-update it.
   - `blueprint_replace` + `replace`: compare and replace from blueprint when different, but only after producing and reviewing a diff summary.
   - `bootstrap_then_managed_block` + `bootstrap_then_managed_block`: create the full starter file only if missing; if present, update only the matching `GSD-BLUEPRINT` block and preserve all `GSD-PROJECT` content exactly.
   - `bootstrap_if_missing` + `create_if_missing`: create only if missing; otherwise preserve.
   - `managed_block` + `managed_block`: update only matching marker blocks.
   - `project_preserve` + `preserve`: never overwrite.
   - `generated_project_local` + `ignore`: do not touch.
6. Before modifying target files, produce a concise sync plan unless the user explicitly requested direct execution and the change is obviously safe.
7. Stop and ask for approval if:
   - a project-owned file would be overwritten
   - a managed block marker is malformed
   - a `bootstrap_then_managed_block` target such as `PROJECT.md` or `.planning/CODEBASE_MAP.md` is missing expected markers and needs marker insertion
   - target has local edits inside a managed block and replacement is not explicitly approved
   - ownership is unknown
   - the sync would delete files
8. Apply approved changes.
9. Update or create `.gsd/blueprint.lock.json` in the target project with blueprint version, commit if known, timestamp, source path, target path, and file actions.
10. Run lightweight verification:
    - manifest is valid JSON
    - required blueprint files exist in target after sync
    - project-preserve files were not overwritten
    - `bootstrap_then_managed_block` project blocks were preserved exactly
    - managed block markers are balanced
    - no `.codex` generated project-local files were modified
    - target `README.md` was not created, overwritten, replaced, or managed-block-updated
11. Return a final summary.

## Managed Block Rules

- Replace only content between matching marker comments.
- Preserve all content outside markers.
- `AGENTS.md` remains a `managed_block` file. `PROJECT.md` and `.planning/CODEBASE_MAP.md` use the separate `bootstrap_then_managed_block` strategy.
- Never apply managed-block rules to target project `README.md`.
- If the target file lacks the managed block, propose insertion.
- If the target file has malformed markers, stop and report conflict.
- If multiple blocks with the same block ID exist, stop and report conflict.

## Bootstrap-Then-Managed-Block Rules

- Apply this strategy only to manifest entries that explicitly use `bootstrap_then_managed_block`, including `PROJECT.md` and `.planning/CODEBASE_MAP.md`.
- If the target file is missing, create the full starter file from the blueprint source.
- If the target file exists, update only the matching `GSD-BLUEPRINT` block from the blueprint source.
- Preserve every `GSD-PROJECT` block exactly, including whitespace and ordering.
- Preserve all other target content outside the updated `GSD-BLUEPRINT` block unless the user explicitly approves a marker insertion diff.
- If required markers are missing, produce a diff plan showing the proposed `GSD-BLUEPRINT` and `GSD-PROJECT` marker insertion and require explicit approval before editing.
- If markers are malformed or duplicated, stop and report a conflict.
- Never overwrite existing project content in order to install the new block structure.
- Never update an existing `.planning/STATE.md`; state remains `bootstrap_if_missing` / `create_if_missing` only and must not use managed blocks.

## Safety Rules

- Never overwrite project runtime artifacts.
- Never create, overwrite, replace, or managed-block-update target `README.md`.
- If target `README.md` is missing, report it as project-owned and not managed by GSD sync.
- Do not treat missing `README.md` as a missing required GSD file.
- Never sync milestone, phase, verification, roadmap history, state history, CONTEXT_INDEX, or existing `.planning/STATE.md` over an existing project copy.
- Never sync `PROJECT.md` or `.planning/CODEBASE_MAP.md` over an existing project copy; update only their `GSD-BLUEPRINT` guidance blocks through `bootstrap_then_managed_block`.
- Never write Obsidian vault memory.
- Never update generated `.codex` project-local files.
- Never delete target files unless the user explicitly approves deletion in the current task.
- If unsure, preserve and report.

## Completion Check

- Blueprint-owned files were updated or confirmed current.
- Project-owned files were preserved.
- Managed blocks were updated only inside markers.
- Bootstrap-then-managed-block files were created only when missing or had only their `GSD-BLUEPRINT` guidance blocks updated.
- Existing `PROJECT.md`, `.planning/CODEBASE_MAP.md`, and `.planning/STATE.md` project-owned content was preserved.
- Lock file was created or updated when changes were applied.
- Verification reported no overwrite of project runtime files.
