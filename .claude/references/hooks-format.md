# Hooks Format Reference

Hooks run shell commands or prompts at lifecycle events.

**Locations:**
- Project: `.claude/settings.json`
- Local (not committed): `.claude/settings.local.json`
- Personal: `~/.claude/settings.json`

---

## settings.json Structure

```json
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<regex>",
        "hooks": [
          {
            "type": "command",
            "command": "shell command here",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

---

## Hook Events

| Event | Matcher Filters | Notes |
|-------|----------------|-------|
| `SessionStart` | `startup`, `resume`, `clear`, `compact` | Fires when session begins |
| `UserPromptSubmit` | — | Fires on every user message |
| `PreToolUse` | Tool name (e.g. `Bash`, `Edit\|Write`) | Before a tool runs |
| `PostToolUse` | Tool name | After a tool succeeds |
| `PostToolUseFailure` | Tool name | After a tool fails |
| `PermissionRequest` | Tool name | When permission is requested |
| `Notification` | `permission_prompt`, `idle_prompt` | On notifications |
| `Stop` | — | When Claude stops responding |
| `PreCompact` | `manual`, `auto` | Before context compaction |
| `SessionEnd` | `clear`, `logout` | When session ends |

---

## Hook Types

| Type | Field | Description |
|------|-------|-------------|
| `command` | `command` | Shell command. stdout → agent context |
| `prompt` | `prompt` | Claude evaluates a prompt |
| `agent` | `prompt` | Subagent with tools evaluates prompt |

---

## Exit Codes (for `command` type)

| Exit Code | Behavior |
|-----------|---------|
| `0` | Success — output added to context |
| `2` | Block — tool call is cancelled |
| other | Error — shown as warning |

---

## Matcher

- Empty string `""` matches all
- Regex pattern matches tool names or event sources
- Example: `"Edit\|Write"` matches Edit or Write tools

---

## Examples

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "cat PLAN.md" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": ".claude/hooks/validate.sh", "timeout": 10 }]
      }
    ]
  }
}
```

---

## Hook Script Pattern

```bash
#!/bin/bash
INPUT=$(cat)  # JSON with tool_input, tool_name, etc.

FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE" == *".env"* ]]; then
  echo "Blocked: .env is protected" >&2
  exit 2  # Block the action
fi

exit 0  # Allow
```
