---
name: gsd-run-milestone
description: Orchestrate an entire active milestone from the root session by delegating each GSD step to bounded sub-agents until the milestone is explicitly complete.
---

# GSD Run Milestone

Use the root session as a milestone orchestrator.
This skill is for user-requested milestone automation where the main session should coordinate the full planning -> execution -> verification loop across multiple phases without doing the phase work itself.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), and the active milestone or phase file named in state.
2. Determine the correct immediate GSD action from state and artifacts:
   - no active milestone or no active phase for a needed milestone step: `$gsd-plan-milestone`
   - active phase ready to build: `$gsd-execute-phase`
   - active phase implemented and awaiting review: `$gsd-verify-phase`
3. Choose the child role from the immediate GSD step plus the current phase domain and selected stack context already established by repo-local planning artifacts. Keep that role choice root-owned, stack-agnostic at the blueprint level, and constrained to one bounded delegated step.
4. Spawn exactly one bounded sub-agent for that step. The root session should pass only the minimal prompt and required file references, keep `fork_context: false` by default, set `reasoning_effort: "medium"` on the spawn unless the user explicitly overrides it, wait for the result, and not perform the delegated work itself. If the root session needs prior durable context to route correctly, it may request a narrow `gsd-memory-lookup` context pack before spawning, but it still remains the only orchestrator.
5. Read the child result and route only from explicit response signals:
   - `Phase Status`
   - `Milestone Status`
   - `Next-Step Prompt`
6. Continue spawning one next sub-agent at a time while `Milestone Status` is `in_progress`. If a child result or stale state requires durable context to route safely, refresh the narrow memory context pack before the next loop; do not infer routing from memory alone.
7. Stop only when a child result explicitly reports `Milestone Status: completed`, or when the child result says no automatic next-step prompt applies and the next action is genuinely unclear.

## Rules
- This skill requires an explicit user request for subagent-driven milestone automation.
- Keep the root session as manager. Do not let child agents recursively fan out unless the environment is intentionally configured for deeper delegation.
- Keep the root session at high reasoning for milestone orchestration. Do not inherit high reasoning into sub-agents by default.
- For every planning, execution, and verification child, call `spawn_agent(..., reasoning_effort="medium")` unless the user explicitly asks for a different child reasoning level.
- Use `fork_context: false` for child spawns unless the delegated step truly cannot proceed without full thread history.
- Pass only the minimum step-specific instructions and artifact references needed for the delegated skill. Do not hand the child the full milestone loop responsibility.
- The root session must never tell a child to spawn, wait for, route to, or manage other agents.
- Root-owned role selection may use the current phase domain and selected stack context from planning artifacts, but children must not reinterpret that context to widen scope or self-select a different role.
- Memory lookup is advisory for routing context only; it never replaces explicit `Phase Status`, `Milestone Status`, or `Next-Step Prompt` text.
- If a child tries to orchestrate, delegate further, wait for nonexistent agents, or continue into a later GSD step, interrupt that child, discard its routing attempt, and respawn a fresh bounded child with a narrower prompt.
- Do not infer milestone completion from a missing `Next-Step Prompt` alone. Milestone completion must be explicit.
- If a child returns `partial` or `fail`, use its `Next-Step Prompt` only when the recovery action is explicit. Otherwise stop and surface the ambiguity.
- Re-read [`.planning/STATE.md`](../../../.planning/STATE.md) between loops when a child reports artifact updates, so the orchestrator does not route from stale context.
- Keep conservative reviewer defaults intact. Review-oriented roles such as `qa_reviewer` remain read-only by default, challenge implementation quality and validation adequacy, and must not silently edit artifacts or broaden into implementation unless a later project-local override explicitly permits it.
- The user's selected conversation language never carries into child prompts or child outputs; every delegated child interaction remains English-only.

## Child Prompt Contract
Every delegated child prompt should make the child role explicit. Use wording equivalent to all of the following:
- You are a delegated child agent, not the milestone orchestrator.
- Execute exactly one GSD step: planning, execution, or verification.
- Do not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- Do not perform any later GSD step, even if the next action seems obvious.
- Keep the child prompt and all child outputs in English, even if the main agent is speaking to the user in another language.
- Do not inherit or mirror the user's selected conversation language in child prompts or child outputs.
- When your assigned step is complete, return `Phase Status`, `Milestone Status`, and `Next-Step Prompt`, then stop immediately.

## Required Outputs
- A milestone-level summary from the root session showing each delegated step, the final milestone status, and any blocking ambiguity if the loop could not continue automatically.
- No direct implementation, planning, or verification work performed by the root session beyond delegation, routing, and final reporting.

## Completion Check
- The root session delegated each GSD step to sub-agents instead of doing the step work itself.
- The loop continued across multiple phases when the milestone stayed in progress.
- Child-role selection stayed root-owned, bounded, and derived from the current phase domain plus selected stack context rather than child autonomy.
- The loop stopped only on explicit milestone completion or explicit routing ambiguity.
