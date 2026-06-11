import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_harness_adapter import BrowserHarnessAdapter  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".gsd" / "browser-evidence.config.json"
MODES = ("evidence", "replay", "qa", "smoke", "doctor")
SETUP_COMMANDS = ("setup-check", "ensure-browser-harness", "launch-chrome", "wait-cdp", "wait-app")
STATUS_VALUES = ("passed", "failed", "partial", "blocked")
TAB_POLICIES = ("reuse-primary", "allow-new-tab", "force-new-tab")

# Deterministic exit-code map (browser-evidence-contract.md: exit-code map).
EXIT_PASS = 0
EXIT_ASSERTION = 1
EXIT_CONFIG = 2
EXIT_ENGINE = 3
EXIT_APP_HEALTH = 4
EXIT_AUTONOMY_BLOCK = 5
EXIT_REPLAY_CONTRACT = 6
EXIT_REDACTION = 7
EXIT_PARTIAL_BLOCKED = 8

# Centralized redaction patterns. Secret values are replaced before any artifact
# is finalized (evidence-redaction-safety-contract.md: redaction-before-finalization).
REDACTION_REPLACEMENT = "[REDACTED_SECRET]"
_REDACTION_PATTERNS = {
    "authorization-header": re.compile(r"(?i)(authorization\s*[:=]\s*)(bearer\s+)?[^\s\"',]+"),
    "bearer-token": re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+"),
    "cookie": re.compile(r"(?i)(set-cookie|cookie)\s*[:=]\s*[^\s\"',]+"),
    "password": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*[^\s\"',]+"),
    "token": re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|token)\s*[:=]\s*[^\s\"',]+"),
    "connection-string": re.compile(r"(?i)[a-z]+://[^\s:@/]+:[^\s:@/]+@[^\s\"',]+"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC )?PRIVATE KEY-----"),
}


def _tab_config(config):
    return config.get("tabLifecycle", {})


def _allowed_new_tab_reasons(config):
    return set(_tab_config(config).get("allowedCriticalNewTabReasons", []))


def _normalize_goal_id(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", (value or "").strip()).strip("-") or "manual"


def _goal_id_for_run(args, run_id):
    supplied = getattr(args, "goal_id", "") or ""
    return _normalize_goal_id(supplied or run_id or f"{getattr(args, 'scope', 'manual')}-{getattr(args, 'role', 'agent')}")


def _tab_lifecycle_baseline(config, args, run_id, blocked_attempt=None):
    tab_cfg = _tab_config(config)
    policy = getattr(args, "tab_policy", None) or tab_cfg.get("defaultPolicy", "reuse-primary")
    goal_id = _goal_id_for_run(args, run_id)
    blocked = []
    if blocked_attempt:
        blocked.append(blocked_attempt)
    return {
        "goalId": goal_id,
        "tabPolicy": policy,
        "reusePolicy": tab_cfg.get("reusePolicy", "single-primary-tab"),
        "primaryTargetId": "",
        "primaryTabUrlBefore": "",
        "primaryTabUrlAfter": "",
        "openedNewTabs": [],
        "closedExtraTabs": [],
        "preservedTabs": [],
        "newTabReasons": [],
        "blockedNewTabAttempts": blocked,
        "tabDecisionEvidenceStatus": "Confirmed",
    }


def _merge_tab_lifecycle(config, args, run_id, observed):
    baseline = _tab_lifecycle_baseline(config, args, run_id)
    if isinstance(observed, dict):
        for key in baseline:
            if key in observed:
                baseline[key] = observed[key]
    return baseline


def _tab_decision(tab_lifecycle):
    opened = tab_lifecycle.get("openedNewTabs", [])
    return {
        "usedPrimaryTab": not bool(opened),
        "openedNewTab": bool(opened),
        "newTabReason": ", ".join(tab_lifecycle.get("newTabReasons", [])),
        "closedRunOwnedTabs": tab_lifecycle.get("closedExtraTabs", []),
        "evidence_status": tab_lifecycle.get("tabDecisionEvidenceStatus", "Confirmed"),
    }


def _validate_tab_args(config, args):
    tab_cfg = _tab_config(config)
    allowed_policies = tuple(tab_cfg.get("allowedPolicies", TAB_POLICIES))
    policy = getattr(args, "tab_policy", None) or tab_cfg.get("defaultPolicy", "reuse-primary")
    reason = (getattr(args, "new_tab_reason", "") or "").strip()
    if policy not in allowed_policies:
        return f"tab policy {policy!r} is not allowed"
    if policy in ("allow-new-tab", "force-new-tab"):
        if not reason:
            return f"--tab-policy {policy} requires --new-tab-reason"
        if reason not in _allowed_new_tab_reasons(config):
            return f"--new-tab-reason {reason!r} is not an allowed critical new-tab reason"
    if policy == "reuse-primary" and reason:
        return "--new-tab-reason requires --tab-policy allow-new-tab or force-new-tab"
    return ""


def redact_text(text):
    """Redact secrets in a string. Returns (redacted_text, counts_by_pattern)."""
    counts = {}
    if not text:
        return text, counts
    redacted = text
    for name, pattern in _REDACTION_PATTERNS.items():
        redacted, n = pattern.subn(REDACTION_REPLACEMENT, redacted)
        if n:
            counts[name] = counts.get(name, 0) + n
    return redacted, counts


def redact_payload(value, counts):
    """Recursively redact strings inside a JSON-serializable structure, accumulating counts."""
    if isinstance(value, str):
        redacted, local = redact_text(value)
        for key, num in local.items():
            counts[key] = counts.get(key, 0) + num
        return redacted
    if isinstance(value, list):
        return [redact_payload(item, counts) for item in value]
    if isinstance(value, dict):
        return {key: redact_payload(item, counts) for key, item in value.items()}
    return value


def _run_scoped_env(run_id, artifact_dir):
    """Compute and create run-scoped environment isolation.

    Returns a dict of env var names -> values; creates the runtime/tmp dirs.
    """
    runtime_dir = f".planning/tmp/browser-harness/{run_id}/runtime"
    tmp_dir = f".planning/tmp/browser-harness/{run_id}/tmp"
    (ROOT / runtime_dir).mkdir(parents=True, exist_ok=True)
    (ROOT / tmp_dir).mkdir(parents=True, exist_ok=True)
    return {
        "BU_NAME": f"gsd-{run_id}",
        "BH_RUNTIME_DIR": runtime_dir,
        "BH_TMP_DIR": tmp_dir,
        "GSD_BROWSER_RUN_ID": run_id,
        "GSD_BROWSER_ARTIFACT_DIR": artifact_dir.rstrip("/"),
    }


def _load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _slug(value):
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "unspecified"


def _timestamp(value):
    if value:
        if not re.fullmatch(r"\d{8}-\d{6}", value):
            raise ValueError("--timestamp must match YYYYMMDD-HHMMSS")
        return value
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")


def calculate_run(config, args):
    run_id = getattr(args, "run_id", None)
    if run_id:
        if not re.fullmatch(r"\d{8}-\d{6}-[a-z0-9][a-z0-9-]*-[a-z0-9][a-z0-9-]*", run_id):
            raise ValueError("--run-id must match YYYYMMDD-HHMMSS-<scope-slug>-<role-slug>")
    else:
        run_id = f"{_timestamp(getattr(args, 'timestamp', None))}-{_slug(args.scope)}-{_slug(args.role)}"
    artifact_root = config["artifactRoot"]
    if not artifact_root.endswith("/"):
        artifact_root += "/"
    return {
        "runId": run_id,
        "artifactRoot": artifact_root,
        "artifactDir": f"{artifact_root}{run_id}/",
        "createsArtifacts": False,
        "pathStatus": "calculated-only"
    }


def _utc_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_git_status(path):
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--short"],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "exitCode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr.strip(),
    }


def _probe_http(url, timeout=2):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read(2048).decode("utf-8", errors="replace")
        return {
            "url": url,
            "reachable": True,
            "statusCode": response.status,
            "bodyPreview": body[:500],
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "url": url,
            "reachable": False,
            "error": str(exc),
        }


def _probe_cdp(url, timeout=2):
    return _probe_http(url, timeout=timeout)


def _wait_http(url, timeout_seconds, interval_seconds=0.5):
    deadline = time.monotonic() + max(0.0, timeout_seconds)
    attempts = 0
    last_probe = None
    while True:
        attempts += 1
        last_probe = _probe_http(url, timeout=min(2, max(0.2, interval_seconds)))
        if last_probe.get("reachable"):
            return True, attempts, last_probe
        if time.monotonic() >= deadline:
            return False, attempts, last_probe
        time.sleep(max(0.1, interval_seconds))


def _setup_defaults(config):
    setup = config.get("browserSetup", {})
    return {
        "defaultDebuggingPort": int(setup.get("defaultDebuggingPort", 9222)),
        "defaultCdpUrl": setup.get("defaultCdpUrl", "http://127.0.0.1:9222/json/version"),
        "profileRoot": setup.get("profileRoot", ".planning/tmp/browser-harness/chrome-profiles/"),
        "launchFlags": setup.get("launchFlags", []),
        "userOnlyPrerequisites": setup.get("userOnlyPrerequisites", []),
        "agentRunnableSteps": setup.get("agentRunnableSteps", []),
    }


