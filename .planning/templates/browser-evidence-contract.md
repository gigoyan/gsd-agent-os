# Browser Evidence Contract

## Purpose
Define deterministic browser evidence output for GSD.

## Output Root

```text
.planning/evidence/browser-runs/<run-id>/
```

## Required Files

```text
summary.json
environment.json
action-log.json
network.json
console.log
storage-summary.json
autonomy-policy.json
safety-events.json
app-process.log
screenshots/
page-states/
dom-snapshots/
```

## Run ID Format

```text
YYYYMMDD-HHMMSS-<scope-slug>-<role-slug>
```

## summary.json Schema

```json
{
  "schemaVersion": 1,
  "runId": "",
  "mode": "evidence | replay | qa | smoke | interactive",
  "status": "passed | failed | partial | blocked",
  "exitCode": 0,
  "projectName": "",
  "baseUrl": "",
  "scope": {
    "type": "project | page | flow | role | feature | replay-plan | manual",
    "value": ""
  },
  "role": "",
  "autonomy": {
    "mode": "safe | custom | unrestricted",
    "blockedActionCategories": [],
    "unrestricted": false
  },
  "browser": {
    "name": "",
    "version": "",
    "cdpUrl": "",
    "profileMode": "dedicated | existing | remote | manual"
  },
  "tabLifecycle": {
    "goalId": "",
    "tabPolicy": "reuse-primary | allow-new-tab | force-new-tab",
    "reusePolicy": "single-primary-tab",
    "primaryTargetId": "",
    "primaryTabUrlBefore": "",
    "primaryTabUrlAfter": "",
    "openedNewTabs": [],
    "closedExtraTabs": [],
    "preservedTabs": [],
    "newTabReasons": [],
    "blockedNewTabAttempts": [],
    "tabDecisionEvidenceStatus": "Confirmed | Suggested | Unknown"
  },
  "app": {
    "commandsRun": [],
    "healthChecks": [],
    "ownedProcessesStopped": true
  },
  "artifacts": {
    "actionLog": "action-log.json",
    "network": "network.json",
    "console": "console.log",
    "screenshots": [],
    "pageStates": [],
    "domSnapshots": []
  },
  "safety": {
    "blockedActions": [],
    "dangerousActionsAllowed": []
  },
  "failure": null,
  "timings": {
    "startedAt": "",
    "finishedAt": "",
    "durationMs": 0
  }
}
```

## action-log.json Entry Schema

```json
{
  "stepId": "BR-S001",
  "timestamp": "",
  "intent": "",
  "action": "navigate | click | fill | select | keypress | wait | assertion | manual",
  "target": "",
  "urlBefore": "",
  "urlAfter": "",
  "screenshotBefore": "",
  "screenshotAfter": "",
  "pageStateBefore": "",
  "pageStateAfter": "",
  "networkRefs": [],
  "consoleRefs": [],
  "status": "passed | failed | blocked | partial",
  "tabDecision": {
    "usedPrimaryTab": true,
    "openedNewTab": false,
    "newTabReason": "",
    "closedRunOwnedTabs": [],
    "evidence_status": "Confirmed"
  },
  "evidence_status": "Confirmed"
}
```

## Goal-Scoped Browser Session And Tab Reuse

Browser Evidence Runtime uses one primary tab per goal by default.

Default tab policy:

`reuse-primary`

New browser tabs are forbidden unless explicitly justified by a critical reason.

Allowed critical reasons:

- OAuth/SSO popup
- external provider popup
- payment/provider popup
- side-by-side live comparison
- app behavior explicitly opens a new tab
- preserving unsaved state while checking another route
- explicit user request

Every browser run must record:

- goal ID
- tab policy
- primary target ID
- primary tab URL before/after
- opened new tabs
- closed extra tabs
- preserved tabs
- new-tab reasons
- blocked new-tab attempts
- tab decision evidence status

Runs must close only tabs opened by the current run unless marked primary or preserved.
Runs must never close unknown/user-owned tabs.

## Rules

- Replay writes a new run. Never overwrite old evidence.
- Screenshots should be after meaningful actions and failures.
- DOM snapshots default to failure-only or debug mode.
- Network and console logs must be redacted.
- Supported command surface is `evidence`, `replay`, `qa`, `smoke`, `doctor`, `setup-check`, `ensure-browser-harness`, `launch-chrome`, `wait-cdp`, and `wait-app`. Browser modes accept `--goal-id`, `--tab-policy reuse-primary|allow-new-tab|force-new-tab`, and `--new-tab-reason <reason>`. The stable GSD command surface is `python .gsd/browser-evidence.py <command>`; native `browser-harness evidence/replay/qa/smoke` subcommands are NOT required. The wrapper resolves Browser Harness from PATH, then the GSD user cache installed from `.gsd/browser-harness.lock.json`, then optional configured vendor fallback. Browser Harness source is not copied into target repositories. The wrapper drives the Browser Harness engine through its interactive/heredoc execution surface, which remains the engine's own behavior; the GSD modes are additive to it, not a replacement.
- First browser-evidence goal setup must use `.planning/templates/browser-evidence-install-guide.md`: user-only prerequisites are gathered first, then agent-runnable setup commands complete Chrome/CDP/app readiness and smoke evidence when safe prerequisites are present.
- Autonomy modes are `safe`, `custom`, and `unrestricted`.
- Redaction remains active in `unrestricted` mode.
- Exit codes are deterministic:
  - `0` passed.
  - `1` expected behavior or assertion failure.
  - `2` config or setup error.
  - `3` browser or CDP failure.
  - `4` app or server health failure.
  - `5` action blocked by autonomy policy.
  - `6` scenario or replay contract error.
  - `7` evidence write or redaction failure.
  - `8` partial run with unresolved blockers.
- Partial or scaffolded runtime runs must not mark browser behavior as `Confirmed` unless the captured evidence directly supports the claim.
