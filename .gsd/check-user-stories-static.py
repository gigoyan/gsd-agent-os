#!/usr/bin/env python
"""Validate the static user-story scaffold generated from Flow Intelligence."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_VALIDATOR_FIXTURE_STORY_ID = "US-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_FLOW_ID = "FL-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID = "20000101-000000-internal-fixture-browser-summary"
INTERNAL_VALIDATOR_FIXTURE_SOURCE_REFS = {
    "source-material://internal-flow-intelligence-source#primary-flow-coverage",
    "source-material://internal-flow-intelligence-source#role-and-page-discovery",
    "source-material://internal-flow-intelligence-source#traceability-preservation",
    "source-material://internal-flow-intelligence-source#evidence-status-preservation",
}
STORY_ID = INTERNAL_VALIDATOR_FIXTURE_STORY_ID
FLOW_ID = INTERNAL_VALIDATOR_FIXTURE_FLOW_ID
STORY_ROOT = ROOT / ".planning" / "user-stories" / STORY_ID
ALLOWED_EVIDENCE_STATUSES = {"Confirmed", "Suggested", "Unknown"}
ALLOWED_FORMAT_PROFILES = {"default-gsd", "bdd-gherkin", "qa-ready", "custom"}
ALLOWED_STORY_STATUSES = {"current", "stale", "partial", "removed"}
REQUIRED_STORY_FILES = [
    "story.md",
    "story.json",
    "acceptance-criteria.md",
    "gherkin.feature",
    "source-links.json",
    "publish-source.md",
    "story-hashes.json",
]
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


def walk_statuses(value: object, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "evidence_status":
                check_evidence_status(child, child_location)
            else:
                walk_statuses(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_statuses(child, f"{location}[{index}]")


def check_skill() -> None:
    path = ROOT / ".agents" / "skills" / "gsd-create-user-stories" / "SKILL.md"
    if not path.exists():
        fail("missing .agents/skills/gsd-create-user-stories/SKILL.md")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("gsd-create-user-stories SKILL.md missing YAML frontmatter")
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("gsd-create-user-stories SKILL.md frontmatter is not closed")
    frontmatter = match.group("body")
    if "name: gsd-create-user-stories" not in frontmatter:
        fail("gsd-create-user-stories SKILL.md frontmatter missing expected name")
    if "description:" not in frontmatter:
        fail("gsd-create-user-stories SKILL.md frontmatter missing description")
    required_terms = [
        ".planning/user-stories/",
        ".planning/flow-intelligence/",
        "Confirmed",
        "Suggested",
        "Unknown",
        "Do Not Own",
        "Do not browse",
        "Do not redo discovery",
        "Vault",
        "QA",
        "source_id",
        "claim_id",
        "publish-source.md",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail(f"gsd-create-user-stories SKILL.md missing required guidance terms: {', '.join(missing)}")


def check_required_files() -> None:
    if not STORY_ROOT.exists():
        fail(f"missing .planning/user-stories/{STORY_ID}/")
    for name in REQUIRED_STORY_FILES:
        if not (STORY_ROOT / name).exists():
            fail(f"missing .planning/user-stories/{STORY_ID}/{name}")


def check_story_json() -> dict[str, object]:
    data = parse_json_file(STORY_ROOT / "story.json")
    if not isinstance(data, dict):
        fail("story.json must be an object")
    if data.get("schema_version") != 1:
        fail("story.json schema_version must be 1")
    if data.get("story_id") != STORY_ID:
        fail("story.json story_id must match fixture directory")
    if data.get("source_flow_ids") != [FLOW_ID]:
        fail("story.json source_flow_ids must contain the fixture flow")
    if data.get("format_profile") not in ALLOWED_FORMAT_PROFILES:
        fail("story.json has invalid format_profile")
    if data.get("status") not in ALLOWED_STORY_STATUSES:
        fail("story.json has invalid status")
    source_paths = data.get("source_paths")
    if not isinstance(source_paths, list) or not source_paths:
        fail("story.json source_paths must be a non-empty list")
    required_source_paths = {
        ".planning/flow-intelligence/flows/FL-0001-internal-validator-fixture/flow.json",
        ".planning/flow-intelligence/flows/FL-0001-internal-validator-fixture/story-source.json",
        ".planning/flow-intelligence/flows/FL-0001-internal-validator-fixture/evidence-manifest.json",
    }
    if not required_source_paths.issubset(set(str(item) for item in source_paths)):
        fail("story.json missing required Flow Intelligence source paths")
    sections = data.get("sections")
    if not isinstance(sections, dict):
        fail("story.json sections must be an object")
    for key in ["story", "business_goal", "main_flow", "acceptance_criteria"]:
        if key not in sections:
            fail(f"story.json sections missing {key}")
    if not isinstance(sections["main_flow"], list) or not sections["main_flow"]:
        fail("story.json sections.main_flow must be a non-empty list")
    if not isinstance(sections["acceptance_criteria"], list) or not sections["acceptance_criteria"]:
        fail("story.json sections.acceptance_criteria must be a non-empty list")
    if data.get("content_hash") != sha256_file(STORY_ROOT / "story.md"):
        fail("story.json content_hash must match story.md")
    if data.get("publish_hash") != sha256_file(STORY_ROOT / "publish-source.md"):
        fail("story.json publish_hash must match publish-source.md")
    return data


def check_source_links() -> None:
    data = parse_json_file(STORY_ROOT / "source-links.json")
    if not isinstance(data, dict):
        fail("source-links.json must be an object")
    if data.get("schema_version") != 1:
        fail("source-links.json schema_version must be 1")
    if data.get("story_id") != STORY_ID:
        fail("source-links.json story_id must match fixture story")
    links = data.get("links")
    if not isinstance(links, list) or not links:
        fail("source-links.json links must be a non-empty list")
    statuses = set()
    refs = set()
    for index, link in enumerate(links):
        if not isinstance(link, dict):
            fail(f"source-links.json links[{index}] must be an object")
        check_evidence_status(link.get("evidence_status"), f"source-links.json.links[{index}].evidence_status")
        statuses.add(link.get("evidence_status"))
        refs.add(link.get("ref"))
    if "Confirmed" not in statuses or "Suggested" not in statuses or "Unknown" not in statuses:
        fail("source-links.json must preserve Confirmed, Suggested, and Unknown statuses from fixture inputs")
    required_refs = {
        f"flow://{FLOW_ID}#FL-0001-S01",
        f"flow://{FLOW_ID}#FL-0001-S02",
        *INTERNAL_VALIDATOR_FIXTURE_SOURCE_REFS,
        f"browser-run://{INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID}/summary.json",
    }
    if not required_refs.issubset(refs):
        fail("source-links.json missing required compact source/evidence refs")


def check_hashes() -> None:
    data = parse_json_file(STORY_ROOT / "story-hashes.json")
    if not isinstance(data, dict):
        fail("story-hashes.json must be an object")
    if data.get("schema_version") != 1:
        fail("story-hashes.json schema_version must be 1")
    hashes = data.get("hashes")
    if not isinstance(hashes, dict):
        fail("story-hashes.json hashes must be an object")
    for name in [
        "story.md",
        "story.json",
        "acceptance-criteria.md",
        "gherkin.feature",
        "source-links.json",
        "publish-source.md",
    ]:
        expected = sha256_file(STORY_ROOT / name)
        actual = hashes.get(name)
        if actual != expected:
            fail(f"story-hashes.json hash for {name} is not deterministic")


def check_no_raw_or_sensitive_markers() -> None:
    for path in sorted(STORY_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".har"}:
            fail(f"raw binary/browser artifact copied into story outputs: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in RAW_OR_SENSITIVE_MARKERS:
            if marker.lower() in lowered:
                fail(f"{path.relative_to(ROOT)} contains raw or sensitive marker {marker!r}")


def main() -> None:
    check_skill()
    if not STORY_ROOT.exists():
        print("SKIP: no user-story fixture artifacts present; skill guidance is valid")
        return
    check_required_files()
    check_story_json()
    check_source_links()
    check_hashes()
    check_no_raw_or_sensitive_markers()
    print("PASS: static user-story scaffold and artifacts are valid")


if __name__ == "__main__":
    main()
