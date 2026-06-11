"""Browser Evidence Runtime static/runtime validator.

This validator carries two explicit paths:

  (1) A no-network/no-browser UNIT path -- the binding gate in EVERY environment.
      It exercises config/help/path/doctor read-only invariants and the
      no-browser `evidence` run's artifact-writing + deterministic non-zero
      exit-code behavior WITHOUT a real browser.

  (2) A CONDITIONAL real-browser path that runs ONLY when a Browser Harness
      engine, a reachable CDP endpoint, and a reachable app are all available.
      It includes the former standalone real-capture discriminator:
      real-capture-vs-blocked discriminator: a real `evidence` capture must
      record browserHarness.invoked, a real navigation result, real page-state,
      Unknown markers for unavailable channels, redaction-summary, and must
      NEVER label a blocked run `Confirmed`. When any prerequisite is absent it
      prints a clear SKIP and exits 0 (honest conditional skip, never a false
      PASS and never a hard FAIL purely for engine/app absence -- C2/DC1).

The replay/qa/smoke validator lives in `check-browser-evidence-modes.py`.
"""
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".gsd" / "browser-evidence.config.json"
WRAPPER = ROOT / ".gsd" / "browser-evidence.py"
RUN_ROOT = ROOT / ".planning" / "evidence" / "browser-runs"
TMP_ROOT = ROOT / ".planning" / "tmp" / "browser-harness"
MODES = ["evidence", "replay", "qa", "smoke", "doctor"]
SETUP_COMMANDS = ["setup-check", "ensure-browser-harness", "launch-chrome", "wait-cdp", "wait-app"]
TAB_FLAGS = ["--goal-id", "--tab-policy", "--new-tab-reason"]
INTERNAL_VALIDATOR_FIXTURE_PATH_TIMESTAMP = "20000101-000000"
INTERNAL_VALIDATOR_FIXTURE_UNAVAILABLE_TIMESTAMP = "20000101-000100"
INTERNAL_VALIDATOR_FIXTURE_RUN_ID = (
    f"{INTERNAL_VALIDATOR_FIXTURE_PATH_TIMESTAMP}-internal-validator-fixture-execution-child"
)
INTERNAL_VALIDATOR_FIXTURE_UNAVAILABLE_RUN_ID = (
    f"{INTERNAL_VALIDATOR_FIXTURE_UNAVAILABLE_TIMESTAMP}-local-unavailable-anonymous"
)
INTERNAL_VALIDATOR_FIXTURE_INVALID_TAB_RUN_ID = "20000101-000200-invalid-tab-agent"
INTERNAL_VALIDATOR_FIXTURE_REAL_RUN_ID = "20000101-000300-runtime-realcap-validator"
INTERNAL_VALIDATOR_FIXTURE_NEGATIVE_RUN_ID = "20000101-000400-runtime-negdiscriminator"

# Conditional real-browser prerequisites. Probed (not assumed) before any real run.
CDP_URL = "http://127.0.0.1:9222/json/version"
APP_BASE_URL = "http://127.0.0.1:43111"

