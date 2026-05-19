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
2. Define the targeted validation for this slice.
3. Update the most relevant tests or checks first when practical.
4. Implement the minimum change needed to satisfy that validation.
5. If the phase produces durable insight, leave a session-save candidate for later instead of writing memory here.

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

## Implementation Notes
- Concrete instructions, examples, or sequencing notes needed to execute this phase without guesswork.
- When the phase relies on repo evidence, recommendations, or unresolved gaps, keep them labeled as `Confirmed`, `Suggested`, or `Unknown` instead of flattening them into certainty.

## Test-First Validation
- Primary test level:
- First tests or checks:
- Failing-first expectation or exception note:
- Broader phase checks:
- Memory-aware context pack:

## Done Criteria
- DC1: Targeted validation exists for the changed behavior, or an exception is justified with the nearest safeguard.
- DC2: Implementation is the minimum needed to satisfy the targeted validation and broader required checks.
- DC3: Validated behavior satisfies the milestone acceptance criteria with evidence suitable for verification.
- DC4: Phase-specific constraints and implementation notes were respected, or any necessary deviation was escalated for replanning.
- DC5: Context routing was followed or a justified exception was recorded when the context index was missing, stale, or insufficient.

## Post-Verification Routing
- If this phase passes and the milestone is incomplete, the next action should be `$gsd-plan-milestone` for the next bounded phase in the same milestone.
- Keep the phase repo-local unless the next phase explicitly needs a memory lookup or later session-save follow-up.
