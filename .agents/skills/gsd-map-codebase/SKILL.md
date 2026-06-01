---
name: gsd-map-codebase
description: Unified self-orchestrating GSD mapping workflow for empty, new, existing, partial, stale, and large or transformation-oriented repositories.
---

# GSD Map Codebase

Map the current repository with one unified mapping workflow.
This skill replaces the user-facing responsibilities formerly split across default codebase mapping, serious codebase mapping, and context-index refresh. It is the root orchestrator for mapping work and must not create milestones for mapping or hand mapping execution to `$gsd-run-milestone`.

## Operating Model

- The root mapping orchestrator owns mapping strategy, mapping state classification, slice decomposition, child prompt quality, child result review, artifact updates, and final consistency review.
- Mapping sub-agents own only their assigned factual mapping slice.
- The root orchestrator spawns exactly one bounded mapping child at a time, waits for that child result, reviews it, updates or confirms artifacts, then decides the next slice.
- The root orchestrator does not continue other work while waiting for a mapping child.
- The loop stops only when mapping is complete enough for future coding agents, blocked, the repository has no meaningful structure to map, or no safe next slice exists.
- Mapping artifacts are written for future coding agents first: routing, canonical examples, symbols, conventions, validation paths, command evidence, and do-not-touch boundaries take priority over narrative explanation.

## Source Inputs

Read these before choosing the first slice:

- [PROJECT.md](../../../PROJECT.md)
- [`.planning/STATE.md`](../../../.planning/STATE.md)
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md)
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md)
- [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md)
- [`.planning/tool-capabilities.md`](../../../.planning/tool-capabilities.md) when present
- [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md)
- [`.planning/templates/delegated-agent-contract.md`](../../../.planning/templates/delegated-agent-contract.md)
- [`.planning/templates/codebase-map-template.md`](../../../.planning/templates/codebase-map-template.md)
- [`.planning/templates/context-index-template.md`](../../../.planning/templates/context-index-template.md)
- Relevant repository structure, manifests, commands, entry points, modules, tests, generated or vendor boundaries, and directly related docs.

Use [`.planning/templates/project-template.md`](../../../.planning/templates/project-template.md) only when `PROJECT.md` is missing or placeholder-only and a minimal backfill is needed.

## Mapping State Classification

Classify the current repository as exactly one of these states before the first child slice, then revise the classification only when new evidence justifies it:

- `no_meaningful_project_structure`
- `structure_exists_but_no_mapping`
- `partial_mapping_exists`
- `mature_mapping_may_be_stale`
- `serious_full_mapping_needed`
- `transformation_migration_refactor_mapping_requested`

Use `Confirmed`, `Suggested`, and `Unknown` with the shared meanings from the intake contract:

- `Confirmed`: direct repo evidence, supplied materials, command evidence, or explicit user decision.
- `Suggested`: evidence-backed inference or recommended route that still needs stronger proof or user confirmation.
- `Unknown`: missing, conflicting, inaccessible, or unverified.

## Bounded Mapping Slices

Choose one bounded slice at a time. Good slice shapes include:

- repository structure and entry points
- build, test, lint, run, and tool capability surfaces
- backend, API, service, package, or module boundaries
- frontend, client, UI, or route boundaries
- persistence, schema, migration, and data model surfaces
- auth, permission, privacy, or security surfaces
- integrations, webhooks, jobs, queues, cron, messaging, and provider boundaries
- test structure and validation strategy
- coding conventions and canonical examples
- symbol or API map for one module or task family
- fragile, generated, vendor, build-output, and do-not-scan boundaries
- context-index routing rows for one task family
- stale mapping correction for a specific contradicted route or module card

Keep slices factual and current-state only. Do not turn mapping into implementation planning, target architecture design, migration design, or milestone planning.

## Root Workflow

1. Read the source inputs and classify the mapping state.
2. Decide whether there is meaningful structure to map. If not, leave `CODEBASE_MAP.md` and `CONTEXT_INDEX.md` placeholder or minimal, update `STATE` only if needed, and route to `$gsd-new-project` when project bootstrap is the correct next step.
3. Select the next bounded mapping slice from repo evidence, stale artifact gaps, user intent, or the highest-value missing agent-routing need.
4. Spawn exactly one mapping child for that slice.
5. Use `model: "gpt-5.5"`, `reasoning_effort: "medium"`, and `fork_context: false` by default. Set `fork_context: true` only when the slice truly needs prior conversation context that cannot be passed as explicit file paths and instructions.
6. Pass only the necessary file paths, current mapping classification, relevant artifact excerpts, command capability notes, and slice instructions. Do not pass the entire conversation unless required.
7. Wait for the child result before doing anything else.
8. Review the child output. Apply only evidence-supported updates and preserve `Confirmed`, `Suggested`, and `Unknown`.
9. Update [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) when current architecture, runtime, data, integration, dependency, risk, or operational reality changed or was newly mapped.
10. Update [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md) when routing rows, module cards, symbols, conventions, canonical examples, validation guidance, command surfaces, search recipes, or do-not-scan boundaries changed.
11. Update [`.planning/STATE.md`](../../../.planning/STATE.md) only when needed to record mapping progress, partial/stale areas, blockers, or a precise next action. Do not create milestones, phases, verification files, or roadmap pointers for mapping work.
12. Decide the next slice. Repeat the one-child-at-a-time loop until mapping is complete, partial with explicit unknowns, blocked, or unsafe to continue automatically.
13. Run the completion review against both mapping artifacts so `CODEBASE_MAP.md` records current system reality and `CONTEXT_INDEX.md` tells future agents how to work safely and narrowly.

## Child Spawn Contract

Every mapping child prompt must include wording equivalent to all of the following:

- Follow [`.planning/templates/delegated-agent-contract.md`](../../../.planning/templates/delegated-agent-contract.md); you are a delegated mapping child agent, not the mapping orchestrator.
- Perform only the assigned mapping slice.
- Do not edit files unless the root prompt explicitly allows it.
- Do not design implementation, migration, target architecture, or future milestone work.
- Keep facts labeled as `Confirmed`, `Suggested`, or `Unknown`.
- Report exact file paths, symbols, commands, conventions, and evidence.
- Return proposed updates for `CODEBASE_MAP.md` and/or `CONTEXT_INDEX.md` as structured sections.
- Return whether another mapping slice is needed.
- Stop after the assigned slice.

## Child Output Contract

The child must return these sections:

- `Mapping Slice`
- `Files Inspected`
- `Confirmed Findings`
- `Suggested Interpretations`
- `Unknowns / Gaps`
- `Relevant Symbols / APIs`
- `Canonical Examples`
- `Validation / Command Evidence`
- `Recommended CODEBASE_MAP.md Updates`
- `Recommended CONTEXT_INDEX.md Updates`
- `Do-Not-Scan / Fragile Areas`
- `Next Mapping Slice Recommendation`
- `Slice Status: complete | partial | blocked`

## Artifact Rules

- `CODEBASE_MAP.md` records current system reality: architecture, runtime flows, data and integration surfaces, dependency direction, operational surfaces, risks, and transformation-sensitive constraints.
- `CONTEXT_INDEX.md` records how coding agents should work safely in the repo: task routes, start-here files, inspect-next files, likely edit files, symbols and APIs, canonical examples, conventions, validation paths, command notes, and avoid-unless-needed areas.
- Treat `.planning/templates/context-index-template.md` `Agent Context Routing Contract` as the canonical contract for how future agents consume and update context routing.
- Keep `CONTEXT_INDEX.md` compact and task-routing oriented. Do not duplicate the full `CODEBASE_MAP.md`.
- When `.planning/CODEBASE_MAP.md` has `GSD-BLUEPRINT: codebase-map-surface-contract` and `GSD-PROJECT: codebase-map-content` markers, update only the `GSD-PROJECT: codebase-map-content` block.
- When `PROJECT.md` has markers and needs minimal backfill, update only the `GSD-PROJECT: project-charter` block.
- If markers are missing but project content exists, preserve the file and report a marker migration need instead of overwriting it.
- Preserve repo-vault separation. Do not write durable vault memory from mapping.
- Do not store `CONTEXT_INDEX.md` in the vault and do not use vault memory as a replacement for repo-local task routing.
- Do not create milestones or phases for mapping, verification artifacts, or `$gsd-run-milestone` handoffs.

## Required Outputs

- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md): current repository reality with evidence status, agent working model, architecture/runtime/data/integration facts, risk and fragile areas, and unknowns.
- [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md): compact coding-agent navigation guide with task-routing rows, module cards, symbol/API map, convention cards, validation matrix, search recipes, change-impact routing, and do-not-scan boundaries.
- [PROJECT.md](../../../PROJECT.md): minimal project charter backfill only when missing or placeholder-only.
- [`.planning/STATE.md`](../../../.planning/STATE.md): updated only when mapping status, blockers, stale areas, or next action need to be recorded.
- Final response with mapping classification, slices completed, artifacts updated, remaining `Unknown` gaps, blockers if any, and the next recommended GSD action.

## Rules

- Prefer repo evidence over assumptions. If evidence is thin or contradictory, mark it `Unknown`.
- The same unified skill handles onboarding, partial refresh, stale context-index repair, and serious transformation-oriented mapping.
- For transformation, modernization, major refactor, version upgrade, platform migration, stack migration, or architecture restructuring requests, choose deeper and more numerous factual slices inside this skill instead of routing to a separate serious-mapping workflow.
- For context-index-only requests, choose targeted routing/convention/validation slices inside this skill.
- Do not classify blueprint-owned GSD skill or template files as application architecture unless the current repository is explicitly the reusable GSD blueprint. In normal project repositories, treat `.agents/skills/**`, `.planning/templates/**`, `.gsd/**`, and reusable GSD docs as workflow infrastructure.
- If the active repository is the reusable GSD blueprint, map GSD workflow assets as the product and use the blueprint manifest as the main ownership boundary.
- Cite real paths, commands, symbols, and evidence. Avoid hand-wavy summaries.
- Do not infer stack decisions beyond what the repository already proves.
- If mapping reaches stack-selection readiness, route to `$gsd-select-stack`. If readiness artifacts are current enough for implementation planning, route to `$gsd-plan-milestone`.
- Use UI options whenever remaining user input can reasonably be expressed as structured choices or confirmations.

## Completion Check

- Mapping state was classified and evidence status remained visible.
- Each mapping slice was delegated to exactly one bounded child at a time, with medium reasoning and default `fork_context: false`.
- The root orchestrator waited for every child result before continuing.
- Mapping children did not orchestrate, spawn agents, edit unrelated files, or design future implementation.
- `CODEBASE_MAP.md` captures current system reality at the selected depth.
- `CONTEXT_INDEX.md` gives future coding agents compact operational routes, symbols, conventions, canonical examples, validation paths, and do-not-scan boundaries.
- Remaining gaps are recorded as `Unknown` or blockers.
- No milestone or phase for mapping, verification artifact, or `$gsd-run-milestone` handoff was created.
