#!/usr/bin/env python
"""Audit and safely clean reusable GSD blueprint source candidates."""

from __future__ import annotations

import argparse
import os
import importlib.util
import json
import posixpath
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

MANIFEST_RELATIVE_PATH = ".gsd/blueprint-manifest.json"
BLUEPRINT_NAME = "gsd"
BLUEPRINT_OWNER_CLASSES = {"blueprint_replace", "managed_block"}
STARTER_OWNER_CLASSES = {
    "bootstrap_then_managed_block",
    "bootstrap_if_missing",
    "project_preserve",
}
RUNTIME_OWNER_CLASSES = {"generated_project_local"}
RUNTIME_PREFIXES = (
    ".codex/",
    ".claude/",
    ".planning/evidence/",
    ".planning/flow-intelligence/",
    ".planning/qa/",
    ".planning/story-knowledge-mirror/",
    ".planning/tmp/",
    ".planning/ui-discovery/",
    ".planning/user-stories/",
    ".planning/" "validation/",
    ".planning/verification/",
)
RUNTIME_EXACT = {
    ".codex",
    ".claude",
    ".planning/archive",
    ".planning/evidence",
    ".planning/flow-intelligence",
    ".planning/qa",
    ".planning/story-knowledge-mirror",
    ".planning/tmp",
    ".planning/ui-discovery",
    ".planning/user-stories",
    ".planning/" "validation",
    ".planning/verification",
}
EXPORT_PREFIXES = (".gsd/exports/",)
PYTHON_CACHE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PYTHON_CACHE_FILE_SUFFIXES = (".pyc", ".pyo")
FINAL_RUNTIME_HISTORY_DIRS = (
    ".codex",
    ".claude",
    ".planning/archive",
    ".planning/evidence",
    ".planning/flow-intelligence",
    ".planning/milestones",
    ".planning/phases",
    ".planning/qa",
    ".planning/story-knowledge-mirror",
    ".planning/tmp",
    ".planning/ui-discovery",
    ".planning/user-stories",
    ".planning/" "validation",
    ".planning/verification",
)
STARTER_SURFACES = {
    "AGENTS.md",
    "CLAUDE.md",
    "PROJECT.md",
    "README.md",
    ".gitignore",
    ".planning/CODEBASE_MAP.md",
    ".planning/CONTEXT_INDEX.md",
    ".planning/REQUIREMENTS.md",
    ".planning/ROADMAP.md",
    ".planning/STATE.md",
    ".planning/tool-capabilities.md",
}
STARTER_HISTORY_ROOTS = {
    ".planning/milestones",
    ".planning/phases",
}
STARTER_RESET_TEMPLATES = {
    ".planning/CONTEXT_INDEX.md": ".planning/templates/context-index-template.md",
    ".planning/ROADMAP.md": ".planning/templates/roadmap-template.md",
    ".planning/STATE.md": ".planning/templates/state-template.md",
}
EXPORT_SCRIPT_RELATIVE_PATH = ".agents/skills/gsd-export-blueprint-package/scripts/export_blueprint_package.py"
CLEANUP_SKILL_PATH = ".agents/skills/gsd-clean-blueprint-source/SKILL.md"
CLEANUP_SCRIPT_PATH = ".agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py"
BLUEPRINT_IDENTITY_REQUIRED_PATHS = (
    ".agents/skills/gsd-run-milestone/SKILL.md",
    ".agents/skills/gsd-clean-blueprint-source/SKILL.md",
    ".agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py",
    ".gsd/managed-blocks/agents-operating-contract.md",
)
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

PROJECT_PATH_LEAK_PATTERN = "|".join(
    [
        r"D:[\\/]",
        "projects/" + "T" + "MS",
        "gsd-vault" + "-spec-first-flow",
        "Smart" + "Ecosystem",
        "validation" + "Repo",
        "external" + "Validation",
    ]
)

CONTAMINATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("project/path leaks", re.compile(PROJECT_PATH_LEAK_PATTERN)),
    ("opaque source/claim/fixture numbering", re.compile(r"\b(?:src-\d{3}|source-\d{3}|claim-\d{3}|unknown-\d{3}|fixture-(?:source|claim|unknown)-\d+|src-###)\b")),
    ("concrete line-range anchors", re.compile(r"\b(?:lines|anchor)-\d{2,}(?:-\d{2,})?\b")),
    ("history-shaped fixture timestamps", re.compile(r"\b20\d{6}-\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*\b")),
    ("generated runtime defaults under .planning/**", re.compile(r"\.planning/(?:evidence|flow-intelligence|qa|tmp|user-stories|validation|verification)/")),
    ("stale export references", re.compile(r"\.gsd/exports/|export-lock\.json|export-manifest\.json|checksums\.sha256")),
    ("cleanup-session history in starter surfaces", re.compile(r"cleanup(?: skill| session| report| history)|blueprint source cleanup", re.IGNORECASE)),
)


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    owner: str
    sync_strategy: str


@dataclass(frozen=True)
class ClassifiedPath:
    path: str
    path_class: str
    reason: str


@dataclass(frozen=True)
class CleanupOperation:
    action: str
    path: str
    reason: str
    source_path: str = ""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit and safely clean reusable blueprint cleanup candidates.")
    parser.add_argument("--audit", action="store_true", help="Run audit-only classification.")
    parser.add_argument(
        "--finalize-blueprint-source-cleanup",
        action="store_true",
        help=(
            "Destructive one-go cleanup for the reusable blueprint source repo only. "
            "Requires --confirm-blueprint-source-repo and --confirm-destroy-runtime-planning-state."
        ),
    )
    parser.add_argument(
        "--apply-generated",
        action="store_true",
        help="Internal guardrail: remove changed runtime/generated artifacts after fail-closed classification.",
    )
    parser.add_argument(
        "--reset-starter-surfaces",
        action="store_true",
        help="Internal guardrail: reset deterministic starter surfaces from template content.",
    )
    parser.add_argument(
        "--validate-export-integration",
        action="store_true",
        help="Internal guardrail: validate cleanup skill/script export inclusion and balanced root-only export sections without writing files.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview apply/reset operations without modifying files.")
    parser.add_argument(
        "--confirm-live",
        action="store_true",
        help="Required with apply/reset operations when --dry-run is not present.",
    )
    parser.add_argument(
        "--confirm-blueprint-source-repo",
        action="store_true",
        help="Required with --finalize-blueprint-source-cleanup to acknowledge this is the reusable blueprint source repo.",
    )
    parser.add_argument(
        "--confirm-destroy-runtime-planning-state",
        action="store_true",
        help=(
            "Required with --finalize-blueprint-source-cleanup to acknowledge runtime planning state, "
            "phase, milestone, verification, adapter, generated, and cache artifacts will be removed or reset."
        ),
    )
    parser.add_argument("--repo-root", help="Repository root. Defaults to nearest parent with the blueprint manifest.")
    args = parser.parse_args(argv)
    selected_modes = [
        args.audit,
        args.finalize_blueprint_source_cleanup,
        args.apply_generated,
        args.reset_starter_surfaces,
        args.validate_export_integration,
    ]
    if not any(selected_modes):
        args.audit = True
    if sum(bool(mode) for mode in selected_modes) > 1:
        parser.error(
            "--audit, --finalize-blueprint-source-cleanup, --apply-generated, "
            "--reset-starter-surfaces, and --validate-export-integration are mutually exclusive"
        )
    if (args.confirm_blueprint_source_repo or args.confirm_destroy_runtime_planning_state) and not args.finalize_blueprint_source_cleanup:
        parser.error("blueprint-source confirmation flags are only valid with --finalize-blueprint-source-cleanup")
    if args.finalize_blueprint_source_cleanup:
        if args.dry_run or args.confirm_live:
            parser.error("--finalize-blueprint-source-cleanup cannot be combined with --dry-run or --confirm-live")
        if not args.confirm_blueprint_source_repo or not args.confirm_destroy_runtime_planning_state:
            parser.error(
                "--finalize-blueprint-source-cleanup requires --confirm-blueprint-source-repo "
                "and --confirm-destroy-runtime-planning-state"
            )
    if args.confirm_live and args.dry_run:
        parser.error("--confirm-live cannot be combined with --dry-run")
    if args.validate_export_integration and (args.dry_run or args.confirm_live):
        parser.error("--validate-export-integration is always no-write and cannot be combined with --dry-run or --confirm-live")
    if (args.apply_generated or args.reset_starter_surfaces) and not args.dry_run and not args.confirm_live:
        parser.error("live apply/reset requires --confirm-live; use --dry-run to preview")
    return args


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize_path(raw_path: str) -> str:
    candidate = raw_path.replace("\\", "/").strip()
    if candidate.startswith("./"):
        candidate = candidate[2:]
    normalized = posixpath.normpath(candidate)
    return "" if normalized == "." else normalized


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / MANIFEST_RELATIVE_PATH).is_file():
            return candidate
    fail("could not find repository root; pass --repo-root")


