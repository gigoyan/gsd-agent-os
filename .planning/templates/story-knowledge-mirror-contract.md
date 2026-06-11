# Story Knowledge Mirror Contract

## Purpose
Define deterministic incremental publishing from repo-local story/workflow/QA/UX artifacts to the project Vault namespace.

## Owner
`gsd-publish-story-knowledge`

## Rule

```text
Repo = operational source of truth
Vault = assistant/product-readable published mirror
Mirror = deterministic delta sync, not full rewrite
repo = operational source
Vault = published mirror
mirror = deterministic delta sync
```

## Mirror Paths

```text
.planning/story-knowledge-mirror/mirror-config.json
.planning/story-knowledge-mirror/mirror-lock.json
.planning/story-knowledge-mirror/mirror-manifest.json
.planning/story-knowledge-mirror/mirror-report.md
.planning/story-knowledge-mirror/mirror-runs/<run-id>/
```

## Vault Paths

```text
projects/<vault-project-id>/knowledge/user-stories/**
projects/<vault-project-id>/knowledge/workflows/**
projects/<vault-project-id>/knowledge/roles/**
projects/<vault-project-id>/knowledge/qa/**
projects/<vault-project-id>/knowledge/business/**
```

## Delta Actions

| Case | Action |
| --- | --- |
| Source exists, not in lock | `create` |
| Source exists, hash unchanged | `unchanged` |
| Source exists, hash changed | `update` |
| Source missing, in lock | `removed` |
| Vault page changed outside managed block | `preserve + update managed block` |
| Vault managed block changed manually | `conflict` |
| Target path changed due to title rename | `rename` or `create + archive old` based on config |

## Dry-Run Rule

Default to dry run. Apply writes only with explicit approval or `--apply`.

## Managed Block Format

Mirror writes use managed blocks. Manual content outside managed blocks must be preserved.

```md
<!-- GSD-MIRROR:START <source-id> -->
Generated content.
<!-- GSD-MIRROR:END <source-id> -->
```

## Removed-Source Default

Default to tombstone/archive, not hard delete.

## Raw Evidence Rule

Do not mirror raw screenshots, network logs, DOM snapshots, cookies, tokens, console logs, or raw browser artifacts by default.

## mirror-lock.json Schema

```json
{
  "schema_version": 1,
  "mirror_version": 1,
  "vault_project_id": "",
  "last_mirrored_at": "",
  "items": [
    {
      "source_id": "",
      "source_type": "user_story | workflow | role | qa_summary | ux_summary | business_rule",
      "source_path": "",
      "source_content_hash": "sha256:",
      "source_metadata_hash": "sha256:",
      "vault_path": "",
      "vault_last_written_hash": "sha256:",
      "vault_managed_block_hash": "sha256:",
      "last_action": "created | updated | unchanged | tombstoned | archived | deleted | conflict | renamed",
      "last_mirrored_at": "",
      "source_commit": "",
      "status": "current | removed | conflict"
    }
  ],
  "removed_source_items": []
}
```
