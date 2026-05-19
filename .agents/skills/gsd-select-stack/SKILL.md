---
name: gsd-select-stack
description: Select curated stack profiles and project-specific variant options after the Project Idea Document is current and the project has reached stack-selection readiness, then prepare or refresh the stack-selection/configuration-package artifact. Use when spec-first readiness has reached stack selection for a new project, when an existing project needs stack-aware onboarding after repo mapping, or when the current stack-selection/configuration-package artifact is missing, stale, or needs an explicit update before milestone planning.
---

# GSD Select Stack

## Overview

Run the stack-selection step of the GSD spec-first flow.
Use this skill to resolve curated stack profiles, guide the user through supported variant choices, surface profile-backed `Suggested` recommendations when the profile metadata justifies them, and capture the selected stack in the project artifact without blocking on a fully finished Technical Specification.
If the user explicitly asks to select the stack, this skill is allowed to act as the entry point and gather the minimum missing stack-selection context itself.
Project-local output generation and profile-specific expansion remain derived follow-on work after stack selection is current; they are not part of this bounded evidence-aware selection step.

## Workflow

1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md), [`.planning/STATE.md`](../../../.planning/STATE.md), the current Project Idea Document, the current Technical Specification if one exists, and the current stack-selection/configuration-package artifact if one already exists.
2. For existing repositories, also read [`.planning/CODEBASE_MAP.md`](../../../.planning/CODEBASE_MAP.md) and treat proven repo facts as stronger than assumptions or user shorthand.
3. Read [`.planning/templates/stack-profile-contract.md`](../../../.planning/templates/stack-profile-contract.md) and [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md) before selecting or updating any stack profile.
4. If the user explicitly asked to select the stack, do not block on missing bootstrap artifacts. Instead, gather the minimum missing stack-selection context inline and proceed.
5. Otherwise, stop if the Project Idea Document is missing or if the project has not yet reached stack-selection readiness. Return an explicit prerequisite route instead of improvising stack choices.
6. Assess stack-selection readiness from the current project artifacts or from the explicit stack-selection conversation. A fully complete Technical Specification is not required for first-time stack selection when the current project already has:
   - problem and user or operator outcomes clear enough to judge fit
   - primary flows understood
   - major constraints and non-negotiables captured
   - architecture direction clear enough to distinguish likely stack options
   - If the user explicitly requested stack selection and any of those inputs are still missing, ask only for the missing information needed to choose the stack. Do not force a prior `$gsd-new-project` or `$gsd-map-codebase` run.
7. If the Technical Specification is missing or still draft, treat it as an input surface, not a blocker. Record stack-sensitive open questions and use the selected stack to help finish the Technical Specification afterward.
8. Determine whether the current request needs:
   - first-time stack selection
   - a partial update to an existing stack-selection artifact
9. Resolve domain by domain. Use curated stack profiles under [`.agents/stack-profiles/`](../../../.agents/stack-profiles/) whenever a supported profile exists. If a supported curated profile does not exist for a required domain, record `Other`, capture the constraint, and do not invent a fake curated package.
10. For each selected curated profile, read its recommendation metadata before asking new questions. Use matching recommendation sets, recommended option combinations, and convention overlays only when repo evidence or explicit user inputs satisfy the profile's `when_to_suggest` conditions.
11. Track stack facts, recommendations, and open decisions as `Confirmed`, `Suggested`, or `Unknown`. Treat repo-proven technologies, explicit user choices, and profile options already selected in the current artifact as `Confirmed`; keep profile-backed defaults, recommended combinations, prefills, and convention bundles as `Suggested`; keep undecided axes, conflicting evidence, or not-yet-proven operational constraints as `Unknown`.
12. When structured user choices are still needed:
   - In `Default` mode, stop and instruct the user to switch to `Plan` mode and reply `done`.
   - In `Plan` mode, use `request_user_input` and ask at most `1-3` questions at a time.
   - Show short option descriptions, best-fit guidance, and main tradeoffs in the UI choice descriptions.
   - When a profile-backed recommendation bundle exists, show the recommended option combination first and make any override path explicit instead of hiding it in prose.
   - If an option would be easier to understand with an example, provide the compact example in normal chat text before or between the structured questions rather than bloating the button text.
