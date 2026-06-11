# Microcopy Checklist

Use this checklist for labels, actions, errors, validation, empty states, confirmations, help text, and accessibility text.

## Principles

Microcopy should be:

- clear
- concise
- specific
- consistent
- user-language first
- action-oriented
- accessible
- localizable when the product supports localization

Do not optimize visible text by removing necessary context. Apply the information preservation rules first.

## Terminology

Check whether:

- the same concept uses the same term everywhere
- user-facing terms avoid internal implementation names
- product-specific terms are defined or learnable
- status names are distinguishable
- role names match product language
- API, database, permission, or stack terms are hidden unless users need them
- abbreviations are expanded or commonly understood by the target users

## Action labels

Check whether:

- button text describes the action
- primary action text is specific enough to predict the result
- destructive actions use explicit verbs
- row-level actions avoid repeating entity names already visible in the row
- bulk actions communicate scope
- menu items are parallel in grammar
- icon-only actions have accessible names
- visible labels and accessible labels do not conflict

### Row action rule

If a row, card, or list item already shows the entity name, the visible action label usually should be only the action:

- Prefer: `Edit`
- Avoid: `Edit John Smith`

Preserve entity context through one or more of:

- row context
- dialog title
- confirmation message
- accessible label, such as `Edit John Smith`
- tooltip
- detail page title

Do not remove entity context from destructive confirmations.

## Buttons and links

Check whether:

- links navigate
- buttons perform actions
- “Cancel,” “Close,” “Back,” and “Done” are used consistently
- “Save,” “Apply,” “Submit,” and “Continue” are not used interchangeably without reason
- “Delete,” “Remove,” “Archive,” and “Deactivate” reflect different consequences
- disabled actions explain why when the reason is not obvious

## Form labels and helper text

Check whether:

- labels are persistent and visible
- placeholders are examples, not labels
- helper text explains non-obvious constraints
- examples match valid input
- required/optional wording is consistent
- units, formats, and limits are visible before error
- fields with business consequences explain impact

## Validation messages

Each validation message should answer:

1. What is wrong?
2. Where is it wrong?
3. How does the user fix it?

Prefer:

- “Enter a valid email address.”
- “Password must be at least 12 characters.”
- “End date must be after start date.”

Avoid:

- “Invalid.”
- “Error.”
- “Something went wrong.”
- raw exception text
- API error codes without explanation

## Error messages

Check whether errors:

- use plain language
- explain what happened
- explain what the user can do next
- avoid blame
- preserve technical detail only when useful for support
- include retry/contact/support path when appropriate
- distinguish user-correctable errors from system failures

## Empty states

Check whether empty states explain:

- what is empty
- why it may be empty
- what the user can do next
- whether permissions, filters, or setup are involved
- whether the state is normal or problematic

Avoid decorative empty states with no action or explanation.

## Loading and success messages

Check whether:

- loading text indicates what is happening when wait time matters
- skeletons do not imply false content structure
- success messages confirm the completed action
- save states distinguish saving, saved, failed, and unsaved changes
- long-running actions show progress or next expectation

## Destructive confirmations

Check whether destructive confirmation includes:

- entity name
- consequence
- reversibility
- affected scope
- primary destructive action
- safe cancel action
- stronger confirmation for irreversible/high-impact actions

Example:

- Title: `Delete user?`
- Body: `John Smith will lose access immediately. This cannot be undone.`
- Destructive action: `Delete user`
- Safe action: `Cancel`

## Accessibility copy

Check whether:

- accessible names are meaningful
- repeated controls are distinguishable for screen-reader users
- aria labels do not hide or contradict visible labels
- screen-reader-only text adds context without duplicating noise
- status announcements are concise
- tooltips are not the only source of essential information

## Localization readiness

Check whether:

- text can expand without breaking layout
- labels avoid hard-coded word order dependencies
- dates, numbers, currencies, and pluralization are locale-aware
- icons are not culturally ambiguous without labels
- concatenated strings are avoided when localization exists

## Microcopy output format

For each microcopy finding include:

- current text
- proposed text
- location
- problem
- evidence
- preservation decision
- accessibility impact
- acceptance criteria
