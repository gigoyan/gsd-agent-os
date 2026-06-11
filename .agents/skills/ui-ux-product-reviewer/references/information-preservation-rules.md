# Information Preservation Rules

Use this reference before recommending removal, hiding, shortening, combining, or relocation of UI information.

## Core rule

Do not simplify by deleting context. Simplify by matching information visibility to user need, risk, frequency, and task timing.

Every recommendation that affects visible information must include one preservation classification.

## Required classifications

Use exactly one:

| Classification | Meaning | Typical destination |
|---|---|---|
| `Must remain visible` | User needs this information in the current context to decide, act, avoid harm, or satisfy business/legal/security requirements. | Keep visible in current screen or row. |
| `Can move to secondary detail` | Useful but not needed for the primary scan or decision. | Detail page, expandable row, side panel, secondary metadata area. |
| `Can hide behind tooltip/details` | Helpful clarification but not required for most users or critical decisions. | Tooltip, help text, disclosure, docs link. |
| `Can be available only in confirmation/dialog/detail page` | Needed at the moment of consequence, not during normal scanning. | Confirmation dialog, review step, detail page. |
| `Can be removed` | Duplicate, obsolete, misleading, non-user-facing, or not tied to current user goals. | Remove from UI and tests if safe. |
| `Needs product-owner confirmation` | Potentially important but evidence is insufficient or business/legal/customer risk is unclear. | Do not remove until confirmed. |

## Step 1 — Identify the information

For every affected item record:

- exact visible text/data
- location
- current purpose
- user action it supports
- whether it appears elsewhere
- whether it is visible, hidden, accessible-only, or tooltip-only
- evidence status

## Step 2 — Classify risk

Treat information as high-risk when it affects:

- legal/compliance requirements
- pricing, billing, payment, or financial decisions
- security, permissions, access, or identity
- irreversible or destructive actions
- auditability
- health, safety, or regulated domains
- user trust
- customer support traceability
- contractual commitments
- data freshness or synchronization status
- role-specific restrictions

High-risk information usually must remain visible or require product-owner confirmation.

## Step 3 — Classify frequency and timing

Ask:

- Is the information needed every time?
- Is it needed only when deciding?
- Is it needed only when troubleshooting?
- Is it needed only before destructive action?
- Is it needed only after error?
- Is it needed only by admins or expert users?
- Is it needed only for support/audit?

Move information closer to the moment it is needed.

## Step 4 — Check redundancy

Information may be redundant when:

- the same entity appears in the row and action label
- the same status appears in title, badge, and helper text
- table columns repeat group-level context
- every row repeats identical metadata
- helper text repeats the label
- icon and text duplicate without adding clarity

Redundancy is not automatically removable. Keep or relocate if it supports accessibility, safety, scanning, or confirmation.

## Step 5 — Preserve accessibility context

When shortening visible labels:

- preserve distinguishable accessible names
- keep destructive confirmation context visible
- do not rely only on color, icon, hover, or tooltip
- ensure keyboard and touch users can access any relocated detail
- ensure screen-reader users retain entity context

Example:

- Visible row action: `Edit`
- Accessible name: `Edit John Smith`
- Dialog title: `Edit John Smith`
- Confirmation: not needed for non-destructive edit unless product risk requires it

## Step 6 — Decide destination

Use this decision pattern:

- Needed for immediate decision: keep visible.
- Needed for scan but not every row: group/header/summary.
- Needed for occasional clarification: tooltip/details.
- Needed for consequence review: confirmation/dialog/detail page.
- Needed only by advanced users: secondary detail or expandable section.
- Not user-relevant and duplicated elsewhere: remove.
- Business value unclear: product-owner confirmation.

## Required output

For each affected information item:

| Item | Current location | Proposed action | Classification | Rationale | Risk | Evidence status |
|---|---|---|---|---|---|---|
|  |  | Keep/move/hide/remove |  |  |  |  |

## Prohibited recommendations

Do not recommend:

- “Remove this because it looks cluttered” without preservation classification.
- “Hide this in a tooltip” when it is required for keyboard/touch/screen-reader users.
- “Remove status” when status affects user decision or trust.
- “Simplify destructive action copy” by removing entity or consequence.
- “Use icons only” for unfamiliar, destructive, or high-risk actions.
- “Move all details to a drawer” when users must compare items across rows.
- “Remove repeated entity names” from accessible names or confirmations when they disambiguate repeated controls.
