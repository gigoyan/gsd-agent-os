# Node.js Backend Profile Sources

Last reviewed: `2026-04-19`

This profile is intentionally grounded first in official Node.js, npm, TypeScript, Fastify, Express, and ESLint documentation. Architecture variants use established secondary sources where Node.js itself does not prescribe one structure.

## Primary Official Sources

### Node.js releases
- Source: [Node.js Releases](https://nodejs.org/en/about/releases/)
- Key use in profile:
  - Production targets should use Active LTS or Maintenance LTS releases.
  - The exact major version should be rechecked during the profile freshness step instead of hardcoding a branch forever.

### Node.js modules
- Source: [ECMAScript modules](https://nodejs.org/api/esm.html)
- Source: [CommonJS modules](https://nodejs.org/api/modules.html)
- Key use in profile:
  - Node.js supports both ESM and CommonJS.
  - New projects should use explicit module markers instead of relying on auto-detection.
  - ESM is the official JavaScript module standard and is a sound default for new services.

### Node.js test runner
- Source: [node:test](https://nodejs.org/api/test.html)
- Key use in profile:
  - `node:test` is stable.
  - `node --test` can be the default baseline when the project does not already standardize on another runner.
  - Watch mode exists but is still experimental, so it should not be treated as the only local loop.

### Node.js environment variables
- Source: [Environment Variables](https://nodejs.org/api/environment_variables.html)
- Key use in profile:
  - `.env` support is part of Node.js.
  - `process.env` is the configuration boundary.
  - Uppercase underscore variable names are the recommended convention.

### Node.js event-loop safety
- Source: [Don't Block the Event Loop (or the Worker Pool)](https://nodejs.org/learn/asynchronous-work/dont-block-the-event-loop)
- Key use in profile:
  - Node.js services must avoid blocking request paths with CPU-heavy or sync work.
  - This is a first-class architectural constraint for backend design and review.

### npm package model
- Source: [package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json)
- Source: [scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts)
- Source: [workspaces](https://docs.npmjs.com/cli/v7/using-npm/workspaces)
- Key use in profile:
  - `package.json` is the right place for scripts, engines, and workspaces.
  - Workspaces are appropriate only when there are genuinely multiple packages.
  - Scripts are the stable command surface GSD should later generate into project-local outputs.

### TypeScript for Node.js
- Source: [TypeScript modules reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)
- Key use in profile:
  - `node16`, `node18`, `node20`, and `nodenext` model real Node.js module behavior.
  - TypeScript NodeNext mode is the correct curated option when the project chooses TypeScript authoring.

### Fastify
- Source: [Fastify docs](https://fastify.dev/docs/latest/)
- Source: [Validation and Serialization](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/)
- Key use in profile:
  - Fastify is strong when the project wants schema-first HTTP APIs.
  - Response and request schemas are a core part of the framework value proposition.

### Express
- Source: [Basic routing](https://expressjs.com/en/starter/basic-routing.html)
- Source: [Production best practices](https://expressjs.com/en/advanced/best-practice-performance.html)
- Key use in profile:
  - Express remains a viable familiar framework option.
  - The profile uses Express production guidance for error handling, no sync APIs in request paths, and process supervision expectations.

### ESLint
- Source: [Configure ESLint](https://eslint.org/docs/latest/use/configure/)
- Source: [Rules reference](https://eslint.org/docs/latest/rules/)
- Key use in profile:
  - Linting should be configurable rather than hardcoded.
  - The curated baseline can rely on recommended safety rules without pretending there is one universal formatting style.

## Secondary Architecture Sources

These are used because Node.js itself does not define one mandatory service architecture.

### Hexagonal architecture
- Source: [Alistair Cockburn, Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- Key use in profile:
  - Justifies the `hexagonal` variant for adapter-heavy systems.

### Layering principles
- Source: [Martin Fowler, Layering Principles](https://martinfowler.com/bliki/LayeringPrinciples.html)
- Source: [Martin Fowler, Presentation Domain Data Layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
- Key use in profile:
  - Supports the `strict-layered` and `feature-first-layered` options.
  - Especially supports the idea that domain-oriented modules often scale better than only technical top-level layers.

## Freshness-Check Guidance

At stack-selection time, recheck:
- current supported Node.js LTS lines
- any major changes to ESM or CommonJS guidance
- `node:test` capabilities that affect generated commands
- npm scripts and workspaces behavior
- TypeScript NodeNext guidance
- selected framework guidance if the user chooses Fastify or Express

Do not auto-rewrite the reusable profile from search results alone.
If current official guidance materially changes a reusable recommendation, flag the profile for maintainer review.
