# QA Evidence Contract

## Purpose
Define QA session, defect candidate, and coverage artifacts.

## Owner
`gsd-qa-tester`

## Output Root

```text
.planning/qa/**
.planning/evidence/browser-runs/**
```

## Session Files

```text
.planning/qa/sessions/<qa-session-id>/
  qa-report.md
  qa-report.json
  test-charter.md
  test-cases.md
  defects.md
  evidence-manifest.json
```

## Coverage Matrix

Each QA session should include a coverage matrix in `qa-report.md` and `qa-report.json` that maps flows, roles, user stories when available, test cases, evidence references, and defect candidates.

## defect candidate Schema

```json
{
  "schema_version": 1,
  "defect_id": "QA-F001",
  "qa_session_id": "",
  "title": "",
  "type": "functional | regression | accessibility | permission | data | performance | UX | reliability | unknown",
  "severity": "blocker | critical | high | medium | low",
  "priority": "P0 | P1 | P2 | P3 | unknown",
  "status": "candidate | confirmed | rejected | needs_triage",
  "environment": "",
  "route_or_flow": "",
  "role": "",
  "preconditions": [],
  "steps_to_reproduce": [],
  "expected_result": "",
  "actual_result": "",
  "evidence_refs": [],
  "browser_run_refs": [],
  "affected_user_goal": "",
  "suspected_root_cause": "",
  "regression_risk": "",
  "suggested_verification": []
}
```

## Rules

- QA can run without user stories.
- QA may consume user stories and Flow Intelligence when available.
- QA must not publish Vault pages.
- QA must not own broad UX redesign unless invoked in UX-verification mode.
