---
name: gsd-create-user-stories
description: Generate deterministic repo-local user story artifacts from existing Flow Intelligence while preserving compact source and evidence links without browsing, rediscovering flows, publishing Vault notes, or creating QA evidence.
---

# GSD Create User Stories

Generate user stories from the Flow Intelligence base layer.

This skill owns curated story outputs. It consumes Flow Intelligence; it does not discover flows, validate product UX, run QA sessions, publish durable Vault memory, or plan milestones.

## Ownership

This skill owns:

- `.planning/user-stories/**`

Follow these contracts when present:

- `.planning/templates/user-story-generation-contract.md`
- `.planning/templates/flow-intelligence-contract.md`
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

Use compact source traceability only:

- `source_id`
- `claim_id`
- `source_id#anchor`
- evidence status: `Confirmed`, `Suggested`, or `Unknown`

Do not copy raw source-material bodies or duplicate source registry rows.

## Outputs

For each story, create:

```text
.planning/user-stories/<story-id>/
  story.md
  story.json
  acceptance-criteria.md
  gherkin.feature
  source-links.json
  publish-source.md
  story-hashes.json
```

`publish-source.md` is curated for later Vault mirroring. This skill must not publish it.

## Workflow

1. Read `PROJECT.md`, `.planning/STATE.md`, the active milestone and phase when present, and the user-story generation contract.
2. Read `.planning/CONTEXT_INDEX.md` and use the narrowest routed Flow Intelligence paths.
3. Load only the selected flow directories and compact evidence manifests needed for the requested stories.
4. Preserve every `Confirmed`, `Suggested`, and `Unknown` status. Do not promote `Suggested` to `Confirmed`; do not treat `Unknown` as implementation authority.
5. Generate deterministic story files under `.planning/user-stories/**`.
6. Keep browser evidence as compact references such as `browser-run://<run-id>/summary.json`.
7. Run the focused story validator, such as `python .gsd\check-user-stories-static.py`, before treating story outputs as complete.

## Rules

- Do not browse by default.
- Do not redo discovery unless Flow Intelligence is missing, stale, or the user explicitly requests refresh.
- Do not start Browser Evidence Runtime or replay browser runs.
- Do not copy screenshots, DOM snapshots, full action logs, network payloads, cookies, storage values, console logs, secrets, or raw source-material bodies into story outputs.
- Do not generate QA reports, defect candidates, QA sessions, or coverage evidence.
- Do not write Vault notes or durable memory.
- Do not create milestones, phases, roadmap entries, or verification artifacts.
- Keep `publish-source.md` safe for later mirroring, but leave publishing to `gsd-publish-story-knowledge`.

## Do Not Own

- Flow Intelligence discovery or refresh.
- QA evidence generation.
- UI/UX product review.
- Browser Evidence Runtime implementation or capture.
- Vault publishing.
- Milestone planning, phase planning, execution orchestration, or verification.
- Product code edits.

## Validation

Before completion, confirm:

- `SKILL.md` has valid frontmatter and names owner/non-owner boundaries.
- Required story files exist for every generated story.
- `story.json`, `source-links.json`, and `story-hashes.json` parse as JSON.
- `story.json` uses schema version 1, a stable `story_id`, source flow IDs, allowed `format_profile`, allowed `status`, required sections, and deterministic hashes.
- Compact source/evidence links preserve `Confirmed`, `Suggested`, and `Unknown`.
- Story outputs do not contain raw browser evidence, raw source-material bodies, secrets, cookies, tokens, screenshots, DOM snapshots, network payloads, console logs, or full action logs.

## Completion Check

- Outputs are repo-local under `.planning/user-stories/**`.
- Story content is traceable to existing Flow Intelligence.
- Evidence status distinctions are preserved.
- Redaction and raw-evidence boundaries are respected.
- Performance-sensitive file reads and hash calculations are bounded to selected flow and story directories.
- Remaining `Suggested` and `Unknown` items are visible in story artifacts for later phases.
