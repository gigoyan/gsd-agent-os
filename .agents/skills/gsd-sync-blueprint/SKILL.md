---
name: gsd-sync-blueprint
description: Audit a target repository against the current reusable GSD blueprint, then perform approval-gated install or update sync with content comparison, managed-block comparison, and removed-file handling.
---

# GSD Sync Blueprint

`$gsd-sync-blueprint` is the only Blueprint audit and synchronization workflow.
It owns read-only audit reporting, first-time install, and update of installed Blueprint assets.
There is no separate Blueprint drift audit skill, wrapper skill, or compatibility alias.

## User-Facing Commands

```text
$gsd-sync-blueprint audit-only <TARGET_REPOSITORY_PATH>
$gsd-sync-blueprint install <TARGET_REPOSITORY_PATH>
$gsd-sync-blueprint update <TARGET_REPOSITORY_PATH>
```

## Modes

- `audit-only`: audit and report only. Stop after the audit plan. Do not create, update, delete, migrate, insert markers, or write a lock file.
- `install`: audit first, ask for explicit approval, then install only the approved starter and Blueprint-owned files.
- `update`: audit first, ask for explicit approval, then update only the approved Blueprint-owned content and safe removed-file cleanup.

If the user asks for a read-only audit, use `audit-only`.
If mode is omitted, infer `install` only when the target has no `.gsd/blueprint.lock.json` and no installed GSD evidence; otherwise infer `update`.
Report the inferred mode in the audit plan.

## Source Of Truth

- Treat the current working directory as the reusable GSD Blueprint source path.
- Verify the current working directory contains `.gsd/blueprint-manifest.json`. If it does not, stop with a clear error.
- Use `.gsd/blueprint-manifest.json` as the authoritative inventory and ownership source.
- Use `.planning/templates/blueprint-distribution-contract.md` for ownership and sync safety rules.
- Use `.gsd/managed-blocks/agents-operating-contract.md` as the canonical source for the target `AGENTS.md` `GSD-BLUEPRINT: operating-contract` managed block.
- Read `.gsd/blueprint.lock.json` in the target repository when present.
- Do not write Obsidian vault memory.

## Input Contract

- Accept one mode plus one target repository path, or one target repository path with mode inferred.
- Do not ask for or accept a separate Blueprint source path; the source is always the current working directory.
- Do not sync any external repository other than the single target path provided by the user.
- Before running repository commands, read `.planning/tool-capabilities.md` when present and follow any recorded fallbacks.

## Mandatory Audit-First Workflow

Every mode starts with the same audit phase. No mutation is allowed before the audit plan is produced.

1. Read the source Blueprint manifest.
2. Read the target Blueprint lock if present.
3. Classify every source manifest entry by ownership and sync strategy.
4. Compare source and target content according to the ownership rules below.
5. Detect target files previously installed from the Blueprint but removed from the current source manifest.
6. Produce the required Blueprint Sync Audit Plan.
7. For `audit-only`, stop here with no writes.
8. For `install` and `update`, stop for explicit user approval before applying any changes.
9. Apply only approved changes.
10. Update the lock and verification report only after approved sync changes are applied successfully.
11. Report exactly what changed, preserved, skipped, deleted, or conflicted.

## Required Audit Plan Output

The audit phase must produce this complete plan shape:

```text
Blueprint Sync Audit Plan

Mode:
Blueprint source:
Target repository:
Source manifest:
Target lock:

Files to create:
Files to replace because content changed:
Managed blocks to update because block content changed:
Bootstrap guidance blocks to update:
Previously installed Blueprint files removed from current manifest:
Files to preserve:
Files skipped:
Claude skill projection refresh: planned | not applicable
Conflicts / approval required:
Unsafe or ambiguous items:

Approval required before applying:
- replacements
- managed-block updates
- bootstrap guidance updates
- deletions
- legacy AGENTS migration
- marker insertion
- ambiguous ownership changes
```

