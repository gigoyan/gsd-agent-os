# UI Discovery Scope Contract

## Purpose

Define the scope capsule produced by `$gsd-ui-discovery-orchestrator` before browser-backed UI discovery begins.

## Required Artifact

```text
.planning/ui-discovery/<goal-id>/scope.json
```

## Schema

```json
{
  "schema_version": 1,
  "goal_id": "",
  "request": "",
  "scope": {
    "type": "project | role | page | flow | feature | changed-files | manual-source",
    "value": ""
  },
  "roles": [],
  "base_url": "",
  "environment": "local | staging | production | unknown",
  "auth": {
    "strategy": "none | manual_login | provided_secret_channel | existing_session | unknown",
    "mfa_required": "yes | no | unknown"
  },
  "autonomy": {
    "mode": "safe | custom | unrestricted",
    "policy_file": ""
  },
  "outputs_requested": {
    "browser_evidence": true,
    "flow_intelligence": true,
    "user_stories": false,
    "qa": false,
    "coverage_report": true,
    "vault_publish": false
  },
  "blocked_actions_policy": "",
  "coverage_target": "smoke | normal | deep",
  "unknowns": []
}
```

## Rules

- Do not invent credentials.
- Do not decide data-safety policy without user input.
- Do not treat production automation as allowed unless explicitly approved.
- Preserve user-provided scope exactly.
- Mark unresolved items as `unknowns`.
- Vault publishing must remain false unless the user explicitly requests it.
