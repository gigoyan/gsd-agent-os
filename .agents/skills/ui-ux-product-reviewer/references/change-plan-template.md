# Change Plan Template

Use this template to produce developer-ready UI/UX tasks without editing code.

## Summary

- Review scope:
- Primary user goal:
- Screens/routes/components:
- Evidence reviewed:
- Assumptions:
- Product-owner confirmations needed:
- Implementation boundary:
- Recommended implementation mode: `GSD quick task | GSD milestone/phase | manual design review first`

## Priority definitions

- `Critical`: blocks core task, causes data loss, creates security/privacy/compliance risk, or prevents accessible use of a core workflow.
- `High`: materially increases errors, confusion, abandonment, or inaccessible behavior in a common workflow.
- `Medium`: causes friction, inconsistency, maintainability risk, or avoidable support burden.
- `Low`: polish, copy, minor consistency, or low-frequency usability improvement.

## Effort definitions

- `Small`: localized copy, token, prop, style, or single-component change.
- `Medium`: component structure, state handling, responsive behavior, or test update across a contained area.
- `Large`: cross-screen pattern, route-level flow, design-system primitive, data contract, or major responsive redesign.

## Change plan table

| ID | Priority | Effort | Page/screen/component | Problem | Evidence | Principle | Recommendation | Preservation decision | Likely files/components | Risk | Acceptance criteria | Tests | Manual QA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UX-001 | High | Medium |  |  |  |  |  |  |  |  |  |  |  |

## Finding detail format

### UX-001 — `<short finding title>`

- **Priority:** `Critical | High | Medium | Low`
- **Effort:** `Small | Medium | Large`
- **Evidence status:** `Confirmed | Suggested | Unknown`
- **Page/screen/component:**
- **Problem:**
- **Evidence:**
- **Affected users:**
- **UX/UI/accessibility principle:**
- **Recommended change:**
- **Information preservation decision:** `Must remain visible | Can move to secondary detail | Can hide behind tooltip/details | Can be available only in confirmation/dialog/detail page | Can be removed | Needs product-owner confirmation`
- **Preservation rationale:**
- **Likely affected files/components:**
- **Implementation notes:**
- **Risks:**
- **Dependencies:**
- **Acceptance criteria:**
  - [ ] 
  - [ ] 
- **Suggested automated tests:**
  - 
- **Suggested manual QA:**
  - 
- **Product-owner confirmation needed:** `yes | no`
- **Open questions:**

## Acceptance criteria guidance

Acceptance criteria should be observable and testable.

Good:

- “Row action visible text is `Edit`; screen-reader accessible name includes the user’s name.”
- “Delete confirmation shows the entity name and irreversible consequence.”
- “The table remains readable at 320 CSS px width with no loss of primary action.”
- “All form fields have visible labels and errors identify how to fix the input.”

Weak:

- “Looks cleaner.”
- “Make it nicer.”
- “Improve accessibility.”
- “Reduce clutter.”

## Test recommendation guidance

Suggest the smallest useful validation:

- unit or component test for state/copy logic
- accessibility test for labels/roles when available
- Storybook story for visual states
- Playwright/Cypress flow for critical journeys
- manual keyboard test
- manual responsive test
- manual screen-reader smoke test
- visual regression screenshot when available

## Product-owner confirmation section

Use this when simplification affects business-critical information.

| Item | Proposed change | Why confirmation is needed | Decision owner | Status |
|---|---|---|---|---|
|  |  |  |  | `pending | approved | rejected` |
