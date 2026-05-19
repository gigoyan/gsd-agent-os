# Obsidian Vault Operating Spec

## Core Rule
- Repo = how Codex should work here.
- Vault = what Codex should remember over time.
- Use the repo for live workflow control.
- Use the vault for durable memory only.

## Shared MCP Root And Project Namespace

- The Obsidian MCP server points to one shared vault root.
- GSD project memory must live under a project namespace inside that root:

    projects/<vault-project-id>/

- `<vault-project-id>` is resolved from the active repository:
  1. Prefer the confirmed `GSD Vault Project ID` in `PROJECT.md`.
  2. Otherwise derive it from the current repository root folder name.
  3. Preserve the repository folder name except replace filesystem-invalid path characters with `-`.
  4. Stop for user confirmation if the derived namespace appears to belong to a different project.
- Every path in this spec is relative to:

    projects/<vault-project-id>/

- Never store durable project memory directly at the shared vault root.
- Never read or write another project namespace unless the user explicitly requests cross-project memory work.

## Fixed Project Namespace Structure

    projects/<vault-project-id>/
      00-home/
        index.md
        current priorities.md

      atlas/
        project architecture.md
        tech stack.md
        database.md
        deployment.md

      knowledge/
        integrations/
        decisions/
        debugging/
        patterns/
        business/

      sessions/
      inbox/

In the routing rules below, paths such as `00-home/current priorities.md` mean:

    projects/<vault-project-id>/00-home/current priorities.md

## Area Ownership
### `00-home/`
- `index.md`
  - Small navigation note.
  - Links only to high-value anchor notes.
  - Update only when the durable memory surface expands enough that navigation would degrade without a new anchor.
- `current priorities.md`
  - Current durable priorities.
  - Active concerns worth carrying across sessions.
  - Do not store minor tactical next steps here.

### `atlas/`
- Stable project reference notes only.
- These notes are long-lived references, not session logs.
- `project architecture.md`: architecture shape, system boundaries, major flows, and durable structural constraints.
- `tech stack.md`: core stack decisions, major frameworks, runtimes, tooling, and durable platform constraints.
- `database.md`: data model, schema conventions, entity relationships, and DB rules worth carrying across sessions.
- `deployment.md`: infrastructure, environments, deployment flow, hosting, secrets boundaries, and operational release constraints.

### `knowledge/integrations/`
- Durable external-system knowledge:
  - APIs
  - auth flows
  - sync behavior
  - rate limits
  - webhooks
  - provider-specific constraints

### `knowledge/decisions/`
- Durable choices:
  - what was chosen
  - why
  - alternatives rejected
  - what it affects

### `knowledge/debugging/`
- Reusable debugging knowledge:
  - recurring bugs
  - root causes
  - fixes
  - traps
  - recovery patterns

### `knowledge/patterns/`
- Reusable implementation and workflow patterns:
  - project conventions
  - approved approaches
  - recurring implementation templates
  - standards worth repeating

### `knowledge/business/`
- Business or domain context only when it materially affects implementation.

### `sessions/`
- Session logs only.
- Store what happened, what changed, what remains next, and links to decisions/debugging/pattern notes created or updated.

### `inbox/`
- Temporary captures only.
- Promote anything that matters later into the proper durable note type.
- Do not let inbox notes become permanent storage.

## Exact Information Routing
- Current durable priorities -> `00-home/current priorities.md`
- Navigation anchors -> `00-home/index.md`
- Architecture summary -> `atlas/project architecture.md`
- Stack summary -> `atlas/tech stack.md`
- Database structure or rules -> `atlas/database.md`
- Deployment or infrastructure summary -> `atlas/deployment.md`
- External system behavior -> `knowledge/integrations/<statement-style title>.md`
- Durable technical or workflow decision -> `knowledge/decisions/<statement-style title>.md`
- Root cause, recurring bug, or fix pattern -> `knowledge/debugging/<statement-style title>.md`
- Reusable coding or workflow pattern -> `knowledge/patterns/<statement-style title>.md`
- Durable business or domain rule -> `knowledge/business/<statement-style title>.md`
- Session history or handoff summary -> `sessions/<timestamp> - <statement-style outcome>.md`
- Temporary unprocessed capture -> `inbox/<timestamp> - <short capture>.md`

## Naming Rules
- All durable notes must use statement-style titles that are specific enough to retrieve later.
- Use the human-readable statement directly as the filename stem; do not slugify unless the filesystem requires it.
- Good examples:
  - `Supabase Auth uses RLS on every tenant table.md`
  - `Rate limit requires a 5-minute backoff after 500 requests.md`
  - `Chat sync uses chats_list instead of the analytics endpoint.md`
