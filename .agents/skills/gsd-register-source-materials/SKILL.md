---
name: gsd-register-source-materials
description: Register repository-local files or directories as GSD source materials by initializing and maintaining the project-owned source-material registry without copying unsafe or inappropriate raw material into the repository.
---

# GSD Register Source Materials

Use this skill when the user supplies repository-relative source-material paths that should become durable planning inputs.
The workflow is registry-first: preserve provenance, classify material, record evidence status, and only copy or move files when the source-material contract allows it.

## Source Of Truth
- Use [`.planning/templates/source-materials-contract.md`](../../../.planning/templates/source-materials-contract.md) for exact custody, classification, evidence, and downstream consumption rules.
- Use [`.planning/templates/source-materials-registry-template.md`](../../../.planning/templates/source-materials-registry-template.md) to initialize the project-owned runtime registry at `.planning/source-materials/SOURCE_MATERIALS.md`.
- Treat `.planning/source-materials/SOURCE_MATERIALS.md`, `.planning/source-materials/materials/**`, and `.planning/source-materials/extracts/**` as project-owned runtime outputs, not blueprint-owned files.
- Do not edit generated runtime adapter outputs while registering source materials.

## Input Contract
The user may provide only:
- Repository-relative file paths.
- Repository-relative directory paths.
- An optional instruction: `organize` or `register only`.

Interpret missing instruction as `register only`.
Do not require the user to provide titles, classifications, statuses, or scopes before beginning; infer conservative defaults and keep uncertain fields `Unknown`.
If the user supplies a URL, external reference, absolute external file path, or non-repository location, do not register it directly. Ask the user to place the material inside the repository and rerun `$gsd-register-source-materials` with the repo-relative path.
The skill may register external references discovered inside repository files, but direct user input must be repository-relative paths only.

## Modes
- `register only`: Prefer `registered-in-place` for stable repository paths. Do not copy, move, delete, or reorganize files.
- `organize`: Register first, then copy small, text-friendly, safe user-supplied materials into `.planning/source-materials/materials/` when repo custody is appropriate. Move files only when the user explicitly asked to move them, or when the file is already inside the repository and the move is clearly part of the approved organization task.

## Workflow
1. Read `.planning/tool-capabilities.md` when present and obey recorded command fallbacks before running repository commands.
2. Read the source-material contract and registry template listed in `Source Of Truth`.
3. Ensure `.planning/source-materials/` exists. If `.planning/source-materials/SOURCE_MATERIALS.md` is missing, initialize it by copying the template content exactly, then update only runtime metadata fields such as project, created, last updated, and registry owner when those values are known from repo context or the current task.
4. Resolve every user-supplied path:
   - Repository-relative paths resolve from the repository root.
   - Reject URLs, external references, absolute external file paths, and non-repository locations as direct input.
   - If a repository file contains external references, register only the repository file as the direct input and record discovered references as claims, notes, or separate source rows when useful.
   - Missing paths are registered only when the user clearly referenced them as expected material; set custody to `missing`.
5. For each accepted path or source-local reference discovered inside a registered repository file, create or update one `Source Materials` row with:
   - a stable `source_id` unique in the registry; prefer descriptive IDs derived from the material or purpose over opaque imported sequence IDs;
   - a short title derived from filename, document heading, or user label when available;
   - one allowed `classification`;
   - `scope`, defaulting to `project` unless the path, registry context, or user instruction narrows it;
   - explicit `governs`, defaulting to `none` when authority is unclear;
   - `evidence_status` of `Confirmed`, `Suggested`, or `Unknown`;
   - `location`, `custody`, `date_or_version`, `owner_or_origin`, and provenance notes.
6. Classify conservatively:
   - briefs, goals, audiences, constraints, and non-goals -> `product_brief`;
   - functional, non-functional, compliance, operational, or acceptance statements -> `requirements_input`;
   - architecture, APIs, data models, dependencies, runtime, or implementation constraints -> `technical_input`;
   - UX, UI, visual, content, IA, or interaction guidance -> `design_input`;
   - process, planning, validation, deployment, handoff, or operating procedure -> `workflow_input`;
   - existing repo files or observed repo behavior intentionally used as evidence -> `repo_evidence`;
   - explicit decisions, approvals, rejections, or tradeoffs -> `decision_record`;
   - third-party docs, standards, vendor pages, specs, or URLs discovered inside repository files -> `external_reference`;
   - exploratory notes, comparisons, investigations, or unresolved findings -> `research_note`;
   - unclear material -> `unknown`.
7. Preserve evidence semantics:
   - Use exact `Confirmed`, `Suggested`, and `Unknown` meanings from [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md).
   - Registration-specific examples: direct supplied repository material, direct repo evidence, external references discovered inside registered repository files, or explicit user decisions can be `Confirmed`; inferred titles, classifications, scopes, recommendations, or applicability stay `Suggested`; missing, conflicting, private, inaccessible, ambiguous, or stale inputs stay `Unknown`.
   - Never silently promote `Suggested` to `Confirmed`, and never downgrade `Confirmed` without recording the reason and affected downstream artifacts.
8. Choose custody:
   - `registered-in-place` for stable repo paths the project should reference without copying.
   - `copied` for safe, small, text-friendly user-supplied files that are useful for repeatable planning and appropriate to store under `.planning/source-materials/materials/`.
   - `moved` only under the `organize` mode when explicitly authorized by the user or clearly approved for an existing in-repo organization task.
   - `external-reference` only for URLs, vendor docs, standards, or other external references discovered inside registered repository files.
   - `missing` for known referenced material that is not currently available.
9. Before any copy or move, screen the candidate by filename, type, size, and visible metadata or brief content sample when safe:
   - Do not copy secrets, credentials, key files, tokens, private personal data, licensed content, large binaries, generated runtime adapter outputs, dependency folders, build outputs, or noisy archives.
   - When raw custody is unsafe or inappropriate, register the source in place and optionally create a compact extract or claim index entry only for relevant non-sensitive claims.
   - Preserve original filename, original location, received date when known, owner/origin when known, checksum only when already available or cheap to compute safely, and any transformation notes.
10. Handle directories as bounded collections:
    - Expand only immediate useful children unless the user explicitly asks for recursive handling.
    - Skip dependency folders, build outputs, generated runtime adapter outputs, VCS folders, caches, and obvious large/noisy binary sets.
    - Register the directory itself as one material when its organization is the evidence.
    - Register individual files when each file has distinct provenance, classification, scope, or downstream use.
    - For mixed directories, add a conflict or unknown item that records skipped categories and the reason.
11. Update the `Claim Index` only with lightweight, source-local claims that may be useful to later planning, mapping, specification, milestones, phases, verification, or export. Cite `source_id` plus a stable anchor such as heading, page, timestamp, line, or section when possible. Do not decide final requirements, milestone scope, acceptance criteria, implementation behavior, or verification conclusions.
12. Update `Conflicts And Unknowns` for missing files, inaccessible paths, ambiguous custody, classification uncertainty, conflicting claims, skipped sensitive material, or follow-up questions.
13. Update `Downstream Consumption Log` when this registration directly feeds a GSD artifact or workflow step. Record the consumer, source refs, compact claims used, consumption rule, result, and follow-up. Do not paste full source bodies into the log.
14. Update registry metadata `Last updated` after registry changes.
15. Validate the registry shape after edits:
    - required sections are present;
    - all source rows have allowed `classification`, `evidence_status`, and `custody` values;
    - source IDs and claim IDs are unique;
    - copied files, if any, exist under `.planning/source-materials/materials/`;
    - no full sensitive, oversized, licensed, or binary source body was copied into planning artifacts.

## Registry Editing Rules
- Preserve existing registry entries and IDs.
- Do not replace the registry wholesale unless it was just initialized from the template.
- Prefer appending rows and maintenance notes over rewriting unrelated history.
- Keep source rows compact. Put provenance and transformation details in `notes`, not in copied source bodies.
- Use exact allowed vocabulary from the contract for `classification`, `evidence_status`, and `custody`.
- Keep `Confirmed`, `Suggested`, and `Unknown` visible in claims and downstream consumption; do not flatten them into a single status.

## Output Contract
Return a compact summary with:
- Registered repository paths and their `source_id` values.
- Whether the registry was initialized.
- Whether mode was `register only` or `organize`.
- Files copied or moved, if any.
- Materials skipped from repo custody and why.
- Validation performed.
- Skipped validation, if any.
- Unresolved issues or follow-up questions.

## Completion Check
- `.planning/source-materials/SOURCE_MATERIALS.md` exists when registration succeeds.
- Every accepted input has a registry entry or an explicit skipped/unknown record.
- Provenance is preserved before any copy or move.
- Unsafe or inappropriate materials were not copied into the repository.
- Registry consumption/log sections were updated as needed without extracting full source bodies.
