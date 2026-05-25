# Intake Routing And Evidence Contract

This reference defines the shared intake and routing semantics for the reusable GSD blueprint.
Use it to keep later skills, templates, and verification behavior aligned without overloading `AGENTS.md`.

## Intake Route Classification
- `placeholder_bootstrap`: use when the repo is new, effectively empty, or still on placeholder planning surfaces. Route to `$gsd-new-project`.
- `document_first_intake`: use when the user supplies substantial docs, notes, or files that can answer bootstrap or Spec-First questions. Extract from those materials before re-asking.
- `existing_project_mapping`: use when the repo already contains meaningful code and the need is factual onboarding, stale mapping repair, serious full mapping, transformation-oriented mapping, or context-index routing refresh. Route to the unified `$gsd-map-codebase` mapping orchestrator.
- `explicit_stack_selection`: use when the user explicitly asks to choose or confirm the stack. Route to `$gsd-select-stack` using repo evidence first.
- `partial_maturity_continuation`: use when some project artifacts already exist but are incomplete, stale, or unevenly mature. Continue from the highest valid readiness point instead of restarting earlier steps.

## Evidence Statuses
- `Confirmed`: backed by direct repo evidence, supplied materials, or an explicit user decision. Treat as factual input.
- `Suggested`: a recommendation, inference, or prefill derived from evidence. Keep it visible as a suggestion until the user confirms it or stronger evidence proves it.
- `Unknown`: still unresolved, missing, or conflicting. Keep it open, record the gap explicitly, and ask a focused follow-up only when it materially blocks progress.

## Interaction Contract
- Use UI options as the default user interaction model whenever the needed input can reasonably be expressed as structured choices, recommended combinations, confirmations, or curated next-step routes.
- Use free-text only when the required input cannot be reasonably reduced to options without losing important meaning.
- Never silently promote `Suggested` values to `Confirmed`.

## Unified Mapping Depth
- Treat requests as serious full mapping or transformation/migration/refactor mapping when the user needs transformation-ready understanding for modernization, major refactor, version upgrade, platform migration, stack migration, or similar architecture-shaping work.
- Do not collapse serious mapping intent into a shallow repo summary.
- Preserve the mapping depth explicitly so the unified `$gsd-map-codebase` orchestrator can choose enough bounded factual slices.
- Mapping must remain current-state understanding. It must not create milestones or phases for mapping, roadmap pointers, `$gsd-run-milestone` handoffs, migration design, target architecture design, or implementation plans.

## Cleanup Permission Gate
- Temporary blueprint-improvement milestone, phase, verification, roadmap-pointer, and state-detail scaffolding must remain in place until final verification passes and the user explicitly approves cleanup.
- After final verification passes, stop and ask the user whether cleanup should run.
- Do not silently delete temporary scaffolding and do not silently keep it as if the cleanup decision did not exist.
