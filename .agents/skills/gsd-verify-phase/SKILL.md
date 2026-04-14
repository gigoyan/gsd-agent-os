---
name: gsd-verify-phase
description: Verify a completed execution phase against its explicit done criteria and acceptance checks inside the Codex-native GSD workflow. Use after phase implementation when the next step is to run checks, assess results, write a verification artifact, and decide pass, fail, or partial.
---

# GSD Verify Phase

Verify the active phase before it is considered complete.
Use this skill to compare implementation results against the phase and milestone criteria, write a verification artifact, and update session state.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), the active phase file, the parent milestone file, and the governing spec or planning artifacts already named by those active artifacts.
2. Review which tests or checks were added or changed and run the targeted and broader checks defined in the phase or the closest available equivalent. If the verification needs prior durable context, request a narrow `gsd-memory-lookup` context pack first; otherwise keep verification repo-local and driven by the active artifacts.
3. Compare actual results with the phase done criteria, milestone acceptance criteria, the governing spec-defined behavior slice for the phase, and the adequacy of the validation used for the changed behavior.
4. Write or refresh a verification file under [`.planning/verification/`](../../../.planning/verification/) using the active phase naming pattern, including test-first evidence and any justified exception. If verification exposes a durable insight worth keeping, record the later `gsd-session-save` follow-up as `candidate` or `none` instead of writing durable memory here.
5. Decide whether the phase is complete and whether the milestone is now complete or still in progress with follow-up phases remaining.
6. Update [`.planning/STATE.md`](../../../.planning/STATE.md) with disposition, milestone status, phase status, latest verification, residual risks, next action, and an explicit durable-memory follow-up decision of `candidate` or `none`.

## Source Template
- [`.planning/templates/verification-template.md`](../../../.planning/templates/verification-template.md)

## Disposition Rules
- `pass`: checks and observed behavior satisfy the phase criteria, remain traceable to the governing spec-defined behavior slice, and have adequate validation for the changed behavior, or a justified exception with the nearest practical safeguard.
- `partial`: progress is real but not enough to declare the phase complete, including when validation is incomplete or traceability to the governing spec remains uncertain.
- `fail`: blocking gaps, regressions, missing validation evidence, missing spec traceability, or unjustified code-first changes prevent completion.

## Required Outputs
- Verification artifact named like the active phase file and stored in [`.planning/verification/`](../../../.planning/verification/).
- Verification artifact records tests or checks added or changed, what targeted validation ran first, whether failing-first evidence was observed, any justification when it was not, and how the evidence maps back to the governing spec-defined behavior slice.
- Updated [`.planning/STATE.md`](../../../.planning/STATE.md) showing the latest verification result and next action.
- Response includes explicit `Phase Status` and `Milestone Status` lines for orchestrator routing.
- Residual risks listed even when the phase passes, if any uncertainty remains.

## Rules
- Verification is not implementation. Do not silently expand the phase while verifying.
- Use memory lookup only to recover missing durable context that affects the verdict; do not broaden verification into archival research.
- Do not write durable memory from this skill; verification remains read-only on the vault and only identifies later session-save candidates.
- At a meaningful verification stop point, explicitly decide whether later `gsd-session-save` is warranted. If not, record `none` rather than leaving the outcome implicit.
- Mark `partial` or `fail` when behavior changed without adequate validation evidence, without a justified exception, or without a clear trace back to the governing spec artifacts and planned behavior slice.
- If a failure suggests new work, capture it in the verification artifact and hand back to planning or a follow-up phase.
- When invoked as a delegated child under `$gsd-run-milestone`, perform verification only. Do not orchestrate, do not delegate, and do not continue into replanning or execution yourself.
- As a delegated child, do not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- If the phase passes and the milestone is still incomplete, set `Phase Status: completed`, set `Milestone Status: in_progress`, and emit a `Next-Step Prompt` that sends the next agent to `$gsd-plan-milestone` to define the next bounded phase inside the current milestone.
- If verification shows the active milestone is complete, set `Milestone Status: completed` and do not emit a `Next-Step Prompt`. Instead, state briefly that the milestone is complete and suggest the next incomplete milestone or milestones from `.planning/ROADMAP.md` if any exist.
- If verification is `partial` or `fail`, keep `Milestone Status: in_progress` unless the milestone is explicitly abandoned, and emit a `Next-Step Prompt` only when the immediate recovery action is clear; if not, say briefly that no automatic next-step prompt applies.
- After returning the required outputs, stop immediately. Do not begin planning, execution, or any additional routing work yourself.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into verification, phase, milestone, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- Prefer concrete evidence over narrative claims.

## Completion Check
- A verification artifact exists with checks, results, test-first evidence, spec-traceability evidence, residual risks, and disposition.
- [`.planning/STATE.md`](../../../.planning/STATE.md) reflects the latest verification outcome and whether the milestone is still in progress or complete.
