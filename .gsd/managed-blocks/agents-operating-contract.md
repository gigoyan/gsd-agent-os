<!-- GSD-BLUEPRINT:START operating-contract -->
# GSD Operating Contract

## Repo / Vault Split
- The repo is the runtime workflow layer: instructions, skills, planning, execution, validation, and handoff.
- The vault is the durable memory layer: long-lived project memory, decisions, debugging history, and reusable context.
- Do not use `.planning/` or `.codex/` as shadow memory systems.
- `.codex/` may hold local convenience helpers only; it is not authoritative memory.
- The exact vault structure, note-routing rules, naming rules, linking rules, and save behavior are defined in [`.planning/templates/vault-operating-spec.md`](./.planning/templates/vault-operating-spec.md).

## Bootstrap And Local Ownership
- This GSD package may be used directly in a project repository or copied in from a reusable source.
- The local repository copy owns live workflow control, and the project namespace under the shared Obsidian vault root owns that project's durable memory.
- When syncing updates from a reusable source, copy them in after manual review; do not rely on automatic sync or shared runtime state.
- The reusable vault scaffold and note templates live under [`.planning/templates/vault-scaffold/`](./.planning/templates/vault-scaffold/) and [`.planning/templates/vault-note-templates/`](./.planning/templates/vault-note-templates/).

## Blueprint Distribution And Sync

- GSD has a reusable blueprint source and installed project repository copies.
- The blueprint source owns reusable GSD assets such as skills, templates, contracts, managed-block source content, and the blueprint manifest.
- Project repositories receive an installed local copy of selected GSD files.
- Blueprint updates must be distributed through manifest-driven sync, not manual copy-paste.
- GSD has one Blueprint synchronization workflow: `$gsd-sync-blueprint`.
- `$gsd-sync-blueprint` owns both audit-only reporting and approval-gated install/update.
- Separate blueprint drift audit skill does not exist.
- `$gsd-sync-blueprint` must compare real content for Blueprint-owned files and managed-block content for mixed files; file presence alone is insufficient.
- `$gsd-sync-blueprint` must detect Blueprint-installed files removed from the current manifest by comparing the target lock with the source manifest.
- `$gsd-sync-blueprint` must preserve project-owned runtime files and generated project-local files.
- `$gsd-sync-blueprint` must stop for explicit approval before applying replacements, managed-block updates, starter creation, deletions, marker migrations, or lock updates.
- Use `.gsd/blueprint-manifest.json` as the source of file ownership and sync strategy.
- Use `.gsd/managed-blocks/agents-operating-contract.md` as the canonical reusable source for the `AGENTS.md` `GSD-BLUEPRINT: operating-contract` managed block.
- The root blueprint `AGENTS.md` `GSD-BLUEPRINT: operating-contract` block must match `.gsd/managed-blocks/agents-operating-contract.md` exactly.
- Project repositories use `.gsd/blueprint.lock.json` to record installed Blueprint file metadata, ownership, sync strategy, content hashes when available, and installed version or commit.
- Treat files by ownership class:
  - `blueprint_replace`: reusable blueprint files that may be replaced during sync.
  - `project_preserve`: project runtime files that must never be overwritten during sync.
  - `managed_block`: mixed files where only marked blueprint blocks may be updated.
  - `bootstrap_then_managed_block`: starter surfaces created when missing, then updated only inside marked blueprint guidance blocks while preserving project-owned content.
  - `bootstrap_if_missing`: starter files created only when missing.
  - `generated_project_local`: project-specific generated files that blueprint sync must ignore.