def _find_chrome(explicit_path=""):
    candidates = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    for name in ("chrome.exe", "chrome", "google-chrome", "chromium", "chromium-browser"):
        resolved = shutil.which(name)
        if resolved:
            candidates.append(Path(resolved))
    if sys.platform.startswith("win"):
        local = os.environ.get("LOCALAPPDATA", "")
        program_files = [os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", "")]
        candidates.extend(
            Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe"
            for base in [local, *program_files]
            if base
        )
    elif sys.platform == "darwin":
        candidates.append(Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
    else:
        candidates.extend([Path("/usr/bin/google-chrome"), Path("/usr/bin/chromium"), Path("/snap/bin/chromium")])

    seen = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists():
            return str(candidate)
    return ""


def _cdp_url_from_port(port):
    return f"http://127.0.0.1:{int(port)}/json/version"


def _launch_chrome(config, args):
    setup = _setup_defaults(config)
    port = int(args.port or setup["defaultDebuggingPort"])
    cdp_url = args.cdp_url or _cdp_url_from_port(port)
    if not args.force:
        existing = _probe_cdp(cdp_url)
        if existing.get("reachable"):
            return {
                "status": "already-running",
                "exitCode": EXIT_PASS,
                "cdpUrl": cdp_url,
                "probe": existing,
                "processStarted": False,
            }

    chrome_path = _find_chrome(args.chrome_path)
    if not chrome_path:
        return {
            "status": "blocked",
            "exitCode": EXIT_CONFIG,
            "cdpUrl": cdp_url,
            "processStarted": False,
            "blocker": "Chrome executable was not found. User must install Chrome or pass --chrome-path.",
        }

    profile_root = Path(args.profile_dir or (ROOT / setup["profileRoot"] / f"port-{port}"))
    if not profile_root.is_absolute():
        profile_root = ROOT / profile_root
    profile_root.mkdir(parents=True, exist_ok=True)

    flags = []
    configured_flags = setup["launchFlags"] or [
        "--remote-debugging-port={port}",
        "--user-data-dir={profileDir}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    for flag in configured_flags:
        flags.append(flag.format(port=port, profileDir=str(profile_root)))
    if args.headless:
        flags.append("--headless=new")
    if args.open_url:
        flags.append(args.open_url)
    else:
        flags.append("about:blank")

    creationflags = 0
    if sys.platform.startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    process = subprocess.Popen([chrome_path, *flags], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
    ready, attempts, probe = _wait_http(cdp_url, args.timeout_seconds, args.interval_seconds)
    return {
        "status": "passed" if ready else "blocked",
        "exitCode": EXIT_PASS if ready else EXIT_ENGINE,
        "cdpUrl": cdp_url,
        "chromePath": chrome_path,
        "profileDir": str(profile_root),
        "pid": process.pid,
        "processStarted": True,
        "waitAttempts": attempts,
        "probe": probe,
    }


def _read_project_name(project_path):
    package_json = project_path / "package.json"
    if not package_json.exists():
        return project_path.name
    try:
        return json.loads(package_json.read_text(encoding="utf-8")).get("name") or project_path.name
    except (json.JSONDecodeError, OSError):
        return project_path.name


def _ensure_run_layout(run_dir):
    run_dir.mkdir(parents=True, exist_ok=False)
    for name in ("screenshots", "page-states", "dom-snapshots"):
        (run_dir / name).mkdir()


def _write_blocked_run(mode, config, args, cause, details, exit_code=EXIT_PARTIAL_BLOCKED):
    run_info = calculate_run(config, args)
    run_id = run_info["runId"]
    run_dir = ROOT / run_info["artifactDir"]
    started_at = _utc_iso()
    _ensure_run_layout(run_dir)
    tab_lifecycle = _tab_lifecycle_baseline(config, args, run_id, details.get("tabBlocker") if isinstance(details, dict) else None)

    # Run-scoped environment isolation: created here for the wrapper foundation so
    # later real-capture phases can hand these to the engine.
    run_env = _run_scoped_env(run_id, run_info["artifactDir"])

    # Resolve/audit the engine for the foundation summary (no browser start).
    engine_audit = BrowserHarnessAdapter(ROOT, config).audit()

    project_path = Path(args.project_path).resolve()
    validation_status_before = _run_git_status(project_path)
    validation_status_after = _run_git_status(project_path)
    finished_at = _utc_iso()

    autonomy_mode = args.autonomy
    autonomy_config = config["autonomy"][autonomy_mode]
    failure = {
        "type": "environment-blocker",
        "cause": cause,
        "details": details,
    }
    lifecycle = {
        "browserHarnessInvoked": False,
        "browserHarnessUpdateInvoked": False,
        "browserHarnessReloadInvoked": False,
        "stdinExecutionInvoked": False,
        "ownedProcessesStarted": [],
        "ownedProcessesStopped": True,
        "unknownProcessesStopped": False,
        "ownedProcessMarker": config["lifecycle"]["ownedProcessMarker"],
    }
    validation_target = {
        "target": {
            "path": str(project_path),
            "mutationPolicy": "read-only",
            "inspectedFiles": [
                "PROJECT.md",
                "package.json",
                ".planning/STATE.md",
                ".planning/CONTEXT_INDEX.md",
                ".planning/CODEBASE_MAP.md",
            ],
            "gitStatusBefore": validation_status_before["stdout"],
            "gitStatusAfter": validation_status_after["stdout"],
            "gitStatusExitCodeBefore": validation_status_before["exitCode"],
            "gitStatusExitCodeAfter": validation_status_after["exitCode"],
        }
    }
    summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": mode,
        "status": "blocked",
        "exitCode": exit_code,
        # Whole-run confidence: no real browser evidence was captured, so the run is
        # never Confirmed (evidence-status-and-reference-contract).
        "evidence_status": "Unknown",
        "projectName": _read_project_name(project_path),
        "baseUrl": args.base_url or "",
        "target": getattr(args, "target", None) or "",
        "browserHarness": {
            "strategy": engine_audit.get("strategy"),
            "available": engine_audit.get("available"),
            "version": engine_audit.get("version"),
            "commit": engine_audit.get("commit"),
            "source": engine_audit.get("source"),
            "evidence_status": engine_audit.get("evidence_status"),
        },
        "runScopedEnv": run_env,
        "scope": {
            "type": "project",
            "value": args.scope,
        },
        "role": args.role,
        "autonomy": {
            "mode": autonomy_mode,
            "blockedActionCategories": autonomy_config["blockedActionCategories"],
            "unrestricted": autonomy_config["unrestricted"],
        },
        "browser": {
            "name": "",
            "version": "",
            "cdpUrl": args.cdp_url,
            "profileMode": "dedicated",
        },
        "tabLifecycle": tab_lifecycle,
        "app": {
            "commandsRun": [],
            "healthChecks": [details.get("cdpProbe", {})],
            "ownedProcessesStopped": True,
        },
        "artifacts": {
            "actionLog": "action-log.json",
            "network": "network.json",
            "console": "console.log",
            "screenshots": [],
            "pageStates": [],
            "domSnapshots": [],
        },
        "safety": {
            "blockedActions": [
                {
                    "category": "browser-runtime-startup",
                    "reason": cause,
                    "evidence_status": "Confirmed",
                }
            ],
            "dangerousActionsAllowed": [],
        },
        "failure": failure,
        "timings": {
            "startedAt": started_at,
            "finishedAt": finished_at,
            "durationMs": 0,
        },
    }
    environment = {
        "schemaVersion": 1,
        "runId": run_id,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "cwd": str(ROOT),
        "pid": os.getpid(),
        "browserHarness": {
            "vendorPath": config["vendor"]["browserHarnessPath"],
            "invoked": False,
            "engineAudit": engine_audit,
            "runScopedEnv": run_env,
            "deviationJustification": "Wrapper-only blocker; vendored internals were not modified or invoked because safe browser/app prerequisites were absent.",
        },
        "lifecycle": lifecycle,
        "validationTarget": validation_target,
        "sourceTraceability": config["sourceTraceability"],
        "confirmedSuggestedUnknown": {
            "Confirmed": [
                "Browser Runtime artifacts remain repo-local.",
                "Confirmed/Suggested/Unknown evidence labels are preserved.",
            ],
            "Suggested": config["remainingForLaterPhases"]["Suggested"],
            "Unknown": [
                "Real Browser Harness capture remains unknown until a reachable base URL and safe CDP/app lifecycle are provided.",
            ],
        },
    }
    safety_events = {
        "schemaVersion": 1,
        "runId": run_id,
        "events": [
            {
                "eventId": "SAFETY-001",
                "timestamp": finished_at,
                "category": "runtime-blocker",
                "action": "browser evidence capture",
                "decision": "blocked",
                "reason": cause,
                "evidence_status": "Confirmed",
            }
        ],
    }
    blocker = {
        "schemaVersion": 1,
        "runId": run_id,
        "status": "blocked",
        "cause": cause,
        "details": details,
        "rawEvidenceFinalized": False,
        "unrelatedMutation": False,
        "browserHarnessUpdateInvoked": False,
        "browserHarnessReloadInvoked": False,
        "stdinExecutionInvoked": False,
    }

    # Unavailable evidence channels are written as Unknown markers, never omitted
    # (evidence-redaction-safety-contract.md).
    network_payload = {
        "schemaVersion": 1,
        "runId": run_id,
        "available": False,
        "reason": cause,
        "evidence_status": "Unknown",
        "entries": [],
        "redacted": True,
    }
    storage_payload = {
        "schemaVersion": 1,
        "runId": run_id,
        "available": False,
        "reason": cause,
        "evidence_status": "Unknown",
        "storageCaptured": False,
    }

    # Centralized redaction is applied to every artifact before it is finalized,
    # even on the blocked/no-browser path and in unrestricted mode.
    redaction_counts = {}
    artifacts_to_write = {
        "summary.json": redact_payload(summary, redaction_counts),
        "environment.json": redact_payload(environment, redaction_counts),
        "action-log.json": redact_payload([{
            "step": 1,
            "action": "tab-policy-check",
            "target": getattr(args, "base_url", "") or "",
            "result": "blocked" if tab_lifecycle.get("blockedNewTabAttempts") else "not-run",
            "tabDecision": _tab_decision(tab_lifecycle),
            "evidence_status": "Confirmed",
            "timestamp": finished_at,
        }] if tab_lifecycle.get("blockedNewTabAttempts") else [], redaction_counts),
        "network.json": redact_payload(network_payload, redaction_counts),
        "storage-summary.json": redact_payload(storage_payload, redaction_counts),
        "autonomy-policy.json": redact_payload(summary["autonomy"], redaction_counts),
        "safety-events.json": redact_payload(safety_events, redaction_counts),
        "blocker-details.json": redact_payload(blocker, redaction_counts),
    }
    console_text, console_counts = redact_text("")
    for key, num in console_counts.items():
        redaction_counts[key] = redaction_counts.get(key, 0) + num

    redactions_applied = sum(redaction_counts.values())
    redaction_summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "redactionReplacement": REDACTION_REPLACEMENT,
        "redactionsApplied": redactions_applied,
        "countsByPattern": redaction_counts,
        "filesProcessed": sorted(artifacts_to_write.keys()) + ["console.log"],
        "manualReviewRequired": redactions_applied > 0,
        "rawEvidenceFinalized": False,
        "vaultPublication": "not-published",
        "evidence_status": "Unknown",
        "notes": "No raw browser evidence, screenshots, DOM snapshots, network payloads, cookies, or storage values were finalized because the run blocked before Browser Harness capture; centralized redaction ran over all written artifacts.",
    }

    for filename, payload in artifacts_to_write.items():
        _write_json(run_dir / filename, payload)
    (run_dir / "console.log").write_text(console_text, encoding="utf-8")
    (run_dir / "app-process.log").write_text("No app process was started; no owned processes required shutdown.\n", encoding="utf-8")
    _write_json(run_dir / "redaction-summary.json", redaction_summary)

    payload = {
        "mode": mode,
        "status": "blocked",
        "runId": run_id,
        "artifactDir": run_info["artifactDir"],
        "summary": run_info["artifactDir"] + "summary.json",
        "failure": failure,
        "browserHarnessInvoked": False,
        "browserHarnessUpdateInvoked": False,
        "browserHarnessReloadInvoked": False,
        "stdinExecutionInvoked": False,
        "createsArtifacts": True,
        "exitCode": exit_code,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


def _channel_unknown(run_id, reason, extra=None):
    """Standard unavailable-channel marker."""
    payload = {
        "schemaVersion": 1,
        "runId": run_id,
        "available": False,
        "reason": reason,
        "evidence_status": "Unknown",
    }
    if extra:
        payload.update(extra)
    return payload


def _write_capture_run(mode, config, args, cdp_probe):
    """Real evidence-capture path.

    Resolves the engine, drives a bounded run-scoped capture via subprocess +
    heredoc (confirmed helper names), populates the existing full artifact set
    with really-captured channels, writes Unknown markers for channels the engine
    did not expose, applies centralized redaction before finalizing every
    artifact (including network/console/DOM/storage text), and labels the run
    honestly: passed only when load + required capture genuinely succeeded,
    partial when optional channels are missing, blocked when capture failed.
    Never fakes Confirmed evidence.
    """
    run_info = calculate_run(config, args)
    run_id = run_info["runId"]
    run_dir = ROOT / run_info["artifactDir"]
    started_at = _utc_iso()
    _ensure_run_layout(run_dir)

    run_env = _run_scoped_env(run_id, run_info["artifactDir"])
    adapter = BrowserHarnessAdapter(ROOT, config, env={**os.environ, **run_env})
    engine_audit = adapter.audit()

    # Resolve the capture target. --target page:<path> combines with --base-url;
    # url:<url> is absolute; bare value falls back to base-url.
    target_arg = (getattr(args, "target", "") or "").strip()
    base_url = (args.base_url or "").rstrip("/")
    if target_arg.startswith("url:"):
        target_url = target_arg[len("url:"):]
    elif target_arg.startswith("page:"):
        path = target_arg[len("page:"):]
        if not path.startswith("/"):
            path = "/" + path
        target_url = base_url + path
    elif target_arg:
        target_url = target_arg
    else:
        target_url = base_url or args.base_url

    screenshot_rel = "screenshots/capture.png"
    screenshot_abs = str((run_dir / screenshot_rel).resolve())

    wait_timeout = float(config["browserHarness"].get("timeoutSeconds", 30)) * 0.5
    capture = adapter.capture(
        target_url,
        run_env,
        screenshot_abs,
        wait_timeout=wait_timeout,
        goal_id=_goal_id_for_run(args, run_id),
        cdp_url=args.cdp_url,
        tab_policy=args.tab_policy,
        new_tab_reason=args.new_tab_reason,
    )
    finished_at = _utc_iso()

    result = capture.get("result") or {}
    tab_lifecycle = _merge_tab_lifecycle(config, args, run_id, capture.get("tabLifecycle") or result.get("tabLifecycle"))
    channels = result.get("channels", {})
    captured_ok = capture.get("ok")
    autonomy_mode = args.autonomy
    autonomy_config = config["autonomy"][autonomy_mode]

    # ---- action log (records the real navigation + its result) -------------
    nav_result = "load-complete" if result.get("loaded") else "load-incomplete-or-failed"
    action_log = [
        {
            "step": 1,
            "action": "navigate",
            "target": target_url,
            "result": nav_result if capture.get("exitCode") is not None else "engine-not-invoked",
            "ownedTab": result.get("ownedTab"),
            "tabDecision": _tab_decision(tab_lifecycle),
            "evidence_status": "Confirmed" if result.get("loaded") else "Unknown",
            "timestamp": finished_at,
        }
    ]

    # ---- per-channel population (real or Unknown marker) --------------------
    page_info = channels.get("pageInfo")
    page_states_written = []
    if isinstance(page_info, dict) and page_info:
        page_state = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "pageInfo": page_info,
            "currentTab": result.get("currentTab"),
        }
        page_states_written.append("page-states/page-state-001.json")
    else:
        page_state = _channel_unknown(run_id, capture.get("note", "page info was not captured"))

    dom_snapshot = channels.get("domSnapshot")
    dom_written = []
    dom_payload = None
    if isinstance(dom_snapshot, str) and dom_snapshot:
        dom_payload = dom_snapshot
        dom_written.append("dom-snapshots/dom-001.html")

    screenshot_present = bool(channels.get("screenshotPath")) and (run_dir / screenshot_rel).exists()

    network_events = channels.get("network")
    if isinstance(network_events, list):
        network_payload = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "entries": network_events,
            "redacted": True,
            "captureCaveat": "Daemon event buffer is global (maxlen 500) and shared across tabs; entries were drained around the navigation window but per-session filtering was unavailable, so unrelated-tab traffic may appear and high-volume traffic may be capped.",
        }
    else:
        network_payload = _channel_unknown(run_id, "engine did not expose network events", {"entries": [], "redacted": True})

    console_events = channels.get("console")
    console_lines = []
    console_available = isinstance(console_events, list)
    if console_available:
        for ev in console_events:
            console_lines.append(json.dumps(ev, sort_keys=True))

    storage = channels.get("storage")
    if isinstance(storage, dict):
        storage_payload = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "storageCaptured": True,
            "localStorage": storage.get("local", {}),
            "sessionStorage": storage.get("session", {}),
        }
    else:
        storage_payload = _channel_unknown(run_id, "engine did not expose storage", {"storageCaptured": False})

    # ---- whole-run status (honest) -----------------------------------------
    optional_missing = []
    if not screenshot_present:
        optional_missing.append("screenshots")
    if network_payload.get("available") is not True:
        optional_missing.append("network")
    if not console_available:
        optional_missing.append("console")
    if storage_payload.get("available") is not True:
        optional_missing.append("storage")
    if not dom_written:
        optional_missing.append("dom-snapshots")

    if captured_ok and result.get("loaded"):
        status = "partial" if optional_missing else "passed"
        exit_code = EXIT_PASS if status == "passed" else EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Confirmed"
        failure = None
    else:
        status = "blocked"
        exit_code = EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Unknown"
        failure = {
            "type": "capture-incomplete",
            "cause": capture.get("note", "engine capture did not complete"),
            "details": {
                "exitCode": capture.get("exitCode"),
                "stderr": capture.get("stderr", ""),
                "engineErrors": result.get("errors", []),
            },
        }

    project_path = Path(args.project_path).resolve()
    summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": mode,
        "status": status,
        "exitCode": exit_code,
        "evidence_status": run_evidence_status,
        "projectName": _read_project_name(project_path),
        "baseUrl": args.base_url or "",
        "target": target_arg,
        "targetUrl": target_url,
        "browserHarness": {
            "strategy": engine_audit.get("strategy"),
            "available": engine_audit.get("available"),
            "invoked": capture.get("exitCode") is not None,
            "version": engine_audit.get("version"),
            "commit": engine_audit.get("commit"),
            "source": engine_audit.get("source"),
            "captureNote": capture.get("note"),
            "captureExitCode": capture.get("exitCode"),
            "evidence_status": engine_audit.get("evidence_status"),
        },
        "runScopedEnv": run_env,
        "scope": {"type": "project", "value": args.scope},
        "role": args.role,
        "autonomy": {
            "mode": autonomy_mode,
            "blockedActionCategories": autonomy_config["blockedActionCategories"],
            "unrestricted": autonomy_config["unrestricted"],
        },
        "browser": {
            "name": "",
            "version": "",
            "cdpUrl": args.cdp_url,
            "profileMode": "dedicated",
        },
        "tabLifecycle": tab_lifecycle,
        "app": {
            "commandsRun": [],
            "healthChecks": [cdp_probe],
            "ownedProcessesStopped": True,
        },
        "channelsCaptured": sorted(
            name for name, present in (
                ("page-state", isinstance(page_info, dict) and bool(page_info)),
                ("screenshots", screenshot_present),
                ("network", network_payload.get("available") is True),
                ("console", console_available),
                ("storage", storage_payload.get("available") is True),
                ("dom-snapshots", bool(dom_written)),
            ) if present
        ),
        "channelsUnknown": sorted(optional_missing),
        "artifacts": {
            "actionLog": "action-log.json",
            "network": "network.json",
            "console": "console.log",
            "screenshots": [screenshot_rel] if screenshot_present else [],
            "pageStates": page_states_written,
            "domSnapshots": dom_written,
        },
        "safety": {
            "blockedActions": [],
            "dangerousActionsAllowed": [],
            "redactionActive": True,
            "safetyEventsActive": True,
        },
        "failure": failure,
        "timings": {
            "startedAt": started_at,
            "finishedAt": finished_at,
            "durationMs": 0,
        },
    }

    lifecycle = {
        "browserHarnessInvoked": capture.get("exitCode") is not None,
        "browserHarnessUpdateInvoked": False,
        "browserHarnessReloadInvoked": False,
        "stdinExecutionInvoked": capture.get("exitCode") is not None,
        "ownedProcessesStarted": ["run-scoped browser-harness daemon"] if capture.get("exitCode") is not None else [],
        "ownedProcessesStopped": bool(result.get("daemonStopped", False)) or capture.get("exitCode") is None,
        "unknownProcessesStopped": False,
        "ownedProcessMarker": config["lifecycle"]["ownedProcessMarker"],
        "daemonStopped": result.get("daemonStopped"),
    }
    environment = {
        "schemaVersion": 1,
        "runId": run_id,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "cwd": str(ROOT),
        "pid": os.getpid(),
        "browserHarness": {
            "vendorPath": config["vendor"]["browserHarnessPath"],
            "invoked": capture.get("exitCode") is not None,
            "engineAudit": engine_audit,
            "runScopedEnv": run_env,
            "captureCommand": capture.get("command"),
            "captureNote": capture.get("note"),
            "helperApisUsed": [
                "ensure_real_tab", "current_tab", "list_tabs", "goto_url", "wait_for_load", "page_info",
                "current_tab", "capture_screenshot", "js", "drain_events",
                "close_tab", "restart_daemon", "new_tab gated by explicit tab policy only",
            ],
        },
        "lifecycle": lifecycle,
        "tabLifecycle": tab_lifecycle,
        "sourceTraceability": config["sourceTraceability"],
        "confirmedSuggestedUnknown": {
            "Confirmed": [
                "Browser Runtime artifacts remain repo-local.",
                "Confirmed/Suggested/Unknown evidence labels are preserved.",
                "Engine identity (version/commit) was inspected.",
            ],
            "Suggested": config["remainingForLaterPhases"]["Suggested"],
            "Unknown": [
                "Screenshot pixels cannot be programmatically redacted; secrets visible on-screen may persist in the PNG (filenames/metadata only are managed).",
                "Network/console events are drained from a global shared buffer without per-session filtering, so cross-tab leakage and 500-event capping are possible.",
            ],
        },
    }
    safety_events = {
        "schemaVersion": 1,
        "runId": run_id,
        "events": [
            {
                "eventId": "SAFETY-001",
                "timestamp": finished_at,
                "category": "browser-capture",
                "action": "open target and capture evidence",
                "decision": "allowed" if captured_ok else "completed-with-incomplete-capture",
                "reason": "real capture explicitly enabled via --allow-browser-harness with safe prerequisites present",
                "autonomyMode": autonomy_mode,
                "evidence_status": "Confirmed",
            }
        ],
    }

    # ---- centralized redaction over every captured artifact ----------------
    redaction_counts = {}
    artifacts_to_write = {
        "summary.json": redact_payload(summary, redaction_counts),
        "environment.json": redact_payload(environment, redaction_counts),
        "action-log.json": redact_payload(action_log, redaction_counts),
        "network.json": redact_payload(network_payload, redaction_counts),
        "storage-summary.json": redact_payload(storage_payload, redaction_counts),
        "autonomy-policy.json": redact_payload(summary["autonomy"], redaction_counts),
        "safety-events.json": redact_payload(safety_events, redaction_counts),
    }
    if page_states_written:
        artifacts_to_write["page-states/page-state-001.json"] = redact_payload(page_state, redaction_counts)
    else:
        artifacts_to_write["page-states/page-state-unavailable.json"] = redact_payload(page_state, redaction_counts)

    console_joined = "\n".join(console_lines)
    console_text, console_counts = redact_text(console_joined)
    for key, num in console_counts.items():
        redaction_counts[key] = redaction_counts.get(key, 0) + num

    dom_text = None
    if dom_payload is not None:
        dom_text, dom_counts = redact_text(dom_payload)
        for key, num in dom_counts.items():
            redaction_counts[key] = redaction_counts.get(key, 0) + num

    redactions_applied = sum(redaction_counts.values())
    files_processed = sorted(artifacts_to_write.keys()) + ["console.log"]
    if dom_written:
        files_processed.append("dom-snapshots/dom-001.html")
    redaction_summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "redactionReplacement": REDACTION_REPLACEMENT,
        "redactionsApplied": redactions_applied,
        "countsByPattern": redaction_counts,
        "filesProcessed": files_processed,
        "manualReviewRequired": redactions_applied > 0,
        "rawEvidenceFinalized": False,
        "vaultPublication": "not-published",
        "evidence_status": "Confirmed",
        "screenshotPixelCaveat": "Screenshot PNG pixels are not text-redactable; review screenshots/ before any external publication.",
        "notes": "Centralized redaction ran over all captured text artifacts (summary/environment/action-log/network/console/storage/DOM/page-state) before finalization, including in unrestricted mode.",
    }

    for filename, payload in artifacts_to_write.items():
        _write_json(run_dir / filename, payload)
    (run_dir / "console.log").write_text(console_text, encoding="utf-8")
    if dom_text is not None:
        (run_dir / "dom-snapshots" / "dom-001.html").write_text(dom_text, encoding="utf-8")
    (run_dir / "app-process.log").write_text(
        "No app server was started by the wrapper; the run-scoped Browser Harness daemon was started and stopped by the capture script.\n",
        encoding="utf-8",
    )
    _write_json(run_dir / "redaction-summary.json", redaction_summary)

    # ---- clean up the run-scoped tmp/runtime dirs (C5) ----------------------
    try:
        import shutil as _shutil

        _shutil.rmtree(ROOT / ".planning" / "tmp" / "browser-harness" / run_id, ignore_errors=True)
    except OSError:
        pass

    payload = {
        "mode": mode,
        "status": status,
        "runId": run_id,
        "artifactDir": run_info["artifactDir"],
        "summary": run_info["artifactDir"] + "summary.json",
        "evidence_status": run_evidence_status,
        "browserHarnessInvoked": capture.get("exitCode") is not None,
        "channelsCaptured": summary["channelsCaptured"],
        "channelsUnknown": summary["channelsUnknown"],
        "createsArtifacts": True,
        "exitCode": exit_code,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


def _finalize_run(run_dir, run_id, summary, environment, action_log, safety_events,
                  network_payload, storage_payload, page_state, page_states_written,
                  dom_payload, dom_written, console_lines, extra_artifacts=None,
                  redaction_evidence_status="Confirmed"):
    """Redact and write the full artifact set for replay/qa/smoke.

    Reuses the centralized redaction + artifact-writing pattern from
    `_write_capture_run` so replay/qa/smoke do not re-author redaction/artifact
    writing. Centralized redaction runs over every text artifact before
    finalization, including in unrestricted mode.
    `extra_artifacts` is an optional dict of {relative_path: json_payload}
    (e.g. qa-findings.json) that is redacted and written alongside the set.
    """
    redaction_counts = {}
    artifacts_to_write = {
        "summary.json": redact_payload(summary, redaction_counts),
        "environment.json": redact_payload(environment, redaction_counts),
        "action-log.json": redact_payload(action_log, redaction_counts),
        "network.json": redact_payload(network_payload, redaction_counts),
        "storage-summary.json": redact_payload(storage_payload, redaction_counts),
        "autonomy-policy.json": redact_payload(summary["autonomy"], redaction_counts),
        "safety-events.json": redact_payload(safety_events, redaction_counts),
    }
    if page_states_written:
        artifacts_to_write["page-states/page-state-001.json"] = redact_payload(page_state, redaction_counts)
    else:
        artifacts_to_write["page-states/page-state-unavailable.json"] = redact_payload(page_state, redaction_counts)
    for rel, payload in (extra_artifacts or {}).items():
        artifacts_to_write[rel] = redact_payload(payload, redaction_counts)

    console_joined = "\n".join(console_lines)
    console_text, console_counts = redact_text(console_joined)
    for key, num in console_counts.items():
        redaction_counts[key] = redaction_counts.get(key, 0) + num

    dom_text = None
    if dom_payload is not None:
        dom_text, dom_counts = redact_text(dom_payload)
        for key, num in dom_counts.items():
            redaction_counts[key] = redaction_counts.get(key, 0) + num

    redactions_applied = sum(redaction_counts.values())
    files_processed = sorted(artifacts_to_write.keys()) + ["console.log"]
    if dom_written:
        files_processed.append("dom-snapshots/dom-001.html")
    redaction_summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "redactionReplacement": REDACTION_REPLACEMENT,
        "redactionsApplied": redactions_applied,
        "countsByPattern": redaction_counts,
        "filesProcessed": files_processed,
        "manualReviewRequired": redactions_applied > 0,
        "rawEvidenceFinalized": False,
        "vaultPublication": "not-published",
        "evidence_status": redaction_evidence_status,
        "screenshotPixelCaveat": "Screenshot PNG pixels are not text-redactable; review screenshots/ before any external publication.",
        "notes": "Centralized redaction ran over all captured text artifacts before finalization, including in unrestricted mode.",
    }

    for filename, payload in artifacts_to_write.items():
        _write_json(run_dir / filename, payload)
    (run_dir / "console.log").write_text(console_text, encoding="utf-8")
    if dom_text is not None:
        (run_dir / "dom-snapshots" / "dom-001.html").write_text(dom_text, encoding="utf-8")
    (run_dir / "app-process.log").write_text(
        "No app server was started by the wrapper; the run-scoped Browser Harness daemon was started and stopped by the engine script.\n",
        encoding="utf-8",
    )
    _write_json(run_dir / "redaction-summary.json", redaction_summary)


