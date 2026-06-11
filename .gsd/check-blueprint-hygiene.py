#!/usr/bin/env python
"""Validate reusable blueprint source for project/test contamination."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".gsd" / "blueprint-manifest.json"

SKIP_OWNERS = {"project_preserve", "generated_project_local"}
ALLOWED_GENERIC_PATH_MARKERS = {
    ".planning/tmp/",
    ".planning/tmp",
    ".planning/verification/",
    ".planning/verification",
}
EXPLICIT_MARKERS = [
    "D:\\CDM\\",
    "D:/CDM/",
    "projects/TMS",
    "gsd-vault-spec-first-flow",
    "SmartEcosystem",
    "M005-P03",
    "M006-final-cleanup-gate",
    "validationRepo",
    "externalValidation",
    "deployment-baseline.md",
    "docs/deployment-reference.md",
    "static-flow-intelligence-scaffold",
    ".planning/validation/",
    ".planning/validation",
    ".planning/flow-intelligence/flows/FL-9001-",
]
REGEX_MARKERS = [
    ("TMS", re.compile(r"\bTMS\b")),
    ("milestone-phase-label", re.compile(r"\bM00[3-7][-\s]+P0[2-4]\b")),
    ("raw-src-fixture-id", re.compile(r"\bsrc-00[12]\b")),
    ("numbered-fixture-source-id", re.compile(r"\bfixture-source-\d+\b")),
    ("numbered-fixture-claim-id", re.compile(r"\bfixture-claim-\d+\b")),
    ("numbered-fixture-unknown-id", re.compile(r"\bfixture-unknown-\d+\b")),
    ("numbered-source-template-id", re.compile(r"\bsource-\d{3}\b")),
    ("numbered-source-material-id", re.compile(r"\bsrc-\d{3}\b")),
    ("opaque-source-sequence-placeholder", re.compile(r"\bsrc-###\b")),
    ("numbered-claim-id", re.compile(r"\bclaim-\d{3}\b")),
    ("numbered-unknown-id", re.compile(r"\bunknown-\d{3}\b")),
    ("line-range-anchor", re.compile(r"\b(?:lines|anchor)-\d{2,}(?:-\d{2,})?\b")),
    ("dated-browser-run-fixture", re.compile(r"\b20\d{6}-\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*\b")),
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_manifest() -> dict[str, object]:
    if not MANIFEST.exists():
        fail(".gsd/blueprint-manifest.json is missing")
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f".gsd/blueprint-manifest.json is invalid JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        fail(".gsd/blueprint-manifest.json must contain a files array")
    return data


def manifest_sources() -> list[Path]:
    data = load_manifest()
    sources: set[Path] = set()
    for item in data["files"]:
        if not isinstance(item, dict):
            fail("manifest files entries must be objects")
        owner = item.get("owner")
        if owner in SKIP_OWNERS:
            continue
        rel = item.get("path")
        if not isinstance(rel, str) or not rel:
            fail("manifest files entries must include a non-empty path")
        if "*" in rel:
            continue
        path = (ROOT / rel).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            fail(f"manifest path escapes repository root: {rel}")
        if path.is_file():
            sources.add(path)

    for extra in [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "PROJECT.md", ROOT / "README.md"]:
        if extra.exists():
            sources.add(extra.resolve())

    exports = (ROOT / ".gsd" / "exports").resolve()
    return sorted(
        path
        for path in sources
        if not str(path).startswith(str(exports))
    )


def allowed(marker: str, line: str) -> bool:
    if marker in ALLOWED_GENERIC_PATH_MARKERS:
        return True
    if "INTERNAL_VALIDATOR_FIXTURE_" in line:
        return True
    if "browser-run://<run-id>/summary.json" in line:
        return True
    if "<fixture-project-id>" in line or "fixture-project" in line:
        return True
    return False


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings
    rel = path.relative_to(ROOT).as_posix()
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized = line.replace("\\", "/")
        candidates: list[tuple[str, str]] = []
        for marker in EXPLICIT_MARKERS:
            marker_normalized = marker.replace("\\", "/")
            if marker in line or marker_normalized in normalized:
                candidates.append((marker, line))
        for label, pattern in REGEX_MARKERS:
            if pattern.search(line):
                candidates.append((label, line))
        for marker, raw_line in candidates:
            if rel == ".gsd/check-blueprint-hygiene.py":
                continue
            if allowed(marker, raw_line):
                continue
            findings.append(f"{rel}:{line_number}: {marker}: {raw_line.strip()}")
    return findings


def main() -> int:
    findings: list[str] = []
    for path in manifest_sources():
        findings.extend(scan_file(path))
    if findings:
        print("FAIL: reusable blueprint source contains non-allowlisted contamination markers")
        for finding in findings:
            print(finding)
        return 1
    print("PASS: reusable blueprint source hygiene markers are clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
