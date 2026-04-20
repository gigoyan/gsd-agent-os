# Generated Skills Manifest: Node.js Backend Service

These are dormant generation targets, not active repo skills yet.

## Core Skills

### `node-backend-implementation`
- Purpose:
  - implement backend changes in the selected Node.js style
- Inputs:
  - selected authoring mode
  - selected architecture option
  - selected framework option
  - active project spec artifacts
- Should enforce:
  - thin transport handlers
  - explicit validation boundaries
  - non-blocking request-path rules
  - selected module-system conventions

### `node-backend-testing`
- Purpose:
  - add or update targeted tests for the Node.js backend
- Should enforce:
  - `node:test` by default unless the project already standardized elsewhere
  - test placement and naming that mirrors selected structure
  - coverage of failure paths and boundary validation

### `node-backend-debugging`
- Purpose:
  - diagnose backend failures, performance issues, environment problems, and event-loop blocking risks
- Should enforce:
  - local-only inspector guidance
  - environment-variable boundary checks
  - event-loop and sync-API review

## Variant-Specific Skills

### `node-fastify-routes`
- Generate only when `http_framework=fastify`
- Should enforce:
  - schema-aware route definitions
  - plugin and decorator boundaries
  - structured logging usage

### `node-express-routes`
- Generate only when `http_framework=express`
- Should enforce:
  - router-per-feature conventions
  - middleware error propagation
  - no sync APIs on request paths

### `node-typescript-boundaries`
- Generate only when `authoring_mode=typescript-node-next`
- Should enforce:
  - NodeNext-compatible imports
  - public boundary typing
  - typecheck command discipline

## Recommended Project-Local Agent Roles
- `backend-implementer`
- `backend-reviewer`
- `backend-debugger`
- `api-framework-specialist`

These should be generated later into project-local `.codex` outputs only after stack selection is complete.
Use `output-manifest.toml` and the `project-local-*.template.toml` files in this folder as the source templates for those generated role files.
