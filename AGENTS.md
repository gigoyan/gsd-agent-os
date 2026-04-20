# GSD Operating Contract

## Repo / Vault Split
- The repo is the runtime workflow layer: instructions, skills, planning, execution, validation, and handoff.
- The vault is the durable memory layer: long-lived project memory, decisions, debugging history, and reusable context.
- Do not use `.planning/` or `.codex/` as shadow memory systems.
- `.codex/` may hold local convenience helpers only; it is not authoritative memory.
- The exact vault structure, note-routing rules, naming rules, linking rules, and save behavior are defined in [`.planning/templates/vault-operating-spec.md`](./.planning/templates/vault-operating-spec.md).

## Bootstrap And Local Ownership
- This GSD package may be used directly in a project repository or copied in from a reusable source.
- The local repository copy owns live workflow control, and the project-local vault owns that project's durable memory.
- When syncing updates from a reusable source, copy them in after manual review; do not rely on automatic sync or shared runtime state.
- The reusable vault scaffold and note templates live under [`.planning/templates/vault-scaffold/`](./.planning/templates/vault-scaffold/) and [`.planning/templates/vault-note-templates/`](./.planning/templates/vault-note-templates/).

## Required Reading Order
- Before non-trivial work, read `[PROJECT.md](./PROJECT.md)`, [`.planning/STATE.md`](./.planning/STATE.md), and the active milestone and phase named in state.
- When the current project already has a Project Idea Document and Technical Specification, read the governing copies before milestone planning or implementation.
- For GSD-relevant work, use narrow, task-shaped retrieval only when it helps the current task.
- For discussion-only work, suppress automatic memory lookup unless the user explicitly asks for memory.

## Intake Routing And Interaction Contract
- Use the shared intake routes and evidence semantics defined in [`.planning/templates/intake-routing-and-evidence-contract.md`](./.planning/templates/intake-routing-and-evidence-contract.md).
- Keep route selection explicit across placeholder bootstrap, document-first intake, existing-project mapping, explicit stack-selection, and partial-maturity continuation entry states.
- Use UI options as the default for choice-shaped user interactions whenever the needed input can reasonably be expressed as structured choices, combinations, or confirmations.
- Treat serious deep-mapping intent as distinct from lightweight mapping so later workflow steps can route to dedicated deep-mapping work instead of a shallow repo summary.

## Spec-First Readiness Gate
- Spec-First is mandatory for non-trivial greenfield work and non-trivial existing-project changes.
- Required lifecycle order is:
  - Idea
  - Project Idea Document
  - preliminary technical direction
  - stack selection
  - stack-aware Technical Specification completion
  - project-specific configuration package
  - milestone planning
  - execution
  - verification
  - handoff
- Exception: when the repository itself is the reusable GSD blueprint and the active work is improving the blueprint's own workflow, skills, templates, contracts, or docs, treat the active milestone, active phase, and prior verification artifacts as the governing spec context for that blueprint-improvement effort.
- In that blueprint-improvement mode, do not require a project-specific Project Idea Document, Technical Specification, or stack-selection/configuration-package artifact before milestone planning, execution, or verification.
- This exception applies only while the work remains repo-internal blueprint improvement and the cleanup rule will reset temporary milestone scaffolding before the blueprint is handed to a real project.
- Do not start non-trivial milestone planning or implementation until the Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact are sufficiently current for the work being proposed.
- If an existing project lacks those artifacts, map current repo reality first, then backfill the missing idea/spec layer before planning implementation.
- Lightweight prompt normalization remains automatic for GSD-relevant work; written normalization is required only when ambiguity, risk, scope, or explicit user request justifies it.
- Discussion-only mode and explicit-only fast mode remain valid exceptions to workflow overhead, but they do not silently waive the Spec-First gate for non-trivial implementation work.

## Stack Selection Readiness Gate
- `$gsd-select-stack` uses a narrower readiness gate than milestone planning.
- Stack selection may begin before the Technical Specification is fully complete when the current project has:
  - a current Project Idea Document
  - primary flows and user or operator outcomes understood well enough to judge stack fit
  - major constraints and non-negotiables captured
  - architecture direction clear enough to distinguish likely stack options
- When the user explicitly asks to select the stack, treat that request itself as a valid Spec-First entry point.
- In that explicit stack-selection path, do not block on missing bootstrap or spec artifacts. Instead, gather the minimum missing stack-selection inputs inline, use repo evidence when it exists, and proceed with stack selection for the current project.
- Preliminary technical direction may live in an early Technical Specification draft or in the current project's bootstrap charter and requirements surfaces while the detailed Technical Specification is still being completed.
- Use stack selection to resolve the concrete stack and variants, then finish the Technical Specification with those choices before milestone planning or implementation.

