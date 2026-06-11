# UI Discovery Coverage Contract

## Purpose

Define the coverage report produced by `$gsd-ui-discovery-orchestrator` after scoped browser-backed discovery and downstream GSD outputs.

## Required Artifacts

```text
.planning/ui-discovery/<goal-id>/coverage-report.md
.planning/ui-discovery/<goal-id>/coverage-report.json
```

## Coverage Questions

The report must answer:

- request interpreted
- scope covered
- roles covered
- pages/routes discovered
- pages/routes visited
- forms discovered
- forms tested
- actions discovered
- actions executed
- actions skipped and why
- destructive/payment/send actions blocked or allowed
- validation states tested
- flows created/updated
- stories created/updated
- QA sessions created
- defect candidates
- remaining unknowns
- recommended next GSD action

## JSON Schema

```json
{
  "schema_version": 1,
  "goal_id": "",
  "request_interpreted": "",
  "scope_covered": {},
  "roles_covered": [],
  "pages_discovered": [],
  "pages_visited": [],
  "forms_discovered": [],
  "forms_tested": [],
  "actions_discovered": [],
  "actions_executed": [],
  "actions_skipped": [],
  "blocked_or_allowed_dangerous_actions": [],
  "validation_states_tested": [],
  "flow_refs": [],
  "story_refs": [],
  "qa_refs": [],
  "defect_candidates": [],
  "remaining_unknowns": [],
  "recommended_next_gsd_action": ""
}
```
