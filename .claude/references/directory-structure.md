# Claude Code .claude Directory Structure

```
.claude/
├── settings.json              # Project-level config (hooks, permissions)
├── settings.local.json        # Local config — not committed to git
│
├── skills/                    # Custom slash commands
│   └── <skill-name>/
│       ├── SKILL.md           # Required — skill definition + frontmatter
│       ├── reference.md       # Optional supporting docs
│       └── scripts/           # Optional helper scripts
│
├── agents/                    # Custom subagents
│   └── <agent-name>/
│       └── AGENT.md           # Agent definition + system prompt
│
├── references/                # Reference docs for agents and skills
│   └── *.md                   # Lookup via /lookup-reference skill
│
├── hooks/                     # Hook scripts referenced from settings.json
│   └── *.sh                   # Must be chmod +x
│
└── rules/                     # Modular instruction rules
    └── *.md
```

---

## Scope Hierarchy

```
managed settings  (highest priority)
  ↓
user settings     (~/.claude/settings.json)
  ↓
project settings  (.claude/settings.json)
  ↓
local settings    (.claude/settings.local.json)  ← not committed
```

---

## Skills vs Commands

| | Skills | Legacy Commands |
|-|--------|----------------|
| Location | `.claude/skills/<name>/SKILL.md` | `.claude/commands/<name>.md` |
| Frontmatter | Yes | No |
| Supporting files | Yes | No |
| Auto-invocation | Yes | No |
| Status | **Recommended** | Still works |

---

## Key Files

| File | Purpose |
|------|---------|
| `settings.json` | Hooks, permissions, MCP servers |
| `SKILL.md` | Defines a slash command + behavior |
| `AGENT.md` | Defines a specialized subagent |
| `CLAUDE.md` | Project-level instructions always loaded |

---

## Available References in This Project

| File | Contents |
|------|---------|
| `skills-format.md` | SKILL.md frontmatter fields and examples |
| `agents-format.md` | AGENT.md frontmatter fields and examples |
| `hooks-format.md` | settings.json hooks format and events |
| `directory-structure.md` | This file |
