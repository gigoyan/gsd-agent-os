---
name: gsd-new-project
description: Bootstrap a greenfield repository into the Codex-native GSD workflow by turning a project idea or sparse brief into the core planning artifacts. Use when a repo is new, planning files are missing, or the project charter and requirements need to be created or refreshed before milestone work begins.
---

# GSD New Project

Initialize the repository planning layer before feature work starts.
Use this skill to interview for project intent, create the core planning docs, and set the repository state so milestone planning can begin cleanly.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), and [`.planning/STATE.md`](../../../.planning/STATE.md).
2. Classify the intake using [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md). Use this skill for `placeholder_bootstrap`, `document_first_intake`, or `partial_maturity_continuation` cases that still belong to bootstrap rather than existing-project mapping.
3. Use [`.planning/templates/document-first-intake-reference.md`](../../../.planning/templates/document-first-intake-reference.md) to decide which artifact surfaces should be populated first. Start from placeholders only when the repo is still placeholder-level; otherwise continue from the highest valid readiness artifact already supported by repo evidence or supplied materials.
4. Determine whether the files are missing, placeholder-only, stale, or partially filled, then extract already-available facts from repo evidence or supplied materials before re-asking the user. For `document_first_intake`, extract into the Project Idea Document or Technical Specification templates too when the supplied material is already specific enough to support those artifacts.
5. Gather only the minimum missing inputs for the next required surfaces: objective, audience, goals, known stack or runtime context if already available, constraints, risks, non-goals, readiness gaps, and whether the project should adopt the shared Obsidian MCP vault, and if so resolve the `GSD Vault Project ID` from the repository root folder name unless `PROJECT.md` already contains a confirmed value. Do not require stack selection at bootstrap time.
6. Track extracted and requested inputs as `Confirmed`, `Suggested`, or `Unknown`. Treat repo-proven facts, direct supplied-material facts, and explicit user decisions as `Confirmed`; keep derived recommendations or prefills as `Suggested`; keep unresolved or conflicting fields as `Unknown`.
7. When remaining user input is choice-shaped, use UI options rather than free-text whenever practical.
8. Rewrite or refresh the core bootstrap artifacts using the templates under [`.planning/templates/`](../../../.planning/templates/), including the bootstrap and adoption model for the project namespace under the shared Obsidian MCP vault root. When `PROJECT.md` contains `GSD-BLUEPRINT: project-surface-contract` and `GSD-PROJECT: project-charter` markers, update only the `GSD-PROJECT: project-charter` block and preserve the blueprint guidance block exactly. When the current project is already beyond placeholder bootstrap, update only the artifact surfaces that still need to be created or refreshed.
9. If the project is adopting the vault layer, record `GSD Vault Project ID`, `GSD Vault Namespace`, and `Vault scaffold status` in `PROJECT.md`, then create or verify `projects/<vault-project-id>/` through `gsd-vault-bootstrap` before milestone planning begins.
10. Record the next non-trivial readiness path explicitly: Project Idea Document -> preliminary technical direction -> `$gsd-select-stack` -> stack-aware Technical Specification completion -> milestone planning. Use the current project's filled-in spec artifacts for that path; do not treat [PROJECT.md](../../../PROJECT.md) or [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md) as substitutes.
11. Set [`.planning/STATE.md`](../../../.planning/STATE.md) to indicate bootstrap is complete and the next action is spec-readiness preparation rather than milestone planning when those governing artifacts are still missing or stale.

## Required Outputs
- [PROJECT.md](../../../PROJECT.md): project charter with objective, audience, goals, known stack or runtime context if already available, constraints, and non-goals, while keeping populated fields visibly `Confirmed`, `Suggested`, or `Unknown` when the template supports it. If managed markers exist, only the `GSD-PROJECT: project-charter` block is updated.
- [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md): functional and non-functional requirements, acceptance criteria, and exclusions, with extracted defaults still shown as `Suggested` until confirmed.
- When `document_first_intake` or `partial_maturity_continuation` reaches beyond bootstrap, refresh or create the current project's Project Idea Document and Technical Specification from extracted material instead of re-asking already answered questions.
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md): initialize milestone sequencing and the current pointer.
- Readiness handoff: explicit pointer to the current project's next required artifacts, using [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md), [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md), and `$gsd-select-stack` with [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md) before non-trivial milestone planning starts.
- Project namespace bootstrap status: `PROJECT.md` records the resolved `GSD Vault Project ID`, `GSD Vault Namespace`, and whether `projects/<vault-project-id>/` was verified or needs the next explicit `gsd-vault-bootstrap` handoff.
- Context index status: record `not applicable until structure exists`, `placeholder`, or the next `$gsd-refresh-context-index` handoff when relevant.
- [`.planning/STATE.md`](../../../.planning/STATE.md): record status as bootstrap complete, milestone and phase as `none`, milestone status and phase status as `none`, the durable-memory follow-up as `none`, and the next action as either the spec-readiness artifact work or `$gsd-plan-milestone` only when those governing artifacts are already sufficiently current.