def _cleanup_run_scoped(run_id):
    try:
        import shutil as _shutil

        _shutil.rmtree(ROOT / ".planning" / "tmp" / "browser-harness" / run_id, ignore_errors=True)
    except OSError:
        pass


def _channels_from_result(run_id, result, run_dir):
    """Common channel population for replay/qa from an engine result dict.

    Returns (network_payload, storage_payload, page_state, page_states_written,
    dom_payload, dom_written, console_lines, console_available, optional_missing).
    """
    channels = (result or {}).get("channels", {})

    page_info = channels.get("pageInfo")
    page_states_written = []
    if isinstance(page_info, dict) and page_info:
        page_state = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "pageInfo": page_info,
        }
        page_states_written.append("page-states/page-state-001.json")
    else:
        page_state = _channel_unknown(run_id, "page info was not captured")

    dom_snapshot = channels.get("domSnapshot")
    dom_written = []
    dom_payload = None
    if isinstance(dom_snapshot, str) and dom_snapshot:
        dom_payload = dom_snapshot
        dom_written.append("dom-snapshots/dom-001.html")

    network_events = channels.get("network")
    if isinstance(network_events, list):
        network_payload = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "entries": network_events,
            "redacted": True,
            "captureCaveat": "Daemon event buffer is global (maxlen 500) and shared across tabs; per-session filtering was unavailable.",
        }
    else:
        network_payload = _channel_unknown(run_id, "engine did not expose network events", {"entries": [], "redacted": True})

    console_events = channels.get("console")
    console_lines = []
    console_available = isinstance(console_events, list)
    if console_available:
        for ev in console_events:
            console_lines.append(json.dumps(ev, sort_keys=True))

    storage = channels.get("storage")
    if isinstance(storage, dict):
        storage_payload = {
            "schemaVersion": 1,
            "runId": run_id,
            "available": True,
            "evidence_status": "Confirmed",
            "storageCaptured": True,
            "localStorage": storage.get("local", {}),
            "sessionStorage": storage.get("session", {}),
        }
    else:
        storage_payload = _channel_unknown(run_id, "engine did not expose storage", {"storageCaptured": False})

    optional_missing = []
    if network_payload.get("available") is not True:
        optional_missing.append("network")
    if not console_available:
        optional_missing.append("console")
    if storage_payload.get("available") is not True:
        optional_missing.append("storage")
    if not dom_written:
        optional_missing.append("dom-snapshots")

    return (network_payload, storage_payload, page_state, page_states_written,
            dom_payload, dom_written, console_lines, console_available, optional_missing)


