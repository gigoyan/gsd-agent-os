"""Static validator for the GSD UI discovery orchestration layer.

No browser, CDP endpoint, or target application is required. The validator checks
the reusable skill/contracts and any repo-local UI discovery artifacts that exist.
"""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "gsd-ui-discovery-orchestrator" / "SKILL.md"
TEMPLATE_ROOT = ROOT / ".planning" / "templates"
UI_ROOT = ROOT / ".planning" / "ui-discovery"

REQUIRED_TEMPLATES = [
    "ui-discovery-scope-contract.md",
    "ui-discovery-coverage-contract.md",
    "ui-role-session-contract.md",
    "ui-inventory-contract.md",
    "browser-session-reuse-contract.md",
]

ALLOWED_OUTPUT_STATUSES = {"complete", "partial", "blocked", "skipped", "not_requested"}
ALLOWED_EVIDENCE_STATUSES = {"Confirmed", "Suggested", "Unknown"}
COMPACT_BROWSER_REF = re.compile(r"^browser-run://[A-Za-z0-9_.-]+/summary\.json$")
FORBIDDEN_KEYS = {
    "screenshot",
    "screenshots",
    "dom_snapshot",
    "dom_snapshots",
    "dom",
    "network_payload",
    "network_payloads",
    "network",
    "console_log",
    "console_logs",
    "console",
    "cookie",
    "cookies",
    "token",
    "tokens",
    "storage",
    "localStorage",
    "sessionStorage",
    "action_log",
    "action_logs",
}


class ValidationError(Exception):
    pass


def fail(path, field, message):
    raise ValidationError(f"{path}: {field}: {message}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        fail(path, "$", f"could not read JSON: {exc}")
    except json.JSONDecodeError as exc:
        fail(path, "$", f"invalid JSON: {exc}")


def require_file(path, field="$"):
    if not path.exists():
        fail(path, field, "required file is missing")


def parse_frontmatter(text, path):
    if not text.startswith("---\n"):
        fail(path, "frontmatter", "missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail(path, "frontmatter", "unterminated YAML frontmatter")
    body = text[4:end].strip().splitlines()
    data = {}
    for line in body:
        if not line.strip():
            continue
        if ":" not in line:
            fail(path, "frontmatter", f"invalid line {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_skill():
    require_file(SKILL)
    text = SKILL.read_text(encoding="utf-8")
    fm = parse_frontmatter(text, SKILL)
    if fm.get("name") != "gsd-ui-discovery-orchestrator":
        fail(SKILL, "frontmatter.name", "expected gsd-ui-discovery-orchestrator")
    if not fm.get("description"):
        fail(SKILL, "frontmatter.description", "description is required")
    if ".planning/ui-discovery/**" not in text:
        fail(SKILL, "ownership", "skill must declare ownership of .planning/ui-discovery/**")
    forbidden_owned = [
        ".planning/flow-intelligence/**",
        ".planning/user-stories/**",
        ".planning/qa/**",
        ".planning/story-knowledge-mirror/**",
        ".planning/evidence/browser-runs/**",
    ]
    for owned_path in forbidden_owned:
        marker = f"This skill owns:\n\n```text\n{owned_path}"
        if marker in text:
            fail(SKILL, "ownership", f"skill must not claim ownership of {owned_path}")
    for owned_path in forbidden_owned:
        if owned_path not in text:
            fail(SKILL, "ownership-boundary", f"skill must explicitly exclude {owned_path}")


def validate_templates():
    for name in REQUIRED_TEMPLATES:
        require_file(TEMPLATE_ROOT / name)


def walk_values(value, path, field="$"):
    if isinstance(value, dict):
        for key, item in value.items():
            subfield = f"{field}.{key}" if field != "$" else key
            if key in FORBIDDEN_KEYS:
                fail(path, subfield, "raw browser evidence or secret-bearing field is not allowed in UI discovery artifacts")
            if key == "evidence_status" and item not in ALLOWED_EVIDENCE_STATUSES:
                fail(path, subfield, f"invalid evidence status {item!r}")
            if key.endswith("_ref") or key.endswith("_refs") or key in {"source_browser_runs", "browser_run_refs"}:
                refs = item if isinstance(item, list) else [item]
                for ref in refs:
                    if isinstance(ref, str) and ref.startswith("browser-run://") and not COMPACT_BROWSER_REF.match(ref):
                        fail(path, subfield, f"browser ref must use browser-run://<run-id>/summary.json, got {ref!r}")
            walk_values(item, path, subfield)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk_values(item, path, f"{field}[{index}]")
    elif isinstance(value, str):
        lower = value.lower()
        if value.startswith("browser-run://") and not COMPACT_BROWSER_REF.match(value):
            fail(path, field, f"browser ref must use browser-run://<run-id>/summary.json, got {value!r}")
        raw_markers = [
            ".png",
            "dom-snapshots/",
            "network.json",
            "console.log",
            "action-log.json",
            "cookie:",
            "authorization:",
            "bearer ",
            "localstorage",
            "sessionstorage",
        ]
        if any(marker in lower for marker in raw_markers):
            fail(path, field, "raw browser evidence, logs, storage, cookies, or tokens must not be copied here")


def validate_scope(path):
    data = load_json(path)
    if data.get("schema_version") != 1:
        fail(path, "schema_version", "expected 1")
    outputs = data.get("outputs_requested")
    if not isinstance(outputs, dict):
        fail(path, "outputs_requested", "required object is missing")
    if outputs.get("vault_publish") is not False:
        explicit = data.get("vault_publish_explicitly_requested") is True
        if not explicit:
            fail(path, "outputs_requested.vault_publish", "must be false unless explicitly requested")
    walk_values(data, path)


def validate_run_manifest(path):
    data = load_json(path)
    if data.get("schema_version") != 1:
        fail(path, "schema_version", "expected 1")
    steps = data.get("steps")
    if not isinstance(steps, list):
        fail(path, "steps", "required array is missing")
    for index, step in enumerate(steps):
        status = step.get("status") if isinstance(step, dict) else None
        if status not in ALLOWED_OUTPUT_STATUSES and status not in {"planned", "running", ""}:
            fail(path, f"steps[{index}].status", f"invalid output status {status!r}")
    walk_values(data, path)


def validate_optional_json(path):
    if path.exists():
        walk_values(load_json(path), path)


def validate_ui_artifacts():
    if not UI_ROOT.exists():
        return
    for goal_dir in sorted(p for p in UI_ROOT.iterdir() if p.is_dir()):
        scope_path = goal_dir / "scope.json"
        manifest_path = goal_dir / "run-manifest.json"
        inventory_path = goal_dir / "ui-inventory.json"
        role_matrix_path = goal_dir / "role-session-matrix.json"
        coverage_path = goal_dir / "coverage-report.json"
        if scope_path.exists():
            validate_scope(scope_path)
        if manifest_path.exists():
            validate_run_manifest(manifest_path)
        validate_optional_json(inventory_path)
        validate_optional_json(role_matrix_path)
        validate_optional_json(coverage_path)


def main():
    try:
        validate_skill()
        validate_templates()
        validate_ui_artifacts()
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - setup/config errors should be distinct.
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2
    print("PASS: UI discovery static validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
