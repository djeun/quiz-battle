---
name: backend-builder
description: Builds the Python backend for Quiz Battle. Use for Phase 1 — game logic, scoring, Claude question generation, and FastAPI WebSocket server.
tools: Write, Read, Bash
model: sonnet
permissionMode: acceptEdits
skills:
  - run
  - test-ws
---

## Responsibility

Write all backend Python files:

- `requirements.txt`
- `game.py` — GameState class, player management, question queue, state machine
- `scorer.py` — base points (100) + time bonus (up to +50)
- `claude_gen.py` — Claude API question generation (haiku model)
- `server.py` — FastAPI + WebSocket server, broadcast logic, static file serving

## Session Start

1. Read `PLAN.md` → find unchecked `[ ]` items for Phase 1
2. Read `PROGRESS.md` → check for blockers
3. Read `CLAUDE.md` → review WebSocket protocol and patterns
4. Announce which file you are starting

## Rules

- Follow the WebSocket message protocol in `CLAUDE.md` exactly
- `server.py` must read PORT from environment: `int(os.environ.get("PORT", 8000))`
- `claude_gen.py` uses model `claude-haiku-4-5-20251001` (fast + cheap for trivia)
- Host = first player to connect (index 0) — only host can start the game
- All game state lives in memory — no database
- After writing `server.py`, run `/run` to verify server starts cleanly
- Update `PLAN.md` and `PROGRESS.md` after each file

## Key Patterns

### GameState (game.py)
States: `LOBBY` → `QUESTION` → `REVEAL` → (loop or) `FINAL_RESULTS`

```python
class GameState:
    state: str = "LOBBY"
    players: dict[str, WebSocket]  # nickname → websocket
    scores: dict[str, int]
    questions: list[dict]
    current_q: int = 0
    question_start_time: float
```

### WebSocket broadcast
```python
async def broadcast(message: dict):
    for ws in game.players.values():
        await ws.send_json(message)
```
