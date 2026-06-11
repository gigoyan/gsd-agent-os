---
name: gsd-ui-discovery-orchestrator
description: Orchestrate full or scoped UI discovery from natural-language requests by composing Browser Evidence Runtime, Flow Intelligence discovery, optional user-story generation, optional QA evidence, coverage reporting, and optional Vault publishing without replacing the lower-level owner skills.
---

# GSD UI Discovery Orchestrator

Use this skill when the user asks for browser-backed UI discovery or natural-language UI capture such as:

- capture all user stories
- go through the whole UI
- explore every page and form
- test the Admin role
- discover all app flows
- document UI flows and bugs
- perform full UI discovery
- create stories from the actual browser UI

## Ownership

This skill owns:

```text
.planning/ui-discovery/**
```

This skill does not own:

```text
.planning/flow-intelligence/**
.planning/user-stories/**
.planning/qa/**
.planning/story-knowledge-mirror/**
.planning/evidence/browser-runs/**
```

Those outputs remain owned by their specialist skills or the Browser Evidence Runtime. This skill orchestrates them and records coverage; it does not replace them.

## Default Output Selection

```json
{
  "browser_evidence": true,
  "flow_intelligence": true,
  "user_stories": false,
  "qa": false,
  "coverage_report": true,
  "vault_publish": false
}
```

Set `user_stories: true` when the user explicitly asks for stories. Set `qa: true` when the user asks for bugs, defects, testing, or QA. Keep `vault_publish: false` unless the user explicitly requests Vault publishing.

## Supported Scope Types

```text
project
role
page
flow
feature
changed-files
manual-source
```

## Workflow

User-facing requests for UI discovery must remain natural language. Translate the request into Browser Evidence Runtime, Flow Intelligence, story, QA, coverage, and validator steps internally. Do not ask the user to run browser-evidence commands, validators, goal IDs, tab-policy flags, or artifact inspections manually unless the agent lacks permission or environment access.

1. Read `PROJECT.md`, `.planning/STATE.md`, and `.planning/CONTEXT_INDEX.md` when present.
2. Resolve the natural-language request into `.planning/ui-discovery/<goal-id>/scope.json` using `.planning/templates/ui-discovery-scope-contract.md`.
3. Create or update `.planning/ui-discovery/<goal-id>/run-manifest.json` and mark every requested output as `planned`, then `running`, then one of `complete`, `partial`, `blocked`, `skipped`, or `not_requested`.
4. Check Browser Evidence prerequisites using the Browser Evidence Runtime setup contract.
5. Ask only for user-only blockers:
   - base URL
   - safe data policy
   - credentials, manual login, or MFA handling
   - target role(s)
   - autonomy mode when safe mode is not sufficient
6. Run Browser Evidence setup or smoke only when prerequisites and data policy are clear.
7. Run browser evidence with a goal-scoped one-primary-tab session:

```text
python .gsd/browser-evidence.py evidence --goal-id <goal-id> --tab-policy reuse-primary ...
```

8. Build `.planning/ui-discovery/<goal-id>/ui-inventory.json` using only compact browser evidence references.
9. Invoke or hand off to `$gsd-discover-flow-evidence` for Flow Intelligence discovery.
10. Invoke or hand off to `$gsd-create-user-stories` only when stories are requested.
11. Invoke or hand off to `$gsd-qa-tester` only when QA is requested.
12. Write `.planning/ui-discovery/<goal-id>/coverage-report.md` and `.planning/ui-discovery/<goal-id>/coverage-report.json`.
13. Invoke or hand off to `$gsd-publish-story-knowledge` only when Vault publishing is explicitly requested.
14. Run:

```text
python .gsd/check-ui-discovery-static.py
```

## Safety And Evidence Rules

- Do not invent credentials.
- Do not decide data-safety policy without user input.
- Do not treat production automation as allowed unless explicitly approved.
- Preserve user-provided scope exactly in `scope.json`.
- Mark unresolved items in `unknowns`.
- Keep browser evidence in `.planning/evidence/browser-runs/**`; reference it with `browser-run://<run-id>/summary.json`.
- Do not copy raw screenshots, DOM snapshots, cookies, storage values, tokens, network payloads, console logs, or full action logs into UI discovery artifacts.
- Preserve evidence status values exactly as `Confirmed`, `Suggested`, or `Unknown`.
- Keep role evidence separated unless the project docs, code evidence, user input, or browser evidence explicitly supports merging.
