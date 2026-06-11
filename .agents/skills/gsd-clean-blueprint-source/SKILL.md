---
name: gsd-clean-blueprint-source
description: Audit reusable GSD blueprint source cleanup candidates by manifest ownership and path class before guarded generated cleanup or starter reset is applied. Use after blueprint maintenance when source, starter, generated, export, or contamination residue needs fail-closed classification and safe cleanup sequencing.
---

# GSD Clean Blueprint Source

Audit reusable blueprint source cleanup candidates before any cleanup is applied, then use guarded internal cleanup steps only after the audit is understood and unblocked.

## Workflow
1. Read `.planning/tool-capabilities.md` and avoid commands recorded as blocked.
2. Run the audit script from the repository root. Audit is the default and must be no-change:

```bash
python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --audit
```

3. Review the path-class summary, contamination categories, and blocked/unknown paths.
4. If any unknown or unclassified path is present, stop. Add an explicit manifest entry or path-class rule in a later scoped phase before cleanup can proceed.
5. Preview generated/runtime cleanup and starter-surface reset with dry-run guarded commands when the user needs to inspect the cleanup plan without mutation:

```bash
python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --apply-generated --dry-run
python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --reset-starter-surfaces --dry-run
```

6. Run Strict Validation before reporting or considering any export action:

```bash
python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --validate-export-integration
python .agents/skills/gsd-export-blueprint-package/scripts/export_blueprint_package.py --mode full --dry-run --include-dirty
python .gsd/check-blueprint-hygiene.py
```

7. For final reusable blueprint-source cleanup, use the explicit one-go finalizer. It is non-interactive, live, and intentionally destructive to runtime planning history, generated adapters, generated validation/evidence outputs, and Python/cache artifacts:

```bash
python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --finalize-blueprint-source-cleanup --confirm-blueprint-source-repo --confirm-destroy-runtime-planning-state
```

8. The finalizer must refuse to run unless the repository identity checks prove this is the reusable GSD blueprint source repo. It resets starter surfaces from templates, removes runtime planning/history directories, removes generated/cache artifacts, runs strict validation before and after cleanup, and performs a final cache sweep.
9. Do not run the finalizer in downstream project repositories. It is designed to remove current GSD runtime files such as milestone, phase, verification, evidence, adapter, and state history. The long confirmation flags are required so accidental execution fails closed.
10. Use Final Reporting in chat or, if a persistent local report is explicitly needed, under ignored `.planning/tmp/`. Do not write cleanup-session history, validation transcripts, or export decisions into starter planning surfaces such as `.planning/STATE.md`, `.planning/ROADMAP.md`, or `.planning/CONTEXT_INDEX.md`. The final evidence rule is no cleanup-session history in starter surfaces.

## Export Policy
- Confirmed: full export mode is the canonical regeneration path and builds export content from current blueprint source; previous exports are caches only.
- Confirmed: cleanup skill/script inclusion is validated by the cleanup script's no-write `--validate-export-integration` mode and the export script's dry-run render-plan validation.
- Confirmed: generated export directories under `.gsd/exports/` are generated artifacts. The cleanup skill must not delete or regenerate them by default.
- Confirmed: live export regeneration is a separate explicit export action through `$gsd-export-blueprint-package` or the export script, normally after dry-run validation passes.
- Suggested: use a temporary output root for validation exports when a written package is needed only for inspection, then remove that temporary output according to the active phase or user instruction.
- Unknown: whether future blueprint maintenance should keep the latest generated export by policy or clean all exports after distribution. Until that is decided, cleanup remains dry-run-first and does not delete exports by default.

## Current Scope
- Classifies paths as blueprint truth, starter project surfaces, runtime/generated artifacts, exports, or unknown/unclassified.
- Audit mode is the default and remains no-change.
- Guarded generated/runtime cleanup can remove only paths classified as runtime/generated artifacts plus Python/cache artifacts discovered under the repo root.
- Guarded starter reset writes deterministic starter/template content for `.planning/STATE.md`, `.planning/CONTEXT_INDEX.md`, and `.planning/ROADMAP.md`.
- Final blueprint-source cleanup removes runtime planning/history directories, generated adapter/evidence directories, and Python/cache artifacts, then resets starter state surfaces from templates.
- No-write export integration validation proves the cleanup skill is included in `skills.md`, the cleanup script is included in `skill-scripts.md`, export outputs are root-only, and consolidated section markers are balanced.
- Reports semantic contamination categories including project/path leaks, opaque source/claim/fixture numbering, concrete line-range anchors, history-shaped fixture timestamps, generated runtime defaults under `.planning/**`, stale export references, and cleanup-session history in starter surfaces.
- Unknown or unclassified paths block apply/reset until a later phase defines ownership or cleanup behavior.
- Export deletion and live export regeneration are explicit follow-up actions, not default cleanup behavior.

## Completion Check
- Audit output is deterministic and no-change.
- Any unknown path is reported clearly instead of being silently cleaned.
- Apply/reset dry-runs are reviewed before live mutation.
- Generated/runtime cleanup deletes only classified runtime/generated artifacts.
- Python/cache artifacts such as `__pycache__`, `*.pyc`, `*.pyo`, `.pytest_cache`, `.mypy_cache`, and `.ruff_cache` are removed during generated cleanup/final cleanup and are not treated as source.
- Starter reset uses deterministic template content and does not preserve cleanup-session history.
- Strict validation passes: cleanup export integration validation, full export dry-run, and blueprint hygiene.
- Final reporting avoids starter state/history surfaces and uses chat or ignored temporary output only.
- Export deletion or live regeneration happens only when a later active phase or user explicitly authorizes it.
