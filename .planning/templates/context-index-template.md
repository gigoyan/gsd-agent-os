# Context Index Template

Use this template for `.planning/CONTEXT_INDEX.md`.
This artifact is a compact routing guide for agents. It is not a full architecture document and it is not durable vault memory.

## Purpose
- Help Codex choose the smallest useful context for a task.
- Reduce repeated repository discovery.
- Tell planning, execution, verification, quick-task, and orchestration skills where to start.
- Keep repository navigation guidance evidence-based and task-shaped.

## Status
- Status: `placeholder` | `current` | `stale` | `partial`
- Last refreshed:
- Refreshed by:
- Source basis:
  - `PROJECT.md`:
  - `.planning/CODEBASE_MAP.md`:
  - `.planning/REQUIREMENTS.md`:
  - Project Idea Document:
  - Technical Specification:
  - Stack-selection/configuration package:
  - Repo inspection:
  - Other:
- Staleness triggers:
  - major folder restructuring
  - new module or service boundary
  - changed build/test/lint commands
  - changed framework/runtime/tooling
  - changed validation strategy
  - repeated agent over-scanning in the same area
  - failed task because routing guidance was missing or wrong

## Use Rule
- Before broad repo scanning, read this file and choose the narrowest relevant route.
- Treat this file as routing guidance, not source-of-truth code evidence.
- Verify important claims against actual files before changing behavior.
- If this file conflicts with repo evidence, repo evidence wins and this file should be refreshed.
- Do not use this file to bypass the active milestone, phase, specification, or verification criteria.
- Do not store this file or its contents in the Obsidian vault.

## Project Navigation Summary
- Repository type:
- Primary language/runtime:
- Main application entry points:
- Main configuration surfaces:
- Main test surfaces:
- Main build/lint/typecheck surfaces:
- Main data/persistence surfaces:
- Main external integration surfaces:
- Main generated or vendor areas to avoid:

## Task Routing Matrix

| Task type | Start here | Then inspect | Usually changes | Validation path | Avoid unless needed | Evidence status |
| --- | --- | --- | --- | --- | --- | --- |
| Add or change API endpoint |  |  |  |  |  | Unknown |
| Change business/domain logic |  |  |  |  |  | Unknown |
| Change data model or persistence |  |  |  |  |  | Unknown |
| Change authentication or authorization |  |  |  |  |  | Unknown |
| Change external integration |  |  |  |  |  | Unknown |
| Change UI or client behavior |  |  |  |  |  | Unknown |
| Change configuration or environment behavior |  |  |  |  |  | Unknown |
| Fix bug or regression |  |  |  |  |  | Unknown |
| Add or update tests |  |  |  |  |  | Unknown |
| Documentation-only change |  |  |  |  |  | Unknown |

## Module Routing Cards

### `<module or area name>`
- Responsibility:
- Main paths:
- Entry points:
- Depends on:
- Used by:
- Common change types:
- Local validation:
- Related tests:
- Related configuration:
- Avoid touching unless:
- Evidence status:

## Validation Matrix

| Area | Fast targeted check | Broader check | When to run | Evidence status |
| --- | --- | --- | --- | --- |
|  |  |  |  | Unknown |

## Search Recipes

### Find endpoint or route owner
- Start:
- Then:
- Validation:
- Avoid:

### Find business rule owner
- Start:
- Then:
- Validation:
- Avoid:

### Find data model usage
- Start:
- Then:
- Validation:
- Avoid:

### Find integration behavior
- Start:
- Then:
- Validation:
- Avoid:

### Find test coverage for a behavior
- Start:
- Then:
- Validation:
- Avoid:

## Do-Not-Scan Boundaries
- Do not inspect generated files unless the task concerns generated output or build artifacts.
- Do not inspect vendor, dependency, cache, or build-output folders unless the task explicitly concerns those areas.
- Do not inspect unrelated frontend areas for backend-only tasks unless the API contract or user-facing behavior requires it.
- Do not inspect unrelated backend areas for UI-only tasks unless data contracts, permissions, or integration behavior require it.
- Do not run full-suite validation before targeted validation unless the phase, milestone, or repo convention requires it.

## GSD Infrastructure Boundary
- In normal application repositories, treat `.agents/skills/**`, `.planning/templates/**`, `.gsd/**`, and reusable GSD docs as workflow infrastructure, not application code.
- Do not route application implementation tasks into GSD infrastructure files unless the task explicitly concerns GSD itself.
- If the active task is to update GSD itself, switch routing to blueprint-maintenance mode and use the blueprint manifest.

## Tool Capability Notes
- Before running repository commands, check `.planning/tool-capabilities.md` if it exists.
- If a command is recorded as blocked, unavailable, non-executable, incompatible, or unsafe, use the approved fallback.
- If a new command fails because of environment/tool availability, record the failure once in `.planning/tool-capabilities.md` with the approved fallback.

## Staleness And Refresh Notes
- Last structural change considered:
- Last command-surface change considered:
- Known stale sections:
- Recommended refresh trigger:
