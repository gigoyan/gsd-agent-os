# Milestone Handoff Prompt Contract

## Purpose
Define a copy-paste prompt that evidence-producing skills can give the user for later milestone planning.

## Rule
Evidence-producing skills must not create milestones. They may provide this handoff prompt.

## Prompt Template

```text
Use $gsd-plan-milestone to plan implementation from the stored evidence below.

Source evidence:
- Evidence type:
- Evidence artifact path:
- Report path:
- Finding IDs:
- Root cause IDs:
- Evidence status summary:
- Product-owner confirmations required:
- Out of scope:
- Required validation:
- Recommended implementation boundary:

Important rules:
- Preserve Confirmed/Suggested/Unknown evidence statuses.
- Do not implement Unknown or Suggested claims as confirmed requirements.
- Read the cited evidence artifacts before planning.
- Create a milestone only after user confirmation.
```

## Completion Check

- Handoff prompt cites evidence artifacts instead of copying raw evidence.
- Handoff prompt preserves `Confirmed`, `Suggested`, and `Unknown`.
- Handoff prompt does not perform implementation, verification, QA, story generation, Vault publishing, or milestone planning itself.
