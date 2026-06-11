# UI Inventory Contract

## Purpose

Define the compact UI inventory produced by `$gsd-ui-discovery-orchestrator` from Browser Evidence Runtime outputs.

## Required Artifact

```text
.planning/ui-discovery/<goal-id>/ui-inventory.json
```

## Schema

```json
{
  "schema_version": 1,
  "goal_id": "",
  "source_browser_runs": [],
  "pages": [],
  "routes": [],
  "navigation_items": [],
  "forms": [],
  "fields": [],
  "buttons": [],
  "links": [],
  "modals": [],
  "drawers": [],
  "tables": [],
  "empty_states": [],
  "error_states": [],
  "permission_states": [],
  "unknown_actions": []
}
```

## Rules

- Use only compact browser evidence references.
- Do not copy raw screenshots, DOM snapshots, cookies, storage values, tokens, network payloads, console logs, or full action logs into UI inventory.
- Preserve evidence status values as `Confirmed`, `Suggested`, or `Unknown`.
