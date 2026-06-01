---
name: gsd-execute-phase
description: Implement the currently active phase from the GSD coding-agent workflow while staying strictly inside its defined scope. Use when an active phase already exists and the next step is to change code, configuration, or docs according to the phase file rather than create a new plan.
---

# GSD Execute Phase

Execute the active phase and nothing larger.
Use this skill after milestone planning is complete and before verification has been run.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), and resolve the active phase path.
2. Read the active phase file, the parent milestone file, and the governing spec or planning artifacts already named by those active artifacts so implementation stays anchored to the Project Idea Document, Technical Specification, and stack-selection/configuration-package context rather than treating the phase as detached.
3. Read the milestone and phase `Source Traceability` sections. If they cite `.planning/source-materials/SOURCE_MATERIALS.md`, follow the runtime consumption contract in [`.planning/templates/source-materials-contract.md`](../../../.planning/templates/source-materials-contract.md) and the evidence meanings in [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md). Execute from compact prepared traceability only: needed registry rows, claim IDs, `source_id#anchor` references, and evidence statuses.
4. Read `.planning/CODEBASE_MAP.md`, `.planning/CONTEXT_INDEX.md`, and the phase `Context Routing` section before scanning source files. Follow the `Agent Context Routing Contract` in `.planning/CONTEXT_INDEX.md`: start from the routed task row or module card, inspect `Start here` first, copy canonical examples, prefer targeted validation, avoid routed do-not-scan areas, and update the index or record a `$gsd-map-codebase` refresh candidate when execution proves routing wrong or incomplete.
5. Apply [`.planning/templates/performance-first-reuse-contract.md`](../../../.planning/templates/performance-first-reuse-contract.md): inspect phase-listed reusable surfaces, canonical examples, and extension points before new code; identify performance-sensitive paths and hot-path, request-path, database/API/I/O/network/file/queue risks before implementation.
6. Apply [`.planning/templates/validation-evidence-contract.md`](../../../.planning/templates/validation-evidence-contract.md) for the behavior slice. Define the minimum sufficient pre-implementation validation set before changing production code. If the phase depends on prior durable context, request a narrow `gsd-memory-lookup` context pack first; otherwise stay repo-local and use the phase, milestone, state artifacts, and prepared source traceability as the source of truth.
7. Create or update the validation set before implementation when the change is reasonably testable. Run the smallest decisive failing test or check first when practical to confirm the expected red state, run additional newly created checks before implementation when useful and practical, and record a justified exception when full test-first validation is impractical.
8. Implement only the minimum scoped work needed to make the selected validation set pass. If the execution reveals a durable decision or recurring insight, classify the later `gsd-session-save` follow-up as `candidate` or `none` instead of writing durable memory here.
9. Refactor only after green, then run the broader checks named in the phase file or the minimum available equivalent without adding speculative validation outside the active phase scope.
10. Before finishing, compare actual touched files, conventions used, validation path, performance/reuse evidence, and source-traceability use against `.planning/CONTEXT_INDEX.md`, `.planning/CODEBASE_MAP.md`, and the active phase/milestone source references. If the work proves either artifact wrong, stale, incomplete, or missing, update the artifact when the correction is small and directly evidenced; otherwise record a precise `$gsd-map-codebase` unified mapping refresh candidate or source-registry follow-up in state.
11. Update [`.planning/STATE.md`](../../../.planning/STATE.md) with execution status, touched areas, checks run, context routing used, source-traceability references consumed or intentionally not present, performance/reuse evidence, mapping artifact updates or refresh candidates, and an explicit durable-memory follow-up decision of `candidate` or `none`.

## Scope Guardrails
- Do not expand into unplanned features, refactors, or architecture changes.
- If the requested work exceeds the active phase, stop and send the task back to `$gsd-plan-milestone`.
- If the phase is underspecified, fill small gaps from repo evidence, but escalate if the gap changes scope or acceptance criteria.

## Required Outputs
- Implementation aligned with the active phase objective.
- A concise execution update in [`.planning/STATE.md`](../../../.planning/STATE.md) including:
  - current status
  - active milestone
  - milestone status
  - active phase
  - phase status
  - touched files or areas
  - checks run
  - source-traceability references consumed, if any, by compact `source_id`, `claim_id`, anchor, and evidence status
  - performance/reuse evidence:
    - Reusable surfaces inspected:
    - Final reuse decision: `reused | extended | composed | new-local | new-abstraction`
    - New code justification:
    - Performance-sensitive paths touched:
    - Performance risks checked:
    - Performance validation run:
    - Minimum-new-code justification:
  - codebase map and context index consulted, routing used, any deviation from routed areas, and whether a unified mapping refresh follow-up is `candidate` or `none`
  - next action

