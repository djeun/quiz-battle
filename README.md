# ⚡ Quiz Battle

Real-time multiplayer trivia for 2–4 players — no installation needed for players.
Built with FastAPI + WebSockets + Claude AI question generation.

---

## Play it

1. Host opens the game URL in their browser
2. Share the URL with friends (up to 4 players total)
3. Everyone enters a nickname and joins the lobby
4. Host picks a question source and presses **Start Game**
5. Answer as fast as you can — speed bonus points reward quick correct answers!

---

## Question sources

| Source | How it works |
|--------|--------------|
| ⚡ Claude AI | Generates fresh questions on-demand. Choose category, difficulty, and count. |
| 📁 Custom JSON | Upload your own question pack to the `questions/` folder. See `questions/README.md`. |

---

## Scoring

| Event | Points |
|-------|--------|
| Correct answer | 100 base |
| Speed bonus | +0 to +50 (based on remaining time) |
| Wrong answer | 0 |
| No answer (timeout) | 0 |

---

## Local development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key (only needed for Claude-generated questions)
export ANTHROPIC_API_KEY=sk-ant-...   # macOS / Linux
set ANTHROPIC_API_KEY=sk-ant-...      # Windows

# 3. Start the server
python server.py

# 4. Open in browser
# http://localhost:8000
```

---

## Deploy to Render.com

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect your repo
3. Render reads `render.yaml` automatically — no extra config needed
4. Add your `ANTHROPIC_API_KEY` in the Render dashboard under **Environment**
5. Deploy — Render gives you a public URL to share with players

> **Note:** Render's free tier spins down after 15 min of inactivity (~30 s cold start).
> This is fine for active game sessions.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Server | FastAPI + uvicorn |
| Real-time | WebSockets |
| Question AI | Anthropic Claude (Haiku) |
| Frontend | Vanilla HTML / CSS / JS — zero dependencies |