- Bad examples:
  - `auth.md`
  - `bugs.md`
  - `ideas.md`
  - `integration notes.md`
- Allowed structural exceptions:
  - `00-home/index.md`
  - `00-home/current priorities.md`
  - `atlas/project architecture.md`
  - `atlas/tech stack.md`
  - `atlas/database.md`
  - `atlas/deployment.md`
- Session note filenames must use:
  - `YYYY-MM-DD HHmm - <statement-style outcome>.md`
- Inbox note filenames must use:
  - `YYYY-MM-DD HHmm - <short capture>.md`

## Update Vs Create Rules
- Fixed home and atlas notes are single owners. Always update the fixed file path instead of creating duplicates.
- For `knowledge/` notes:
  - Update an existing note if it already owns the same durable truth.
  - Create a new note only when the durable fact, decision, bug pattern, or business rule is genuinely distinct.
  - Prefer one owner per truth. If two notes would substantially overlap, merge or update instead of duplicating.
- For `sessions/`:
  - Create a new session note for each meaningful stopping point.
  - Continue updating the same session note only while the stopping point is still being formed in the same working block.
- For `inbox/`:
  - Create temporary captures only when immediate categorization is not practical.
  - Promote or delete later; do not preserve inbox notes as durable truth owners.

## Linking Rules
- Use wiki-link-style relationships.
- Minimum required links:
  - Session notes link to decisions, debugging notes, patterns, integrations, or atlas notes they produced or updated.
  - Decision notes link to affected architecture and integration notes.
  - Debugging notes link to related integration and architecture notes.
  - Pattern notes link to related decisions, integrations, or architecture notes when relevant.
  - `current priorities.md` links to the notes that explain why those priorities matter.
  - `index.md` links only to high-value anchor notes.
- Do not keep notes isolated.

## Save Rules
- Default rule: `do not write`.
- Before writing, ask:
  - Is this durable?
  - Will future work benefit from finding this again?
  - Is this better in the vault than in repo workflow files?
  - Is this specific enough to retrieve later?
- If the answer is no, do not write.

## Save And No-Save Behavior
### Save a session note when
- meaningful planning, execution, verification, or handoff happened
- future continuity would benefit
- there was a real change in understanding, state, or direction

### Do not save a session note when
- the interaction was trivial
- the work was pure discussion
- nothing durable was learned
- no meaningful state changed

### Save a decision note when
- a real durable choice was made
- future sessions might otherwise re-debate it
- the choice affects architecture, workflow, tooling, or implementation direction

### Do not save a decision note when
- the choice is temporary
- the choice is obvious and low-value
- the choice is already fully captured in active repo workflow state only

### Save a debugging note when
- a root cause was found
- a fix pattern is reusable
- the issue is likely to recur
- the lesson will help later debugging

### Do not save a debugging note when
- it was incidental
- it was one-off noise
- it has no likely reuse value

### Update `00-home/current priorities.md` when
- durable priorities materially changed
- important focus areas changed
- important blockers or next durable actions changed

### Do not update `00-home/current priorities.md` when
- only minor tactical phase steps changed

### Update `00-home/index.md` when
- the knowledge surface expanded enough that navigation needs another anchor

### Do not update `00-home/index.md` when
- only one small low-impact note was added

## What Must Stay Out Of The Vault
- Raw chat transcripts.
- Raw command logs.
- Milestone files copied from the repo.
- Phase files copied from the repo.
- Verification files copied from the repo.
- Every small clarification.
- Temporary brainstorming junk.
- Duplicate backlog or task systems.

## Repo Vs Vault Boundary
- Keep these in the repo:
  - `AGENTS.md`
  - skills
  - milestone, phase, and verification workflow
  - live execution state
  - active routing
  - immediate handoff state
- Keep these in the vault:
  - durable decisions
  - durable priorities
  - architecture memory
  - debugging history
  - reusable patterns
  - integration knowledge
  - session memory worth keeping

## Minimum End-Of-Session Save Behavior
- At a meaningful stopping point:
  - create or update a session note if continuity needs it
  - update `00-home/current priorities.md` if durable priorities changed
  - write a decision note if a real durable decision was made
  - write a debugging note if a real root cause or fix pattern was found
  - update `00-home/index.md` only if memory expansion makes navigation worse without it
- If none of those are justified, write nothing.

## Best Practical Rule
- Write less.
- Name better.
- Link intentionally.
- Keep one owner for each kind of truth.
