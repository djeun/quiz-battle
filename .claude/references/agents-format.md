# Agents (Subagents) Format Reference

Agents live at `.claude/agents/<name>/AGENT.md` (project) or `~/.claude/agents/<name>/AGENT.md` (personal).

---

## AGENT.md Structure

```markdown
---
name: my-agent
description: When Claude should delegate to this agent
tools: Read, Glob, Grep, Bash
disallowedTools: Write, Edit
model: sonnet
permissionMode: default
maxTurns: 50
skills:
  - my-skill
background: false
isolation: worktree
---

System prompt for the agent.

You are a specialist in...
```

---

## Frontmatter Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | — | Unique ID: lowercase, hyphens only |
| `description` | Yes | — | When Claude should delegate to this agent |
| `tools` | No | all | Allowed tools list |
| `disallowedTools` | No | — | Tools to deny from inherited list |
| `model` | No | inherit | `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | No | `default` | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | — | Max agentic turns before stopping |
| `skills` | No | — | Skills preloaded into context at startup |
| `background` | No | `false` | Run as background task by default |
| `isolation` | No | — | Set `worktree` for isolated git worktree |
| `hooks` | No | — | Lifecycle hooks scoped to this agent |

---

## permissionMode Values

| Value | Behavior |
|-------|---------|
| `default` | Normal permission prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Skip most permission prompts |
| `bypassPermissions` | Skip all permission prompts |
| `plan` | Plan mode — read-only, no writes |

---

## Example

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use for reviewing PRs and code quality checks.
tools: Read, Glob, Grep
disallowedTools: Write, Edit, Bash
model: sonnet
permissionMode: plan
maxTurns: 30
---

You are a senior code reviewer specializing in quality and security.

Review code for:
- Logic errors
- Security vulnerabilities
- Performance issues
- Code style consistency
```
