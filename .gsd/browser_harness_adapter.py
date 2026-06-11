"""Browser Harness engine adapter.

Responsibilities:
- Resolve a Browser Harness engine via a deterministic path -> cache -> module -> vendor strategy.
- Provide a no-browser-safe identity/doctor audit (version/commit/path or a blocker).
- Drive a bounded real capture through the engine's stdin/heredoc
  execution surface, returning structured channel data for the wrapper to redact
  and finalize.

Confirmed Browser Harness helper-API names (from
`.vendor/browser-harness/src/browser_harness/helpers.py`, pre-imported into the
heredoc namespace via `from .helpers import *` in `run.py`):
  new_tab(url), goto_url(url), wait_for_load(timeout), page_info(),
  current_tab(), list_tabs(), ensure_real_tab(), capture_screenshot(path),
  js(expression), drain_events(), close_tab(target).
`restart_daemon()` is in the heredoc namespace too (imported from `admin` in
`run.py`) and stops the run-scoped daemon on cleanup. These names were CONFIRMED
by source inspection and a live probe; they were not invented.

Source traceability (compact, do not duplicate registry rows):
- Wrapper does not fork Browser Harness ownership; engine stays the low-level CDP layer.
- Wrapper owns evidence artifacts, safety metadata, redaction, and Unknown fallback markers.
- Engine audit records availability, version, and commit when they can be inspected.
- Subprocess/heredoc capture remains bounded and adapter-owned.
- Browser Harness interactive behavior is preserved behind the wrapper boundary.
"""

import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


CAPTURE_RESULT_MARKER = "GSD_CAPTURE_RESULT:"
ALLOWED_TAB_POLICIES = {"reuse-primary", "allow-new-tab", "force-new-tab"}
ALLOWED_NEW_TAB_REASONS = {
    "oauth_sso_popup",
    "external_provider_popup",
    "payment_provider_popup",
    "side_by_side_comparison",
    "app_opened_new_tab",
    "preserve_unsaved_state",
    "manual_user_requested",
}


