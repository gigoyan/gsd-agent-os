---
name: gsd-export-blueprint-package
description: export the reusable gsd blueprint into a versioned root-only package by consolidating skills, templates, and stack profiles, copying root agents and project files, and marking git clean or dirty state. use when the user needs a file-count-friendly chatgpt project package, a portable blueprint export, export audit metadata, or a compact upload bundle for reusable gsd workflow assets.
---

# GSD Export Blueprint Package

Export the reusable GSD blueprint into a compact, versioned, root-only package for ChatGPT Project upload or portable review.

## Source Of Truth

- Use `.gsd/blueprint-manifest.json` as the authoritative inventory.
- Inspect the manifest schema before exporting and require a usable `files` array.
- The current source files, source hashes, source manifest, and export renderer version are authoritative.
- A previous export is only an incremental cache. It must never become source of truth.
- Include the current skill's `SKILL.md` if it is present under `.agents/skills/gsd-export-blueprint-package/` at execution time, even during first-run validation before downstream installs have caught up.

## Export Modes

- `full`: canonical correctness path and default. Regenerates all export content from the current blueprint source.
- `incremental`: creates a new versioned export directory using `--base-export <path>` as a cache. Reuses unchanged copied files and unchanged consolidated sections only when the previous `export-lock.json`, target files, section markers, source hashes, and rendered hashes prove reuse is safe. Falls back to regenerating affected targets when evidence is insufficient.
- `incremental-strict`: same cache intent as `incremental`, but fails instead of falling back when the previous lock, renderer version, target file, marker boundaries, or rendered hashes are missing, unsupported, malformed, ambiguous, or inconsistent.

## CLI

Run the bundled script:

```bash
python .agents/skills/gsd-export-blueprint-package/scripts/export_blueprint_package.py --mode full
```

Supported options:

- `--mode full|incremental|incremental-strict`
- `--base-export <path>` for incremental modes
- `--verify-against-full-render` to compare incremental output content against a fresh full render
- `--repo-root <path>`
- `--output-root <path>`
- `--dry-run`
- `--include-dirty`

If `--base-export` is omitted in an incremental mode, fail clearly. Automatic previous-export detection is not part of the current contract.

## Output Contract

- Versioned export directory under the selected output root.
- Root files only; no export subdirectories.
- Always generate:
  - `index.md`
  - `export-lock.json`
  - `export-manifest.json`
  - `checksums.sha256`
  - `git-status.txt`
  - `skills.md`
  - `skill-scripts.md` when text/code files exist under `.agents/skills/**/scripts/**`
  - `skill-references.md` when supported UTF-8 text files exist under `.agents/skills/**/references/**`
  - `gsd-tools.md` when selected reusable `.gsd/**` tools, validators, configs, or fixtures are manifest-listed
  - `templates.md`
  - `stack-profiles-<domain>.md` for each stack-profile domain with manifest-listed content
  - `agents.md`
  - `claude.md` when root `CLAUDE.md` is present and manifest-listed
  - `project.md`
- Always regenerate metadata files instead of copying them from the previous export.
- `checksums.sha256` covers all final root-level export files except itself.

## Index File

- Generate root-level `index.md` for every export.
- Explain that the package is a flattened ChatGPT Project representation, not the original repository layout.
- Document the mapping from `.agents/skills/**/SKILL.md`, `.agents/skills/**/scripts/**`, `.agents/skills/**/references/**`, `.planning/templates/**`, `.agents/stack-profiles/**`, `AGENTS.md`, `CLAUDE.md`, `PROJECT.md`, `.gsd/blueprint-manifest.json`, skipped child-agent configs, runtime planning history, `.codex/**`, and generated `.claude/**` to their export representation or skip reason.
- Make clear that separate skill folders, script folders, reference folders, template files, stack-profile folders, runtime planning files, project history, and generated runtime adapter outputs such as `.codex/**` and generated `.claude/**` are intentionally absent.

## Consolidation Rules

