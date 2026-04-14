---
name: gsd-new-project
description: Bootstrap a greenfield repository into the Codex-native GSD workflow by turning a project idea or sparse brief into the core planning artifacts. Use when a repo is new, planning files are missing, or the project charter and requirements need to be created or refreshed before milestone work begins.
---

# GSD New Project

Initialize the repository planning layer before feature work starts.
Use this skill to interview for project intent, create the core planning docs, and set the repository state so milestone planning can begin cleanly.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), and [`.planning/STATE.md`](../../../.planning/STATE.md).
2. Determine whether the files are missing, placeholder-only, stale, or partially filled.
3. Gather the minimum missing bootstrap inputs from the user: objective, audience, goals, known stack or runtime context if already available, constraints, risks, non-goals, and whether the project-local vault scaffold needs to be created or verified. Do not require stack selection at bootstrap time.
4. Rewrite or refresh the core bootstrap artifacts using the templates under [`.planning/templates/`](../../../.planning/templates/), including the bootstrap and adoption model for the project-local vault.
5. If the project is adopting the vault layer, create or verify the project-local vault scaffold through `gsd-vault-bootstrap` before milestone planning begins.
6. Record the next non-trivial readiness path explicitly: Project Idea Document -> Technical Specification -> stack selection and configuration-package planning -> milestone planning. Use the current project's filled-in spec artifacts for that path; do not treat [PROJECT.md](../../../PROJECT.md) or [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md) as substitutes.
7. Set [`.planning/STATE.md`](../../../.planning/STATE.md) to indicate bootstrap is complete and the next action is spec-readiness preparation rather than milestone planning when those governing artifacts are still missing or stale.

## Required Outputs
- [PROJECT.md](../../../PROJECT.md): project charter with objective, audience, goals, known stack or runtime context if already available, constraints, and non-goals.
- [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md): functional and non-functional requirements, acceptance criteria, and exclusions.
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md): initialize milestone sequencing and the current pointer.
- Readiness handoff: explicit pointer to the current project's next required artifacts, using [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md), [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md), and [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md) before non-trivial milestone planning starts.
- Project-local vault bootstrap status: scaffold verified or the next explicit vault-bootstrap handoff.
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
- Treat stack selection as a later readiness artifact, not a bootstrap prerequisite.
- Keep written normalization lightweight by default. Write a fuller problem or scope summary only when ambiguity, risk, scope, or explicit user request justifies it.
- If the repository already contains meaningful code, stop and switch to `$gsd-map-codebase` unless the user explicitly wants a full rewrite of the planning docs.
- Do not write durable project memory during bootstrap. Creating or verifying the project-local vault scaffold is allowed; writing durable notes is not.
- Do not create milestone or phase files here. This skill ends at project bootstrap.

## Completion Check
- [PROJECT.md](../../../PROJECT.md) is usable and no longer placeholder-only.
- [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), and [`.planning/STATE.md`](../../../.planning/STATE.md) are consistent with one another.
- The outputs clearly route the current project toward Project Idea Document, Technical Specification, and stack-selection/configuration-package planning before non-trivial milestone planning begins.
- [`.planning/STATE.md`](../../../.planning/STATE.md) clearly says the next action is spec-readiness preparation or `$gsd-plan-milestone`, with milestone planning allowed only when the governing artifacts are already sufficiently current.
