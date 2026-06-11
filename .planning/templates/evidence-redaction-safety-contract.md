# Evidence Redaction And Safety Contract

## Purpose
Prevent GSD evidence artifacts and Vault mirror outputs from leaking secrets, credentials, sensitive raw logs, or unsafe production actions.

## Applies To
- Browser Evidence Runtime
- `gsd-discover-flow-evidence`
- `ui-ux-product-reviewer`
- `gsd-qa-tester`
- `gsd-create-user-stories`
- `gsd-publish-story-knowledge`
- project-context export and mirror scripts

## Never Publish To Vault By Default
- passwords
- tokens
- cookies
- authorization headers
- private keys
- connection strings
- payment secrets
- raw request bodies unless explicitly safe
- full network logs
- raw network logs
- full DOM snapshots
- raw DOM
- screenshots
- console logs

## Repo-Local Evidence Rule
Raw operational evidence may stay repo-local under `.planning/evidence/**` when needed for verification, but secrets must be redacted before writing whenever practical.

## Redaction Replacement
Use:

```text
[REDACTED_SECRET]
```

## Safety Event Rule

If an action is blocked or dangerous but allowed, record it in `safety-events.json`.

## Unrestricted Mode Rule

`unrestricted` mode removes action-level blockers only. It does not remove redaction, safety-event recording, or evidence marking.

## Completion Check

- Redaction ran before artifact finalization.
- Manual review is flagged when redactions occur.
- Vault mirror contains only curated safe summaries by default.
