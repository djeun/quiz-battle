# Skills Format Reference

Skills live at `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (personal).
Legacy: `.claude/commands/<name>.md` still works but Skills are preferred.

---

## SKILL.md Structure

```markdown
---
name: my-skill
description: What this skill does and when to use it
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Bash
model: haiku
context: fork
agent: Explore
argument-hint: [filename]
---

Skill instructions here.

Use $ARGUMENTS for all args, $0 $1 ... for positional args.
```

---

## Frontmatter Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | No | directory name | Lowercase, hyphens only, max 64 chars |
| `description` | Recommended | — | When to use this skill. Used by Claude for auto-invocation |
| `user-invocable` | No | `true` | Set `false` to hide from `/` menu |
| `disable-model-invocation` | No | `false` | Set `true` to prevent auto-loading |
| `allowed-tools` | No | — | Tools usable without permission prompt |
| `model` | No | inherit | `haiku`, `sonnet`, `opus`, or `inherit` |
| `context` | No | — | Set `fork` to run in isolated subagent |
| `agent` | No | — | Subagent type when `context: fork` |
| `argument-hint` | No | — | Autocomplete hint e.g. `[issue-number]` |
| `hooks` | No | — | Hooks scoped to this skill |

---

## String Substitutions

| Token | Meaning |
|-------|---------|
| `$ARGUMENTS` | All arguments as a string |
| `$0`, `$1`, ... | Positional arguments |
| `$ARGUMENTS[N]` | Argument at index N |
| `${CLAUDE_SESSION_ID}` | Current session ID |

---

## Supporting Files

```
.claude/skills/my-skill/
├── SKILL.md          ← required
├── reference.md      ← optional, reference from SKILL.md
├── examples.md       ← optional
└── scripts/
    └── helper.py     ← optional executable
```

---

## Example

```markdown
---
name: fix-issue
description: Fix a GitHub issue by number
allowed-tools: Read, Bash, Edit
argument-hint: [issue-number]
---

Fix GitHub issue #$ARGUMENTS following our coding standards.

1. Read the issue
2. Implement the fix
3. Write tests
4. Commit
```