## Rules
- Follow the implementation intent from [PROJECT.md](../../../PROJECT.md) and the planning docs before adding new behavior.
- If execution touches blueprint-owned installed files, confirm whether the active phase is a blueprint-sync/update task. Do not silently edit installed reusable GSD assets in a project repository when the correct action is to update the blueprint source and sync.
- Keep active implementation traceable to the governing Project Idea Document, Technical Specification, and stack-selection/configuration-package planning context already established by planning artifacts for the phase. If those artifacts are missing, stale, or contradicted, stop and route back to planning instead of improvising detached code-first changes.
- For blueprint-self-improvement work inside the reusable GSD package, trace execution to the active milestone, active phase, and prior verification artifacts when project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifacts are intentionally absent.
- Do not stop execution solely because those project-specific artifacts do not exist for blueprint-internal improvement work.
- When the active milestone or phase includes `Source Traceability`, consume only the cited registry rows, claim IDs, and anchors needed for the phase under [`.planning/templates/source-materials-contract.md`](../../../.planning/templates/source-materials-contract.md). Do not discover requirements by broad-scanning raw source-material folders.
- Keep source-backed execution claims labeled with their original `Confirmed`, `Suggested`, or `Unknown` status. A `Suggested` source-backed recommendation is not a confirmed implementation requirement unless a later artifact or user decision confirms it; an `Unknown` claim may guide risk handling but must not become implementation authority.
- Do not duplicate registry rows or copy raw source bodies into execution notes, state updates, or handoff output. Cite compact `source_id`, `claim_id`, anchor, and evidence status instead.
- Work in small, meaningful, testable slices. Do not split into microscopic fragments or batch a large speculative test set ahead of all implementation.
- Use [`.planning/templates/validation-evidence-contract.md`](../../../.planning/templates/validation-evidence-contract.md) for minimum sufficient validation, failing-first behavior, justified exceptions, and targeted-before-broader validation.
- Do not treat one failing test or check as automatically sufficient. The validation set must be justified by the behavior slice and may be singular only when it covers the slice adequately.
- Before production-code changes, create or update the minimum sufficient validation set for the current slice when reasonably testable. Add multiple focused tests or checks when one cannot cover the relevant behavior, boundary, contract, integration, persistence, authorization, or regression risk.
- If the phase includes a justified exception to test-first, apply the nearest practical safeguard and record it.
- Prefer the smallest architecture-consistent reusable solution. Generalize only when at least two current use cases, a known near-term phase, or an existing extension point justifies it; performance safety outranks minimum-code reduction.
- If execution creates new code without inspecting the reusable surfaces named by the phase, context index, or codebase map, record why. If a new abstraction is used, justify it under the performance-first reuse contract.
- Use memory lookup only when the active phase needs prior durable context that is not already present in repo-local state.
- Apply [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md) for any vault-memory boundary question: repo artifacts remain workflow control, vault notes remain durable memory, retrieval stays in `projects/<vault-project-id>/`, sibling namespaces and shared-root durable writes are prohibited, and durable writes are only `gsd-session-save` candidates from this skill.
- Do not begin execution with broad repository scanning when `.planning/CONTEXT_INDEX.md` or the phase `Context Routing` section gives a narrower route.
- If execution must inspect files outside the routed areas, record why in `.planning/STATE.md` and mark whether a `$gsd-map-codebase` unified mapping refresh follow-up is needed.
- If the context index is missing, placeholder, stale, or misleading, do not silently ignore that. Update it when the correction is local and evidenced, or record a unified mapping refresh candidate.
- If implementation introduces or changes a route, convention, symbol/API, canonical example, validation command, or do-not-scan boundary, update `CONTEXT_INDEX.md` when the update is small and directly supported by the execution evidence.
- If implementation changes architecture, dependency direction, runtime flow, persistence shape, data shape, or integration behavior, update `CODEBASE_MAP.md` when the update is small and directly supported by the execution evidence; otherwise record a unified mapping refresh candidate in `.planning/STATE.md`.
- Prefer targeted validation from the context index before broader checks unless the phase explicitly requires a broader check first.
- Do not write durable memory from this skill; execution only produces session-save candidates for later review.
- At a meaningful execution stop point, do not leave durable-memory follow-up vague. Record whether `gsd-session-save` is warranted and why, or explicitly record `none`.
- When invoked as a delegated child, follow [`.planning/templates/delegated-agent-contract.md`](../../../.planning/templates/delegated-agent-contract.md), perform execution only, and do not continue into verification or replanning yourself.
- Report what changed, the validation set created or updated, which decisive validation ran first, any additional pre-implementation checks, and what broader checks confirmed the phase.
- End the response with explicit `Phase Status: executed` and `Milestone Status: in_progress` lines, then hand off to `$gsd-verify-phase` with a compact `Next-Step Prompt` that tells the next agent to verify the active phase against its done criteria and validation evidence.
- After returning the required outputs, stop immediately. Do not begin verification, planning, or any additional routing work yourself.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into phase, milestone, verification, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- If execution needs durable context, request `gsd-memory-lookup` scoped to `projects/<vault-project-id>/`.
- Do not read sibling project namespaces.
- Do not write durable memory during execution; only record a later `gsd-session-save` candidate when execution reveals a durable decision, debugging insight, integration behavior, or reusable pattern.

## Completion Check
- Implementation matches the active phase objective.
- The minimum sufficient validation set was defined and created or updated before implementation when reasonably testable, or a justified exception was recorded.
- Performance/reuse evidence is recorded and supports the implementation decision.
- Execution stayed inside scope or explicitly escalated when scope broke.
- Execution followed the phase context route or recorded a justified deviation and mapping artifact update or unified refresh follow-up.
- Execution consumed only prepared source traceability when present, preserved evidence statuses, and avoided duplicating registry rows or raw source bodies.
- Execution evidence remains traceable to the governing spec-defined behavior slice named by planning.
- [`.planning/STATE.md`](../../../.planning/STATE.md) records targeted and broader checks run, marks the phase as executed, and sets the next action as verification.
