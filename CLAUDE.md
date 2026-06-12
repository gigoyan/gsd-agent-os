@AGENTS.md

<!-- GSD-BLUEPRINT:START claude-runtime-adapter -->
# Claude Code Runtime Adapter

Use GSD as the governing coding-agent workflow for this repository.

## GSD Skill Surface

- Canonical GSD skills live under `.agents/skills/**/SKILL.md` and remain the runtime-neutral source of truth.
- Claude Code runs GSD skills from the projected copies under `.claude/skills/<skill-name>/SKILL.md`.
- Every `$gsd-<name>` reference in `AGENTS.md`, GSD skills, templates, or user requests means the Claude Code project skill `gsd-<name>`: invoke it with the Skill tool, exactly as if the user typed `/gsd-<name>`.
- Users may invoke any projected GSD skill directly by typing `/gsd-<name>` in chat; treat such input as an explicit skill invocation request.
- Claude Code project subagents live under `.claude/agents/**`.

## Request Routing

- For every new user request, apply the Skill Routing rules in `AGENTS.md` before improvising a workflow.
- When a route matches, invoke the matching `gsd-*` skill through the Skill tool instead of re-implementing its workflow inline.
- When no route matches, handle the request directly while keeping the GSD operating contract in force (required reading, spec-first gate, state and handoff rules).
- High-risk skills (`gsd-sync-blueprint`, `gsd-export-blueprint-package`, `gsd-export-project-context`) are explicit-invocation-only: run them only when the user clearly asks for that operation.

## Runtime Surface Repair

Before executing a non-trivial GSD task, check whether the Claude Code runtime surface exists:

- `.claude/settings.json`
- `.claude/skills/**/SKILL.md`
- `.claude/agents/*.md`

If a requested GSD skill is missing under `.claude/skills/**`, but the canonical source exists under `.agents/skills/<skill-name>/SKILL.md`, refresh the projection before falling back to manual reading:

```bash
python3 .agents/skills/gsd-generate-runtime-adapters/scripts/generate_runtime_adapters.py --target claude_code --repair --skills-only
```

After repair/generation, re-check `.claude/skills/**` and continue using the projected Claude skill.
Skills projected mid-session may become invocable only in the next session; in that case read the projected `.claude/skills/<skill-name>/SKILL.md` and follow it directly for the current task.
Do not pass `--force` without explicit user approval, and do not hand-edit projected `.claude/skills/**` files; change canonical `.agents/skills/**` sources and re-project instead.
If repair is blocked, report the blocker and fall back to reading canonical `.agents/skills/**` only for the current task.

## Runtime Behavior Rules

Do not assume Codex-specific tool names or runtime behavior exist.

When a GSD instruction refers to delegated-agent behavior, apply the runtime-neutral rule: delegated children must not spawn, delegate to, message, wait for, close, or orchestrate other agents.

Read full adapter rules when the task requires runtime-specific detail:

- `.planning/templates/agent-runtime-adapter-contract.md`
<!-- GSD-BLUEPRINT:END claude-runtime-adapter -->

<!-- GSD-PROJECT:START claude-local-settings -->
## Project-Local Claude Code Notes

- Add project-specific Claude Code guidance here.
<!-- GSD-PROJECT:END claude-local-settings -->
