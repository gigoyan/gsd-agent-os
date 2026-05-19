# State Template

## Current Status
- Status:
- Current milestone:
- Milestone status:
- Current phase:
- Phase status:
- Latest verification:
- Memory-aware context pack:
  - If used, it must come from `projects/<vault-project-id>/`.
  - Do not store the vault project ID here; `PROJECT.md` owns that value.
- Context index:
  - Status: `missing` | `placeholder` | `current` | `partial` | `stale`
  - Last consulted:
  - Refresh follow-up: `none` | `candidate: <why>`
- Durable-memory follow-up:
  - Record `candidate: <note kind + why>` or `none`.
  - Do not store the durable content itself in state.

## Open Risks
- List active planning or delivery risks.

## Next Action
- Record the immediate next GSD action or note that no automatic next step applies.
- If durable context is needed for routing, refresh it through `gsd-memory-lookup`; do not store it in state.

## Notes
- Keep this file concise. It is the primary handoff artifact between sessions and milestone orchestrator runs.
