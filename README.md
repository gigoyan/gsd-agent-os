# GSD

## Overview
GSD is a repository-local workflow package for running project work through structured planning, execution, verification, and handoff. It combines:
- a root operating contract in `AGENTS.md`
- live planning files in `PROJECT.md` and `.planning/`
- reusable skills in `.agents/skills/`
- reusable templates in `.planning/templates/`

## Purpose
Its main purpose is to keep project work explicit, reviewable, and resumable instead of relying on hidden chat context or ad hoc notes.

## Main Functionality
- Bootstraps a new project with starter planning files through `$gsd-new-project`
- Maps an existing codebase into `.planning/CODEBASE_MAP.md` through `$gsd-map-codebase`
- Plans non-trivial work as milestones and phases through `$gsd-plan-milestone`
- Executes and verifies planned work through `$gsd-execute-phase` and `$gsd-verify-phase`
- Supports small bounded work through `$gsd-quick-task`
- Supports milestone orchestration through `$gsd-run-milestone`
- Supports narrow memory lookup, vault bootstrap, and later session-save follow-up through the corresponding skills

## Intake Routes
- Use the shared contract in `.planning/templates/intake-routing-and-evidence-contract.md` for intake classification, evidence statuses, UI-option defaults, serious deep-mapping intent, and the cleanup permission gate.
- Start from `placeholder_bootstrap` for new or placeholder repos, `document_first_intake` when supplied materials can answer key questions, `existing_project_mapping` for factual repo onboarding, `explicit_stack_selection` when the user asks to choose the stack, and `partial_maturity_continuation` when artifacts already exist but are unevenly mature.
- Treat `Confirmed`, `Suggested`, and `Unknown` as shared evidence labels across intake, mapping, stack selection, planning, and verification.
- Use UI options whenever the next user input can reasonably be expressed as structured choices or confirmations.
- Treat serious deep-mapping requests as transformation-oriented work, not lightweight mapping.
- For proactive bootstrap and document-first extraction details, use `.planning/templates/document-first-intake-reference.md` together with `$gsd-new-project`.

## Workflow Paths
| Need | Start Here | Notes |
| --- | --- | --- |
| New or placeholder repo | `$gsd-new-project` | Route through `placeholder_bootstrap` first and create or refresh the bootstrap and later Spec-First artifacts in order. |
| Large notes, docs, or other supplied materials | `$gsd-new-project` | Use `document_first_intake` to extract known facts before asking more questions, and keep extracted inputs labeled as `Confirmed`, `Suggested`, or `Unknown`. |
| Existing repo onboarding or factual repo understanding | `$gsd-map-codebase` | Use lightweight mapping when the goal is a grounded repo map, not transformation planning. |
| Explicit stack choice request | `$gsd-select-stack` | Stack selection is a valid entry path when the user explicitly asks for it, but it still feeds the normal Spec-First flow before milestone planning or implementation. |
| Unevenly mature planning artifacts | `$gsd-new-project` | Use `partial_maturity_continuation` and continue from the highest valid readiness point instead of restarting from placeholders. |
| Modernization, major refactor, upgrade, or migration-oriented understanding | `$gsd-map-codebase`, then `gsd-deep-map-codebase` or `$gsd-plan-milestone` when the intent is serious | Treat this as serious deep mapping: produce transformation-ready understanding, keep it factual, and route serious follow-on work to a large structured mapping milestone instead of implementation. |

## How It Works
- `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `.planning/CODEBASE_MAP.md` are the live project surfaces.
- `.planning/templates/` provides starter templates for bootstrap files and later Spec-First artifacts such as the Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact.
- Non-trivial work follows a Spec-First path before implementation: Project Idea Document -> Technical Specification -> stack selection/configuration package -> milestone planning -> execution -> verification.
- State and roadmap files track active work; when nothing is active, they stay reset.

## Using It in a New Project
1. Copy this GSD package into the new repository.
2. Keep the placeholder planning files in place.
3. Route intake before asking questions: use `placeholder_bootstrap` for sparse repos, `document_first_intake` when the user already has substantial notes or docs, and `partial_maturity_continuation` when some artifacts exist but are incomplete.
4. Run `$gsd-new-project` to replace the placeholders in `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md`, or to continue from the highest valid readiness point instead of restarting earlier artifacts.
5. When the user already supplied substantial source material, extract known facts into the appropriate bootstrap or Spec-First artifact surfaces first and label each captured input as `Confirmed`, `Suggested`, or `Unknown`.
6. Ask only residual intake questions after extraction, and present them as UI options whenever the answer space can be structured.
7. Create the Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact from the templates when the work becomes non-trivial.
8. Use `$gsd-plan-milestone` to start milestone-based work only after the governing readiness artifacts are current.

## Using It in an Existing Project
1. Copy this GSD package into the repository.
2. Decide whether the request is lightweight mapping or serious deep mapping before you start.
3. Run `$gsd-map-codebase` to replace `.planning/CODEBASE_MAP.md` with a grounded map of the repo.
4. Keep lightweight mapping focused on factual repo understanding, seams, and current structure.
5. Treat modernization, large refactor, upgrade, or stack-migration understanding as serious deep mapping; keep it transformation-ready and factual, and route the next step to a large structured mapping milestone rather than implementation.
6. If the user explicitly asks to choose the stack, use `$gsd-select-stack` once the project is ready for that decision instead of burying stack choice inside mapping.
7. Backfill or refresh `PROJECT.md` and the planning files as needed.
8. If the repo has unevenly mature planning artifacts but still belongs to bootstrap, continue from the highest valid readiness point rather than restarting from placeholders.
9. If the project does not yet have a current Project Idea Document and Technical Specification, create them before non-trivial milestone work.
10. Use `$gsd-plan-milestone` once the readiness artifacts are sufficiently current.

## Notes / Limitations
- This repo is a workflow package, not an application runtime.
- Some behavior is instruction-driven rather than enforced by executable code.
- `.codex` generation is described, but concrete project-local `.codex` files are not shipped here.
- Vault behavior depends on the external project-local vault arrangement described in `.planning/templates/vault-operating-spec.md`.
- Temporary blueprint-improvement milestone scaffolding must remain until final verification passes and the user explicitly approves cleanup.