13. For existing projects, ask only for missing or future-target choices. Do not re-ask authoring mode, framework, repo shape, or similar decisions when the repo already proves them and the user is not asking to change them.
14. Write or refresh the current project's stack-selection/configuration-package artifact using [`.planning/templates/stack-selection-and-configuration-package-template.md`](../../../.planning/templates/stack-selection-and-configuration-package-template.md). Capture selected profile IDs, selected options, recommendation sets reviewed, accepted or overridden combinations, fit reasoning, accepted tradeoffs, convention overlays shown, examples shown, and any explicitly reviewed inputs, while keeping `Suggested` recommendations and `Unknown` decision gaps visible until confirmation.
15. If bootstrap artifacts, the Project Idea Document, or the Technical Specification are still missing or draft after selection, stop after updating the stack-selection artifact and route explicitly to the next missing upstream artifact work.
16. If the current request primarily asks for profile freshness validation, project-local `AGENTS.md` or `.codex` generation, or profile-specific output planning, stop after stack selection and route that work to a later bounded stack-selection follow-on. Keep the current skill limited to evidence-aware profile choice capture and explicit routing.

## Deferred Follow-On Boundary

- Keep project-local `AGENTS.md` and `.codex` outputs as derived artifacts from the selected stack rather than blueprint truth, but defer their planning or generation until a later bounded stack-selection follow-on.
- Keep narrow official-doc freshness checks tied to selected profiles as later follow-on work instead of folding them into this selection step.
- Keep profile-specific integration details, generated-output manifests, and profile-asset expansion outside this skill until the later stack-selection phase explicitly takes ownership.
- When stack selection changes expected structure, commands, validation strategy, generated project-local outputs, or runtime surfaces, record a `$gsd-refresh-context-index` follow-up candidate so the context index stays aligned with the selected stack.

## Required Outputs

- Updated stack-selection/configuration-package artifact for the current project, or an explicit stop reason when readiness is not satisfied.
- Updated stack-selection/configuration-package artifact for the current project, with repo-proven inputs, recommended defaults, and unresolved decisions kept visibly `Confirmed`, `Suggested`, or `Unknown`.
- Accepted or overridden profile-backed recommendation sets and convention overlays captured explicitly instead of being flattened into confirmed facts.
- Explicit deferment when the request also needs profile freshness validation, project-local output generation, or profile-specific expansion work beyond stack-selection capture.
- Context-index impact: whether selected stack choices require creating or refreshing `.planning/CONTEXT_INDEX.md`.
- Explicit next-step routing:
  - Bootstrap, Project Idea Document, or Technical Specification completion when stack selection is done but upstream artifacts are still incomplete.
  - `$gsd-plan-milestone` when stack selection and the Technical Specification are sufficiently current for planning.
  - A prerequisite artifact step only when the user did not explicitly request stack selection and stack-selection readiness is still incomplete.

## Rules

- Keep the skill focused on evidence-aware stack selection. Do not blur this skill into project bootstrap, codebase mapping, milestone planning, implementation, profile freshness review, or project-local output generation.
- Do not auto-select a curated profile or option from message language, vague user preference, or community advice alone.
- Do not silently convert a recommended profile or variant from `Suggested` to `Confirmed`.
- Do not silently convert an accepted recommendation bundle into repo evidence; record the user acceptance or override explicitly.
- Keep unanswered but material selection gaps as `Unknown`, and when the plausible answers can be enumerated, ask for confirmation through UI options instead of free-text.
- Prefer the smallest number of questions that still yields a coherent stack choice package.
- Do not require a fully completed Technical Specification before first-time stack selection if stack-selection readiness is already satisfied.
- When the user explicitly asks to select the stack, do not reject the request just because bootstrap artifacts are missing.
- Never rewrite the reusable blueprint stack profiles from ad hoc research during selection.
- Treat project-local `AGENTS.md` and `.codex` outputs as derived-only follow-on work, never as reusable blueprint truth.
- Keep examples short and explanatory. Longer rationale belongs in the profile assets or references, not the project artifact.
- End with explicit handoff text when another GSD step is required.

## Completion Check

- Stack-selection readiness was checked before any stack questions were asked, and explicit user-requested stack selection was allowed to gather missing context inline.
- The selected curated profiles and option IDs are recorded in the current project's stack-selection/configuration-package artifact together with fit reasoning and any explicitly reviewed inputs.
- Any profile-backed recommendation bundles used during selection are recorded with their acceptance or override outcome.
- Later profile-expansion work such as official-doc freshness checks and project-local output generation is explicitly deferred instead of being folded into this selection step.
- The final routing clearly points either to upstream artifact completion, `$gsd-plan-milestone`, or the missing prerequisite work.
