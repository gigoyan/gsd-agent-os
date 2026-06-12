# Agent Runtime Adapter Contract

## Purpose

This contract defines how the runtime-neutral GSD core is projected into specific coding-agent runtimes.

GSD has one core workflow. Runtime adapters provide the physical instruction, skill, agent, settings, and tool configuration surfaces required by each supported runtime.

## Supported Runtime IDs

- `codex`
- `claude_code`
- `both`

## Runtime-Neutral Core Artifacts

These artifacts are runtime-neutral source-of-truth surfaces for workflow behavior:

- `AGENTS.md`
- `PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/CODEBASE_MAP.md`
- `.planning/CONTEXT_INDEX.md`
- `.planning/milestones/**`
- `.planning/phases/**`
- `.planning/verification/**`
- `.planning/templates/**`
- `.agents/skills/**`
- `.agents/stack-profiles/**`
- `.gsd/blueprint-manifest.json`

## Codex Runtime Adapter

Codex runtime surfaces include:

- `AGENTS.md`
- `.agents/skills/**/SKILL.md`
- `.agents/skills/**/agents/openai.yaml`
- `.codex/config.toml`
- `.codex/agents/*.toml`

Codex-specific instructions may mention:

- Codex child-agent operations
- Codex sandbox/model/MCP configuration
- Codex skill configuration
- `.codex/**`

`.agents/skills/**` remains canonical reusable GSD skill source, not generated project-local output.

## Claude Code Runtime Adapter

Claude Code runtime surfaces include:

- `CLAUDE.md`
- `.claude/settings.json`
- `.claude/agents/*.md`
- `.claude/skills/**/SKILL.md`
- optional `.claude/rules/**`
- optional `.claude/hooks/**`

Claude-specific instructions may mention:

- Claude Code project memory/instruction loading
- Claude Code project settings
- Claude Code subagents
- Claude Code skills
- Claude Code hooks/rules

`.claude/skills/**` is a generated/projected runtime surface unless explicitly classified otherwise.

In Claude Code, the projected skill directory name is the skill name: each projected GSD skill is invocable by the user as `/<skill-name>` and by the model through the Skill tool.
Every `$gsd-<name>` reference in runtime-neutral GSD artifacts resolves in Claude Code to the projected project skill `gsd-<name>`.
Keeping `.claude/skills/**` projections current is what keeps the Claude Code slash-command surface working; the projections are refreshed by the runtime adapter generation/repair workflow and by the Claude Runtime Projection Refresh step of blueprint sync.

## Claude Runtime Auto-Repair

`.agents/skills/**/SKILL.md` remains the canonical reusable source for GSD skills.
`.claude/skills/**/SKILL.md` remains the generated/project-local Claude Code runtime projection.

Missing `.claude/**` files are a repairable runtime-surface condition, not a reason to silently bypass the Claude adapter.
Before executing a non-trivial GSD task, Claude Code should check for the required Claude runtime surfaces:

- `.claude/settings.json`
- `.claude/skills/**/SKILL.md`
- `.claude/agents/*.md`

If the requested GSD skill is missing under `.claude/skills/**`, but the canonical skill exists under `.agents/skills/<skill-name>/SKILL.md`, Claude Code should run the Claude Code runtime adapter repair/generation workflow before manually reading `.agents/skills/**`.
After repair/generation, Claude Code should re-check `.claude/skills/**` and continue with the projected Claude skill when available.
If repair is blocked, Claude Code must report the blocker and may fall back to canonical `.agents/skills/**` only for the current task.

Repair must be conservative.
It may generate missing `.claude/settings.json`, `.claude/agents/*.md`, and `.claude/skills/**/SKILL.md` files from canonical GSD sources and approved runtime templates.
A skills-only repair (`--skills-only`) projects only `.claude/skills/**` and is the preferred minimal repair when the goal is restoring the Claude Code skill surface.
Existing different `.claude/**` files must not be overwritten unless repair is explicitly run with `--force`.
Generated `.claude/**` files remain `generated_project_local` outputs and are not blueprint truth.

## Source-Of-Truth Rule

Do not maintain separate Codex and Claude versions of the GSD workflow manually.

Canonical reusable sources remain:

- `.agents/skills/**/SKILL.md` for GSD skills
- `.agents/stack-profiles/**` for stack profiles
- `.planning/templates/**` for reusable contracts and starter surfaces

## Runtime Output Ownership

Generated runtime outputs are project-local. Blueprint sync must not copy them from the blueprint source or treat them as blueprint truth.

Generated project-local outputs include:

- `.codex/**`
- `.claude/settings.json`
- `.claude/agents/**`
- `.claude/skills/**`
- `.claude/rules/**`
- `.claude/hooks/**`

`.claude/skills/**` GSD projections are deterministic derived outputs of the project's canonical `.agents/skills/**`. Blueprint sync may regenerate them in the target through the approval-covered Claude Runtime Projection Refresh step so the Claude Code skill surface stays current after canonical skills change; the regenerated files remain generated project-local outputs.

`CLAUDE.md` is not generated_project_local. It is a bootstrap-then-managed-block project-facing runtime adapter surface because it may contain reusable guidance and project-owned local content.

## Delegation Invariant

Generic delegated-agent behavior is governed by [delegated-agent-contract.md](delegated-agent-contract.md). Runtime adapters must preserve that contract when projecting Codex or Claude Code agent surfaces.

## Hooks Policy

Hooks are not generated by default.

Generate hooks only when a selected project or runtime adapter explicitly requires deterministic lifecycle behavior that model instructions cannot reliably enforce.

Acceptable future hook uses include:

- protecting generated runtime adapter files from accidental edits
- running deterministic formatting after writes
- injecting compact runtime context after compaction
- blocking dangerous commands or protected file access

## Adapter Validation

A runtime adapter is valid only when:

- core GSD artifacts remain runtime-neutral
- Codex-specific content is isolated to Codex adapter sections or files
- Claude-specific content is isolated to Claude Code adapter sections or files
- generated project-local files are not treated as blueprint truth
- sync and export rules preserve project runtime files
