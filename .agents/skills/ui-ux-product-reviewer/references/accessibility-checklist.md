# Accessibility Checklist

Use this checklist for WCAG-oriented accessibility review. Mark items as `Confirmed` only when verified by code, screenshot, browser behavior, automated test, or manual test.

## Baseline principles

Review for:

- perceivable content
- operable controls
- understandable interaction and copy
- robust semantic implementation

Accessibility findings should include the affected users, affected interaction, evidence, and suggested validation.

## Semantic structure

Check:

- page has one clear primary heading where appropriate
- heading levels are logical and not chosen only for visual size
- landmark regions are used when appropriate
- lists use list semantics
- tables use table semantics only for tabular data
- buttons are used for actions
- links are used for navigation
- form controls have programmatic labels
- custom controls expose correct role, name, state, and value
- decorative icons/images are hidden from assistive tech
- meaningful images have useful alt text or equivalent text

## Keyboard access

Check:

- all interactive controls are reachable by keyboard
- focus order matches visual/logical order
- no keyboard trap exists
- custom widgets support expected keyboard patterns
- skip or bypass mechanisms exist when navigation is long
- dialogs, menus, drawers, comboboxes, tabs, and popovers have expected keyboard behavior
- disabled controls are not focusable unless the design intentionally exposes explanation
- hidden content is not keyboard reachable

## Focus management

Check:

- visible focus indicator exists and is not obscured
- focus is moved intentionally when opening dialogs, drawers, menus, or route-like overlays
- focus returns to a logical trigger after closing temporary UI
- destructive confirmations place focus on a safe/logical control
- validation errors move focus or provide clear navigation to the error
- route changes or major content changes communicate context

## Screen-reader clarity

Check:

- accessible names are concise and unique in context
- repeated row actions have distinguishable accessible names when visible labels are short
- icon-only buttons have accessible names
- status changes are announced when needed
- error messages are associated with fields
- required/invalid state is programmatically exposed
- loading state is communicated when it blocks interaction
- table headers are associated with cells
- dialogs have accessible titles and descriptions

## ARIA usage

Check:

- native HTML is used before ARIA
- ARIA does not contradict native semantics
- `aria-label` does not hide useful visible text
- `aria-describedby` is used for helper/error text when appropriate
- live regions are used sparingly and only for meaningful updates
- expanded/selected/current/pressed states are accurate
- hidden content uses the correct visual and accessibility hiding strategy

## Forms and validation

Check:

- every field has a persistent visible label
- helper text explains format or constraints before submission
- errors identify the field, problem, and fix
- validation timing avoids premature noise
- required fields are clear
- optional fields are clear when most fields are required
- grouped controls have group labels
- autocomplete attributes are used where appropriate
- destructive submissions include entity and consequence confirmation

## Color and contrast

Check:

- normal text meets at least 4.5:1 contrast where applicable
- large text meets at least 3:1 contrast where applicable
- icons and interactive component boundaries meet non-text contrast expectations
- color is not the only way to communicate state
- focus indicators have sufficient contrast
- disabled-state contrast is still understandable when the control is visible
- charts/status colors have labels, patterns, or text alternatives

## Motion and animation

Check:

- reduced-motion preference is respected
- motion does not trigger vestibular discomfort
- animations are not required to understand content
- auto-updating content can be paused/stopped when relevant
- loading shimmer or animation does not obscure status indefinitely

## Responsive, zoom, and touch

Check:

- content reflows without losing information
- text zoom does not clip labels, buttons, or table content
- page remains usable around 320 CSS px width where relevant
- touch targets are large enough and sufficiently spaced
- hover-only information is also available by keyboard and touch
- modals/drawers remain usable on small screens
- horizontal scrolling is avoided except for intentional data grids

## Modals, drawers, and popovers

Check:

- dialog has accessible title
- focus moves into the dialog
- focus is trapped only while the modal is open
- background is inert or unavailable to assistive tech when modal is active
- Escape or close behavior is available when appropriate
- focus returns to a logical element after close
- destructive dialogs include entity, consequence, and action clarity

## Accessibility output format

For each accessibility finding include:

- affected component or route
- affected interaction
- affected user group
- evidence
- likely WCAG principle or criterion area
- recommendation
- acceptance criteria
- suggested automated test
- suggested manual keyboard or screen-reader check
- evidence status
