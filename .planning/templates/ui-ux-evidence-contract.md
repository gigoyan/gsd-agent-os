# UI/UX Evidence Contract

## Purpose
Define structured UI/UX evidence, finding, and report artifacts.

## Owner
`ui-ux-product-reviewer`

## Output Root

```text
.planning/evidence/ui-ux/<review-id>/
```

## Required Files

```text
summary.json
artifact-manifest.json
interaction-model.json
target-behavior-model.json
root-causes.json
findings.jsonl
evidence-index.jsonl
report.md
handoff-prompt.md
```

## Review ID Format

```text
UXR-YYYYMMDD-HHMMSS-<scope-slug>
```

## UI/UX Finding Schema

```json
{
  "schema_version": 1,
  "finding_id": "UX-0001",
  "review_id": "",
  "title": "",
  "screen_route_component": "",
  "flow_id": "",
  "role_or_user_type": "",
  "ui_state": "default | edit | dirty | disabled | read_only | destructive | empty | loading | error | success | permission | responsive | accessibility | unknown",
  "evidence_status": "Confirmed | Suggested | Unknown",
  "evidence_refs": [],
  "screenshot_refs": [],
  "browser_run_refs": [],
  "code_refs": [],
  "affected_user_goal": "",
  "risk_classification": "structural_ux_risk | local_polish | evidence_gap",
  "root_cause": "",
  "local_symptoms": [],
  "recommendation": "",
  "information_preservation_decision": "Must remain visible | Can move to secondary detail | Can hide behind tooltip/details | Can be available only in confirmation/dialog/detail page | Can be removed | Needs product-owner confirmation | Not applicable",
  "priority": "Critical | High | Medium | Low",
  "severity": "blocker | critical | high | medium | low | info",
  "implementation_risk": "high | medium | low | unknown",
  "acceptance_criteria": [],
  "qa_verification_suggestions": [],
  "product_owner_confirmation_needed": false,
  "open_questions": []
}
```

## Rules

- Diagnose interaction model before listing local findings.
- Define target behavior model before recommending implementation.
- Cluster local symptoms under root causes.
- Separate structural UX risk from local polish.
- Do not create milestones.
- Do not implement code by default.
- Produce final report plus copy-paste milestone handoff prompt.
