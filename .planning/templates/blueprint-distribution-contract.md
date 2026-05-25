# Blueprint Distribution Contract

This contract defines how the reusable GSD blueprint is audited, installed, and synchronized across project repositories.

## Core Rule

Reusable GSD workflow assets may be updated from the blueprint.
Project runtime artifacts must be preserved.
`$gsd-sync-blueprint` is the only Blueprint synchronization workflow. It owns `audit-only`, `install`, and `update` modes.
Every install or update starts with an audit plan and stops for explicit approval before any mutation.
There is no separate blueprint drift audit skill.

## Ownership Classes

### blueprint_replace
- Reusable blueprint truth.
- Safe to replace from the blueprint after diff review.
- Examples: `.agents/skills/**/SKILL.md`, `.planning/templates/**`.

### project_preserve
- Project runtime data.
- Never overwrite during blueprint sync.
- Examples: `README.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/CONTEXT_INDEX.md`, milestones, phases, verification artifacts.

### managed_block
- Mixed file containing blueprint-controlled blocks and project-specific content.
- Sync may replace only blocks wrapped with GSD blueprint markers.

Marker format:

    <!-- GSD-BLUEPRINT:START <block-id> -->
    blueprint-managed content
    <!-- GSD-BLUEPRINT:END <block-id> -->

### bootstrap_then_managed_block
- Hybrid starter surface with reusable guidance and project-owned runtime content.
- Create the full starter file only when the target file is missing.
- If the target file exists, update only the marked `GSD-BLUEPRINT` block from the blueprint source.
- Preserve all `GSD-PROJECT` content exactly.
- If required markers are missing, produce a proposed insertion diff and require explicit review before inserting markers.
- Do not use this strategy for active runtime state.
- Examples: `PROJECT.md`, `.planning/CODEBASE_MAP.md`.

### bootstrap_if_missing
- Starter file copied only when missing.
- Existing project file wins.
- `.planning/STATE.md` is active runtime state and must remain bootstrap-if-missing only. Existing project state must never be sync-updated.

### generated_project_local
- Generated for the current project only.
- Not synced from reusable blueprint.

## Sync Safety Rules

- Never overwrite project runtime artifacts during blueprint sync.
- Compare real content for Blueprint-owned files; file presence alone is not enough.
- Compare only marked Blueprint-managed block content for managed and bootstrap-then-managed-block files.
- `PROJECT.md` and `.planning/CODEBASE_MAP.md` may receive reusable guidance updates only through `bootstrap_then_managed_block`; their project-owned content must be preserved exactly.
- Existing `.planning/STATE.md` is active runtime state. Blueprint sync may create it only when missing and must never update it when it exists.
- Target project `README.md` is project-owned. Blueprint sync must not create, overwrite, replace, or managed-block-update target `README.md`.
- A missing target `README.md` must not be treated as a missing GSD blueprint file.
- Reusable GSD usage guidance belongs in blueprint documentation, `AGENTS.md`, skills, templates, or contracts, not in target project `README.md`.
- Never overwrite files with uncommitted project changes without surfacing a diff and asking for approval.
- Never update `.codex` project-local outputs through blueprint sync.
- Never copy milestone, phase, verification, roadmap history, or state history from the blueprint into a project repository.
- Detect files previously installed by Blueprint sync but removed from the current manifest by comparing target lock entries with the current source manifest.
- Do not delete anything unless it is a proven Blueprint-installed delete candidate, local modification can be safely ruled out, and the user explicitly approves deletion.
- Stop for explicit approval before file creation, replacement, managed-block updates, bootstrap guidance updates, marker insertion, legacy `AGENTS.md` migration, deletion, lock updates, or verification report writes.
- Do not treat the Obsidian vault as the blueprint distribution channel.
- If ownership is unknown, preserve the file and report it as unresolved.

## Manifest And Lock

The blueprint repository owns:

    .gsd/blueprint-manifest.json

The canonical reusable source for the `AGENTS.md` operating-contract managed block is:

    .gsd/managed-blocks/agents-operating-contract.md

The root blueprint `AGENTS.md` `GSD-BLUEPRINT: operating-contract` block must match that canonical file exactly.

