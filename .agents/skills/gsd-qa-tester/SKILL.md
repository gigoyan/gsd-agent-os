---
name: gsd-qa-tester
description: Generate repo-local QA charters, test cases, reports, defect candidates, and coverage evidence from existing Flow Intelligence and compact evidence references without browsing, rediscovering flows, publishing Vault notes, or requiring user stories.
---

# GSD QA Tester

Generate QA evidence from the Flow Intelligence base layer.

This skill owns curated QA outputs. It consumes Flow Intelligence, compact Browser Evidence Runtime summaries, and user stories when available; it does not discover flows, redesign UX, publish durable Vault memory, or plan milestones.

## Ownership

This skill owns:

- `.planning/qa/**`

Follow these contracts when present:

- `.planning/templates/qa-evidence-contract.md`
- `.planning/templates/flow-intelligence-contract.md`
- `.planning/templates/user-story-generation-contract.md`
- `.planning/templates/evidence-status-and-reference-contract.md`
- `.planning/templates/evidence-redaction-safety-contract.md`
- `.planning/templates/browser-evidence-contract.md`
- `.planning/templates/validation-evidence-contract.md`
- `.planning/templates/performance-first-reuse-contract.md`
- `.planning/templates/source-materials-contract.md`

## Inputs

Use existing Flow Intelligence as the source layer:

```text
.planning/flow-intelligence/**
.planning/evidence/flow-intelligence/**
```

Use Browser Evidence Runtime summaries as compact references when useful:

```text
browser-run://<run-id>/summary.json
```

User stories are optional supporting context. QA must be able to run without user stories.

Use compact source traceability only:

- `source_id`
- `claim_id`
- `source_id#anchor`
- evidence status: `Confirmed`, `Suggested`, or `Unknown`

Do not copy raw source-material bodies or duplicate source registry rows.

## Outputs

For each QA session, create:

```text
.planning/qa/sessions/<qa-session-id>/
  test-charter.md
  test-cases.md
  qa-report.md
  qa-report.json
  defects.md
  evidence-manifest.json
```

## Workflow

1. Read `PROJECT.md`, `.planning/STATE.md`, the active milestone and phase when present, and the QA evidence contract.
2. Read `.planning/CONTEXT_INDEX.md` and use the narrowest routed Flow Intelligence, QA, and optional story paths.
3. Load only the selected flow directories, compact evidence manifests, and optional story summaries needed for the requested QA session.
4. Preserve every `Confirmed`, `Suggested`, and `Unknown` status. Do not promote `Suggested` to `Confirmed`; do not treat `Unknown` as implementation authority.
5. Generate deterministic QA files under `.planning/qa/**`.
6. Keep browser evidence as compact references such as `browser-run://<run-id>/summary.json`.
7. Record defect candidates only when evidence supports them. If evidence is incomplete, keep the status as `candidate`, `needs_triage`, `Suggested`, or `Unknown`.
8. Run the focused QA validator, such as `python .gsd\check-qa-evidence-static.py`, before treating QA outputs as complete.

## Rules

- Do not browse by default.
- Do not redo discovery unless Flow Intelligence is missing, stale, or the user explicitly requests refresh.
- Do not start Browser Evidence Runtime or replay browser runs by default.
- Do not copy screenshots, DOM snapshots, full browser operation histories, network payloads, cookies, storage values, console logs, secrets, or raw source-material bodies into QA outputs.
- Do not require user stories; consume them only as optional supporting context.
- Do not generate user stories or story mirror files.
- Do not write Vault notes or durable memory.
- Do not create milestones, phases, roadmap entries, or verification artifacts.
- Do not own broad UX redesign. UX-verification mode must be explicit and still preserve compact evidence references.

## Do Not Own

- Flow Intelligence discovery or refresh.
- User story generation.
- UI/UX product redesign.
- Browser Evidence Runtime implementation or capture.
- Vault publishing.
- Milestone planning, phase planning, execution orchestration, or verification.
- Product code edits.

## Validation

Before completion, confirm:

- `SKILL.md` has valid frontmatter and names owner/non-owner boundaries.
- Required QA session files exist for every generated QA session.
- `qa-report.json` and `evidence-manifest.json` parse as JSON.
- The QA session uses schema version 1, a stable `qa_session_id`, source flow IDs, compact evidence references, optional story references, and `requires_user_stories: false`.
- Defect candidate entries, if present, follow the QA evidence contract fields.
- Compact source/evidence links preserve `Confirmed`, `Suggested`, and `Unknown`.
- QA outputs do not contain raw browser evidence, raw source-material bodies, secrets, cookies, tokens, screenshots, DOM snapshots, network payloads, console logs, or full browser operation histories.

## Completion Check

- Outputs are repo-local under `.planning/qa/**`.
- QA content is traceable to existing Flow Intelligence.
- User story context remains optional.
- Evidence status distinctions are preserved.
- Redaction and raw-evidence boundaries are respected.
- Performance-sensitive file reads are bounded to selected flow, story, and QA session directories.
- Remaining `Suggested` and `Unknown` items are visible in QA artifacts for later phases.
