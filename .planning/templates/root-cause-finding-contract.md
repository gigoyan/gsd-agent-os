# Root Cause Finding Contract

## Purpose
Group local UI/UX symptoms under structural causes so reports do not become flat checklists.

## Root-Cause Examples

- wrong interaction model
- always-editable UI where read-first UI is expected
- missing state lifecycle
- weak action hierarchy
- poor information hierarchy
- unsafe destructive-action design
- insufficient identity/context preservation
- inaccessible custom interaction pattern
- unclear ownership between list/detail/edit surfaces
- missing permission/role behavior
- missing feedback/recovery loop
- evidence gap

## root-causes.json Schema

```json
{
  "schema_version": 1,
  "review_id": "",
  "root_causes": [
    {
      "root_cause_id": "RC-0001",
      "title": "",
      "risk_classification": "structural_ux_risk | local_polish | evidence_gap",
      "affected_screens": [],
      "affected_flows": [],
      "affected_roles": [],
      "evidence_status": "Confirmed | Suggested | Unknown",
      "evidence_refs": [],
      "symptom_finding_ids": [],
      "recommendation": "",
      "priority": "Critical | High | Medium | Low",
      "acceptance_criteria": []
    }
  ]
}
```

## Rule

If multiple local symptoms share one root cause, report the root cause first and list symptoms underneath.
