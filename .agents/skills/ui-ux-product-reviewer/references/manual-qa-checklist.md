# Manual QA Checklist

Use this checklist after a UI/UX audit or after implementation of approved UI changes.

## Scope

- Screen/route:
- Flow:
- Role:
- Browser/device:
- Viewport:
- Test data:
- Build/environment:
- Reviewer:
- Date:

## Smoke checks

- [ ] Page loads without console errors that affect the reviewed flow.
- [ ] Primary content is visible.
- [ ] Primary action is available.
- [ ] Navigation to and from the screen works.
- [ ] Loading state appears when relevant.
- [ ] Error state appears when relevant.
- [ ] Empty state appears when relevant.
- [ ] Success state appears when relevant.
- [ ] Permission or role-based state appears when relevant.

## UX checks

- [ ] Screen purpose is clear.
- [ ] Primary action is obvious.
- [ ] Secondary actions do not compete with the primary action.
- [ ] Destructive actions are visually and semantically distinct.
- [ ] User can recover from mistakes.
- [ ] Feedback appears after user actions.
- [ ] Users do not need to remember hidden context from previous screens.
- [ ] Critical information remains visible or available at the right moment.
- [ ] Any removed/relocated information matches the preservation decision.

## Microcopy checks

- [ ] Button labels are short and specific.
- [ ] Row actions do not unnecessarily repeat entity names in visible text.
- [ ] Accessible names preserve row/entity context where needed.
- [ ] Empty-state text explains what happened and what to do next.
- [ ] Validation errors explain the problem and fix.
- [ ] Destructive confirmation includes entity, consequence, and reversibility.
- [ ] Terminology is consistent across the flow.
- [ ] Technical/internal wording is not exposed unless appropriate.

## Accessibility checks

- [ ] All interactive controls are keyboard reachable.
- [ ] Focus order is logical.
- [ ] Focus indicator is visible.
- [ ] No keyboard trap exists.
- [ ] Modal/dialog focus moves correctly and returns correctly.
- [ ] Form fields have visible labels.
- [ ] Errors are associated with fields.
- [ ] Icon-only controls have accessible names.
- [ ] Links and buttons use correct semantics.
- [ ] Color is not the only state indicator.
- [ ] Text contrast appears sufficient or has been checked.
- [ ] Screen-reader smoke test confirms names, roles, and states for critical controls.
- [ ] Reduced-motion preference is respected where motion exists.

## Responsive checks

Test relevant breakpoints:

- [ ] Mobile narrow width
- [ ] Mobile wide width
- [ ] Tablet width
- [ ] Desktop width
- [ ] Large desktop width if relevant

Check:

- [ ] No unintended horizontal scroll except intentional data grids.
- [ ] Primary action remains available.
- [ ] Critical information remains available.
- [ ] Navigation remains usable.
- [ ] Tables/lists/cards remain readable.
- [ ] Modals/drawers fit the viewport.
- [ ] Text does not clip or overlap.
- [ ] Touch targets are usable.

## Table/list/card checks

- [ ] Default sort supports the common workflow.
- [ ] Status values are understandable.
- [ ] Row actions are consistently placed.
- [ ] Bulk actions communicate affected scope.
- [ ] Empty and filtered-empty states are distinct.
- [ ] Long values wrap/truncate with safe access to full value.
- [ ] Details moved out of primary view remain discoverable.

## Form checks

- [ ] Required/optional fields are clear.
- [ ] Helper text appears before validation errors.
- [ ] Validation timing is appropriate.
- [ ] Error messages are actionable.
- [ ] Save/submit state is clear.
- [ ] Unsaved changes are handled.
- [ ] Disabled controls communicate why when needed.

## Destructive action checks

- [ ] Entity name is shown.
- [ ] Consequence is shown.
- [ ] Reversibility is shown.
- [ ] Destructive action is not the default accidental action.
- [ ] Cancel/safe action is clear.
- [ ] Keyboard focus starts in a safe/logical place.
- [ ] Success/failure feedback is shown.

## Final disposition

- [ ] Pass
- [ ] Pass with follow-up
- [ ] Partial
- [ ] Fail

Notes:

- 
