# PLAN.md — Quiz Battle

---

## Phase 1 — Backend

- [x] `requirements.txt`
- [x] `game.py` — GameState class: player management, question queue, state machine (LOBBY → QUESTION → REVEAL → RESULTS)
- [x] `scorer.py` — points (100 base) + time bonus (up to +50)
- [x] `claude_gen.py` — Claude API question generation (haiku model)
- [x] `server.py` — FastAPI + WebSocket server, routes, broadcast logic

## Phase 2 — Frontend

- [x] `static/index.html` — single-page UI with 4 views: lobby, question, reveal, results
- [x] `static/style.css` — clean game-like styling, timer bar, leaderboard
- [x] `static/game.js` — WebSocket client, state machine, UI updates

## Phase 3 — Questions

- [x] `questions/example.json` — 20 example questions across categories
- [x] `questions/README.md` — custom question pack format documentation

## Phase 4 — Deployment

- [x] `.gitignore`
- [x] `render.yaml` — Render.com deployment config
- [x] README.md — setup instructions + deploy button

## Phase 5 — Polish

- [x] Answer fuzzy matching (normalize articles/punctuation, edit-distance typo tolerance)
- [x] Host can skip a question
- [x] Play again without refreshing
- [x] Reconnect handling if player drops
