---
name: gsd-execute-phase
description: Implement the currently active phase from the Codex-native GSD workflow while staying strictly inside its defined scope. Use when an active phase already exists and the next step is to change code, configuration, or docs according to the phase file rather than create a new plan.
---

# GSD Execute Phase

Execute the active phase and nothing larger.
Use this skill after milestone planning is complete and before verification has been run.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), and resolve the active phase path.
2. Read the active phase file, the parent milestone file, and the governing spec or planning artifacts already named by those active artifacts so implementation stays anchored to the Project Idea Document, Technical Specification, and stack-selection/configuration-package context rather than treating the phase as detached.
3. Read `.planning/CONTEXT_INDEX.md` and the phase `Context Routing` section before scanning source files. Start with the routed start-here paths and inspect-next paths. Avoid unrelated areas unless repo evidence shows the phase cannot be completed without them.
4. For each meaningful behavior slice in scope, create or update the targeted tests or checks first when the change is reasonably testable. If the phase depends on prior durable context, request a narrow `gsd-memory-lookup` context pack first; otherwise stay repo-local and use the phase, milestone, and state artifacts as the source of truth.
5. Run the targeted test or check first when practical to confirm the expected failing state, or record why that is not practical.
6. Implement only the minimum scoped work needed to make the targeted validation pass. If the execution reveals a durable decision or recurring insight, classify the later `gsd-session-save` follow-up as `candidate` or `none` instead of writing durable memory here.
7. Refactor only after green, then run the broader checks named in the phase file or the minimum available equivalent.
8. Update [`.planning/STATE.md`](../../../.planning/STATE.md) with execution status, touched areas, checks run, and an explicit durable-memory follow-up decision of `candidate` or `none`.

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
  - context index consulted, routing used, any deviation from routed areas, and whether a context-index refresh follow-up is `candidate` or `none`
  - next action

## Rules
- Follow the implementation intent from [PROJECT.md](../../../PROJECT.md) and the planning docs before adding new behavior.
- If execution touches blueprint-owned installed files, confirm whether the active phase is a blueprint-sync/update task. Do not silently edit installed reusable GSD assets in a project repository when the correct action is to update the blueprint source and sync.
- Keep active implementation traceable to the governing Project Idea Document, Technical Specification, and stack-selection/configuration-package planning context already established by planning artifacts for the phase. If those artifacts are missing, stale, or contradicted, stop and route back to planning instead of improvising detached code-first changes.
- For blueprint-self-improvement work inside the reusable GSD package, trace execution to the active milestone, active phase, and prior verification artifacts when project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifacts are intentionally absent.
- Do not stop execution solely because those project-specific artifacts do not exist for blueprint-internal improvement work.
- Work in small, meaningful, testable slices. Do not split into microscopic fragments or batch a large speculative test set ahead of all implementation.
- If the phase includes a justified exception to test-first, apply the nearest practical safeguard and record it.
- Use memory lookup only when the active phase needs prior durable context that is not already present in repo-local state.
- Do not begin execution with broad repository scanning when `.planning/CONTEXT_INDEX.md` or the phase `Context Routing` section gives a narrower route.
- If execution must inspect files outside the routed areas, record why in `.planning/STATE.md` and mark whether a `$gsd-refresh-context-index` follow-up is needed.
- If the context index is missing, placeholder, stale, or misleading, do not silently ignore that. Record a refresh follow-up candidate.
- Prefer targeted validation from the context index before broader checks unless the phase explicitly requires a broader check first.
- Do not write durable memory from this skill; execution only produces session-save candidates for later review.
- At a meaningful execution stop point, do not leave durable-memory follow-up vague. Record whether `gsd-session-save` is warranted and why, or explicitly record `none`.
- When invoked as a delegated child under `$gsd-run-milestone`, perform execution only. Do not orchestrate, do not delegate, and do not continue into verification or replanning yourself.
- As a delegated child, do not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- Report what changed, which validation ran first, and what broader checks confirmed the phase.
- End the response with explicit `Phase Status: executed` and `Milestone Status: in_progress` lines, then hand off to `$gsd-verify-phase` with a compact `Next-Step Prompt` that tells the next agent to verify the active phase against its done criteria and validation evidence.
- After returning the required outputs, stop immediately. Do not begin verification, planning, or any additional routing work yourself.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into phase, milestone, verification, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- If execution needs durable context, request `gsd-memory-lookup` scoped to `projects/<vault-project-id>/`.
- Do not read sibling project namespaces.
- Do not write durable memory during execution; only record a later `gsd-session-save` candidate when execution reveals a durable decision, debugging insight, integration behavior, or reusable pattern.

## Completion Check
- Implementation matches the active phase objective.
- Targeted tests or checks were updated first, or a justified exception was recorded.
- Execution stayed inside scope or explicitly escalated when scope broke.
- Execution followed the phase context route or recorded a justified deviation and refresh follow-up.
- Execution evidence remains traceable to the governing spec-defined behavior slice named by planning.
- [`.planning/STATE.md`](../../../.planning/STATE.md) records targeted and broader checks run, marks the phase as executed, and sets the next action as verification.
