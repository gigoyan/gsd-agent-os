# Browser Evidence Install Guide

## Purpose
Make the first browser-evidence goal complete in a new GSD project by separating user-only prerequisites from agent-runnable setup automation.

Browser Evidence commands are agent-runnable internal steps. Users normally provide prerequisites and natural-language goals; the agent runs setup, smoke, evidence, replay, QA, and validator commands when the environment allows it.

Browser Harness itself is an external pinned engine, not vendored source in each project. GSD installs or reuses it from a user-level cache using `.gsd/browser-harness.lock.json` and `.gsd/ensure-browser-harness.py`. The cache location can be overridden with `GSD_BROWSER_HARNESS_CACHE`.

## User-Only Prerequisites
- Install Google Chrome, or provide the Chrome executable path to the agent.
- Approve OS, firewall, antivirus, browser, or extension prompts that block Chrome or local CDP.
- Provide the target app base URL.
- Confirm whether automation may run against local, staging, or real data.
- Provide credentials through the project's approved secret channel, or complete login/MFA manually when required.
- Close or separate personal Chrome sessions if they conflict with the dedicated debugging port or profile.
- The agent uses a dedicated Chrome profile and one primary browser tab by default. Extra tabs may be opened only when the app workflow critically requires it, such as OAuth/SSO popup, external provider popup, payment/provider popup, side-by-side comparison, app-triggered new tab behavior, or preserving unsaved state.

## Agent-Runnable Setup Examples

```text
python .gsd/browser-evidence.py setup-check --base-url <target-url>
python .gsd/browser-evidence.py ensure-browser-harness
python .gsd/browser-evidence.py launch-chrome
python .gsd/browser-evidence.py wait-cdp --cdp-url http://127.0.0.1:9222/json/version
python .gsd/browser-evidence.py wait-app --base-url <target-url>
python .gsd/browser-evidence.py smoke --launch-browser --base-url <target-url> --allow-browser-harness --tab-policy reuse-primary
```

## First-Goal Rule
- At the beginning of the first browser-evidence goal, ask the user for the target URL, safe data policy, and any required manual login/credential handling.
- The agent may run setup checks, install or reuse Browser Harness in the user cache, launch a dedicated Chrome profile, wait for CDP, wait for the app, and run smoke evidence.
- The agent must not install Chrome, approve OS/security prompts, invent credentials, bypass MFA, or decide data-safety policy.
- The agent must reuse the goal's primary tab unless a supported critical new-tab reason is supplied.

## Completion Criteria
- `setup-check` reports all user-only blockers explicitly.
- `ensure-browser-harness` reports Browser Harness available from PATH or the GSD user cache without mutating the project repository.
- `wait-cdp` exits `0`.
- `wait-app` exits `0` for the user-provided target URL.
- `smoke --launch-browser --allow-browser-harness` creates a browser run and exits `0` for the agreed target.
- If any user-only blocker remains, the run is recorded as blocked or skipped honestly rather than marked `Confirmed`.
