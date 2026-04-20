# Generated AGENTS Fragment: Node.js Backend Service

Use this as a source template when the current project selects `backend-nodejs-service`.
Do not activate it globally in the blueprint.

## Node.js Backend Baseline
- Target an Active LTS or Maintenance LTS Node.js release unless the spec explicitly documents a different constraint.
- Use explicit module-system markers in `package.json` and file extensions where needed. Do not rely on accidental module detection.
- Keep request handlers and job entrypoints thin. Delegate business logic to feature or core modules.
- Do not put blocking synchronous filesystem, crypto, compression, or large CPU work on request paths.
- Read configuration from `process.env` through one config boundary. Keep environment variable names in `UPPER_SNAKE_CASE`.
- Use `package.json` scripts as the stable command surface for `dev`, `test`, `lint`, `build`, `typecheck`, and `start`.
- Prefer `node:test` as the default testing baseline when the repo does not already standardize on another runner.
- Normalize transport errors at the boundary. Do not rely on `uncaughtException` as a normal recovery strategy.

## Overlay: `authoring_mode=javascript-esm`
- Use `import` and `export`.
- Keep `"type": "module"` explicit in `package.json`.
- Avoid introducing a compile step unless another selected variant requires it.

## Overlay: `authoring_mode=typescript-node-next`
- Keep TypeScript module settings aligned with Node behavior.
- Run typecheck as a default verification command.
- Prefer explicit types at public boundaries and adapter interfaces.

## Overlay: `authoring_mode=commonjs-compat`
- Use `require` and `module.exports` consistently.
- Avoid mixed module syntax without a documented interoperability reason.

## Overlay: `service_architecture=feature-first-layered`
- Organize by business feature first.
- Keep route, service, and repository code separated inside each feature.
- Treat shared modules as truly shared, not as a dumping ground.

## Overlay: `service_architecture=strict-layered`
- Preserve directional dependencies between transport, application, domain, and data layers.
- Do not skip layers for convenience.

## Overlay: `service_architecture=hexagonal`
- Keep framework, database, and queue clients in adapters.
- Keep core business logic free from HTTP and persistence types.
- Use ports only where a real boundary exists.

## Overlay: `http_framework=fastify`
- Prefer route schemas for validation and response serialization.
- Keep Fastify decorators and plugins at the transport edge.
- Treat schemas as application code and review them like code.

## Overlay: `http_framework=express`
- Keep middleware chains short and explicit.
- Handle errors close to the failure site or normalize them at the HTTP boundary.
- Avoid synchronous APIs inside request handlers and middleware.

## Overlay: `repo_shape=npm-workspaces-monorepo`
- Use workspace-aware commands when running lint, test, or build.
- Respect package boundaries; do not use workspaces as a substitute for module discipline.