def _base_environment(run_id, run_env, engine_audit, config, invoked, captureCommand=None,
                      captureNote=None, extra_unknown=None):
    env = {
        "schemaVersion": 1,
        "runId": run_id,
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "cwd": str(ROOT),
        "pid": os.getpid(),
        "browserHarness": {
            "vendorPath": config["vendor"]["browserHarnessPath"],
            "invoked": invoked,
            "engineAudit": engine_audit,
            "runScopedEnv": run_env,
            "captureCommand": captureCommand,
            "captureNote": captureNote,
        },
        "sourceTraceability": config["sourceTraceability"],
        "confirmedSuggestedUnknown": {
            "Confirmed": [
                "Browser Runtime artifacts remain repo-local.",
                "Confirmed/Suggested/Unknown evidence labels are preserved.",
            ],
            "Suggested": config["remainingForLaterPhases"]["Suggested"],
            "Unknown": [
                "Screenshot pixels cannot be programmatically redacted; secrets visible on-screen may persist in the PNG.",
                "Network/console events are drained from a global shared buffer without per-session filtering.",
            ] + (extra_unknown or []),
        },
    }
    return env


def _autonomy_block(config, autonomy_mode):
    cfg = config["autonomy"][autonomy_mode]
    return {
        "mode": autonomy_mode,
        "blockedActionCategories": cfg["blockedActionCategories"],
        "unrestricted": cfg["unrestricted"],
    }


def _resolve_target_url(target_arg, base_url):
    target_arg = (target_arg or "").strip()
    base_url = (base_url or "").rstrip("/")
    if target_arg.startswith("url:"):
        return target_arg[len("url:"):]
    if target_arg.startswith("page:"):
        path = target_arg[len("page:"):]
        if not path.startswith("/"):
            path = "/" + path
        return base_url + path
    if target_arg.startswith("flow:"):
        return base_url or target_arg
    if target_arg:
        return target_arg
    return base_url