## Source Templates
- [`.planning/templates/project-template.md`](../../../.planning/templates/project-template.md)
- [`.planning/templates/requirements-template.md`](../../../.planning/templates/requirements-template.md)
- [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md)
- [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md)
- [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md)
- [`.planning/templates/roadmap-template.md`](../../../.planning/templates/roadmap-template.md)
- [`.planning/templates/state-template.md`](../../../.planning/templates/state-template.md)
- [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md)

## Rules
- Keep the outputs concise and operational. This is scaffolding, not polished product documentation.
- Do not invent stack details, requirements, or constraints. Ask for missing intent when it matters.
- If the repository already has `.gsd/blueprint.lock.json`, preserve it and do not overwrite blueprint sync metadata during bootstrap.
- If GSD starter files are missing, treat them as `bootstrap_if_missing`; do not overwrite existing project runtime artifacts.
- If `PROJECT.md` has the blueprint/project marker structure, never rewrite the whole file during bootstrap. Replace only the project-owned `GSD-PROJECT: project-charter` block.
- If `PROJECT.md` is missing markers but contains project content, preserve it and surface a marker insertion or migration plan instead of overwriting it.
- Extract from supplied materials before re-asking the user when the intake route is `document_first_intake`.
- Continue from the highest valid readiness point when the intake route is `partial_maturity_continuation`; do not restart bootstrap artifacts that are already usable.
- Use the shared `Confirmed` / `Suggested` / `Unknown` evidence meanings; do not invent alternate evidence labels here.
- Carry evidence status forward into refreshed artifact fields instead of restating the value as if it were fully certain.
- Do not silently promote a `Suggested` stack, scope, or requirement prefill to `Confirmed` just because it fits the surrounding material.
- Keep `Unknown` gaps explicit and ask a focused follow-up only when the gap materially blocks the next readiness artifact.
- Prefer UI options for remaining choice-shaped questions whenever practical.
- Treat stack selection as a later readiness artifact handled through `$gsd-select-stack`, not a bootstrap prerequisite.
- If the user explicitly asks to select the stack before bootstrap is complete, allow `$gsd-select-stack` to run first and then route back to finish bootstrap and the stack-aware spec artifacts afterward.
- Do not require `.planning/CONTEXT_INDEX.md` for a project that has not started and has no meaningful structure. Once real structure exists, route to `$gsd-refresh-context-index` so later agents can navigate efficiently.
- Keep written normalization lightweight by default. Write a fuller problem or scope summary only when ambiguity, risk, scope, or explicit user request justifies it.
- If the repository already contains meaningful code, stop and switch to `$gsd-map-codebase` unless the user explicitly wants a full rewrite of the planning docs.
- Do not write durable project memory during bootstrap. Creating or verifying the project namespace scaffold under the shared Obsidian MCP vault root is allowed; writing durable notes is not.
- Do not create milestone or phase files here. This skill ends at project bootstrap.

## Completion Check
- [PROJECT.md](../../../PROJECT.md) is usable and no longer placeholder-only.
- [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), and [`.planning/STATE.md`](../../../.planning/STATE.md) are consistent with one another.
- Document-first intake and partial-maturity continuation behavior are explicit enough that the agent can populate the highest valid artifact surfaces before asking residual questions.
- The outputs clearly route the current project toward Project Idea Document, preliminary technical direction, `$gsd-select-stack`, and stack-aware Technical Specification completion before non-trivial milestone planning begins.
- [`.planning/STATE.md`](../../../.planning/STATE.md) clearly says the next action is spec-readiness preparation or `$gsd-plan-milestone`, with milestone planning allowed only when the governing artifacts are already sufficiently current.
