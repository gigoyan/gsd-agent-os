# Interaction Model And Target Behavior Contract

## Purpose
Force product-level UI/UX synthesis before local findings.

## Interaction Model Diagnosis

Select one or more current interaction models:

- read-only management table
- bulk-edit table
- form
- dashboard
- approval/review queue
- settings page
- detail page
- wizard/step flow
- modal workflow
- search/browse/listing surface
- creation/editing workflow
- reporting/analytics surface
- custom/unknown

For each reviewed screen, answer:

```text
What is the user goal?
What interaction model is currently implemented?
What interaction model should this be?
Does current model match user goal and product context?
If not, what structural UX risk does the mismatch create?
```

## target-behavior-model.json Schema

```json
{
  "schema_version": 1,
  "review_id": "",
  "scope": "",
  "target_model": "",
  "states": {
    "default": "",
    "edit": "",
    "dirty_unsaved": "",
    "inactive_disabled_read_only": "",
    "destructive_action": "",
    "empty": "",
    "loading": "",
    "error": "",
    "success": "",
    "permission_role_based": "",
    "responsive_mobile": "",
    "accessibility": ""
  },
  "evidence_status": "Confirmed | Suggested | Unknown",
  "evidence_refs": [],
  "open_questions": []
}
```

## Rule

No implementation recommendation is complete until the relevant target states are defined or marked `Unknown`.