def _write_replay_run(mode, config, args, cdp_probe):
    """Replay mode: consume replay.plan.json and drive ordered MVP actions.

    ALWAYS creates a new run dir (never overwrites), records one action-log entry
    per plan step preserving each step's evidence_status (downgrade-only), and
    marks unsupported/failed actions failed/partial/unsupported -- never Confirmed.
    """
    plan_path = Path(args.replay_plan)
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"replay plan could not be loaded: {exc}", file=sys.stderr)
        return EXIT_REPLAY_CONTRACT

    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        print("replay plan is malformed: missing non-empty steps[]", file=sys.stderr)
        return EXIT_REPLAY_CONTRACT
    plan_base_url = plan.get("base_url") or args.base_url or ""

    run_info = calculate_run(config, args)
    run_id = run_info["runId"]
    run_dir = ROOT / run_info["artifactDir"]
    started_at = _utc_iso()
    _ensure_run_layout(run_dir)

    run_env = _run_scoped_env(run_id, run_info["artifactDir"])
    adapter = BrowserHarnessAdapter(ROOT, config, env={**os.environ, **run_env})
    engine_audit = adapter.audit()

    screenshot_dir = str((run_dir / "screenshots").resolve())
    replay = adapter.replay(
        plan_base_url,
        steps,
        screenshot_dir,
        goal_id=_goal_id_for_run(args, run_id),
        cdp_url=args.cdp_url,
        tab_policy=args.tab_policy,
        new_tab_reason=args.new_tab_reason,
    )
    finished_at = _utc_iso()
    result = replay.get("result") or {}
    tab_lifecycle = _merge_tab_lifecycle(config, args, run_id, replay.get("tabLifecycle") or result.get("tabLifecycle"))
    invoked = replay.get("exitCode") is not None
    engine_steps = {s.get("stepId"): s for s in result.get("steps", []) if isinstance(s, dict)}

    # ---- per-step action log: preserve plan evidence_status (downgrade-only) --
    OUTCOME_DOWNGRADE = {"failed", "partial", "unsupported"}
    action_log = []
    any_unsupported_or_failed = False
    any_step_failed = False
    for idx, step in enumerate(steps):
        sid = step.get("step_id") or f"step-{idx + 1}"
        plan_status = step.get("evidence_status", "Suggested")
        if plan_status not in ("Confirmed", "Suggested", "Unknown"):
            plan_status = "Suggested"
        engine_step = engine_steps.get(sid, {})
        if invoked and engine_step:
            outcome = engine_step.get("outcome", "failed")
            detail = engine_step.get("detail", "")
        elif not invoked:
            outcome = "unsupported"
            detail = replay.get("note", "engine not invoked")
        else:
            outcome = "failed"
            detail = "engine returned no result for this step"
        # Downgrade-only: never upgrade the plan's evidence_status on success.
        if outcome in OUTCOME_DOWNGRADE:
            step_evidence = "Unknown"
            any_unsupported_or_failed = True
            if outcome in ("failed",):
                any_step_failed = True
        else:
            step_evidence = plan_status  # passed: keep plan label, never upgrade
        action_log.append({
            "step": idx + 1,
            "stepId": sid,
            "action": step.get("action"),
            "target": step.get("target"),
            "value": step.get("value"),
            "outcome": outcome,
            "detail": detail,
            "tabDecision": _tab_decision(tab_lifecycle) if step.get("action") == "navigate" else None,
            "evidence_status": step_evidence,
            "planEvidenceStatus": plan_status,
            "timestamp": finished_at,
        })

    (network_payload, storage_payload, page_state, page_states_written,
     dom_payload, dom_written, console_lines, console_available,
     optional_missing) = _channels_from_result(run_id, result, run_dir)

    screenshots_written = sorted(p.name for p in (run_dir / "screenshots").glob("*.png"))

    # ---- whole-run status (honest) -----------------------------------------
    if not invoked:
        status = "blocked"
        exit_code = EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Unknown"
        failure = {"type": "replay-not-invoked", "cause": replay.get("note", "engine not invoked"),
                   "details": {"stderr": replay.get("stderr", "")}}
    elif any_step_failed:
        status = "failed"
        exit_code = EXIT_ASSERTION
        run_evidence_status = "Unknown"
        failure = {"type": "replay-step-failed",
                   "cause": "one or more replay steps failed or were unsupported",
                   "details": {"engineErrors": result.get("errors", [])}}
    elif any_unsupported_or_failed:
        status = "partial"
        exit_code = EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Unknown"
        failure = None
    else:
        status = "passed"
        exit_code = EXIT_PASS
        run_evidence_status = "Confirmed"
        failure = None

    autonomy_mode = args.autonomy
    project_path = Path(args.project_path).resolve()
    summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": mode,
        "status": status,
        "exitCode": exit_code,
        "evidence_status": run_evidence_status,
        "projectName": _read_project_name(project_path),
        "baseUrl": plan_base_url,
        "target": getattr(args, "target", "") or "",
        "replay": {
            "planId": plan.get("plan_id"),
            "planPath": str(plan_path.relative_to(ROOT)) if str(plan_path).startswith(str(ROOT)) else str(plan_path),
            "planStepCount": len(steps),
            "stepsRecorded": len(action_log),
            "unsupportedOrFailed": any_unsupported_or_failed,
        },
        "browserHarness": {
            "strategy": engine_audit.get("strategy"),
            "available": engine_audit.get("available"),
            "invoked": invoked,
            "version": engine_audit.get("version"),
            "commit": engine_audit.get("commit"),
            "captureNote": replay.get("note"),
            "captureExitCode": replay.get("exitCode"),
            "evidence_status": engine_audit.get("evidence_status"),
        },
        "runScopedEnv": run_env,
        "scope": {"type": "project", "value": args.scope},
        "role": args.role,
        "autonomy": _autonomy_block(config, autonomy_mode),
        "browser": {"name": "", "version": "", "cdpUrl": args.cdp_url, "profileMode": "dedicated"},
        "tabLifecycle": tab_lifecycle,
        "app": {"commandsRun": [], "healthChecks": [cdp_probe], "ownedProcessesStopped": True},
        "channelsUnknown": sorted(optional_missing),
        "artifacts": {
            "actionLog": "action-log.json",
            "network": "network.json",
            "console": "console.log",
            "screenshots": ["screenshots/" + n for n in screenshots_written],
            "pageStates": page_states_written,
            "domSnapshots": dom_written,
        },
        "safety": {"blockedActions": [], "dangerousActionsAllowed": [],
                   "redactionActive": True, "safetyEventsActive": True},
        "failure": failure,
        "timings": {"startedAt": started_at, "finishedAt": finished_at, "durationMs": 0},
    }
    environment = _base_environment(run_id, run_env, engine_audit, config, invoked,
                                    replay.get("command"), replay.get("note"))
    environment["lifecycle"] = {
        "browserHarnessInvoked": invoked,
        "stdinExecutionInvoked": invoked,
        "ownedProcessesStopped": bool(result.get("daemonStopped", False)) or not invoked,
        "daemonStopped": result.get("daemonStopped"),
        "ownedProcessMarker": config["lifecycle"]["ownedProcessMarker"],
    }
    environment["tabLifecycle"] = tab_lifecycle
    safety_events = {
        "schemaVersion": 1,
        "runId": run_id,
        "events": [{
            "eventId": "SAFETY-001",
            "timestamp": finished_at,
            "category": "browser-replay",
            "action": "drive ordered replay actions",
            "decision": "allowed" if invoked else "blocked",
            "reason": "replay explicitly enabled via --allow-browser-harness with safe prerequisites" if invoked else replay.get("note", ""),
            "autonomyMode": autonomy_mode,
            "evidence_status": "Confirmed",
        }],
    }

    _finalize_run(run_dir, run_id, summary, environment, action_log, safety_events,
                  network_payload, storage_payload, page_state, page_states_written,
                  dom_payload, dom_written, console_lines,
                  redaction_evidence_status=run_evidence_status)
    _cleanup_run_scoped(run_id)

    print(json.dumps({
        "mode": mode, "status": status, "runId": run_id,
        "artifactDir": run_info["artifactDir"],
        "summary": run_info["artifactDir"] + "summary.json",
        "evidence_status": run_evidence_status,
        "planStepCount": len(steps), "stepsRecorded": len(action_log),
        "createsArtifacts": True, "exitCode": exit_code,
    }, indent=2, sort_keys=True))
    return exit_code


def _write_qa_run(mode, config, args, cdp_probe):
    """QA mode: open target, capture channels, run basic checks, write qa-findings.json.

    Writes a minimal findings list (NOT a full QA report -- that stays owned by
    gsd-qa-tester). Unavailable channels carry Unknown markers.
    """
    target_arg = (getattr(args, "target", "") or "").strip()
    base_url = (args.base_url or "").rstrip("/")
    target_url = _resolve_target_url(target_arg, base_url) or base_url

    run_info = calculate_run(config, args)
    run_id = run_info["runId"]
    run_dir = ROOT / run_info["artifactDir"]
    started_at = _utc_iso()
    _ensure_run_layout(run_dir)

    run_env = _run_scoped_env(run_id, run_info["artifactDir"])
    adapter = BrowserHarnessAdapter(ROOT, config, env={**os.environ, **run_env})
    engine_audit = adapter.audit()

    screenshot_rel = "screenshots/capture.png"
    screenshot_abs = str((run_dir / screenshot_rel).resolve())
    wait_timeout = float(config["browserHarness"].get("timeoutSeconds", 30)) * 0.5
    capture = adapter.capture(
        target_url,
        run_env,
        screenshot_abs,
        wait_timeout=wait_timeout,
        goal_id=_goal_id_for_run(args, run_id),
        cdp_url=args.cdp_url,
        tab_policy=args.tab_policy,
        new_tab_reason=args.new_tab_reason,
    )
    finished_at = _utc_iso()
    result = capture.get("result") or {}
    tab_lifecycle = _merge_tab_lifecycle(config, args, run_id, capture.get("tabLifecycle") or result.get("tabLifecycle"))
    invoked = capture.get("exitCode") is not None
    loaded = bool(result.get("loaded"))

    (network_payload, storage_payload, page_state, page_states_written,
     dom_payload, dom_written, console_lines, console_available,
     optional_missing) = _channels_from_result(run_id, result, run_dir)

    channels = result.get("channels", {})
    page_info = channels.get("pageInfo") if isinstance(channels.get("pageInfo"), dict) else {}
    screenshot_present = bool(channels.get("screenshotPath")) and (run_dir / screenshot_rel).exists()
    console_errors = []
    if isinstance(channels.get("console"), list):
        for ev in channels["console"]:
            if isinstance(ev, dict) and ev.get("method") == "Runtime.exceptionThrown":
                console_errors.append(ev)

    # ---- basic QA checks (findings list, NOT a full report) -----------------
    def _finding(check_id, desc, ok, evidence_ref, evidence_status):
        return {
            "checkId": check_id,
            "description": desc,
            "status": "pass" if ok else "fail",
            "evidenceRef": evidence_ref,
            "evidence_status": evidence_status,
        }

    findings = [
        _finding("qa-page-loads", "Target reached load-complete", loaded,
                 "action-log.json", "Confirmed" if invoked else "Unknown"),
        _finding("qa-no-engine-failure", "Engine invoked without launch/timeout failure",
                 invoked and capture.get("exitCode") == 0, "summary.json",
                 "Confirmed" if invoked else "Unknown"),
        _finding("qa-title-url-captured", "Page title/url captured",
                 bool(page_info.get("url")), "page-states/page-state-001.json",
                 "Confirmed" if page_info.get("url") else "Unknown"),
        _finding("qa-console-errors", "No uncaught console exceptions recorded",
                 console_available and not console_errors, "console.log",
                 "Confirmed" if console_available else "Unknown"),
        _finding("qa-screenshot", "Screenshot captured",
                 screenshot_present, screenshot_rel,
                 "Confirmed" if screenshot_present else "Unknown"),
    ]
    failed_findings = [f for f in findings if f["status"] == "fail"]

    if not invoked:
        status = "blocked"
        exit_code = EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Unknown"
    elif loaded and not failed_findings:
        status = "passed"
        exit_code = EXIT_PASS
        run_evidence_status = "Confirmed"
    elif loaded:
        status = "partial"
        exit_code = EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Confirmed"
    else:
        status = "failed"
        exit_code = EXIT_ASSERTION
        run_evidence_status = "Unknown"

    autonomy_mode = args.autonomy
    project_path = Path(args.project_path).resolve()
    summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": mode,
        "status": status,
        "exitCode": exit_code,
        "evidence_status": run_evidence_status,
        "projectName": _read_project_name(project_path),
        "baseUrl": args.base_url or "",
        "target": target_arg,
        "targetUrl": target_url,
        "qa": {
            "findingsCount": len(findings),
            "failedFindings": len(failed_findings),
            "reportType": "findings-only",
        },
        "browserHarness": {
            "strategy": engine_audit.get("strategy"),
            "available": engine_audit.get("available"),
            "invoked": invoked,
            "version": engine_audit.get("version"),
            "commit": engine_audit.get("commit"),
            "captureNote": capture.get("note"),
            "captureExitCode": capture.get("exitCode"),
            "evidence_status": engine_audit.get("evidence_status"),
        },
        "runScopedEnv": run_env,
        "scope": {"type": "project", "value": args.scope},
        "role": args.role,
        "autonomy": _autonomy_block(config, autonomy_mode),
        "browser": {"name": "", "version": "", "cdpUrl": args.cdp_url, "profileMode": "dedicated"},
        "tabLifecycle": tab_lifecycle,
        "app": {"commandsRun": [], "healthChecks": [cdp_probe], "ownedProcessesStopped": True},
        "channelsUnknown": sorted(optional_missing),
        "artifacts": {
            "actionLog": "action-log.json",
            "network": "network.json",
            "console": "console.log",
            "qaFindings": "qa-findings.json",
            "screenshots": [screenshot_rel] if screenshot_present else [],
            "pageStates": page_states_written,
            "domSnapshots": dom_written,
        },
        "safety": {"blockedActions": [], "dangerousActionsAllowed": [],
                   "redactionActive": True, "safetyEventsActive": True},
        "failure": None if status in ("passed", "partial") else {
            "type": "qa-target-not-loaded" if invoked else "qa-not-invoked",
            "cause": capture.get("note", "qa target did not load"),
        },
        "timings": {"startedAt": started_at, "finishedAt": finished_at, "durationMs": 0},
    }
    action_log = [{
        "step": 1,
        "action": "navigate",
        "target": target_url,
        "result": "load-complete" if loaded else "load-incomplete-or-failed",
        "ownedTab": result.get("ownedTab"),
        "tabDecision": _tab_decision(tab_lifecycle),
        "evidence_status": "Confirmed" if loaded else "Unknown",
        "timestamp": finished_at,
    }]
    environment = _base_environment(run_id, run_env, engine_audit, config, invoked,
                                    capture.get("command"), capture.get("note"))
    environment["lifecycle"] = {
        "browserHarnessInvoked": invoked,
        "stdinExecutionInvoked": invoked,
        "ownedProcessesStopped": bool(result.get("daemonStopped", False)) or not invoked,
        "daemonStopped": result.get("daemonStopped"),
        "ownedProcessMarker": config["lifecycle"]["ownedProcessMarker"],
    }
    environment["tabLifecycle"] = tab_lifecycle
    safety_events = {
        "schemaVersion": 1,
        "runId": run_id,
        "events": [{
            "eventId": "SAFETY-001",
            "timestamp": finished_at,
            "category": "browser-qa",
            "action": "open target and run basic QA checks",
            "decision": "allowed" if invoked else "blocked",
            "reason": "qa explicitly enabled via --allow-browser-harness with safe prerequisites" if invoked else capture.get("note", ""),
            "autonomyMode": autonomy_mode,
            "evidence_status": "Confirmed",
        }],
    }
    qa_findings_doc = {
        "schemaVersion": 1,
        "runId": run_id,
        "reportType": "findings-only",
        "ownershipNote": "Browser Runtime QA mode writes basic findings only; full QA reports stay owned by gsd-qa-tester.",
        "target": target_url,
        "findings": findings,
    }

    _finalize_run(run_dir, run_id, summary, environment, action_log, safety_events,
                  network_payload, storage_payload, page_state, page_states_written,
                  dom_payload, dom_written, console_lines,
                  extra_artifacts={"qa-findings.json": qa_findings_doc},
                  redaction_evidence_status=run_evidence_status)
    _cleanup_run_scoped(run_id)

    print(json.dumps({
        "mode": mode, "status": status, "runId": run_id,
        "artifactDir": run_info["artifactDir"],
        "summary": run_info["artifactDir"] + "summary.json",
        "evidence_status": run_evidence_status,
        "qaFindings": run_info["artifactDir"] + "qa-findings.json",
        "findingsCount": len(findings), "failedFindings": len(failed_findings),
        "createsArtifacts": True, "exitCode": exit_code,
    }, indent=2, sort_keys=True))
    return exit_code


