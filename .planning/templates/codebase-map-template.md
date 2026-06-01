# Codebase Map Content Template

Use this project-owned map content when `.planning/CODEBASE_MAP.md` needs the `GSD-PROJECT: codebase-map-content` block created or refreshed.
This template is project-owned content only; it does not include blueprint sync guidance or managed block markers.

Keep observable repo facts, forward-looking interpretations, and unresolved gaps visibly separated as `Confirmed`, `Suggested`, and `Unknown`.

## Mapping Mode
- Mapping state: `no_meaningful_project_structure` | `structure_exists_but_no_mapping` | `partial_mapping_exists` | `mature_mapping_may_be_stale` | `serious_full_mapping_needed` | `transformation_migration_refactor_mapping_requested`
- Confirmed user goal or repo-backed trigger:
- Mapping depth chosen by the unified mapping orchestrator:
- Completed mapping slices:
- Remaining mapping gaps:
- Evidence status:
- Source or rationale:

## Repository Shape And Operational Surfaces
- Repository shape: mono-repo, multi-package, multi-service, modular, hybrid, or other observable structure
- Key directories and their roles:
- Entry points:
- Build, test, lint, and run surfaces:
- Release or deployment-relevant paths:
- Evidence status:
- Source or rationale:

## Technical Foundation
- Languages and language mix:
- Frameworks and runtimes in use:
- Package and dependency management:
- Code generation surfaces:
- Environment and configuration strategy:
- Runtime assumptions:
- Version-sensitive constraints:
- Evidence status:
- Source or rationale:

## Syntax And Conventions In Practice
- Syntax style actually used in practice:
- Naming conventions:
- Code organization conventions:
- Validation patterns:
- Error-handling patterns:
- Dependency usage patterns:
- Test patterns:
- Framework-specific conventions actually present:
- Evidence status:
- Source or rationale:

## Architecture And Dependency Direction
- Architecture style actually present:
- Subsystem or module boundaries:
- Layers and layer responsibilities:
- Dependency direction:
- Cross-layer violations:
- Blurred ownership areas:
- Coupling points:
- Evidence status:
- Source or rationale:

## Agent Working Model
- Primary edit surfaces:
- Primary read-only/reference surfaces:
- Main extension points:
- Canonical implementation examples:
- Canonical extension points:
- Canonical reuse examples:
- Reusable internal APIs/utilities:
- Minimum-new-code constraints:
- Dependency boundaries agents must respect:
- Common wrong edit locations:
- Fragile areas where minimum-code shortcuts are dangerous:
- Generated, vendor, cache, or build-output areas:
- Validation paths agents should prefer:
- Mapping artifacts that must be updated when this area changes:
- Evidence status:
- Source or rationale:

## Runtime And Behavior Flows
- Startup or bootstrap flow:
- Request or response flow:
- Performance-sensitive paths:
- Hot paths:
- Background job flow:
- Event or messaging flow:
- Auth or permission flow:
- Operational or runtime control flow:
- Important user or operator flows observable from repo evidence:
- Evidence status:
- Source or rationale:

## Data, Persistence, And Integration Surfaces
- Persistence shape:
- Entities, tables, documents, and relationships observable from the repo:
- Migrations or backfills:
- External integrations:
- Internal and external API boundaries:
- Jobs, cron, queues, webhooks, or messaging surfaces:
- Expensive database/API/I/O/queue/file/network surfaces:
- Hot-path, request-path, I/O, API, database, file, network, and queue risk notes:
- Provider constraints visible from code, config, or docs:
- Evidence status:
- Source or rationale:

## Quality, Risk, And Transformation Readiness
- Hotspots:
- Fragile areas:
- Legacy areas:
- Hidden dependencies:
- Upgrade blockers:
- Migration-sensitive constraints:
- Minimum-code shortcut risks:
- Subsystem seams useful for future refactor:
- Subsystem seams that currently block safe transformation:
- Evidence status:
- Source or rationale:

## GSD Infrastructure Boundary
- Installed GSD workflow files:
- Application files:
- Boundary notes:
- If this repository is the reusable GSD blueprint itself, state that GSD files are the primary product.

## Suggested Interpretations Or Follow-On Mapping Slices
- Suggested future-facing interpretations or recommended follow-up mapping slices:
- Source or rationale:

## Unknowns Requiring Confirmation
- Contradictory or thin evidence:
- Unknown blockers or hidden dependencies:
- Next choice-shaped questions to present as UI options:

## Context Index Handoff
- Context index status:
- Recommended `$gsd-map-codebase` unified mapping scope:
- Highest-value routing rows to create:
- Highest-value module cards to create:
- Highest-value symbol/API rows to create:
- Highest-value convention cards to create:
- Validation paths to capture:
- Do-not-scan boundaries to capture:
- Exact stale or missing routes to correct:
