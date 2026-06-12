# GSD Operating Contract

## Purpose
- This file contains always-on GSD routing and safety invariants only.
- Detailed workflows live in `.agents/skills/**/SKILL.md`.
- Detailed contracts and templates live in `.planning/templates/**`.

## Runtime / Memory Boundary
- The repository is the live workflow-control layer: instructions, skills, planning, execution, validation, and handoff.
- The vault is the durable memory layer only.
- Runtime adapter outputs are configuration/convenience surfaces, not memory.

## Required Reading
- Before non-trivial GSD work, read `PROJECT.md`, `.planning/STATE.md`, and the active milestone and active phase named in state, when present.
- Read governing Project Idea Document, Technical Specification, or stack-selection/configuration-package artifacts when referenced by state, milestone, phase, or the user request.
- Read `.planning/CONTEXT_INDEX.md` before broad repository scanning when it exists and is current.

## Skill Routing
- `$gsd-<name>` denotes the canonical GSD skill `gsd-<name>`; invoke it through the active runtime's skill surface (Codex skills from `.agents/skills/**`, Claude Code projected skills from `.claude/skills/**`).
- New/sparse project or bootstrap refresh -> `$gsd-new-project`.
- Existing/stale/unknown repo reality, serious mapping, or context-index repair -> `$gsd-map-codebase`.
- Stack selection -> `$gsd-select-stack`.
- Milestone planning -> `$gsd-plan-milestone`.
- Active phase execution -> `$gsd-execute-phase`.
- Active phase verification -> `$gsd-verify-phase`.
- Full active milestone orchestration -> `$gsd-run-milestone`.
- Small bounded task that does not need milestone ceremony -> `$gsd-quick-task`.
- Full UI discovery, browser-backed UI exploration, role/page/flow UI capture, user-story capture from UI, full app crawl, form/action inventory, UI QA coverage, or "go through the app" requests -> `$gsd-ui-discovery-orchestrator`.
- Source-material registration, organization, classification, or durable project evidence intake from repository file/directory paths -> `$gsd-register-source-materials`.
- Blueprint install/update/audit -> `$gsd-sync-blueprint`; do not sync manually.
- Durable memory lookup -> `$gsd-memory-lookup`.
- Durable memory writeback -> `$gsd-session-save`.
- Vault scaffold initialization/repair -> `$gsd-vault-bootstrap`.

## Natural-Language Interaction Boundary
- Users request outcomes in natural language; internal commands, flags, validators, goal IDs, artifact paths, and script names are agent execution details.
- Agents must translate user requests into the required GSD skill, command, validation, and artifact-inspection steps without asking the user to run those steps manually when the agent can run them.
- Ask the user only for user-only blockers: target URL, credentials or manual login/MFA, safe data policy, permission for destructive/payment/send actions, missing local software, OS/browser permission prompts, or environment access the agent cannot provide.
- When commands are needed, run them internally and report the result in natural language with the important artifact references.

## Spec-First Gate
- Non-trivial implementation requires sufficient current spec context before milestone planning or execution.
- Existing projects with unknown or stale repo reality must be mapped before implementation planning.
- Blueprint-self-improvement may use active milestone, active phase, and prior verification artifacts as governing context instead of project-specific product specs.

## Mapping And Context Routing
- `$gsd-map-codebase` is the only mapping workflow.
- Mapping must not create milestones or phases.
- `.planning/CODEBASE_MAP.md` records current system reality.
- `.planning/CONTEXT_INDEX.md` is the repo-local navigation guide for future coding agents.
- Use current `.planning/CONTEXT_INDEX.md` before broad scanning.
- If routing is stale or missing, update it when small and evidence-supported, or record a `$gsd-map-codebase` refresh candidate in `.planning/STATE.md`.

## Vault Namespace Boundary
- Each repository owns exactly one vault namespace: `projects/<vault-project-id>/`.
- Resolve `<vault-project-id>` from `PROJECT.md`; if missing, derive it from the repository root folder name.
- Never read or write sibling project namespaces.
- Never write durable notes directly under the shared vault root.
- Do not store absolute vault-root paths in repository artifacts.
- Full vault rules live in `.planning/templates/vault-operating-spec.md`.

## Runtime Adapter Boundary
- GSD core workflow is runtime-neutral.
- Codex runtime surfaces may include `AGENTS.md`, `.agents/skills/**`, and `.codex/**`.
- Claude Code runtime surfaces may include `CLAUDE.md` and `.claude/**`.
- Generated runtime outputs are not blueprint truth and not durable memory.
- Full adapter rules live in `.planning/templates/agent-runtime-adapter-contract.md` when present.

## State And Handoff Contract
- Keep `.planning/STATE.md` concise and operational.
- Planning, execution, and verification outputs must include explicit `Phase Status` and `Milestone Status` when routing depends on them.
- Emit a minimal `Next-Step Prompt` only when another GSD step is needed.
- Treat `Next-Step Prompt` as response-only handoff text unless the user explicitly asks to write it into an artifact.

## Tool Capability Boundary
- Before repository commands, check `.planning/tool-capabilities.md` when present.
- If a command is recorded as blocked, unavailable, incompatible, or unsafe, use the recorded fallback.
- Record new environment/tool availability failures once with the approved fallback.

## Conversation Language
- Main-agent conversation language is project-local runtime preference.
- If unset, continue in the current conversation language.
- Change it only on explicit user request or unmistakable intent.
- Store it only in the project-owned `GSD-PROJECT: local-settings` block.
- Internal GSD artifacts, control labels, prompts, state, docs, and delegated-agent outputs stay in English.
