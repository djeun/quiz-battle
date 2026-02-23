import asyncio
import json
import os
import random
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from claude_gen import generate_questions
from game import GamePhase, GameState

app = FastAPI()

# ── Global state ───────────────────────────────────────────────────────────

game = GameState()
connections: dict[WebSocket, str | None] = {}  # ws → nickname (None until joined)
question_timer: asyncio.Task | None = None

# ── Static files ───────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/question-files")
async def list_question_files():
    questions_dir = Path(__file__).parent / "questions"
    files = sorted(f.name for f in questions_dir.glob("*.json"))
    return {"files": files}


# ── Helpers ────────────────────────────────────────────────────────────────

async def broadcast(message: dict):
    """Send a message to every connected client."""
    data = json.dumps(message)
    dead: list[WebSocket] = []
    for ws in list(connections):
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        await _on_disconnect(ws)


async def send_to(ws: WebSocket, message: dict):
    """Send a message to a single client."""
    try:
        await ws.send_text(json.dumps(message))
    except Exception:
        pass


async def _on_disconnect(ws: WebSocket):
    """Handle a dead / departing WebSocket."""
    global question_timer

    nickname = connections.pop(ws, None)
    if not nickname:
        return
    game.remove_player(nickname)

    # If no one with a nickname is left, fully reset so the next group can start fresh
    if not any(connections.values()):
        if question_timer and not question_timer.done():
            question_timer.cancel()
            question_timer = None
        game.__init__()
        return

    if game.phase == GamePhase.LOBBY:
        await broadcast({"type": "player_joined", "players": game.players})
    else:
        await broadcast({"type": "player_left", "nickname": nickname, "players": game.players})


# ── Game flow helpers ──────────────────────────────────────────────────────

async def push_question():
    """Advance to the next question and broadcast it, or end the game."""
    global question_timer

    q = game.advance_question()

    if q is None:
        await broadcast({"type": "final_results", "scores": game.scores})
        return

    choices = [q["answer"]] + q.get("wrong_answers", [])
    random.shuffle(choices)
    game.current_choices = choices  # store for reconnecting players

    await broadcast(
        {
            "type": "question",
            "number": game.current_index + 1,
            "total": len(game.questions),
            "text": q["question"],
            "choices": choices,
            "time_limit": game.time_limit,
        }
    )

    question_timer = asyncio.create_task(_auto_reveal(game.time_limit))


async def _auto_reveal(delay: float):
    global question_timer
    await asyncio.sleep(delay)
    question_timer = None  # clear before calling do_reveal so it doesn't cancel itself
    await do_reveal()


async def do_reveal(skipped: bool = False):
    """Reveal the answer and schedule the next question."""
    global question_timer

    if game.phase != GamePhase.QUESTION:
        return  # guard against double-call

    game.phase = GamePhase.ANSWER_REVEAL

    if question_timer and not question_timer.done():
        question_timer.cancel()
        question_timer = None

    payload = game.get_reveal_payload()
    if skipped:
        payload["skipped"] = True
    await broadcast({"type": "answer_reveal", **payload})

    await asyncio.sleep(3)
    await push_question()


# ── WebSocket endpoint ─────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections[websocket] = None

    try:
        async for data in websocket.iter_json():
            msg_type = data.get("type")
            if msg_type == "join":
                await handle_join(websocket, data)
            elif msg_type == "start":
                await handle_start(websocket, data)
            elif msg_type == "answer":
                await handle_answer(websocket, data)
            elif msg_type == "skip":
                await handle_skip(websocket)
            elif msg_type == "play_again":
                await handle_play_again(websocket)
    except WebSocketDisconnect:
        pass
    finally:
        await _on_disconnect(websocket)


# ── Message handlers ───────────────────────────────────────────────────────

async def handle_join(ws: WebSocket, data: dict):
    nickname = data.get("nickname", "").strip()
    if not nickname:
        await send_to(ws, {"type": "error", "message": "Nickname is required."})
        return

    accepted, is_reconnect = game.add_player(nickname)
    if not accepted:
        await send_to(
            ws,
            {
                "type": "error",
                "message": (
                    "Cannot join: game is in progress, nickname is taken, "
                    "or the room is full (max 4 players)."
                ),
            },
        )
        return

    connections[ws] = nickname

    if is_reconnect:
        # Catch the reconnecting player up with the current game state
        await send_to(ws, {"type": "player_joined", "players": game.players})
        await _send_current_state(ws)
        await broadcast({"type": "player_rejoined", "nickname": nickname, "players": game.players})
    else:
        await broadcast({"type": "player_joined", "players": game.players})


async def _send_current_state(ws: WebSocket):
    """Send the current game state to a reconnecting player."""
    if game.phase == GamePhase.QUESTION and game.current_question:
        q = game.current_question
        remaining = int(game.time_remaining())
        await send_to(
            ws,
            {
                "type": "question",
                "number": game.current_index + 1,
                "total": len(game.questions),
                "text": q["question"],
                "choices": game.current_choices,
                "time_limit": remaining,
                "reconnect": True,
            },
        )
    elif game.phase == GamePhase.FINAL_RESULTS:
        await send_to(ws, {"type": "final_results", "scores": game.scores})


async def handle_start(ws: WebSocket, data: dict):
    nickname = connections.get(ws)
    if nickname != game.host:
        await send_to(ws, {"type": "error", "message": "Only the host can start the game."})
        return
    if len(game.players) < 2:
        await send_to(ws, {"type": "error", "message": "Need at least 2 players to start."})
        return
    if game.phase != GamePhase.LOBBY:
        await send_to(ws, {"type": "error", "message": "Game already in progress."})
        return

    source = data.get("source")
    try:
        if source == "claude":
            questions = generate_questions(
                category=data.get("category", "Mixed"),
                difficulty=data.get("difficulty", "medium"),
                count=int(data.get("count", 10)),
            )
        elif source == "file":
            filename = Path(data.get("filename", "")).name  # strip directory traversal
            questions_dir = Path(__file__).parent / "questions"
            path = questions_dir / filename
            if not path.exists() or path.suffix != ".json":
                raise FileNotFoundError(f"Question file not found: {filename}")
            with open(path, encoding="utf-8") as f:
                questions = json.load(f)
        else:
            await send_to(ws, {"type": "error", "message": "Invalid source. Use 'claude' or 'file'."})
            return
    except Exception as exc:
        await send_to(ws, {"type": "error", "message": f"Failed to load questions: {exc}"})
        return

    game.load_questions(questions)
    await broadcast({"type": "game_started"})
    await asyncio.sleep(0.5)
    await push_question()


async def handle_answer(ws: WebSocket, data: dict):
    nickname = connections.get(ws)
    if not nickname:
        return

    answer_text = data.get("text", "")
    correct, points = game.submit_answer(nickname, answer_text)
    await send_to(ws, {"type": "answer_ack", "correct": correct, "points": points})

    if game.all_answered():
        await do_reveal()


async def handle_skip(ws: WebSocket):
    """Host skips the current question."""
    nickname = connections.get(ws)
    if nickname != game.host:
        return
    if game.phase != GamePhase.QUESTION:
        return
    await do_reveal(skipped=True)


async def handle_play_again(ws: WebSocket):
    """Host resets the game so everyone can play again without refreshing."""
    nickname = connections.get(ws)
    if nickname != game.host:
        return
    if game.phase != GamePhase.FINAL_RESULTS:
        return

    # Only keep players who are still connected
    connected_nicks = [n for n in connections.values() if n]
    game.reset(keep_players=connected_nicks)
    await broadcast({"type": "game_reset", "players": game.players})


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
