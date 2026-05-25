# Stack Selection And Configuration Package Template

Use this template after a Project Idea Document is current and the project has reached stack-selection readiness.
If the user explicitly requests stack selection before bootstrap or spec artifacts exist, use this template anyway and mark which upstream artifacts still need to be completed afterward.
Keep the reusable GSD generic: record concrete choices for the current project, not for the package itself.
Use [`.planning/templates/stack-profile-contract.md`](./stack-profile-contract.md) as the contract for reusable stack profiles and variant options.

## Purpose
- Select the project stack in a structured way.
- Capture the inputs needed to generate the current project's configuration package after selection is complete.
- Do not ship prefilled `.codex/config.toml` or `.codex/agents/*.toml` as part of a reusable GSD package; generate them only when the current project is ready.

## Readiness Gate
- Related Project Idea Document:
- Related Technical Specification or draft technical direction:
- Readiness statement:
  - Confirm the problem, primary flows, constraints, and architecture direction are clear enough to make stack choices deliberately.
  - Note whether Technical Specification completion still depends on the selected stack.
  - Note whether stack selection started from an explicit user request before bootstrap artifacts were in place.

## Decision Summary
- Project name:
- Decision owner:
- Decision date:
- Deployment or operating context:
- Key non-negotiable constraints:
- Confirmed facts already proven by repo evidence, supplied material, or explicit user decisions:
- Suggested defaults or recommendations awaiting confirmation:
- Unknown decision gaps or conflicting inputs:

## Stack Profile Resolution
- Selected profile IDs and versions:
- Selected profile package paths:
- Profile-backed recommendation sets reviewed:
- Convention overlays reviewed:
- Deferred freshness follow-on status:
- Official sources reserved for later freshness review:
- Project-local deviations from curated profile defaults:
- Evidence status for the current profile resolution:

## Profile-Backed Recommendations Reviewed
Record each profile-backed recommendation bundle that was surfaced during stack selection.
Keep repo-proven facts `Confirmed`, profile-backed proposals `Suggested`, and unresolved or conflicting choices `Unknown`.

- Recommendation ID:
- Recommendation label:
- Triggering confirmed inputs:
- Suggested axis options:
- Suggested conventions:
- Rationale shown:
- Tradeoffs shown:
- User decision: accepted, overridden, deferred, or not-shown
- Override or deferral note:
- Evidence status:
- Source or rationale:

## Variant Selections
Record each selected variant option with the reason it fits the current project.
Keep repo-proven or user-confirmed choices `Confirmed`, best-fit recommendations `Suggested`, and unresolved axes `Unknown`.

- Axis ID:
- Selected option ID:
- Recommendation source ID, if any:
- Why this fit:
- Tradeoff accepted:
- Example or reference shown to the user:
- Override confirmation note:
- Evidence status:
- Source or rationale:

## Stack Domains
Record the selected option for each domain.
Use `Other` when the common options do not fit, then explain the choice and constraints.

### Frontend Or Client Surface
- Options: Web SPA, SSR web app, mobile app, desktop app, API-only, CLI, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Backend Or Server Runtime
- Options: Node.js, Python, Go, JVM, .NET, serverless platform, no dedicated backend, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Data Storage
- Options: PostgreSQL, MySQL, SQLite, document store, key-value store, object storage only, no durable store, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Auth And Identity
- Options: First-party auth, external IdP, enterprise SSO, magic link, no auth, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Integrations And Messaging
- Options: REST APIs, GraphQL, webhooks, queues, cron or jobs, event bus, none, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Hosting And Delivery
- Options: Cloud VM, managed platform, serverless, edge platform, on-prem, hybrid, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

### Observability And Operations
- Options: Hosted monitoring, self-hosted monitoring, basic logs only, Other
- Selected option:
- Notes:
- Evidence status:
- Source or rationale:

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
- Default delegated child-agent model: latest available supported child-agent model in the current runtime unless the current project explicitly overrides it
- Default delegated child-agent reasoning effort:
- Required agent roles or workflow specializations:
- Generated `AGENTS.md` instruction layers or fragments:
- Generated or enabled skills:
- Generated project-local output files:
- Generated project-local templates or starter assets:
- Review or approval constraints:
- Any project-local toolchain requirements:
- Obsidian MCP mode:
  - `shared-root`
- GSD Vault Project ID:
- GSD Vault Namespace:
- MCP config ownership:
  - The absolute Obsidian vault root is configured outside reusable GSD artifacts.
  - Do not generate one MCP server per project unless the user explicitly overrides the shared-root model.

## Context Index Impact
- Does selected stack change expected structure, commands, validation strategy, generated project-local outputs, or runtime surfaces:
- Context-index action: `none` | `create` | `refresh`
- Recommended `$gsd-map-codebase` unified mapping scope:
- Notes:

## Project-Local `.codex` Generation Checklist
Use this only after the stack domains and configuration-package inputs above are complete.

- Confirm generation happens inside the current project's local runtime copy, not inside a reusable source package.
- Confirm the selected stack, stack-aware Technical Specification, runtime environments, and review constraints are current enough to generate project-local `.codex/config.toml` and `.codex/agents/*.toml`.
- Confirm the selected curated profile manifests and template assets were the sources for generated project-local outputs.
- When delegated child agents are used, rely on the runtime default latest available supported child-agent model unless the current project explicitly selects a concrete child model override. Record explicit project-level overrides in generated project-local configuration.
- Generate only the project-local files the current project actually needs; do not create placeholder roles or unsupported config fields.
- Keep generated role prompts and permissions aligned with bounded-child orchestration and conservative reviewer defaults unless the current project explicitly overrides them.
- If schema details are needed, verify them narrowly from official Codex or OpenAI guidance at generation time.
- Review generated files against the current Project Idea Document, Technical Specification, and this completed stack-selection artifact before adoption.

## Project-Local Output Rule
- Generate `.codex/config.toml` and `.codex/agents/*.toml` only after the stack decisions above and the stack-aware Technical Specification are complete enough to support safe project-local generation.
- Generate those files only inside the current project's local runtime copy.
- Do not treat `.codex` as the main blueprint documentation surface or as durable memory.
- Do not generate project-local `.codex/config.toml` entries that point MCPVault directly to `projects/<vault-project-id>/` when the shared-root model is active. The MCP server should point to the shared Obsidian root; GSD skills must scope reads and writes to the project namespace.

## Open Questions
- Remaining `Unknown` decision gaps:
- `Suggested` defaults or recommendations awaiting confirmation:
- Deferred follow-on work outside active selection, such as freshness review or project-local output generation:
- Risks introduced by the selected stack:
- Follow-up actions before implementation:
