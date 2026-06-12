---
name: gsd-generate-runtime-adapters
description: Generate or safely repair project-local runtime adapter outputs for selected GSD stack profiles. Use when stack selection has captured target runtimes and the next step is to project Codex outputs, Claude Code outputs, or both without treating generated files as blueprint truth, or when Claude Code runtime surfaces are missing, incomplete, or stale enough to prevent skill invocation.
---

# GSD Generate Runtime Adapters

Generate runtime-specific project-local outputs from the current stack-selection/configuration-package artifact and the selected stack profile output manifest.
Also use this skill for conservative Claude Code runtime repair when missing or incomplete `.claude/**` adapter files would otherwise prevent GSD skill invocation.

This skill supports two use cases:

1. Normal generation after stack selection is current.
2. Runtime repair for missing Claude Code adapter files.

Do not use it to choose the stack, change reusable stack-profile truth, update export behavior, or verify a phase.

## Supported Runtime Targets

- `codex`
- `claude_code`
- `both`

`both` expands to `codex` and `claude_code`.

## Workflow

1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), the current stack-selection/configuration-package artifact, and [`.planning/templates/agent-runtime-adapter-contract.md`](../../../.planning/templates/agent-runtime-adapter-contract.md).
2. Read the selected stack profile metadata and output manifest. For the Node.js backend service profile, start with [`.agents/stack-profiles/backend/nodejs-service/assets/output-manifest.toml`](../../../.agents/stack-profiles/backend/nodejs-service/assets/output-manifest.toml).
3. Resolve target runtime(s) from the stack-selection artifact, the user request, or an explicit script argument. Accept only `codex`, `claude_code`, or `both`. Keep `Confirmed`, `Suggested`, and `Unknown` meanings intact:
   - `Confirmed`: explicit user choice, current artifact decision, or repo-proven fact.
   - `Suggested`: profile-backed recommendation that still needs acceptance.
   - `Unknown`: missing or conflicting decision; stop and ask for confirmation before writing outputs.
4. Run a dry run first when practical and inspect the created/updated/skipped/blocked report. Do not write generated runtime outputs until target runtimes, selected profile, output root, and preservation behavior are clear.
5. Generate only project-local runtime adapter outputs:
   - Codex: `.codex/config.toml` and `.codex/agents/*.toml` from the selected profile templates and output-manifest mappings.
   - Claude Code: `.claude/settings.json`, `.claude/agents/*.md`, and `.claude/skills/**/SKILL.md` from selected profile templates plus canonical `.agents/skills/**/SKILL.md` projection rules.
6. Preserve project-owned files and managed blocks:
   - Do not overwrite existing generated runtime files by default when content differs.
   - Report existing different files as `skipped` unless the user explicitly approves replacement.
   - Treat `.codex/**` and generated `.claude/**` as project-local runtime outputs, not blueprint truth.
7. Do not generate root `CLAUDE.md` from stack profile data. `CLAUDE.md` remains governed by the global bootstrap-then-managed-block adapter rule established in the root Claude Code adapter phase.
8. Report all outputs as `created`, `updated`, `skipped`, `blocked`, or `missing_prerequisites`, with a short reason for each skipped or blocked file.
9. If validation uses a temporary output root, remove or ignore that temporary root before handoff. Do not leave generated `.codex/**` or `.claude/**` changes in the repository unless the user explicitly requested generation into the project.

## Claude Runtime Repair

Use repair mode when Claude Code cannot invoke a requested GSD skill from `.claude/skills/**` and the canonical source exists under `.agents/skills/<skill-name>/SKILL.md`.

Repair mode is intentionally conservative:

- Generate missing files.
- Preserve existing different `.claude/**` files unless `--force` is explicitly used.
- Prefer `--dry-run` first when practical.
- Project canonical `.agents/skills/**/SKILL.md` into `.claude/skills/**/SKILL.md` using the Claude skill projection rules below.
- Attempt `.claude/settings.json` and `.claude/agents/*.md` from the selected profile templates when prerequisites exist.
- If stack/profile values or templates are unavailable, still project Claude skills when possible and report settings or agents as `skipped`, `blocked`, or `missing_prerequisites`.
- Do not update root `CLAUDE.md` from the generator.
- Do not treat `.claude/**` as blueprint truth.
- Report created, updated, skipped, blocked, and missing-prerequisite outputs.

Repair command (POSIX shells):

```bash
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target claude_code --repair --dry-run
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target claude_code --repair
```

Repair command (PowerShell):

```powershell
python .agents\skills\gsd-generate-runtime-adapters\scripts\generate_runtime_adapters.py --target claude_code --repair --dry-run
python .agents\skills\gsd-generate-runtime-adapters\scripts\generate_runtime_adapters.py --target claude_code --repair
```

Skills-only refresh (projects `.claude/skills/**` without touching settings or agents):

```bash
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target claude_code --repair --skills-only
```

## Scripted Projection

Use the deterministic helper when available:

```bash
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target both --dry-run
```

```powershell
python .agents\skills\gsd-generate-runtime-adapters\scripts\generate_runtime_adapters.py --target both --dry-run
```

Useful arguments:

- `--target codex|claude_code|both`
- `--profile-assets <path>` defaults to `.agents/stack-profiles/backend/nodejs-service/assets`
- `--output-root <path>` defaults to the repository root
- `--selection-file <path>` reads simple stack-selection values when present
- `--var key=value` supplies explicit render values for template placeholders
- `--force` allows updating existing generated files whose content differs
- `--repair` runs conservative Claude Code runtime-surface repair; supported with `--target claude_code`
- `--skills-only` projects only `.claude/skills/**` from canonical skills and skips settings/agents outputs; supported with `--target claude_code`
- `--skills-root <path>` overrides the canonical skills directory; defaults to `<output-root>/.agents/skills` when present, else `./.agents/skills`
- `--dry-run` reports without writing files
- `--json` emits a machine-readable report

Run target validation without leaving generated runtime output changes in the repository by using a temporary output root:

```bash
tmp="$(mktemp -d)/gsd-runtime-adapters-codex"
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target codex --output-root "$tmp" --var http_framework=fastify
rm -rf "$tmp"
```

```powershell
$tmp = Join-Path $env:TEMP "gsd-runtime-adapters-codex"
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
python .agents\skills\gsd-generate-runtime-adapters\scripts\generate_runtime_adapters.py --target codex --output-root $tmp --var http_framework=fastify
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
```

Repeat for `claude_code` and `both` when validating this workflow.

## Claude Skill Projection Rules

Source:

```text
.agents/skills/<skill-name>/SKILL.md
```

Target:

```text
.claude/skills/<skill-name>/SKILL.md
```

Projection rules:

- Preserve the core workflow content.
- Normalize legacy workflow-name phrases to `GSD coding-agent workflow`.
- Normalize generic Codex child-agent tool-name prohibitions to the runtime-neutral delegation rule.
- Do not copy `.agents/skills/**/agents/openai.yaml`.
- Add Claude Code frontmatter to the projected skill.
- The projected directory name is the Claude Code skill name, so the projected skill is invocable as `/<skill-name>` and through the Skill tool.
- Emit the canonical skill description as a YAML double-quoted scalar so colons and quotes cannot break frontmatter parsing.
- Omit `allowed-tools` for normal skills so orchestrator skills inherit the full runtime tool surface, including delegation and skill-invocation tools.
- Add `disable-model-invocation: true` and append `Invoke explicitly only.` to the description for high-risk generated skills:
  - `gsd-sync-blueprint`
  - `gsd-export-blueprint-package`
  - `gsd-export-project-context`

High-risk frontmatter:

```yaml
---
description: "<canonical skill description> Invoke explicitly only."
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---
```

Normal projected frontmatter:

```yaml
---
description: "<canonical skill description>"
---
```

Read-only projected skills use:

```yaml
---
description: "<canonical skill description>"
allowed-tools: Read, Glob, Grep, Bash
---
```

## Rules

- Generate only project-local runtime adapter outputs.
- Do not classify generated `.codex/**` or generated `.claude/**` as blueprint truth.
- Do not update `AGENTS.md`, root `CLAUDE.md`, export scripts, project-context export files, sync/distribution contracts, flattened generated export files, or vault notes from this skill.
- Do not generate runtime outputs during stack selection; this workflow is the bounded follow-on.
- For normal generation, stop instead of guessing when target runtime, selected profile, or material stack-selection values remain `Unknown`.
- For Claude repair mode, do not require stack-selection values just to project generic GSD skills; report missing agent/settings prerequisites without blocking skill projection when possible.
- Preserve existing project-owned runtime files unless replacement was explicitly approved.

## Completion Check

- Target runtime(s) were resolved as `codex`, `claude_code`, or `both`.
- The selected stack profile output manifest was read.
- A dry-run report was reviewed before writing to the project root.
- Generated outputs were limited to project-local runtime adapter paths.
- Existing project-owned runtime files and managed blocks were preserved or explicitly approved for update.
- The report lists created, updated, and skipped outputs.
- Root `CLAUDE.md` was not generated from stack profile data.
