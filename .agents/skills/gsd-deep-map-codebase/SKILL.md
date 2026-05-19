---
name: gsd-deep-map-codebase
description: Produce transformation-ready exhaustive current-state mapping for an existing repository when the user needs serious modernization, refactor, upgrade, or migration understanding before transformation work is orchestrated.
---

# GSD Deep Map Codebase

Deep-map an existing repository exhaustively without drifting into migration design or implementation.
Use this skill when lightweight repo onboarding is no longer enough and the user needs factual, transformation-ready current-state understanding that is strong enough to support later refactoring, modernization, upgrade, migration, or architecture-restructuring planning.

## Workflow
1. Start from the current [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md), [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md), [`.planning/STATE.md`](../../../.planning/STATE.md), the active repo evidence, and [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md). Use the codebase-map, milestone, phase, roadmap, and state templates when they help keep the output aligned. Preserve the same `Confirmed`, `Suggested`, and `Unknown` meanings used by lightweight mapping.
2. Confirm that the request reflects serious deep-mapping intent: modernization, major refactor, version upgrade, platform migration, stack migration, or similar architecture-shaping transformation work.
3. Inspect the repo exhaustively enough to produce full-project current-state understanding rather than a thin onboarding summary. Cover repository shape, package or service structure, entry points, build or test or lint or run surfaces, deployment-relevant paths, technical foundation, syntax and conventions actually used in practice, architecture boundaries, runtime flows, data and integration surfaces, and quality or transformation-readiness constraints. If evidence is thin or contradictory, keep it explicit as `Unknown`.
4. Record factual current-state understanding separately from forward-looking interpretations. Keep observable structure and constraints `Confirmed`, keep milestone-shaping recommendations or future mapping slices `Suggested`, and keep unresolved blockers, hidden dependencies, or contradictory evidence `Unknown`.
5. Update [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) so it captures transformation-ready full-project mapping output rather than only onboarding summary material. When the file contains `GSD-BLUEPRINT: codebase-map-surface-contract` and `GSD-PROJECT: codebase-map-content` markers, update only the `GSD-PROJECT: codebase-map-content` block and preserve the blueprint guidance block exactly. The map must support later safe refactoring, modernization, upgrade, migration planning, and architecture restructuring without pretending those later plans are already done.
6. Refresh `.planning/CONTEXT_INDEX.md` from the exhaustive current-state map so later transformation, refactor, upgrade, migration, planning, execution, and verification agents can route to the smallest relevant modules, files, commands, and validation paths without repeating the deep scan.
7. Automatically create one large structured mapping milestone under [`.planning/milestones/`](../../../.planning/milestones/) and exactly one first bounded mapping phase under [`.planning/phases/`](../../../.planning/phases/). The milestone must stay mapping-focused, transformation-ready, and phase-decomposed. Do not turn it into migration design, target architecture design, or implementation planning. The first phase must stay bounded and execution-ready, but it should still be a current-state mapping slice rather than a build phase.
8. Update [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) so they point to the created mapping milestone and first bounded phase, with milestone status shown as `in_progress`, phase status shown as `planned`, and durable-memory follow-up left repo-local as `none` unless stronger repo-local planning context explicitly justifies `candidate`.
9. Produce a serious-mapping handoff inside the codebase map and in the response that names the created milestone, the created first phase, the recommended next GSD action, and an exact next-session prompt telling the user to run the already-created milestone through `$gsd-run-milestone` rather than executing the phase directly.
10. Stop after the mapping artifacts, milestone and phase artifacts, roadmap and state updates, and orchestration handoff are complete. Do not execute the phase, verify the phase, invent target architecture, or create migration or implementation tasks from this skill.

## Required Outputs
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) with:
  - exhaustive current-state understanding across repository shape, technical foundation, syntax and conventions in practice, architecture, runtime flows, data or integration surfaces, and transformation-readiness risks
  - transformation-ready subsystem boundaries
  - dependency seams, integration hotspots, and coupling points
  - modernization blockers, upgrade blockers, and migration-sensitive constraints
  - `Confirmed`, `Suggested`, and `Unknown` kept explicit
  - a serious-mapping handoff that names the created milestone and points to `$gsd-run-milestone`
  - only the `GSD-PROJECT: codebase-map-content` block updated when markers exist
