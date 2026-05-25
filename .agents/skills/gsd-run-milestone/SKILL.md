---
name: gsd-run-milestone
description: Orchestrate an entire active milestone from the root session by delegating each GSD step to bounded sub-agents until the milestone is explicitly complete.
---

# GSD Run Milestone

Use the root session as a milestone orchestrator.
This skill is for user-requested milestone automation where the main session should coordinate the full planning -> execution -> verification-plus-next-phase-planning loop across multiple phases without doing the phase work itself.

## Workflow
1. Read [PROJECT.md](../../../PROJECT.md), [`.planning/STATE.md`](../../../.planning/STATE.md), and the active milestone or phase file named in state.
2. Determine the correct immediate delegated action from state and artifacts:
   - no active milestone or no active phase for a needed milestone step: spawn one planning child for `$gsd-plan-milestone`
   - active phase ready to build: spawn one execution child for `$gsd-execute-phase`
   - active phase implemented and awaiting review: spawn one verification-and-next-phase-planning child
3. For each active phase, use at most two children in sequence:
   - one execution child that performs `$gsd-execute-phase` only
   - one verification-and-next-phase-planning child that verifies the active phase using `$gsd-verify-phase` rules, and only after a passing verification may create the next bounded phase in the same active milestone using `$gsd-plan-milestone` rules
4. Choose the child role from the immediate delegated action plus the current phase domain and selected stack context already established by repo-local planning artifacts. Keep that role choice root-owned, stack-agnostic at the blueprint level, and constrained to the assigned planning, execution, or verification-and-next-phase-planning child step.
5. Read `.planning/CONTEXT_INDEX.md` when available and pass only the relevant context-routing section, routing row, module card, or phase `Context Routing` summary to the delegated child. Do not pass the full repository map unless the delegated step genuinely requires it.
6. Resolve child spawn settings for the current run before spawning.

   Default child spawn settings:
   - model: latest available supported child-agent model in the current runtime
   - reasoning_effort: medium
   - fork_context: false unless the delegated step truly requires full thread history

   Invocation override:
   - If the user request that invoked `$gsd-run-milestone` specifies a child-agent model, use that model for this run.
   - If the user request specifies child-agent reasoning effort, use that reasoning effort for this run.
   - If the override is scoped to a child type, apply it only to that child type.
   - Otherwise apply the override to all child spawns in this run.
7. Spawn exactly one bounded sub-agent for the next child action. The root session should pass only the minimal prompt and required file references, use the resolved child spawn settings, wait for the result, and not perform the delegated work itself. If the root session needs prior durable context to route correctly, it may request a narrow `gsd-memory-lookup` context pack before spawning, but it still remains the only orchestrator.
8. After a child returns, the root orchestrator must read the result, close the completed child with `close_agent`, and only then spawn the next child if the milestone should continue. Route only from explicit response signals:
   - `Phase Status`
   - `Milestone Status`
   - `Next-Step Prompt`
9. Continue spawning the next child action while `Milestone Status` is `in_progress`: execution for the active phase, then verification-and-next-phase-planning for that same phase. If a child result or stale state requires durable context to route safely, refresh the narrow memory context pack before the next loop; do not infer routing from memory alone.
10. Stop only when a child result explicitly reports `Milestone Status: completed`, or when the child result says no automatic next-step prompt applies and the next action is genuinely unclear.