def _write_smoke_run(mode, config, args, cdp_probe):
    """Smoke mode: deterministic CI-friendly load plus optional text/url assert.

    The smoke pass rule: smoke passes = load reached AND any requested text/url
    assertions hold, INDEPENDENT of optional channel availability (a missing
    network/console/storage channel does NOT fail smoke). Returns 0 ONLY on pass.
    Writes summary.json + action-log.json plus the full artifact set.
    """
    base_url = (args.base_url or "").rstrip("/")
    path = getattr(args, "path", "") or ""
    if path and not path.startswith("/"):
        path = "/" + path
    target_url = base_url + path if base_url else (args.base_url or "")

    run_info = calculate_run(config, args)
    run_id = run_info["runId"]
    run_dir = ROOT / run_info["artifactDir"]
    started_at = _utc_iso()
    _ensure_run_layout(run_dir)

    run_env = _run_scoped_env(run_id, run_info["artifactDir"])
    adapter = BrowserHarnessAdapter(ROOT, config, env={**os.environ, **run_env})
    engine_audit = adapter.audit()

    screenshot_rel = "screenshots/capture.png"
    screenshot_abs = str((run_dir / screenshot_rel).resolve())
    wait_timeout = float(config["browserHarness"].get("timeoutSeconds", 30)) * 0.5
    capture = adapter.capture(
        target_url,
        run_env,
        screenshot_abs,
        wait_timeout=wait_timeout,
        goal_id=_goal_id_for_run(args, run_id),
        cdp_url=args.cdp_url,
        tab_policy=args.tab_policy,
        new_tab_reason=args.new_tab_reason,
    )
    finished_at = _utc_iso()
    result = capture.get("result") or {}
    tab_lifecycle = _merge_tab_lifecycle(config, args, run_id, capture.get("tabLifecycle") or result.get("tabLifecycle"))
    invoked = capture.get("exitCode") is not None
    loaded = bool(result.get("loaded"))

    channels = result.get("channels", {})
    page_info = channels.get("pageInfo") if isinstance(channels.get("pageInfo"), dict) else {}
    dom_snapshot = channels.get("domSnapshot") if isinstance(channels.get("domSnapshot"), str) else ""

    # ---- assertions (optional) ----------------------------------------------
    assert_text = getattr(args, "assert_text", "") or ""
    assert_url = getattr(args, "assert_url", "") or ""
    assertions = []
    text_ok = True
    url_ok = True
    if assert_text:
        text_ok = assert_text in dom_snapshot
        assertions.append({"type": "text", "expected": assert_text, "passed": text_ok})
    if assert_url:
        seen_url = page_info.get("url", "")
        url_ok = assert_url in seen_url
        assertions.append({"type": "url", "expected": assert_url, "seen": seen_url, "passed": url_ok})

    # ---- THE SMOKE PASS RULE (independent of optional channels) -------------
    smoke_passed = bool(invoked and loaded and text_ok and url_ok)

    (network_payload, storage_payload, page_state, page_states_written,
     dom_payload, dom_written, console_lines, console_available,
     optional_missing) = _channels_from_result(run_id, result, run_dir)

    if smoke_passed:
        status = "passed"
        exit_code = EXIT_PASS
        run_evidence_status = "Confirmed"
        failure = None
    elif not invoked:
        status = "blocked"
        exit_code = EXIT_ENGINE if not engine_audit.get("available") else EXIT_PARTIAL_BLOCKED
        run_evidence_status = "Unknown"
        failure = {"type": "smoke-not-invoked", "cause": capture.get("note", "engine not invoked")}
    elif not loaded:
        status = "failed"
        exit_code = EXIT_APP_HEALTH
        run_evidence_status = "Unknown"
        failure = {"type": "smoke-load-failed", "cause": capture.get("note", "target did not load")}
    else:
        status = "failed"
        exit_code = EXIT_ASSERTION
        run_evidence_status = "Confirmed"
        failure = {"type": "smoke-assertion-failed",
                   "cause": "one or more smoke assertions did not hold",
                   "details": {"assertions": assertions}}

    autonomy_mode = args.autonomy
    project_path = Path(args.project_path).resolve()
    summary = {
        "schemaVersion": 1,
        "runId": run_id,
        "mode": mode,
        "status": status,
        "exitCode": exit_code,
        "evidence_status": run_evidence_status,
        "projectName": _read_project_name(project_path),
        "baseUrl": args.base_url or "",
        "targetUrl": target_url,
        "smoke": {
            "passed": smoke_passed,
            "loaded": loaded,
            "assertions": assertions,
            "ciFriendly": True,
            "passRule": "load reached AND requested text/url assertions hold; independent of optional channel availability",
        },
        "browserHarness": {
            "strategy": engine_audit.get("strategy"),
            "available": engine_audit.get("available"),
            "invoked": invoked,
            "version": engine_audit.get("version"),
            "commit": engine_audit.get("commit"),
            "captureNote": capture.get("note"),
            "captureExitCode": capture.get("exitCode"),
            "evidence_status": engine_audit.get("evidence_status"),
        },
        "runScopedEnv": run_env,
        "scope": {"type": "project", "value": args.scope},
        "role": args.role,
        "autonomy": _autonomy_block(config, autonomy_mode),
        "browser": {"name": "", "version": "", "cdpUrl": args.cdp_url, "profileMode": "dedicated"},
        "tabLifecycle": tab_lifecycle,
        "app": {"commandsRun": [], "healthChecks": [cdp_probe], "ownedProcessesStopped": True},
        "channelsUnknown": sorted(optional_missing),
        "artifacts": {
            "actionLog": "action-log.json",
            "network": "network.json",
            "console": "console.log",
            "summary": "summary.json",
            "screenshots": [screenshot_rel] if (run_dir / screenshot_rel).exists() else [],
            "pageStates": page_states_written,
            "domSnapshots": dom_written,
        },
        "safety": {"blockedActions": [], "dangerousActionsAllowed": [],
                   "redactionActive": True, "safetyEventsActive": True},
        "failure": failure,
        "timings": {"startedAt": started_at, "finishedAt": finished_at, "durationMs": 0},
    }
    action_log = [
        {
            "step": 1,
            "action": "navigate",
            "target": target_url,
            "result": "load-complete" if loaded else "load-incomplete-or-failed",
            "ownedTab": result.get("ownedTab"),
            "tabDecision": _tab_decision(tab_lifecycle),
            "evidence_status": "Confirmed" if loaded else "Unknown",
            "timestamp": finished_at,
        }
    ]
    for i, a in enumerate(assertions):
        action_log.append({
            "step": 2 + i,
            "action": "assert-" + a["type"],
            "target": a.get("expected"),
            "result": "passed" if a.get("passed") else "failed",
            "evidence_status": "Confirmed" if invoked else "Unknown",
            "timestamp": finished_at,
        })
    environment = _base_environment(run_id, run_env, engine_audit, config, invoked,
                                    capture.get("command"), capture.get("note"))
    environment["lifecycle"] = {
        "browserHarnessInvoked": invoked,
        "stdinExecutionInvoked": invoked,
        "ownedProcessesStopped": bool(result.get("daemonStopped", False)) or not invoked,
        "daemonStopped": result.get("daemonStopped"),
        "ownedProcessMarker": config["lifecycle"]["ownedProcessMarker"],
    }
    environment["tabLifecycle"] = tab_lifecycle
    safety_events = {
        "schemaVersion": 1,
        "runId": run_id,
        "events": [{
            "eventId": "SAFETY-001",
            "timestamp": finished_at,
            "category": "browser-smoke",
            "action": "open URL and verify load",
            "decision": "allowed" if invoked else "blocked",
            "reason": "smoke explicitly enabled via --allow-browser-harness with safe prerequisites" if invoked else capture.get("note", ""),
            "autonomyMode": autonomy_mode,
            "evidence_status": "Confirmed",
        }],
    }

    _finalize_run(run_dir, run_id, summary, environment, action_log, safety_events,
                  network_payload, storage_payload, page_state, page_states_written,
                  dom_payload, dom_written, console_lines,
                  redaction_evidence_status=run_evidence_status)
    _cleanup_run_scoped(run_id)

    print(json.dumps({
        "mode": mode, "status": status, "runId": run_id,
        "artifactDir": run_info["artifactDir"],
        "summary": run_info["artifactDir"] + "summary.json",
        "evidence_status": run_evidence_status,
        "smokePassed": smoke_passed, "createsArtifacts": True, "exitCode": exit_code,
    }, indent=2, sort_keys=True))
    return exit_code


