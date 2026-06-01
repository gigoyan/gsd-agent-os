# Validation Evidence Contract

## Minimum Sufficient Validation
- Validation must be scoped to the smallest meaningful behavior slice being changed.
- One test or check is sufficient only when it adequately proves the slice.
- Add the focused combination needed for relevant happy path, failure path, edge case, validation boundary, authorization boundary, contract/API, regression, integration, persistence, or manual behavior evidence.
- Do not create oversized speculative test batches unrelated to the active slice.

## Targeted Before Broader
- Prefer the smallest decisive targeted check before broader validation.
- Run broader checks when the phase requires them, targeted evidence is stale or incomplete, shared behavior changed, or risk justifies broader confirmation.
- If broader checks are intentionally skipped during verification, record why.

## Failing-First
- Before implementation, create or update the minimum sufficient validation set when the change is reasonably testable.
- Run the first decisive failing test or check when practical to confirm the expected red state.
- Additional pre-implementation checks are required only when useful for the slice.

## Justified Exceptions
- If test-first validation is impractical, record why before implementation.
- Use the nearest practical safeguard, such as a regression check, smoke check, static validation command, manual verification note, characterization check, or verifier confirmation.

## Required Execution Evidence
- Behavior slice validated.
- Validation set created or updated.
- First decisive failing check, or justified exception.
- Targeted checks run and results.
- Broader checks run, skipped, or deferred with reason.
- How validation maps to phase done criteria and milestone acceptance criteria.

## Required Verification Evidence
- Execution evidence reviewed.
- Whether the validation set was sufficient for the behavior slice.
- Targeted verifier check rerun and result.
- Broader-check rerun decision and reason.
- Any test-first exception and nearest safeguard.
- Residual risks.
- Disposition: `pass | partial | fail`.

## Verification Disposition
- `pass`: criteria are satisfied, traceability is clear, and validation is adequate, or a justified exception has the nearest practical safeguard.
- `partial`: progress is real but validation, traceability, broader confirmation, or residual risk is incomplete enough that the phase is not fully complete.
- `fail`: blocking behavior gaps, regressions, missing validation evidence, missing traceability, or unjustified code-first changes prevent completion.
