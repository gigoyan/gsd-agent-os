---
name: gsd-export-blueprint-package
description: export the reusable gsd blueprint into a versioned root-only package by consolidating skills, templates, and stack profiles, copying root agents and project files, and marking git clean or dirty state. use when the user needs a file-count-friendly chatgpt project package, a portable blueprint export, export audit metadata, or a compact upload bundle for reusable gsd workflow assets.
---

# GSD Export Blueprint Package

Export the reusable GSD blueprint into a compact, versioned package for ChatGPT project upload or portable review.

## Source Of Truth

- Use `.gsd/blueprint-manifest.json` as the authoritative inventory.
- Inspect the manifest schema before exporting and adapt to the fields that are present.
- Do not invent a separate file inventory for copied blueprint source files.
- Include the current skill's `SKILL.md` if it is present under `.agents/skills/gsd-export-blueprint-package/` at execution time, even during first-run validation before downstream installs have caught up.

## Primary Purpose

- Reduce ChatGPT Project file count by consolidating GSD skill instructions into `skills.md`.
- Reduce template file count by consolidating `.planning/templates/**` into `templates.md`.
- Reduce stack-profile file count by consolidating `.agents/stack-profiles/**` into root-level `stack-profiles-<domain>.md` files.
- Copy repository root `AGENTS.md` to export-root `agents.md`.
- Copy repository root `PROJECT.md` to export-root `project.md`.
- Record Git branch, commit, clean or dirty state, source lists, skip reasons, warnings, and checksums.
- Produce a package that can be compared against older or newer exports.

## Non-Trigger Conditions

- User wants to audit, install, or update a blueprint in a target repository. Use `$gsd-sync-blueprint audit-only|install|update <TARGET_REPOSITORY_PATH>`.
- User wants to execute project work, plan a milestone, update vault memory, or generate project-local `.codex` outputs.

## Input Contract

- Source repository path, or the current working directory somewhere inside the reusable GSD blueprint repository.
- Optional output root. Default: `.gsd/exports/`.
- Optional dry run.
- Optional explicit dirty-export acknowledgement. Dirty exports are allowed by default but must be marked clearly.

## Output Contract

- Versioned export directory under the selected output root:
  - `export-manifest.json`
  - `checksums.sha256`
  - `git-status.txt`
  - `skills.md`
  - `templates.md`
  - `stack-profiles-<domain>.md` for each stack-profile domain with manifest-listed content
  - `agents.md`
  - `project.md`
- Export manifest with generated time, source repository path, manifest path, blueprint version, Git identity, dirty flag, generated files, consolidated skill sources, consolidated template sources, consolidated stack-profile sources, root copied sources, skipped sources with reasons, warnings, and counts.
- Console summary of the package path and classification counts.

## Workflow

1. Read `.planning/tool-capabilities.md` when present before running repository commands.
2. Read `.gsd/blueprint-manifest.json` and confirm the manifest has a usable `files` array.
3. Run the bundled script:

   ```bash
   python .agents/skills/gsd-export-blueprint-package/scripts/export_blueprint_package.py
   ```

4. Use `--dry-run` first when changing the script or when the user asks for a preview.
5. Use `--repo-root` when running from outside the repository.
6. Use `--output-root` for validation exports so temporary packages can be deleted after inspection.
7. Review `export-manifest.json`, `git-status.txt`, and `checksums.sha256` before reporting success.

## Script Behavior

- Build the directory name as:

  `gsd-blueprint-<version>-<YYYYMMDD-HHMMSS>-<branch>-<short-commit>-<clean|dirty>/`

- Use `blueprint_version`, `version`, or `unversioned` when no version field exists.
- Use Git for branch, short commit, and dirty state when available.
- Use `nogit` for branch and commit fields when Git is unavailable or the source is not a Git repository.
- Treat any `git status --porcelain` output as dirty, including untracked files.
- Allow dirty exports by default, but mark the package directory and manifest as dirty.

