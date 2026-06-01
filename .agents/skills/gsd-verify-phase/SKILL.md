---
name: gsd-verify-phase
description: Verify a completed execution phase against its explicit done criteria and acceptance checks inside the GSD coding-agent workflow. Use after phase implementation when the next step is to run checks, assess results, write a verification artifact, and decide pass, fail, or partial.
---

# GSD Verify Phase

Verify the active phase before it is considered complete.
Use this skill to compare implementation results against the phase and milestone criteria, write a verification artifact, and update session state. Standalone verification remains verification-only.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), the active phase file, the parent milestone file, and the governing spec or planning artifacts already named by those active artifacts.
2. Read the milestone and phase `Source Traceability` sections. If they cite `.planning/source-materials/SOURCE_MATERIALS.md`, follow the runtime consumption contract in [`.planning/templates/source-materials-contract.md`](../../../.planning/templates/source-materials-contract.md) and read only the cited registry rows, claim IDs, `source_id#anchor` references, and evidence statuses needed to verify this phase.
3. Read `.planning/CODEBASE_MAP.md`, `.planning/CONTEXT_INDEX.md`, and the phase `Context Routing` section. Verify implementation against the `Agent Context Routing Contract`: routed start paths, canonical examples, conventions, targeted validation, avoided areas, justified deviations, and any required context-index update or `$gsd-map-codebase` refresh candidate.
4. Review execution evidence first: changed tests or checks, the declared validation set, failing-first evidence or exception, checks run, broader-check evidence, `Performance And Reuse Evidence`, source-traceability references consumed, and any stated gaps. Inspect changed tests or checks as evidence; do not recreate them. If the verification needs prior durable context, request a narrow `gsd-memory-lookup` context pack first; otherwise keep verification repo-local and driven by the active artifacts.
5. Apply [`.planning/templates/validation-evidence-contract.md`](../../../.planning/templates/validation-evidence-contract.md). Decide whether the execution validation set was sufficient for the governing behavior slice and whether test-first behavior happened, or whether a justified exception with the nearest practical safeguard was recorded.
6. Rerun only the smallest decisive targeted check needed for independent confirmation. Rerun broader checks only when the phase requires them, execution evidence is missing or stale, or risk justifies broader confirmation. Record why broader checks were not rerun when intentionally skipped.
7. Compare actual results with the phase done criteria, milestone acceptance criteria, the governing spec-defined behavior slice for the phase, and the adequacy of the validation used for the changed behavior.
8. For blueprint-self-improvement work inside the reusable GSD package, verify traceability against the active milestone, active phase, shared contracts, and prior verification chain when project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifacts are intentionally absent.
9. Verify that any `Confirmed`, `Suggested`, and `Unknown` handling used by the changed behavior matches the shared meanings in [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md), and verify source-backed claim consumption against [`.planning/templates/source-materials-contract.md`](../../../.planning/templates/source-materials-contract.md).
10. Verify performance/reuse handling against [`.planning/templates/performance-first-reuse-contract.md`](../../../.planning/templates/performance-first-reuse-contract.md), including reusable surfaces inspected, final reuse decision, new code or abstraction justification, performance-sensitive paths touched, risk checks, validation run, and minimum-new-code justification.
11. Write or refresh a verification file under [`.planning/verification/`](../../../.planning/verification/) using the active phase naming pattern, including execution evidence reviewed, validation-set sufficiency, performance/reuse evidence, verifier confirmation checks, any justified exception, broader-check rerun decision, source-traceability handling when relevant, and mapping-artifact evidence: whether the codebase map and context index were consulted, which routing row or module card was used, whether canonical examples and conventions were followed, whether unnecessary scanning was avoided, whether validation used the intended route, and whether mapping artifacts were updated or a unified mapping refresh candidate was recorded. If verification exposes a durable insight worth keeping, record the later `gsd-session-save` follow-up as `candidate` or `none` instead of writing durable memory here.
12. Decide whether the phase is complete and whether the milestone is now complete or still in progress with follow-up phases remaining.
13. Standalone verification and normal delegated verification stop after the verification result and routing output. Exception: when the child prompt explicitly assigns the `$gsd-run-milestone` verification-and-next-phase-planning composite step, and verification passes while the milestone is incomplete, create exactly one next bounded phase in the same active milestone using `$gsd-plan-milestone` rules.
14. If the milestone has completed and cleanup would remove temporary blueprint-improvement scaffolding, stop at the verification result and ask the user whether cleanup should run before any deletion or reset happens.
15. Update [`.planning/STATE.md`](../../../.planning/STATE.md) with disposition, milestone status, phase status, latest verification, residual risks, source-traceability handling when relevant, next action, and an explicit durable-memory follow-up decision of `candidate` or `none`.

