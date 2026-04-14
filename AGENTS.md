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

## Spec-First Readiness Gate
- Spec-First is mandatory for non-trivial greenfield work and non-trivial existing-project changes.
- Required lifecycle order is:
  - Idea
  - Project Idea Document
  - Technical Specification
  - stack selection
  - project-specific configuration package
  - milestone planning
  - execution
  - verification
  - handoff
- Do not start non-trivial milestone planning or implementation until the Project Idea Document and Technical Specification are sufficiently current for the work being proposed.
- If an existing project lacks those artifacts, map current repo reality first, then backfill the missing idea/spec layer before planning implementation.
- Lightweight prompt normalization remains automatic for GSD-relevant work; written normalization is required only when ambiguity, risk, scope, or explicit user request justifies it.
- Discussion-only mode and explicit-only fast mode remain valid exceptions to workflow overhead, but they do not silently waive the Spec-First gate for non-trivial implementation work.

## Spec Artifact Boundaries
- `PROJECT.md` is the current repository's project charter and bootstrap artifact; it is not the Project Idea Document.
- `.planning/REQUIREMENTS.md` is the current repository's project requirements surface; it is not the Technical Specification.
- `.planning/CODEBASE_MAP.md` is the current repository's grounded architecture map or a placeholder until `$gsd-map-codebase` replaces it.
- `.planning/ROADMAP.md` and `.planning/STATE.md` are live workflow control surfaces and must stay reset when no project work is active.
- Use [`.planning/templates/project-template.md`](./.planning/templates/project-template.md) and [`.planning/templates/requirements-template.md`](./.planning/templates/requirements-template.md) for the bootstrap charter and requirements surfaces.
- Use [`.planning/templates/project-idea-document-template.md`](./.planning/templates/project-idea-document-template.md), [`.planning/templates/technical-specification-template.md`](./.planning/templates/technical-specification-template.md), and [`.planning/templates/stack-selection-and-configuration-package-template.md`](./.planning/templates/stack-selection-and-configuration-package-template.md) for later Spec-First readiness artifacts.
- Keep the reusable GSD base generic. Do not hardcode a concrete frontend, backend, database, auth, or deployment stack into reusable instructions or starter files unless the current project has explicitly selected it.
- Project-specific `.codex/config.toml` and `.codex/agents/*.toml` are generated only after the required stack selection is complete for the current project.
- `.codex` remains a runtime convenience surface, not the main documentation layer and not a memory system.

## Project-Local Configuration Package Generation
- Post-stack-selection `.codex` generation happens only after the current project's stack-selection/configuration-package artifact is sufficiently current.
- Required inputs for project-local generation are the current project's Project Idea Document, Technical Specification, completed stack-selection/configuration-package artifact, runtime environments, toolchain constraints, required child-role set, and reviewer-permission policy.
- Reusable GSD packages may provide instructions and checklists for that generation step, but must not ship concrete project-local `.codex/config.toml` or `.codex/agents/*.toml` outputs.
- Keep generated project-local configuration packages stack-aware for the current project while keeping the reusable GSD wording stack-agnostic.
- If project-local `.codex` schema detail is needed, verify it narrowly from official Codex or OpenAI guidance at execution time and do not invent unsupported fields.
- Review generated project-local `.codex` files against the selected stack, approval constraints, and bounded-child orchestration rules before treating them as ready.

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
- The user may explicitly choose the conversation language used for direct discussion with the main agent, and may change that choice later.
- The latest explicit user choice applies to future main-agent replies and to how the main agent interprets the user's messages.
- Mixed-language user input does not change the selected conversation language unless the user explicitly asks to switch or the intent to switch is unmistakable.
- This conversation-language choice affects only user-facing main-agent discussion, not internal workflow text or repository artifacts.
- All internal GSD work remains in English, including planning, execution, verification, memory lookup, state updates, documentation, markdown artifacts, sub-agent prompts, sub-agent outputs, and control labels such as `Phase Status`, `Milestone Status`, and `Next-Step Prompt`.
- Do not store the conversation-language choice in `.planning/`, `.codex/`, the vault, templates, or any other repository artifact.

## GSD Workflow Preservation
- Preserve the existing GSD workflow model.
- Keep these capabilities intact:
  - `$gsd-new-project`
  - `$gsd-map-codebase`
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

## State And Output Contract
- Keep [`.planning/STATE.md`](./.planning/STATE.md) current, concise, and operational after planning, execution, and verification.
- Keep milestone and phase names explicit in state so an orchestrator can resume without guessing.
- Planning, execution, and verification outputs must include explicit `Phase Status` and `Milestone Status` lines.
- Each completed GSD step must end with a minimal, directly usable `Next-Step Prompt` when another GSD step is needed.
- Long-form templates belong under [`.planning/templates/`](./.planning/templates/), not in this file.
