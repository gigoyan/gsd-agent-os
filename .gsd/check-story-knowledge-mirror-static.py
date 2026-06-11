#!/usr/bin/env python
"""Validate the static story knowledge mirror dry-run fixture."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_VALIDATOR_FIXTURE_STORY_ID = "US-0001-internal-validator-fixture"
STORY_ID = INTERNAL_VALIDATOR_FIXTURE_STORY_ID
INTERNAL_VALIDATOR_FIXTURE_PROJECT_ID = "fixture-project"
RUN_ID = "story-knowledge-mirror-dry-run-fixture"
MIRROR_ROOT = ROOT / ".planning" / "story-knowledge-mirror"
RUN_ROOT = MIRROR_ROOT / "mirror-runs" / RUN_ID
STORY_ROOT = ROOT / ".planning" / "user-stories" / STORY_ID
SKILL_PATH = ROOT / ".agents" / "skills" / "gsd-publish-story-knowledge" / "SKILL.md"
ALLOWED_EVIDENCE_STATUSES = {"Confirmed", "Suggested", "Unknown"}
RAW_OR_SENSITIVE_MARKERS = [
    '"cookies"',
    '"authorization"',
    '"cookie"',
    '"token"',
    '"password"',
    '"privateKey"',
    '"storage-summary"',
    '"console.log"',
    '"action-log"',
    '"networkPayload"',
    '"domSnapshot"',
    "BEGIN PRIVATE KEY",
    "[REDACTED_SECRET]",
    "screenshots/",
    "page-states/",
    "dom-snapshots/",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def parse_json_file(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def check_evidence_status(value: object, location: str) -> None:
    if value not in ALLOWED_EVIDENCE_STATUSES:
        fail(f"{location} has invalid evidence_status {value!r}")


def walk_statuses(value: object, location: str) -> set[str]:
    statuses: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "evidence_status":
                check_evidence_status(child, child_location)
                statuses.add(str(child))
            else:
                statuses.update(walk_statuses(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            statuses.update(walk_statuses(child, f"{location}[{index}]"))
    return statuses


def check_skill() -> None:
    if not SKILL_PATH.exists():
        fail("missing .agents/skills/gsd-publish-story-knowledge/SKILL.md")
    text = SKILL_PATH.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("gsd-publish-story-knowledge SKILL.md missing YAML frontmatter")
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("gsd-publish-story-knowledge SKILL.md frontmatter is not closed")
    frontmatter = match.group("body")
    if "name: gsd-publish-story-knowledge" not in frontmatter:
        fail("gsd-publish-story-knowledge SKILL.md frontmatter missing expected name")
    if "description:" not in frontmatter:
        fail("gsd-publish-story-knowledge SKILL.md frontmatter missing description")
    required_terms = [
        ".planning/story-knowledge-mirror/",
        "publish-source.md",
        "dry-run",
        "--apply",
        "managed block",
        "Confirmed",
        "Suggested",
        "Unknown",
        "Do Not Own",
        "Do not generate user stories",
        "Do not run QA",
        "Do not browse",
        "Do not write Vault notes",
        "source_id",
        "claim_id",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail(f"gsd-publish-story-knowledge SKILL.md missing required guidance terms: {', '.join(missing)}")


def check_required_files() -> None:
    required = [
        MIRROR_ROOT / "mirror-config.json",
        MIRROR_ROOT / "mirror-lock.json",
        MIRROR_ROOT / "mirror-manifest.json",
        MIRROR_ROOT / "mirror-report.md",
        RUN_ROOT / "actions.json",
        RUN_ROOT / "create-pass.json",
        RUN_ROOT / "repeat-pass.json",
        RUN_ROOT / "dry-run-report.md",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing {path.relative_to(ROOT)}")


def check_config() -> dict[str, object]:
    data = parse_json_file(MIRROR_ROOT / "mirror-config.json")
    if not isinstance(data, dict):
        fail("mirror-config.json must be an object")
    if data.get("schema_version") != 1:
        fail("mirror-config.json schema_version must be 1")
    if data.get("mode_default") != "dry-run":
        fail("mirror-config.json mode_default must be dry-run")
    if data.get("apply_requires_explicit_approval") is not True:
        fail("mirror-config.json must require explicit apply approval")
    if data.get("vault_project_id") != INTERNAL_VALIDATOR_FIXTURE_PROJECT_ID:
        fail("mirror-config.json must use the fixture project id")
    namespace = data.get("vault_namespace")
    if namespace != f"projects/{INTERNAL_VALIDATOR_FIXTURE_PROJECT_ID}/":
        fail("mirror-config.json must use the fixture project-owned vault namespace")
    if data.get("source_root") != ".planning/user-stories/":
        fail("mirror-config.json source_root must stay under user stories")
    if data.get("mirror_root") != ".planning/story-knowledge-mirror/":
        fail("mirror-config.json mirror_root must stay under story knowledge mirror")
    return data


def check_manifest() -> dict[str, object]:
    data = parse_json_file(MIRROR_ROOT / "mirror-manifest.json")
    if not isinstance(data, dict):
        fail("mirror-manifest.json must be an object")
    if data.get("schema_version") != 1:
        fail("mirror-manifest.json schema_version must be 1")
    if data.get("run_id") != RUN_ID:
        fail("mirror-manifest.json run_id must match fixture")
    if data.get("mode") != "dry-run":
        fail("mirror-manifest.json mode must be dry-run")
    if data.get("writes_performed") is not False:
        fail("mirror-manifest.json must record writes_performed false")
    items = data.get("items")
    if not isinstance(items, list) or len(items) != 1:
        fail("mirror-manifest.json must contain one fixture item")
    item = items[0]
    if not isinstance(item, dict):
        fail("mirror-manifest.json item must be an object")
    if item.get("source_id") != STORY_ID:
        fail("mirror-manifest.json item source_id must match fixture story")
    if item.get("source_type") != "user_story":
        fail("mirror-manifest.json item source_type must be user_story")
    source_path = f".planning/user-stories/{STORY_ID}/publish-source.md"
    if item.get("source_path") != source_path:
        fail("mirror-manifest.json item source_path must point at publish-source.md")
    if item.get("source_content_hash") != sha256_file(STORY_ROOT / "publish-source.md"):
        fail("mirror-manifest.json source_content_hash must match publish-source.md")
    if item.get("source_metadata_hash") != sha256_file(STORY_ROOT / "source-links.json"):
        fail("mirror-manifest.json source_metadata_hash must match source-links.json")
    if item.get("first_run_action") != "create":
        fail("mirror-manifest.json first_run_action must be create")
    if item.get("repeat_run_action") != "unchanged":
        fail("mirror-manifest.json repeat_run_action must be unchanged")
    if item.get("vault_path") != f"projects/{INTERNAL_VALIDATOR_FIXTURE_PROJECT_ID}/knowledge/user-stories/{STORY_ID}.md":
        fail("mirror-manifest.json vault_path must stay in the project-owned namespace")
    statuses = walk_statuses(data, "mirror-manifest.json")
    if not {"Confirmed", "Suggested", "Unknown"}.issubset(statuses):
        fail("mirror-manifest.json must preserve Confirmed, Suggested, and Unknown statuses")
    return data


def check_lock() -> None:
    data = parse_json_file(MIRROR_ROOT / "mirror-lock.json")
    if not isinstance(data, dict):
        fail("mirror-lock.json must be an object")
    if data.get("schema_version") != 1:
        fail("mirror-lock.json schema_version must be 1")
    if data.get("mirror_version") != 1:
        fail("mirror-lock.json mirror_version must be 1")
    if data.get("vault_project_id") != INTERNAL_VALIDATOR_FIXTURE_PROJECT_ID:
        fail("mirror-lock.json vault_project_id must match config")
    items = data.get("items")
    if not isinstance(items, list) or len(items) != 1:
        fail("mirror-lock.json must contain one item")
    item = items[0]
    if item.get("source_id") != STORY_ID:
        fail("mirror-lock.json source_id must match fixture story")
    if item.get("last_action") != "created":
        fail("mirror-lock.json last_action must record created after first dry run")
    if item.get("status") != "current":
        fail("mirror-lock.json item status must be current")
    if data.get("removed_source_items") != []:
        fail("mirror-lock.json removed_source_items must be an empty P01 placeholder")


def check_run_actions() -> None:
    data = parse_json_file(RUN_ROOT / "actions.json")
    if not isinstance(data, dict):
        fail("actions.json must be an object")
    if data.get("schema_version") != 1:
        fail("actions.json schema_version must be 1")
    if data.get("run_id") != RUN_ID:
        fail("actions.json run_id must match fixture")
    if data.get("writes_performed") is not False:
        fail("actions.json must record writes_performed false")
    first = data.get("first_run_actions")
    repeat = data.get("repeat_run_actions")
    if not isinstance(first, list) or not isinstance(repeat, list):
        fail("actions.json must contain first and repeat action arrays")
    if [item.get("action") for item in first if isinstance(item, dict)] != ["create"]:
        fail("actions.json first_run_actions must record one create")
    if [item.get("action") for item in repeat if isinstance(item, dict)] != ["unchanged"]:
        fail("actions.json repeat_run_actions must record one unchanged")
    statuses = walk_statuses(data, "actions.json")
    if "Confirmed" not in statuses:
        fail("actions.json must preserve compact source traceability statuses")
    create_pass = parse_json_file(RUN_ROOT / "create-pass.json")
    repeat_pass = parse_json_file(RUN_ROOT / "repeat-pass.json")
    if not isinstance(create_pass, dict) or create_pass.get("classification") != "create":
        fail("create-pass.json classification must be create")
    if not isinstance(repeat_pass, dict) or repeat_pass.get("classification") != "unchanged":
        fail("repeat-pass.json classification must be unchanged")
    if create_pass.get("writes_performed") is not False or repeat_pass.get("writes_performed") is not False:
        fail("dry-run pass files must record writes_performed false")


def check_reports() -> None:
    for path in [MIRROR_ROOT / "mirror-report.md", RUN_ROOT / "dry-run-report.md"]:
        text = path.read_text(encoding="utf-8")
        for required in [
            "dry-run",
            "writes_performed: false",
            "create",
            "unchanged",
            "Confirmed",
            "Suggested",
            "Unknown",
        ]:
            if required not in text:
                fail(f"{path.relative_to(ROOT)} missing {required!r}")


def check_no_raw_or_sensitive_markers() -> None:
    for path in sorted(MIRROR_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".har"}:
            fail(f"raw binary/browser artifact copied into mirror outputs: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in RAW_OR_SENSITIVE_MARKERS:
            if marker.lower() in lowered:
                fail(f"{path.relative_to(ROOT)} contains raw or sensitive marker {marker!r}")


def main() -> None:
    check_skill()
    if not MIRROR_ROOT.exists():
        print("SKIP: no story-knowledge mirror fixture artifacts present; skill guidance is valid")
        return
    check_required_files()
    check_config()
    check_manifest()
    check_lock()
    check_run_actions()
    check_reports()
    check_no_raw_or_sensitive_markers()
    print("PASS: static story knowledge mirror dry-run artifacts are valid")


if __name__ == "__main__":
    main()
