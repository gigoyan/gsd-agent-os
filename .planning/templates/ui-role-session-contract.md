# UI Role Session Contract

## Purpose

Track role-specific browser sessions and coverage for `$gsd-ui-discovery-orchestrator`.

## Required Artifact

```text
.planning/ui-discovery/<goal-id>/role-session-matrix.json
```

## Schema

```json
{
  "schema_version": 1,
  "goal_id": "",
  "roles": [
    {
      "role_id": "",
      "auth_strategy": "none | manual_login | provided_secret_channel | existing_session | unknown",
      "session_status": "ready | missing | blocked | expired | unknown",
      "browser_run_refs": [],
      "covered_pages": [],
      "covered_flows": [],
      "permission_findings": [],
      "unknowns": []
    }
  ]
}
```

## Rules

- Role names must come from user input, project docs, code evidence, or browser evidence.
- Do not invent roles.
- Separate evidence per role.
- Do not merge Admin, Manager, and Member evidence unless explicitly supported.
