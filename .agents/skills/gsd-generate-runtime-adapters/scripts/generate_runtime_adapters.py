#!/usr/bin/env python3
"""Generate project-local GSD runtime adapter outputs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VALID_TARGETS = {"codex", "claude_code", "both"}
HIGH_RISK_SKILLS = {
    "gsd-sync-blueprint",
    "gsd-export-blueprint-package",
    "gsd-export-project-context",
}
READ_ONLY_SKILLS = {"gsd-memory-lookup"}
DEFAULT_VALUES = {
    "backend_scope": "the selected backend service scope",
    "authoring_mode_label": "Unknown",
    "service_architecture_label": "Unknown",
    "http_framework": "fastify",
    "http_framework_label": "Fastify",
    "repo_shape_label": "Unknown",
    "nodejs_backend_baseline": "Follow the selected Node.js backend profile baseline.",
    "selected_variant_overlays": "No additional variant overlays were provided.",
    "framework_overlay": "Apply the selected HTTP framework conventions.",
    "verification_commands": "Use the validation commands captured in the stack-selection artifact.",
}


@dataclass
class ReportItem:
    status: str
    path: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Project GSD runtime adapter outputs for codex, claude_code, or both."
    )
    parser.add_argument("--target", required=True, choices=sorted(VALID_TARGETS))
    parser.add_argument(
        "--profile-assets",
        default=".agents/stack-profiles/backend/nodejs-service/assets",
        help="Directory containing output-manifest.toml and project-local templates.",
    )
    parser.add_argument(
        "--output-root",
        default=".",
        help="Project root where generated runtime adapter outputs should be written.",
    )
    parser.add_argument(
        "--selection-file",
        help="Optional stack-selection/configuration-package artifact to scan for simple values.",
    )
    parser.add_argument(
        "--var",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Template render value. May be repeated.",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing differing files.")
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair missing Claude Code runtime adapter files before falling back to canonical GSD sources.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report.")
    return parser.parse_args()


def load_manifest(profile_assets: Path) -> dict:
    manifest_path = profile_assets / "output-manifest.toml"
    if not manifest_path.exists():
        raise SystemExit(f"missing output manifest: {manifest_path}")
    return tomllib.loads(manifest_path.read_text(encoding="utf-8"))


def load_values(selection_file: str | None, explicit_vars: Iterable[str]) -> dict[str, str]:
    values = dict(DEFAULT_VALUES)
    if selection_file:
        selection_path = Path(selection_file)
        if not selection_path.exists():
            raise SystemExit(f"selection file not found: {selection_path}")
        text = selection_path.read_text(encoding="utf-8")
        values.update(extract_selection_values(text))
    for item in explicit_vars:
        if "=" not in item:
            raise SystemExit(f"--var must use KEY=VALUE: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"--var key cannot be empty: {item}")
        values[key] = value.strip()
    if "http_framework_label" not in values or values["http_framework_label"] == "Unknown":
        values["http_framework_label"] = labelize(values.get("http_framework", "unknown"))
    return values


def extract_selection_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pairs = {
        "http_framework": [r"HTTP framework:\s*`?([A-Za-z0-9_-]+)`?", r"http_framework:\s*([A-Za-z0-9_-]+)"],
        "authoring_mode_label": [r"Authoring mode:\s*(.+)"],
        "service_architecture_label": [r"Service architecture:\s*(.+)"],
        "repo_shape_label": [r"Repository shape:\s*(.+)"],
        "backend_scope": [r"Backend scope:\s*(.+)"],
    }
    for key, patterns in pairs.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                values[key] = cleanup_value(match.group(1))
                break
    if "http_framework" in values:
        values["http_framework_label"] = labelize(values["http_framework"])
    return values


def cleanup_value(value: str) -> str:
    return value.strip().strip("`").strip()


def labelize(value: str) -> str:
    if value.lower() == "node-core-http":
        return "Node core HTTP"
    return value.replace("_", " ").replace("-", " ").title()


def expand_targets(target: str) -> list[str]:
    if target == "both":
        return ["codex", "claude_code"]
    return [target]


def should_generate_role(role: dict, values: dict[str, str]) -> bool:
    apply_when = role.get("apply_when", "always")
    if apply_when == "always":
        return True
    if apply_when == "http_framework in ['fastify', 'express']":
        return values.get("http_framework", "").lower() in {"fastify", "express"}
    return False


def render_template(text: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return values.get(key, f"Unknown {key}")

    return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", replace, text)


def write_or_report(path: Path, content: str, dry_run: bool, force: bool, report: list[ReportItem]) -> None:
    normalized = content.replace("\r\n", "\n")
    rel = path.as_posix()
    if not path.exists():
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(normalized, encoding="utf-8", newline="\n")
        report.append(ReportItem("created", rel, "missing"))
        return
    current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if current == normalized:
        report.append(ReportItem("skipped", rel, "unchanged"))
        return
    if not force:
        report.append(ReportItem("skipped", rel, "exists with different content; use --force to replace"))
        return
    if not dry_run:
        path.write_text(normalized, encoding="utf-8", newline="\n")
    report.append(ReportItem("updated", rel, "forced replacement"))


def write_template_or_report(
    template_path: Path,
    target_path: Path,
    values: dict[str, str],
    args: argparse.Namespace,
    report: list[ReportItem],
) -> None:
    if not template_path.exists():
        report.append(
            ReportItem(
                "missing_prerequisites",
                target_path.as_posix(),
                f"template not found: {template_path.as_posix()}",
            )
        )
        return
    write_or_report(
        target_path,
        render_template(template_path.read_text(encoding="utf-8"), values),
        args.dry_run,
        args.force,
        report,
    )


def generate_codex(profile_assets: Path, output_root: Path, manifest: dict, values: dict[str, str], args: argparse.Namespace, report: list[ReportItem]) -> None:
    generated = manifest["generated_outputs"]
    config_template = profile_assets / generated["codex_config_template"]
    config_target = output_root / generated["targets"]["codex"]["codex_config"]
    write_or_report(config_target, render_template(config_template.read_text(encoding="utf-8"), values), args.dry_run, args.force, report)
    for role in manifest.get("roles", []):
        if not should_generate_role(role, values):
            report.append(ReportItem("skipped", role["targets"]["codex"]["target"], f"condition not met: {role.get('apply_when')}"))
            continue
        target_data = role["targets"]["codex"]
        template_path = profile_assets / target_data["template"]
        target_path = output_root / target_data["target"]
        write_or_report(target_path, render_template(template_path.read_text(encoding="utf-8"), values), args.dry_run, args.force, report)


def generate_claude(profile_assets: Path, output_root: Path, manifest: dict, values: dict[str, str], args: argparse.Namespace, report: list[ReportItem]) -> None:
    generated = manifest["generated_outputs"]
    settings_template = profile_assets / generated["claude_settings_template"]
    settings_target = output_root / generated["targets"]["claude_code"]["settings"]
    write_or_report(settings_target, render_template(settings_template.read_text(encoding="utf-8"), values), args.dry_run, args.force, report)
    for role in manifest.get("roles", []):
        if not should_generate_role(role, values):
            report.append(ReportItem("skipped", role["targets"]["claude_code"]["target"], f"condition not met: {role.get('apply_when')}"))
            continue
        target_data = role["targets"]["claude_code"]
        template_path = profile_assets / target_data["template"]
        target_path = output_root / target_data["target"]
        write_or_report(target_path, render_template(template_path.read_text(encoding="utf-8"), values), args.dry_run, args.force, report)
    project_skills(output_root, args.dry_run, args.force, report)


def generate_claude_repair(profile_assets: Path, output_root: Path, values: dict[str, str], args: argparse.Namespace, report: list[ReportItem]) -> None:
    manifest_path = profile_assets / "output-manifest.toml"
    manifest: dict | None = None
    if manifest_path.exists():
        try:
            manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            reason = f"invalid output manifest: {exc}"
            report.append(ReportItem("blocked", ".claude/settings.json", reason))
            report.append(ReportItem("blocked", ".claude/agents/*.md", reason))
    else:
        reason = f"profile output manifest not found: {manifest_path.as_posix()}"
        report.append(ReportItem("missing_prerequisites", ".claude/settings.json", reason))
        report.append(ReportItem("missing_prerequisites", ".claude/agents/*.md", reason))

    if manifest is not None:
        generated = manifest.get("generated_outputs", {})
        claude_targets = generated.get("targets", {}).get("claude_code", {})

        settings_template_name = generated.get("claude_settings_template")
        settings_target_name = claude_targets.get("settings")
        if settings_template_name and settings_target_name:
            write_template_or_report(
                profile_assets / settings_template_name,
                output_root / settings_target_name,
                values,
                args,
                report,
            )
        else:
            report.append(ReportItem("missing_prerequisites", ".claude/settings.json", "Claude settings template mapping missing from output manifest"))

        roles = manifest.get("roles", [])
        if not roles:
            report.append(ReportItem("missing_prerequisites", ".claude/agents/*.md", "Claude agent role mappings missing from output manifest"))
        for role in roles:
            target_data = role.get("targets", {}).get("claude_code")
            if not target_data:
                role_id = role.get("role_id", "unknown")
                report.append(ReportItem("missing_prerequisites", ".claude/agents/*.md", f"Claude target mapping missing for role: {role_id}"))
                continue
            if not should_generate_role(role, values):
                report.append(ReportItem("skipped", target_data["target"], f"condition not met: {role.get('apply_when')}"))
                continue
            write_template_or_report(
                profile_assets / target_data["template"],
                output_root / target_data["target"],
                values,
                args,
                report,
            )

    project_skills(output_root, args.dry_run, args.force, report, missing_status="missing_prerequisites")


def project_skills(output_root: Path, dry_run: bool, force: bool, report: list[ReportItem], missing_status: str = "skipped") -> None:
    skills_root = Path(".agents/skills")
    if not skills_root.exists():
        report.append(ReportItem(missing_status, ".claude/skills/**/SKILL.md", "canonical .agents/skills directory not found"))
        return
    for source in sorted(skills_root.glob("*/SKILL.md")):
        skill_name = source.parent.name
        target = output_root / ".claude" / "skills" / skill_name / "SKILL.md"
        projected = project_skill(source, skill_name)
        write_or_report(target, projected, dry_run, force, report)


def project_skill(source: Path, skill_name: str) -> str:
    text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
    description, body = split_frontmatter(text)
    legacy_workflow_phrase = "Codex-native" + " GSD workflow"
    legacy_child_agent_prohibition = (
        "Do not call `spawn_" + "agent`, `send_" + "input`, `wait_" + "agent`, or `close_" + "agent`."
    )
    body = body.replace(legacy_workflow_phrase, "GSD coding-agent workflow")
    body = body.replace(
        legacy_child_agent_prohibition,
        "Do not spawn, delegate to, message, wait for, close, or orchestrate other agents. Only the root orchestrator may manage delegated agents.",
    )
    frontmatter = claude_frontmatter(skill_name, description)
    return f"{frontmatter}\n\n{body.strip()}\n"


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            description = "Generated GSD skill."
            for line in parts[1].splitlines():
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')
                    break
            return description, parts[2].lstrip()
    return "Generated GSD skill.", text


def claude_frontmatter(skill_name: str, description: str) -> str:
    if skill_name in HIGH_RISK_SKILLS:
        return "\n".join(
            [
                "---",
                "description: Audit, export, or synchronize GSD workflow assets. Invoke explicitly only.",
                "disable-model-invocation: true",
                "allowed-tools: Read, Glob, Grep, Bash, Edit, Write",
                "---",
            ]
        )
    tools = "Read, Glob, Grep, Bash" if skill_name in READ_ONLY_SKILLS else "Read, Glob, Grep, Bash, Edit, Write"
    safe_description = description.replace("\n", " ").strip() or "Generated GSD skill."
    return "\n".join(["---", f"description: {safe_description}", f"allowed-tools: {tools}", "---"])


def emit_report(report: list[ReportItem], as_json: bool) -> None:
    if as_json:
        print(json.dumps([item.__dict__ for item in report], indent=2, sort_keys=True))
        return
    for item in report:
        print(f"{item.status}\t{item.path}\t{item.reason}")
    totals: dict[str, int] = {}
    for item in report:
        totals[item.status] = totals.get(item.status, 0) + 1
    print("summary\t" + " ".join(f"{key}={totals[key]}" for key in sorted(totals)))


def ensure_safe_output_root(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if not output_root.is_dir():
        raise SystemExit(f"output root is not a directory: {output_root}")


def main() -> int:
    args = parse_args()
    if args.repair and args.target != "claude_code":
        raise SystemExit("--repair is supported only with --target claude_code")
    profile_assets = Path(args.profile_assets)
    output_root = Path(args.output_root)
    ensure_safe_output_root(output_root)
    values = load_values(args.selection_file, args.var)
    report: list[ReportItem] = []
    if args.repair:
        generate_claude_repair(profile_assets, output_root, values, args, report)
        emit_report(report, args.json)
        return 0
    manifest = load_manifest(profile_assets)
    for target in expand_targets(args.target):
        if target == "codex":
            generate_codex(profile_assets, output_root, manifest, values, args, report)
        elif target == "claude_code":
            generate_claude(profile_assets, output_root, manifest, values, args, report)
        else:
            raise SystemExit(f"unsupported target: {target}")
    emit_report(report, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
