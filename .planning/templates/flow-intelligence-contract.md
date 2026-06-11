# Flow Intelligence Contract

## Purpose
Define repo-local operational artifacts describing user-visible flows, roles, pages, APIs, entities, code references, replay plans, and evidence.

## Owner
`gsd-discover-flow-evidence`

## Consumers
- `ui-ux-product-reviewer`
- `gsd-create-user-stories`
- `gsd-qa-tester`
- `gsd-publish-story-knowledge`
- `gsd-plan-milestone`

## Output Root

```text
.planning/flow-intelligence/**
.planning/evidence/flow-intelligence/**
```

## Indexes

```text
.planning/flow-intelligence/INDEX.md
.planning/flow-intelligence/capability-index.jsonl
.planning/flow-intelligence/role-index.jsonl
.planning/flow-intelligence/page-index.jsonl
.planning/flow-intelligence/api-index.jsonl
.planning/flow-intelligence/db-entity-index.jsonl
.planning/flow-intelligence/flow-index.jsonl
.planning/flow-intelligence/traceability-index.jsonl
.planning/flow-intelligence/evidence-index.jsonl
.planning/flow-intelligence/replay-index.jsonl
```

## Per-Flow Files

```text
.planning/flow-intelligence/flows/<flow-id>/
  flow.json
  flow.compact.md
  story-source.json
  code-map.json
  replay.plan.json
  qa-hints.json
  evidence-manifest.json
  source-hashes.json
```

## Rules

- User stories are not the base artifact.
- Flow Intelligence is the reusable base.
- Never invent paths, symbols, roles, APIs, routes, or entities.
- Preserve `Confirmed | Suggested | Unknown`.
- Browser evidence is referenced, not copied into flow JSON.
- Raw evidence stays under `.planning/evidence/**`.

## flow.json Schema

```json
{
  "schema_version": 1,
  "flow_id": "FL-0001-login",
  "title": "User logs in to dashboard",
  "scope": {
    "type": "flow",
    "value": "login"
  },
  "roles": [
    {
      "role_id": "registered_user",
      "evidence_status": "Confirmed"
    }
  ],
  "entrypoints": [
    {
      "type": "frontend_route",
      "value": "/login",
      "evidence_status": "Confirmed"
    }
  ],
  "related_pages": [],
  "related_apis": [],
  "related_entities": [],
  "steps": [
    {
      "step_id": "FL-0001-S01",
      "intent": "",
      "user_visible_action": "",
      "system_behavior": "",
      "evidence_refs": [],
      "code_ref_ids": [],
      "evidence_status": "Confirmed"
    }
  ],
  "confidence": "confirmed | suggested | mixed | unknown",
  "status": "current | stale | partial | removed",
  "last_discovered_at": "",
  "last_evidence_run_id": "",
  "staleness_hash": "sha256:"
}
```