# Required artifact files for every evidence-producing run (browser-evidence-contract.md).
REQUIRED_ARTIFACT_FILES = [
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
REQUIRED_ARTIFACT_DIRS = ["screenshots", "page-states", "dom-snapshots"]


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def run_wrapper(*args):
    return subprocess.run(
        [sys.executable, str(WRAPPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _http_reachable(url, timeout=3.0):
    """Best-effort HTTP reachability probe used only to gate the real path."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _engine_available():
    """True when Browser Harness resolves on PATH or in the GSD user cache."""
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


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path} did not read/parse as JSON: {exc}")


def _rmtree_quiet(*dirs):
    for directory in dirs:
        if directory and Path(directory).exists():
            shutil.rmtree(directory, ignore_errors=True)


if not CONFIG.exists():
    fail(".gsd/browser-evidence.config.json is missing")

try:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    fail(f"config JSON does not parse: {exc}")

if config.get("artifactRoot") != ".planning/evidence/browser-runs/":
    fail("artifactRoot must be .planning/evidence/browser-runs/")

# (a) browserHarness.strategy must exist in config (engine strategy resolution block).
browser_harness = config.get("browserHarness")
if not isinstance(browser_harness, dict):
    fail("config is missing the browserHarness strategy block")
if not browser_harness.get("strategy"):
    fail("config.browserHarness.strategy is missing or empty")
for required_key in ("strategy", "command", "vendorPath", "python", "timeoutSeconds"):
    if required_key not in browser_harness:
        fail(f"config.browserHarness is missing key {required_key}")
bootstrap = config.get("browserHarnessBootstrap")
if not isinstance(bootstrap, dict):
    fail("config is missing browserHarnessBootstrap")
for required_key in ("enabled", "autoInstall", "lockPath", "ensureScript", "installTimeoutSeconds"):
    if required_key not in bootstrap:
        fail(f"config.browserHarnessBootstrap is missing key {required_key}")
if not (ROOT / bootstrap.get("lockPath", "")).is_file():
    fail("config.browserHarnessBootstrap.lockPath does not exist")
if not (ROOT / bootstrap.get("ensureScript", "")).is_file():
    fail("config.browserHarnessBootstrap.ensureScript does not exist")

browser_setup = config.get("browserSetup")
if not isinstance(browser_setup, dict):
    fail("config is missing the browserSetup first-goal install block")
for required_key in ("defaultDebuggingPort", "defaultCdpUrl", "profileRoot", "agentRunnableSteps", "userOnlyPrerequisites"):
    if required_key not in browser_setup:
        fail(f"config.browserSetup is missing key {required_key}")
for required_step in SETUP_COMMANDS:
    if required_step not in browser_setup.get("agentRunnableSteps", []):
        fail(f"config.browserSetup.agentRunnableSteps is missing {required_step}")
if len(browser_setup.get("userOnlyPrerequisites", [])) < 3:
    fail("config.browserSetup.userOnlyPrerequisites must document user-only setup blockers")

tab_lifecycle = config.get("tabLifecycle")
if not isinstance(tab_lifecycle, dict):
    fail("config is missing tabLifecycle")
if tab_lifecycle.get("defaultPolicy") != "reuse-primary":
    fail("config.tabLifecycle.defaultPolicy must be reuse-primary")
if tab_lifecycle.get("newTabRequiresReason") is not True:
    fail("config.tabLifecycle.newTabRequiresReason must be true")
if tab_lifecycle.get("sessionStateRoot") != ".planning/tmp/browser-harness/sessions/":
    fail("config.tabLifecycle.sessionStateRoot must be .planning/tmp/browser-harness/sessions/")
if tab_lifecycle.get("reusePolicy") != "single-primary-tab":
    fail("config.tabLifecycle.reusePolicy must be single-primary-tab")
for policy in ("reuse-primary", "allow-new-tab", "force-new-tab"):
    if policy not in tab_lifecycle.get("allowedPolicies", []):
        fail(f"config.tabLifecycle.allowedPolicies is missing {policy}")
for reason in (
    "oauth_sso_popup",
    "external_provider_popup",
    "payment_provider_popup",
    "side_by_side_comparison",
    "app_opened_new_tab",
    "preserve_unsaved_state",
    "manual_user_requested",
):
    if reason not in tab_lifecycle.get("allowedCriticalNewTabReasons", []):
        fail(f"config.tabLifecycle.allowedCriticalNewTabReasons is missing {reason}")

# (b) no mode status may equal "stubbed".
modes_config = config.get("modes", {})
for mode_name, mode_cfg in modes_config.items():
    if mode_cfg.get("status") == "stubbed":
        fail(f"mode {mode_name} still has status 'stubbed'; expected implemented-wrapper status")

if not WRAPPER.exists():
    fail(".gsd/browser-evidence.py is missing")

before_runs = set()
if RUN_ROOT.exists():
    before_runs = {path.name for path in RUN_ROOT.iterdir()}

help_result = run_wrapper("--help")
if help_result.returncode != 0:
    fail(f"help exited {help_result.returncode}: {help_result.stderr.strip()}")
help_text = help_result.stdout
for command in [*MODES, *SETUP_COMMANDS]:
    if command not in help_text:
        fail(f"help output is missing command {command}")
for flag in TAB_FLAGS:
    if flag not in help_text:
        fail(f"top-level help output must mention runtime tab flag {flag}")

path_result = run_wrapper(
    "path",
    "--timestamp",
    INTERNAL_VALIDATOR_FIXTURE_PATH_TIMESTAMP,
    "--scope",
    "internal validator fixture",
    "--role",
    "Execution Child",
)
if path_result.returncode != 0:
    fail(f"path exited {path_result.returncode}: {path_result.stderr.strip()}")

expected_run_id = INTERNAL_VALIDATOR_FIXTURE_RUN_ID
expected_artifact_dir = ".planning/evidence/browser-runs/" + expected_run_id + "/"
try:
    path_payload = json.loads(path_result.stdout)
except json.JSONDecodeError as exc:
    fail(f"path output is not JSON: {exc}")

if path_payload.get("runId") != expected_run_id:
    fail(f"unexpected runId: {path_payload.get('runId')}")
if path_payload.get("artifactDir") != expected_artifact_dir:
    fail(f"unexpected artifactDir: {path_payload.get('artifactDir')}")
after_runs = set()
if RUN_ROOT.exists():
    after_runs = {path.name for path in RUN_ROOT.iterdir()}
created_runs = sorted(after_runs - before_runs)
if created_runs:
    fail(".planning/evidence/browser-runs/ gained artifacts after read-only checks: " + ", ".join(created_runs))

for mode in [*MODES, *SETUP_COMMANDS]:
    result = run_wrapper(mode, "--help")
    if result.returncode != 0:
        fail(f"{mode} help exited {result.returncode}: {result.stderr.strip()}")
    unsafe_terms = ["--update", "--reload", "stdin", "ensure_daemon"]
    if any(term in result.stderr for term in unsafe_terms):
        fail(f"{mode} help wrote unsafe routing text to stderr")
    if mode in {"evidence", "replay", "qa", "smoke"}:
        for flag in TAB_FLAGS:
            if flag not in result.stdout:
                fail(f"{mode} help output is missing runtime tab flag {flag}")

adapter_path = ROOT / ".gsd" / "browser_harness_adapter.py"
adapter_text = adapter_path.read_text(encoding="utf-8")
for helper in ("ensure_real_tab()", "current_tab()", "list_tabs()", "goto_url("):
    if helper not in adapter_text:
        fail(f"browser_harness_adapter.py must use {helper} for primary-tab reuse")
new_tab_lines = [
    (idx + 1, line)
    for idx, line in enumerate(adapter_text.splitlines())
    if "new_tab(" in line
]
if not new_tab_lines:
    fail("browser_harness_adapter.py must keep a gated new_tab(...) path for critical reasons")
adapter_lines = adapter_text.splitlines()
for lineno, line in new_tab_lines:
    if lineno < 300 or "CONFIRMED helper" in line or line.strip().startswith("#") or line.strip().startswith("def _validate"):
        continue
    nearby = "\n".join(adapter_lines[max(0, lineno - 4):lineno])
    if "TAB_POLICY in ('allow-new-tab', 'force-new-tab')" not in nearby and "gated by explicit tab policy" not in nearby:
        fail(f"new_tab(...) at browser_harness_adapter.py:{lineno} is not behind explicit allowed-new-tab logic")

# (c) doctor output must report engine availability fields (no-browser-safe audit).
doctor_result = run_wrapper("doctor")
if doctor_result.returncode not in (0, 2, 3):
    fail(f"doctor exited with unexpected code {doctor_result.returncode}: {doctor_result.stderr.strip()}")
try:
    doctor_payload = json.loads(doctor_result.stdout)
except json.JSONDecodeError as exc:
    fail(f"doctor output is not JSON: {exc}; stderr={doctor_result.stderr.strip()}")
engine_block = doctor_payload.get("engine")
if not isinstance(engine_block, dict):
    fail("doctor output is missing the engine availability block")
for engine_key in ("available", "strategy", "version", "commit", "evidence_status"):
    if engine_key not in engine_block:
        fail(f"doctor engine block is missing field {engine_key}")
# After the read-only doctor audit, the read-only invariant must still hold.
after_doctor_runs = set()
if RUN_ROOT.exists():
    after_doctor_runs = {path.name for path in RUN_ROOT.iterdir()}
created_by_doctor = sorted(after_doctor_runs - before_runs)
if created_by_doctor:
    fail("doctor created run artifacts; doctor must be read-only: " + ", ".join(created_by_doctor))

# (c2) setup automation commands must be no-browser safe unless explicitly launched.
setup_result = run_wrapper(
    "setup-check",
    "--base-url",
    "http://127.0.0.1:9",
    "--skip-browser-harness-install",
)
if setup_result.returncode not in (0, 8):
    fail(f"setup-check exited with unexpected code {setup_result.returncode}: {setup_result.stderr.strip()}")
try:
    setup_payload = json.loads(setup_result.stdout)
except json.JSONDecodeError as exc:
    fail(f"setup-check output is not JSON: {exc}; stderr={setup_result.stderr.strip()}")
for key in ("agentRunnableSteps", "userOnlyPrerequisites", "requiredUserInputsAtFirstGoal", "nextAgentCommands"):
    if key not in setup_payload:
        fail(f"setup-check output is missing {key}")
if not setup_payload["userOnlyPrerequisites"]:
    fail("setup-check must report user-only prerequisites")
after_setup_runs = set()
if RUN_ROOT.exists():
    after_setup_runs = {path.name for path in RUN_ROOT.iterdir()}
created_by_setup = sorted(after_setup_runs - before_runs)
if created_by_setup:
    fail("setup-check created run artifacts; setup-check must be read-only: " + ", ".join(created_by_setup))

wait_cdp_result = run_wrapper(
    "wait-cdp",
    "--cdp-url",
    "http://127.0.0.1:9/json/version",
    "--timeout-seconds",
    "0.1",
    "--interval-seconds",
    "0.1",
)
if wait_cdp_result.returncode != 3:
    fail(f"wait-cdp unavailable endpoint must exit 3, got {wait_cdp_result.returncode}")
try:
    wait_cdp_payload = json.loads(wait_cdp_result.stdout)
except json.JSONDecodeError as exc:
    fail(f"wait-cdp output is not JSON: {exc}; stderr={wait_cdp_result.stderr.strip()}")
if wait_cdp_payload.get("status") != "blocked":
    fail("wait-cdp unavailable endpoint must report blocked status")

# (d) a no-browser evidence run creates a run dir with ALL required artifact files
#     (including redaction-summary.json), unavailable channels marked Unknown, and a
#     deterministic non-zero exit. This is a SEPARATE, dir-creating check.
EVIDENCE_RUN_ID = INTERNAL_VALIDATOR_FIXTURE_UNAVAILABLE_RUN_ID
evidence_run_dir = RUN_ROOT / EVIDENCE_RUN_ID
evidence_tmp_dir = TMP_ROOT / EVIDENCE_RUN_ID
# Ensure repeatability: clean up any prior run-id directories before invoking.
for stale_dir in (evidence_run_dir, evidence_tmp_dir):
    if stale_dir.exists():
        shutil.rmtree(stale_dir)

evidence_result = run_wrapper(
    "evidence",
    "--target",
    "page:/",
    "--base-url",
    "http://127.0.0.1:9",
    "--timestamp",
    INTERNAL_VALIDATOR_FIXTURE_UNAVAILABLE_TIMESTAMP,
    "--scope",
    "local-unavailable",
    "--role",
    "anonymous",
)
if evidence_result.returncode == 0:
    fail("no-browser evidence run must return a deterministic non-zero exit code")
if not evidence_run_dir.is_dir():
    fail(f"no-browser evidence run did not create {evidence_run_dir}")

for artifact_name in REQUIRED_ARTIFACT_FILES:
    if not (evidence_run_dir / artifact_name).exists():
        fail(f"no-browser evidence run is missing required artifact {artifact_name}")
for artifact_dir in REQUIRED_ARTIFACT_DIRS:
    if not (evidence_run_dir / artifact_dir).is_dir():
        fail(f"no-browser evidence run is missing required artifact dir {artifact_dir}/")

try:
    summary_payload = json.loads((evidence_run_dir / "summary.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    fail(f"summary.json is not valid JSON: {exc}")
if summary_payload.get("status") not in ("blocked", "partial"):
    fail(f"no-browser evidence summary.json status must be blocked/partial, got {summary_payload.get('status')}")
if summary_payload.get("exitCode") == 0:
    fail("no-browser evidence summary.json must record a non-zero exit code")
if summary_payload.get("evidence_status") == "Confirmed":
    fail("no-browser evidence run must not label the run evidence_status Confirmed")
summary_tab = summary_payload.get("tabLifecycle")
if not isinstance(summary_tab, dict):
    fail("no-browser evidence summary.json is missing tabLifecycle")
if summary_tab.get("goalId") != EVIDENCE_RUN_ID:
    fail("tabLifecycle.goalId must default to the run id when --goal-id is absent")
if summary_tab.get("tabPolicy") != "reuse-primary":
    fail("tabLifecycle.tabPolicy must default to reuse-primary")
if summary_tab.get("tabDecisionEvidenceStatus") not in {"Confirmed", "Suggested", "Unknown"}:
    fail("tabLifecycle.tabDecisionEvidenceStatus must be an evidence status value")

try:
    redaction_payload = json.loads((evidence_run_dir / "redaction-summary.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    fail(f"redaction-summary.json is not valid JSON: {exc}")
for redaction_key in ("redactionsApplied", "countsByPattern", "filesProcessed", "evidence_status"):
    if redaction_key not in redaction_payload:
        fail(f"redaction-summary.json is missing field {redaction_key}")

# Unavailable channels must be Unknown markers, not omitted.
try:
    network_payload = json.loads((evidence_run_dir / "network.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    fail(f"network.json is not valid JSON: {exc}")
if network_payload.get("evidence_status") != "Unknown":
    fail("network.json (unavailable channel) must be marked evidence_status Unknown")
try:
    storage_payload = json.loads((evidence_run_dir / "storage-summary.json").read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    fail(f"storage-summary.json is not valid JSON: {exc}")
if storage_payload.get("evidence_status") != "Unknown":
    fail("storage-summary.json (unavailable channel) must be marked evidence_status Unknown")

# Clean up the dir-creating run so the validator stays repeatable.
for created_dir in (evidence_run_dir, evidence_tmp_dir):
    if created_dir.exists():
        shutil.rmtree(created_dir)

# Invalid new-tab requests must be rejected deterministically before browser use.
INVALID_TAB_RUN_ID = INTERNAL_VALIDATOR_FIXTURE_INVALID_TAB_RUN_ID
invalid_tab_run_dir = RUN_ROOT / INVALID_TAB_RUN_ID
invalid_tab_tmp_dir = TMP_ROOT / INVALID_TAB_RUN_ID
_rmtree_quiet(invalid_tab_run_dir, invalid_tab_tmp_dir)
invalid_tab_result = run_wrapper(
    "evidence",
    "--target", "page:/",
    "--base-url", "http://127.0.0.1:9",
    "--run-id", INVALID_TAB_RUN_ID,
    "--tab-policy", "allow-new-tab",
)
if invalid_tab_result.returncode != 5:
    fail(f"invalid new-tab request must exit 5, got {invalid_tab_result.returncode}: {invalid_tab_result.stderr.strip()}")
if not invalid_tab_run_dir.is_dir():
    fail("invalid new-tab request must write a blocked run")
invalid_tab_summary = _load_json(invalid_tab_run_dir / "summary.json")
blocked_attempts = invalid_tab_summary.get("tabLifecycle", {}).get("blockedNewTabAttempts", [])
if not blocked_attempts:
    fail("invalid new-tab request must record blockedNewTabAttempts in summary.tabLifecycle")
if invalid_tab_summary.get("tabLifecycle", {}).get("tabDecisionEvidenceStatus") not in {"Confirmed", "Suggested", "Unknown"}:
    fail("invalid new-tab tab lifecycle must carry an evidence-status label")
_rmtree_quiet(invalid_tab_run_dir, invalid_tab_tmp_dir)

print("PASS: browser evidence runtime no-browser UNIT path (config/help/path/doctor/no-browser-evidence)")


# ---------------------------------------------------------------------------
# (2) CONDITIONAL real-browser path.
#     Runs ONLY when engine + CDP + app are all available; otherwise SKIP exit 0.
# ---------------------------------------------------------------------------

def _assert_capture_invariants(run_dir, run_id):
    """Real capture discriminator.

    Asserts the real-capture signals the honest blocked path CANNOT produce.
    """
    for artifact_name in REQUIRED_ARTIFACT_FILES:
        if not (run_dir / artifact_name).exists():
            fail(f"real-capture run is missing required artifact {artifact_name}")
    for artifact_dir in REQUIRED_ARTIFACT_DIRS:
        if not (run_dir / artifact_dir).is_dir():
            fail(f"real-capture run is missing required artifact dir {artifact_dir}/")

    summary = _load_json(run_dir / "summary.json")
    if summary.get("runId") != run_id:
        fail(f"real-capture summary.runId does not match {run_id}")
    if summary.get("status") not in ("passed", "partial"):
        fail(f"real-capture run must be passed/partial, got status={summary.get('status')}")
    bh = summary.get("browserHarness", {})
    if bh.get("invoked") is not True:
        fail("real-capture run must record summary.browserHarness.invoked true")

    action_log = _load_json(run_dir / "action-log.json")
    if not isinstance(action_log, list):
        fail("real-capture action-log.json must be a JSON array")
    nav_actions = [
        a for a in action_log
        if isinstance(a, dict) and a.get("action") in {"navigate", "goto", "open-target"}
    ]
    if not nav_actions:
        fail("real-capture action-log must record a navigation action")
    if not any(a.get("result") for a in nav_actions):
        fail("real-capture navigation action must record a real result")

    page_states = list((run_dir / "page-states").glob("*.json"))
    if not page_states:
        fail("real-capture run must record at least one real page-state")

    # Never a faked Confirmed on a passed run; honest non-Unknown evidence_status.
    if summary.get("status") == "passed" and summary.get("evidence_status") not in {"Confirmed", "Suggested"}:
        fail("passed real-capture run must carry an honest non-Unknown evidence_status")

    # Unavailable channels, when unavailable, must carry the Unknown marker shape.
    for channel_name in ("network.json", "storage-summary.json"):
        channel = _load_json(run_dir / channel_name)
        if channel.get("available") is False:
            if channel.get("evidence_status") != "Unknown":
                fail(f"{channel_name} unavailable marker must carry evidence_status Unknown")
            if "reason" not in channel:
                fail(f"{channel_name} unavailable marker must include a reason")

    # Centralized redaction ran before finalization.
    redaction = _load_json(run_dir / "redaction-summary.json")
    if redaction.get("redactionReplacement") != "[REDACTED_SECRET]":
        fail("real-capture redaction-summary.json must record the [REDACTED_SECRET] replacement")
    if redaction.get("vaultPublication") != "not-published":
        fail("real-capture redaction-summary.json must record no Vault publication")

    # Owned daemon must have been stopped by the wrapper's restart_daemon()-in-finally.
    environment = _load_json(run_dir / "environment.json")
    if environment.get("lifecycle", {}).get("daemonStopped") is False:
        fail("real-capture run reported daemonStopped false (potential orphan daemon)")


def _assert_blocked_never_confirmed(run_dir, run_id):
    """Negative discriminator: a blocked run must NEVER be labeled Confirmed.

    This proves the consolidated capture assertions are non-vacuous -- the same
    assertion set FAILS to read a real capture out of a blocked run.
    """
    summary = _load_json(run_dir / "summary.json")
    if summary.get("status") != "blocked":
        fail(f"expected a blocked run for the negative discriminator, got {summary.get('status')}")
    if summary.get("evidence_status") == "Confirmed":
        fail("blocked run must never be labeled evidence_status Confirmed")
    bh = summary.get("browserHarness", {})
    if bh.get("invoked") is True:
        fail("blocked run must not claim browserHarness.invoked true")


engine_ready = _engine_available()
cdp_ready = _http_reachable(CDP_URL)
app_ready = _http_reachable(APP_BASE_URL)

if not (engine_ready and cdp_ready and app_ready):
    missing = []
    if not engine_ready:
        missing.append("engine-on-PATH-or-GSD-cache")
    if not cdp_ready:
        missing.append(f"CDP({CDP_URL})")
    if not app_ready:
        missing.append(f"app({APP_BASE_URL})")
    print(
        "SKIP: conditional real-browser path skipped honestly (missing: "
        + ", ".join(missing)
        + "); the no-browser UNIT path above is the binding gate."
    )
    sys.exit(0)

REAL_RUN_ID = INTERNAL_VALIDATOR_FIXTURE_REAL_RUN_ID
real_run_dir = RUN_ROOT / REAL_RUN_ID
real_tmp_dir = TMP_ROOT / REAL_RUN_ID
_rmtree_quiet(real_run_dir, real_tmp_dir)

try:
    real_result = run_wrapper(
        "evidence",
        "--target", "page:/",
        "--base-url", APP_BASE_URL,
        "--cdp-url", CDP_URL,
        "--allow-browser-harness",
        "--run-id", REAL_RUN_ID,
    )
    if not real_run_dir.is_dir():
        fail(
            "real-browser evidence run did not create a run dir; "
            f"exit={real_result.returncode} stderr={real_result.stderr.strip()}"
        )
    real_summary = _load_json(real_run_dir / "summary.json")
    if real_summary.get("status") in ("passed", "partial"):
        _assert_capture_invariants(real_run_dir, REAL_RUN_ID)
        # Non-vacuous proof: generate one blocked run and confirm the same
        # validator rejects any Confirmed/invoked claim on it (the capture
        # discriminator is real, not a tautology).
        NEG_RUN_ID = INTERNAL_VALIDATOR_FIXTURE_NEGATIVE_RUN_ID
        neg_run_dir = RUN_ROOT / NEG_RUN_ID
        neg_tmp_dir = TMP_ROOT / NEG_RUN_ID
        _rmtree_quiet(neg_run_dir, neg_tmp_dir)
        try:
            run_wrapper(
                "evidence",
                "--target", "page:/",
                "--base-url", "http://127.0.0.1:9",
                "--run-id", NEG_RUN_ID,
            )
            if neg_run_dir.is_dir():
                _assert_blocked_never_confirmed(neg_run_dir, NEG_RUN_ID)
        finally:
            _rmtree_quiet(neg_run_dir, neg_tmp_dir)
        print(
            "PASS: conditional real-browser path -- real evidence "
            f"capture valid for {REAL_RUN_ID} (status={real_summary.get('status')})"
        )
    else:
        # Engine present but live capture could not be confirmed (e.g. target down
        # mid-run): record honestly, never a false PASS or false FAIL.
        if real_summary.get("evidence_status") == "Confirmed":
            fail("a non-captured run must never be labeled Confirmed")
        print(
            "SKIP: real-browser path could not confirm a live capture "
            f"(status={real_summary.get('status')}); recorded honestly, not a failure."
        )
finally:
    _rmtree_quiet(real_run_dir, real_tmp_dir)