- If ownership is unclear, preserve the target file and report the ambiguity.
- Never overwrite project-specific `PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/CODEBASE_MAP.md`, `.planning/CONTEXT_INDEX.md`, milestones, phases, verification files, or `.codex` outputs during blueprint sync.
- In `PROJECT.md` and `.planning/CODEBASE_MAP.md`, blueprint sync may update only the marked `GSD-BLUEPRINT` guidance block and must preserve all `GSD-PROJECT` content exactly.
- `.planning/STATE.md` is active runtime state and must remain bootstrap-if-missing only; existing project state must never be sync-updated or converted to managed blocks.
- Target project `README.md` is project-owned and must not be created, overwritten, replaced, compared, or managed-block-updated by GSD blueprint sync.
- Keep `AGENTS.md` as the only `managed_block` project-facing documentation file unless another file is explicitly approved later. `PROJECT.md` and `.planning/CODEBASE_MAP.md` use `bootstrap_then_managed_block`, not generic `managed_block`.
- In `AGENTS.md`, blueprint sync may update only the `GSD-BLUEPRINT: operating-contract` managed block.
- Blueprint sync must preserve the project-owned `GSD-PROJECT: local-settings` block exactly, except when the user explicitly asks to change the local setting.
- Do not place marker examples inside `AGENTS.md`; marker syntax and sync behavior are defined in `.planning/templates/blueprint-distribution-contract.md`.
- If target `AGENTS.md` lacks the `operating-contract` marker but contains old unmarked GSD template or operating content, `$gsd-sync-blueprint` must report `AGENTS.md legacy-template migration required`, show a reviewed migration diff, and require explicit approval before replacing the old template content with the canonical managed block plus the `GSD-PROJECT: local-settings` block.
- Preserve genuinely project-specific local instructions outside old unmarked GSD template content. If the boundary is ambiguous, stop and report a conflict instead of guessing.
- Preserve all project-specific content outside the blueprint-managed block.

## Obsidian MCP Vault Namespace

- Codex connects to one shared Obsidian MCP vault root configured outside this repository.
- GSD must not require one MCP server or one `config.toml` entry per project.
- Each repository owns exactly one project memory namespace inside the shared vault root:

    projects/<vault-project-id>/

- `<vault-project-id>` must be resolved from the current repository before any vault read, write, bootstrap, lookup, or save action.
- Resolve `<vault-project-id>` in this order:
  1. Use the confirmed `GSD Vault Project ID` recorded in `PROJECT.md`.
  2. If it is missing, derive it from the current repository root folder name.
  3. Preserve the repository folder name except replace filesystem-invalid path characters with `-`.
  4. Do not infer the ID from product names, package names, company names, branch names, or chat wording.
  5. If the derived namespace already exists and appears to belong to another project, stop and ask the user for an explicit override.
- All paths in the vault operating spec are relative to:

    projects/<vault-project-id>/

- Do not read from or write to another project namespace.
- Do not write durable notes directly under the shared vault root.
- Do not store the absolute Obsidian vault root in repository artifacts; it belongs to Codex MCP configuration.

## Required Reading Order
- Before non-trivial work, read `[PROJECT.md](./PROJECT.md)`, [`.planning/STATE.md`](./.planning/STATE.md), and the active milestone and phase named in state.
- When the current project already has a Project Idea Document and Technical Specification, read the governing copies before milestone planning or implementation.
- Before broad repository scanning during planning, execution, verification, quick tasks, or milestone orchestration, read `.planning/CONTEXT_INDEX.md` when it exists and is not placeholder-only. Use it to select the narrowest relevant context route before inspecting source files.
- For GSD-relevant work, use narrow, task-shaped retrieval only when it helps the current task.
- For discussion-only work, suppress automatic memory lookup unless the user explicitly asks for memory.

## Intake Routing And Interaction Contract
- Use the shared intake routes and evidence semantics defined in [`.planning/templates/intake-routing-and-evidence-contract.md`](./.planning/templates/intake-routing-and-evidence-contract.md).
- Keep route selection explicit across placeholder bootstrap, document-first intake, existing-project mapping, explicit stack-selection, and partial-maturity continuation entry states.
- Use UI options as the default for choice-shaped user interactions whenever the needed input can reasonably be expressed as structured choices, combinations, or confirmations.
- GSD has one unified mapping capability: `$gsd-map-codebase`.
- The unified mapping capability handles empty or nearly empty repositories, new projects with some files, existing projects without GSD mapping, partial mapping, stale mature mapping, serious full mapping, transformation/migration/refactor mapping, and targeted context-index routing refresh.
- Do not route mapping to any other mapping workflow.