## Source Template
- [`.planning/templates/verification-template.md`](../../../.planning/templates/verification-template.md)

## Disposition Rules
- Use [`.planning/templates/validation-evidence-contract.md`](../../../.planning/templates/validation-evidence-contract.md) for validation disposition. Local routing consequences remain defined below.

## Required Outputs
- Verification artifact named like the active phase file and stored in [`.planning/verification/`](../../../.planning/verification/).
- Verification artifact records execution evidence reviewed, tests or checks added or changed, validation-set sufficiency, what targeted validation ran first, whether failing-first evidence was observed, any justification when it was not, verifier confirmation checks, broader-check rerun decision, and how the evidence maps back to the governing spec-defined behavior slice.
- Verification artifact records performance/reuse evidence and whether it satisfies the performance-first reuse contract.
- Verification artifact records source-traceability handling when relevant, using compact `source_id`, `claim_id`, anchor, and evidence status references instead of duplicated registry rows or raw source bodies.
- Updated [`.planning/STATE.md`](../../../.planning/STATE.md) showing the latest verification result and next action.
- Response includes explicit `Phase Status` and `Milestone Status` lines for orchestrator routing.
- Residual risks listed even when the phase passes, if any uncertainty remains.

## Rules
- Verification is not implementation. Do not silently expand the phase while verifying.
- Do not perform a second execution pass. Do not recreate tests, refactor implementation, change production code, or add new behavior while verifying.
- Use execution evidence as the starting point. Verification confirms adequacy and truthfulness with selective independent checks, not by blindly repeating every execution command.
- For blueprint-sync/update phases, verify that project-owned files were preserved and managed blocks were updated only inside markers.
- Use memory lookup only to recover missing durable context that affects the verdict; do not broaden verification into archival research.
- Apply [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md) for vault-memory boundaries: verification artifacts stay repo-local, durable memory stays under `projects/<vault-project-id>/`, sibling namespaces and shared-root durable writes are prohibited, and verification may only record later `gsd-session-save` candidates.
- Do not write durable memory from this skill; verification remains read-only on the vault and only identifies later session-save candidates.
- At a meaningful verification stop point, explicitly decide whether later `gsd-session-save` is warranted. If not, record `none` rather than leaving the outcome implicit.
- Mark `partial` or `fail` when behavior changed without adequate validation evidence, without a justified exception, or without a clear trace back to the governing spec artifacts and planned behavior slice.
- Mark `partial` or `fail` when performance/reuse evidence is missing, superficial, contradicted by the diff, or when performance-sensitive paths lack appropriate risk checks or validation.
- Mark `partial` or `fail` when the execution validation set was insufficient for the behavior slice and no justified exception or recovery path supports completion.
- Return `partial` or record explicit residual risk when implementation changed routing, conventions, symbols, canonical examples, or validation guidance but `CONTEXT_INDEX.md` was not updated or marked stale.
- Return `partial` or record explicit residual risk when implementation changed architecture, dependency direction, runtime flow, data, persistence, or integration behavior but `CODEBASE_MAP.md` was not updated or a unified mapping refresh candidate was not recorded.
- Return `partial` or record explicit residual risk when validation commands changed but the validation matrix or `.planning/tool-capabilities.md` was not updated as applicable.
- Return `partial` or record explicit residual risk when context-index routing was materially wrong and no correction or unified mapping refresh candidate was recorded.
- For blueprint-self-improvement work inside the reusable GSD package, treat the active milestone, active phase, shared contracts, and prior verification chain as acceptable governing traceability when project-specific Project Idea Document, Technical Specification, and stack-selection/configuration-package artifacts are intentionally absent.
- When milestone or phase source traceability is present, verify that execution consumed only the prepared registry rows, claim IDs, and anchors needed for the phase and did not broad-scan raw source-material folders to discover requirements.
- Mark `partial` or `fail` when execution or verification silently promotes `Suggested` source-backed claims to `Confirmed`, treats `Unknown` claims as implementation authority, or drops material source-status distinctions without justification.
- Do not duplicate registry rows or copy raw source bodies into verification artifacts, state updates, or response output. Cite compact source references and evidence statuses.
- Mark `partial` or `fail` when changed behavior silently blurs `Confirmed`, `Suggested`, and `Unknown`, or when choice-shaped user interaction falls back to free-text without justification.
- If a failure suggests new work, capture it in the verification artifact and hand back to planning or a follow-up phase.
- Standalone verification remains verification-only. Normal delegated verification remains verification-only.
- Narrow exception: when the child prompt explicitly assigns the `$gsd-run-milestone` verification-and-next-phase-planning composite step, the child may create exactly one next bounded phase after a passing verification if the milestone is incomplete.
- In the composite step, do not create the next phase on `fail`, `partial`, blocked verification, or completed milestone.
- In the composite step, do not execute the next phase, continue the milestone loop, orchestrate, delegate, or route beyond creating the single next bounded phase.
- When invoked as a delegated child, follow [`.planning/templates/delegated-agent-contract.md`](../../../.planning/templates/delegated-agent-contract.md). Under `$gsd-run-milestone` without the explicit composite assignment, limit the work to verification and do not create a follow-up phase or execute implementation yourself.
- If the phase passes and the milestone is still incomplete, set `Phase Status: completed`, set `Milestone Status: in_progress`, and emit a `Next-Step Prompt` that sends the next agent to `$gsd-plan-milestone` to define the next bounded phase inside the current milestone.
- In the explicit `$gsd-run-milestone` composite step, replace that handoff by creating the next bounded phase directly in the same child response, then emit routing output for the root orchestrator to execute that new active phase.
- If verification shows the active milestone is complete, set `Milestone Status: completed` and do not emit a `Next-Step Prompt`. Instead, state briefly that the milestone is complete and suggest the next incomplete milestone or milestones from `.planning/ROADMAP.md` if any exist.
- If the active milestone is a temporary blueprint-improvement effort and verification completion would make cleanup eligible, stop and ask the user whether cleanup should run; do not delete or reset scaffolding during verification without explicit approval.
- If verification is `partial` or `fail`, keep `Milestone Status: in_progress` unless the milestone is explicitly abandoned, and emit a `Next-Step Prompt` only when the immediate recovery action is clear; if not, say briefly that no automatic next-step prompt applies.
- After returning the required outputs, stop immediately. Outside the explicit `$gsd-run-milestone` composite step, do not begin planning, execution, or any additional routing work yourself.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into verification, phase, milestone, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- Prefer concrete evidence over narrative claims.
- Verification should check not only whether behavior passed, but whether the implementation used the intended context route or justified deviations.
- If implementation scanned broadly because the context index was missing, stale, or misleading, mark a `$gsd-map-codebase` unified mapping refresh follow-up candidate.
- Do not fail a phase only because context routing was imperfect if behavior and validation are correct, but require the stale routing to be fixed or recorded as residual risk or a unified mapping refresh candidate.
- If verification needs durable context, request `gsd-memory-lookup` scoped to `projects/<vault-project-id>/`.
- Do not broaden verification into shared-vault or sibling-project retrieval.
- If verification exposes durable insight, record a later `gsd-session-save` candidate only; do not write durable memory during verification.

## Completion Check
- A verification artifact exists with execution evidence reviewed, selective verifier confirmation, validation-set adequacy, test-first evidence, spec-traceability evidence, residual risks, and disposition.
- Verification records context-routing evidence, mapping-artifact truthfulness checks, and any unified mapping refresh follow-up.
- Verification records source-traceability handling when relevant, preserves `Confirmed`, `Suggested`, and `Unknown`, and avoids duplicating registry rows or raw source bodies.
- [`.planning/STATE.md`](../../../.planning/STATE.md) reflects the latest verification outcome and whether the milestone is still in progress or complete.