## Rules
- This skill requires an explicit user request for subagent-driven milestone automation.
- Keep the root session as manager. Do not let child agents recursively fan out unless the environment is intentionally configured for deeper delegation.
- Keep the root session at high reasoning for milestone orchestration. Do not inherit high reasoning into sub-agents by default.
- For every planning, execution, and verification-and-next-phase-planning child, use the latest available supported child-agent model in the current runtime and `reasoning_effort: "medium"` by default.
- If the user invocation that triggered `$gsd-run-milestone` explicitly specifies a child-agent model or child-agent reasoning effort, use that override for this run. If the override is scoped to a child type, apply it only to that child type; otherwise apply it to every child spawned during the run.
- Use `fork_context: false` for child spawns unless the delegated step truly cannot proceed without full thread history.
- Pass only the minimum step-specific instructions and artifact references needed for the delegated skill. Do not hand the child the full milestone loop responsibility.
- The root orchestrator should use `.planning/CONTEXT_INDEX.md` to keep child prompts narrow.
- Child prompts should include the active phase, parent milestone, and only the relevant context-routing guidance needed for the assigned step.
- Do not hand child agents the full codebase map or broad repo-discovery task when the context index already identifies start-here paths and validation routes.
- If a child reports broad scanning caused by missing or stale routing guidance, the root should route to `$gsd-map-codebase` for a targeted unified mapping refresh when that is the clear next recovery action.
- The root session must never tell a child to spawn, wait for, route to, or manage other agents.
- After a child returns, the root orchestrator must read `Phase Status`, `Milestone Status`, and `Next-Step Prompt`, close the completed child with `close_agent`, and only then decide whether to spawn the next child.
- The verification-and-next-phase-planning child is the only allowed composite child. It may create the next bounded phase only when verification passes and the milestone remains incomplete.
- The composite child must not create the next phase on `fail`, `partial`, blocked verification, or completed milestone.
- The composite child must never execute the newly created phase, continue the milestone loop, or choose another delegated step after creating the next phase.
- Root-owned role selection may use the current phase domain and selected stack context from planning artifacts, but children must not reinterpret that context to widen scope or self-select a different role.
- Memory lookup is advisory for routing context only; it never replaces explicit `Phase Status`, `Milestone Status`, or `Next-Step Prompt` text.
- When the root session needs prior durable context to route safely, it may request `gsd-memory-lookup`, but the lookup must be scoped to the active repository namespace:

    projects/<vault-project-id>/

- The root orchestrator must not let child agents search the shared vault root or sibling project namespaces unless the user explicitly requested cross-project memory work.
- If a child tries to orchestrate, delegate further, wait for nonexistent agents, execute after verification, or continue the milestone loop, interrupt that child, discard its routing attempt, and respawn a fresh bounded child with a narrower prompt.
- Do not infer milestone completion from a missing `Next-Step Prompt` alone. Milestone completion must be explicit.
- If a child returns `partial` or `fail`, use its `Next-Step Prompt` only when the recovery action is explicit. Otherwise stop and surface the ambiguity.
- Re-read [`.planning/STATE.md`](../../../.planning/STATE.md) between loops when a child reports artifact updates, so the orchestrator does not route from stale context.
- Keep conservative reviewer defaults intact. Review-oriented roles such as `qa_reviewer` remain read-only by default, challenge implementation quality and validation adequacy, and must not silently edit artifacts or broaden into implementation unless a later project-local override explicitly permits it.

## Child Prompt Contract
Every delegated child prompt should make the child role explicit. Use wording equivalent to all of the following:
- You are a delegated child agent, not the milestone orchestrator.
- Perform only the assigned child action: planning, execution, or the explicit `$gsd-run-milestone` verification-and-next-phase-planning composite step.
- Do not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- If assigned execution, do not perform verification or planning.
- If assigned the verification-and-next-phase-planning composite step, first verify the active phase using `$gsd-verify-phase` rules. If verification passes and the milestone is incomplete, create exactly one next bounded phase in the same active milestone using `$gsd-plan-milestone` rules, then stop.
- If assigned the composite step, do not create the next phase on `fail`, `partial`, blocked verification, or completed milestone.
- If assigned the composite step, do not execute the newly created phase, continue the loop, spawn agents, or route beyond the single next phase creation.
- Use the provided context-routing guidance first. Do not broaden into unrelated repository areas unless necessary, and explain any deviation.
- Child prompts and child outputs must remain English, following the conversation-language policy defined in `AGENTS.md`.
- When your assigned step is complete, return `Phase Status`, `Milestone Status`, and `Next-Step Prompt` when another step applies, then stop immediately.

## Required Outputs
- A milestone-level summary from the root session showing each delegated step, the final milestone status, and any blocking ambiguity if the loop could not continue automatically.
- No direct implementation, planning, or verification work performed by the root session beyond delegation, routing, and final reporting.

## Completion Check
- The root session delegated each GSD step to sub-agents instead of doing the step work itself.
- The loop continued across multiple phases when the milestone stayed in progress.
- Child-role selection stayed root-owned, bounded, and derived from the current phase domain plus selected stack context rather than child autonomy.
- The root session used context-routing guidance to keep child prompts bounded when the context index was available.
- The loop stopped only on explicit milestone completion or explicit routing ambiguity.
