---
name: gsd-plan-milestone
description: Turn the next meaningful goal into one milestone file and one bounded execution phase inside the Codex-native GSD workflow. Use when work is too large for a quick task, spans multiple files, changes behavior, or needs explicit acceptance criteria and verification planning.
---

# GSD Plan Milestone

Plan the next unit of non-trivial work without starting implementation.
Use this skill to translate a goal into one milestone file and one executable phase, with synchronized roadmap and state updates. When an active milestone is already in progress, this skill plans the next bounded phase inside that milestone instead of creating a replacement milestone.
Standalone planning and normal delegated planning remain planning-only.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md), [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md), and [`.planning/STATE.md`](../../../.planning/STATE.md).
2. Determine whether the work is non-trivial. If it is tiny and bounded, stop and switch to `$gsd-quick-task`.
3. For non-trivial work, confirm the governing readiness artifacts are sufficiently current before planning: the current project's Project Idea Document, Technical Specification, and stack-selection/configuration-package planning artifact. Treat [PROJECT.md](../../../PROJECT.md) and [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md) as the current project's bootstrap charter and requirements surfaces, not as substitutes for those later readiness artifacts.
4. Exception: if the active repository is the reusable GSD blueprint and the requested work is blueprint-self-improvement, use the active milestone, completed phase verifications, and current repo-local planning artifacts as the governing readiness context instead of requiring a project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact.
5. If any governing artifact is missing, stale, or materially underspecified for the requested scope, stop planning and return an explicit prerequisite route naming the missing artifact work. When the missing step is stack selection or configuration-package planning, route explicitly to `$gsd-select-stack`. Do not create or update milestone or phase files for implementation planning until the readiness gate is satisfied.
6. Classify the planning entry using [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md), then determine whether the work needs a brand-new milestone or the next phase for the current active milestone. Reuse the active milestone when it is still in progress and the next work item belongs to its acceptance criteria.
7. Use `.planning/CODEBASE_MAP.md` and especially `.planning/CONTEXT_INDEX.md` to identify the narrowest relevant routing rows, module cards, symbol/API rows, convention cards, start-here paths, canonical examples, validation path, and avoid-unless-needed areas before creating or updating milestone and phase files. If the context index is missing, stale, or insufficient for the requested work, record a precise `$gsd-map-codebase` unified mapping refresh candidate or route to that skill when missing routing would materially affect planning quality.
8. Clarify the requested outcome, intended scope, exclusions, dependencies, success criteria, and the smallest meaningful behavior slices that need validation. If the work depends on prior durable context, request a narrow `gsd-memory-lookup` context pack first; otherwise stay repo-local and use the active planning artifacts as the source of truth.
9. Track planning claims and recommendations as `Confirmed`, `Suggested`, or `Unknown`, especially when the plan depends on repo evidence, extracted materials, or user confirmation. Keep milestone shape, phase sequencing, recommended slices, and inferred constraints visibly `Suggested` until repo evidence or the user confirms them.
10. Use UI options as the default for remaining choice-shaped user interactions whenever practical.
11. If the requested work is repository mapping, context-index refresh, stale mapping repair, serious full mapping, or transformation/migration/refactor mapping, stop milestone planning and route to `$gsd-map-codebase`. Mapping is self-orchestrating and must not be converted into a milestone for later execution.
12. Create or update one milestone file under [`.planning/milestones/`](../../../.planning/milestones/) with enough detail that a later execution or verification agent does not need to guess the milestone intent. The milestone must capture the concrete outcome, scope, explicit exclusions, assumptions, dependencies, risks, acceptance criteria, validation strategy, and a phase list that reflects both completed and pending phases. Include a `Context Routing` section that captures the exact context-index routing row or module card used, canonical example files to copy, first files to inspect, likely files to edit, validation command or check, avoided areas, and conditions that require updating `CONTEXT_INDEX.md` or `CODEBASE_MAP.md`. Preserve which inputs are `Confirmed`, which planning directions remain `Suggested`, and which blocking gaps remain `Unknown` when that distinction matters to scope or sequencing. Include concrete instructions or examples when the user, repo evidence, or prior analysis already supplies them. Keep the milestone itself repo-local and do not write durable memory from planning.
13. Create exactly one active phase file under [`.planning/phases/`](../../../.planning/phases/) for the first or next bounded implementation pass. The phase must be execution-ready: identify the exact behavior slice, touched areas, first tests or checks to create or update before implementation when practical, key constraints, concrete implementation notes, and explicit done criteria. Include a `Context Routing` section in the phase with the exact context-index routing row or module card used, canonical example files to copy, first files to inspect, likely files to edit, validation command or check, avoided areas, and mapping-artifact update triggers. When the phase depends on an inferred direction or unresolved prerequisite, keep that dependency labeled as `Suggested` or `Unknown` instead of flattening it into certainty. If the planning stop point is likely to matter later, note the later `gsd-session-save` follow-up as `candidate` or `none` without writing durable memory here.
14. Update [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) so the active milestone, milestone status, active phase, phase status, context-index use or refresh candidate, and durable-memory follow-up are explicit and still point to repo-local workflow control.

