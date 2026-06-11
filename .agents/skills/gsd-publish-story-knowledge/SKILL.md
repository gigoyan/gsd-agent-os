---
name: gsd-publish-story-knowledge
description: Publish curated story knowledge to the project Vault namespace through deterministic dry-run-first mirror artifacts while preserving compact source and evidence links without generating stories, running QA, browsing, or writing Vault notes by default.
---

# GSD Publish Story Knowledge

Mirror curated repo-local story knowledge into the project Vault namespace.

This skill owns Vault mirror behavior and deterministic mirror state. It consumes curated `publish-source.md` files; it does not create the story source layer.

## Ownership

This skill owns:

- `.planning/story-knowledge-mirror/**`
- project-owned Vault mirror behavior under `projects/<vault-project-id>/knowledge/**`

Follow these contracts when present:

- `.planning/templates/story-knowledge-mirror-contract.md`
- `.planning/templates/evidence-status-and-reference-contract.md`
- `.planning/templates/evidence-redaction-safety-contract.md`
- `.planning/templates/vault-operating-spec.md`
- `.planning/templates/validation-evidence-contract.md`
- `.planning/templates/performance-first-reuse-contract.md`
- `.planning/templates/source-materials-contract.md`

## Inputs

Use curated story publish sources:

```text
.planning/user-stories/<story-id>/publish-source.md
.planning/user-stories/<story-id>/story.json
.planning/user-stories/<story-id>/source-links.json
.planning/user-stories/<story-id>/story-hashes.json
```

Use compact source traceability only:

- `source_id`
- `claim_id`
- `source_id#anchor`
- evidence status: `Confirmed`, `Suggested`, or `Unknown`

Do not copy raw source-material bodies or duplicate source registry rows.

## Outputs

Maintain deterministic mirror state:

```text
.planning/story-knowledge-mirror/mirror-config.json
.planning/story-knowledge-mirror/mirror-lock.json
.planning/story-knowledge-mirror/mirror-manifest.json
.planning/story-knowledge-mirror/mirror-report.md
.planning/story-knowledge-mirror/mirror-runs/<run-id>/
```

## Workflow

1. Read `PROJECT.md`, `.planning/STATE.md`, the active milestone and phase when present, and the story knowledge mirror contract.
2. Resolve the Vault project namespace from `PROJECT.md`; if it is unset, derive it from the repository root folder name.
3. Load only selected curated story publish sources and compact source/evidence metadata needed for the mirror pass.
4. Default to `dry-run`. Apply writes only after explicit approval or `--apply`.
5. Classify deltas deterministically as `create`, `update`, `unchanged`, `removed`, `conflict`, or `rename`.
6. In dry-run mode, write only repo-local mirror state and reports under `.planning/story-knowledge-mirror/**`.
7. In apply mode, write only approved managed block content inside the project-owned Vault namespace and preserve manual content outside each managed block.
8. Preserve every `Confirmed`, `Suggested`, and `Unknown` status. Do not promote `Suggested`; do not treat `Unknown` as implementation authority.
9. Run a focused mirror validator, such as `python .gsd\check-story-knowledge-mirror-static.py`, before treating mirror outputs as complete.

## Apply, Conflict, And Removal Rules

- apply mode remains non-default. Dry-run remains the default even when apply fixture behavior exists.
- Apply requires explicit approval metadata that records the approval source, approval scope, run ID, target namespace, and whether the write is fixture-only or real Vault apply.
- Fixture apply behavior is repo-local fixture validation only. It may write under `.planning/story-knowledge-mirror/fixtures/vault/projects/<fixture-project-id>/**`; it must not write the real shared Vault or use Obsidian MCP.
- Validation namespaces must be resolved from the target repository `PROJECT.md`; if unavailable, record the fallback without scanning the target repository broadly.
- Managed block writes must use `<!-- GSD-MIRROR:START <source-id> -->` and `<!-- GSD-MIRROR:END <source-id> -->`.
- Apply updates only generated managed block content and must preserve manual content outside managed blocks.
- manual edits inside managed blocks produce deterministic `conflict` output instead of overwriting the page.
- Removed-source handling defaults to tombstone/archive, never hard delete, unless a later explicitly approved cleanup phase says otherwise.

## Rules

- Dry-run is the default.
- `--apply` requires explicit user approval or a phase that explicitly authorizes apply behavior.
- Do not write Vault notes in dry-run mode.
- Do not write durable memory from this skill; later session-save work must be explicit.
- Do not browse by default.
- Do not generate user stories.
- Do not run QA.
- Do not run UI/UX review.
- Do not rediscover Flow Intelligence.
- Do not publish raw operational evidence by default.
- Do not write shared Vault root notes or sibling project namespaces.
- Do not hard-delete Vault pages unless explicitly approved.
- Use the managed block format from the mirror contract for generated Vault sections.
- Keep conflict, removed-source, tombstone, archive, and rename behavior deterministic and visible in reports.

## Do Not Own

- User story generation.
- QA evidence generation.
- UI/UX product review.
- Browser Evidence Runtime implementation or capture.
- Flow Intelligence discovery or refresh.
- Milestone planning, phase planning, execution orchestration, or verification.
- Final cleanup approval or deletion.
- Product code edits.

## Validation

Before completion, confirm:

- `SKILL.md` has valid frontmatter and names owner/non-owner boundaries.
- Mirror config, lock, manifest, and report files exist and parse or render consistently.
- Dry-run is default and reports planned writes without writing Vault notes.
- First dry-run classification records `create` for new curated story sources.
- Repeat dry-run classification records `unchanged` when hashes match the deterministic lock and manifest inputs.
- Vault paths stay under `projects/<vault-project-id>/knowledge/**`.
- Compact source/evidence links preserve `Confirmed`, `Suggested`, and `Unknown`.
- Mirror outputs do not contain raw screenshots, network logs, DOM snapshots, cookies, credentials, browser artifacts, or raw source-material bodies.

## Completion Check

- Outputs are repo-local under `.planning/story-knowledge-mirror/**` unless apply is explicitly approved.
- Mirror content is traceable to curated story publish sources.
- Evidence status distinctions are preserved.
- Redaction and raw-evidence boundaries are respected.
- Performance-sensitive reads and hashes stay bounded to selected story and mirror paths.
- Future apply, conflict, removal, and cleanup work remains visible without being implemented prematurely.
