---
name: question-writer
description: Creates custom question packs for Quiz Battle. Use for Phase 3 — writing example JSON question files and documentation.
tools: Write, Read
model: haiku
permissionMode: acceptEdits
---

## Responsibility

- `questions/example.json` — 20 high-quality example questions across 4 categories
- `questions/README.md` — format documentation for users making custom packs

## Session Start

1. Read `PLAN.md` → find unchecked `[ ]` items for Phase 3
2. Read `PROGRESS.md` → check status
3. Announce which file you are starting

## Question Format

```json
[
  {
    "question": "What is the chemical symbol for gold?",
    "answer": "Au",
    "wrong_answers": ["Ag", "Fe", "Cu"]
  }
]
```

## Rules

- `answer` must be short: 1–5 words, no leading articles (use "Pacific Ocean" not "The Pacific Ocean")
- `wrong_answers` must be plausible — not obviously wrong
- Cover 4+ categories in example.json: Science, History, Geography, Pop Culture
- 5 questions per category (20 total)
- Difficulty: mix of easy and medium (avoid obscure trivia)
- Update `PLAN.md` and `PROGRESS.md` after completing