## Spec Artifact Boundaries
- `PROJECT.md` is the current repository's project charter and bootstrap artifact; it is not the Project Idea Document.
- `.planning/REQUIREMENTS.md` is the current repository's project requirements surface; it is not the Technical Specification.
- `.planning/CODEBASE_MAP.md` is the current repository's grounded architecture map or a placeholder until `$gsd-map-codebase` replaces it.
- `.planning/ROADMAP.md` and `.planning/STATE.md` are live workflow control surfaces and must stay reset when no project work is active.
- Use [`.planning/templates/project-template.md`](./.planning/templates/project-template.md) and [`.planning/templates/requirements-template.md`](./.planning/templates/requirements-template.md) for the bootstrap charter and requirements surfaces.
- Use [`.planning/templates/project-idea-document-template.md`](./.planning/templates/project-idea-document-template.md), [`.planning/templates/technical-specification-template.md`](./.planning/templates/technical-specification-template.md), and [`.planning/templates/stack-selection-and-configuration-package-template.md`](./.planning/templates/stack-selection-and-configuration-package-template.md) for later Spec-First readiness artifacts.
- Use [`.planning/templates/stack-profile-contract.md`](./.planning/templates/stack-profile-contract.md) as the reusable contract for stack-aware blueprint data, supported variant options, and the mapping from selected stack choices into generated project-local outputs.
- Keep the reusable GSD base generic. Do not hardcode a concrete frontend, backend, database, auth, or deployment stack into reusable instructions or starter files unless the current project has explicitly selected it.
- Project-specific `.codex/config.toml` and `.codex/agents/*.toml` are generated only after the required stack selection is complete for the current project.
- `.codex` remains a runtime convenience surface, not the main documentation layer and not a memory system.

## Project-Local Configuration Package Generation
- Post-stack-selection `.codex` generation happens only after the current project's stack-selection/configuration-package artifact and stack-aware Technical Specification are sufficiently current.
- Required inputs for project-local generation are the current project's Project Idea Document, Technical Specification, completed stack-selection/configuration-package artifact, selected stack profile IDs and variant options, runtime environments, toolchain constraints, required child-role set, and reviewer-permission policy.
- Use `$gsd-select-stack` as the standard GSD workflow step for curated stack-profile selection, narrow official-doc freshness checks, and project-local generation planning.
- Reusable GSD packages may provide instructions and checklists for that generation step, but must not ship concrete project-local `.codex/config.toml` or `.codex/agents/*.toml` outputs.
- Keep generated project-local configuration packages stack-aware for the current project while keeping the reusable GSD wording stack-agnostic.
- When the current project uses curated stack profiles, derive generated `AGENTS.md` fragments, skills, templates, and project-local `.codex` outputs from the selected profile and option set rather than inventing detached stack behavior during execution.
- If project-local `.codex` schema detail is needed, verify it narrowly from official Codex or OpenAI guidance at execution time and do not invent unsupported fields.
- Review generated project-local `.codex` files against the selected stack, approval constraints, and bounded-child orchestration rules before treating them as ready.

## Stack Selection Flow
- Run `$gsd-select-stack` after the current project reaches stack-selection readiness, even if the Technical Specification is still draft or partial.
- If the user explicitly requests stack selection, allow `$gsd-select-stack` to gather the minimum missing context itself instead of first routing away to `$gsd-new-project` or `$gsd-map-codebase`.
- Use curated stack profiles under [`.agents/stack-profiles/`](./.agents/stack-profiles/) as the blueprint source of truth for supported stacks and variant options.
- For existing repositories, map what the repo already proves first and ask only for missing or future-target choices instead of re-asking proven stack facts.
- When curated choice questions are still needed and collaboration mode is `Default`, stop and instruct the user to switch to `Plan` mode and reply `done` before continuing stack selection.
- When curated choice questions are needed and collaboration mode is `Plan`, use structured UI selection with short descriptions, best-fit guidance, tradeoffs, and compact examples where they materially improve understanding.
- After stack choices are confirmed, capture them in the current project's stack-selection/configuration-package artifact, then finish any stack-sensitive Technical Specification work that remains before milestone planning or project-local generation.

## Mode Rules
- Standard GSD mode uses the full applicable lifecycle: read, narrow retrieve when useful, plan, execute, verify, and update state.
- Discussion-only mode suppresses automatic memory lookup and suppresses durable writeback.
- Explicit-only fast mode is allowed only when explicitly requested; it narrows lookup, minimizes normalization, and does not reduce safety or continuity.
- Example: a short clarification question during planning does not require a vault write.
- Example: a recurring integration decision or debugging root cause does require durable memory writeback if it will matter later.

