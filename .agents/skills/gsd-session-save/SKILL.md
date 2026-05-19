---
name: gsd-session-save
description: Decide whether current work has durable value and, if so, write a bounded session or decision artifact. Use when meaningful planning, execution, verification, or handoff occurred and future continuity benefits from durable memory.
---

# GSD Session Save

Use this skill for durable writeback only.
It must respect the canonical `do not write` default.

## Source Of Truth
- Use [`.planning/templates/vault-operating-spec.md`](../../../.planning/templates/vault-operating-spec.md) for exact save rules, note routing, naming rules, update-vs-create behavior, and linking requirements.
- Use [`.planning/templates/vault-note-templates/`](../../../.planning/templates/vault-note-templates/) for note payload structure.

## Namespace Resolution

Before any durable write:

1. Resolve `<vault-project-id>`:
   - Prefer `PROJECT.md` -> `GSD Vault Project ID`.
   - If missing, derive it from the current repository root folder name.
   - If the value is newly derived, require that `PROJECT.md` can be updated or that the user explicitly approves the derived namespace before writing durable memory.
2. Confirm that the active project namespace exists:

    projects/<vault-project-id>/

3. Write only inside that namespace.
4. Do not create or update notes directly under the shared vault root.
5. Do not write into sibling project namespaces.
6. If the namespace does not exist, skip the write and hand off to `gsd-vault-bootstrap`.

## Primary Purpose
- Decide whether the current work has durable value.
- Write a bounded session, decision, or debugging artifact only when the value is likely to matter later.

## Trigger Conditions
- Meaningful planning, execution, verification, or handoff occurred.
- A recurring decision or debugging insight needs retention.
- Current priorities materially changed.
- Future continuity would benefit from a durable record.

## Non-Trigger Conditions
- The exchange was trivial or exploratory.
- The user only asked for clarification.
- The work is already fully captured in repo-local active state.
- The lookup only needs to be remembered temporarily.

## Input Contract
- Session summary.
- Durable-value signal.
- Target note type, such as session, decision, or debugging.
- Relevant links or references.
- Any known vault path or existing note that may already own the same durable truth.

## Output Contract
- Write-or-skip decision.
- Deterministic note type classification.
- Deterministic note path or fixed-note update target when a write occurs.
- Bounded note payload when writing.
- Required wiki links to add when writing.
- Short rationale when the action is not obvious.

## Pre-Write Questions
- Before writing, ask:
  - Is this durable?
  - Will future work benefit from finding this again?
  - Is this better in the vault than in repo workflow files?
  - Is this specific enough to retrieve later?
- If the answer is no, skip the write and say so explicitly.

## Deterministic Classification
- Route the durable item to exactly one primary owner under `projects/<vault-project-id>/`:
  - current durable priorities -> update `00-home/current priorities.md`
  - architecture summary or durable architecture change -> update `atlas/project architecture.md`
  - stack summary or durable tooling/runtime change -> update `atlas/tech stack.md`
  - database structure or DB rule -> update `atlas/database.md`
  - deployment or infrastructure rule -> update `atlas/deployment.md`
  - external system behavior -> `knowledge/integrations/<statement-style title>.md`
  - durable technical or workflow decision -> `knowledge/decisions/<statement-style title>.md`
  - recurring bug, root cause, or reusable fix pattern -> `knowledge/debugging/<statement-style title>.md`
  - reusable coding or workflow pattern -> `knowledge/patterns/<statement-style title>.md`
  - business or domain rule that affects implementation -> `knowledge/business/<statement-style title>.md`
  - meaningful session or handoff summary -> `sessions/YYYY-MM-DD HHmm - <statement-style outcome>.md`
  - temporary uncategorized capture -> `inbox/YYYY-MM-DD HHmm - <short capture>.md`
- Do not invent alternate categories or store repo workflow artifacts in the vault.

## Update Vs Create Rules
- Fixed home and atlas notes are single-owner notes. Always update the existing file path instead of creating duplicates.
- For `knowledge/` notes:
  - update an existing note if it already owns the same durable truth
  - create a new note only when the durable fact is genuinely distinct
  - prefer one owner per truth and avoid overlapping duplicates
- For `sessions/`:
  - create a new session note for each meaningful stopping point
  - continue updating the same session note only while the same stopping point is still being formed
- For `inbox/`:
  - use only for temporary uncategorized captures that will later be promoted or removed

## Naming And Linking Rules
- Dynamic durable notes must use statement-style titles as filenames.
- Session filenames must use `YYYY-MM-DD HHmm - <statement-style outcome>.md`.
- Inbox filenames must use `YYYY-MM-DD HHmm - <short capture>.md`.
- Required wiki links:
  - session notes link to the decision, debugging, pattern, integration, business, or atlas notes created or updated
  - decision notes link to affected architecture or integration notes
  - debugging notes link to related integration or architecture notes
  - pattern notes link to related decision, architecture, or integration notes
  - `00-home/current priorities.md` links to the notes that explain why the priorities matter
  - update `00-home/index.md` only when the durable memory surface expanded enough to need a new anchor

## Minimum End-Of-Session Save Behavior
- At a meaningful stopping point:
  - create or update a session note if continuity needs it
  - update `00-home/current priorities.md` if durable priorities changed
  - write a decision note if a real durable decision was made
  - write a debugging note if a real root cause or fix pattern was found
  - update `00-home/index.md` only if navigation would otherwise degrade
- If none of those are justified, write nothing.

## Boundary Limits
- No retrieval expansion.
- No scaffold changes.
- No attempt to manage other memory responsibilities.
- No default write when the durable-value signal is weak.
- Do not save blueprint sync lock details into the vault. Save only durable decisions or patterns if the sync model itself changes in a way future sessions need to remember.
- Do not save `.planning/CONTEXT_INDEX.md` content into the vault. If routing knowledge represents a durable reusable pattern beyond the current repository, save only the durable pattern through the normal vault routing rules, not the repo-local context index itself.

## Handoff Rules
- If the work does not justify a durable note, say so and stop.
- If multiple note types seem plausible, choose the smallest durable owner that preserves one owner for each truth and add links rather than duplicating content.
- If the write decision depends on missing context, request only the minimum context needed to decide.
