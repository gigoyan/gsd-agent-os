# Evidence Status And Reference Contract

## Purpose
Define shared evidence confidence labels and reference syntax for GSD evidence artifacts.

## Evidence Statuses

Use exactly:

- `Confirmed`: directly supported by code, screenshot, browser behavior, test, log, documentation, source material, or explicit user input.
- `Suggested`: reasoned inference from partial evidence.
- `Unknown`: missing, inaccessible, contradictory, stale, or unverified evidence.

## Rules

- Do not promote `Suggested` to `Confirmed` without stronger evidence.
- Do not treat `Unknown` as implementation authority.
- Preserve evidence status across planning, execution, verification, QA, UI/UX review, story generation, and publishing.
- Every material finding must include at least one evidence reference or state why evidence is `Unknown`.

## Reference Schemes

Use compact references:

- `repo://<path>#L<start>-L<end>`
- `browser-run://<run-id>/summary.json`
- `browser-run://<run-id>/action-log.json#<step-id>`
- `browser-run://<run-id>/screenshots/<file>`
- `browser-run://<run-id>/page-states/<file>`
- `flow://<flow-id>#<step-id>`
- `ux-review://<review-id>#<finding-id>`
- `qa://<qa-session-id>#<finding-id>`
- `story://<story-id>`
- `source-material://<source-id>#<claim-id>`

## Evidence Reference Object

```json
{
  "ref": "browser-run://<run-id>/screenshots/<screenshot-file>",
  "kind": "screenshot",
  "evidence_status": "Confirmed",
  "notes": ""
}
```

## Completion Check

- All findings preserve `Confirmed | Suggested | Unknown`.
- Unknowns are listed as evidence gaps.
- References are compact and do not duplicate raw source bodies.
