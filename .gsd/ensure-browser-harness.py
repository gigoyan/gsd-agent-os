#!/usr/bin/env python
"""Ensure the pinned Browser Harness engine is available outside the repo."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / ".gsd" / "browser-harness.lock.json"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or install the pinned Browser Harness engine into a user cache."
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--install", action="store_true", help="Install into the user cache when missing.")
    action.add_argument("--check-only", action="store_true", help="Check PATH/cache without installing.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--lock-path", default=str(DEFAULT_LOCK), help="Browser Harness lock file path.")
    parser.add_argument("--cache-root", default="", help="Override cache root for tests or controlled setups.")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Install command timeout.")
    return parser.parse_args(argv)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_lock(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"could not read Browser Harness lock {path}: {exc}")
    required = ("engine", "repository", "revision", "version", "cacheNamespace", "pythonModule")
    missing = [key for key in required if not data.get(key)]
    if missing:
        fail("Browser Harness lock is missing required keys: " + ", ".join(missing))
    return data


def user_cache_root(lock: dict[str, Any], override: str = "") -> Path:
    if override:
        return Path(override).expanduser().resolve()
    explicit = os.environ.get("GSD_BROWSER_HARNESS_CACHE")
    if explicit:
        return Path(explicit).expanduser().resolve()
    namespace = Path(*str(lock["cacheNamespace"]).split("/"))
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return (base / namespace).resolve()
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return (base / namespace).resolve()


def safe_remove(path: Path, root: Path) -> None:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError:
        fail(f"refusing to remove path outside cache root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def run(command: list[str], cwd: Path | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def version_ok(raw: str, expected: str) -> bool:
    return bool(expected) and expected in (raw or "")


def path_engine(lock: dict[str, Any], timeout: int) -> dict[str, Any] | None:
    command_name = str(lock.get("entrypoint") or "browser-harness")
    resolved = shutil.which(command_name)
    if not resolved:
        return None
    result = run([command_name, "--version"], timeout=timeout)
    version = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return None
    if not version_ok(version, str(lock["version"])):
        return {
            "available": False,
            "strategy": "path",
            "source": resolved,
            "version": version,
            "blocker": f"PATH browser-harness version does not match pinned {lock['version']}",
        }
    return {
        "available": True,
        "strategy": "path",
        "source": resolved,
        "command": [command_name],
        "version": version,
        "installed": False,
    }


def cache_paths(lock: dict[str, Any], cache_root: Path) -> dict[str, Path]:
    revision = str(lock["revision"])
    target = cache_root / revision
    return {
        "target": target,
        "source": target / "source",
        "venv": target / "venv",
        "python": venv_python(target / "venv"),
    }


def cached_engine(lock: dict[str, Any], cache_root: Path, timeout: int) -> dict[str, Any] | None:
    paths = cache_paths(lock, cache_root)
    python = paths["python"]
    source = paths["source"]
    if not python.is_file() or not source.is_dir():
        return None
    module = str(lock["pythonModule"])
    result = run([str(python), "-m", module, "--version"], timeout=timeout)
    version = (result.stdout or result.stderr).strip()
    if result.returncode != 0 or not version_ok(version, str(lock["version"])):
        return {
            "available": False,
            "strategy": "cache",
            "source": str(source),
            "version": version,
            "blocker": "cached Browser Harness exists but failed pinned version verification",
        }
    return {
        "available": True,
        "strategy": "cache",
        "source": str(source),
        "command": [str(python), "-m", module],
        "version": version,
        "installed": False,
        "cacheRoot": str(cache_root),
        "revision": str(lock["revision"]),
    }


def install_engine(lock: dict[str, Any], cache_root: Path, timeout: int) -> dict[str, Any]:
    git = shutil.which("git")
    if not git:
        return {"available": False, "strategy": "cache", "blocker": "git is required to install Browser Harness"}

    paths = cache_paths(lock, cache_root)
    target = paths["target"]
    source = paths["source"]
    venv = paths["venv"]
    cache_root.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)

    if not source.is_dir():
        temp_source = Path(tempfile.mkdtemp(prefix="source-", dir=str(target)))
        try:
            result = run([git, "clone", str(lock["repository"]), str(temp_source)], timeout=timeout)
            if result.returncode != 0:
                return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}
            result = run([git, "-C", str(temp_source), "checkout", str(lock["revision"])], timeout=timeout)
            if result.returncode != 0:
                return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}
            temp_source.replace(source)
        finally:
            if temp_source.exists():
                safe_remove(temp_source, target)
    else:
        result = run([git, "-C", str(source), "rev-parse", "HEAD"], timeout=timeout)
        current_revision = result.stdout.strip() if result.returncode == 0 else ""
        if current_revision != str(lock["revision"]):
            result = run([git, "-C", str(source), "fetch", "--all", "--tags"], timeout=timeout)
            if result.returncode != 0:
                return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}
            result = run([git, "-C", str(source), "checkout", str(lock["revision"])], timeout=timeout)
            if result.returncode != 0:
                return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}

    python = paths["python"]
    if not python.is_file():
        result = run([sys.executable, "-m", "venv", str(venv)], timeout=timeout)
        if result.returncode != 0:
            return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}

    result = run([str(python), "-m", "pip", "install", "-e", str(source)], timeout=timeout)
    if result.returncode != 0:
        return {"available": False, "strategy": "cache", "blocker": result.stderr.strip() or result.stdout.strip()}

    verified = cached_engine(lock, cache_root, timeout)
    if verified and verified.get("available"):
        verified["installed"] = True
        return verified
    return verified or {"available": False, "strategy": "cache", "blocker": "install completed but verification failed"}


def payload(lock: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    cache_root = user_cache_root(lock, args.cache_root)
    timeout = max(1, args.timeout_seconds)
    path = path_engine(lock, timeout)
    if path and path.get("available"):
        return {**path, "lock": lock, "cacheRoot": str(cache_root), "status": "passed", "blockers": []}

    cache = cached_engine(lock, cache_root, timeout)
    if cache and cache.get("available"):
        return {**cache, "lock": lock, "status": "passed", "blockers": []}

    blockers = []
    for candidate in (path, cache):
        if candidate and candidate.get("blocker"):
            blockers.append(str(candidate["blocker"]))

    if args.install:
        installed = install_engine(lock, cache_root, timeout)
        if installed.get("available"):
            return {**installed, "lock": lock, "status": "passed", "blockers": []}
        blockers.append(str(installed.get("blocker") or "install failed"))

    if not blockers:
        blockers.append("Browser Harness is not available on PATH or in the GSD user cache")
    return {
        "available": False,
        "strategy": "none",
        "source": None,
        "command": None,
        "version": None,
        "installed": False,
        "cacheRoot": str(cache_root),
        "revision": str(lock["revision"]),
        "lock": lock,
        "status": "blocked",
        "blockers": blockers,
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    lock = load_lock(Path(args.lock_path).resolve())
    result = payload(lock, args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if result.get("available"):
            print(f"Browser Harness available via {result.get('strategy')}: {result.get('source')}")
        else:
            print("Browser Harness unavailable: " + "; ".join(result.get("blockers", [])))
    return 0 if result.get("available") else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
