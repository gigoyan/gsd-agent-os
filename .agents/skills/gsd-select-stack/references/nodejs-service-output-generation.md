# Node.js Service Output Generation

Use this reference only when the selected backend profile is `backend-nodejs-service`.

## Source Files

Load these files in this order:
1. [`.agents/stack-profiles/backend/nodejs-service/profile.toml`](../../../../.agents/stack-profiles/backend/nodejs-service/profile.toml)
2. [`.agents/stack-profiles/backend/nodejs-service/assets/output-manifest.toml`](../../../../.agents/stack-profiles/backend/nodejs-service/assets/output-manifest.toml)
3. [`.agents/stack-profiles/backend/nodejs-service/assets/generated-agents-fragment.md`](../../../../.agents/stack-profiles/backend/nodejs-service/assets/generated-agents-fragment.md)
4. [`.agents/stack-profiles/backend/nodejs-service/assets/generated-skills-manifest.md`](../../../../.agents/stack-profiles/backend/nodejs-service/assets/generated-skills-manifest.md)
5. [`.agents/stack-profiles/backend/nodejs-service/assets/project-structure-examples.md`](../../../../.agents/stack-profiles/backend/nodejs-service/assets/project-structure-examples.md)

## Selection Rules

- Ask `authoring_mode` first because it affects commands, module rules, and generated role guidance.
- Ask `service_architecture` next because it affects structure, boundaries, and review checklists.
- Ask `http_framework` only when the project exposes HTTP APIs or the Technical Specification leaves that surface in scope.
- Ask `repo_shape` after the service shape is clear, because a single package remains the recommended default until the spec proves multiple packages or deployables are needed.
- Use repo evidence to skip questions for existing projects whenever the repo clearly proves the current choice and the user is not asking to change it.

## Example Usage Rules

- If the option's `example` field is enough, use it directly in short explanatory text.
- If the user still needs help, use the matching section from `project-structure-examples.md`.
- Keep examples compact. Do not paste long code listings into the stack-selection artifact.

## Project-Local Output Rules

The output manifest defines the reusable source templates for:
- `AGENTS.md` Node.js backend fragments
- `.codex/config.toml`
- `.codex/agents/backend-implementer.toml`
- `.codex/agents/backend-reviewer.toml`
- `.codex/agents/backend-debugger.toml`
- `.codex/agents/api-framework-specialist.toml` when the HTTP framework is `fastify` or `express`

When generating those files:
- Fill placeholders from the selected option set and the current project artifact.
- Preserve the baseline Node.js backend rules from `generated-agents-fragment.md`.
- Add only the overlays that match the selected options.
- Keep the generated reviewers read-only unless the project explicitly needs a writable review role.
- Keep `agents.max_depth = 1` unless the current project explicitly justifies deeper delegation.

## Verification Rules

- Verify that generated commands match the selected authoring mode and repo shape.
- Verify that the selected framework role is omitted when `http_framework=node-core-http`.
- Verify that the generated role instructions reference the current project artifact surfaces, not the reusable blueprint files, as the runtime source of truth.
