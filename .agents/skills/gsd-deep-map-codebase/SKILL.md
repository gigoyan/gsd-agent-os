---
name: gsd-deep-map-codebase
description: Produce transformation-ready mapping for an existing repository when the user needs serious modernization, refactor, upgrade, or migration understanding before milestone planning.
---

# GSD Deep Map Codebase

Deep-map an existing repository without drifting into migration design or implementation.
Use this skill when lightweight repo onboarding is no longer enough and the user needs factual, transformation-ready understanding for later milestone planning.

## Workflow
1. Start from the current [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md), the active repo evidence, and [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md). Preserve the same `Confirmed`, `Suggested`, and `Unknown` meanings used by lightweight mapping.
2. Confirm that the request reflects serious deep-mapping intent: modernization, major refactor, version upgrade, platform migration, stack migration, or similar architecture-shaping transformation work.
3. Inspect the repo further only where needed to make the transformation-ready picture concrete: subsystem boundaries, ownership seams, dependency chains, external integrations, operational constraints, upgrade blockers, and migration-sensitive assumptions.
4. Record factual current-state understanding separately from forward-looking interpretations. Keep observable structure and constraints `Confirmed`, keep transformation opportunities or likely milestone slices `Suggested`, and keep unresolved blockers, hidden dependencies, or contradictory evidence `Unknown`.
5. Update [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) so it captures transformation-ready mapping output rather than only onboarding summary material.
6. Produce a serious-mapping handoff inside the codebase map that names the recommended next GSD action, the intended milestone shape, and an exact next-session prompt for later `$gsd-plan-milestone` use.
7. Stop after the mapping and handoff are complete. Do not create milestone or phase files from this skill.

## Required Outputs
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) with:
  - transformation-ready subsystem boundaries
  - dependency seams and integration hotspots
  - modernization blockers and migration-sensitive constraints
  - `Confirmed`, `Suggested`, and `Unknown` kept explicit
  - a serious-mapping handoff that points to `$gsd-plan-milestone`
- A next-session handoff precise enough that later milestone planning can create a large structured mapping milestone without reconstructing the intent from chat history.

## Rules
- Stay factual and transformation-ready. Do not invent target architecture, migration sequencing, or execution tasks that the evidence does not support.
- Preserve lightweight mapping as a different path. This skill is for serious transformation-oriented understanding, not default repo onboarding.
- Keep follow-up questions choice-shaped when the remaining decision space can reasonably be expressed as UI options.
- Preserve repo-vault separation and do not write durable memory from this skill.
- If the repo evidence is too thin to support a claimed transformation concern, mark it `Unknown` instead of promoting a guess.
- Keep recommended milestone boundaries or follow-on mapping slices visibly `Suggested` until the user or stronger evidence confirms them.

## Suggested Serious-Mapping Handoff Shape
- Recommended next GSD action: `$gsd-plan-milestone`
- Suggested milestone shape: `large structured mapping milestone`
- Exact next-session prompt:
  - `Plan a large structured mapping milestone for this repository using .planning/CODEBASE_MAP.md as the governing map. Keep the work transformation-ready and scoped to factual understanding for the confirmed modernization, refactor, upgrade, or migration goal. Do not start implementation or migration design; produce the next bounded mapping phase and verification plan only.`

## Completion Check
- The codebase map distinguishes current-state facts from forward-looking interpretations and unresolved blockers.
- The output is concrete enough to support later modernization, refactor, upgrade, or migration planning without pretending that planning is already done.
- The serious-mapping handoff is explicit, exact, and routes to `$gsd-plan-milestone` rather than to implementation.
