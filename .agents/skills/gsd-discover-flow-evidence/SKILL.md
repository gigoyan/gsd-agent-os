---
name: gsd-discover-flow-evidence
description: Discover and maintain repo-local Flow Intelligence artifacts for static pages, roles, flows, APIs, entities, code references, replay plans, and compact evidence references without creating stories, QA reports, Vault notes, milestones, or browser captures.
---

# GSD Discover Flow Evidence

Own the Flow Intelligence base layer for a repository.

Flow Intelligence is the reusable source artifact for downstream UI/UX review, user story generation, QA testing, Vault publishing, and milestone planning. This skill discovers or validates repo-local flow evidence only. Downstream skills consume Flow Intelligence; they do not define it.

## Ownership

This skill owns:

- `.planning/flow-intelligence/INDEX.md`
- `.planning/flow-intelligence/*.jsonl`
- `.planning/flow-intelligence/flows/<flow-id>/**`
- `.planning/evidence/flow-intelligence/**`

Follow these contracts when present:

- `.planning/templates/flow-intelligence-contract.md`
- `.planning/templates/evidence-status-and-reference-contract.md`
- `.planning/templates/evidence-redaction-safety-contract.md`
- `.planning/templates/browser-evidence-contract.md`
- `.planning/templates/validation-evidence-contract.md`
- `.planning/templates/performance-first-reuse-contract.md`
- `.planning/templates/source-materials-contract.md`

## Inputs

Use the narrowest available evidence:

- repo-local source paths routed by `.planning/CONTEXT_INDEX.md`
- active milestone, phase, and verification artifacts
- registered source-material claims from `.planning/source-materials/SOURCE_MATERIALS.md`
- compact browser evidence references such as `browser-run://<run-id>/summary.json`
- compact repository references such as `repo://<path>#L<start>-L<end>`

When source materials constrain work, cite only compact `source_id`, `claim_id`, anchors, and evidence status. Do not copy raw source bodies or duplicate registry rows.

## Outputs

Maintain the required Flow Intelligence indexes:

```text
.planning/flow-intelligence/INDEX.md
.planning/flow-intelligence/capability-index.jsonl
.planning/flow-intelligence/role-index.jsonl
.planning/flow-intelligence/page-index.jsonl
.planning/flow-intelligence/api-index.jsonl
.planning/flow-intelligence/db-entity-index.jsonl
.planning/flow-intelligence/flow-index.jsonl
.planning/flow-intelligence/traceability-index.jsonl
.planning/flow-intelligence/evidence-index.jsonl
.planning/flow-intelligence/replay-index.jsonl
```

When a flow is emitted, create:

```text
.planning/flow-intelligence/flows/<flow-id>/
  flow.json
  flow.compact.md
  story-source.json
  code-map.json
  replay.plan.json
  qa-hints.json
  evidence-manifest.json
  source-hashes.json
```

Evidence details, validation manifests, blockers, and discovery summaries belong under `.planning/evidence/flow-intelligence/**`.

## Workflow

1. Read `PROJECT.md`, `.planning/STATE.md`, `.planning/CONTEXT_INDEX.md`, the active milestone and phase when present, and the Flow Intelligence contracts.
2. Resolve scope: project, role, page, route, API, entity, feature, or flow.
3. Inspect only routed source paths and directly necessary adjacent files. Avoid broad scans of `node_modules`, build outputs, raw source-material folders, raw evidence folders, vendored code, and external projects unless explicitly scoped.
4. Classify each discovered item with an evidence status:
   - `Confirmed`: directly supported by code, contract, browser evidence, test, source material, documentation, or explicit user input.
   - `Suggested`: reasoned inference from partial evidence.
   - `Unknown`: missing, stale, contradictory, inaccessible, or unverified evidence.
5. Write compact indexes first, then per-flow files only when evidence supports a concrete flow.
6. Preserve evidence references as compact strings or objects. Use `browser-run://<run-id>/summary.json` references for browser-backed evidence and keep screenshots, DOM snapshots, network payloads, cookies, storage values, console logs, and raw action logs out of Flow Intelligence bodies.
7. Apply redaction before writing evidence manifests. Replace secrets with `[REDACTED_SECRET]` and record safety events in `.planning/evidence/flow-intelligence/**` when relevant.
8. Run the focused static validation path, such as `python .gsd\check-flow-intelligence-static.py`, before treating outputs as usable by downstream skills.

## Static Discovery Rules

- Never invent paths, symbols, roles, APIs, routes, pages, entities, or user-visible behavior.
- Empty indexes are valid when no supported item exists yet.
- Keep unsupported downstream recommendations as `Suggested` or `Unknown`.
- A `Suggested` source-backed claim is not a confirmed implementation requirement.
- An `Unknown` claim may identify a gap but must not authorize implementation.
- Keep source traceability compact using `source_id`, `claim_id`, anchor, and evidence status.

## Browser Reference Handoff

Browser-backed discovery is a later integration layer. In this skill, browser evidence may be represented only as compact references. Prefer summary references for Flow Intelligence records:

```json
{
  "ref": "browser-run://<run-id>/summary.json",
  "kind": "browser-summary",
  "evidence_status": "Suggested",
  "notes": "Reference only; raw evidence remains under .planning/evidence/browser-runs/."
}
```

Every browser reference object must preserve one of `Confirmed`, `Suggested`, or `Unknown`. A blocked or partial Browser Evidence Runtime summary is a valid compact reference target, but it must not be promoted to `Confirmed` unless the summary directly supports the Flow Intelligence claim.

Do not start a browser, invoke Browser Evidence Runtime, replay a run, copy screenshots, copy DOM snapshots, copy network logs, copy cookies or storage values, copy console logs, copy full action logs, or inline raw browser artifacts unless a later phase explicitly assigns browser-backed discovery.

## Do Not Use As Owner For

- User story generation.
- QA testing or QA report generation.
- Vault publishing or durable memory writes.
- milestone planning or phase planning.
- Browser Evidence Runtime implementation.
- UI/UX product review ownership.
- Product code edits.
- Runtime adapter generation.

## Validation

Before completion, confirm:

- `SKILL.md` has valid frontmatter and names ownership boundaries.
- Required Flow Intelligence indexes exist and each non-empty JSONL line parses as an object.
- Per-flow files exist when a flow directory exists.
- Every `evidence_status` is exactly `Confirmed`, `Suggested`, or `Unknown`.
- Browser evidence appears only as compact `browser-run://<run-id>/summary.json` references.
- No raw source-material bodies, screenshots, DOM snapshots, full logs, secrets, cookies, tokens, or storage values were copied into Flow Intelligence artifacts.
- No stories, QA reports, Vault notes, milestones, or product code were created by this skill.

## Completion Check

- Outputs are repo-local under `.planning/flow-intelligence/**` and `.planning/evidence/flow-intelligence/**`.
- Source/evidence status distinctions are preserved.
- Redaction and safety boundaries are documented for any evidence artifact.
- Performance-sensitive scan and artifact-write risks are bounded.
- Remaining `Suggested` and `Unknown` decisions are listed for later phases.