## Unified Mapping
- `$gsd-map-codebase` is a self-orchestrating mapping workflow, not a milestone-planning workflow.
- The mapping orchestrator may spawn bounded mapping sub-agents for factual mapping slices.
- Mapping sub-agents run at medium reasoning effort.
- The mapping orchestrator must wait for each child result before continuing.
- The mapping orchestrator owns mapping strategy, slice decomposition, child prompt quality, artifact updates, and final consistency review.
- Mapping children own only their assigned slice: inspect assigned paths, report factual findings, suggest precise updates, identify gaps or stale assumptions, and return structured output.
- Mapping children must not orchestrate, spawn agents, edit unrelated files, broaden beyond the assigned slice, invent architecture or conventions, or design future implementation, migration, or target architecture.
- Mapping must not create milestones or phases for mapping, `$gsd-run-milestone` handoffs, mapping-specific verification bypasses, or special `$gsd-run-milestone` behavior.
- `CODEBASE_MAP.md` records current system reality: architecture, dependency direction, runtime behavior, data and integration surfaces, operational surfaces, risks, fragile areas, and evidence status.
- `CONTEXT_INDEX.md` is the repo-local coding-agent navigation guide: task routes, start-here paths, likely edit files, symbols/APIs, canonical examples, conventions, validation paths, search recipes, and do-not-touch boundaries.
- Mapping artifacts are written for future coding agents first. Prioritize operational routing, canonical examples, symbols, conventions, validation paths, command evidence, and do-not-touch boundaries over human-facing narrative explanation.
- Planning, execution, and verification agents must actively use `CODEBASE_MAP.md` and `CONTEXT_INDEX.md` to navigate the repo, follow conventions, select validation, and avoid unrelated, generated, vendor, or fragile areas.
- Agents must update those artifacts when real work proves them stale or incomplete and the correction is local and evidence-supported; otherwise record a precise `$gsd-map-codebase` unified mapping refresh candidate in `.planning/STATE.md`.
- Do not store `CONTEXT_INDEX.md` in the vault.
- Do not use vault memory as a replacement for repo-local task routing.

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
- `.planning/CODEBASE_MAP.md` is the current repository's grounded current-system-reality map or a placeholder until `$gsd-map-codebase` replaces it.
- `.planning/CONTEXT_INDEX.md` is the current repository's repo-local coding-agent navigation guide. It tells agents where to start, what to inspect next, what usually changes, which symbols/APIs and canonical examples matter, how to validate, and what to avoid for common task types. It is not durable memory and must not be copied into the vault.
- `.planning/ROADMAP.md` and `.planning/STATE.md` are live workflow control surfaces and must stay reset when no project work is active.
- `PROJECT.md` and `.planning/CODEBASE_MAP.md` may contain a small `GSD-BLUEPRINT` guidance block plus a `GSD-PROJECT` content block. Runtime skills update only the project-owned content blocks when markers exist.
- `.planning/STATE.md` must not contain managed-block markers.
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
- Treat `.planning/CONTEXT_INDEX.md` as repo-local workflow guidance. Do not store it in the Obsidian vault, and do not use the vault as a replacement for task routing.

## Main-Agent Conversation Language
- The conversation language used for direct discussion with the main agent is a project-level runtime preference.
- `AGENTS.md` is the single source of truth for conversation-language behavior in this blueprint.
- Do not block work just because no conversation-language preference has been set yet.
- If no explicit preference has been set for the current project, continue in the current ongoing conversation language by default.
- The user may explicitly set or change the preferred conversation language at any time.
- When the user explicitly asks to use a different conversation language, save that preference only in the project-owned `GSD-PROJECT: local-settings` block in `AGENTS.md`, then continue in that language for future main-agent discussion in the same project.
- To determine whether a conversation-language preference has been set, read the `Main-agent conversation language:` field in the project-owned local settings block below the blueprint-managed GSD operating contract.
- Do not store the conversation-language preference in `.planning/`, `.codex/`, the vault, templates, generated project-local artifacts, or inside the blueprint-managed `GSD-BLUEPRINT: operating-contract` block.
- Do not silently change the selected conversation language based on a single mixed-language message. Only switch when the user explicitly asks, or when the intent to switch is unmistakable.
- This conversation-language preference affects only user-facing main-agent discussion.
- All internal GSD work remains in English, including planning, execution, verification, memory lookup, state updates, documentation, markdown artifacts, sub-agent prompts, sub-agent outputs, and control labels such as `Phase Status`, `Milestone Status`, and `Next-Step Prompt`.