def resolve_repo_root(value: str | None) -> Path:
    if value:
        root = Path(value).expanduser().resolve()
        if not (root / MANIFEST_RELATIVE_PATH).is_file():
            fail(f"manifest not found under --repo-root: {root / MANIFEST_RELATIVE_PATH}")
        return root
    return find_repo_root(Path.cwd())


def load_manifest_data(repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"manifest is not valid JSON: {exc}")


def load_manifest(repo_root: Path) -> dict[str, ManifestEntry]:
    data = load_manifest_data(repo_root)
    files = data.get("files")
    if not isinstance(files, list):
        fail("manifest must contain a files array")

    entries: dict[str, ManifestEntry] = {}
    for item in files:
        if not isinstance(item, dict):
            fail("manifest file entries must be objects")
        raw_path = item.get("path")
        owner = item.get("owner")
        strategy = item.get("sync_strategy")
        if not isinstance(raw_path, str) or not isinstance(owner, str) or not isinstance(strategy, str):
            fail("manifest entries must include path, owner, and sync_strategy strings")
        path = normalize_path(raw_path)
        if not path or path.startswith("../") or posixpath.isabs(path) or re.match(r"^[A-Za-z]:", path):
            fail(f"manifest path is invalid: {raw_path}")
        entries[path] = ManifestEntry(path=path, owner=owner, sync_strategy=strategy)
    return entries


def git_status_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "git status failed")

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line:
            continue
        payload = line[3:]
        if " -> " in payload:
            _, payload = payload.split(" -> ", 1)
        path = normalize_path(payload.strip().strip('"'))
        if path:
            paths.add(path)
    return sorted(paths, key=str.lower)


def generated_runtime_path(path: str) -> bool:
    parts = set(path.split("/"))
    return (
        path.endswith(PYTHON_CACHE_FILE_SUFFIXES)
        or bool(parts & PYTHON_CACHE_PARTS)
        or path in RUNTIME_EXACT
        or any(path.startswith(prefix) for prefix in RUNTIME_PREFIXES)
    )


def classify_path(path: str, manifest: dict[str, ManifestEntry]) -> ClassifiedPath:
    entry = manifest.get(path)
    if entry:
        if entry.owner in BLUEPRINT_OWNER_CLASSES:
            return ClassifiedPath(path, "blueprint truth", f"manifest owner {entry.owner}")
        if entry.owner in STARTER_OWNER_CLASSES:
            return ClassifiedPath(path, "starter project surfaces", f"manifest owner {entry.owner}")
        if entry.owner in RUNTIME_OWNER_CLASSES:
            return ClassifiedPath(path, "runtime/generated artifacts", f"manifest owner {entry.owner}")
        return ClassifiedPath(path, "unknown/unclassified", f"manifest owner {entry.owner} has no cleanup class")

    if any(path.startswith(prefix) for prefix in EXPORT_PREFIXES):
        return ClassifiedPath(path, "exports", "export output path")
    if generated_runtime_path(path):
        return ClassifiedPath(path, "runtime/generated artifacts", "runtime/generated path")
    if (
        path in STARTER_SURFACES
        or path in STARTER_HISTORY_ROOTS
        or path.startswith(".planning/milestones/")
        or path.startswith(".planning/phases/")
    ):
        return ClassifiedPath(path, "starter project surfaces", "explicit starter or workflow surface")
    if path.startswith(".agents/skills/") or path.startswith(".agents/stack-profiles/") or path.startswith(".gsd/") or path.startswith(".planning/templates/"):
        return ClassifiedPath(path, "blueprint truth", "explicit blueprint source path")
    return ClassifiedPath(path, "unknown/unclassified", "no manifest or explicit path class")


def repo_path(repo_root: Path, path: str) -> Path:
    candidate = repo_root / Path(*path.split("/"))
    try:
        resolved = candidate.resolve()
        resolved.relative_to(repo_root)
    except ValueError:
        fail(f"path resolves outside repository root: {path}")
    return resolved


def readable_text_path(repo_root: Path, path: str) -> bool:
    candidate = repo_root / Path(*path.split("/"))
    if not candidate.is_file():
        return False
    if candidate.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        candidate.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return True


def scan_contamination(repo_root: Path, paths: list[str]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        if not readable_text_path(repo_root, path):
            continue
        text = (repo_root / Path(*path.split("/"))).read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            normalized = line.replace("\\", "/")
            for category, pattern in CONTAMINATION_PATTERNS:
                if pattern.search(normalized):
                    findings[category].append(f"{path}:{line_number}")
    return dict(sorted(findings.items()))


def unknown_paths(classified: list[ClassifiedPath]) -> list[ClassifiedPath]:
    return [item for item in classified if item.path_class == "unknown/unclassified"]


def fail_if_unknown(classified: list[ClassifiedPath]) -> None:
    unknowns = unknown_paths(classified)
    if not unknowns:
        return
    print("Cleanup status: blocked")
    print("Unknown/unclassified paths require an explicit manifest entry or path-class rule before apply/reset:")
    for item in unknowns:
        print(f"  - {item.path}: {item.reason}")
    raise SystemExit(2)


def append_unique_operation(operations: list[CleanupOperation], seen: set[str], operation: CleanupOperation) -> None:
    key = f"{operation.action}:{operation.path}"
    if key in seen:
        return
    seen.add(key)
    operations.append(operation)


def path_to_repo_relative(repo_root: Path, candidate: Path) -> str:
    try:
        return normalize_path(candidate.resolve().relative_to(repo_root).as_posix())
    except ValueError:
        fail(f"path resolves outside repository root: {candidate}")


def cache_cleanup_operations(repo_root: Path) -> list[CleanupOperation]:
    operations: list[CleanupOperation] = []
    seen: set[str] = set()
    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)
        dirs[:] = [directory for directory in dirs if directory != ".git"]
        for directory in list(dirs):
            if directory not in PYTHON_CACHE_PARTS:
                continue
            cache_path = root_path / directory
            rel_path = path_to_repo_relative(repo_root, cache_path)
            append_unique_operation(
                operations,
                seen,
                CleanupOperation("delete", rel_path, "python/cache artifact"),
            )
            dirs.remove(directory)
        for filename in files:
            if not filename.endswith(PYTHON_CACHE_FILE_SUFFIXES):
                continue
            cache_file = root_path / filename
            rel_path = path_to_repo_relative(repo_root, cache_file)
            append_unique_operation(
                operations,
                seen,
                CleanupOperation("delete", rel_path, "python/cache artifact"),
            )
    return sorted(operations, key=lambda item: item.path.lower())


