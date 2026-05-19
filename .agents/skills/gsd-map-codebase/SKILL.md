---
name: gsd-map-codebase
description: Onboard an existing repository into the Codex-native GSD workflow by inspecting the actual codebase and producing a grounded architecture map and initial planning state. Use when a repo already contains code but lacks a trustworthy CODEBASE_MAP.md or workflow artifacts.
---

# GSD Map Codebase

Create a factual repository map before milestone planning starts.
Use this skill to inspect structure, commands, dependencies, conventions, and hotspots without inventing unsupported architecture claims.

## Workflow
1. Classify the intake using [`.planning/templates/intake-routing-and-evidence-contract.md`](../../../.planning/templates/intake-routing-and-evidence-contract.md). Use this skill for `existing_project_mapping` and for `partial_maturity_continuation` cases that need factual repo grounding.
2. Inspect the repository layout, entrypoints, manifests, scripts, major modules, and test setup.
3. Identify build, test, lint, and run commands from repo evidence.
4. Summarize the actual architecture, conventions, and risk areas in [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md). When the file contains `GSD-BLUEPRINT: codebase-map-surface-contract` and `GSD-PROJECT: codebase-map-content` markers, update only the `GSD-PROJECT: codebase-map-content` block and preserve the blueprint guidance block exactly.
5. Create or refresh `.planning/CONTEXT_INDEX.md` through `gsd-refresh-context-index` when the mapping pass has enough repo evidence to produce useful task-routing guidance. If the index cannot be completed, record it as `partial` and identify the missing routing areas.
6. Track mapping conclusions as `Confirmed`, `Suggested`, or `Unknown`. Treat observable repo structure, commands, manifests, and explicit user confirmations as `Confirmed`; keep forward-looking interpretations, likely milestone candidates, and recommended next steps as `Suggested`; keep unresolved or conflicting areas as `Unknown`.
7. Backfill [PROJECT.md](../../../PROJECT.md) and [`.planning/STATE.md`](../../../.planning/STATE.md) minimally if they are missing or placeholder-only, including whether the repo expects a project namespace under the shared Obsidian MCP vault root. When `PROJECT.md` has markers, update only the `GSD-PROJECT: project-charter` block.
8. Assess whether the current project already has a sufficiently current Project Idea Document and enough preliminary technical direction grounded in repo evidence and explicit user input to reach stack-selection readiness. If either is missing, stale, or materially underspecified, stop short of stack selection and milestone planning and route explicitly to the prerequisite artifact work first.
9. Treat `$gsd-select-stack` as the next step after stack-selection readiness. Do not infer stack decisions beyond what the repository already proves.
10. Record whether the active repository has a `GSD Vault Project ID` in `PROJECT.md`; if missing, derive it from the repository root folder name and record whether `projects/<vault-project-id>/` already exists, should be verified, or should be created through `gsd-vault-bootstrap`.
11. Distinguish lightweight mapping from serious deep-mapping intent before finalizing the output. Treat repo onboarding, current-state orientation, and fast factual discovery as lightweight mapping. Treat modernization, major refactor, version upgrade, platform migration, stack migration, or other transformation-oriented understanding as serious deep mapping.
12. For lightweight mapping, keep the output concise and factual. For serious deep-mapping intent, preserve the same factual grounding but route to the dedicated [`.agents/skills/gsd-deep-map-codebase/SKILL.md`](../../../.agents/skills/gsd-deep-map-codebase/SKILL.md) workflow so the output expands into exhaustive transformation-ready current-state mapping, automatic mapping-milestone creation, first-phase preparation, roadmap and state updates, and the deep-mapping-specific orchestration handoff instead of collapsing into a thin summary.
13. Recommend likely first milestone candidates only when the governing Project Idea Document and Technical Specification are sufficiently current; otherwise recommend the missing readiness work instead. Do not create milestone files unless explicitly asked to switch into milestone planning.

## Source Templates
- [`.planning/templates/codebase-map-template.md`](../../../.planning/templates/codebase-map-template.md)
- [`.planning/templates/project-template.md`](../../../.planning/templates/project-template.md)
- [`.planning/templates/project-idea-document-template.md`](../../../.planning/templates/project-idea-document-template.md)
- [`.planning/templates/technical-specification-template.md`](../../../.planning/templates/technical-specification-template.md)
- [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md)