## GSD Workflow Preservation
- Preserve the existing GSD workflow model.
- Keep these capabilities intact:
  - `$gsd-new-project`
  - `$gsd-map-codebase` (unified mapping)
  - `$gsd-select-stack`
  - `$gsd-plan-milestone`
  - `$gsd-execute-phase`
  - `$gsd-verify-phase`
  - `$gsd-run-milestone`
  - `$gsd-quick-task`
  - `$gsd-sync-blueprint`
- Use the milestone path for anything cross-file, architectural, ambiguous, multi-step, or likely to span multiple turns.
- Use `$gsd-quick-task` only for small, low-risk, bounded work.
- Default to test-first by meaningful behavior slice when practical.
- Do not skip verification after implementation.

## `gsd-run-milestone`
- Preserve `$gsd-run-milestone` as a user-requested milestone automation capability.
- The root session is the only milestone orchestrator.
- `$gsd-run-milestone` uses the latest available supported child-agent model with medium reasoning effort by default.
- A user-provided child model or child reasoning-effort value in the invocation of `$gsd-run-milestone` overrides the default for that run.
- The root orchestrator closes each completed child after reading its output and before spawning the next child.
- Child agents must not call `close_agent`; child cleanup is root-owned.
- If no active milestone or phase exists and planning is needed, the root session may delegate one planning child as before.
- The normal active-phase loop uses at most two child agents:
  1. one execution child that executes the active phase;
  2. one verification-and-next-phase-planning child that verifies the active phase and, only if verification passes and the milestone is still incomplete, creates the next bounded phase in the same active milestone.
- The verification-and-next-phase-planning composite child behavior is allowed only inside `$gsd-run-milestone`.
- Standalone `$gsd-verify-phase` and standalone `$gsd-plan-milestone` remain unchanged.
- Child agents must not orchestrate, spawn agents, continue the milestone loop, or execute implementation after verification.
- The composite child must not create the next phase on failed, partial, blocked, or milestone-completing verification.
- Routing depends on explicit `Phase Status`, `Milestone Status`, and `Next-Step Prompt` output.

## Reusable Package Cleanup Requirement
- A reusable GSD package must not ship milestone, phase, verification, roadmap, or state history from developing the GSD package itself.
- A reusable GSD package must ship blueprint assets and starter placeholders only. It must not ship live project history, active milestone execution state, project-specific context index content, or project-specific vault memory.
- Before handing this GSD to a new or existing project, reset `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/CODEBASE_MAP.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` to clean project-local starter surfaces or placeholders.
- Clear milestone, phase, and verification artifacts that belong to the GSD package itself while preserving durable operating assets such as skills, templates, and contract docs.
- When no project work is active, `.planning/STATE.md` and `.planning/ROADMAP.md` must show no active milestone or phase rather than stale execution pointers.
- During blueprint-improvement work, keep temporary milestone scaffolding until final verification passes and the user explicitly approves cleanup.

## State And Output Contract
- Keep [`.planning/STATE.md`](./.planning/STATE.md) current, concise, and operational after planning, execution, and verification.
- Keep milestone and phase names explicit in state so an orchestrator can resume without guessing.
- Planning, execution, and verification outputs must include explicit `Phase Status` and `Milestone Status` lines.
- Each completed GSD step must end with a minimal, directly usable `Next-Step Prompt` when another GSD step is needed.
- When an agent scans broadly because the context index is missing, stale, or insufficient, record a `$gsd-map-codebase` unified mapping refresh candidate in state instead of allowing repeated rediscovery.
- Long-form templates belong under [`.planning/templates/`](./.planning/templates/), not in this file.

## Repository Tool Capability Rule

Before running any repository command, check `.planning/tool-capabilities.md` if it exists.

If a command is marked as blocked, unavailable, non-executable, incompatible, or unsafe in the current environment:
- do not run it again
- use the recorded approved alternative
- mention the fallback briefly in the execution summary only when relevant

When a command fails due to environment/tool availability, record it once in `.planning/tool-capabilities.md` with:
- command
- failure reason
- approved fallback
- date
- evidence

Do not repeatedly rediscover the same unavailable command.
<!-- GSD-BLUEPRINT:END operating-contract -->
