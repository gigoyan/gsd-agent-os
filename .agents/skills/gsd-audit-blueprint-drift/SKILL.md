---
name: gsd-audit-blueprint-drift
description: Compare a project repository's installed GSD files against the reusable blueprint manifest and report outdated, modified, missing, preserved, or conflicting files without applying changes. Use before syncing, during maintenance, or when checking whether a project repo has drifted from the blueprint.
---

# GSD Audit Blueprint Drift

Audit blueprint drift without modifying files.

## Source Of Truth

- Use `.gsd/blueprint-manifest.json` from the blueprint source repository.
- Use `.gsd/blueprint.lock.json` from the target project repository when present.
- Use `.planning/templates/blueprint-distribution-contract.md` for ownership rules.
- Use `.gsd/managed-blocks/agents-operating-contract.md` as the canonical source for the `AGENTS.md` `GSD-BLUEPRINT: operating-contract` managed block. The root blueprint `AGENTS.md` operating-contract block must match this file exactly.

## Primary Purpose

- Report whether a project repository is up to date with the blueprint.
- Identify outdated blueprint-owned files.
- Identify changed managed blocks.
- Identify changed reusable guidance blocks in bootstrap-then-managed-block starter surfaces.
- Preserve project-owned files.
- Produce a safe sync recommendation.

## Trigger Conditions

- User asks whether a project repo has the latest GSD.
- User wants to preview blueprint sync impact.
- User wants to detect drift before updating.
- User suspects manual changes were made to installed GSD files.

## Non-Trigger Conditions

- User wants to apply updates now. Use `gsd-sync-blueprint`.
- User wants to run project workflow.
- User wants to modify project-specific planning artifacts.

## Input Contract

- Blueprint source path.
- Target project repository path.
- Optional file/category allowlist.

## Output Contract

- Drift report.
- Missing blueprint files.
- Outdated blueprint-owned files.
- Managed block drift by block ID.
- Bootstrap-then-managed-block guidance drift by block ID.
- Project-owned files preserved and ignored.
- Unknown ownership findings.
- Recommended safe sync command or next prompt.

## Workflow

1. Read blueprint manifest.
2. Read target lock if present.
3. For each manifest entry:
   - if `README.md`, treat it as project-owned; do not compare it to the blueprint README and do not report a missing target README as a required blueprint or managed file
   - if `blueprint_replace`, compare blueprint source and project target content
   - if `managed_block`, compare only managed block content
   - if the managed-block entry is `AGENTS.md` and the target lacks `GSD-BLUEPRINT: operating-contract`, inspect for old unmarked GSD template or operating content before reporting a missing block
   - if `bootstrap_then_managed_block`, report missing files as create-if-missing; when the target exists, compare only the matching `GSD-BLUEPRINT` block and ignore all project-owned content
   - if `bootstrap_if_missing`, report missing or present; do not call present files drift
   - if `project_preserve`, report present/missing only when relevant; do not compare content for replacement
   - if `generated_project_local`, ignore except to confirm sync would not touch it
4. Report drift by severity:
   - blocking conflict
   - safe update available
   - missing optional file
   - missing required blueprint file
   - legacy-template migration requirement
   - preserved project-owned file
   - unknown ownership
5. Return a recommended `gsd-sync-blueprint` follow-up only when safe.

## Safety Rules

- Read-only only.
- Do not modify files.
- Do not update lock file.
- Do not write vault memory.
- Treat target `README.md` as project-owned. Preserve existing README content and ignore missing README as not managed by GSD.
- Treat existing `.planning/STATE.md` as preserved active runtime state. Report it as present or missing only; never compare its content and never recommend managed-block insertion.
- For `AGENTS.md`, detect old unmarked GSD content before reporting missing markers. Treat these as legacy signals when they appear outside managed markers: `# Codex-Native GSD Template`, `## Operating Mode` with GSD planning references, `## Task Triage` with `$gsd-quick-task`, `## Milestone Workflow`, `## State Management`, `## Output Contract`, or old unmarked lists of GSD skill invocations.
- If target `AGENTS.md` lacks the `operating-contract` block and contains old unmarked GSD template or operating content, report `AGENTS.md legacy-template migration required`, not a simple missing-block insertion.
- The audit must state that sync should show a reviewed migration diff replacing recognizable old unmarked GSD template content with the canonical operating-contract block plus the `GSD-PROJECT: local-settings` block, while preserving genuinely project-specific local instructions outside the old template content.
- For `bootstrap_then_managed_block`, report missing or malformed markers as a managed-block insertion requirement that needs review, not as permission to overwrite the file.
- Do not infer project runtime files should be overwritten.

## Completion Check

- Every manifest entry was classified.
- Drift report separates blueprint-owned drift from project-owned differences.
- Old unmarked GSD content in target `AGENTS.md` is reported as a legacy-template migration requirement, not as safe block insertion above the old content.
- `bootstrap_then_managed_block` entries report drift only for reusable `GSD-BLUEPRINT` blocks when target markers exist.
- No files were modified.