def run_replay_mode(args):
    """Replay dispatch: prereq-gated; honest blocked otherwise."""
    config = _load_config()
    try:
        Path(args.project_path).resolve(strict=True)
        calculate_run(config, args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_CONFIG
    tab_blocker = _validate_tab_args(config, args)
    if tab_blocker:
        return _write_blocked_run(
            "replay", config, args, tab_blocker,
            {"tabBlocker": tab_blocker, "replayPlan": getattr(args, "replay_plan", ""),
             "wrapperDecision": "blocked-before-browser-harness-tab-policy"},
            exit_code=EXIT_AUTONOMY_BLOCK,
        )

    cdp_probe = _probe_cdp(args.cdp_url)
    blockers = []
    if not cdp_probe.get("reachable"):
        blockers.append("Chrome DevTools Protocol endpoint is not reachable")
    if not args.allow_browser_harness:
        blockers.append("Browser Harness execution was not explicitly enabled for this safety-bounded run")
    if blockers:
        return _write_blocked_run(
            "replay", config, args, "; ".join(blockers),
            {"replayPlan": getattr(args, "replay_plan", ""), "cdpProbe": cdp_probe,
             "allowBrowserHarness": args.allow_browser_harness,
             "wrapperDecision": "replay-blocked-before-browser-harness"},
        )
    return _write_replay_run("replay", config, args, cdp_probe)


def run_qa_mode(args):
    config = _load_config()
    try:
        Path(args.project_path).resolve(strict=True)
        calculate_run(config, args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_CONFIG
    tab_blocker = _validate_tab_args(config, args)
    if tab_blocker:
        return _write_blocked_run(
            "qa", config, args, tab_blocker,
            {"tabBlocker": tab_blocker, "baseUrl": args.base_url or "",
             "target": getattr(args, "target", "") or "",
             "wrapperDecision": "blocked-before-browser-harness-tab-policy"},
            exit_code=EXIT_AUTONOMY_BLOCK,
        )

    cdp_probe = _probe_cdp(args.cdp_url)
    blockers = []
    if not args.base_url:
        blockers.append("no explicit base URL was provided for the QA target")
    if not cdp_probe.get("reachable"):
        blockers.append("Chrome DevTools Protocol endpoint is not reachable")
    if not args.allow_browser_harness:
        blockers.append("Browser Harness execution was not explicitly enabled for this safety-bounded run")
    if blockers:
        return _write_blocked_run(
            "qa", config, args, "; ".join(blockers),
            {"baseUrl": args.base_url or "", "target": getattr(args, "target", "") or "",
             "cdpProbe": cdp_probe, "allowBrowserHarness": args.allow_browser_harness,
             "wrapperDecision": "qa-blocked-before-browser-harness"},
        )
    return _write_qa_run("qa", config, args, cdp_probe)


def run_smoke_mode(args):
    config = _load_config()
    try:
        Path(args.project_path).resolve(strict=True)
        calculate_run(config, args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_CONFIG
    tab_blocker = _validate_tab_args(config, args)
    if tab_blocker:
        return _write_blocked_run(
            "smoke", config, args, tab_blocker,
            {"tabBlocker": tab_blocker, "baseUrl": args.base_url or "",
             "path": getattr(args, "path", "") or "",
             "wrapperDecision": "blocked-before-browser-harness-tab-policy"},
            exit_code=EXIT_AUTONOMY_BLOCK,
        )

    if getattr(args, "launch_browser", False):
        setup = _setup_defaults(config)
        if not getattr(args, "cdp_url", ""):
            args.cdp_url = setup["defaultCdpUrl"]
        launch_args = argparse.Namespace(
            chrome_path=getattr(args, "chrome_path", ""),
            cdp_url=args.cdp_url,
            force=False,
            headless=False,
            interval_seconds=0.5,
            open_url=args.base_url or "about:blank",
            port=setup["defaultDebuggingPort"],
            profile_dir="",
            timeout_seconds=float(config["browserHarness"].get("timeoutSeconds", 30)),
        )
        launch = _launch_chrome(config, launch_args)
        if launch.get("exitCode") != EXIT_PASS:
            return _write_blocked_run(
                "smoke", config, args, "Chrome could not be launched for smoke automation",
                {"launchChrome": launch, "wrapperDecision": "smoke-blocked-before-cdp"},
                exit_code=launch.get("exitCode", EXIT_ENGINE),
            )

    cdp_probe = _probe_cdp(args.cdp_url)
    blockers = []
    if not args.base_url:
        blockers.append("no explicit base URL was provided for the smoke target")
    if not cdp_probe.get("reachable"):
        blockers.append("Chrome DevTools Protocol endpoint is not reachable")
    if not args.allow_browser_harness:
        blockers.append("Browser Harness execution was not explicitly enabled for this safety-bounded run")
    if blockers:
        return _write_blocked_run(
            "smoke", config, args, "; ".join(blockers),
            {"baseUrl": args.base_url or "", "path": getattr(args, "path", "") or "",
             "cdpProbe": cdp_probe, "allowBrowserHarness": args.allow_browser_harness,
             "wrapperDecision": "smoke-blocked-before-browser-harness"},
        )
    return _write_smoke_run("smoke", config, args, cdp_probe)


def run_evidence_mode(mode, args):
    config = _load_config()
    try:
        Path(args.project_path).resolve(strict=True)
        calculate_run(config, args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_CONFIG
    tab_blocker = _validate_tab_args(config, args)
    if tab_blocker:
        return _write_blocked_run(
            mode,
            config,
            args,
            tab_blocker,
            {
                "tabBlocker": tab_blocker,
                "projectPath": str(Path(args.project_path).resolve()),
                "baseUrl": args.base_url or "",
                "target": getattr(args, "target", "") or "",
                "wrapperDecision": "blocked-before-browser-harness-tab-policy",
            },
            exit_code=EXIT_AUTONOMY_BLOCK,
        )

    cdp_probe = _probe_cdp(args.cdp_url)
    blockers = []
    if not args.base_url:
        blockers.append("no explicit base URL was provided for the validation target")
    if not cdp_probe.get("reachable"):
        blockers.append("Chrome DevTools Protocol endpoint is not reachable")
    if not args.allow_browser_harness:
        blockers.append("Browser Harness execution was not explicitly enabled for this safety-bounded run")

    if blockers:
        return _write_blocked_run(
            mode,
            config,
            args,
            "; ".join(blockers),
            {
                "projectPath": str(Path(args.project_path).resolve()),
                "baseUrl": args.base_url or "",
                "target": getattr(args, "target", "") or "",
                "cdpProbe": cdp_probe,
                "allowBrowserHarness": args.allow_browser_harness,
                "wrapperDecision": "blocked-before-browser-harness-capture",
            },
        )

    # Prerequisites satisfied. The `evidence` mode performs real capture through
    # the resolved engine; replay/qa/smoke use their dedicated dispatchers.
    return _write_capture_run(mode, config, args, cdp_probe)


def print_config(args):
    config = _load_config()
    print(json.dumps(config, indent=2, sort_keys=True))
    return 0


def print_path(args):
    config = _load_config()
    try:
        payload = calculate_run(config, args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def run_doctor(args):
    """No-browser-capable doctor with deterministic exit codes.

    Exit codes: 0 pass, 2 config/setup error, 3 engine unavailable/doctor failed,
    7 report/redaction failure (browser-evidence-contract.md).
    Never starts an app server, the engine daemon, or mutates the project.
    """
    checks = {}
    blockers = []

    # Config load + JSON validity (2 = config/setup error).
    try:
        config = _load_config()
        checks["configLoads"] = True
    except (OSError, json.JSONDecodeError) as exc:
        payload = {
            "command": "doctor",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "checks": {"configLoads": False},
            "error": str(exc),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return EXIT_CONFIG

    # Artifact root must be repo-local.
    artifact_root = config.get("artifactRoot", "")
    artifact_repo_local = bool(artifact_root) and not Path(artifact_root).is_absolute() and ".." not in Path(artifact_root).parts
    checks["artifactRootRepoLocal"] = artifact_repo_local
    if not artifact_repo_local:
        blockers.append("artifactRoot is not repo-local")

    # browserHarness strategy block must be present and well-formed.
    bh = config.get("browserHarness")
    bh_ok = isinstance(bh, dict) and all(k in bh for k in ("strategy", "command", "vendorPath", "python", "timeoutSeconds"))
    checks["browserHarnessConfig"] = bh_ok
    if not bh_ok:
        blockers.append("config.browserHarness strategy block is missing or incomplete")

    # Python version is recorded (verify interpreter is usable).
    checks["pythonVersion"] = sys.version.split()[0]

    # Run-scoped dirs can be created (probe is self-cleaning; doctor stays read-only).
    try:
        import shutil as _shutil

        probe = ROOT / ".planning" / "tmp" / "browser-harness" / "doctor-probe"
        probe.mkdir(parents=True, exist_ok=True)
        checks["runScopedDirsCreatable"] = True
        _shutil.rmtree(probe, ignore_errors=True)
    except OSError as exc:
        checks["runScopedDirsCreatable"] = False
        blockers.append(f"cannot create run-scoped dirs: {exc}")

    # Redaction policy loads (verify the centralized helper is functional).
    try:
        _, _ = redact_text("authorization: Bearer abc123")
        checks["redactionPolicyLoads"] = True
    except re.error as exc:
        checks["redactionPolicyLoads"] = False
        blockers.append(f"redaction policy failed to load: {exc}")

    # Exit-code mapping is present.
    checks["exitCodeMapping"] = {
        "pass": EXIT_PASS,
        "configSetup": EXIT_CONFIG,
        "engineUnavailable": EXIT_ENGINE,
        "reportRedaction": EXIT_REDACTION,
    }

    # Engine resolution + identity audit (no browser/daemon start).
    engine_audit = BrowserHarnessAdapter(ROOT, config).audit()
    checks["engineAudit"] = engine_audit

    status = "passed"
    exit_code = EXIT_PASS
    if not engine_audit.get("available"):
        # Engine unavailable is a deterministic blocker but does NOT fail the phase;
        # doctor reports exit 3 (engine unavailable) per the contract.
        status = "blocked"
        exit_code = EXIT_ENGINE
        blockers.append(engine_audit.get("blocker") or "Browser Harness engine unavailable")
    if not checks["redactionPolicyLoads"]:
        status = "failed"
        exit_code = EXIT_REDACTION
    elif blockers and exit_code == EXIT_PASS:
        status = "failed"
        exit_code = EXIT_CONFIG

    payload = {
        "command": "doctor",
        "status": status,
        "exitCode": exit_code,
        "startsAppServer": False,
        "startsEngineDaemon": False,
        "mutatesProject": False,
        "engine": engine_audit,
        "checks": checks,
        "blockers": blockers,
        "evidence_status": engine_audit.get("evidence_status", "Unknown"),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


def run_setup_check(args):
    """Read-only install readiness check for the first browser-evidence goal."""
    try:
        config = _load_config()
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "command": "setup-check",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "error": str(exc),
        }, indent=2, sort_keys=True))
        return EXIT_CONFIG

    setup = _setup_defaults(config)
    engine_audit = BrowserHarnessAdapter(ROOT, config).audit(
        allow_bootstrap=not args.skip_browser_harness_install
    )
    chrome_path = _find_chrome(args.chrome_path)
    cdp_url = args.cdp_url or setup["defaultCdpUrl"]
    cdp_probe = _probe_cdp(cdp_url)
    app_probe = _probe_http(args.base_url) if args.base_url else {
        "url": "",
        "reachable": False,
        "skipped": True,
        "reason": "--base-url not supplied",
    }

    required_user_inputs = [
        {"name": "baseUrl", "required": True, "reason": "Target app URL to validate."},
        {"name": "safeDataPolicy", "required": True, "reason": "Whether browser automation may run against local, staging, or real data."},
        {"name": "credentialsOrManualLogin", "required": "when-app-needs-auth", "reason": "The agent must not invent credentials or perform MFA alone."},
    ]
    blockers = []
    if not engine_audit.get("available"):
        blockers.append("Browser Harness engine is unavailable")
    if not chrome_path:
        blockers.append("Chrome executable is unavailable")
    if args.require_cdp and not cdp_probe.get("reachable"):
        blockers.append("Chrome CDP endpoint is unavailable")
    if args.base_url and args.require_app and not app_probe.get("reachable"):
        blockers.append("target app is unavailable")

    status = "passed" if not blockers else "blocked"
    payload = {
        "command": "setup-check",
        "status": status,
        "exitCode": EXIT_PASS if status == "passed" else EXIT_PARTIAL_BLOCKED,
        "mutatesProject": False,
        "startsBrowser": False,
        "engine": engine_audit,
        "chrome": {
            "available": bool(chrome_path),
            "path": chrome_path,
        },
        "cdp": cdp_probe,
        "app": app_probe,
        "agentRunnableSteps": setup["agentRunnableSteps"],
        "userOnlyPrerequisites": setup["userOnlyPrerequisites"],
        "requiredUserInputsAtFirstGoal": required_user_inputs,
        "nextAgentCommands": [
            "python .gsd/browser-evidence.py ensure-browser-harness",
            f"python .gsd/browser-evidence.py launch-chrome --port {setup['defaultDebuggingPort']}",
            f"python .gsd/browser-evidence.py wait-cdp --cdp-url {cdp_url}",
            "python .gsd/browser-evidence.py wait-app --base-url <user-provided-url>",
            "python .gsd/browser-evidence.py smoke --launch-browser --base-url <user-provided-url> --allow-browser-harness --tab-policy reuse-primary",
        ],
        "blockers": blockers,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload["exitCode"]


def run_ensure_browser_harness(args):
    try:
        config = _load_config()
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "command": "ensure-browser-harness",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "error": str(exc),
        }, indent=2, sort_keys=True))
        return EXIT_CONFIG

    bootstrap = config.get("browserHarnessBootstrap", {})
    ensure_script = ROOT / bootstrap.get("ensureScript", ".gsd/ensure-browser-harness.py")
    lock_path = ROOT / bootstrap.get("lockPath", ".gsd/browser-harness.lock.json")
    if not ensure_script.is_file() or not lock_path.is_file():
        print(json.dumps({
            "command": "ensure-browser-harness",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "error": "Browser Harness bootstrap script or lock file is missing",
        }, indent=2, sort_keys=True))
        return EXIT_CONFIG

    action = "--check-only" if args.check_only else "--install"
    command = [
        config.get("browserHarness", {}).get("python", "python"),
        str(ensure_script),
        "--json",
        action,
        "--lock-path",
        str(lock_path),
        "--timeout-seconds",
        str(args.timeout_seconds or bootstrap.get("installTimeoutSeconds", 300)),
    ]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "failed",
            "available": False,
            "blockers": [result.stderr.strip() or result.stdout.strip() or "ensure script did not return JSON"],
        }
    payload["command"] = "ensure-browser-harness"
    payload["mutatesProject"] = False
    payload["cacheOnly"] = True
    payload["exitCode"] = EXIT_PASS if payload.get("available") else EXIT_ENGINE
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload["exitCode"]


def run_launch_chrome(args):
    try:
        config = _load_config()
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "command": "launch-chrome",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "error": str(exc),
        }, indent=2, sort_keys=True))
        return EXIT_CONFIG
    payload = _launch_chrome(config, args)
    payload["command"] = "launch-chrome"
    payload["userOnlyNote"] = "If Chrome is missing or blocked by OS/security prompts, the user must install/approve it."
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload["exitCode"]