The plan must distinguish:

- `safe update available`
- `deletion candidate`
- `conflict requiring manual review`
- `preserved project-owned file`
- `skipped generated/local file`
- `missing required file`
- `legacy marker migration required`
- `up to date`

Include a compact diff summary or changed-file marker for every content-changing replacement, managed-block update, bootstrap guidance update, marker insertion, migration, or deletion candidate.

## Content Comparison Rules

Presence is not enough. Audit must compare actual content whenever the ownership class permits comparison.

### `blueprint_replace`

- Compare full source file content against target file content.
- If the target file is missing, report `create`.
- If the target file exists and content differs, report `replace because content changed` with a concise diff summary or changed-file marker.
- If content is identical, report `up to date`.
- Apply creation or replacement only after explicit approval.
- Never treat a wildcard manifest entry as a concrete replace action.

### `managed_block`

- Compare only the marked Blueprint-managed block content.
- For `AGENTS.md`, compare the target `GSD-BLUEPRINT: operating-contract` block against `.gsd/managed-blocks/agents-operating-contract.md`.
- Replace only the matching `GSD-BLUEPRINT` block after approval.
- Preserve all content outside the managed block exactly.
- If markers are missing but old unmarked GSD operating content exists, report `AGENTS.md legacy-template migration required`, show the proposed migration plan, and require explicit approval.
- If marker start/end comments are malformed, duplicated, mismatched, or ambiguous, stop and report a conflict.
- If project-local content exists outside the managed block, preserve it byte-for-byte.

### `bootstrap_then_managed_block`

- If the target file is missing, report `create starter file`; apply only after approval.
- If the target file exists, compare only the `GSD-BLUEPRINT` guidance block.
- Update only that block after approval.
- Preserve all `GSD-PROJECT` blocks and other project-owned content byte-for-byte.
- If markers are missing, report `marker insertion required`, show the proposed insertion or migration plan, and require approval.
- Do not overwrite the whole file when project-owned content exists.
- For `CLAUDE.md`, create the starter only when missing; when present, update only the `GSD-BLUEPRINT: claude-runtime-adapter` block after approval and preserve `GSD-PROJECT: claude-local-settings` plus all other project-owned content byte-for-byte.

### `bootstrap_if_missing`

- If the target file is missing, report `create starter file`; apply only after approval.
- If the target file exists, preserve existing target content.
- Never compare existing target content as drift.
- Never overwrite existing target content.
- Treat active runtime files such as `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/CONTEXT_INDEX.md` as protected once present.

### `project_preserve`

- Never overwrite, replace, delete, or managed-block update.
- Report as preserved when relevant.
- Preserve runtime/history areas, including `README.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/CONTEXT_INDEX.md`, `.planning/milestones/**`, `.planning/phases/**`, `.planning/verification/**`, and `.planning/archive/**`.
- Use the manifest as source of truth for declared ownership, but if ownership is unclear or runtime/project-owned, preserve and report the ambiguity.

### `generated_project_local`

- Ignore for blueprint file sync.
- Do not compare.
- Do not copy from the Blueprint source.
- Do not delete.
- Examples include `.codex/**`, `.claude/settings.json`, `.claude/agents/**`, `.claude/skills/**`, `.claude/rules/**`, and `.claude/hooks/**`.
- `CLAUDE.md` is not generated_project_local; handle it as `bootstrap_then_managed_block`.
- `.claude/skills/**` GSD projections may change only through the separate Claude Runtime Projection Refresh step below, never through blueprint file copying.

## Claude Runtime Projection Refresh

Blueprint file sync never copies `.claude/**` outputs from the Blueprint source. The Claude Code skill surface (`.claude/skills/**`) is kept current through this separate, approval-covered refresh step instead.

During audit:

1. For `install` mode, always set `Claude skill projection refresh: planned` in the audit plan: install creates the required `CLAUDE.md` adapter, so the target will use the Claude Code runtime surface after apply even though `CLAUDE.md` and `.claude/` do not exist yet at audit time.
2. For `update` and `audit-only` modes, set `planned` when the target `CLAUDE.md` or target `.claude/` exists; otherwise set `not applicable`.

During apply, after approved file sync actions succeed:

1. Run the skills-only projection against the target using the target's freshly synced canonical skills:

```bash
python3 <TARGET>/.agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target claude_code --repair --skills-only --output-root <TARGET>
```

2. Report created and skipped projections in the final sync output.
3. If existing projections were skipped because their content differs, list them and ask for separate explicit approval before re-running the projection with `--force`. Never force-overwrite differing projections silently.
4. Do not record `.claude/**` outputs in `.gsd/blueprint.lock.json`; projections stay generated project-local outputs, not blueprint truth.
5. If the projection script is missing or fails, report the refresh as `blocked` with the reason; do not fail the whole sync because of a blocked projection refresh.

## Removed Blueprint File Handling

Removed-file detection is mandatory in `audit-only` and `update` mode. It is informational during first install.

Compare:

```text
target .gsd/blueprint.lock.json installed file list
vs
current source .gsd/blueprint-manifest.json file list
```

For every concrete file recorded in the target lock as previously installed from the Blueprint but absent from the current source manifest, report it under:

```text
Previously installed Blueprint files removed from current manifest
```

Classify each candidate as exactly one of:

- `delete candidate`
- `preserve because project-owned/runtime`
- `conflict because locally modified`
- `ignore because generated_project_local`
- `unknown ownership`

Delete only when all are true:

- the file was installed by previous Blueprint sync according to lock metadata;
- the file is not `project_preserve`, an existing `bootstrap_if_missing` runtime file, or `generated_project_local`;
- the file is not a generated runtime adapter output such as `.codex/**` or generated `.claude/**`;
- the file has no target-local modifications compared with the installed lock hash/content when hash evidence exists;
- local modification can be safely determined;
- the user explicitly approves deletion.

If local modification cannot be safely determined, preserve the file and report `conflict requiring manual review`.
Never delete generated runtime adapter files such as `.codex/**` or generated `.claude/**` during removed-from-manifest cleanup, even if they appear in old lock metadata, unless the user explicitly approves a separate runtime-output cleanup task.
Never delete project runtime/history artifacts, generated project-local files, managed-block host files, bootstrap/project surfaces, user documents, wildcard paths, or target files never recorded in the lock.
After approved safe deletes, remove empty parent directories only inside strict Blueprint-owned namespaces such as `.agents/skills/<removed-skill>/`, and never remove non-empty directories.

## Approval Gate

`install` and `update` must stop after the audit plan unless the user gives explicit approval.
The approval request must include a compact summary of exactly what will change.

Allowed approval phrases are exact, case-insensitive matches:

```text
approve sync
apply this sync plan
approve these changes
sync approved
```

Do not treat vague responses such as `yes`, `ok`, `approved`, `go ahead`, or similar as approval.
If approval is missing or ambiguous, stop after the audit plan.

Mutations requiring approval include:

- file creation
- file replacement
- managed-block update
- bootstrap guidance block update
- marker insertion
- legacy `AGENTS.md` migration
- delete candidate removal
- lock file update
- verification report creation or update

Do not apply blocked, conflicting, unsafe, ambiguous, or manual-review-required items even when approval is explicit.

## Apply Workflow

Only after explicit approval:

1. Re-read the manifest, lock, and every target file that will be changed.
2. Reconfirm each approved action still matches the audit classification.
3. Apply only approved actions:
   - create missing `blueprint_replace` files from the Blueprint;
   - replace changed `blueprint_replace` files from the Blueprint;
   - create missing `bootstrap_then_managed_block` starter files;
   - update only marked blocks for `managed_block` and existing `bootstrap_then_managed_block` files;
   - create missing `bootstrap_if_missing` files;
   - delete approved removed-from-manifest candidates.