def generated_cleanup_operations(repo_root: Path, classified: list[ClassifiedPath]) -> list[CleanupOperation]:
    operations: list[CleanupOperation] = [
        CleanupOperation("delete", item.path, item.reason)
        for item in classified
        if item.path_class == "runtime/generated artifacts"
    ]
    seen = {f"{operation.action}:{operation.path}" for operation in operations}
    for operation in cache_cleanup_operations(repo_root):
        append_unique_operation(operations, seen, operation)
    return sorted(operations, key=lambda item: item.path.lower())


def final_runtime_history_operations(repo_root: Path) -> list[CleanupOperation]:
    operations: list[CleanupOperation] = []
    for path in FINAL_RUNTIME_HISTORY_DIRS:
        target = repo_root / Path(*path.split("/"))
        if target.exists() or target.is_symlink():
            operations.append(CleanupOperation("delete", path, "runtime planning or adapter history"))
    return operations


def starter_reset_operations(repo_root: Path) -> list[CleanupOperation]:
    operations: list[CleanupOperation] = []
    for target, source in sorted(STARTER_RESET_TEMPLATES.items()):
        source_path = repo_path(repo_root, source)
        if not source_path.is_file():
            fail(f"starter reset template is missing: {source}")
        operations.append(CleanupOperation("reset", target, "starter template content", source))
    return operations


def print_operations(title: str, operations: list[CleanupOperation], dry_run: bool) -> None:
    print(title)
    print(f"Mode: {'dry-run; no files modified' if dry_run else 'live apply'}")
    if not operations:
        print("  - none")
        return
    for operation in operations:
        source = f" from {operation.source_path}" if operation.source_path else ""
        print(f"  - {operation.action}: {operation.path}{source} ({operation.reason})")


def remove_generated_path(repo_root: Path, path: str) -> None:
    target = repo_path(repo_root, path)
    if not target.exists() and not target.is_symlink():
        return
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    else:
        target.unlink()


