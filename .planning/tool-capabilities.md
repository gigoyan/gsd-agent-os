# Tool Capability Registry

## Blocked Commands
| Command | Reason | Approved Alternative | Date | Evidence |
| --- | --- | --- | --- | --- |
| rg / rg.exe | Discoverable but not executable in this environment | PowerShell-native search: Get-ChildItem + Select-String | YYYY-MM-DD | rg.exe failed during repo execution |
| python | Command is not installed in this environment | `python3` | 2026-06-12 | `python .agents/skills/gsd-clean-blueprint-source/scripts/clean_blueprint_source.py --audit` failed with `command not found` |
| git diff --no-index --label | This Git build reports `unknown option label` | `git diff --no-index --no-ext-diff` without custom labels | 2026-05-20 | `git diff --no-index --no-ext-diff --label ...` failed while generating GSD sync preview |
| PowerShell `[System.Security.Cryptography.SHA256]::HashData(...)` | Current PowerShell/.NET runtime does not expose the static `HashData` method | Use `[System.Security.Cryptography.SHA256]::Create().ComputeHash(...)` | 2026-05-25 | Inline blueprint audit script failed with `does not contain a method named 'HashData'` |

## Rules
- Before using a shell/search/build/test command, check this file.
- If a command is listed under Blocked Commands, do not call it again.
- Use the approved alternative instead.
- If a new command fails because of environment/tooling limits, add it here once with:
  - failed command
  - reason
  - approved fallback
  - evidence
- Do not retry blocked commands unless the user explicitly approves revalidation.
