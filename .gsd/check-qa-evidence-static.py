#!/usr/bin/env python
"""Validate the static QA evidence scaffold generated from Flow Intelligence."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_VALIDATOR_FIXTURE_QA_SESSION_ID = "QA-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_FLOW_ID = "FL-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_STORY_ID = "US-0001-internal-validator-fixture"
INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID = "20000101-000000-internal-fixture-browser-summary"
INTERNAL_VALIDATOR_FIXTURE_SOURCE_ID = "internal-flow-intelligence-source"
INTERNAL_VALIDATOR_FIXTURE_SOURCE_REFS = {
    "source-material://internal-flow-intelligence-source#primary-flow-coverage",
    "source-material://internal-flow-intelligence-source#role-and-page-discovery",
    "source-material://internal-flow-intelligence-source#traceability-preservation",
    "source-material://internal-flow-intelligence-source#evidence-status-preservation",
}
INTERNAL_VALIDATOR_FIXTURE_CLAIMS = {
    "primary-flow-coverage": {
        "internal-flow-intelligence-source#flow-index-coverage",
        "internal-flow-intelligence-source#replay-and-qa-linkage",
    },
    "role-and-page-discovery": {
        "internal-flow-intelligence-source#role-page-index",
        "internal-flow-intelligence-source#source-traceability-index",
    },
    "traceability-preservation": {"internal-flow-intelligence-source#evidence-manifest-traceability"},
    "evidence-status-preservation": {"internal-flow-intelligence-source#evidence-status-model"},
}
QA_SESSION_ID = INTERNAL_VALIDATOR_FIXTURE_QA_SESSION_ID
FLOW_ID = INTERNAL_VALIDATOR_FIXTURE_FLOW_ID
STORY_ID = INTERNAL_VALIDATOR_FIXTURE_STORY_ID
QA_ROOT = ROOT / ".planning" / "qa" / "sessions" / QA_SESSION_ID
ALLOWED_EVIDENCE_STATUSES = {"Confirmed", "Suggested", "Unknown"}
ALLOWED_DEFECT_TYPES = {
    "functional",
    "regression",
    "accessibility",
    "permission",
    "data",
    "performance",
    "UX",
    "reliability",
    "unknown",
}
ALLOWED_DEFECT_SEVERITIES = {"blocker", "critical", "high", "medium", "low"}
ALLOWED_DEFECT_PRIORITIES = {"P0", "P1", "P2", "P3", "unknown"}
ALLOWED_DEFECT_STATUSES = {"candidate", "confirmed", "rejected", "needs_triage"}
REQUIRED_QA_FILES = [
    "test-charter.md",
    "test-cases.md",
    "qa-report.md",
    "qa-report.json",
    "defects.md",
    "evidence-manifest.json",
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
    "full action log",
    "raw source body",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def parse_json_file(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


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
    path = ROOT / ".agents" / "skills" / "gsd-qa-tester" / "SKILL.md"
    if not path.exists():
        fail("missing .agents/skills/gsd-qa-tester/SKILL.md")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("gsd-qa-tester SKILL.md missing YAML frontmatter")
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("gsd-qa-tester SKILL.md frontmatter is not closed")
    frontmatter = match.group("body")
    if "name: gsd-qa-tester" not in frontmatter:
        fail("gsd-qa-tester SKILL.md frontmatter missing expected name")
    if "description:" not in frontmatter:
        fail("gsd-qa-tester SKILL.md frontmatter missing description")
    required_terms = [
        ".planning/qa/",
        ".planning/flow-intelligence/",
        "Confirmed",
        "Suggested",
        "Unknown",
        "Do Not Own",
        "Do not browse",
        "Do not redo discovery",
        "without user stories",
        "Vault",
        "source_id",
        "claim_id",
        "defect",
        "browser-run://",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail(f"gsd-qa-tester SKILL.md missing required guidance terms: {', '.join(missing)}")


def check_required_files() -> None:
    if not QA_ROOT.exists():
        fail(f"missing .planning/qa/sessions/{QA_SESSION_ID}/")
    for name in REQUIRED_QA_FILES:
        if not (QA_ROOT / name).exists():
            fail(f"missing .planning/qa/sessions/{QA_SESSION_ID}/{name}")


def require_refs(records: list[object], required_refs: set[str], location: str) -> set[str]:
    refs = set()
    statuses = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            fail(f"{location}[{index}] must be an object")
        ref = record.get("ref")
        if not isinstance(ref, str) or "://" not in ref:
            fail(f"{location}[{index}].ref must be a compact reference")
        check_evidence_status(record.get("evidence_status"), f"{location}[{index}].evidence_status")
        refs.add(ref)
        statuses.add(record.get("evidence_status"))
    if not required_refs.issubset(refs):
        fail(f"{location} missing required compact refs")
    if not {"Confirmed", "Suggested", "Unknown"}.issubset(statuses):
        fail(f"{location} must preserve Confirmed, Suggested, and Unknown statuses")
    return refs


def check_defect_candidate(defect: object, index: int) -> None:
    if not isinstance(defect, dict):
        fail(f"qa-report.json defect_candidates[{index}] must be an object")
    required_keys = {
        "schema_version",
        "defect_id",
        "qa_session_id",
        "title",
        "type",
        "severity",
        "priority",
        "status",
        "environment",
        "route_or_flow",
        "role",
        "preconditions",
        "steps_to_reproduce",
        "expected_result",
        "actual_result",
        "evidence_refs",
        "browser_run_refs",
        "affected_user_goal",
        "suspected_root_cause",
        "regression_risk",
        "suggested_verification",
    }
    missing = sorted(required_keys.difference(defect))
    if missing:
        fail(f"qa-report.json defect_candidates[{index}] missing fields: {', '.join(missing)}")
    if defect["schema_version"] != 1:
        fail(f"qa-report.json defect_candidates[{index}] schema_version must be 1")
    if defect["qa_session_id"] != QA_SESSION_ID:
        fail(f"qa-report.json defect_candidates[{index}] qa_session_id must match fixture")
    if defect["type"] not in ALLOWED_DEFECT_TYPES:
        fail(f"qa-report.json defect_candidates[{index}] has invalid type")
    if defect["severity"] not in ALLOWED_DEFECT_SEVERITIES:
        fail(f"qa-report.json defect_candidates[{index}] has invalid severity")
    if defect["priority"] not in ALLOWED_DEFECT_PRIORITIES:
        fail(f"qa-report.json defect_candidates[{index}] has invalid priority")
    if defect["status"] not in ALLOWED_DEFECT_STATUSES:
        fail(f"qa-report.json defect_candidates[{index}] has invalid status")


def check_qa_report() -> None:
    data = parse_json_file(QA_ROOT / "qa-report.json")
    if not isinstance(data, dict):
        fail("qa-report.json must be an object")
    if data.get("schema_version") != 1:
        fail("qa-report.json schema_version must be 1")
    if data.get("qa_session_id") != QA_SESSION_ID:
        fail("qa-report.json qa_session_id must match fixture directory")
    if data.get("source_flow_ids") != [FLOW_ID]:
        fail("qa-report.json source_flow_ids must contain the fixture flow")
    if data.get("supporting_story_ids") != [STORY_ID]:
        fail("qa-report.json supporting_story_ids must reference the optional fixture story")
    if data.get("requires_user_stories") is not False:
        fail("qa-report.json must record requires_user_stories false")
    if data.get("raw_evidence_copied") is not False:
        fail("qa-report.json must record raw_evidence_copied false")
    if data.get("status") not in {"current", "partial", "blocked"}:
        fail("qa-report.json has invalid status")
    source_paths = data.get("source_paths")
    if not isinstance(source_paths, list) or not source_paths:
        fail("qa-report.json source_paths must be a non-empty list")
    required_source_paths = {
        ".planning/flow-intelligence/flows/FL-0001-internal-validator-fixture/flow.json",
        ".planning/flow-intelligence/flows/FL-0001-internal-validator-fixture/evidence-manifest.json",
        ".planning/user-stories/US-0001-internal-validator-fixture/story.json",
        ".planning/user-stories/US-0001-internal-validator-fixture/source-links.json",
    }
    if not required_source_paths.issubset(set(str(item) for item in source_paths)):
        fail("qa-report.json missing required source paths")
    evidence_refs = data.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        fail("qa-report.json evidence_refs must be a list")
    require_refs(
        evidence_refs,
        {
            f"flow://{FLOW_ID}#FL-0001-S01",
            f"flow://{FLOW_ID}#FL-0001-S02",
            f"story://{STORY_ID}",
            *INTERNAL_VALIDATOR_FIXTURE_SOURCE_REFS,
            f"browser-run://{INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID}/summary.json",
        },
        "qa-report.json.evidence_refs",
    )
    coverage = data.get("coverage")
    if not isinstance(coverage, list) or not coverage:
        fail("qa-report.json coverage must be a non-empty list")
    walk_statuses(coverage, "qa-report.json.coverage")
    defects = data.get("defect_candidates")
    if not isinstance(defects, list):
        fail("qa-report.json defect_candidates must be a list")
    for index, defect in enumerate(defects):
        check_defect_candidate(defect, index)
    gaps = data.get("evidence_gaps")
    if not isinstance(gaps, list) or not gaps:
        fail("qa-report.json evidence_gaps must preserve uncertainty for this fixture")
    walk_statuses(data, "qa-report.json")


def check_evidence_manifest() -> None:
    data = parse_json_file(QA_ROOT / "evidence-manifest.json")
    if not isinstance(data, dict):
        fail("evidence-manifest.json must be an object")
    if data.get("schema_version") != 1:
        fail("evidence-manifest.json schema_version must be 1")
    if data.get("qa_session_id") != QA_SESSION_ID:
        fail("evidence-manifest.json qa_session_id must match fixture")
    if data.get("raw_evidence_copied") is not False:
        fail("evidence-manifest.json must record raw_evidence_copied false")
    refs = data.get("evidence_refs")
    if not isinstance(refs, list):
        fail("evidence-manifest.json evidence_refs must be a list")
    require_refs(
        refs,
        {
            "repo://.planning/templates/qa-evidence-contract.md",
            f"flow://{FLOW_ID}#FL-0001-S01",
            f"story://{STORY_ID}",
            f"browser-run://{INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID}/summary.json",
        },
        "evidence-manifest.json.evidence_refs",
    )
    traceability = data.get("source_traceability")
    if not isinstance(traceability, list):
        fail("evidence-manifest.json source_traceability must be a list")
    required_claims = INTERNAL_VALIDATOR_FIXTURE_CLAIMS
    claims_seen: dict[str, set[str]] = {}
    for item in traceability:
        if not isinstance(item, dict):
            fail("evidence-manifest.json source_traceability entries must be objects")
        if item.get("source_id") != INTERNAL_VALIDATOR_FIXTURE_SOURCE_ID or item.get("evidence_status") != "Confirmed":
            fail("evidence-manifest.json source_traceability must preserve Confirmed internal fixture references")
        anchors = item.get("anchors")
        if not isinstance(anchors, list):
            fail("evidence-manifest.json source_traceability anchors must be lists")
        claims_seen.setdefault(str(item.get("claim_id")), set()).update(str(anchor) for anchor in anchors)
    for claim_id, anchors in required_claims.items():
        if not anchors.issubset(claims_seen.get(claim_id, set())):
            fail(f"evidence-manifest.json missing source traceability for {claim_id}")
    walk_statuses(data, "evidence-manifest.json")


def check_markdown_mentions() -> None:
    for name in ["test-charter.md", "test-cases.md", "qa-report.md", "defects.md"]:
        text = (QA_ROOT / name).read_text(encoding="utf-8")
        required_terms = [QA_SESSION_ID, FLOW_ID, "Confirmed", "Suggested", "Unknown"]
        missing = [term for term in required_terms if term not in text]
        if missing:
            fail(f"{name} missing required QA fixture terms: {', '.join(missing)}")


def check_no_raw_or_sensitive_markers() -> None:
    for path in sorted(QA_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".har"}:
            fail(f"raw binary/browser artifact copied into QA outputs: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in RAW_OR_SENSITIVE_MARKERS:
            if marker.lower() in lowered:
                fail(f"{path.relative_to(ROOT)} contains raw or sensitive marker {marker!r}")


def main() -> None:
    check_skill()
    if not QA_ROOT.exists():
        print("SKIP: no QA evidence fixture artifacts present; skill guidance is valid")
        return
    check_required_files()
    check_qa_report()
    check_evidence_manifest()
    check_markdown_mentions()
    check_no_raw_or_sensitive_markers()
    print("PASS: static QA evidence scaffold and artifacts are valid")


if __name__ == "__main__":
    main()
