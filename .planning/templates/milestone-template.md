# Milestone Template

## Goal
- What meaningful outcome does this milestone deliver?
- If the milestone depends on prior durable context, note whether a narrow memory lookup is needed before planning.
- State the concrete end condition, not just the topic area.

## In Scope
- List the work included in this milestone.
- Prefer concrete deliverables, workflow changes, templates, and documents over vague themes.

## Out Of Scope
- List the work explicitly excluded from this milestone.
- Name tempting adjacent work that should not be folded into this milestone.

## Known Inputs
- Confirmed:
  - User-confirmed requirements:
  - Repo evidence and current constraints:
  - Registered source-material claims:
  - Concrete examples or fixed rules to preserve:
- Suggested:
  - Recommended milestone framing, sequencing, or implementation direction that still needs confirmation:
  - Source-backed suggestions that are not confirmed requirements:
- Unknown:
  - Open scope, dependency, or readiness gaps that still need confirmation:
  - Source-material conflicts, missing anchors, or unclear applicability:

## Source Traceability
- Registry consulted: `yes` | `no` | `not-present`
- Registry path: `.planning/source-materials/SOURCE_MATERIALS.md`
- Consumption rule: cite compact `source_id`, claim IDs, anchors, and evidence statuses; do not duplicate registry rows or copy raw source bodies.

| Use | source_id | claim_id | anchor | evidence_status | Downstream status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| scope |  |  |  | `Confirmed` | `Confirmed` |  |
| criterion |  |  |  | `Suggested` | `Suggested` | Keep suggested claims out of confirmed requirements until confirmed. |
| gap |  |  |  | `Unknown` | `Unknown` |  |

- Conflicts or unknowns from registry:
- Registry consumption-log follow-up needed: `yes` | `no` | `unknown`

## Context Routing
- Context index status:
- Relevant routing rows:
- Relevant module cards:
- Files or areas to inspect first:
- Areas to avoid unless needed:
- Validation route from context index:
- Context-index refresh needed before execution: `yes` | `no` | `unknown`

## Assumptions
- A1:
- A2:

## Risks
- R1:
- R2:

## Acceptance Criteria
- AC1: Behavior-focused outcome
- AC2: Behavior-focused outcome
- Make each criterion specific enough that verification can clearly pass or fail it.

## Validation Strategy
- Contract: `.planning/templates/validation-evidence-contract.md`
- Behavior slices:
- Test level(s) and first tests or checks:
- Exception note or fallback:
- Memory-aware handoff note:
- Link each slice to the acceptance criteria it proves.

## Performance And Reuse Strategy
- Reuse-first surfaces:
- Performance-sensitive slices:
- Hot-path / I/O / API / database / queue risks:
- New abstraction policy:

## Dependencies
- External:
- Internal:

## Deliverables
- D1:
- D2:

## Implementation Notes
- Record concrete instructions, examples, or sequencing constraints that later phases must preserve.
- Include file or artifact targets when already known.
- Keep recommendations and inferred sequencing visibly `Suggested` until stronger evidence or explicit confirmation makes them `Confirmed`.
- Keep source-backed recommendations visibly `Suggested` unless the registry claim is confirmed and the downstream requirement is also confirmed by user decision or stronger evidence.
- Use `.planning/CONTEXT_INDEX.md` to keep later phase execution and verification scoped to the smallest relevant file set.

## Planned Phases
| Phase | Name | Status | Goal |
| --- | --- | --- | --- |
| P01 |  | pending |  |

## Phase Details
### P01
- Objective:
- Scope boundary:
- Expected touched areas:
- Source traceability:
- First validation:
- Key implementation notes:
- Exit condition:

## Milestone Status
- `pending` | `in_progress` | `completed` | `blocked`

## Next Planning Trigger
- What condition should cause the next phase to be planned?
- If the next phase needs remembered context, keep the milestone repo-local and route that context through `gsd-memory-lookup` instead of turning planning state into memory.
