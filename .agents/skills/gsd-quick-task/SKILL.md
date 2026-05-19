---
name: gsd-quick-task
description: Handle a small, low-risk, bounded task inside the Codex-native GSD workflow without creating a full milestone. Use for narrow fixes, simple config changes, or single-file adjustments that can be planned, executed, and verified in one short pass.
---

# GSD Quick Task

Use the fast path for truly small work.
This skill is for tasks that do not justify a milestone but still need a visible scope check, lightweight validation, and a state update.

## Workflow
1. Read [`.planning/STATE.md`](../../../.planning/STATE.md) and understand the current active work.
2. Confirm the requested task is small, low-risk, and unlikely to spill across multiple phases.
3. Read `.planning/CONTEXT_INDEX.md` when available and use the relevant routing row or module card to identify the smallest start-here path and validation path. If the task is so explicit that the file is already known, record that no broader routing was needed.
4. Use [`.planning/templates/quick-task-template.md`](../../../.planning/templates/quick-task-template.md) as a lightweight planning aid if the task needs a short written record.
5. Define the smallest meaningful behavior slice and the targeted test or check to update first. If the task depends on prior durable context, request a narrow `gsd-memory-lookup` context pack first. If test-first is impractical, record the reason and nearest safeguard before implementation.
6. Update the targeted test or check first when practical, run proportional validation, implement the minimum change needed, and log the outcome in [`.planning/STATE.md`](../../../.planning/STATE.md). If the task produces durable insight, record the later `gsd-session-save` follow-up as `candidate` or `none` rather than writing durable memory here.
7. If the task expands, stop and redirect to `$gsd-plan-milestone`.

## Quick Path Criteria
- Fits in one focused implementation pass.
- Has clear local impact.
- Does not require milestone-level acceptance criteria.
- Has an obvious validation seam for a targeted test or check, or a clear documented exception.
- Does not hide architecture changes or broad refactors.

## Redirect Criteria
- Cross-file or cross-subsystem change.
- New feature with ambiguous scope.
- Work that needs explicit acceptance criteria or staged verification.
- Any task that stops feeling small once repo inspection begins.

## Required Outputs
- Small task implemented and validated.
- Test-first validation step recorded, or an explicit exception with the nearest safeguard.
- Context-routing result recorded: routing used, explicit file known, or refresh follow-up candidate.
- [`.planning/STATE.md`](../../../.planning/STATE.md) updated with:
  - task summary
  - checks run
  - outcome
  - escalation if the task was redirected

## Rules
- Keep the process lightweight, but do not skip validation entirely.
- Default to test-first for behavior changes that are reasonably testable.
- If the task competes with active milestone work, note that interaction in [`.planning/STATE.md`](../../../.planning/STATE.md).
- Use memory lookup only when needed to resolve prior durable context; otherwise stay repo-local.
- Quick tasks should still use the context index when the relevant file or validation path is not already explicit.
- Do not let the quick path become broad repo discovery. If routing is unclear or the task expands, redirect to `$gsd-plan-milestone` or `$gsd-refresh-context-index` as appropriate.
- Record whether a context-index refresh follow-up is warranted or `none`.
- Do not write durable memory from this skill.
- At the end of the quick task, explicitly record whether a later `gsd-session-save` follow-up is warranted or `none`.
- Quick tasks are not a loophole for silent code-first changes. If test-first is impractical, state why and use the closest realistic safeguard, such as a regression check, smoke check, validation command, or manual verification note.
- End the response with a compact `Next-Step Prompt` only when a clear immediate GSD follow-up exists; otherwise say briefly that no next-step prompt is needed.
- Treat the `Next-Step Prompt` as response-only handoff text. Do not write it into phase, milestone, verification, roadmap, or state artifacts unless the user explicitly asks for that artifact content.
- Use the quick-task template only when it adds clarity. Do not over-document trivial work.

## Completion Check
- The task stayed bounded.
- Validation was run and recorded, with targeted test-first evidence or a justified exception.
- [`.planning/STATE.md`](../../../.planning/STATE.md) reflects the result or explicit escalation.
