# UI/UX Review Checklist

Use this checklist to evaluate usability, interface quality, responsiveness, and frontend implementation quality.

## Review principles

Prioritize findings that affect:

- task completion
- comprehension
- error prevention
- accessibility
- business-critical decision-making
- trust and safety
- support burden
- repeated user effort
- implementation maintainability

Do not report personal aesthetic preference as a finding unless tied to evidence.

## UX clarity

Check whether:

- the screen purpose is immediately understandable
- the primary task is obvious
- the page title, breadcrumbs, and navigation match the user’s mental model
- critical status, risk, or next-step information is visible
- labels use user language rather than internal implementation terms
- users can distinguish current state from available actions
- users can recover from mistakes
- users receive timely feedback after actions
- users can predict what will happen before destructive or irreversible actions
- the UI supports recognition rather than recall

## Information hierarchy

Check whether:

- the most important content appears first or is visually strongest
- related items are grouped together
- unrelated items are separated
- secondary information does not compete with primary information
- repeated metadata is compressed or relocated safely
- tables/cards/lists expose the right summary fields
- details remain available when moved out of the primary surface
- headings and sections create a predictable scan path

## Cognitive load

Check for:

- duplicated labels or repeated entity names
- long action text
- unnecessary columns
- low-value metadata shown in dense views
- visual noise from icons, badges, dividers, or borders
- competing primary actions
- unclear status labels
- hidden dependencies between controls
- unnecessary confirmation steps
- avoidable manual entry
- repeated user decisions that can be defaulted safely

## Navigation and wayfinding

Check whether:

- users know where they are
- global and local navigation are distinct
- breadcrumbs, tabs, filters, and back actions are predictable
- search/filter/sort behavior is discoverable
- pagination or infinite scroll communicates position and remaining content
- users can return to prior context after viewing details
- mobile navigation preserves critical destinations

## Actions and button hierarchy

Check whether:

- exactly one primary action is visually dominant per task context
- secondary actions are lower emphasis
- destructive actions are visually and semantically distinct
- action labels are short and specific
- row-level actions avoid repeating entity names already shown in the row
- icon-only actions have accessible names and visible tooltips when helpful
- disabled actions explain why they are disabled when the reason is not obvious
- confirmation dialogs include the entity, consequence, and recovery path

## Tables, lists, and cards

Check whether:

- columns match user decision needs
- default sort matches the most common workflow
- status fields are meaningful and visually scannable
- row actions are grouped consistently
- dense tables remain readable
- mobile layouts preserve essential information
- empty and filtered-empty states explain what happened
- bulk actions communicate scope and risk
- repeated data can be moved to header, grouping, detail panel, or tooltip without losing context

## Forms

Check whether:

- labels are visible and persistent
- helper text clarifies complex fields
- placeholders are not the only labels
- required and optional fields are clear
- validation happens at the right time
- errors identify the field, problem, and fix
- field order matches user workflow
- destructive or irreversible form submissions require confirmation
- long forms are grouped or stepped only when that reduces effort
- saved progress, dirty state, or unsaved changes are handled

## Visual design

Check whether:

- spacing follows the existing scale
- alignment is consistent
- typography creates hierarchy
- color meaning is consistent
- contrast supports readability
- icons add meaning rather than decoration
- badges/chips/status indicators are consistent
- layout density matches task urgency and frequency
- focus and hover states are visible
- loading states reduce perceived uncertainty
- skeletons/spinners do not hide important status too long

## Responsiveness

Check whether:

- layout works at mobile, tablet, desktop, and large-screen widths relevant to the product
- content reflows without horizontal scrolling except for intentional data grids
- touch targets remain usable
- navigation does not lose critical actions
- modals/drawers fit small screens
- tables have a mobile strategy
- filters and bulk actions remain discoverable
- zoom and text scaling do not clip content

## Frontend implementation quality

Check whether:

- components reuse existing project primitives
- page components are not overloaded with unrelated responsibilities
- UI state is modeled clearly
- loading/error/empty states are implemented close to the relevant component
- form validation is consistent with project conventions
- accessibility is implemented semantically rather than with unnecessary ARIA
- design tokens are used instead of hard-coded one-off values
- repeated UI patterns have consistent component ownership
- tests or stories cover critical states
- proposed changes are small enough to validate

## Priority guidance

Use:

- `Critical`: blocks task completion, causes data loss, exposes security/privacy/compliance risk, or makes core workflow inaccessible.
- `High`: materially increases errors, prevents common user goals, or violates important accessibility requirements.
- `Medium`: causes friction, confusion, inconsistency, or maintainability risk but has a workaround.
- `Low`: polish, minor consistency, or low-frequency improvement.

## Effort guidance

Use:

- `Small`: copy, token, style, prop, or localized component change.
- `Medium`: component structure, state handling, responsive behavior, or test updates across a small area.
- `Large`: cross-screen pattern, design-system primitive, route-level flow, data contract, or major responsive redesign.

## Evidence requirement

Every finding must cite at least one of:

- screenshot observation
- route/page/component path
- code symbol
- browser behavior
- user flow step
- test/storybook evidence
- project convention
- accessibility rule
- explicit user/product-owner input
