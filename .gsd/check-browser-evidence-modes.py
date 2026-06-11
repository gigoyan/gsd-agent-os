"""Browser Evidence Runtime replay/qa/smoke validator.

This validator carries two explicit paths:

  (1) A no-network/no-browser UNIT path -- the binding gate in EVERY environment.
      It SELF-GENERATES a blocked `evidence` run via the wrapper (no real browser)
      and asserts the blocked-artifact shape on it: full artifact set incl.
      `blocker-details.json`, blocked `failure.cause`, redaction replacement +
      no-Vault-publication, the non-mutating lifecycle invariants, and the
      read-only validation-target record. (Back-compat:
      `--run-id` still
      points the shape check at an existing run dir for ad-hoc use.)

  (2) A CONDITIONAL real-browser path that runs ONLY when a Browser Harness
      engine, a reachable CDP endpoint, and a reachable app are all available.
      It validates replay/qa/smoke discriminators against REAL runs the
      validator drives:
        replay : per-step action-log entries preserving each plan step's
                 evidence_status downgrade-only, always a NEW run dir, at least
                 one unsupported/failed step that is NEVER Confirmed.
        qa     : writes `qa-findings.json` (findings-only, NOT a full QA report);
                 unavailable channels carry Unknown markers.
        smoke  : returns 0 ONLY on pass, independent of optional channels;
                 a deliberate-fail run must NOT exit 0.
      When any prerequisite is absent it prints a clear SKIP and exits 0 (honest
      conditional skip, never a false PASS and never a hard FAIL for engine/app
      absence -- C2/DC1).

The no-browser unit path is the binding gate. The real-browser path is
conditional and skips honestly when prerequisites are absent.
"""
import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / ".gsd" / "browser-evidence.py"
RUN_ROOT = ROOT / ".planning" / "evidence" / "browser-runs"
TMP_ROOT = ROOT / ".planning" / "tmp" / "browser-harness"
REPLAY_PLAN = ".gsd/fixtures/browser-evidence/replay.plan.json"

# Conditional real-browser prerequisites. Probed (not assumed) before any real run.
CDP_URL = "http://127.0.0.1:9222/json/version"
APP_BASE_URL = "http://127.0.0.1:43111"

INTERNAL_VALIDATOR_FIXTURE_TIMESTAMP = "20000101-000000"
INTERNAL_VALIDATOR_FIXTURE_DEFAULT_RUN_ID = (
    f"{INTERNAL_VALIDATOR_FIXTURE_TIMESTAMP}-internal-validator-fixture-validation-child"
)
INTERNAL_VALIDATOR_FIXTURE_BLOCKED_RUN_ID = "20000101-000100-internal-validator-fixture-blocked-shape"
INTERNAL_VALIDATOR_FIXTURE_REAL_REPLAY_RUN_ID = "20000101-000200-real-replay-validator"
INTERNAL_VALIDATOR_FIXTURE_REAL_QA_RUN_ID = "20000101-000300-real-qa-validator"
INTERNAL_VALIDATOR_FIXTURE_REAL_SMOKE_PASS_RUN_ID = "20000101-000400-real-smoke-pass-validator"
INTERNAL_VALIDATOR_FIXTURE_REAL_SMOKE_FAIL_RUN_ID = "20000101-000500-real-smoke-fail-validator"

ALLOWED_STATUSES = {"passed", "failed", "partial", "blocked"}
EVIDENCE_STATUSES = {"Confirmed", "Suggested", "Unknown"}

REQUIRED_FILES = [
    "summary.json",
    "environment.json",
    "action-log.json",
    "network.json",
    "console.log",
    "storage-summary.json",
    "autonomy-policy.json",
    "safety-events.json",
    "app-process.log",
    "redaction-summary.json",
]
# blocked-run-only artifact.
BLOCKED_ONLY_FILES = ["blocker-details.json"]
REQUIRED_DIRS = ["screenshots", "page-states", "dom-snapshots"]


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path} did not read/parse as JSON: {exc}")


