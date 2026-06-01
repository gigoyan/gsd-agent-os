# Source Materials Contract

This contract defines how GSD projects register, classify, preserve, and consume repository-local source materials supplied by users or discovered in the repository.
Use it with document-first intake, mapping, specification, milestone planning, execution, verification, and project-context export.

## Ownership Boundary
- This file is blueprint-owned template guidance.
- `.planning/source-materials/SOURCE_MATERIALS.md` is the runtime project registry generated from `source-materials-registry-template.md`.
- Runtime project registries and copied source files are project-owned unless a blueprint sync explicitly owns a managed block.
- Do not treat `.planning/source-materials/SOURCE_MATERIALS.md` as a blueprint-owned file.

## Source-Material Model
A source material is any durable input that may govern, inform, or evidence project work.
Examples include repository-local briefs, transcripts, product notes, screenshots, PDFs, API docs, migration notes, decision records, issue exports, and repository files that are intentionally registered as planning inputs.
Direct user input to `$gsd-register-source-materials` must be repository-relative file or directory paths only. URLs, external references, absolute external file paths, and non-repository locations must not be registered directly; ask the user to place the material inside the repository and rerun registration with the repo-relative path.
External references may still be registered when they are discovered inside repository files, but the registered direct input remains the repository file or directory.

Every registered source material must have:
- `source_id`: stable ID unique within the registry.
- `title`: short human-readable label.
- `classification`: one allowed classification type.
- `scope`: the part of the project or workflow the material applies to.
- `governs`: explicit statement of what the material controls, if anything.
- `evidence_status`: `Confirmed`, `Suggested`, or `Unknown`.
- `location`: repository-relative path, or a source-local anchor/reference discovered inside a registered repository file.
- `custody`: `registered-in-place`, `copied`, `moved`, `external-reference`, or `missing`.
- `consumption_rule`: how downstream agents may use the material.

## Folder Conventions
- Runtime registry path: `.planning/source-materials/SOURCE_MATERIALS.md`.
- Project-owned copied materials should live under `.planning/source-materials/materials/` when they are small, text-friendly, and appropriate to keep in the repository.
- Project-owned indexes, extracts, or summaries should live under `.planning/source-materials/extracts/` when raw material should not be duplicated or is too large/noisy for repo storage.
- Do not write durable source materials directly under the shared vault root.
- `$gsd-register-source-materials` does not accept vault paths as direct input; if later workflows cite vault-backed context, it must stay within the owning namespace: `projects/<vault-project-id>/`.
- Do not copy or move generated runtime adapter outputs into source-material folders.

## Classification Types
- `product_brief`: user or stakeholder description of goals, audience, scope, constraints, or non-goals.
- `requirements_input`: material that states functional, non-functional, compliance, operational, or acceptance requirements.
- `technical_input`: material that describes architecture, APIs, data models, dependencies, runtime behavior, or implementation constraints.
- `design_input`: UX, UI, visual, content, information-architecture, or interaction guidance.
- `workflow_input`: process, planning, delivery, validation, deployment, handoff, or operating-procedure material.
- `repo_evidence`: repository file or observed repository behavior intentionally registered as planning evidence.
- `decision_record`: explicit decision, approval, rejection, or tradeoff record.
- `external_reference`: third-party documentation, standards, vendor pages, specs, or URLs discovered inside repository files.
- `research_note`: exploratory notes, comparisons, investigations, or unresolved findings.
- `unknown`: material whose classification is not yet clear.

## Scope And Governs Rules
- `scope` records where the material applies, such as `project`, `milestone:<id>`, `phase:<id>`, `feature:<name>`, `module:<path>`, `workflow:<name>`, or `export:<profile>`.
- `governs` must be explicit when the material is authoritative for any artifact or workstream.
- A material can inform work without governing it. In that case, set `governs: none` and explain the limited use in `consumption_rule`.
- When two materials conflict, do not silently choose one. Mark the affected claim `Unknown` unless a newer explicit user decision or stronger repo evidence resolves the conflict.
- More specific scope overrides broader scope only when its `evidence_status` is `Confirmed` and the registry records the relationship.
- Do not let source materials bypass the normal Spec-First gate. They feed the Project Idea Document, Technical Specification, stack-selection/configuration package, milestone, phase, or verification artifacts as appropriate.

## Evidence Statuses
Use the shared GSD evidence meanings from `intake-routing-and-evidence-contract.md`:
- `Confirmed`: backed by direct repo evidence, supplied materials, or an explicit user decision. Treat as factual input.
- `Suggested`: a recommendation, inference, or prefill derived from evidence. Keep it visible as a suggestion until the user confirms it or stronger evidence proves it.
- `Unknown`: still unresolved, missing, or conflicting. Keep it open, record the gap explicitly, and ask a focused follow-up only when it materially blocks progress.

Rules:
- Never silently promote `Suggested` values to `Confirmed`.
- Do not downgrade `Confirmed` material without recording the reason, replacement evidence, and affected downstream artifacts.
- If custody, provenance, date, author, or applicability is unclear, keep the affected field or claim `Unknown`.

## Register-In-Place, Copy, And Move Rules
- Prefer `registered-in-place` when the material already exists in a stable repo path.
- Use `copied` when the material is user-supplied, small enough for repo custody, useful for repeatable planning, and safe to store in the project repository.
- Use `moved` only when the user explicitly asks to move the file or when the file is already inside the repository and the move is part of an approved organization task.
- Use `external-reference` only for URLs, vendor docs, standards, or other external references discovered inside registered repository files.
- Use `missing` only for known referenced material that is not currently available.
- Before copying or moving, preserve provenance in the registry: original filename, original location or source note, received date when known, and transformation notes.
- Do not overwrite, delete, or relocate user materials unless the user explicitly requested that operation.
- Do not copy secrets, credentials, private personal data, licensed content, or large binaries into the repo. Register the repository path in place without copied custody, or summarize only the relevant non-sensitive claims when appropriate.

## Registry Schema
The runtime registry must include these sections:
- `Registry Metadata`: schema version, project, owner, generated-from template, and last updated.
- `Custody Rules`: project-specific storage and non-copy constraints.
- `Source Materials`: one row per material.
- `Claim Index`: compact claims extracted from materials and their evidence status.
- `Conflicts And Unknowns`: unresolved contradictions, missing inputs, and follow-up questions.
- `Downstream Consumption Log`: artifacts or workflow steps that consumed registered material.

Each `Source Materials` row must contain:
`source_id`, `title`, `classification`, `scope`, `governs`, `evidence_status`, `location`, `custody`, `date_or_version`, `owner_or_origin`, `notes`.

Each `Claim Index` row must contain:
`claim_id`, `claim`, `source_refs`, `evidence_status`, `applies_to`, `consumed_by`, `notes`.

The registration skill may create only lightweight, source-local claim index entries. It must not decide final project requirements, milestone scope, acceptance criteria, implementation behavior, or verification conclusions. Those decisions belong to document-first intake, milestone planning, phase planning, execution, and verification.

## Downstream Consumption Rules
- Downstream artifacts must cite source material by `source_id` and, when possible, a section, page, heading, timestamp, line, or stable anchor.
- Extract only the claims needed for the target artifact. Do not dump raw source bodies into planning artifacts.
- Keep `Confirmed`, `Suggested`, and `Unknown` visible when claims move into Project Idea Documents, Technical Specifications, stack-selection artifacts, milestones, phases, verification, exports, or codebase maps.
- A `Confirmed` source material can support a `Suggested` downstream recommendation, but the recommendation must remain `Suggested` until explicitly confirmed.
- A `Suggested` source material cannot be the only basis for a `Confirmed` downstream requirement.
- An `Unknown` source material or claim can identify a gap, risk, or follow-up question but must not be treated as implementation authority.
- When a downstream artifact changes or rejects a source-backed claim, update the registry consumption log or record a follow-up to refresh it.
- Project-context export may include compact source indexes and claims, but must avoid copying full sensitive or oversized materials into export packages.

## Runtime Consumption Contract
- Planning, execution, verification, orchestration, mapping, intake, and export workflows must consume registered source material through `.planning/source-materials/SOURCE_MATERIALS.md` first.
- Runtime artifacts should cite compact references: `source_id`, `claim_id`, `source_id#anchor`, `evidence_status`, and the downstream use or status.
- Raw source-material folders may be inspected only when the registry, milestone, phase, or verification artifact cites a narrow file and anchor needed to resolve ambiguity.
- Do not broad-scan `.planning/source-materials/materials/**`, `.planning/source-materials/extracts/**`, or other raw source-material folders to discover requirements during execution or verification.
- Preserve the registry evidence status when carrying a claim downstream. A `Suggested` claim remains non-authoritative until explicit confirmation or stronger evidence exists; an `Unknown` claim may record a gap or risk but must not authorize implementation.
- Runtime artifacts must not duplicate registry rows, paste full source bodies, or become secondary source-material registries.
- When source-backed claims are changed, rejected, consumed, or found stale, update the registry consumption log when in scope; otherwise record a source-registry follow-up.