## Source Templates
- [`.planning/templates/milestone-template.md`](../../../.planning/templates/milestone-template.md)
- [`.planning/templates/phase-template.md`](../../../.planning/templates/phase-template.md)
- [`.planning/templates/roadmap-template.md`](../../../.planning/templates/roadmap-template.md)
- [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md)
- [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md)
- [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md)

## Naming Rules
- Milestone file: `M001-<slug>.md`
- Phase file: `M001-P01-<slug>.md`
- Use zero-padded numeric identifiers.

## Rules
- Keep the milestone meaningful but not broad enough to hide multiple unrelated efforts.
- If the requested work is to audit, install, or update installed GSD blueprint files across repositories, route to `$gsd-sync-blueprint audit-only|install|update <TARGET_REPOSITORY_PATH>` instead of creating a normal application implementation milestone.
- Enforce the Spec-First gate for non-trivial work. Do not plan implementation when the current project's Project Idea Document, Technical Specification, or stack-selection/configuration-package planning artifact is missing, stale, or materially underspecified.
- Exception: if the active repository is the reusable GSD blueprint and the requested work is blueprint-self-improvement, use the active milestone, completed phase verifications, and current repo-local planning artifacts as the governing readiness context instead of requiring a project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact.
- Do not block blueprint-self-improvement phases on missing project-specific readiness artifacts when the active milestone already defines the blueprint-improvement scope and acceptance criteria.
- Milestones must be detailed enough to act as durable repo-local planning artifacts, not thin reminders. Prefer concrete instructions over terse placeholders whenever the needed detail is already known.
- Use the shared `Confirmed` / `Suggested` / `Unknown` evidence meanings and preserve their distinction in planning outputs.
- Do not silently promote a recommended milestone boundary, sequencing choice, or scope interpretation from `Suggested` to `Confirmed`.
- Keep blocking readiness or dependency gaps as `Unknown` and route them through focused UI-option confirmation when the answer space can be structured.
- Include explicit assumptions, constraints, dependencies, verification expectations, and phase intent so later agents can execute without reconstructing the plan from chat history.
- Use `.planning/CODEBASE_MAP.md` and `.planning/CONTEXT_INDEX.md` to narrow milestone and phase scope before scanning source files.
- Do not create a phase that says only "inspect the repo"; name the start-here paths and validation route from the context index when available.
- If the context index is stale or missing for the requested area, either route to `$gsd-map-codebase` first or record a clear unified mapping refresh candidate in state.
- Keep context routing repo-local. Do not use Obsidian vault memory as a replacement for `CONTEXT_INDEX.md`.
- Include concrete examples only when they materially reduce ambiguity. Do not pad the milestone with generic filler or speculative implementation detail.
- Keep the first phase narrow enough for one focused execution pass and organized around a meaningful behavior slice rather than microscopic fragments.
- If the active milestone is incomplete, do not create a new milestone just to continue it. Update the existing milestone and add only the next bounded phase needed.
- Use UI options whenever remaining user collaboration can reasonably be expressed as structured choices, recommendations, or confirmations.
- Preserve serious mapping or transformation-oriented mapping intent explicitly by routing to `$gsd-map-codebase`; do not create milestones or phases for mapping.
- Standalone planning remains planning-only. Normal delegated planning remains planning-only.
- Narrow exception: when used inside the explicit `$gsd-run-milestone` verification-and-next-phase-planning composite step, planning may run after successful verification in the same child response only to create the next bounded phase in the same active milestone.
- In the composite step, do not create a replacement milestone unless the existing planning rules already require that outcome.
- In the composite step, do not execute or verify anything after creating the next phase.
- When invoked as a delegated child under `$gsd-run-milestone` without the explicit composite assignment, perform planning only. Do not orchestrate, do not delegate, and do not continue into execution or verification.
- As a delegated child, do not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- Define validation before implementation. Prefer the most relevant available test level: unit, integration, API or contract, regression, characterization, or smoke or manual fallback when automation is impractical.
- Specify which tests or checks should be created or updated first, or record the closest realistic safeguard when test-first is impractical.
- Tie milestone acceptance criteria and phase done criteria to validated behavior so `$gsd-verify-phase` can verify the slice from explicit evidence.
- For each non-trivial implementation phase, include the exact context-index route or module card used, canonical examples to copy, first files to inspect, likely files to edit, validation command or check, and conditions that require updating `CONTEXT_INDEX.md` or `CODEBASE_MAP.md`.
- When the work is architectural, multi-step, policy-heavy, or integration-heavy, include enough file, workflow, and decision detail in the milestone to make sequencing and expected outputs unambiguous.
- Keep written normalization lightweight by default. Require a fuller written normalization pass only when ambiguity, risk, scope, or explicit user request justifies it.
- Use memory lookup only to recover missing durable context, not to replace planning state or broaden the milestone.
- Do not write durable memory from this skill; durable outcomes belong to `gsd-session-save` after later execution or verification proves they matter.
- When planning reaches a meaningful stop point, record an explicit durable-memory follow-up decision in repo-local state as `candidate` or `none`; do not leave the save decision implicit.
- End the response with explicit `Phase Status: planned` and `Milestone Status: in_progress` lines, then a compact `Next-Step Prompt` for `$gsd-execute-phase` that tells the next agent to execute the active phase defined in the current planning artifacts.
- After returning the required outputs, stop immediately. Do not begin execution, verification, or any additional routing work yourself.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into milestone, phase, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- If the request is actually tiny and bounded, stop and switch to `$gsd-quick-task`.
- If milestone planning depends on durable memory, request `gsd-memory-lookup` scoped to `projects/<vault-project-id>/`; do not search the shared vault root or sibling project namespaces.
- Do not write or update vault notes during planning. If the planning result may deserve durable memory later, record only a `gsd-session-save` follow-up candidate in repo-local state.

## Completion Check
- For non-trivial work, the readiness gate was checked first and either passed explicitly or caused planning to stop and route to prerequisite artifact work.
- One milestone file exists and captures goal, scope, exclusions, assumptions, dependencies, risks, acceptance criteria, validation strategy, and current phase sequencing.
- One active phase file exists, is small enough to execute without further decomposition, and names the first validation step, touched areas, key constraints, and done criteria.
- The milestone and active phase contain exact context-routing guidance, canonical examples, first-inspection files, likely edit files, validation commands, and mapping-artifact update triggers, or explicitly justify why the context index was missing, stale, or not applicable.
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) both point to the same active milestone and phase, with milestone status shown as in progress.