## Required Outputs
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md): architecture summary, key paths, commands, conventions, risks, and any future-facing interpretations with `Confirmed`, `Suggested`, and `Unknown` kept visibly separate when the template supports it. If managed markers exist, only the `GSD-PROJECT: codebase-map-content` block is updated.
- [`.planning/CONTEXT_INDEX.md`](../../../.planning/CONTEXT_INDEX.md): compact task-routing guide with routing rows, module cards, validation paths, search recipes, and do-not-scan boundaries when repo evidence is sufficient; otherwise a `partial` or placeholder index with explicit refresh needs.
- [PROJECT.md](../../../PROJECT.md): minimal project charter if still missing or placeholder-only. If managed markers exist, only the `GSD-PROJECT: project-charter` block is updated.
- Readiness assessment: whether the current project's Project Idea Document, preliminary technical direction, Technical Specification, and stack-selection/configuration-package planning artifacts are sufficiently current for the next step, or which prerequisite artifact work or `$gsd-select-stack` handoff must happen next.
- Vault bootstrap note: the resolved or missing `GSD Vault Project ID`, the expected namespace `projects/<vault-project-id>/`, and whether that namespace scaffold exists or needs the next explicit `gsd-vault-bootstrap` handoff.
- Serious-mapping boundary: when transformation-oriented intent is present, the mapping output must say that lightweight mapping is no longer sufficient, preserve the deep-mapping goal explicitly, and point to the dedicated deep-mapping workflow rather than pretending the onboarding pass already planned the transformation. That deep-mapping workflow owns the exhaustive map, mapping milestone creation, first bounded phase creation, roadmap and state updates, and final `$gsd-run-milestone` handoff.
- [`.planning/STATE.md`](../../../.planning/STATE.md): status updated to reflect mapping completion, milestone and phase status as `none` unless active work already exists, durable-memory follow-up as `none`, and the next recommended action as either prerequisite spec-readiness work, the dedicated deep-mapping workflow when transformation-oriented understanding is required, or `$gsd-plan-milestone` only when the governing artifacts are sufficiently current and deep mapping is not required.

## Rules
- Prefer repo evidence over assumptions. If something is unclear, mark it as unknown rather than guessing.
- Do not classify blueprint-owned GSD skill or template files as project application architecture unless the current repository is explicitly the reusable GSD blueprint. In normal project repositories, treat `.agents/skills/**` and `.planning/templates/**` as GSD workflow infrastructure.
- Use the shared `Confirmed` / `Suggested` / `Unknown` evidence meanings and keep them stable across outputs.
- Keep modernization ideas, probable subsystem boundaries, and likely first-milestone candidates framed as `Suggested` unless the repo or user explicitly confirms them.
- Keep conflicting or missing repo understanding visible as `Unknown` rather than smoothing it into a neat architecture summary.
- Cite real paths and commands. Avoid hand-wavy summaries.
- If the repository is effectively empty, stop and switch to `$gsd-new-project`.
- Exception: if the user explicitly asks to select the stack, allow `$gsd-select-stack` to gather missing stack-selection inputs directly instead of forcing a detour through `$gsd-new-project` first.
- Map repo reality first, then route the current project through Project Idea Document and Technical Specification backfill if needed. Do not pretend milestone planning is valid without those artifacts.
- Use UI options whenever remaining user input can reasonably be expressed as structured choices or confirmations.
- Do not treat serious deep-mapping intent as a lightweight mapping request.
- When deep-mapping intent is present, keep the mapping output factual and transformation-ready. Capture subsystem boundaries, dependency seams, integration hotspots, blockers, and migration-sensitive constraints, but do not turn the skill into migration design, architecture redesign, or execution planning.
- When the user needs serious deep mapping, do not stop at "the repo probably needs a milestone." Route explicitly to the dedicated deep-mapping workflow, which will create the large structured mapping milestone, first bounded mapping phase, roadmap and state updates, and final `$gsd-run-milestone` handoff after the exhaustive map is complete.
- Mapping should produce both factual understanding in `CODEBASE_MAP.md` and practical routing guidance in `CONTEXT_INDEX.md` when the repository has enough structure.
- If `.planning/CODEBASE_MAP.md` has the blueprint/project marker structure, never rewrite the whole file. Replace only the project-owned `GSD-PROJECT: codebase-map-content` block.
- If `PROJECT.md` has the blueprint/project marker structure, preserve the blueprint guidance block and replace only the project-owned `GSD-PROJECT: project-charter` block when a minimal backfill is needed.
- If markers are missing but project content exists, preserve the file and surface a marker insertion or migration plan instead of overwriting it.
- Do not duplicate the full codebase map into the context index. Keep the context index compact and task-routing oriented.
- Do not block lightweight mapping if the context index can only be partial; record the missing routing areas and a `$gsd-refresh-context-index` follow-up.
- Keep written normalization lightweight by default. Only require a fuller written normalization pass when ambiguity, risk, scope, or explicit user request justifies it.
- Do not write durable project memory from mapping. The only vault action allowed here is identifying or handing off project-local scaffold verification.
- Do not create milestone or phase files here. Mapping is preparation for planning, not planning itself.

## Completion Check
- [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) is grounded in observable repository facts.
- `.planning/CONTEXT_INDEX.md` exists as `current`, `partial`, or explicitly placeholder with a clear refresh reason, and future agents have a routing surface before broad repo scanning.
- [`.planning/STATE.md`](../../../.planning/STATE.md) names the next recommended action.
- The output identifies at least one plausible first milestone candidate only when the governing Project Idea Document and Technical Specification are sufficiently current; otherwise it explicitly routes to the missing readiness work without pretending planning is already done.
