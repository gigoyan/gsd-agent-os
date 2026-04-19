# Stack Selection And Configuration Package Template

Use this template after a Project Idea Document and Technical Specification are sufficiently current.
Keep the reusable GSD generic: record concrete choices for the current project, not for the package itself.

## Purpose
- Select the project stack in a structured way.
- Capture the inputs needed to generate the current project's configuration package after selection is complete.
- Do not ship prefilled `.codex/config.toml` or `.codex/agents/*.toml` as part of a reusable GSD package; generate them only when the current project is ready.

## Readiness Gate
- Related Project Idea Document:
- Related Technical Specification:
- Readiness statement:
  - Confirm the problem, flows, constraints, and architecture direction are clear enough to make stack choices deliberately.

## Decision Summary
- Project name:
- Decision owner:
- Decision date:
- Deployment or operating context:
- Key non-negotiable constraints:

## Stack Domains
Record the selected option for each domain.
Use `Other` when the common options do not fit, then explain the choice and constraints.

### Frontend Or Client Surface
- Options: Web SPA, SSR web app, mobile app, desktop app, API-only, CLI, Other
- Selected option:
- Notes:

### Backend Or Server Runtime
- Options: Node.js, Python, Go, JVM, .NET, serverless platform, no dedicated backend, Other
- Selected option:
- Notes:

### Data Storage
- Options: PostgreSQL, MySQL, SQLite, document store, key-value store, object storage only, no durable store, Other
- Selected option:
- Notes:

### Auth And Identity
- Options: First-party auth, external IdP, enterprise SSO, magic link, no auth, Other
- Selected option:
- Notes:

### Integrations And Messaging
- Options: REST APIs, GraphQL, webhooks, queues, cron or jobs, event bus, none, Other
- Selected option:
- Notes:

### Hosting And Delivery
- Options: Cloud VM, managed platform, serverless, edge platform, on-prem, hybrid, Other
- Selected option:
- Notes:

### Observability And Operations
- Options: Hosted monitoring, self-hosted monitoring, basic logs only, Other
- Selected option:
- Notes:

## Cross-Cutting Constraints
- Security and compliance constraints:
- Cost constraints:
- Team familiarity or staffing constraints:
- Performance or latency constraints:
- Vendor or portability constraints:

## Configuration Package Inputs
Capture the inputs required for project-local configuration generation once stack selection is complete.

- Target runtime environments:
- Secrets and environment variable categories:
- Local development expectations:
- CI or automation expectations:
- Default delegated child-agent model: `gpt-5.4`
- Default delegated child-agent reasoning effort:
- Required agent roles or workflow specializations:
- Review or approval constraints:
- Any project-local toolchain requirements:

## Project-Local `.codex` Generation Checklist
Use this only after the stack domains and configuration-package inputs above are complete.

- Confirm generation happens inside the current project's local runtime copy, not inside a reusable source package.
- Confirm the selected stack, runtime environments, and review constraints are current enough to generate project-local `.codex/config.toml` and `.codex/agents/*.toml`.
- When the current project uses delegated child agents, explicitly set the child model in the generated TOML configuration to `gpt-5.4` unless the current project intentionally overrides it.
- Generate only the project-local files the current project actually needs; do not create placeholder roles or unsupported config fields.
- Keep generated role prompts and permissions aligned with bounded-child orchestration and conservative reviewer defaults unless the current project explicitly overrides them.
- If schema details are needed, verify them narrowly from official Codex or OpenAI guidance at generation time.
- Review generated files against the current Project Idea Document, Technical Specification, and this completed stack-selection artifact before adoption.

## Project-Local Output Rule
- Generate `.codex/config.toml` and `.codex/agents/*.toml` only after the stack decisions above are complete.
- Generate those files only inside the current project's local runtime copy.
- Do not treat `.codex` as the main blueprint documentation surface or as durable memory.

## Open Questions
- Remaining decision gaps:
- Research still needed:
- Risks introduced by the selected stack:
- Follow-up actions before implementation:
