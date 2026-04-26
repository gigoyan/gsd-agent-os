# Tool Capability Registry

## Blocked Commands
| Command | Reason | Approved Alternative | Date | Evidence |
| --- | --- | --- | --- | --- |
| rg / rg.exe | Discoverable but not executable in this environment | PowerShell-native search: Get-ChildItem + Select-String | YYYY-MM-DD | rg.exe failed during repo execution |

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