def reset_starter_path(repo_root: Path, operation: CleanupOperation) -> None:
    source = repo_path(repo_root, operation.source_path)
    target = repo_path(repo_root, operation.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def apply_operations(repo_root: Path, operations: list[CleanupOperation], dry_run: bool) -> None:
    if dry_run:
        return
    for operation in operations:
        if operation.action == "delete":
            remove_generated_path(repo_root, operation.path)
        elif operation.action == "reset":
            reset_starter_path(repo_root, operation)
        else:
            fail(f"unsupported cleanup operation: {operation.action}")


def assert_blueprint_source_repo(repo_root: Path) -> None:
    manifest_data = load_manifest_data(repo_root)
    if manifest_data.get("blueprint_name") != BLUEPRINT_NAME:
        fail(
            "final cleanup refused: manifest blueprint_name is not "
            f"{BLUEPRINT_NAME!r}; this command is only for the reusable blueprint source repo"
        )
    manifest_paths = {
        normalize_path(str(item.get("path", "")))
        for item in manifest_data.get("files", [])
        if isinstance(item, dict)
    }
    missing_manifest_paths = [
        path
        for path in (CLEANUP_SKILL_PATH, CLEANUP_SCRIPT_PATH)
        if path not in manifest_paths
    ]
    if missing_manifest_paths:
        fail(
            "final cleanup refused: cleanup sources are missing from the blueprint manifest: "
            + ", ".join(missing_manifest_paths)
        )
    missing_identity_paths = [
        path
        for path in BLUEPRINT_IDENTITY_REQUIRED_PATHS
        if not repo_path(repo_root, path).exists()
    ]
    if missing_identity_paths:
        fail(
            "final cleanup refused: required blueprint-source identity paths are missing: "
            + ", ".join(missing_identity_paths)
        )


def run_python_script(repo_root: Path, relative_path: str, script_args: list[str]) -> None:
    script_path = repo_path(repo_root, relative_path)
    if not script_path.is_file():
        fail(f"validation script is missing: {relative_path}")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(script_path), *script_args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if result.stdout.strip():
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        fail(f"validation command failed: {relative_path} {' '.join(script_args)}")


def run_strict_validation(repo_root: Path, include_export_dry_run: bool) -> None:
    validate_export_integration(repo_root)
    if include_export_dry_run:
        run_python_script(
            repo_root,
            EXPORT_SCRIPT_RELATIVE_PATH,
            ["--mode", "full", "--dry-run", "--include-dirty"],
        )
    run_python_script(repo_root, ".gsd/check-blueprint-hygiene.py", [])


def final_cleanup_operations(repo_root: Path, classified: list[ClassifiedPath]) -> list[CleanupOperation]:
    operations: list[CleanupOperation] = []
    seen: set[str] = set()
    for operation in generated_cleanup_operations(repo_root, classified):
        append_unique_operation(operations, seen, operation)
    for operation in final_runtime_history_operations(repo_root):
        append_unique_operation(operations, seen, operation)
    for operation in starter_reset_operations(repo_root):
        append_unique_operation(operations, seen, operation)
    return sorted(operations, key=lambda item: (item.action, item.path.lower()))


def finalize_blueprint_source_cleanup(repo_root: Path, classified: list[ClassifiedPath]) -> int:
    assert_blueprint_source_repo(repo_root)
    fail_if_unknown(classified)
    print("GSD blueprint source final cleanup")
    print("Mode: live final cleanup; destructive runtime planning cleanup is confirmed")
    print("WARNING: this resets starter planning state and removes runtime planning, adapter, generated, and cache artifacts.")
    print("WARNING: this command is intended only for the reusable GSD blueprint source repository.")
    print()
    print("Pre-cleanup strict validation:")
    run_strict_validation(repo_root, include_export_dry_run=True)

    operations = final_cleanup_operations(repo_root, classified)
    print()
    print_operations("Final cleanup operations", operations, dry_run=False)
    apply_operations(repo_root, operations, dry_run=False)

    print()
    print("Post-cleanup strict validation:")
    run_strict_validation(repo_root, include_export_dry_run=False)

    final_cache_operations = cache_cleanup_operations(repo_root)
    if final_cache_operations:
        print()
        print_operations("Final cache sweep", final_cache_operations, dry_run=False)
        apply_operations(repo_root, final_cache_operations, dry_run=False)

    print()
    print("Final cleanup status: applied")
    return 0


def load_export_module(repo_root: Path) -> Any:
    export_script = repo_path(repo_root, EXPORT_SCRIPT_RELATIVE_PATH)
    if not export_script.is_file():
        fail(f"export script is missing: {EXPORT_SCRIPT_RELATIVE_PATH}")
    spec = importlib.util.spec_from_file_location("gsd_export_blueprint_package", export_script)
    if spec is None or spec.loader is None:
        fail(f"could not load export script: {EXPORT_SCRIPT_RELATIVE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_export_integration(repo_root: Path) -> int:
    export_module = load_export_module(repo_root)
    manifest, _manifest_hash = export_module.load_manifest(repo_root)
    render_plan = export_module.build_render_plan(repo_root, manifest)
    content_by_file = render_plan.content_by_file.copy()
    content_by_file["git-status.txt"] = export_module.git_status_text(export_module.collect_git_info(repo_root))
    generated_files = export_module.generated_files_for(render_plan)
    outputs = export_module.output_lock_entries(render_plan, content_by_file)
    export_module.validate_content_plan(render_plan, content_by_file, outputs, generated_files)

    missing_sources = [
        path
        for path in (CLEANUP_SKILL_PATH, CLEANUP_SCRIPT_PATH)
        if path == CLEANUP_SKILL_PATH and path not in render_plan.skill_sources
        or path == CLEANUP_SCRIPT_PATH and path not in render_plan.skill_script_sources
    ]
    if missing_sources:
        fail("export validation failed: cleanup sources missing from render plan: " + ", ".join(missing_sources))

    nested_generated = sorted(path for path in generated_files if "/" in path or "\\" in path)
    if nested_generated:
        fail("export validation failed: generated export files are not root-only: " + ", ".join(nested_generated))

    output_by_target = {
        output.get("target_file"): output
        for output in outputs
        if isinstance(output.get("target_file"), str)
    }
    skill_output = output_by_target.get("skills.md")
    script_output = output_by_target.get(export_module.SKILL_SCRIPTS_TARGET)
    if not skill_output or skill_output.get("output_kind") != "consolidated":
        fail("export validation failed: skills.md consolidated output is missing")
    if not script_output or script_output.get("output_kind") != "consolidated":
        fail("export validation failed: skill-scripts.md consolidated output is missing")

    skill_ids = {
        section.get("section_id")
        for section in skill_output.get("sections", [])
        if isinstance(section, dict)
    }
    script_ids = {
        section.get("section_id")
        for section in script_output.get("sections", [])
        if isinstance(section, dict)
    }
    expected_skill_id = "gsd-clean-blueprint-source"
    expected_script_id = "gsd-clean-blueprint-source/scripts/clean_blueprint_source.py"
    if expected_skill_id not in skill_ids:
        fail(f"export validation failed: missing cleanup skill section id {expected_skill_id}")
    if expected_script_id not in script_ids:
        fail(f"export validation failed: missing cleanup script section id {expected_script_id}")

    print("GSD cleanup export integration validation")
    print("Mode: no-write validation; export render plan only")
    print(f"Cleanup skill included: {CLEANUP_SKILL_PATH}")
    print(f"Cleanup script included: {CLEANUP_SCRIPT_PATH}")
    print("Root-only export files: pass")
    print("Balanced consolidated section markers: pass")
    print("Export integration status: pass")
    return 0


def print_audit(repo_root: Path, classified: list[ClassifiedPath], contamination: dict[str, list[str]]) -> int:
    class_counts = Counter(item.path_class for item in classified)
    unknowns = unknown_paths(classified)

    print("GSD blueprint source cleanup audit")
    print(f"Repository: {repo_root}")
    print("Mode: audit-only; no files modified")
    print()
    print("Path classes:")
    for path_class in [
        "blueprint truth",
        "starter project surfaces",
        "runtime/generated artifacts",
        "exports",
        "unknown/unclassified",
    ]:
        print(f"  - {path_class}: {class_counts.get(path_class, 0)}")

    print()
    print("Changed path classification:")
    if not classified:
        print("  - none")
    for item in classified:
        print(f"  - {item.path}: {item.path_class} ({item.reason})")

    print()
    print("Contamination categories:")
    if not contamination:
        print("  - none found in changed readable text files")
    for category, locations in contamination.items():
        print(f"  - {category}: {len(locations)}")
        for location in locations[:10]:
            print(f"    - {location}")
        if len(locations) > 10:
            print(f"    - ... {len(locations) - 10} more")

    print()
    if unknowns:
        print("Audit status: blocked")
        print("Unknown/unclassified paths require an explicit manifest entry or path-class rule before cleanup can run:")
        for item in unknowns:
            print(f"  - {item.path}: {item.reason}")
    else:
        print("Audit status: pass")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = resolve_repo_root(args.repo_root)
    manifest = load_manifest(repo_root)
    changed_paths = git_status_paths(repo_root)
    classified = [classify_path(path, manifest) for path in changed_paths]
    contamination = scan_contamination(repo_root, changed_paths)
    if args.audit:
        return print_audit(repo_root, classified, contamination)
    if args.finalize_blueprint_source_cleanup:
        return finalize_blueprint_source_cleanup(repo_root, classified)
    if args.validate_export_integration:
        return validate_export_integration(repo_root)

    fail_if_unknown(classified)
    operations: list[CleanupOperation] = []
    if args.apply_generated:
        operations.extend(generated_cleanup_operations(repo_root, classified))
    if args.reset_starter_surfaces:
        operations.extend(starter_reset_operations(repo_root))

    print_operations("GSD blueprint source cleanup plan", operations, args.dry_run)
    apply_operations(repo_root, operations, args.dry_run)
    if not args.dry_run:
        print("Cleanup status: applied")
    else:
        print("Cleanup status: dry-run pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