- [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md) with transformation-ready routing rows, module cards, dependency seams, validation paths, search recipes, and do-not-scan boundaries derived from the deep map.
- One large structured mapping milestone file under [`.planning/milestones/`](../../../.planning/milestones/) that keeps the work mapping-focused, transformation-ready, and phase-decomposed.
- One first bounded mapping phase file under [`.planning/phases/`](../../../.planning/phases/) that is ready for later execution without turning into implementation work.
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) updated to the created mapping milestone and phase.
- A next-session handoff precise enough that the next session can run the already-created mapping milestone through `$gsd-run-milestone` without reconstructing the intent from chat history.

## Rules
- Stay factual and transformation-ready. Do not invent target architecture, migration sequencing, or implementation tasks that the evidence does not support.
- When deep-mapping an application repository with installed GSD, separate application architecture from GSD blueprint/workflow infrastructure. Do not let reusable GSD files distort the application codebase map.
- The goal is exhaustive current-state understanding, not target-state design. Deep mapping must remain strong enough for later safe transformation work without silently becoming the transformation plan.
- Preserve lightweight mapping as a different path. This skill is for serious transformation-oriented understanding, not default repo onboarding.
- Keep follow-up questions choice-shaped when the remaining decision space can reasonably be expressed as UI options.
- Deep mapping must leave behind a compact context index that future agents can use for narrow task routing.
- Do not put exhaustive current-state prose into `CONTEXT_INDEX.md`; keep exhaustive understanding in `CODEBASE_MAP.md` and keep the context index routing-focused.
- If `.planning/CODEBASE_MAP.md` has the blueprint/project marker structure, never rewrite the whole file. Replace only the project-owned `GSD-PROJECT: codebase-map-content` block.
- If markers are missing but project content exists, preserve the file and surface a marker insertion or migration plan instead of overwriting it.
- When the deep map discovers transformation-sensitive seams, record them in the context index as routing guidance, not as migration implementation tasks.
- Preserve repo-vault separation and do not write durable memory from this skill.
- If the repo evidence is too thin to support a claimed transformation concern, mark it `Unknown` instead of promoting a guess.
- Keep recommended milestone boundaries or follow-on mapping slices visibly `Suggested` until the user or stronger evidence confirms them. Creating the mapping milestone does not promote every planning inference inside it to `Confirmed`.
- The orchestration-oriented final handoff is specific to this serious deep-mapping workflow. Do not generalize this `$gsd-run-milestone` response pattern to unrelated mapping, planning, execution, or verification skills.

## Suggested Serious-Mapping Handoff Shape
- Created mapping milestone: `M001-<slug>`
- Created first bounded phase: `M001-P01-<slug>`
- Recommended next GSD action: `$gsd-run-milestone`
- Suggested milestone shape: `large structured mapping milestone`
- Exact next-session prompt:
  - `Run $gsd-run-milestone for the already-created mapping milestone M001-<slug> (<milestone name>) using the current .planning/ROADMAP.md and .planning/STATE.md pointers. Continue orchestration for that milestone and do not execute the active phase directly.`

## Completion Check
- The codebase map distinguishes current-state facts from forward-looking interpretations and unresolved blockers.
- The output is concrete enough to support later modernization, refactor, upgrade, or migration planning without pretending that those later steps are already done.
- A large structured mapping milestone and its first bounded mapping phase were created automatically.
- `.planning/CONTEXT_INDEX.md` was created or refreshed enough that later `$gsd-run-milestone`, planning, execution, verification, and quick-task flows can avoid repeating broad discovery.
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) both point to that created milestone and phase.
- The serious-mapping handoff is explicit, exact, names the created milestone, and routes the next session to `$gsd-run-milestone` rather than to direct phase execution.
