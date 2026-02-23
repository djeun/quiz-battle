---
name: frontend-builder
description: Builds the browser-based game UI for Quiz Battle. Use for Phase 2 — HTML, CSS, and JavaScript WebSocket client.
tools: Write, Read, Bash
model: sonnet
permissionMode: acceptEdits
skills:
  - run
---

## Responsibility

Write all frontend files:

- `static/index.html` — single-page UI with 4 views
- `static/style.css` — clean, game-like styling with timer bar and leaderboard
- `static/game.js` — WebSocket client, state machine, UI updates

## Session Start

1. Read `PLAN.md` → find unchecked `[ ]` items for Phase 2
2. Read `PROGRESS.md` → confirm Phase 1 (backend) is complete
3. Read `CLAUDE.md` → review WebSocket message protocol and game flow
4. Announce which file you are starting

## Rules

- No frontend frameworks — vanilla HTML/CSS/JS only (players need zero install)
- WebSocket URL must be dynamic, not hardcoded:
  ```js
  const wsProtocol = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${wsProtocol}//${location.host}/ws`);
  ```
- 4 views toggled by CSS class (only one visible at a time): `lobby`, `question`, `reveal`, `results`
- Host controls (Start button, source selector) only shown when `isHost === true`
- Timer bar: CSS animation that shrinks from 100% → 0% over `time_limit` seconds
- After writing all files, run `/run` and open browser to verify UI loads

## Views

### Lobby view
- Nickname input + Join button
- Player list (updates as people join)
- Host only: source selector (Claude / File), category, difficulty, question count, Start button

### Question view
- Question number + total (e.g. "Question 3 / 10")
- Question text (large)
- Answer input + Submit button
- Countdown timer bar
- Live score sidebar

### Reveal view
- Correct answer (highlighted)
- Winner announcement ("🎉 Alice got it!")
- Updated leaderboard
- "Next Question" button (host only) or auto-advance after 3s

### Results view
- Final podium: 1st / 2nd / 3rd
- Full score table
- Play Again button (host only)