- Consolidate `.agents/skills/**/SKILL.md` into `skills.md`.
- Sort skill sources by relative path.
- Use the skill directory name as each section ID and title.
- Consolidate text/code files under `.agents/skills/**/scripts/**` into `skill-scripts.md` when at least one script exists.
- Sort skill script sections by normalized source path.
- Use `<skill-name>/scripts/<relative-script-path>` as each skill script section ID and title.
- Render skill scripts as fenced code blocks with a language inferred from file extension, using fence length that preserves script text safely.
- Do not execute skill scripts during export.
- Consolidate supported UTF-8 text files under `.agents/skills/**/references/**` into `skill-references.md` when at least one supported reference exists.
- Discover skill reference files from manifest entries and filesystem discovery under `.agents/skills/*/references/**`.
- Sort skill reference sections deterministically by skill name, then reference path.
- Use `<skill-name>/references/<relative-reference-path>` as each skill reference section ID and title.
- Render skill references without fenced code wrapping and include source, skill, and reference metadata comments in each section.
- Use group name `skill-references`.
- Do not hardcode any specific skill name when consolidating references.
- Consolidate `.planning/templates/**` into `templates.md`.
- Sort template sources by relative path under `.planning/templates/`.
- Use the template-relative path as each section ID and title.
- Consolidate selected manifest-listed reusable `.gsd/**` runtime tools, validators, configs, and internal fixtures into `gsd-tools.md`.
- Sort `.gsd` tool sections by normalized source path.
- Use the `.gsd` filename, such as `browser-evidence.py`, as each section ID and title.
- Render `.gsd` tools as fenced code blocks with a language inferred from file extension.
- Do not execute `.gsd` tools during export.
- Consolidate manifest-listed `.agents/stack-profiles/<domain>/<profile>/**` source files into root-level domain files named `stack-profiles-<domain>.md`.
- Expand wildcard stack-profile manifest entries deterministically from the filesystem under `.agents/stack-profiles/**`.
- Use `stack-profiles-other.md` for stack-profile domains outside the known set: `backend`, `frontend`, `data`, `auth`, `integration`, `hosting`, and `observability`.
- Sort stack-profile sections by normalized source path.
- Use the stack-profile-relative path, such as `backend/nodejs-service/profile.toml`, as each section ID and title.
- Preserve Markdown stack-profile sources directly. Wrap non-Markdown text sources such as TOML, JSON, YAML, text, and template files in fenced code blocks.
- Do not copy original skill, template, or stack-profile files separately.

## Section Markers

Every consolidated section must be wrapped with stable markers:

```md
[START marker: GSD-EXPORT-SECTION, group, section-id]
...
[END marker: GSD-EXPORT-SECTION, group, section-id]
```

Allowed groups:

- `skills`
- `skill-scripts`
- `skill-references`
- `templates`
- `gsd-tools`
- `stack-profiles`

Markers must be balanced, deterministic, and unique within each target file. Incremental patching must fail or regenerate the affected target when marker boundaries cannot be proven safe.

## Export Lock

- Generate root-level `export-lock.json` for every export.
- Record schema version, export renderer version, generated time, generic source repository placeholder, source manifest path, source manifest hash, blueprint version, Git branch, Git commit, dirty flag, export mode, base export path, generated files, and outputs.
- For consolidated outputs, record target file, output kind, group, section ID, source path, source hash, rendered section hash, content mode, start marker, and end marker.
- For copied outputs, record target file, output kind, source path, source hash, and target hash.
- Use the lock only to validate reuse from a previous export. Do not use it to define current source inventory.

## Copy And Skip Rules

- Copy `AGENTS.md` to root-level `agents.md`.
- Copy `CLAUDE.md` to root-level `claude.md` when present and manifest-listed.
- Copy `PROJECT.md` to root-level `project.md`.
- Skip every other manifest source after recording a reason unless it belongs to a consolidation rule.
- Never create export subdirectories.
- Never copy source blueprint files into a subdirectory.
- Never copy `.gsd` tools directly as root files; consolidate selected reusable `.gsd` tools into `gsd-tools.md`.
- Never copy a broad `.planning/` directory.
- Never copy `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/CONTEXT_INDEX.md`, `.planning/milestones/**`, `.planning/phases/**`, `.planning/verification/**`, or `.planning/archive/**`.
- Never copy generated project-local runtime adapter outputs such as `.codex/**` and generated `.claude/**`.
- Never copy files outside the repository root.
- Never follow symlinks outside the repository root.
- Consolidate supported text/code `.agents/skills/**/scripts/**` files into `skill-scripts.md`; do not list consolidated scripts as skipped.
- Skip unsupported binary, compiled, cache, or non-text files under `.agents/skills/**/scripts/**` with reason `unsupported non-text skill script asset`.
- Consolidate supported UTF-8 text `.agents/skills/**/references/**` files into `skill-references.md`; do not list consolidated references as skipped.
- Skip binary files, cache files, compiled files, oversized files, `.DS_Store`, `__pycache__`, files outside the repository root, and symlinks resolving outside the repository root under `.agents/skills/**/references/**`.
- If ownership is unclear, skip the file and report the reason.

