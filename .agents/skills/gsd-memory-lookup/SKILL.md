---
name: gsd-memory-lookup
description: Retrieve a small project-first context pack and lightly normalize it for the current task. Use when GSD-relevant work starts, the active phase needs context, a milestone handoff needs recent durable memory, or the user explicitly asks for memory lookup.
---

# GSD Memory Lookup

Use this skill for narrow retrieval only.
It does not write durable memory and it does not bootstrap vault structure.

## Source Of Truth
- Apply [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md) for the repository-vs-vault boundary, project namespace resolution, sibling-namespace limits, shared-root write prohibition, exact vault areas, routing rules, and linking expectations. This skill is retrieval-only; durable writes route to `gsd-session-save`.

## Namespace Resolution

Before any lookup:

1. Resolve `<vault-project-id>`:
   - Prefer `PROJECT.md` -> `GSD Vault Project ID`.
   - If missing, derive it from the current repository root folder name for this lookup only.
   - Do not write the derived value from this skill.
2. Scope all retrieval to:

    projects/<vault-project-id>/

3. Treat paths like `00-home/current priorities.md` as:

    projects/<vault-project-id>/00-home/current priorities.md

4. Do not search across sibling project namespaces unless the user explicitly asks for cross-project memory.
5. If the namespace does not exist, return `no project vault scaffold found` and hand off to `gsd-vault-bootstrap`; do not broaden retrieval to the shared vault root.

## Primary Purpose
- Retrieve the smallest useful project-first context pack for the current task.
- Lightly normalize the result so later workflow surfaces can consume it without a vault dump.

## Trigger Conditions
- GSD-relevant work is starting.
- The active phase needs durable-memory context.
- A milestone handoff needs recent memory.
- The user explicitly asks for memory lookup.

## Non-Trigger Conditions
- The session is pure discussion.
- The request is trivial.
- Repo-local context is already sufficient and memory would add no value.
- The user only needs scaffold initialization or durable writeback.

## Input Contract
- Current task.
- Project identifier or repo context.
- Retrieval intent.
- Any explicit scope restrictions, such as phase-only or recent-only.
- Relevant task class, such as planning, architecture change, integration work, debugging, workflow change, or business-rule lookup.
- Active `GSD Vault Project ID` or derived repository folder name.
- Active project namespace: `projects/<vault-project-id>/`.

## Output Contract
- A concise context pack ranked by relevance.
- Source labels or provenance for each retrieved item when available.
- Conflicts or uncertainty surfaced instead of flattened.
- Minimal normalization notes when duplicates or stale items are trimmed.
- The context pack should identify the note area used, such as priorities, atlas, integration, decision, debugging, pattern, business, or session context.

## Retrieval Order
All paths below are relative to `projects/<vault-project-id>/`.

- Use the smallest useful project-first retrieval pack in this general order:
  1. `00-home/current priorities.md` when current durable focus or blockers matter.
  2. The directly relevant fixed atlas note when stable architecture, stack, database, or deployment context matters.
  3. The directly relevant `knowledge/` note type:
     - `knowledge/integrations/` for external-system behavior
     - `knowledge/decisions/` for durable choices
     - `knowledge/debugging/` for recurring root causes or recovery patterns
     - `knowledge/patterns/` for reusable implementation or workflow approaches
     - `knowledge/business/` for domain rules that materially affect implementation
  4. The most recent linked session note only when recent session continuity materially helps the current task.
  5. `00-home/index.md` only as a navigation aid when the direct target note is not already known.
- Prefer one or two directly related durable notes over broad historical retrieval.
- Do not pull broad vault dumps, unrelated old sessions, or entire folders.

## Boundary Limits
- No durable writes.
- No broad archival dump.
- No note creation.
- No bootstrap actions.
- No attempt to manage other memory responsibilities.
- Memory lookup does not replace `.planning/CONTEXT_INDEX.md`. Use memory for durable context, and use the context index for repo navigation and task routing.

## Handoff Rules
- Keep the output small enough for a workflow surface to consume directly.
- Suppress automatic retrieval for pure discussion unless the user explicitly asks for memory.
- If repo-local planning or code context is already sufficient, return no vault retrieval rather than padding the context pack.
- If the lookup reveals durable-value work, hand off to `gsd-session-save` rather than writing here.
