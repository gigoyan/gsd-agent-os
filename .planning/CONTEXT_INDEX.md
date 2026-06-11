# Context Index Template

Use this template for `.planning/CONTEXT_INDEX.md`.
This artifact is the primary coding-agent navigation guide for a repository. It is not a full architecture document, not durable vault memory, and not a replacement for source inspection.

Keep it compact, task-routing oriented, and evidence-based. Prefer paths, symbols, canonical examples, commands, validation routes, and do-not-touch boundaries over narrative explanation.

## Purpose
- Help coding agents choose the smallest useful context for a task.
- Tell planning, execution, verification, quick-task, mapping, and milestone orchestration skills where to start.
- Capture how agents should work safely in this repo.
- Reduce repeated repository discovery.
- Keep repository navigation guidance repo-local and evidence-based.

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
  - Tool capability evidence:
  - Other:
- Staleness triggers:
  - major folder restructuring
  - new module, service, package, or app boundary
  - changed build/test/lint/run commands
  - changed framework/runtime/tooling
  - changed validation strategy
  - changed architecture or dependency direction
  - changed runtime, data, persistence, or integration behavior
  - repeated agent over-scanning in the same area
  - failed task because routing guidance was missing or wrong

## Agent Context Routing Contract
- Start from the matching `Task Routing Matrix` row before broad repository search.
- Inspect the row's `Start here` paths before `Then inspect` paths.
- Copy canonical examples before inventing syntax, naming, error-handling, validation, test, or extension patterns.
- Prefer targeted validation from the matching task row, module card, or validation matrix before broader checks.
- Avoid generated, vendor, dependency, cache, build-output, unrelated, and fragile areas unless the task explicitly requires them.
- Verify important routing claims against source files before changing behavior.
- Update this file when a routing row, module card, convention, symbol/API, canonical example, validation path, command note, or avoid boundary is small, local, and directly evidenced by the task.
- Record a precise `$gsd-map-codebase` unified mapping refresh candidate in `.planning/STATE.md` when the needed routing correction is broad, uncertain, cross-cutting, or based on thin evidence.
- Do not use this file to bypass active milestone, phase, specification, acceptance, source-traceability, or verification criteria.
- Do not store this file or its contents in the Obsidian vault.

## Project Navigation Summary
- Repository type:
- Primary language/runtime:
- Main application entry points:
- Main configuration surfaces:
- Main test surfaces:
- Main build/lint/typecheck surfaces:
- Main reusable surfaces and extension points:
- Main performance-sensitive paths:
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
- Canonical examples:
- Reusable surfaces:
- Extension points:
- Performance-sensitive paths:
- Hot-path risks:
- Key symbols/APIs:
- Avoid touching unless:
- Evidence status:

## Symbol And API Map

| Area | File | Symbol/API | Responsibility | Used by | Change notes | Evidence status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | Unknown |

## Convention Cards

### `<convention name>`
- Applies to:
- Canonical examples:
- Required syntax:
- Naming:
- Error handling:
- Validation:
- Tests:
- Anti-examples / avoid:
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

## Change Impact Routing

| Change observed | Required routing artifact action | Evidence status |
| --- | --- | --- |
| Module ownership/path changes | Update the matching `CONTEXT_INDEX.md` task row and module card. | Unknown |
| Validation command changes | Update the validation matrix and update `.planning/tool-capabilities.md` if a command failed due to environment/tool availability. | Unknown |
| Architecture or dependency direction changes | Update `.planning/CODEBASE_MAP.md`. | Unknown |
| Runtime, data, persistence, or integration behavior changes | Update `.planning/CODEBASE_MAP.md`. | Unknown |
| Reusable implementation pattern changes | Update the matching `CONTEXT_INDEX.md` convention card and record a `gsd-session-save` candidate in `.planning/STATE.md` when the pattern has durable reuse value. | Unknown |
| Reusable surface, extension point, or performance-sensitive route changes | Update the matching task row, module card, convention card, or validation matrix. | Unknown |
| Durable decision or debugging insight emerges | Record a `gsd-session-save` candidate in `.planning/STATE.md`; do not write vault memory from planning, execution, verification, quick-task, or mapping unless the session-save skill is explicitly invoked. | Unknown |
| Route is missing, stale, or misleading | Update `CONTEXT_INDEX.md` when local and evidence-supported; otherwise record a precise `$gsd-map-codebase` unified mapping refresh candidate in `.planning/STATE.md`. | Unknown |

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
- Recommended unified mapping trigger:
