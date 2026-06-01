# Phase Template

## Objective
- What does this phase need to achieve?
- If the phase depends on prior durable context, note whether a narrow memory lookup is needed before implementation.
- State the concrete execution result expected at the end of this phase.

## Behavior Slice
- What coherent behavior or scenario set is being changed?
- Name the exact spec, workflow, or implementation slice this phase is responsible for.

## Steps
1. Read `.planning/CONTEXT_INDEX.md` when available and identify the narrowest relevant routing row or module card before scanning source files.
2. If `.planning/source-materials/SOURCE_MATERIALS.md` exists and the milestone or phase cites source-backed claims, consume the relevant registry claim IDs and `source_id#anchor` references instead of broad-scanning raw source-material folders.
3. Define the minimum sufficient validation set for this behavior slice.
4. Update the required tests or checks first when practical.
5. Implement the minimum change needed to satisfy that validation.
6. If the phase produces durable insight, leave a session-save candidate for later instead of writing memory here.

## Constraints
- C1:
- C2:

## Touched Areas
- Paths:
- Expected change type:
- Note any files that must stay untouched unless the phase is explicitly replanned.

## Context Routing
- Context index consulted:
- Routing row used:
- Module card used:
- Start-here paths:
- Inspect-next paths:
- Usually-changes paths:
- Avoid-unless-needed paths:
- Validation path:
- Refresh needed before execution: `yes` | `no` | `unknown`

## Performance And Reuse Check
- Performance-sensitive path: `yes | no | unknown`; notes:
- Existing reusable surfaces to inspect:
- Canonical examples to follow:
- Extension point preferred:
- Duplication risk:
- New abstraction allowed: `yes | no | only-if-justified`
- Minimum-new-code constraint:

## Source Traceability
- Registry consulted: `yes` | `no` | `not-present`
- Registry path: `.planning/source-materials/SOURCE_MATERIALS.md`
- Consumption rule: follow `.planning/templates/source-materials-contract.md`; cite compact `source_id`, claim IDs, anchors, and evidence statuses; do not duplicate registry rows or copy raw source bodies.

| Applies To | source_id | claim_id | anchor | evidence_status | Execution use | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| behavior slice |  |  |  | `Confirmed` |  |  |
| constraint |  |  |  | `Suggested` | Treat as suggested until confirmed. |  |
| risk or gap |  |  |  | `Unknown` | Do not implement as authority. |  |

- Source conflicts or unknowns affecting execution:
- Registry consumption-log follow-up needed after planning or verification: `yes` | `no` | `unknown`

## Implementation Notes
- Concrete instructions, examples, or sequencing notes needed to execute this phase without guesswork.
- When the phase relies on repo evidence, recommendations, or unresolved gaps, keep them labeled as `Confirmed`, `Suggested`, or `Unknown` instead of flattening them into certainty.
- When the phase relies on registered source material, preserve the source claim evidence status; do not turn a `Suggested` claim into a `Confirmed` requirement during execution.

## Test-First Validation
- Contract: `.planning/templates/validation-evidence-contract.md`
- Primary test level:
- Minimum sufficient pre-implementation validation set:
- First decisive failing test or check:
- Additional tests or checks required for this slice:
- Failing-first expectation or exception note:
- Broader phase checks:
- Memory-aware context pack:

## Done Criteria
- DC1: The minimum sufficient validation set exists for the changed behavior before implementation, or an exception is justified with the nearest safeguard.
- DC2: Implementation is the minimum needed to satisfy the selected validation set and broader required checks.
- DC3: Validated behavior satisfies the milestone acceptance criteria with evidence suitable for verification.
- DC4: Phase-specific constraints and implementation notes were respected, or any necessary deviation was escalated for replanning.
- DC5: Context routing was followed or a justified exception was recorded when the context index was missing, stale, or insufficient.
- DC6: Source traceability was followed when present, with `Suggested` and `Unknown` claims preserved as non-authoritative unless later confirmed.
- DC7: Performance/reuse evidence is recorded and supports the implementation decision.

## Post-Verification Routing
- In standalone verification, if this phase passes and the milestone is incomplete, the next action should be `$gsd-plan-milestone` for the next bounded phase in the same milestone.
- Any verification-and-next-phase-planning child must follow `.planning/templates/delegated-agent-contract.md`.
- In `$gsd-run-milestone`, the root orchestrator may assign a verification-and-next-phase-planning child that verifies this phase and, after a pass with an incomplete milestone, creates the next bounded phase in the same delegated step.
- The `$gsd-run-milestone` composite child must not create a next phase on `fail`, `partial`, blocked verification, or completed milestone, and must not execute the newly created phase.
- Keep the phase repo-local unless the next phase explicitly needs a memory lookup or later session-save follow-up.
