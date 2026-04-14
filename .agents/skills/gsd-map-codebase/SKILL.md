---
name: gsd-map-codebase
description: Onboard an existing repository into the Codex-native GSD workflow by inspecting the actual codebase and producing a grounded architecture map and initial planning state. Use when a repo already contains code but lacks a trustworthy CODEBASE_MAP.md or workflow artifacts.
---

# GSD Map Codebase

Create a factual repository map before milestone planning starts.
Use this skill to inspect structure, commands, dependencies, conventions, and hotspots without inventing unsupported architecture claims.

## Workflow
1. Inspect the repository layout, entrypoints, manifests, scripts, major modules, and test setup.
2. Identify build, test, lint, and run commands from repo evidence.
3. Summarize the actual architecture, conventions, and risk areas in [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md).
4. Backfill [PROJECT.md](../../../PROJECT.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) minimally if they are missing or placeholder-only, including whether the repo expects a project-local vault arrangement.
5. Assess whether the current project already has a sufficiently current Project Idea Document and Technical Specification grounded in repo evidence and explicit user input. If either artifact is missing, stale, or materially underspecified, stop short of milestone planning and route explicitly to the prerequisite artifact work first.
6. Treat stack selection and configuration-package planning as a post-spec-readiness step. Do not infer stack decisions beyond what the repository already proves.
7. Record whether a project-local vault scaffold already exists, should be verified, or should be created through `gsd-vault-bootstrap`.
8. Recommend likely first milestone candidates only when the governing Project Idea Document and Technical Specification are sufficiently current; otherwise recommend the missing readiness work instead. Do not create milestone files unless explicitly asked to switch into milestone planning.

## Source Templates
- [`.planning/templates/codebase-map-template.md`](../../../.planning/templates/codebase-map-template.md)
- [`.planning/templates/project-template.md`](../../../.planning/templates/project-template.md)
- [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md)
- [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md)
- [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md)

## Required Outputs
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md): architecture summary, key paths, commands, conventions, and risks.
- [PROJECT.md](../../../PROJECT.md): minimal project charter if still missing or placeholder-only.
- Readiness assessment: whether the current project's Project Idea Document, Technical Specification, and stack-selection/configuration-package planning artifacts are sufficiently current for milestone planning, or which prerequisite artifact work must happen next.
- Vault bootstrap note: whether a project-local vault scaffold exists or the next explicit `gsd-vault-bootstrap` handoff is needed.
- [`.planning/STATE.md`](../../../.planning/STATE.md): status updated to reflect mapping completion, milestone and phase status as `none` unless active work already exists, durable-memory follow-up as `none`, and the next recommended action as either prerequisite spec-readiness work or `$gsd-plan-milestone` only when the governing artifacts are sufficiently current.

## Rules
- Prefer repo evidence over assumptions. If something is unclear, mark it as unknown rather than guessing.
- Cite real paths and commands. Avoid hand-wavy summaries.
- If the repository is effectively empty, stop and switch to `$gsd-new-project`.
- Map repo reality first, then route the current project through Project Idea Document and Technical Specification backfill if needed. Do not pretend milestone planning is valid without those artifacts.
- Keep written normalization lightweight by default. Only require a fuller written normalization pass when ambiguity, risk, scope, or explicit user request justifies it.
- Do not write durable project memory from mapping. The only vault action allowed here is identifying or handing off project-local scaffold verification.
- Do not create milestone or phase files here. Mapping is preparation for planning, not planning itself.

## Completion Check
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) is grounded in observable repository facts.
- [`.planning/STATE.md`](../../../.planning/STATE.md) names the next recommended action.
- The output identifies at least one plausible first milestone candidate only when the governing Project Idea Document and Technical Specification are sufficiently current; otherwise it explicitly routes to the missing readiness work without pretending planning is already done.