## Write And Retrieval Gates
- Default durable-memory action is `do not write`.
- Write only when the information is likely to matter in later sessions, not because activity happened.
- Retrieve a small context pack, not a vault dump.
- Prefer current project memory, then directly related durable notes, then broader material only when clearly relevant.
- Surface conflicts or uncertainty instead of flattening them into fake certainty.
- Example: retrieve current priorities plus the latest relevant decision note for a feature milestone.
- Example: do not retrieve unrelated debugging history for a pure discussion prompt.
- When a write is justified, route it to the exact vault note owner defined in the vault operating spec rather than inventing a new category or filename.

## Main-Agent Conversation Language
- The conversation language used for direct discussion with the main agent is a project-level runtime preference, not a GSD-step preference.
- Before handling any user request in a project, first check whether a project-scoped conversation-language preference already exists for that project.
- Derive project scope from the current project root so the preference is isolated per project and does not affect other repositories that use this GSD blueprint.
- Store the conversation-language preference only in project-scoped local Codex state outside the repository, for example under `%CODEX_HOME%/project-preferences/<project-id>.toml`.
- Do not store the conversation-language preference in `.planning/`, `.codex/`, the vault, templates, or any other repository artifact.
- If the project-scoped conversation-language preference is missing, do not perform the user's requested task yet.
- When the preference is missing and collaboration mode is `Default`, stop and instruct the user to switch to `Plan` mode and reply `done` so the language can be selected first.
- When the preference is missing and collaboration mode is `Plan`, require a structured UI language selection before any other work proceeds.
- The structured UI language selection must offer these options:
  - `English`
  - `Armenian`
  - `Russian`
- After the user selects one of those options, save it in the project-scoped local Codex state and then continue with the pending task.
- The user may later explicitly change the conversation language, and the latest explicit choice replaces the stored project-scoped preference.
- Do not infer or change the selected conversation language from the language of the user's message alone, including on the first message in a project.
- Mixed-language user input does not change the selected conversation language unless the user explicitly asks to switch or the intent to switch is unmistakable.
- This conversation-language preference affects only user-facing main-agent discussion, not internal workflow text or repository artifacts.
- All internal GSD work remains in English, including planning, execution, verification, memory lookup, state updates, documentation, markdown artifacts, sub-agent prompts, sub-agent outputs, and control labels such as `Phase Status`, `Milestone Status`, and `Next-Step Prompt`.

## GSD Workflow Preservation
- Preserve the existing GSD workflow model.
- Keep these capabilities intact:
  - `$gsd-new-project`
  - `$gsd-map-codebase`
  - `$gsd-select-stack`
  - `$gsd-plan-milestone`
  - `$gsd-execute-phase`
  - `$gsd-verify-phase`
  - `$gsd-run-milestone`
  - `$gsd-quick-task`
- Use the milestone path for anything cross-file, architectural, ambiguous, multi-step, or likely to span multiple turns.
- Use `$gsd-quick-task` only for small, low-risk, bounded work.
- Default to test-first by meaningful behavior slice when practical.
- Do not skip verification after implementation.

## `gsd-run-milestone`
- Preserve `$gsd-run-milestone` as a user-requested milestone automation capability.
- The root session is the only milestone orchestrator.
- The root session delegates exactly one bounded GSD step at a time.
- Child agents perform exactly one assigned GSD step and then stop.
- Child agents must not orchestrate, route, or spawn other agents.
- Routing depends on explicit `Phase Status`, `Milestone Status`, and `Next-Step Prompt` output.
- Example: a child may execute one phase and return control, but may not decide to continue the loop.

## Reusable Package Cleanup Requirement
- A reusable GSD package must not ship milestone, phase, verification, roadmap, or state history from developing the GSD package itself.
- Before handing this GSD to a new or existing project, reset `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/CODEBASE_MAP.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` to clean project-local starter surfaces or placeholders.
- Clear milestone, phase, and verification artifacts that belong to the GSD package itself while preserving durable operating assets such as skills, templates, and contract docs.
- When no project work is active, `.planning/STATE.md` and `.planning/ROADMAP.md` must show no active milestone or phase rather than stale execution pointers.
- During blueprint-improvement work, keep temporary milestone scaffolding until final verification passes and the user explicitly approves cleanup.

## State And Output Contract
- Keep [`.planning/STATE.md`](./.planning/STATE.md) current, concise, and operational after planning, execution, and verification.
- Keep milestone and phase names explicit in state so an orchestrator can resume without guessing.
- Planning, execution, and verification outputs must include explicit `Phase Status` and `Milestone Status` lines.
- Each completed GSD step must end with a minimal, directly usable `Next-Step Prompt` when another GSD step is needed.
- Long-form templates belong under [`.planning/templates/`](./.planning/templates/), not in this file.
