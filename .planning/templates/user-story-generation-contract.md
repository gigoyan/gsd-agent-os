# User Story Generation Contract

## Purpose
Define how user stories are generated from Flow Intelligence and evidence.

## Owner
`gsd-create-user-stories`

## Inputs

```text
.planning/flow-intelligence/**
.planning/evidence/flow-intelligence/**
optional custom story template
```

## Outputs

```text
.planning/user-stories/**
.planning/user-stories/story-index.jsonl
.planning/user-stories/story-catalog.json
```

## Required Files Per Story

```text
story.md
story.json
acceptance-criteria.md
gherkin.feature
source-links.json
publish-source.md
story-hashes.json
```

## Rules

- Do not browse by default.
- Do not redo discovery unless evidence is missing, stale, or user explicitly requests refresh.
- Use Flow Intelligence as the source layer.
- Preserve evidence statuses.
- `publish-source.md` is the curated source for Vault mirroring.

## story.json Schema

```json
{
  "schema_version": 1,
  "story_id": "US-0001-login",
  "source_flow_ids": [],
  "title": "",
  "roles": [],
  "format_profile": "default-gsd | bdd-gherkin | qa-ready | custom",
  "status": "current | stale | partial | removed",
  "source_commit": "",
  "source_paths": [],
  "sections": {
    "story": "",
    "business_goal": "",
    "main_flow": [],
    "acceptance_criteria": []
  },
  "content_hash": "sha256:",
  "publish_hash": "sha256:"
}
```