## Consolidation Rules

- Consolidate `.agents/skills/**/SKILL.md` into `skills.md`.
- Sort skill sources by relative path.
- Use the skill directory name as each section title.
- Preserve each source `SKILL.md` body exactly inside its section.
- Consolidate `.planning/templates/**` into `templates.md`.
- Sort template sources by relative path under `.planning/templates/`.
- Use the template-relative path as each section title.
- Preserve template content exactly inside its section.
- Do not copy original template files separately.
- Consolidate manifest-listed `.agents/stack-profiles/<domain>/<profile>/**` source files into root-level domain files named `stack-profiles-<domain>.md`.
- Create only stack-profile domain files that have concrete, readable manifest-listed source content.
- Expand wildcard stack-profile manifest entries deterministically from the filesystem under `.agents/stack-profiles/**`.
- Use `stack-profiles-other.md` for stack-profile domains outside the known set: `backend`, `frontend`, `data`, `auth`, `integration`, `hosting`, and `observability`.
- Sort stack-profile sections by normalized source path.
- Use the stack-profile-relative path, such as `backend/nodejs-service/profile.toml`, as each section title.
- Preserve Markdown stack-profile sources directly; wrap non-Markdown text sources such as TOML, JSON, YAML, text, and template files in fenced code blocks for readable Markdown output.
- Do not copy original stack-profile files separately.

## Copy Rules

- For each manifest entry:
  - consolidate `.agents/skills/**/SKILL.md` into `skills.md`
  - consolidate `.planning/templates/**` into `templates.md`
  - consolidate `.agents/stack-profiles/**` into root-level `stack-profiles-<domain>.md` files
  - copy `AGENTS.md` to root-level `agents.md`
  - copy `PROJECT.md` to root-level `project.md`
  - skip every other manifest source file after recording a reason
- Never create export subdirectories.
- Never copy source blueprint files into a subdirectory.
- Never copy a broad `.planning/` directory.
- Never copy `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/CONTEXT_INDEX.md`, `.planning/milestones/**`, `.planning/phases/**`, or `.planning/verification/**`.
- Never copy `.planning/templates/**` separately; these belong only in `templates.md`.
- Never copy `.agents/stack-profiles/**` separately; these belong only in `stack-profiles-<domain>.md` files.
- Never copy files outside the repository root.
- Never follow symlinks outside the repository root.

## Safety Rules

- Do not sync, install, or modify target project repositories.
- Do not write Obsidian vault memory.
- Do not write generated project-local `.codex` files.
- Do not export runtime planning history as copied files.
- Do not create export subdirectories.
- Do not silently clean, reset, or hide dirty Git state.
- Do not add `.gsd/exports/**` to the blueprint manifest.
- If ownership is unclear, skip the file and report the reason.

## Completion Check

- Python syntax check passed for the script.
- Dry run printed the planned output directory, consolidated files, root copied files, and skipped files.
- Temporary output export created the expected files.
- `skills.md` contains consolidated GSD skill sections.
- `templates.md` contains consolidated `.planning/templates/**` sections.
- `stack-profiles-<domain>.md` files contain manifest-listed stack-profile source sections for each domain with content.
- `agents.md` exists at the export root.
- `project.md` exists at the export root.
- No export subdirectories exist.
- `.planning/templates/**` files are not duplicated outside `templates.md`.
- `.agents/stack-profiles/**` files are not duplicated outside domain-level `stack-profiles-<domain>.md` files.
- `export-manifest.json` includes `consolidated_stack_profile_sources`, stack-profile generated files, and stack-profile counts.
- Dirty Git state is represented in the package directory and `export-manifest.json` when the repository is dirty.
- `checksums.sha256` includes hashes only for final root-level export files that can be checksummed without self-reference.
- `checksums.sha256` includes every generated `stack-profiles-<domain>.md` file.
- Temporary validation output is removed when repository convention prefers no generated artifacts left behind.