Each project repository owns:

    .gsd/blueprint.lock.json

The manifest defines what should be installed or updated.
The lock records what was installed.
Lock entries for concrete installed files should include `path`, `owner`, `sync_strategy`, installed/source content hash when available, install/update action, and installed version/commit or timestamp when available.
The lock must support future checks for whether a file was installed by Blueprint sync, what hash was installed, whether the target is now locally modified, and whether the file was removed from the current manifest.

## Managed Block Rules

For managed-block files:

- Replace only matching marker blocks.
- Preserve all content outside markers.
- `AGENTS.md` is the only project-facing mixed managed-block documentation file unless another file is explicitly approved later.
- For `AGENTS.md`, use `.gsd/managed-blocks/agents-operating-contract.md` as the canonical source for the `operating-contract` block.
- Do not apply managed-block rules to target project `README.md`.
- If a marker start exists without an end marker, stop and report a conflict.
- If a project has local edits inside a managed block, report the diff before replacing.
- If no managed block exists, propose insertion but do not silently rewrite the full file.
- If target `AGENTS.md` has no `operating-contract` marker but contains old unmarked GSD template or operating content, do not insert the new block above the old content. Report `AGENTS.md legacy-template migration required`, show a reviewed diff that replaces the recognizable old GSD template content with the canonical managed block plus the `GSD-PROJECT: local-settings` block, preserve genuinely project-specific local instructions outside the old template content, and require explicit approval before applying the migration.
- If the boundary between old unmarked GSD template content and project-specific local instructions is ambiguous, stop and report a conflict rather than guessing.

## Bootstrap-Then-Managed-Block Rules

For bootstrap-then-managed-block files:

- Create the complete starter file only when the target file is missing.
- When the target file exists, replace only the matching `GSD-BLUEPRINT` block.
- Preserve all content outside the `GSD-BLUEPRINT` block, including every `GSD-PROJECT` block, byte-for-byte.
- If marker start or end comments are malformed, stop and report a conflict.
- If expected markers are missing, propose a marker insertion diff and require explicit approval before changing the file.
- Do not compare project-owned content as drift and do not use project-owned differences as permission to overwrite the file.
- `.planning/STATE.md` must not use managed blocks; it remains bootstrap-if-missing active runtime state.

## Audit And Drift Rules

- `audit-only` reports drift and sync candidates but performs no writes.
- Content drift is allowed in project-owned files and must not be treated as Blueprint sync drift.
- Drift in `blueprint_replace` files is detected by comparing full source and target content.
- Drift in managed blocks is detected by comparing only the marked block content by block ID.
- Drift in bootstrap-then-managed-block files is reported only for the `GSD-BLUEPRINT` block when markers exist.
- Missing markers in bootstrap-then-managed-block files must be reported as a marker insertion requirement, not as permission to overwrite the whole file.
- Generated project-local files are ignored, not compared.

## Removed-From-Manifest Rules

- Compare the target `.gsd/blueprint.lock.json` installed file list with the current source manifest file list.
- Report every lock entry absent from the current manifest under removed-from-manifest candidates.
- Classify each candidate as `delete candidate`, `preserve because project-owned/runtime`, `conflict because locally modified`, `ignore because generated_project_local`, or `unknown ownership`.
- Delete only concrete files previously installed by Blueprint sync, not protected by project/runtime/generated ownership, unchanged from the installed hash when hash evidence exists, and explicitly approved by the user.
- If local modification cannot be determined, preserve and report a manual-review conflict.
- Never delete managed-block host files, bootstrap/project surfaces, runtime/history files, generated project-local files, wildcard entries, or files not recorded in the lock.

## Verification

A sync or audit must report:

- blueprint source version or commit
- project target path
- mode: `audit-only`, `install`, or `update`
- content comparisons performed
- managed block comparisons performed
- bootstrap block comparisons performed
- removed-from-manifest files checked
- files replaced
- files created
- files deleted
- deletions applied or preserved
- files preserved
- managed blocks updated
- bootstrap guidance blocks updated
- conflicts
- skipped files
- approval obtained before mutations
- lock updated only after approved sync
- verification checks run
