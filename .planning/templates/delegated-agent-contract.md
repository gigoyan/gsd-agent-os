# Delegated Agent Contract

## Purpose
Centralize the invariant for any GSD delegated child agent, sub-agent, generated project-local agent, or runtime-specific worker.

## Contract
- The root orchestrator owns delegation, role selection, prompt boundaries, child lifecycle, child result review, and next-step routing.
- A delegated child owns only the assigned slice, role, or child action passed by the root.
- A delegated child must not spawn, delegate to, message, wait for, close, route, manage, or orchestrate other agents.
- A delegated child must not broaden scope, reinterpret its role, or self-select a different task.
- A delegated child must inspect only assigned paths plus directly necessary adjacent files unless the root prompt explicitly authorizes broader inspection.
- A delegated child must preserve evidence status and source traceability passed by the root, including `Confirmed`, `Suggested`, `Unknown`, compact `source_id`, claim IDs, anchors, and registry paths.
- A delegated child must not duplicate source registry rows, copy raw source bodies, or broad-scan raw source-material folders unless the root prompt explicitly cites a narrow file and anchor.
- A delegated child must return only the required output for its assigned slice, include required status or routing fields, and then stop.
- The root must review child output before applying it, routing from it, closing the child, or spawning another child.

## Runtime Translations
- In Codex, delegated children must not call `spawn_agent`, `send_input`, `wait_agent`, or `close_agent`.
- In Claude Code, delegated subagents must not invoke other subagents, agent teams, dynamic workflows, or recursive delegation behavior.
