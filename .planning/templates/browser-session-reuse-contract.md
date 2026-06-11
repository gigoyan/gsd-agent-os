# Browser Session Reuse Contract

## Purpose

Browser Evidence Runtime uses one primary browser tab per goal by default. Opening a new tab requires an explicit critical reason. Every run must record tab reuse, open, and close decisions.

## Required Session State File

```text
.planning/tmp/browser-harness/sessions/<goal-id>.json
```

## Schema

```json
{
  "schema_version": 1,
  "goalId": "",
  "cdpUrl": "http://127.0.0.1:9222/json/version",
  "primaryTargetId": "",
  "primaryTabUrl": "",
  "profileDir": "",
  "reusePolicy": "single-primary-tab",
  "createdAt": "",
  "updatedAt": "",
  "ownedTabs": [],
  "preservedTabs": []
}
```

## Default Browser Tab Policy

```text
reuse-primary
```

## Supported Tab Policies

```text
reuse-primary
allow-new-tab
force-new-tab
```

## Policy Meanings

`reuse-primary`: Reuse the goal's primary tab. Do not open a new tab unless a critical new-tab reason is supplied and allowed.

`allow-new-tab`: Prefer primary tab reuse, but allow a new tab when a critical reason is supplied.

`force-new-tab`: Open a new tab only when explicitly requested with a critical reason. This is exceptional and must be recorded.

## Allowed Critical New-Tab Reasons

```text
oauth_sso_popup
external_provider_popup
payment_provider_popup
side_by_side_comparison
app_opened_new_tab
preserve_unsaved_state
manual_user_requested
```

Free-text `--new-tab-reason` may be accepted, but the wrapper must map it to one of the allowed categories or reject or block it.

## Rules

- New tab is forbidden by default.
- New tab without reason must be rejected or downgraded to blocked with a deterministic exit code.
- Browser runs must not close user-owned or unknown tabs.
- Browser runs may close only tabs opened by the current run unless a tab is marked as primary or explicitly preserved.
- The primary tab must be activated and reused for normal navigation, smoke, evidence, replay, and QA.
- The adapter must prefer `ensure_real_tab()`, `current_tab()`, `list_tabs()`, and `goto_url(...)` over `new_tab(...)`.
- `new_tab(...)` may be called only behind the explicit new-tab gate.
