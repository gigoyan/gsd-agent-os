# Technical Specification Template

Use this template for the current project's Technical Specification.
Do not use it to replace the bootstrap requirements in `.planning/REQUIREMENTS.md`.
When intake is document-first or continuing from partial maturity, refresh this artifact from supplied material before asking questions that the material already answers.

## Document Purpose
- Translate the approved Project Idea Document into implementation-ready behavior and system detail.
- Keep scope, interfaces, and operational expectations explicit enough for milestone planning and execution.

## Specification Snapshot
- Spec title:
- Related Project Idea Document:
- Owner:
- Status:
- Last updated:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Scope And Traceability
- Problem being solved:
- In-scope capabilities:
- Explicit out-of-scope capabilities:
- Traceability back to Project Idea Document goals:
- Milestones or releases covered by this spec:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## User Stories And Primary Flows
- User story or operator workflow:
- Primary happy-path flows:
- Alternative flows:
- Failure or recovery flows:
- Preconditions and postconditions:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Architecture And Module Breakdown
- System context:
- Module or subsystem list:
- Responsibility of each module:
- Cross-module dependencies:
- Areas requiring future decomposition:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Stack Selection Inputs
- Known stack or runtime constraints:
- Open stack-sensitive decisions:
- Decisions intentionally deferred to stack selection:
- Notes that must be updated after stack selection:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Data Model And State
- Core entities or records:
- Important fields and relationships:
- Persistence strategy:
- Data lifecycle, retention, or deletion rules:
- Migration or backfill considerations:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Interfaces And Integrations
- API endpoints, commands, events, or contracts:
- Input and output schemas:
- External integrations and failure handling:
- Authentication, authorization, or permissions model:
- Rate limits, quotas, or usage constraints:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Client Surfaces
- Screens, views, pages, or operator surfaces:
- Component responsibilities:
- Navigation or workflow transitions:
- Validation and error states:
- Accessibility or localization considerations:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Business Logic And Rules
- Core business rules:
- Validation rules:
- Permission rules:
- Derived calculations or decision logic:
- Feature flags or rollout guards:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Operational Concerns
- Observability requirements:
- Logging, metrics, and alerting expectations:
- Performance or capacity expectations:
- Reliability, backup, or recovery needs:
- Security, privacy, and compliance requirements:
- Evidence notes:
  - Confirmed:
  - Suggested:
  - Unknown:

## Edge Cases And Test Focus
- Known edge cases:
- Abuse, misuse, or invalid-input cases:
- Compatibility considerations:
- Suggested verification slices:
- Open technical questions:
- Residual questions that can use UI options:

## Delivery Notes
- Implementation sequencing notes:
- Dependencies or blockers:
- Decisions deferred until stack selection or project-local configuration generation:
- Handoff notes for milestone planning:
