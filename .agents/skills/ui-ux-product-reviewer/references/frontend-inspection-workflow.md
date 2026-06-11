# Frontend Inspection Workflow

Use this reference when reviewing a frontend codebase, route, screen, component, or screenshot-backed UI flow.

## Goal

Inspect the smallest useful frontend context, gather evidence, and avoid broad repository scanning.

## Evidence labels

Use these labels consistently:

- `Confirmed`: directly supported by code, screenshot, browser behavior, test, documentation, or explicit user input.
- `Suggested`: likely, but inferred from partial evidence.
- `Unknown`: not found, inaccessible, contradictory, or not yet verified.

## Step 1 — Read GSD and project routing context

When present, inspect in this order:

1. `PROJECT.md`
2. `.planning/STATE.md`
3. Active milestone or active phase referenced by state
4. Relevant Project Idea Document or Technical Specification
5. Stack-selection/configuration package
6. `.planning/CONTEXT_INDEX.md`
7. `.planning/CODEBASE_MAP.md`

Use `.planning/CONTEXT_INDEX.md` before broad repository search when it exists and appears current.

If routing is missing or stale:

- continue only with the smallest evidenced route;
- mark gaps as `Unknown`;
- recommend a `$gsd-map-codebase` refresh candidate if mapping is needed for safe implementation.

## Step 2 — Identify frontend stack

Inspect only enough files to identify:

- framework: React, Next.js, Vue, Svelte, Angular, Remix, Astro, Rails views, server-rendered templates, or other
- package manager and workspace shape
- route ownership
- styling approach: CSS modules, Tailwind, Sass, CSS-in-JS, design tokens, component library, native platform UI
- test/storybook/visual regression surfaces
- localization or content files

Do not assume a stack from filenames alone. Confirm with package/config files or imports when possible.

## Step 3 — Locate route and screen owners

Prefer targeted discovery:

- route definitions
- app/page directories
- screen/page components
- layout shell
- route guards and permission wrappers
- route-level loading/error/empty states
- metadata/title/breadcrumb declarations

Record:

- route or screen
- likely owner file
- supporting layout files
- evidence status

## Step 4 — Locate component owners

For the reviewed screen or screenshot, identify likely component layers:

- route/page file
- layout/container component
- domain feature component
- reusable UI primitives
- form components
- table/list/card components
- modal/drawer/popover components
- navigation/breadcrumb components
- loading/empty/error/success state components
- permission/role-based wrappers

Prefer direct import chains over name search only.

## Step 5 — Locate design-system and style sources

Inspect:

- theme provider
- design-token files
- color and typography tokens
- spacing scale
- component library wrappers
- Tailwind config
- global CSS
- CSS modules or component-level styles
- icon library usage
- responsive breakpoints
- dark-mode or high-contrast mode handling

Do not introduce a new design system when existing tokens/components can support the recommendation.

## Step 6 — Locate text and microcopy sources

Inspect:

- visible JSX/template text
- localization files
- constants
- schema validation messages
- form labels and helper text
- error messages
- empty-state text
- destructive confirmation messages
- aria-labels and screen-reader-only text

Check whether user-visible terminology is consistent across screen, route, and related components.

## Step 7 — Locate state variations

Look for:

- loading state
- empty state
- error state
- success state
- disabled state
- read-only state
- validation state
- permission-denied state
- unauthenticated state
- offline/network-failure state
- destructive confirmation state
- mobile and responsive layout changes

A UI audit is incomplete if it only reviews the ideal populated state when other states are present.

## Step 8 — Locate accessibility evidence

Inspect:

- semantic elements
- button vs link usage
- form labels and field associations
- aria attributes
- focus management
- keyboard handlers
- modal/dialog primitives
- skip links or landmarks
- alt text
- contrast tokens
- reduced-motion handling
- responsive zoom and reflow behavior

Mark issues as `Suggested` if they require runtime/browser confirmation.

## Step 9 — Locate validation and QA surfaces

Inspect when present:

- unit tests
- component tests
- accessibility tests
- Playwright/Cypress tests
- Storybook stories
- visual regression tests
- snapshots
- design QA docs
- browser evidence artifacts
- QA checklists

Use existing test conventions in recommendations.

## Step 10 — Avoid low-value scanning

Avoid by default:

- `node_modules/`
- build output
- generated files
- lockfiles except for dependency confirmation
- unrelated backend code
- unrelated routes
- migration/data files unless UI depends on them
- broad raw source-material folders
- compiled assets

Inspect backend/API only when it affects visible UI, permissions, data shape, validation messages, loading states, or error states.

## Inspection output format

Use this compact inventory:

| Area | Evidence | Evidence status | Notes |
|---|---|---|---|
| Product/scope |  | Confirmed/Suggested/Unknown |  |
| Frontend stack |  | Confirmed/Suggested/Unknown |  |
| Route/screen owners |  | Confirmed/Suggested/Unknown |  |
| Components reviewed |  | Confirmed/Suggested/Unknown |  |
| Design-system/style sources |  | Confirmed/Suggested/Unknown |  |
| Microcopy sources |  | Confirmed/Suggested/Unknown |  |
| State variations |  | Confirmed/Suggested/Unknown |  |
| Accessibility evidence |  | Confirmed/Suggested/Unknown |  |
| Test/QA surfaces |  | Confirmed/Suggested/Unknown |  |
| Gaps |  | Unknown |  |

## Stop condition

Stop inspection when there is enough evidence to produce a useful audit and change plan. Do not scan the whole frontend merely to be exhaustive.
