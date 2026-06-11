# Source Materials Registry

Generated from `.planning/templates/source-materials-registry-template.md`.
Use this project-owned registry at `.planning/source-materials/SOURCE_MATERIALS.md`.
Do not treat the runtime registry as blueprint-owned.

## Registry Metadata
- Schema version: 1
- Project:
- Registry owner:
- Created:
- Last updated:
- Generated from template: `.planning/templates/source-materials-registry-template.md`
- Governing contract: `.planning/templates/source-materials-contract.md`

## Custody Rules
- Repository storage root: `.planning/source-materials/`
- Copied materials root: `.planning/source-materials/materials/`
- Extracts root: `.planning/source-materials/extracts/`
- Vault namespace, if used: `projects/<vault-project-id>/`
- Non-copy constraints:
  - Do not copy secrets, credentials, private personal data, licensed content, or large binaries into the repo.
  - Direct user input must be repository-relative file or directory paths. Register external references only when they are discovered inside repository files.

## Source Materials
Allowed `classification`: `product_brief` | `requirements_input` | `technical_input` | `design_input` | `workflow_input` | `repo_evidence` | `decision_record` | `external_reference` | `research_note` | `unknown`

Allowed `evidence_status`: `Confirmed` | `Suggested` | `Unknown`

Allowed `custody`: `registered-in-place` | `copied` | `moved` | `external-reference` | `missing`

| source_id | title | classification | scope | governs | evidence_status | location | custody | date_or_version | owner_or_origin | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<source-id>` |  | `unknown` | `project` | `none` | `Unknown` |  | `missing` |  |  |  |

## Claim Index
Keep claims compact. Cite registered source IDs and repository-local anchors instead of copying long source text.

| claim_id | claim | source_refs | evidence_status | applies_to | consumed_by | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `<claim-id>` |  | `<source-id>#<anchor>` | `Unknown` |  |  |  |

## Conflicts And Unknowns
Record unresolved contradictions, missing materials, stale references, and follow-up questions.

| item_id | type | description | affected_scope | source_refs | status | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| `<unknown-id>` | `missing-material` |  |  |  | `Unknown` |  |

## Downstream Consumption Log
Record when a GSD artifact or workflow step consumes a source material or claim.

| consumed_at | consumer | source_refs | claims_used | consumption_rule | result | follow_up |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Registry Maintenance Notes
- Register material in place before copying or moving it whenever the original location is stable enough.
- Preserve provenance before copying or moving user-supplied files.
- Keep `Suggested` and `Unknown` visible in downstream artifacts; never silently promote them to `Confirmed`.
- Update the consumption log when Project Idea Documents, Technical Specifications, stack-selection artifacts, milestones, phases, verification artifacts, codebase maps, or exports use registered material.