4. Preserve every project-owned/runtime file and generated project-local output exactly during file sync.
   Generated runtime adapter outputs such as `.codex/**` and generated `.claude/**` must never be copied from the Blueprint source; `.claude/skills/**` may change only through the Claude Runtime Projection Refresh step.
5. Stop if a file changed since audit in a way that invalidates the plan.
6. Update or create `.gsd/blueprint.lock.json` only after approved writes and deletes succeed.
7. Run the Claude Runtime Projection Refresh step when planned.
8. Run lightweight verification.
9. Return the required final sync output.

## Lock File Requirements

The lock represents the current installed Blueprint inventory after a successful approved sync.
It must enable future sync to answer:

- Was this file installed by Blueprint sync?
- What was the installed content hash?
- Is the target file now locally modified?
- Was this file removed from the current Blueprint manifest?

When writing lock entries for concrete files, include at least:

- `path`
- `owner`
- `sync_strategy`
- `installed`: `true`
- `last_action`
- `source_hash` or `installed_hash` when available
- `installed_at` or `updated_at`
- `blueprint_version` or `blueprint_commit` when available

For managed-block and bootstrap guidance updates, record the host file path, block id when known, owner, sync strategy, last action, and installed block/content hash when practical.
Do not store project secrets, absolute Obsidian vault paths, or unrelated project runtime content in the lock.

## Conflict Rules

Stop or mark manual review required for:

- malformed, duplicated, missing, or mismatched markers;
- unknown ownership;
- old unmarked `AGENTS.md` operating content requiring migration;
- marker insertion that would alter existing project content;
- ambiguous ownership changes;
- target-local modifications that cannot be safely evaluated from lock metadata;
- missing required Blueprint source files;
- attempted writes to `project_preserve`, existing `bootstrap_if_missing`, or `generated_project_local` paths.

When unsure, preserve and report.

## Verification Checks

Run lightweight checks after approved sync:

- manifest parses as JSON;
- source manifest exists in the Blueprint source path;
- required Blueprint source files exist;
- full-content comparisons were performed for `blueprint_replace` entries;
- managed-block comparisons were performed for `managed_block` entries;
- bootstrap guidance block comparisons were performed for existing `bootstrap_then_managed_block` entries;
- removed-from-manifest files were checked against the target lock;
- explicit approval was obtained before every mutation;
- only approved deletions were applied;
- project-owned/runtime files were preserved;
- generated project-local files were untouched by blueprint file sync;
- generated `.codex/**` runtime adapter outputs were untouched, and `.claude/**` changed only through the approved Claude Runtime Projection Refresh step;
- `CLAUDE.md` project-owned content was preserved when its blueprint block was created or updated;
- managed block markers are balanced in changed mixed files;
- `.gsd/blueprint.lock.json` was updated only after successful approved sync.

## Required Final Sync Output

The final sync response must include:

- Files created
- Files replaced
- Files deleted
- Managed blocks updated
- Bootstrap guidance blocks updated
- Files preserved
- Files skipped
- Claude skill projection refresh results
- Conflicts
- Unsafe or ambiguous items
- Lock file status
- Verification checks run
- Final disposition: `pass` | `fail` | `partial`

Use final dispositions as follows:

- `pass`: all approved safe sync actions applied and verification passed.
- `partial`: approved safe actions applied, but conflicts or skipped review-required items remain.
- `fail`: a write or verification failed; report exactly what changed before failure and what remains unresolved.

## Completion Check

- Audit completed before any write.
- `audit-only` performed no writes.
- `install` and `update` required explicit approval before mutation.
- Content comparison was used for Blueprint-owned files.
- Managed-block comparison was used for mixed files.
- Removed-from-manifest detection used the target lock vs the current source manifest.
- Project-owned/runtime and generated project-local files were preserved.
- Lock metadata includes enough information for future changed-file and removed-file detection.
- No Obsidian vault memory was written.
