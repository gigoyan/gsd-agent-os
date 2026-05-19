# Blueprint Distribution Contract

This contract defines how the reusable GSD blueprint is installed, synchronized, and audited across project repositories.

## Core Rule

Reusable GSD workflow assets may be updated from the blueprint.
Project runtime artifacts must be preserved.

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
- `PROJECT.md` and `.planning/CODEBASE_MAP.md` may receive reusable guidance updates only through `bootstrap_then_managed_block`; their project-owned content must be preserved exactly.
- Existing `.planning/STATE.md` is active runtime state. Blueprint sync may create it only when missing and must never update it when it exists.
- Target project `README.md` is project-owned. Blueprint sync must not create, overwrite, replace, or managed-block-update target `README.md`.
- A missing target `README.md` must not be treated as a missing GSD blueprint file.
- Reusable GSD usage guidance belongs in blueprint documentation, `AGENTS.md`, skills, templates, or contracts, not in target project `README.md`.
- Never overwrite files with uncommitted project changes without surfacing a diff and asking for approval.
- Never update `.codex` project-local outputs through blueprint sync.
- Never copy milestone, phase, verification, roadmap history, or state history from the blueprint into a project repository.
- Do not treat the Obsidian vault as the blueprint distribution channel.
- If ownership is unknown, preserve the file and report it as unresolved.

## Manifest And Lock

The blueprint repository owns:

    .gsd/blueprint-manifest.json

Each project repository owns:

    .gsd/blueprint.lock.json

The manifest defines what should be installed or updated.
The lock records what was installed.

## Managed Block Rules

For managed-block files:

- Replace only matching marker blocks.
- Preserve all content outside markers.
- `AGENTS.md` is the only project-facing mixed managed-block documentation file unless another file is explicitly approved later.
- Do not apply managed-block rules to target project `README.md`.
- If a marker start exists without an end marker, stop and report a conflict.
- If a project has local edits inside a managed block, report the diff before replacing.
- If no managed block exists, propose insertion but do not silently rewrite the full file.

## Bootstrap-Then-Managed-Block Rules

For bootstrap-then-managed-block files:

- Create the complete starter file only when the target file is missing.
- When the target file exists, replace only the matching `GSD-BLUEPRINT` block.
- Preserve all content outside the `GSD-BLUEPRINT` block, including every `GSD-PROJECT` block, byte-for-byte.
- If marker start or end comments are malformed, stop and report a conflict.
- If expected markers are missing, propose a marker insertion diff and require explicit approval before changing the file.
- Do not compare project-owned content as drift and do not use project-owned differences as permission to overwrite the file.
- `.planning/STATE.md` must not use managed blocks; it remains bootstrap-if-missing active runtime state.

## Drift Rules

Drift is allowed in project-owned files.
Drift in blueprint-owned files should be reported.
Drift in managed blocks should be reported by block ID.
Drift in bootstrap-then-managed-block files should be reported only for the `GSD-BLUEPRINT` block when markers exist.
Missing markers in bootstrap-then-managed-block files should be reported as a managed-block insertion requirement, not as permission to overwrite the whole file.

## Verification

A sync or audit must report:

- blueprint source version or commit
- project target path
- files replaced
- files created
- files preserved
- managed blocks updated
- conflicts
- skipped files
- verification checks run