def run_wait_cdp(args):
    ready, attempts, probe = _wait_http(args.cdp_url, args.timeout_seconds, args.interval_seconds)
    payload = {
        "command": "wait-cdp",
        "status": "passed" if ready else "blocked",
        "exitCode": EXIT_PASS if ready else EXIT_ENGINE,
        "cdpUrl": args.cdp_url,
        "attempts": attempts,
        "probe": probe,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload["exitCode"]


def run_wait_app(args):
    if not args.base_url:
        print(json.dumps({
            "command": "wait-app",
            "status": "failed",
            "exitCode": EXIT_CONFIG,
            "error": "--base-url is required",
        }, indent=2, sort_keys=True))
        return EXIT_CONFIG
    ready, attempts, probe = _wait_http(args.base_url, args.timeout_seconds, args.interval_seconds)
    payload = {
        "command": "wait-app",
        "status": "passed" if ready else "blocked",
        "exitCode": EXIT_PASS if ready else EXIT_APP_HEALTH,
        "baseUrl": args.base_url,
        "attempts": attempts,
        "probe": probe,
        "userOnlyNote": "If the app requires login, MFA, credentials, or data-safety approval, the user must provide that before browser evidence runs.",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload["exitCode"]


def add_path_args(parser):
    parser.add_argument("--timestamp", help="UTC timestamp for deterministic run ID: YYYYMMDD-HHMMSS")
    parser.add_argument("--scope", default="manual", help="Scope slug source")
    parser.add_argument("--role", default="agent", help="Role slug source")
    parser.add_argument("--run-id", help="Precomputed run ID override")


def add_runtime_args(parser):
    add_path_args(parser)
    parser.add_argument("--project-path", default=".", help="External validation repository path")
    parser.add_argument("--base-url", default="", help="Browser target URL. Required for real capture.")
    parser.add_argument(
        "--target",
        default="",
        help="Capture target as page:<path> or url:<url>. Combines with --base-url for page:<path>.",
    )
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222/json/version", help="Chrome CDP version endpoint")
    parser.add_argument("--goal-id", default="", help="Goal-scoped browser session id. Defaults from the run id.")
    parser.add_argument("--tab-policy", choices=TAB_POLICIES, default="reuse-primary", help="Browser tab policy for this run.")
    parser.add_argument("--new-tab-reason", default="", help="Allowed critical reason for opening a new tab.")
    parser.add_argument("--autonomy", choices=("safe", "custom", "unrestricted"), default="safe")
    parser.add_argument(
        "--allow-browser-harness",
        action="store_true",
        help="Allow Browser Harness stdin execution when safe prerequisites are present.",
    )


def add_wait_args(parser, url_arg):
    parser.add_argument(url_arg, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--interval-seconds", type=float, default=0.5)


def add_chrome_launch_args(parser):
    parser.add_argument("--chrome-path", default="", help="Optional explicit Chrome executable path.")
    parser.add_argument("--cdp-url", default="", help="Chrome CDP version endpoint. Defaults from browserSetup.")
    parser.add_argument("--port", type=int, default=0, help="Remote debugging port. Defaults from browserSetup.")
    parser.add_argument("--profile-dir", default="", help="Dedicated Chrome profile dir. Defaults under .planning/tmp/.")
    parser.add_argument("--open-url", default="", help="Optional URL to open after launch; defaults to about:blank.")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--interval-seconds", type=float, default=0.5)
    parser.add_argument("--headless", action="store_true", help="Launch Chrome headless when supported.")
    parser.add_argument("--force", action="store_true", help="Start a new Chrome process even when CDP is already reachable.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="browser-evidence",
        description="GSD Browser Evidence Runtime wrapper. Runtime modes expose --goal-id, --tab-policy, and --new-tab-reason.",
        epilog="Browser modes: --goal-id <goal-id> --tab-policy reuse-primary|allow-new-tab|force-new-tab --new-tab-reason <reason>",
    )
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config", help="Print deterministic runtime config as JSON")
    config_parser.set_defaults(func=print_config)

    path_parser = subparsers.add_parser("path", help="Calculate run ID and artifact path without creating artifacts")
    add_path_args(path_parser)
    path_parser.set_defaults(func=print_path)

    setup_parser = subparsers.add_parser("setup-check", help="Browser evidence install/readiness check")
    setup_parser.add_argument("--chrome-path", default="", help="Optional explicit Chrome executable path.")
    setup_parser.add_argument("--cdp-url", default="", help="Chrome CDP version endpoint. Defaults from browserSetup.")
    setup_parser.add_argument("--base-url", default="", help="Optional target app URL to check.")
    setup_parser.add_argument("--require-cdp", action="store_true", help="Treat missing CDP as a blocker.")
    setup_parser.add_argument("--require-app", action="store_true", help="Treat unreachable --base-url as a blocker.")
    setup_parser.add_argument(
        "--skip-browser-harness-install",
        action="store_true",
        help="Check readiness without installing Browser Harness into the user cache.",
    )
    setup_parser.set_defaults(func=run_setup_check)

    ensure_parser = subparsers.add_parser("ensure-browser-harness", help="Install or verify Browser Harness in the GSD user cache")
    ensure_parser.add_argument("--check-only", action="store_true", help="Check PATH/cache without installing.")
    ensure_parser.add_argument("--timeout-seconds", type=int, default=0, help="Override install/check timeout.")
    ensure_parser.set_defaults(func=run_ensure_browser_harness)

    launch_parser = subparsers.add_parser("launch-chrome", help="Launch dedicated Chrome with CDP using a repo-local profile")
    add_chrome_launch_args(launch_parser)
    launch_parser.set_defaults(func=run_launch_chrome)

    wait_cdp_parser = subparsers.add_parser("wait-cdp", help="Wait until Chrome CDP is reachable")
    add_wait_args(wait_cdp_parser, "--cdp-url")
    wait_cdp_parser.set_defaults(func=run_wait_cdp)

    wait_app_parser = subparsers.add_parser("wait-app", help="Wait until the target app URL is reachable")
    add_wait_args(wait_app_parser, "--base-url")
    wait_app_parser.set_defaults(func=run_wait_app)

    for mode in MODES:
        mode_parser = subparsers.add_parser(mode, help=f"Run or report {mode} mode")
        if mode == "doctor":
            add_path_args(mode_parser)
            mode_parser.set_defaults(func=lambda args: run_doctor(args))
        elif mode == "evidence":
            add_runtime_args(mode_parser)
            mode_parser.set_defaults(func=lambda args, selected=mode: run_evidence_mode(selected, args))
        elif mode == "replay":
            add_runtime_args(mode_parser)
            mode_parser.add_argument(
                "--replay-plan",
                default=".gsd/fixtures/browser-evidence/replay.plan.json",
                help="Path to replay.plan.json (consumes base_url + steps[]).",
            )
            mode_parser.set_defaults(func=run_replay_mode)
        elif mode == "qa":
            add_runtime_args(mode_parser)
            mode_parser.set_defaults(func=run_qa_mode)
        elif mode == "smoke":
            add_runtime_args(mode_parser)
            mode_parser.add_argument("--path", default="", help="Optional path appended to --base-url.")
            mode_parser.add_argument("--assert-text", default="", help="Optional text that must appear in the DOM.")
            mode_parser.add_argument("--assert-url", default="", help="Optional substring that must appear in the loaded URL.")
            mode_parser.add_argument("--launch-browser", action="store_true", help="Launch dedicated Chrome first when CDP is not already reachable.")
            mode_parser.add_argument("--chrome-path", default="", help="Optional explicit Chrome executable path for --launch-browser.")
            mode_parser.set_defaults(func=run_smoke_mode)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
