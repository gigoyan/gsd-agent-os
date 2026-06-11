#!/usr/bin/env python
"""Validate the static story knowledge mirror apply/conflict/removal fixture."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_VALIDATOR_FIXTURE_STORY_ID = "US-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_REMOVED_STORY_ID = "US-REMOVED-internal-validator-fixture"
STORY_ID = INTERNAL_VALIDATOR_FIXTURE_STORY_ID
REMOVED_STORY_ID = INTERNAL_VALIDATOR_FIXTURE_REMOVED_STORY_ID
RUN_ID = "story-knowledge-mirror-apply-fixture-validation"
MIRROR_ROOT = ROOT / ".planning" / "story-knowledge-mirror"
RUN_ROOT = MIRROR_ROOT / "mirror-runs" / RUN_ID
FIXTURE_ROOT = MIRROR_ROOT / "fixtures" / "vault" / "projects" / "fixture-project"
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
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def walk_statuses(value: object, location: str) -> set[str]:
    statuses: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "evidence_status":
                if child not in ALLOWED_EVIDENCE_STATUSES:
                    fail(f"{child_location} has invalid evidence_status {child!r}")
                statuses.add(str(child))
            else:
                statuses.update(walk_statuses(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            statuses.update(walk_statuses(child, f"{location}[{index}]"))
    return statuses


def managed_block(text: str, source_id: str) -> str:
    start = f"<!-- GSD-MIRROR:START {source_id} -->"
    end = f"<!-- GSD-MIRROR:END {source_id} -->"
    pattern = re.escape(start) + r"\n(?P<body>.*?)\n" + re.escape(end)
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        fail(f"missing managed block for {source_id}")
    return match.group("body")


def check_skill_guidance() -> None:
    if not SKILL_PATH.exists():
        fail("missing .agents/skills/gsd-publish-story-knowledge/SKILL.md")
    text = SKILL_PATH.read_text(encoding="utf-8")
    required_terms = [
        "apply mode remains non-default",
        "explicit approval metadata",
        "preserve manual content outside managed blocks",
        "manual edits inside managed blocks",
        "conflict",
        "tombstone/archive",
        "repo-local fixture",
        "projects/<fixture-project-id>/",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail(f"gsd-publish-story-knowledge SKILL.md missing fixture guidance terms: {', '.join(missing)}")


def check_config() -> None:
    data = parse_json_file(MIRROR_ROOT / "mirror-config.json")
    if not isinstance(data, dict):
        fail("mirror-config.json must be an object")
    if data.get("mode_default") != "dry-run":
        fail("apply mode must not be the default")
    if data.get("apply_requires_explicit_approval") is not True:
        fail("apply mode must require explicit approval")
    if data.get("removed_source_default") != "tombstone-or-archive":
        fail("removed_source_default must be tombstone-or-archive")
    managed = data.get("managed_block")
    if not isinstance(managed, dict):
        fail("mirror-config.json managed_block must be an object")
    if managed.get("start_format") != "<!-- GSD-MIRROR:START <source-id> -->":
        fail("managed_block start_format is incorrect")
    if managed.get("end_format") != "<!-- GSD-MIRROR:END <source-id> -->":
        fail("managed_block end_format is incorrect")
    apply_fixture = data.get("apply_fixture")
    if not isinstance(apply_fixture, dict):
        fail("mirror-config.json must record apply_fixture metadata")
    if apply_fixture.get("run_id") != RUN_ID:
        fail("apply_fixture run_id must match fixture")
    if apply_fixture.get("fixture_only") is not True:
        fail("apply_fixture must be fixture-only")
    if apply_fixture.get("approval_metadata_required") is not True:
        fail("apply_fixture must require approval metadata")
    if apply_fixture.get("real_vault_writes") is not False:
        fail("apply_fixture must record no real Vault writes")
    if apply_fixture.get("fixture_vault_namespace") != "projects/fixture-project/":
        fail("apply_fixture must target projects/fixture-project/")


def check_namespace() -> None:
    data = parse_json_file(RUN_ROOT / "namespace-validation.json")
    if not isinstance(data, dict):
        fail("namespace-validation.json must be an object")
    if not isinstance(data.get("target_project_path"), str):
        fail("namespace-validation.json must record the targeted project path")
    if data.get("project_file_read") is not True:
        fail("namespace-validation.json must record project_file_read true")
    if data.get("vault_project_id") != "fixture-project":
        fail("namespace-validation.json must resolve vault_project_id fixture-project")
    if data.get("vault_namespace") != "projects/fixture-project/":
        fail("namespace-validation.json must resolve projects/fixture-project/")
    if data.get("fallback_used") is not False:
        fail("namespace-validation.json must not use fallback when the fixture PROJECT.md is available")


def check_run_actions() -> dict[str, object]:
    data = parse_json_file(RUN_ROOT / "actions.json")
    if not isinstance(data, dict):
        fail("actions.json must be an object")
    if data.get("run_id") != RUN_ID:
        fail("actions.json run_id must match fixture")
    if data.get("mode") != "apply-fixture":
        fail("actions.json mode must be apply-fixture")
    if data.get("mode_default") != "dry-run":
        fail("actions.json must preserve dry-run as default")
    if data.get("writes_performed") is not True:
        fail("actions.json must record fixture writes performed")
    if data.get("real_vault_writes") is not False:
        fail("actions.json must record no real Vault writes")
    approval = data.get("approval_metadata")
    if not isinstance(approval, dict):
        fail("actions.json approval_metadata must be an object")
    if approval.get("approved") is not True:
        fail("actions.json approval_metadata.approved must be true for fixture apply")
    if approval.get("scope") != "repo-local-fixture-only":
        fail("actions.json approval scope must be repo-local-fixture-only")
    actions = data.get("actions")
    if not isinstance(actions, list):
        fail("actions.json actions must be a list")
    expected = {
        "clean-apply": "update",
        "manual-outside-preserved": "update",
        "manual-managed-block-edit": "conflict",
        "removed-source": "removed",
    }
    actual = {item.get("case_id"): item.get("action") for item in actions if isinstance(item, dict)}
    if actual != expected:
        fail(f"actions.json case/action map mismatch: {actual!r}")
    for item in actions:
        if not isinstance(item, dict):
            fail("actions.json actions must contain objects")
        if item.get("vault_path", "").startswith("projects/fixture-project/") is not True:
            fail("all fixture vault paths must stay under projects/fixture-project/")
        if item.get("hard_delete") is True:
            fail("fixture apply must not hard delete")
    statuses = walk_statuses(data, "actions.json")
    if not {"Confirmed", "Suggested", "Unknown"}.issubset(statuses):
        fail("actions.json must preserve Confirmed, Suggested, and Unknown statuses")
    return data


def check_fixture_pages() -> None:
    generated_path = FIXTURE_ROOT / "knowledge" / "user-stories" / f"{STORY_ID}.md"
    conflict_path = FIXTURE_ROOT / "knowledge" / "user-stories" / f"{STORY_ID}.conflict.md"
    archive_path = FIXTURE_ROOT / "knowledge" / "user-stories" / "_archive" / f"{REMOVED_STORY_ID}.md"
    tombstone_path = FIXTURE_ROOT / "knowledge" / "user-stories" / "_tombstones" / f"{REMOVED_STORY_ID}.json"
    before_path = RUN_ROOT / "manual-outside-before.md"
    after_path = RUN_ROOT / "manual-outside-after.md"
    for path in [generated_path, conflict_path, archive_path, tombstone_path, before_path, after_path]:
        if not path.exists():
            fail(f"missing {rel(path)}")
    generated = generated_path.read_text(encoding="utf-8")
    outside_before = before_path.read_text(encoding="utf-8")
    outside_after = after_path.read_text(encoding="utf-8")
    if "# Static Flow Intelligence scaffold validation" not in generated:
        fail("generated fixture page missing story title")
    block = managed_block(generated, STORY_ID)
    if "Evidence Status Summary" not in block:
        fail("managed block missing evidence summary")
    for status in ["Confirmed", "Suggested", "Unknown"]:
        if status not in block:
            fail(f"managed block missing {status}")
    for marker in ["Manual heading before managed block", "Manual note outside managed block", "Manual footer after managed block"]:
        if marker not in outside_before or marker not in outside_after:
            fail(f"manual outside content marker {marker!r} not preserved")
    if managed_block(outside_before, STORY_ID) == managed_block(outside_after, STORY_ID):
        fail("manual-outside-after.md managed block was not updated")
    conflict = conflict_path.read_text(encoding="utf-8")
    if "conflict" not in conflict.lower() or "Manual edit inside managed block" not in conflict:
        fail("conflict fixture must preserve manual managed-block edit evidence")
    tombstone = parse_json_file(tombstone_path)
    if not isinstance(tombstone, dict):
        fail("removed-source tombstone must be an object")
    if tombstone.get("source_id") != REMOVED_STORY_ID:
        fail("tombstone source_id mismatch")
    if tombstone.get("action") != "removed":
        fail("tombstone action must be removed")
    if tombstone.get("default_handling") != "tombstone-or-archive":
        fail("tombstone default handling must be tombstone-or-archive")
    if tombstone.get("hard_delete") is not False:
        fail("tombstone must record hard_delete false")
    if archive_path.read_text(encoding="utf-8").count("<!-- GSD-MIRROR:START") != 1:
        fail("archive page must retain exactly one managed block")


def check_manifest_and_lock() -> None:
    manifest = parse_json_file(RUN_ROOT / "apply-manifest.json")
    lock = parse_json_file(RUN_ROOT / "apply-lock.json")
    if not isinstance(manifest, dict) or not isinstance(lock, dict):
        fail("fixture manifest and lock must be objects")
    if manifest.get("run_id") != RUN_ID or lock.get("last_mirrored_at") != RUN_ID:
        fail("fixture manifest/lock run metadata mismatch")
    if manifest.get("mode") != "apply-fixture":
        fail("fixture manifest mode must be apply-fixture")
    if manifest.get("fixture_vault_namespace") != "projects/fixture-project/":
        fail("fixture manifest namespace must be projects/fixture-project/")
    if manifest.get("source_content_hash") != sha256_file(STORY_ROOT / "publish-source.md"):
        fail("fixture manifest source_content_hash must match publish-source.md")
    generated_path = FIXTURE_ROOT / "knowledge" / "user-stories" / f"{STORY_ID}.md"
    generated = generated_path.read_text(encoding="utf-8")
    block = managed_block(generated, STORY_ID)
    if manifest.get("generated_page_hash") != sha256_file(generated_path):
        fail("fixture manifest generated_page_hash mismatch")
    if manifest.get("managed_block_hash") != sha256_text(block):
        fail("fixture manifest managed_block_hash mismatch")
    items = lock.get("items")
    if not isinstance(items, list) or len(items) != 2:
        fail("fixture apply-lock must contain current and conflict items")
    statuses = {item.get("source_id"): item.get("status") for item in items if isinstance(item, dict)}
    if statuses.get(STORY_ID) != "current":
        fail("fixture lock must keep fixture story current")
    if statuses.get(f"{STORY_ID}:manual-managed-block-edit") != "conflict":
        fail("fixture lock must record conflict fixture status")
    removed = lock.get("removed_source_items")
    if not isinstance(removed, list) or len(removed) != 1:
        fail("fixture lock must contain one removed source item")
    if removed[0].get("source_id") != REMOVED_STORY_ID:
        fail("fixture removed source item mismatch")
    if removed[0].get("last_action") != "tombstoned":
        fail("fixture removed source must be tombstoned by default")
    if removed[0].get("hard_delete") is not False:
        fail("fixture removed source must record hard_delete false")


def check_report() -> None:
    path = RUN_ROOT / "apply-report.md"
    if not path.exists():
        fail(f"missing {rel(path)}")
    text = path.read_text(encoding="utf-8")
    required = [
        RUN_ID,
        "mode_default: dry-run",
        "apply_mode: explicit",
        "approval_scope: repo-local-fixture-only",
        "real_vault_writes: false",
        "projects/fixture-project/",
        "update",
        "conflict",
        "removed",
        "tombstone-or-archive",
        "Confirmed",
        "Suggested",
        "Unknown",
    ]
    missing = [term for term in required if term not in text]
    if missing:
        fail(f"apply-report.md missing required terms: {', '.join(missing)}")


def check_no_raw_or_sensitive_markers() -> None:
    for path in sorted(MIRROR_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".har"}:
            fail(f"raw binary/browser artifact copied into mirror outputs: {rel(path)}")
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in RAW_OR_SENSITIVE_MARKERS:
            if marker.lower() in lowered:
                fail(f"{rel(path)} contains raw or sensitive marker {marker!r}")


def main() -> None:
    check_skill_guidance()
    if not MIRROR_ROOT.exists():
        print("SKIP: no story-knowledge mirror apply fixture artifacts present; skill guidance is valid")
        return
    check_config()
    check_namespace()
    check_run_actions()
    check_fixture_pages()
    check_manifest_and_lock()
    check_report()
    check_no_raw_or_sensitive_markers()
    print("PASS: static story knowledge mirror apply/conflict/removal fixture is valid")


if __name__ == "__main__":
    main()