def run_wrapper(*args):
    return subprocess.run(
        [sys.executable, str(WRAPPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _http_reachable(url, timeout=3.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _engine_available():
    if shutil.which("browser-harness") is not None:
        return True
    ensure_script = ROOT / ".gsd" / "ensure-browser-harness.py"
    lock_path = ROOT / ".gsd" / "browser-harness.lock.json"
    if not ensure_script.is_file() or not lock_path.is_file():
        return False
    result = subprocess.run(
        [
            sys.executable,
            str(ensure_script),
            "--json",
            "--check-only",
            "--lock-path",
            str(lock_path),
            "--timeout-seconds",
            "30",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False
    return bool(payload.get("available"))


def _rmtree_quiet(*dirs):
    for directory in dirs:
        if directory and Path(directory).exists():
            shutil.rmtree(directory, ignore_errors=True)


def _assert_common_artifacts(run_dir, files, dirs):
    for name in files:
        if not (run_dir / name).exists():
            fail(f"required artifact is missing: {name}")
    for name in dirs:
        if not (run_dir / name).is_dir():
            fail(f"required artifact directory is missing: {name}")


# ---------------------------------------------------------------------------
# (1) No-browser UNIT path: blocked-artifact-shape check.
# ---------------------------------------------------------------------------

def check_blocked_artifact_shape(run_dir, run_id, validation_target_path):
    """Preserved blocked-shape check for a browser-evidence run.

    This keeps the existing invariant set intact:
    full artifact set incl. blocker-details.json, blocked failure.cause,
    redaction replacement + no Vault publication, non-mutating lifecycle, and
    the read-only validation-target record.
    """
    if not run_dir.exists():
        fail(f"run directory is missing: {run_dir}")

    _assert_common_artifacts(run_dir, REQUIRED_FILES + BLOCKED_ONLY_FILES, REQUIRED_DIRS)

    summary = load_json(run_dir / "summary.json")
    if summary.get("schemaVersion") != 1:
        fail("summary.schemaVersion must be 1")
    if summary.get("runId") != run_id:
        fail(f"summary.runId does not match {run_id}")
    if summary.get("mode") not in {"evidence", "replay", "qa", "smoke", "interactive"}:
        fail("summary.mode is not a browser evidence mode")
    if summary.get("status") not in ALLOWED_STATUSES:
        fail("summary.status is not an allowed value")
    if summary.get("status") == "blocked" and not summary.get("failure"):
        fail("blocked summary must include failure details")
    if not summary.get("failure", {}).get("cause"):
        fail("summary.failure.cause is required")

    safety = load_json(run_dir / "safety-events.json")
    redaction = load_json(run_dir / "redaction-summary.json")
    environment = load_json(run_dir / "environment.json")
    blocker = load_json(run_dir / "blocker-details.json")

    if not isinstance(safety.get("events"), list):
        fail("safety-events.json must include an events array")
    if redaction.get("redactionReplacement") != "[REDACTED_SECRET]":
        fail("redaction-summary.json must record the configured replacement")
    if redaction.get("vaultPublication") != "not-published":
        fail("redaction-summary.json must record no Vault publication")
    if not blocker.get("rawEvidenceFinalized") is False:
        fail("blocker-details.json must state rawEvidenceFinalized false")

    lifecycle = environment.get("lifecycle", {})
    if lifecycle.get("browserHarnessUpdateInvoked") is not False:
        fail("Browser Harness --update must not be invoked")
    if lifecycle.get("browserHarnessReloadInvoked") is not False:
        fail("Browser Harness --reload must not be invoked")
    if lifecycle.get("stdinExecutionInvoked") is not False:
        fail("Browser Harness stdin execution must not occur for this blocked run")
    if lifecycle.get("ownedProcessesStopped") is not True:
        fail("owned-process lifecycle handling must be explicit and complete")
    if lifecycle.get("unknownProcessesStopped") is not False:
        fail("unknown processes must not be stopped")

    validation_target = environment.get("validationTarget", {}).get("target", {})
    if validation_target.get("path") != validation_target_path:
        fail("validation target path does not match requested path")
    if validation_target.get("gitStatusBefore") != validation_target.get("gitStatusAfter"):
        fail("validation target git status changed during validation")
    if validation_target.get("mutationPolicy") != "read-only":
        fail("validation target mutation policy must be read-only")


def run_unit_path(args):
    """Self-generate a blocked run and assert the blocked-artifact shape.

    Self-generation makes this gate pass in EVERY environment (no dependency on
    an untracked fixture run dir). When --run-id is supplied, the shape check is
    pointed at that existing run dir instead (back-compat).
    """
    if args.run_id:
        run_dir = RUN_ROOT / args.run_id
        check_blocked_artifact_shape(run_dir, args.run_id, args.validation_target_path)
        print(f"PASS: no-browser UNIT path -- blocked-artifact shape valid for {args.run_id}")
        return

    unit_run_id = INTERNAL_VALIDATOR_FIXTURE_BLOCKED_RUN_ID
    run_dir = RUN_ROOT / unit_run_id
    tmp_dir = TMP_ROOT / unit_run_id
    _rmtree_quiet(run_dir, tmp_dir)
    # Point the validation target at the always-present repo ROOT so the
    # UNIT gate has NO dependency on an external repo resolving; the wrapper
    # records this path as environment.validationTarget.target.path and
    # the shape check only requires gitStatusBefore == gitStatusAfter (a dirty but
    # unchanged tree is fine), so this passes in every environment.
    unit_validation_target_path = str(ROOT)
    try:
        # No --allow-browser-harness + unreachable target => deterministic blocked run.
        result = run_wrapper(
            "evidence",
            "--target", "page:/",
            "--base-url", "http://127.0.0.1:9",
            "--project-path", unit_validation_target_path,
            "--run-id", unit_run_id,
        )
        if not run_dir.is_dir():
            fail(
                "no-browser UNIT path could not self-generate a blocked run; "
                f"exit={result.returncode} stderr={result.stderr.strip()}"
            )
        check_blocked_artifact_shape(run_dir, unit_run_id, unit_validation_target_path)
        print("PASS: no-browser UNIT path -- self-generated blocked-artifact shape valid")
    finally:
        _rmtree_quiet(run_dir, tmp_dir)


# ---------------------------------------------------------------------------
# (2) Conditional real-browser path: folded replay/qa/smoke discriminators.
# ---------------------------------------------------------------------------

def _check_mode_common(run_dir, run_id, expected_mode):
    _assert_common_artifacts(run_dir, REQUIRED_FILES, REQUIRED_DIRS)
    summary = load_json(run_dir / "summary.json")
    if summary.get("schemaVersion") != 1:
        fail("summary.schemaVersion must be 1")
    if summary.get("runId") != run_id:
        fail(f"summary.runId does not match {run_id}")
    if summary.get("mode") != expected_mode:
        fail(f"summary.mode must be {expected_mode}, got {summary.get('mode')}")
    if summary.get("status") not in ALLOWED_STATUSES:
        fail("summary.status is not an allowed value")
    if summary.get("evidence_status") not in EVIDENCE_STATUSES:
        fail("summary.evidence_status must be Confirmed/Suggested/Unknown")

    redaction = load_json(run_dir / "redaction-summary.json")
    if redaction.get("redactionReplacement") != "[REDACTED_SECRET]":
        fail("redaction-summary.json must record the configured replacement")
    if redaction.get("vaultPublication") != "not-published":
        fail("redaction-summary.json must record no Vault publication")

    action_log = load_json(run_dir / "action-log.json")
    if not isinstance(action_log, list):
        fail("action-log.json must be a JSON array")

    # Never a faked Confirmed when nothing real captured.
    if summary.get("status") == "blocked" and summary.get("evidence_status") == "Confirmed":
        fail("a blocked run must never be Confirmed")
    return summary, action_log


def check_replay(run_dir, run_id):
    summary, action_log = _check_mode_common(run_dir, run_id, "replay")

    replay = summary.get("replay", {})
    plan_steps = replay.get("planStepCount")
    if not isinstance(plan_steps, int) or plan_steps <= 0:
        fail("replay run must record summary.replay.planStepCount (>0)")

    step_entries = [a for a in action_log if isinstance(a, dict) and a.get("stepId")]
    if len(step_entries) != plan_steps:
        fail(
            f"replay action-log must record one entry per plan step "
            f"({plan_steps} expected, {len(step_entries)} found)"
        )
    for entry in step_entries:
        if entry.get("evidence_status") not in EVIDENCE_STATUSES:
            fail(f"replay step {entry.get('stepId')} missing a valid evidence_status")
        if "outcome" not in entry:
            fail(f"replay step {entry.get('stepId')} missing an outcome field")

    # At least one unsupported/failed action exists and is NOT Confirmed (downgrade-only).
    bad = [e for e in step_entries if e.get("outcome") in {"failed", "partial", "unsupported"}]
    if not bad:
        fail("replay run must exercise at least one unsupported/failed action")
    for e in bad:
        if e.get("evidence_status") == "Confirmed":
            fail(
                f"replay step {e.get('stepId')} ({e.get('outcome')}) must NOT carry "
                "evidence_status Confirmed"
            )
    print(
        f"PASS: conditional real-browser replay valid for {run_id} "
        f"(steps={plan_steps}, status={summary.get('status')})"
    )


def check_qa(run_dir, run_id):
    summary, _ = _check_mode_common(run_dir, run_id, "qa")

    findings_path = run_dir / "qa-findings.json"
    if not findings_path.exists():
        fail("qa run must write qa-findings.json")
    findings_doc = load_json(findings_path)
    findings = findings_doc.get("findings") if isinstance(findings_doc, dict) else findings_doc
    if not isinstance(findings, list):
        fail("qa-findings.json must contain a findings list")
    if not findings:
        fail("qa-findings.json must record at least one basic check finding")
    for f in findings:
        if not isinstance(f, dict) or "checkId" not in f or "status" not in f:
            fail("each qa finding must record at least checkId and status")
    # Findings only -- must NOT masquerade as a full QA report.
    if isinstance(findings_doc, dict) and findings_doc.get("reportType") == "full-qa-report":
        fail("qa mode must NOT produce a full QA report (gsd-qa-tester ownership)")

    network = load_json(run_dir / "network.json")
    if network.get("available") is False and network.get("evidence_status") != "Unknown":
        fail("qa unavailable network channel must carry evidence_status Unknown")
    print(
        f"PASS: conditional real-browser qa valid for {run_id} "
        f"(findings={len(findings)}, status={summary.get('status')})"
    )


def check_smoke(run_dir, run_id, expect_pass):
    summary, action_log = _check_mode_common(run_dir, run_id, "smoke")

    if not action_log:
        fail("smoke run must record at least one action-log entry")

    smoke = summary.get("smoke", {})
    passed = smoke.get("passed")
    if not isinstance(passed, bool):
        fail("smoke run must record summary.smoke.passed (bool)")

    exit_code = summary.get("exitCode")
    # The smoke pass rule: returns 0 ONLY on pass, independent of optional channels.
    if passed and exit_code != 0:
        fail(f"a passed smoke run must exit 0, got {exit_code}")
    if not passed and exit_code == 0:
        fail("a failed smoke run must NOT exit 0")
    if passed and summary.get("status") != "passed":
        fail("a passed smoke run must carry summary.status passed")

    if expect_pass is True and not passed:
        fail("expected a passing smoke run but smoke.passed is False")
    if expect_pass is False and passed:
        fail("expected a failing smoke run but smoke.passed is True")
    print(
        f"PASS: conditional real-browser smoke valid for {run_id} "
        f"(passed={passed}, exitCode={exit_code})"
    )


def run_real_browser_path(args):
    """Drive REAL replay/qa/smoke runs and assert mode behavior.

    Gated on engine + CDP + app availability; otherwise honest SKIP exit 0.
    Each real run is cleaned up (run dir + run-scoped tmp), and each run's
    recorded daemon lifecycle is checked so no orphan daemon is left behind.
    """
    replay_plan_path = ROOT / REPLAY_PLAN
    if not (
        _engine_available()
        and _http_reachable(CDP_URL)
        and _http_reachable(APP_BASE_URL)
        and replay_plan_path.exists()
    ):
        missing = []
        if not _engine_available():
            missing.append("engine-on-PATH-or-GSD-cache")
        if not _http_reachable(CDP_URL):
            missing.append(f"CDP({CDP_URL})")
        if not _http_reachable(APP_BASE_URL):
            missing.append(f"app({APP_BASE_URL})")
        if not replay_plan_path.exists():
            missing.append(f"replay-plan({REPLAY_PLAN})")
        print(
            "SKIP: conditional real-browser replay/qa/smoke path skipped honestly (missing: "
            + ", ".join(missing)
            + "); the no-browser UNIT path is the binding gate."
        )
        return

    common = [
        "--base-url", APP_BASE_URL,
        "--cdp-url", CDP_URL,
        "--allow-browser-harness",
    ]
    created = []

    def _drive(run_id, mode_args):
        run_dir = RUN_ROOT / run_id
        tmp_dir = TMP_ROOT / run_id
        _rmtree_quiet(run_dir, tmp_dir)
        created.append((run_dir, tmp_dir))
        result = run_wrapper(*mode_args, "--run-id", run_id)
        if not run_dir.is_dir():
            fail(
                f"real {mode_args[0]} run did not create a run dir; "
                f"exit={result.returncode} stderr={result.stderr.strip()}"
            )
        # Daemon orphan guard: the wrapper stops its run-scoped daemon in finally.
        environment = load_json(run_dir / "environment.json")
        if environment.get("lifecycle", {}).get("daemonStopped") is False:
            fail(f"real {mode_args[0]} run reported daemonStopped false (potential orphan daemon)")
        return run_dir

    try:
        # replay: drive the action-bearing internal fixture (includes one unsupported step).
        replay_id = INTERNAL_VALIDATOR_FIXTURE_REAL_REPLAY_RUN_ID
        replay_dir = _drive(replay_id, ["replay", "--target", "page:/", "--replay-plan", REPLAY_PLAN] + common)
        check_replay(replay_dir, replay_id)

        # qa: findings-only.
        qa_id = INTERNAL_VALIDATOR_FIXTURE_REAL_QA_RUN_ID
        qa_dir = _drive(qa_id, ["qa", "--target", "page:/"] + common)
        check_qa(qa_dir, qa_id)

        # smoke PASS: assert a string known to be present.
        smoke_pass_id = INTERNAL_VALIDATOR_FIXTURE_REAL_SMOKE_PASS_RUN_ID
        smoke_pass_dir = _drive(smoke_pass_id, ["smoke", "--path", "/", "--assert-text", "Pattern"] + common)
        check_smoke(smoke_pass_dir, smoke_pass_id, expect_pass=True)

        # smoke FAIL: assert a string known to be absent -> must NOT exit 0.
        smoke_fail_id = INTERNAL_VALIDATOR_FIXTURE_REAL_SMOKE_FAIL_RUN_ID
        smoke_fail_dir = _drive(
            smoke_fail_id,
            ["smoke", "--path", "/", "--assert-text", "ZZZ-absent-string-unlikely-9f3a"] + common,
        )
        check_smoke(smoke_fail_dir, smoke_fail_id, expect_pass=False)

        print("PASS: conditional real-browser path -- replay/qa/smoke valid")
    finally:
        for run_dir, tmp_dir in created:
            _rmtree_quiet(run_dir, tmp_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Validate browser-evidence blocked-shape (unit) + real replay/qa/smoke (conditional)."
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional: point the blocked-shape unit check at an existing run dir (back-compat).",
    )
    parser.add_argument("--validation-target-path", default=str(ROOT), help="Validation target path.")
    parser.add_argument(
        "--legacy-default-run",
        action="store_true",
        help="Use the legacy committed internal validator fixture run id for the blocked-shape check.",
    )
    args = parser.parse_args()

    if args.legacy_default_run and not args.run_id:
        args.run_id = INTERNAL_VALIDATOR_FIXTURE_DEFAULT_RUN_ID

    run_unit_path(args)
    run_real_browser_path(args)


if __name__ == "__main__":
    main()
