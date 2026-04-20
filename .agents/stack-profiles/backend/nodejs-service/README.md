# Node.js Backend Service Profile

This package is a reusable stack profile for backend projects built on Node.js.

It is dormant blueprint data, not an active skill.
Use it after the current project has:
- a current Project Idea Document
- a current Technical Specification
- a stack-selection step that chooses this profile

## Files
- `profile.toml`: machine-readable stack profile and variant options
- `profile.toml` also carries reusable recommendation sets and convention overlays that the selection step may surface as `Suggested`
- `references/sources.md`: source-backed rationale and freshness-check guidance
- `assets/generated-agents-fragment.md`: template guidance for generated `AGENTS.md` output
- `assets/project-structure-examples.md`: example layouts and code-style examples for user selection
- `assets/generated-skills-manifest.md`: recommended generated skills and role surfaces
- `assets/output-manifest.toml`: machine-readable map from selected options to project-local output targets
- `assets/project-local-*.template.toml`: source templates for generated project-local `.codex` config and custom-agent files

## Scope
- Backend services, APIs, webhooks, and background jobs running on Node.js
- Not a frontend profile
- Not a database profile
- Not a deployment profile by itself

## Baseline Intent
- Keep Node.js runtime guidance grounded in official Node.js, npm, and TypeScript docs
- Treat framework-specific recommendations as variant choices, not hardcoded defaults
- Prefer explicit module markers, explicit quality gates, and non-blocking request paths
- Use profile-backed recommendation bundles only as visible `Suggested` guidance that can be accepted, overridden, or deferred during stack selection
