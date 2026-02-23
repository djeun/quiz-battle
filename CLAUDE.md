# Quiz Battle

Real-time multiplayer quiz game for 3–4 players.
Deployed to Render.com via GitHub — anyone with the URL can join from anywhere, no installation needed.

---

## Agent Collaboration Rules

### MANDATORY: Session Start Checklist

Every agent MUST do this before any other action:

```
1. Read PLAN.md   → understand what has been done and what remains
2. Read PROGRESS.md → check what is in progress and if there are blockers
3. Pick the next unchecked [ ] item in PLAN.md that has no blockers
4. Announce: "Starting: [task name]"
```

**Never start work without reading both files first.**

---

### PLAN.md — What needs to be done
- Full task list organized by phase
- `[ ]` = pending, `[x]` = complete
- Mark items `[x]` immediately after completion

### PROGRESS.md — Current status
- **In Progress**: which agent is doing what
- **Completed**: finished tasks
- **Blockers**: issues preventing progress — always check this first

### Workflow for every task
1. Read `PLAN.md` + `PROGRESS.md`
2. Pick an unchecked `[ ]` item with no blockers
3. Add it to **In Progress** in `PROGRESS.md`
4. Do the work
5. Change `[ ]` → `[x]` in `PLAN.md`
6. Move from In Progress → Completed in `PROGRESS.md`

---

## How It Works

1. Code is pushed to GitHub → Render auto-deploys
2. Share the Render URL (e.g. `https://quiz-battle.onrender.com`) with players
3. Players open that URL in their browser, enter a nickname
3. Host picks question source: **Claude-generated** or **custom JSON file**
4. Questions appear on all screens simultaneously with a countdown timer
5. First player to submit the correct answer earns points (+ time bonus)
6. Live leaderboard updates in real time after each question
7. Final scoreboard shown after all rounds

---

## Project Structure

```
quiz-battle/
├── CLAUDE.md
├── PLAN.md
├── PROGRESS.md
├── requirements.txt
│
├── server.py              # FastAPI + WebSocket server (entry point)
├── game.py                # Game state machine (lobby → playing → results)
├── scorer.py              # Scoring logic (points + time bonus)
├── claude_gen.py          # Question generation via Claude API
│
├── questions/
│   ├── example.json       # Example custom question pack
│   └── README.md          # Format documentation
│
└── static/
    ├── index.html         # Single-page game UI
    ├── style.css          # Styling
    └── game.js            # WebSocket client + UI logic
```

---

## Tech Stack

| Role | Library |
|------|---------|
| HTTP + WebSocket server | `fastapi` + `uvicorn` |
| WebSocket support | `websockets` (via fastapi) |
| Claude question generation | `anthropic` |
| Frontend | Vanilla HTML/CSS/JS (no framework — players need zero installation) |

---

## Game States

```
LOBBY → QUESTION → ANSWER_REVEAL → [next question or] FINAL_RESULTS
```

- **LOBBY**: Players join, host configures game, host presses Start
- **QUESTION**: Question + timer shown to all players simultaneously
- **ANSWER_REVEAL**: Correct answer shown, points awarded, leaderboard updated
- **FINAL_RESULTS**: All rounds done, final scoreboard displayed

---

## Question Sources

### Option A — Claude-generated
Host selects:
- Category (e.g. Science, History, Pop Culture, Sports, Geography, Mixed)
- Difficulty (Easy / Medium / Hard)
- Number of questions (5 / 10 / 15 / 20)

`claude_gen.py` calls the Claude API and returns a list of question objects.
Questions are generated once at game start (not one-by-one).

Prompt strategy:
```
Generate {n} {difficulty} trivia questions about {category}.
Return as JSON array. Each item: {"question": "...", "answer": "...", "wrong_answers": ["...", "...", "..."]}
answer must be short (1–5 words). wrong_answers are plausible distractors.
```

### Option B — Custom JSON file
Host selects a `.json` file from the `questions/` folder.

Format:
```json
[
  {
    "question": "What is the capital of France?",
    "answer": "Paris",
    "wrong_answers": ["London", "Berlin", "Madrid"]
  }
]
```

Both sources produce the same internal question format — server handles them identically.

---

## Scoring

- **Base points**: 100 per correct answer
- **Time bonus**: up to +50 points based on how quickly the player answered
  - Formula: `bonus = round(50 * (time_remaining / total_time))`
- **Wrong answer**: 0 points (no penalty)
- **No answer (timeout)**: 0 points

---

## WebSocket Message Protocol

All messages are JSON. Server → all clients (broadcast) or server → one client (unicast).

### Client → Server
```json
{ "type": "join",   "nickname": "Alice" }
{ "type": "start",  "source": "claude", "category": "Science", "difficulty": "medium", "count": 10 }
{ "type": "start",  "source": "file",   "filename": "example.json" }
{ "type": "answer", "text": "Paris" }
```

### Server → Client (broadcast)
```json
{ "type": "player_joined", "players": ["Alice", "Bob", "Carol"] }
{ "type": "game_started" }
{ "type": "question",      "number": 1, "total": 10, "text": "What is...?", "time_limit": 15 }
{ "type": "answer_reveal", "correct_answer": "Paris", "winner": "Bob", "scores": {"Alice": 120, "Bob": 220} }
{ "type": "final_results", "scores": {"Alice": 420, "Bob": 680, "Carol": 310} }
{ "type": "error",         "message": "..." }
```

### Server → Client (unicast — to answering player only)
```json
{ "type": "answer_ack", "correct": true,  "points": 130 }
{ "type": "answer_ack", "correct": false, "points": 0 }
```

---

## Frontend (static/)

Single HTML page with views toggled by game state:

- **Lobby view**: nickname input, player list, host controls (source, category, difficulty, count)
- **Question view**: question text, answer input box, countdown timer bar, current scores sidebar
- **Reveal view**: correct answer highlighted, winner announcement, updated leaderboard
- **Results view**: final podium (1st/2nd/3rd), play again button

Host = the first player to connect (player index 0). Only the host sees the Start button and game config controls.

---

## server.py Pattern

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn, os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## claude_gen.py Pattern

```python
import anthropic, json

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def generate_questions(category: str, difficulty: str, count: int) -> list[dict]:
    prompt = f"""Generate {count} {difficulty} trivia questions about {category}.
Return ONLY a JSON array, no other text. Each item must have:
- "question": the question text
- "answer": correct answer (1-5 words, no articles needed)
- "wrong_answers": list of 3 plausible but incorrect answers"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)
```

---

## Answer Checking

Answers are checked case-insensitively with minor fuzzy tolerance:
```python
def is_correct(submitted: str, correct: str) -> bool:
    return submitted.strip().lower() == correct.strip().lower()
```

For better UX, also accept answers that contain the correct answer:
```python
    or correct.strip().lower() in submitted.strip().lower()
```

---

## Deployment (Render.com via GitHub)

### One-time setup
1. Push project to a GitHub repo
2. Go to [render.com](https://render.com) → New → Web Service → connect GitHub repo
3. Settings:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `python server.py`
   - **Environment variable**: `ANTHROPIC_API_KEY` = your key
4. Deploy → Render gives a public URL (e.g. `https://quiz-battle.onrender.com`)

### After setup
- Push to GitHub → Render auto-redeploys
- Share the URL with players — no install needed on their end

### Important: cloud deployment differences from local
- Port must come from environment: `PORT = int(os.environ.get("PORT", 8000))`
- WebSocket URL in `game.js` must be dynamic (not hardcoded `localhost`):
  ```js
  const wsProtocol = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${wsProtocol}//${location.host}/ws`);
  ```
- Render free tier "spins down" after 15 min of inactivity (cold start ~30s)
  - Acceptable for a game that's actively being played

### Local development
```bash
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sk-ant-...
python server.py
# Open http://localhost:8000/static/index.html
```

---

## Agent Execution Plan

### Phase 1 — Backend
- `game.py` — GameState class, player management, question queue
- `scorer.py` — scoring + time bonus logic
- `claude_gen.py` — Claude API question generation
- `server.py` — FastAPI + WebSocket server, ties everything together

### Phase 2 — Frontend
- `static/index.html` — HTML structure, all views
- `static/style.css` — clean, game-like styling
- `static/game.js` — WebSocket client, state machine, UI updates

### Phase 3 — Questions
- `questions/example.json` — 20 example questions across categories
- `questions/README.md` — format documentation for making custom packs

### Phase 4 — Polish
- Answer fuzzy matching improvements
- Host kick/restart controls
- Reconnect handling if player drops

---

## Requirements

```
fastapi
uvicorn[standard]
anthropic
```

No database needed — all state is in memory (single game session).
