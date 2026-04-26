# Stack Profile And Variant Option Contract

Use this contract to define reusable stack-aware blueprint data after the current project has completed:
- Project Idea Document
- stack-selection readiness

This contract exists so the reusable GSD package can hold curated stack guidance without shipping project-specific runtime outputs.

## Design Basis
- Put durable project guidance in `AGENTS.md`, because Codex reads `AGENTS.md` files before work and layers them by scope.
- Put repeatable task workflows in skills, because skills package instructions, resources, and optional scripts with progressive disclosure.
- Keep skills narrowly scoped, because Codex matches them by `description` and the official guidance says those descriptions need clear scope and boundaries.
- Put project-local runtime and tool configuration in `.codex/config.toml` when a current project requires generated local Codex configuration.
- If project-local `.codex/` outputs are required for the current project and the repository does not yet contain a `.codex/` directory, create it inside that project’s local runtime copy at generation time.
- Do not use repository `.codex/` files as the source of truth for user-facing conversation-language policy; that policy is defined in `AGENTS.md`.
- Use tools and MCP only when they materially improve the workflow, because Codex supports built-in tools, tool search, function calling, and remote MCP for extending agent capabilities.
- Keep the reusable blueprint generic. Generate project-local `.codex` outputs only after the current project has selected a stack and variants.

## Contract Goals
- Capture enough information to generate stack-aware project instructions, skills, and project-local Codex configuration.
- Separate reusable blueprint truth from project-specific selections.
- Support multiple valid patterns for one stack through explicit variant options.
- Support profile-backed `Suggested` defaults, recommended option combinations, and convention bundles without silently promoting them to `Confirmed`.
- Make non-technical selection possible by requiring plain-language explanations, fit guidance, tradeoffs, and examples.
- Keep official-doc freshness review and project-local output generation as explicit follow-on work after selection capture instead of blurring them into the active selection step.

## Storage Rules
- Store reusable stack profiles and variant options in the blueprint, not in project state files.
- Store project-specific selections in the current project's spec artifacts and stack-selection artifact.
- Store generated project-local Codex files only in the current project's local runtime copy after selection is complete.
- Do not store stack profile data in the vault unless the project itself has a durable project-specific decision worth saving there.

## Stack Profile Contract
Each supported stack profile must define the fields below.

### Identity
- `profile_id`: Stable machine-readable identifier such as `backend-nodejs-express`.
- `display_name`: User-facing name.
- `domain`: One of `frontend`, `backend`, `data`, `auth`, `integration`, `hosting`, `observability`, or another explicit stack domain used by the blueprint.
- `status`: `active`, `experimental`, `deprecated`, or `archived`.
- `version`: Version for the reusable profile itself, not the framework version.
- `summary`: One-paragraph plain-language description of what this profile represents.

### Ownership And Freshness
- `owners`: Maintainer names or team.
- `last_reviewed`: Date the profile was last manually reviewed.
- `freshness_policy`:
  - `official_sources`: Official documentation links used as the source of truth.
  - `check_scope`: What must be revalidated at selection time, such as supported versions, recommended structure, toolchain, or deployment guidance.
  - `check_mode`: `confirm_only`, `project-local-adjustment-allowed`, or another explicit rule.
  - `max_staleness_days`: Maximum age before a review is required.
- `community_sources`: Optional forum or community references used only as secondary guidance.

### Applicability
- `best_for`: Project types or operating contexts that fit this profile well.
- `avoid_when`: Situations where this profile is a poor fit.
- `prerequisites`: Known assumptions, dependencies, or environment requirements.
- `compatibility_notes`: Important compatibility boundaries with other domains or profiles.

### Architecture And Structure Baseline
- `recommended_architecture_baseline`: Default architecture recommendation for this profile before variant selection.
- `recommended_project_structure`: Default folder or module organization before variant selection.
- `testing_baseline`: Default testing layers, tools, and verification seams.
- `tooling_baseline`: Default formatter, linter, package manager, build tool, runtime commands, and quality gates.
- `operational_baseline`: Default logging, observability, deployment, environment, and CI expectations.

### Code Style And Conventions Baseline
- `style_baseline`: Core coding style expectations.
- `naming_baseline`: Naming conventions for files, modules, functions, types, tests, and environment variables.
- `error_handling_baseline`: Error handling, logging, retry, validation, and boundary rules.
- `dependency_baseline`: Rules for dependency selection, package boundaries, and internal module usage.
- `documentation_baseline`: Expectations for comments, public API docs, ADR references, or examples.

### Variant Axes
- `variant_axes`: List of decision axes supported by this profile.
- Each axis must include:
  - `axis_id`: Stable machine-readable identifier such as `backend_architecture`.
  - `label`: User-facing selection label.
  - `required`: Whether the user must pick one option.
  - `selection_stage`: When the choice should happen, such as stack selection, later architecture refinement, or deployment refinement.
  - `default_option_id`: Optional default when the user explicitly accepts the recommended choice.
  - `option_ids`: Variant options allowed for this axis.

### User-Facing Selection Content
- `selection_prompt`: Plain-language question shown to the user.
- `selection_help`: Short explanation of why this choice matters.
- `comparison_rules`: What the user should compare across options, such as simplicity, scale, team skill, or delivery speed.

### Recommendation Metadata
- `recommendation_sets`: Optional named recommendation bundles that the selection skill may surface as `Suggested`.
- Each recommendation set must include:
  - `recommendation_id`: Stable machine-readable identifier.
  - `label`: Short user-facing label.
  - `status`: `active`, `experimental`, `deprecated`, or `archived`.
  - `priority`: `primary`, `secondary`, or another explicit ranking label used only to order `Suggested` recommendations.
  - `when_to_suggest`: Repo-proven facts, explicit user inputs, or project conditions that justify surfacing this bundle as a `Suggested` recommendation.
  - `not_when`: Evidence or constraints that suppress this bundle even if it would otherwise be a fit.
  - `rationale`: Why this recommendation is a fit for the matching conditions.
  - `tradeoffs`: Main costs or constraints the user should understand before accepting it.
  - `suggested_convention_ids`: Convention bundle IDs that should be shown with the recommendation.
  - `override_prompt`: Short confirmation prompt used when the user wants to override the suggested bundle.
  - `deferred_follow_on`: Later work that stays out of the active selection step, such as freshness review or project-local output generation.
- `recommended_axis_options`: Child records under each recommendation set that map a stack-selection axis to the option the profile recommends when that set is surfaced.
- Each recommended-axis record must include:
  - `axis_id`: The affected axis.
  - `option_id`: The suggested option on that axis.
  - `reason`: Why that option is suggested for this recommendation set.

### Convention Overlays
- `convention_overlays`: Optional reusable convention bundles that may be attached to a recommendation set or to explicitly selected options.
- Each convention overlay must include:
  - `convention_id`: Stable machine-readable identifier.
  - `label`: Short user-facing name.
  - `summary`: Plain-language description of the convention.
  - `applies_when`: The selected options or confirmed conditions that make the convention relevant.
  - `guidance`: The selection-time guidance the user should see.
  - `output_implications`: Follow-on implications for generated instructions or project-local outputs. Record these as deferred implications, not as active-generation steps.
  - `deferred_follow_on`: Later bounded work that may use this convention after stack selection is confirmed.

### Generation Targets
- `agents_outputs`: The `AGENTS.md` instruction fragments this profile can generate or update.
- `skill_outputs`: Skills this profile can create, enable, or tailor.
- `config_outputs`: `.codex/config.toml` or related project-local config fragments this profile can generate.
- `template_outputs`: Project structure, starter docs, or code templates this profile can generate.
- `command_outputs`: Standard setup, lint, test, build, and verification commands this profile contributes.
- `review_checklist_outputs`: Review and verification checklists this profile contributes.

### Safety And Mutation Rules
- `mutable_at_selection_time`: What may change during the narrow official-doc freshness check.
- `immutable_without_maintainer_review`: What must not be auto-rewritten from ad hoc research.
- `unsupported_combinations`: Known invalid combinations that must be blocked or escalated.

### Traceability
- `source_refs`: Canonical source links for the profile.
- `change_log_ref`: Where maintainers should record profile changes if the blueprint later introduces a stack catalog changelog.

## Variant Option Contract
Each option on a profile axis must define the fields below.

### Identity
- `option_id`: Stable machine-readable identifier such as `hexagonal`.
- `axis_id`: The parent decision axis.
- `label`: Short user-facing label.
- `status`: `active`, `experimental`, `deprecated`, or `archived`.

### User Guidance
- `short_description`: One concise plain-language explanation suitable for UI option text.
- `best_for`: What kinds of projects or teams this option suits best.
- `avoid_when`: When this option is a poor fit.
- `main_tradeoffs`: What the user gives up by choosing it.
- `example`: A short illustrative example, pseudo-structure, or code-style snippet when that helps selection.
- `non_technical_explanation`: Optional extra explanation for users without technical background.

