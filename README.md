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

## How It Works
- `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `.planning/CODEBASE_MAP.md` are the live project surfaces.
- `.planning/templates/` provides starter templates for bootstrap files and later Spec-First artifacts such as the Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact.
- Non-trivial work follows a Spec-First path before implementation: Project Idea Document -> Technical Specification -> stack selection/configuration package -> milestone planning -> execution -> verification.
- State and roadmap files track active work; when nothing is active, they stay reset.

## Using It in a New Project
1. Copy this GSD package into the new repository.
2. Keep the placeholder planning files in place.
3. Run `$gsd-new-project` to replace the placeholders in `PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md`.
4. Create the Project Idea Document, Technical Specification, and stack-selection/configuration-package artifact from the templates when the work becomes non-trivial.
5. Use `$gsd-plan-milestone` to start milestone-based work.

## Using It in an Existing Project
1. Copy this GSD package into the repository.
2. Run `$gsd-map-codebase` to replace `.planning/CODEBASE_MAP.md` with a grounded map of the repo.
3. Backfill or refresh `PROJECT.md` and the planning files as needed.
4. If the project does not yet have a current Project Idea Document and Technical Specification, create them before non-trivial milestone work.
5. Use `$gsd-plan-milestone` once the readiness artifacts are sufficiently current.

## Notes / Limitations
- This repo is a workflow package, not an application runtime.
- Some behavior is instruction-driven rather than enforced by executable code.
- `.codex` generation is described, but concrete project-local `.codex` files are not shipped here.
- Vault behavior depends on the external project-local vault arrangement described in `.planning/templates/vault-operating-spec.md`.
