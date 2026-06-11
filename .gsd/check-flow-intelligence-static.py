#!/usr/bin/env python
"""Validate the static Flow Intelligence scaffold and artifact shape."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"Confirmed", "Suggested", "Unknown"}
INTERNAL_VALIDATOR_FIXTURE_BROWSER_RUN_ID = "20000101-000000-internal-fixture-browser-summary"
INTERNAL_VALIDATOR_FIXTURE_SOURCE_ID = "internal-flow-intelligence-source"
INTERNAL_VALIDATOR_FIXTURE_CLAIMS = {
    "traceability-preservation": ["internal-flow-intelligence-source#evidence-manifest-traceability"],
    "role-and-page-discovery": [
        "internal-flow-intelligence-source#role-page-index",
        "internal-flow-intelligence-source#source-traceability-index",
    ],
    "evidence-status-preservation": ["internal-flow-intelligence-source#evidence-status-model"],
    "primary-flow-coverage": [
        "internal-flow-intelligence-source#flow-index-coverage",
        "internal-flow-intelligence-source#replay-and-qa-linkage",
    ],
}
BROWSER_SUMMARY_REF_RE = re.compile(
    r"^browser-run://\d{8}-\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*/summary\.json$"
)
RAW_BROWSER_ARTIFACT_FILENAMES = {
    "action-log.json",
    "network.json",
    "console.log",
    "storage-summary.json",
}
RAW_BROWSER_ARTIFACT_DIRS = {
    "screenshots",
    "page-states",
    "dom-snapshots",
}
RAW_BROWSER_PAYLOAD_MARKERS = [
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
]
REQUIRED_INDEXES = [
    "capability-index.jsonl",
    "role-index.jsonl",
    "page-index.jsonl",
    "api-index.jsonl",
    "db-entity-index.jsonl",
    "flow-index.jsonl",
    "traceability-index.jsonl",
    "evidence-index.jsonl",
    "replay-index.jsonl",
]
REQUIRED_FLOW_FILES = [
    "flow.json",
    "flow.compact.md",
    "story-source.json",
    "code-map.json",
    "replay.plan.json",
    "qa-hints.json",
    "evidence-manifest.json",
    "source-hashes.json",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def check_status(value: object, location: str) -> None:
    if value not in ALLOWED_STATUSES:
        fail(f"{location} has invalid evidence_status {value!r}")


def walk_statuses(value: object, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "evidence_status":
                check_status(child, child_location)
            else:
                walk_statuses(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_statuses(child, f"{location}[{index}]")


def walk_browser_references(value: object, location: str, refs: list[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        ref = value.get("ref")
        if isinstance(ref, str) and ref.startswith("browser-run://"):
            check_status(value.get("evidence_status"), f"{location}.evidence_status")
            refs.append((ref, location))
        for key, child in value.items():
            walk_browser_references(child, f"{location}.{key}", refs)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_browser_references(child, f"{location}[{index}]", refs)


def parse_json_file(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def check_skill() -> None:
    path = ROOT / ".agents" / "skills" / "gsd-discover-flow-evidence" / "SKILL.md"
    if not path.exists():
        fail("missing .agents/skills/gsd-discover-flow-evidence/SKILL.md")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md missing YAML frontmatter")
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md frontmatter is not closed")
    frontmatter = match.group("body")
    if "name: gsd-discover-flow-evidence" not in frontmatter:
        fail("SKILL.md frontmatter missing expected name")
    if "description:" not in frontmatter:
        fail("SKILL.md frontmatter missing description")
    required_terms = [
        "Flow Intelligence",
        ".planning/flow-intelligence/",
        ".planning/evidence/flow-intelligence/",
        "Confirmed",
        "Suggested",
        "Unknown",
        "browser-run://",
        "Do Not Use As Owner For",
        "User story generation",
        "QA testing",
        "Vault publishing",
        "milestone planning",
        "source_id",
        "claim_id",
        "redaction",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        fail(f"SKILL.md missing required guidance terms: {', '.join(missing)}")


def check_indexes() -> None:
    root = ROOT / ".planning" / "flow-intelligence"
    if not root.exists():
        fail("missing .planning/flow-intelligence/")
    index = root / "INDEX.md"
    if not index.exists():
        fail("missing .planning/flow-intelligence/INDEX.md")
    index_text = index.read_text(encoding="utf-8")
    for name in REQUIRED_INDEXES:
        if name not in index_text:
            fail(f"INDEX.md does not reference {name}")
        path = root / name
        if not path.exists():
            fail(f"missing .planning/flow-intelligence/{name}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"{path.relative_to(ROOT)} line {line_number} is not valid JSONL: {exc}")
            if not isinstance(record, dict):
                fail(f"{path.relative_to(ROOT)} line {line_number} is not an object")
            walk_statuses(record, f"{path.relative_to(ROOT)}:{line_number}")


def check_flows() -> None:
    flows_root = ROOT / ".planning" / "flow-intelligence" / "flows"
    if not flows_root.exists():
        return
    for flow_dir in sorted(path for path in flows_root.iterdir() if path.is_dir()):
        for name in REQUIRED_FLOW_FILES:
            if not (flow_dir / name).exists():
                fail(f"missing {flow_dir.relative_to(ROOT)}/{name}")
        flow = parse_json_file(flow_dir / "flow.json")
        if not isinstance(flow, dict):
            fail(f"{flow_dir.relative_to(ROOT)}/flow.json must be an object")
        if flow.get("schema_version") != 1:
            fail(f"{flow_dir.relative_to(ROOT)}/flow.json schema_version must be 1")
        if flow.get("flow_id") != flow_dir.name:
            fail(f"{flow_dir.relative_to(ROOT)}/flow.json flow_id must match directory name")
        if flow.get("confidence") not in {"confirmed", "suggested", "mixed", "unknown"}:
            fail(f"{flow_dir.relative_to(ROOT)}/flow.json has invalid confidence")
        if flow.get("status") not in {"current", "stale", "partial", "removed"}:
            fail(f"{flow_dir.relative_to(ROOT)}/flow.json has invalid status")
        walk_statuses(flow, f"{flow_dir.relative_to(ROOT)}/flow.json")
        for name in [
            "story-source.json",
            "code-map.json",
            "replay.plan.json",
            "qa-hints.json",
            "evidence-manifest.json",
            "source-hashes.json",
        ]:
            walk_statuses(parse_json_file(flow_dir / name), f"{flow_dir.relative_to(ROOT)}/{name}")


def check_browser_references() -> None:
    root = ROOT / ".planning" / "flow-intelligence"
    refs: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if path.suffix == ".json":
            walk_browser_references(parse_json_file(path), str(relative), refs)
        elif path.suffix == ".jsonl":
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if line.strip():
                    walk_browser_references(json.loads(line), f"{relative}:{line_number}", refs)
        elif path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            for ref in re.findall(r"browser-run://\S+", text):
                refs.append((ref.rstrip("`.,)"), str(relative)))
    if not refs:
        fail("no compact browser-run:// references found in Flow Intelligence artifacts")
    for ref, location in refs:
        if not BROWSER_SUMMARY_REF_RE.match(ref):
            fail(f"{location} has invalid browser summary reference {ref!r}")
        run_id = ref.removeprefix("browser-run://").removesuffix("/summary.json")
        summary = ROOT / ".planning" / "evidence" / "browser-runs" / run_id / "summary.json"
        if not summary.exists():
            fail(f"{location} references missing browser summary {summary.relative_to(ROOT)}")


def check_no_raw_browser_evidence_copied() -> None:
    root = ROOT / ".planning" / "flow-intelligence"
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        parts = set(relative.parts)
        if path.name in RAW_BROWSER_ARTIFACT_FILENAMES:
            fail(f"raw browser artifact filename copied into Flow Intelligence: {path.relative_to(ROOT)}")
        if parts & RAW_BROWSER_ARTIFACT_DIRS:
            fail(f"raw browser artifact directory copied into Flow Intelligence: {path.relative_to(ROOT)}")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".har"}:
            fail(f"raw browser artifact file copied into Flow Intelligence: {path.relative_to(ROOT)}")
        if path.suffix.lower() in {".json", ".jsonl", ".md"}:
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for marker in RAW_BROWSER_PAYLOAD_MARKERS:
                if marker.lower() in lowered:
                    fail(f"{path.relative_to(ROOT)} contains raw browser payload marker {marker!r}")


def check_evidence_root() -> None:
    path = ROOT / ".planning" / "evidence" / "flow-intelligence"
    if not path.exists():
        fail("missing .planning/evidence/flow-intelligence/")
    manifest = path / "flow-intelligence-static-validation.json"
    if not manifest.exists():
        fail("missing .planning/evidence/flow-intelligence/flow-intelligence-static-validation.json")
    data = parse_json_file(manifest)
    if not isinstance(data, dict):
        fail("flow intelligence static validation manifest must be an object")
    walk_statuses(data, "flow-intelligence-static-validation.json")
    browser_manifest = path / "flow-intelligence-browser-reference-validation.json"
    if not browser_manifest.exists():
        fail("missing .planning/evidence/flow-intelligence/flow-intelligence-browser-reference-validation.json")
    browser_data = parse_json_file(browser_manifest)
    if not isinstance(browser_data, dict):
        fail("flow intelligence browser-reference validation manifest must be an object")
    walk_statuses(browser_data, "flow-intelligence-browser-reference-validation.json")
    pass_manifest = path / "flow-intelligence-validation-pass.json"
    if not pass_manifest.exists():
        fail("missing .planning/evidence/flow-intelligence/flow-intelligence-validation-pass.json")
    pass_data = parse_json_file(pass_manifest)
    if not isinstance(pass_data, dict):
        fail("flow intelligence validation manifest must be an object")
    walk_statuses(pass_data, "flow-intelligence-validation-pass.json")
    if pass_data.get("phase") != "flow-intelligence-validation-pass":
        fail("flow intelligence validation manifest has incorrect phase")
    target_validation = pass_data.get("validation_target")
    if not isinstance(target_validation, dict):
        fail("flow intelligence validation manifest missing validation_target object")
    if target_validation.get("read_only") is not True:
        fail("flow intelligence validation manifest must record read_only true")
    if target_validation.get("broad_scan_performed") is not False:
        fail("flow intelligence validation manifest must record broad_scan_performed false")
    if target_validation.get("product_mutation_performed") is not False:
        fail("flow intelligence validation manifest must record product_mutation_performed false")
    if not isinstance(target_validation.get("paths_inspected"), list) or not target_validation["paths_inspected"]:
        fail("flow intelligence validation manifest must record at least one inspected validation path")
    if "git_status_before" not in target_validation or "git_status_after" not in target_validation:
        fail("flow intelligence validation manifest must record before/after validation target git status")
    validation_result = target_validation.get("validation_result")
    if validation_result not in {"target-derived", "fallback-fixture", "blocked"}:
        fail("flow intelligence validation manifest has invalid validation_result")
    traceability = pass_data.get("source_traceability_consumed")
    if not isinstance(traceability, list):
        fail("flow intelligence validation manifest missing source_traceability_consumed list")
    required_claims = INTERNAL_VALIDATOR_FIXTURE_CLAIMS
    claims_seen: dict[str, set[str]] = {}
    for item in traceability:
        if not isinstance(item, dict):
            fail("flow intelligence source traceability entries must be objects")
        if item.get("source_id") == INTERNAL_VALIDATOR_FIXTURE_SOURCE_ID and item.get("evidence_status") == "Confirmed":
            anchors = item.get("anchors")
            if isinstance(anchors, list):
                claims_seen.setdefault(str(item.get("claim_id")), set()).update(str(anchor) for anchor in anchors)
    for claim_id, anchors in required_claims.items():
        if not set(anchors).issubset(claims_seen.get(claim_id, set())):
            fail(f"flow intelligence validation manifest missing Confirmed source traceability for {claim_id}")
    performance = pass_data.get("performance_reuse_evidence")
    if not isinstance(performance, dict):
        fail("flow intelligence validation manifest missing performance_reuse_evidence object")
    for key in [
        "reusable_surfaces_inspected",
        "final_reuse_decision",
        "new_code_justification",
        "performance_sensitive_paths_touched",
        "performance_risks_checked",
        "performance_validation_run",
        "minimum_new_code_justification",
    ]:
        if key not in performance:
            fail(f"flow intelligence performance_reuse_evidence missing {key}")


def main() -> None:
    check_skill()
    if not (ROOT / ".planning" / "flow-intelligence").exists():
        print("SKIP: no Flow Intelligence artifacts present; skill guidance is valid")
        return
    check_indexes()
    check_flows()
    check_browser_references()
    check_no_raw_browser_evidence_copied()
    check_evidence_root()
    print("PASS: Flow Intelligence static scaffold and artifacts are valid")


if __name__ == "__main__":
    main()