### Implementation Implications
- `architecture_effects`: How this option changes boundaries, module responsibilities, or dependency direction.
- `structure_effects`: How this option changes folder layout or package organization.
- `tooling_effects`: How this option changes tooling or required checks.
- `code_style_effects`: How this option changes naming, patterns, test style, or implementation conventions.
- `skill_effects`: Skills that should be generated, enabled, or adjusted because of this choice.
- `config_effects`: Project-local Codex config or role changes that follow from this choice.

### Compatibility And Selection Rules
- `recommended`: Whether this is the recommended option for a common default case.
- `prerequisites`: Requirements before this option is valid.
- `incompatible_with`: Other option IDs or profile IDs that conflict with this option.
- `follow_up_questions`: Extra questions triggered only when this option is selected.

### Traceability
- `source_refs`: Official or approved secondary references for this option.
- `last_reviewed`: Date the option guidance was last checked.

## Selection Flow Rules
- Run stack-profile selection only after the Project Idea Document is current and the project has reached stack-selection readiness.
- The Technical Specification may still be draft or partial at first-time stack selection if the current project already has enough problem, flow, constraint, and architecture-direction clarity to make deliberate stack choices.
- If the user explicitly asks to select the stack before those artifacts exist, gather the minimum missing stack-selection inputs inline and let stack selection proceed as part of Spec-First instead of blocking on bootstrap artifacts.
- Use structured choice UI when available so the user can choose among curated options.
- Surface profile-backed recommendation sets, recommended option combinations, and convention overlays as visibly `Suggested`; do not silently convert them to `Confirmed`.
- When the user accepts or overrides a recommendation set, capture that decision explicitly in the project stack-selection artifact.
- Every option shown to the user must include:
  - short description
  - best-fit guidance
  - main tradeoff
- Include an example when the option would be materially easier to understand with one.
- Keep examples short in the selection UI. Longer examples belong in supporting text or references.
- For existing projects, map repo reality first and ask only for missing or future-target choices.
- For new projects, ask the minimum stack and variant questions needed to produce a coherent stack-selection artifact and then route back to finish the stack-aware Technical Specification before milestone planning or project-local generation when needed.

## Deferred Follow-On Rules
- Treat the curated stack profile as the primary blueprint source of truth during active stack selection.
- Do not pull narrow official-doc freshness review into the active recommendation-capture step unless a later bounded phase explicitly takes ownership.
- Do not let ad hoc web research silently rewrite the reusable profile.
- If the project later runs a bounded freshness review and finds a material conflict:
  - adjust only the later project-local outputs when the change is low-risk and clearly supported by official docs, or
  - flag the reusable profile for maintainer review when the change would alter blueprint truth.

## Mapping Rules
- Reusable stack profile data belongs in the blueprint.
- Selected profile IDs and selected option IDs belong in the current project's stack-selection artifact.
- The project's Project Idea Document and Technical Specification should record only project-relevant reasoning and architecture decisions, not the full reusable profile payload.
- Generated `AGENTS.md`, skills, and `.codex` config should be derived outputs, not the canonical source of stack truth.

## Minimum Project Artifact Capture
When a project selects a stack profile and variant options, capture at least:
- selected `profile_id`
- selected `version`
- selected `axis_id` to `option_id` mappings
- why each selected option fits the current project
- profile-backed recommendation sets reviewed, accepted, declined, or deferred
- convention overlays shown or accepted
- explicit override decisions and why they were made
- any deferred freshness or project-local-generation follow-up noted at selection time
- any project-local deviations from the curated profile

## Recommended Authoring Pattern
- Start with a small set of officially supported stack profiles.
- Give each profile only the variant axes that genuinely matter for project shape, code conventions, or agent behavior.
- Prefer one focused skill per recurring workflow instead of one broad skill per entire stack.
- Keep `AGENTS.md` outputs concise and behavioral.
- Keep long rationale, examples, and references in skill docs or profile references rather than bloating generated instructions.

## Suggested Future Layout
If the blueprint later adds a stack catalog, use a structure like:

```text
.agents/
  stack-profiles/
    backend/
      nodejs-express/
        profile.toml
        references/
        assets/
        skills/
    frontend/
      nextjs/
        profile.toml
        references/
        assets/
        skills/
```

The exact storage format can be TOML, YAML, or Markdown frontmatter-backed docs, but the contract fields above must remain representable without ambiguity.