## Manifest Requirements

`export-manifest.json` must keep existing summary fields and add:

- `export_mode`
- `base_export_path`
- `export_renderer_version`
- incremental fallback status and reasons
- generated `index.md`
- generated `export-lock.json`
- `skill_scripts_file`, `consolidated_skill_script_sources`, and `skill_scripts_consolidated`
- `skill_references_file`, `consolidated_skill_reference_sources`, and `skill_references_consolidated`
- `gsd_tools_file`, `consolidated_gsd_tool_sources`, and `gsd_tools_consolidated`
- changed, added, and removed sections
- changed copied files
- regenerated target files
- full-render verification result when requested

## Incremental Fallback Rules

- Missing or invalid previous lock: fall back in `incremental`; fail in `incremental-strict`.
- Unsupported renderer version: fall back in `incremental`; fail in `incremental-strict`.
- Missing previous target file: regenerate affected target in `incremental`; fail in `incremental-strict`.
- Missing, malformed, duplicate, nested, or ambiguous section markers: regenerate affected target in `incremental`; fail in `incremental-strict`.
- Previous target content hash mismatch: regenerate affected target in `incremental`; fail in `incremental-strict`.
- Source content changed: replace the corresponding section or copied file from current source.
- Source added: add the section in deterministic order.
- Source removed: omit the old section and record it as removed.
- Metadata is always regenerated.

## Full-Render Verification

- `--verify-against-full-render` compares incremental reusable output content against a fresh full render from the same current source and renderer version.
- `export-manifest.json` records the verification result.
- The export fails when compared content differs.
- Mode-specific metadata files are excluded from the comparison because they intentionally contain mode, base path, and timestamp differences.

## Workflow

1. Read `.planning/tool-capabilities.md` when present before running repository commands.
2. Read `.gsd/blueprint-manifest.json`.
3. Use `--dry-run` first when changing the script or when the user asks for a preview.
4. Use `--repo-root` when running from outside the repository.
5. Use `--output-root` for validation exports so temporary packages can be deleted after inspection.
6. For incremental validation, create a temporary full export first and pass it as `--base-export`.
7. Review `index.md`, `export-lock.json`, `export-manifest.json`, `git-status.txt`, and `checksums.sha256` before reporting success.

## Completion Check

- Python syntax check passed for the script.
- Dry-run full export passed.
- Temporary full export created the expected root files.
- Temporary incremental export using the full export as base passed.
- `index.md` explains the flattened export mapping.
- `export-lock.json` exists and maps sources to copied files or consolidated sections.
- `skills.md`, `templates.md`, and generated `stack-profiles-<domain>.md` files contain balanced section markers.
- `skill-scripts.md` exists when text/code skill scripts exist.
- Every text/code script under `.agents/skills/**/scripts/**` has exactly one section in `skill-scripts.md`.
- Script section markers are balanced.
- Script source hashes and rendered section hashes are recorded in `export-lock.json`.
- Consolidated scripts are not listed as skipped.
- Lock sections match consolidated file sections.
- `checksums.sha256` includes all final root-level export files except itself.
- `checksums.sha256` includes `skill-scripts.md` when generated.
- `skill-references.md` exists when supported skill references exist.
- Every supported UTF-8 text file under `.agents/skills/**/references/**` has exactly one section in `skill-references.md`.
- Reference section markers use group `skill-references` and IDs shaped `<skill-name>/references/<relative-reference-path>`.
- Reference sections include the owning skill, source path, and reference path metadata comments.
- Reference source hashes and rendered section hashes are recorded in `export-lock.json`.
- Consolidated references are not listed as skipped.
- `checksums.sha256` includes `skill-references.md` when generated.
- `gsd-tools.md` exists when manifest-listed reusable `.gsd` text/code/config tools or fixtures exist.
- Every selected `.gsd` tool has exactly one section in `gsd-tools.md`.
- `checksums.sha256` includes `gsd-tools.md` when generated.
- `agents.md` and `project.md` exist at the export root.
- `claude.md` exists at the export root when root `CLAUDE.md` is present and manifest-listed.
- No export subdirectories exist.
- Runtime planning history and generated runtime adapter outputs such as `.codex/**` and generated `.claude/**` are not exported.
- `export-manifest.json` records export mode, renderer version, generated index and lock files, incremental changes, fallback status, regenerated targets, and full-render verification result when requested.
- Temporary validation output is removed when repository convention prefers no generated artifacts left behind.