class BrowserHarnessAdapter:
    """Resolves and audits a Browser Harness engine, and drives a bounded capture.

    Resolution + identity audit are no-browser-safe. The `capture()` method drives
    a real, run-scoped, timeout-bounded capture through the engine's stdin/heredoc
    surface using the CONFIRMED helper names listed in the module docstring.
    """

    def __init__(self, root, config, env=None, timeout_seconds=None):
        self.root = Path(root)
        self.config = config
        self.env = env
        bh = config.get("browserHarness", {})
        self.command = bh.get("command", "browser-harness")
        self.vendor_path = bh.get("vendorPath", ".vendor/browser-harness/")
        self.python = bh.get("python", "python")
        self.timeout_seconds = timeout_seconds or bh.get("timeoutSeconds", 30)
        bootstrap = config.get("browserHarnessBootstrap", {})
        self.bootstrap_enabled = bool(bootstrap.get("enabled", True))
        self.bootstrap_auto_install = bool(bootstrap.get("autoInstall", True))
        self.bootstrap_lock_path = bootstrap.get("lockPath", ".gsd/browser-harness.lock.json")
        self.bootstrap_script_path = bootstrap.get("ensureScript", ".gsd/ensure-browser-harness.py")
        self.bootstrap_timeout_seconds = int(bootstrap.get("installTimeoutSeconds", 300))

    # -- strategy resolution -------------------------------------------------

    def resolve_strategy(self, auto_bootstrap=False):
        """Resolve the engine using path -> cache -> module -> vendor priority.

        Returns a dict describing the resolved strategy. No subprocess is run
        beyond PATH/cache checks unless auto_bootstrap is explicitly enabled.
        """
        # (1) Lock-aware resolver. It prefers PATH when the pinned version matches,
        # then the GSD-managed user cache. Check-only is no-browser-safe.
        cache_strategy = self._cache_strategy(install=False)
        if cache_strategy.get("available"):
            return cache_strategy

        # Legacy fallback only when the bootstrap files are absent or disabled.
        bootstrap_detail = cache_strategy.get("detail", "")
        if (not self.bootstrap_enabled) or "script or lock file is missing" in bootstrap_detail:
            on_path = shutil.which(self.command)
            if on_path:
                return {
                    "strategy": "path",
                    "available": True,
                    "command": [self.command],
                    "source": on_path,
                    "detail": "browser-harness executable resolved on PATH",
                }

        # (3) Python module / entry point in the vendored src tree
        vendor_dir = (self.root / self.vendor_path).resolve()
        vendor_src = vendor_dir / "src"
        module_init = vendor_src / "browser_harness" / "__init__.py"
        if module_init.exists():
            return {
                "strategy": "module",
                "available": True,
                "command": [self.python, "-m", "browser_harness.run"],
                "source": str(module_init),
                "pythonPath": str(vendor_src),
                "detail": "browser_harness Python module resolved in vendor src tree",
            }

        # (4) configured local vendor path (present but not importable as a module)
        if vendor_dir.exists():
            return {
                "strategy": "vendor",
                "available": True,
                "command": None,
                "source": str(vendor_dir),
                "detail": "vendor directory present but no PATH executable or importable module resolved",
            }

        if auto_bootstrap and self.bootstrap_enabled and self.bootstrap_auto_install:
            installed_strategy = self._cache_strategy(install=True)
            if installed_strategy.get("available"):
                return installed_strategy

        blocker = cache_strategy.get("blocker") or cache_strategy.get("detail")
        return {
            "strategy": "none",
            "available": False,
            "command": None,
            "source": None,
            "detail": blocker or "no PATH executable, cached engine, Python module, or vendor directory resolved",
        }

    def _strategy_env(self, strategy, *overrides):
        merged = {**os.environ}
        if self.env:
            merged.update(self.env)
        for env in overrides:
            if env:
                merged.update(env)
        if strategy.get("pythonPath"):
            existing = merged.get("PYTHONPATH")
            python_path = str(strategy["pythonPath"])
            merged["PYTHONPATH"] = f"{python_path}{os.pathsep}{existing}" if existing else python_path
        for key, value in (strategy.get("env") or {}).items():
            merged[str(key)] = str(value)
        return merged

    def _cache_strategy(self, install=False):
        if not self.bootstrap_enabled:
            return {
                "strategy": "cache",
                "available": False,
                "command": None,
                "source": None,
                "detail": "Browser Harness bootstrap is disabled",
            }
        ensure_script = (self.root / self.bootstrap_script_path).resolve()
        lock_path = (self.root / self.bootstrap_lock_path).resolve()
        if not ensure_script.is_file() or not lock_path.is_file():
            return {
                "strategy": "cache",
                "available": False,
                "command": None,
                "source": None,
                "detail": "Browser Harness bootstrap script or lock file is missing",
            }
        args = [
            self.python,
            str(ensure_script),
            "--json",
            "--lock-path",
            str(lock_path),
            "--install" if install else "--check-only",
            "--timeout-seconds",
            str(self.bootstrap_timeout_seconds if install else self.timeout_seconds),
        ]
        try:
            result = subprocess.run(
                args,
                cwd=str(self.root),
                text=True,
                capture_output=True,
                check=False,
                timeout=self.bootstrap_timeout_seconds if install else self.timeout_seconds,
                env=self.env,
            )
        except subprocess.TimeoutExpired:
            return {
                "strategy": "cache",
                "available": False,
                "command": None,
                "source": None,
                "detail": "Browser Harness bootstrap timed out",
            }
        except OSError as exc:
            return {
                "strategy": "cache",
                "available": False,
                "command": None,
                "source": None,
                "detail": f"Browser Harness bootstrap failed to launch: {exc}",
            }
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            detail = result.stderr.strip() or result.stdout.strip() or f"bootstrap exited {result.returncode}"
            return {
                "strategy": "cache",
                "available": False,
                "command": None,
                "source": None,
                "detail": detail,
            }
        command = payload.get("command")
        if payload.get("available") and isinstance(command, list) and command:
            return {
                "strategy": payload.get("strategy") or "cache",
                "available": True,
                "command": [str(item) for item in command],
                "source": payload.get("source"),
                "detail": "Browser Harness resolved through GSD user-cache bootstrap",
                "version": payload.get("version"),
                "commit": payload.get("revision") or payload.get("lock", {}).get("revision"),
                "cacheRoot": payload.get("cacheRoot"),
            }
        blockers = payload.get("blockers") or [payload.get("blocker") or "Browser Harness bootstrap did not resolve an engine"]
        return {
            "strategy": "cache",
            "available": False,
            "command": None,
            "source": payload.get("source"),
            "detail": "; ".join(str(item) for item in blockers if item),
            "blocker": "; ".join(str(item) for item in blockers if item),
        }

    # -- identity / audit ----------------------------------------------------

    def _vendor_commit(self):
        """Read the vendored engine commit without driving anything (read-only git)."""
        vendor_dir = (self.root / self.vendor_path).resolve()
        if not (vendor_dir / ".git").exists():
            return None
        try:
            result = subprocess.run(
                ["git", "-C", str(vendor_dir), "rev-parse", "HEAD"],
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if result.returncode == 0:
            return result.stdout.strip() or None
        return None

    def _engine_version(self, strategy):
        """Get engine version via `--version` only (pre-daemon, no browser start).

        Returns (version_or_None, raw_note). Never starts the auto-start daemon.
        """
        command = strategy.get("command")
        if not command:
            return None, "no invocable engine command resolved"
        try:
            result = subprocess.run(
                [*command, "--version"],
                cwd=str(self.root),
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
                env=self._strategy_env(strategy),
            )
        except subprocess.TimeoutExpired:
            return None, "engine --version timed out"
        except OSError as exc:
            return None, f"engine --version failed to launch: {exc}"
        if result.returncode != 0:
            return None, f"engine --version exited {result.returncode}: {result.stderr.strip()}"
        return (result.stdout.strip() or result.stderr.strip() or None), "engine --version succeeded"

    def audit(self, allow_bootstrap=False):
        """No-browser-safe engine audit for `doctor`.

        Records resolved strategy, version (via --version), and vendored commit.
        Engine facts stay Unknown when the engine cannot be inspected.
        Does NOT invoke `browser-harness doctor` because the engine help documents
        that the daemon auto-starts, which would violate the no-app-server boundary.
        """
        strategy = self.resolve_strategy(auto_bootstrap=allow_bootstrap)
        commit = strategy.get("commit") or self._vendor_commit()

        if not strategy["available"]:
            return {
                "available": False,
                "strategy": strategy["strategy"],
                "source": strategy["source"],
                "version": None,
                "commit": commit,
                "remote": "https://github.com/browser-use/browser-harness.git",
                "evidence_status": "Unknown",
                "blocker": "Browser Harness engine is not resolvable via path/module/vendor",
                "detail": strategy["detail"],
                "daemonProbed": False,
            }

        version, version_note = self._engine_version(strategy)
        # The engine resolved and identity was inspected; identity facts are
        # Confirmed-in-audit. Live browser/daemon capability remains Unknown until
        # a real capture phase exercises it (we intentionally do not start the daemon).
        return {
            "available": True,
            "strategy": strategy["strategy"],
            "source": strategy["source"],
            "version": version,
            "commit": commit,
            "remote": "https://github.com/browser-use/browser-harness.git",
            "evidence_status": "Confirmed" if version else "Suggested",
            "versionNote": version_note,
            "detail": strategy["detail"],
            "daemonProbed": False,
            "liveBrowserCapability": "Unknown",
        }

    # -- real capture ---------------------------------------------------------

    def _utc_iso(self):
        return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")

    def _safe_goal_id(self, goal_id):
        return re.sub(r"[^A-Za-z0-9_.-]+", "-", (goal_id or "").strip()).strip("-") or "manual"

    def _tab_config(self):
        return self.config.get("tabLifecycle", {})

    def _session_path(self, goal_id):
        root = self._tab_config().get("sessionStateRoot", ".planning/tmp/browser-harness/sessions/")
        session_root = self.root / root
        session_root.mkdir(parents=True, exist_ok=True)
        return session_root / f"{self._safe_goal_id(goal_id)}.json"

    def _default_tab_lifecycle(self, goal_id, cdp_url, tab_policy, new_tab_reason=""):
        return {
            "goalId": self._safe_goal_id(goal_id),
            "tabPolicy": tab_policy or self._tab_config().get("defaultPolicy", "reuse-primary"),
            "reusePolicy": self._tab_config().get("reusePolicy", "single-primary-tab"),
            "primaryTargetId": "",
            "primaryTabUrlBefore": "",
            "primaryTabUrlAfter": "",
            "openedNewTabs": [],
            "closedExtraTabs": [],
            "preservedTabs": [],
            "newTabReasons": [new_tab_reason] if new_tab_reason else [],
            "blockedNewTabAttempts": [],
            "tabDecisionEvidenceStatus": "Confirmed",
            "cdpUrl": cdp_url,
        }

    def _load_session_state(self, goal_id, cdp_url):
        path = self._session_path(goal_id)
        now = self._utc_iso()
        if path.exists():
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                state = {}
        else:
            state = {}
        state.setdefault("schema_version", 1)
        state["goalId"] = self._safe_goal_id(goal_id)
        state.setdefault("cdpUrl", cdp_url)
        state.setdefault("primaryTargetId", "")
        state.setdefault("primaryTabUrl", "")
        state.setdefault("profileDir", "")
        state.setdefault("reusePolicy", self._tab_config().get("reusePolicy", "single-primary-tab"))
        state.setdefault("createdAt", now)
        state["updatedAt"] = now
        state.setdefault("ownedTabs", [])
        state.setdefault("preservedTabs", [])
        return state

    def _save_session_state(self, goal_id, state, tab_lifecycle):
        now = self._utc_iso()
        state["updatedAt"] = now
        state["primaryTargetId"] = tab_lifecycle.get("primaryTargetId", state.get("primaryTargetId", ""))
        state["primaryTabUrl"] = tab_lifecycle.get("primaryTabUrlAfter", state.get("primaryTabUrl", ""))
        state["ownedTabs"] = tab_lifecycle.get("openedNewTabs", state.get("ownedTabs", []))
        state["preservedTabs"] = tab_lifecycle.get("preservedTabs", state.get("preservedTabs", []))
        self._session_path(goal_id).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _validate_tab_request(self, tab_policy, new_tab_reason):
        if tab_policy not in ALLOWED_TAB_POLICIES:
            return f"tab policy {tab_policy!r} is not allowed"
        if tab_policy in {"allow-new-tab", "force-new-tab"}:
            if not new_tab_reason:
                return f"{tab_policy} requires a critical new-tab reason"
            if new_tab_reason not in ALLOWED_NEW_TAB_REASONS:
                return f"new-tab reason {new_tab_reason!r} is not allowed"
        if tab_policy == "reuse-primary" and new_tab_reason:
            return "reuse-primary cannot open a new tab"
        return ""

    def _tab_prelude(self, goal_id, cdp_url, tab_policy, new_tab_reason):
        return (
            f"GOAL_ID = {json.dumps(self._safe_goal_id(goal_id))}\n"
            f"CDP_URL = {json.dumps(cdp_url)}\n"
            f"TAB_POLICY = {json.dumps(tab_policy)}\n"
            f"NEW_TAB_REASON = {json.dumps(new_tab_reason or '')}\n"
            "def _tab_id(tab):\n"
            "    if isinstance(tab, dict):\n"
            "        return str(tab.get('targetId') or tab.get('id') or tab.get('target_id') or '')\n"
            "    return str(tab or '')\n"
            "def _tab_url(tab):\n"
            "    if isinstance(tab, dict):\n"
            "        return str(tab.get('url') or '')\n"
            "    return ''\n"
            "def _record_current(lifecycle, suffix):\n"
            "    try:\n"
            "        tab = current_tab()\n"
            "        lifecycle['primaryTargetId'] = lifecycle.get('primaryTargetId') or _tab_id(tab)\n"
            "        lifecycle['primaryTabUrl' + suffix] = _tab_url(tab)\n"
            "        return tab\n"
            "    except Exception as e:\n"
            "        lifecycle.setdefault('blockedNewTabAttempts', []).append({'reason': 'current_tab_failed', 'detail': str(e)})\n"
            "        return None\n"
        )

    def _capture_script(self, target_url, wait_timeout, screenshot_path, goal_id, cdp_url, tab_policy, new_tab_reason):
        """Build the Python script piped to the engine over stdin (heredoc surface).

        Uses only CONFIRMED helper names. The script:
        - drains+discards stale buffered events (the daemon event buffer is global
          and shared), then ensures a real tab and navigates with goto_url(),
        - waits for load, reads page_info(), captures a screenshot, reads
          localStorage/sessionStorage and a bounded DOM snapshot via js(),
        - drains the freshly-produced events (network/console) filtered to the
          owned session where possible,
        - prints a single GSD_CAPTURE_RESULT line with a JSON payload,
        - ALWAYS closes the owned tab and stops the run-scoped daemon in `finally`.
        """
        # json.dumps gives safe Python string literals for embedding.
        return (
            "import json\n"
            + self._tab_prelude(goal_id, cdp_url, tab_policy, new_tab_reason) +
            "result = {\"channels\": {}, \"errors\": [], \"tabLifecycle\": {\"goalId\": GOAL_ID, \"tabPolicy\": TAB_POLICY, \"reusePolicy\": \"single-primary-tab\", \"primaryTargetId\": \"\", \"primaryTabUrlBefore\": \"\", \"primaryTabUrlAfter\": \"\", \"openedNewTabs\": [], \"closedExtraTabs\": [], \"preservedTabs\": [], \"newTabReasons\": ([NEW_TAB_REASON] if NEW_TAB_REASON else []), \"blockedNewTabAttempts\": [], \"tabDecisionEvidenceStatus\": \"Confirmed\"}}\n"
            "owned_tab = None\n"
            "try:\n"
            "    try:\n"
            "        # The daemon event buffer is global and shared across tabs; we\n"
            "        # drain-to-clear before navigation, then drain-to-collect after,\n"
            "        # to bound the events to our navigation window. Per-session\n"
            "        # filtering is not available from the public helper surface\n"
            "        # (_send is private), so cross-tab leakage in the window is a\n"
            "        # recorded honest caveat rather than a hard guarantee.\n"
            "        drain_events()  # discard stale/global buffer before our navigation\n"
            "        try:\n"
            "            result['tabLifecycle']['preservedTabs'] = list_tabs()\n"
            "        except Exception as e:\n"
            "            result['errors'].append('list_tabs: ' + str(e))\n"
            "        ensure_real_tab()\n"
            "        primary_before = _record_current(result['tabLifecycle'], 'Before')\n"
            "        if TAB_POLICY in ('allow-new-tab', 'force-new-tab') and NEW_TAB_REASON:\n"
            f"            owned_tab = new_tab({json.dumps(target_url)})\n"
            "            result['ownedTab'] = owned_tab\n"
            "            result['tabLifecycle']['openedNewTabs'].append({'targetId': _tab_id(owned_tab), 'reason': NEW_TAB_REASON})\n"
            "        else:\n"
            f"            goto_url({json.dumps(target_url)})\n"
            "            result['ownedTab'] = None\n"
            "        try:\n"
            "            result[\"currentTab\"] = current_tab()\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"current_tab: \" + str(e))\n"
            f"        loaded = wait_for_load(timeout={float(wait_timeout)})\n"
            "        result[\"loaded\"] = bool(loaded)\n"
            "        try:\n"
            "            result[\"channels\"][\"pageInfo\"] = page_info()\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"page_info: \" + str(e))\n"
            "        try:\n"
            f"            shot = capture_screenshot({json.dumps(screenshot_path)})\n"
            "            result[\"channels\"][\"screenshotPath\"] = shot\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"screenshot: \" + str(e))\n"
            "        try:\n"
            "            storage = js(\"JSON.stringify({local:Object.fromEntries(Object.entries(localStorage)),session:Object.fromEntries(Object.entries(sessionStorage))})\")\n"
            "            result[\"channels\"][\"storage\"] = json.loads(storage) if storage else {\"local\": {}, \"session\": {}}\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"storage: \" + str(e))\n"
            "        try:\n"
            "            dom = js(\"document.documentElement.outerHTML\")\n"
            "            result[\"channels\"][\"domSnapshot\"] = dom[:200000] if isinstance(dom, str) else None\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"dom: \" + str(e))\n"
            "        try:\n"
            "            events = drain_events()\n"
            "            net = []\n"
            "            console = []\n"
            "            for ev in events:\n"
            "                method = ev.get(\"method\", \"\")\n"
            "                if method.startswith(\"Network.\"):\n"
            "                    net.append(ev)\n"
            "                elif method in (\"Runtime.consoleAPICalled\", \"Runtime.exceptionThrown\", \"Log.entryAdded\"):\n"
            "                    console.append(ev)\n"
            "            result[\"channels\"][\"network\"] = net[:500]\n"
            "            result[\"channels\"][\"console\"] = console[:500]\n"
            "            result[\"channels\"][\"sessionFiltered\"] = False\n"
            "        except Exception as e:\n"
            "            result[\"errors\"].append(\"events: \" + str(e))\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"capture: \" + str(e))\n"
            "finally:\n"
            "    try:\n"
            "        if owned_tab is not None:\n"
            "            close_tab(owned_tab)\n"
            "            result['tabLifecycle']['closedExtraTabs'].append({'targetId': _tab_id(owned_tab), 'reason': 'run-owned-extra-tab'})\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"close_tab: \" + str(e))\n"
            "    _record_current(result['tabLifecycle'], 'After')\n"
            "    try:\n"
            "        restart_daemon()  # stop the run-scoped daemon we caused to start\n"
            "        result[\"daemonStopped\"] = True\n"
            "    except Exception as e:\n"
            "        result[\"daemonStopped\"] = False\n"
            "        result[\"errors\"].append(\"restart_daemon: \" + str(e))\n"
            f"    print({json.dumps(CAPTURE_RESULT_MARKER)} + json.dumps(result))\n"
        )

    def capture(self, target_url, run_env, screenshot_path, wait_timeout=15.0,
                goal_id="manual", cdp_url="", tab_policy="reuse-primary", new_tab_reason=""):
        """Drive one bounded real capture through the engine over stdin/heredoc.

        Returns a dict:
          {"ok": bool, "result": <parsed engine JSON or None>,
           "exitCode": int, "stderr": str, "note": str, "command": [...]}
        Never raises for engine failures; the wrapper records honest partial/blocked.
        The subprocess is timeout-bounded, runs with cwd=ROOT, no shell=True, and
        is handed a full-env merge (os.environ + run-scoped vars) so PATH/SystemRoot
        survive on Windows while BU_NAME/BH_RUNTIME_DIR scope the daemon to the run.
        """
        tab_policy = tab_policy or self._tab_config().get("defaultPolicy", "reuse-primary")
        tab_error = self._validate_tab_request(tab_policy, new_tab_reason or "")
        session_state = self._load_session_state(goal_id, cdp_url)
        default_lifecycle = self._default_tab_lifecycle(goal_id, cdp_url, tab_policy, new_tab_reason)
        if tab_error:
            default_lifecycle["blockedNewTabAttempts"].append({"reason": "invalid-tab-policy", "detail": tab_error})
            return {
                "ok": False,
                "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle,
                "exitCode": None,
                "stderr": "",
                "note": tab_error,
                "command": None,
            }

        strategy = self.resolve_strategy(auto_bootstrap=True)
        command = strategy.get("command")
        if not strategy.get("available") or not command:
            return {
                "ok": False,
                "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle,
                "exitCode": None,
                "stderr": "",
                "note": "no invocable engine command resolved for capture",
                "command": command,
            }

        script = self._capture_script(target_url, wait_timeout, screenshot_path, goal_id, cdp_url, tab_policy, new_tab_reason or "")
        merged_env = self._strategy_env(strategy, run_env)
        try:
            proc = subprocess.run(
                list(command),
                input=script,
                cwd=str(self.root),
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
                env=merged_env,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle,
                "exitCode": None,
                "stderr": "",
                "note": f"engine capture timed out after {self.timeout_seconds}s",
                "command": list(command),
            }
        except OSError as exc:
            return {
                "ok": False,
                "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle,
                "exitCode": None,
                "stderr": "",
                "note": f"engine capture failed to launch: {exc}",
                "command": list(command),
            }

        parsed = None
        for line in proc.stdout.splitlines():
            if line.startswith(CAPTURE_RESULT_MARKER):
                try:
                    parsed = json.loads(line[len(CAPTURE_RESULT_MARKER):])
                except json.JSONDecodeError:
                    parsed = None
                break

        tab_lifecycle = default_lifecycle
        if isinstance(parsed, dict) and isinstance(parsed.get("tabLifecycle"), dict):
            tab_lifecycle.update(parsed["tabLifecycle"])
            self._save_session_state(goal_id, session_state, tab_lifecycle)

        ok = proc.returncode == 0 and parsed is not None and bool(parsed.get("loaded"))
        note = "engine capture completed"
        if proc.returncode != 0:
            note = f"engine capture exited {proc.returncode}"
        elif parsed is None:
            note = "engine capture produced no parseable result marker"
        elif not parsed.get("loaded"):
            note = "engine capture ran but the target did not reach load-complete"
        return {
            "ok": ok,
            "result": parsed,
            "tabLifecycle": tab_lifecycle,
            "exitCode": proc.returncode,
            "stderr": (proc.stderr or "").strip(),
            "note": note,
            "command": list(command),
        }

    # -- ordered-action replay driver ----------------------------------------
    #
    # `capture()` runs a fixed script and cannot drive ordered plan steps, so
    # replay needs a bounded ordered-action driver. It keeps the same capture
    # lifecycle guarantees (run-scoped env, timeout-bounded subprocess, no
    # shell=True, owned-tab close + restart_daemon() in `finally`). MVP actions
    # are implemented ONLY via CONFIRMED helpers (ensure_real_tab/current_tab/
    # list_tabs/goto_url/wait/
    # wait_for_load/page_info/capture_screenshot/js); unsupported actions are
    # reported back as outcome "unsupported" (the wrapper marks them
    # failed/partial, never Confirmed). Per-step outcomes are returned; the
    # wrapper preserves each plan step's evidence_status (downgrade-only).

    SUPPORTED_ACTIONS = (
        "navigate", "wait", "wait_for_load", "wait_for_url",
        "wait_for_text", "screenshot", "assert_text",
    )

    def _replay_script(self, base_url, steps, screenshot_dir, goal_id, cdp_url, tab_policy, new_tab_reason):
        """Build the ordered-action replay script piped to the engine over stdin.

        Drives the plan steps in order using CONFIRMED helpers only and prints a
        single GSD_CAPTURE_RESULT line with per-step results + captured channels.
        Unsupported actions are recorded with outcome "unsupported" (no fake
        success). The owned tab is closed and the run-scoped daemon stopped in
        `finally`, matching the capture lifecycle.
        """
        # Embed structured inputs as JSON *strings* parsed inside the script, so
        # JSON null/true/false do not leak as invalid Python identifiers.
        return (
            "import json, time\n"
            + self._tab_prelude(goal_id, cdp_url, tab_policy, new_tab_reason) +
            f"BASE_URL = json.loads({json.dumps(json.dumps(base_url))})\n"
            f"STEPS = json.loads({json.dumps(json.dumps(steps))})\n"
            f"SHOT_DIR = json.loads({json.dumps(json.dumps(screenshot_dir))})\n"
            f"SUPPORTED = json.loads({json.dumps(json.dumps(list(self.SUPPORTED_ACTIONS)))})\n"
            "result = {\"steps\": [], \"channels\": {}, \"errors\": [], \"loaded\": False, \"tabLifecycle\": {\"goalId\": GOAL_ID, \"tabPolicy\": TAB_POLICY, \"reusePolicy\": \"single-primary-tab\", \"primaryTargetId\": \"\", \"primaryTabUrlBefore\": \"\", \"primaryTabUrlAfter\": \"\", \"openedNewTabs\": [], \"closedExtraTabs\": [], \"preservedTabs\": [], \"newTabReasons\": ([NEW_TAB_REASON] if NEW_TAB_REASON else []), \"blockedNewTabAttempts\": [], \"tabDecisionEvidenceStatus\": \"Confirmed\"}}\n"
            "owned_tab = None\n"
            "def _resolve(target):\n"
            "    t = target or \"\"\n"
            "    if t.startswith(\"http://\") or t.startswith(\"https://\"):\n"
            "        return t\n"
            "    if not t:\n"
            "        return BASE_URL\n"
            "    if not t.startswith(\"/\"):\n"
            "        t = \"/\" + t\n"
            "    return BASE_URL.rstrip(\"/\") + t\n"
            "def _body_text():\n"
            "    try:\n"
            "        return js(\"document.body ? document.body.innerText : ''\") or \"\"\n"
            "    except Exception:\n"
            "        return \"\"\n"
            "try:\n"
            "    try:\n"
            "        drain_events()\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"drain_pre: \" + str(e))\n"
            "    try:\n"
            "        result['tabLifecycle']['preservedTabs'] = list_tabs()\n"
            "    except Exception as e:\n"
            "        result['errors'].append('list_tabs: ' + str(e))\n"
            "    ensure_real_tab()\n"
            "    _record_current(result['tabLifecycle'], 'Before')\n"
            "    for idx, step in enumerate(STEPS):\n"
            "        sid = step.get(\"step_id\") or (\"step-\" + str(idx + 1))\n"
            "        action = step.get(\"action\")\n"
            "        target = step.get(\"target\")\n"
            "        value = step.get(\"value\")\n"
            "        timeout_ms = step.get(\"timeout_ms\") or 10000\n"
            "        timeout_s = float(timeout_ms) / 1000.0\n"
            "        entry = {\"stepId\": sid, \"action\": action, \"outcome\": \"failed\", \"detail\": \"\"}\n"
            "        try:\n"
            "            if action not in SUPPORTED:\n"
            "                entry[\"outcome\"] = \"unsupported\"\n"
            "                entry[\"detail\"] = \"action is not in the replay MVP set\"\n"
            "            elif action == \"navigate\":\n"
            "                url = _resolve(target)\n"
            "                if TAB_POLICY in ('allow-new-tab', 'force-new-tab') and NEW_TAB_REASON and owned_tab is None:\n"
            "                    owned_tab = new_tab(url)\n"
            "                    result['tabLifecycle']['openedNewTabs'].append({'targetId': _tab_id(owned_tab), 'reason': NEW_TAB_REASON})\n"
            "                else:\n"
            "                    goto_url(url)\n"
            "                loaded = wait_for_load(timeout=timeout_s)\n"
            "                result[\"loaded\"] = result[\"loaded\"] or bool(loaded)\n"
            "                entry[\"outcome\"] = \"passed\" if loaded else \"partial\"\n"
            "                entry[\"detail\"] = url\n"
            "            elif action == \"wait\":\n"
            "                secs = float(value) if value not in (None, \"\") else 1.0\n"
            "                wait(secs)\n"
            "                entry[\"outcome\"] = \"passed\"\n"
            "                entry[\"detail\"] = \"waited \" + str(secs) + \"s\"\n"
            "            elif action == \"wait_for_load\":\n"
            "                loaded = wait_for_load(timeout=timeout_s)\n"
            "                entry[\"outcome\"] = \"passed\" if loaded else \"partial\"\n"
            "            elif action == \"wait_for_url\":\n"
            "                deadline = time.time() + timeout_s\n"
            "                needle = target or \"\"\n"
            "                seen = \"\"\n"
            "                hit = False\n"
            "                while time.time() < deadline:\n"
            "                    try:\n"
            "                        seen = (page_info() or {}).get(\"url\", \"\")\n"
            "                    except Exception:\n"
            "                        seen = \"\"\n"
            "                    if needle in seen:\n"
            "                        hit = True\n"
            "                        break\n"
            "                    time.sleep(0.2)\n"
            "                entry[\"outcome\"] = \"passed\" if hit else \"failed\"\n"
            "                entry[\"detail\"] = \"url=\" + str(seen)\n"
            "            elif action == \"wait_for_text\":\n"
            "                deadline = time.time() + timeout_s\n"
            "                needle = value or target or \"\"\n"
            "                hit = False\n"
            "                while time.time() < deadline:\n"
            "                    if needle in _body_text():\n"
            "                        hit = True\n"
            "                        break\n"
            "                    time.sleep(0.2)\n"
            "                entry[\"outcome\"] = \"passed\" if hit else \"failed\"\n"
            "            elif action == \"screenshot\":\n"
            "                path = SHOT_DIR + \"/\" + sid + \".png\"\n"
            "                shot = capture_screenshot(path)\n"
            "                entry[\"outcome\"] = \"passed\" if shot else \"partial\"\n"
            "                entry[\"detail\"] = \"screenshots/\" + sid + \".png\"\n"
            "                result[\"channels\"].setdefault(\"screenshots\", []).append(sid + \".png\")\n"
            "            elif action == \"assert_text\":\n"
            "                needle = value or target or \"\"\n"
            "                present = needle in _body_text()\n"
            "                entry[\"outcome\"] = \"passed\" if present else \"failed\"\n"
            "                entry[\"detail\"] = \"assert \" + json.dumps(needle) + \" present=\" + str(present)\n"
            "        except Exception as e:\n"
            "            entry[\"outcome\"] = \"failed\"\n"
            "            entry[\"detail\"] = str(e)\n"
            "            result[\"errors\"].append(sid + \": \" + str(e))\n"
            "        result[\"steps\"].append(entry)\n"
            "    try:\n"
            "        result[\"channels\"][\"pageInfo\"] = page_info()\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"page_info: \" + str(e))\n"
            "    try:\n"
            "        events = drain_events()\n"
            "        net = []\n"
            "        console = []\n"
            "        for ev in events:\n"
            "            method = ev.get(\"method\", \"\")\n"
            "            if method.startswith(\"Network.\"):\n"
            "                net.append(ev)\n"
            "            elif method in (\"Runtime.consoleAPICalled\", \"Runtime.exceptionThrown\", \"Log.entryAdded\"):\n"
            "                console.append(ev)\n"
            "        result[\"channels\"][\"network\"] = net[:500]\n"
            "        result[\"channels\"][\"console\"] = console[:500]\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"events: \" + str(e))\n"
            "finally:\n"
            "    try:\n"
            "        if owned_tab is not None:\n"
            "            close_tab(owned_tab)\n"
            "            result['tabLifecycle']['closedExtraTabs'].append({'targetId': _tab_id(owned_tab), 'reason': 'run-owned-extra-tab'})\n"
            "    except Exception as e:\n"
            "        result[\"errors\"].append(\"close_tab: \" + str(e))\n"
            "    _record_current(result['tabLifecycle'], 'After')\n"
            "    try:\n"
            "        restart_daemon()\n"
            "        result[\"daemonStopped\"] = True\n"
            "    except Exception as e:\n"
            "        result[\"daemonStopped\"] = False\n"
            "        result[\"errors\"].append(\"restart_daemon: \" + str(e))\n"
            f"    print({json.dumps(CAPTURE_RESULT_MARKER)} + json.dumps(result))\n"
        )

    def replay(self, base_url, steps, screenshot_dir, goal_id="manual", cdp_url="",
               tab_policy="reuse-primary", new_tab_reason=""):
        """Drive ordered replay steps through the engine over stdin/heredoc.

        Returns a dict mirroring capture(): {"ok", "result", "exitCode",
        "stderr", "note", "command"}. Never raises for engine failures.
        """
        tab_policy = tab_policy or self._tab_config().get("defaultPolicy", "reuse-primary")
        tab_error = self._validate_tab_request(tab_policy, new_tab_reason or "")
        session_state = self._load_session_state(goal_id, cdp_url)
        default_lifecycle = self._default_tab_lifecycle(goal_id, cdp_url, tab_policy, new_tab_reason)
        if tab_error:
            default_lifecycle["blockedNewTabAttempts"].append({"reason": "invalid-tab-policy", "detail": tab_error})
            return {
                "ok": False, "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle, "exitCode": None, "stderr": "",
                "note": tab_error, "command": None,
            }

        strategy = self.resolve_strategy(auto_bootstrap=True)
        command = strategy.get("command")
        if not strategy.get("available") or not command:
            return {
                "ok": False,
                "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle,
                "exitCode": None,
                "stderr": "",
                "note": "no invocable engine command resolved for replay",
                "command": command,
            }

        script = self._replay_script(base_url, steps, screenshot_dir, goal_id, cdp_url, tab_policy, new_tab_reason or "")
        merged_env = self._strategy_env(strategy)
        try:
            proc = subprocess.run(
                list(command),
                input=script,
                cwd=str(self.root),
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
                env=merged_env,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False, "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle, "exitCode": None, "stderr": "",
                "note": f"engine replay timed out after {self.timeout_seconds}s",
                "command": list(command),
            }
        except OSError as exc:
            return {
                "ok": False, "result": {"tabLifecycle": default_lifecycle},
                "tabLifecycle": default_lifecycle, "exitCode": None, "stderr": "",
                "note": f"engine replay failed to launch: {exc}",
                "command": list(command),
            }

        parsed = None
        for line in proc.stdout.splitlines():
            if line.startswith(CAPTURE_RESULT_MARKER):
                try:
                    parsed = json.loads(line[len(CAPTURE_RESULT_MARKER):])
                except json.JSONDecodeError:
                    parsed = None
                break

        tab_lifecycle = default_lifecycle
        if isinstance(parsed, dict) and isinstance(parsed.get("tabLifecycle"), dict):
            tab_lifecycle.update(parsed["tabLifecycle"])
            self._save_session_state(goal_id, session_state, tab_lifecycle)

        ok = proc.returncode == 0 and parsed is not None
        note = "engine replay completed"
        if proc.returncode != 0:
            note = f"engine replay exited {proc.returncode}"
        elif parsed is None:
            note = "engine replay produced no parseable result marker"
        return {
            "ok": ok,
            "result": parsed,
            "tabLifecycle": tab_lifecycle,
            "exitCode": proc.returncode,
            "stderr": (proc.stderr or "").strip(),
            "note": note,
            "command": list(command),
        }
