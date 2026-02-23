"use strict";

// ── WebSocket connection ───────────────────────────────────────────────────

const wsProtocol = location.protocol === "https:" ? "wss:" : "ws:";
let ws = null;

let myNickname = null;
let isHost = false;
let hasAnswered = false;
let myAnswer = null;    // track which answer was submitted for visual feedback
let timerInterval = null;
let localScores = {};   // kept in sync via server messages

// ── DOM helpers ────────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);

function showView(name) {
  document.querySelectorAll(".view").forEach(v => {
    v.classList.add("hidden");
    v.classList.remove("active");
  });
  const view = $(`view-${name}`);
  view.classList.remove("hidden");
  view.classList.add("active");
}

function showToast(msg, duration = 3500) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => t.classList.add("hidden"), duration);
}

// ── WebSocket setup & reconnect ────────────────────────────────────────────

function connect() {
  ws = new WebSocket(`${wsProtocol}//${location.host}/ws`);

  ws.onopen = () => {
    console.log("[WS] connected");
    // Auto-rejoin if we already had a nickname (reconnect after drop)
    if (myNickname) {
      ws.send(JSON.stringify({ type: "join", nickname: myNickname }));
    }
  };

  ws.onclose = () => {
    showToast("Connection lost. Reconnecting…");
    setTimeout(connect, 2000);   // attempt reconnect after 2 s
  };

  ws.onerror = () => {
    // onclose fires after onerror, so just let that handle the retry
  };

  ws.onmessage = event => {
    let msg;
    try { msg = JSON.parse(event.data); } catch { return; }
    const handler = handlers[msg.type];
    if (handler) handler(msg);
  };
}

connect();

// Populate file dropdown on load
async function loadQuestionFiles() {
  try {
    const res = await fetch("/api/question-files");
    const data = await res.json();
    const select = $("filename-select");
    const labels = { easy: "🟢", medium: "🟡", hard: "🔴" };
    select.innerHTML = data.files.map(f => {
      const [diff, ...rest] = f.replace(".json", "").split("-");
      const label = labels[diff] || "";
      const name = rest.map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
      const display = `${label} ${name} (${diff.charAt(0).toUpperCase() + diff.slice(1)})`;
      return `<option value="${escAttr(f)}">${display}</option>`;
    }).join("");
  } catch (e) {
    console.error("Failed to load question files:", e);
  }
}
loadQuestionFiles();

// ── Message handlers ───────────────────────────────────────────────────────

const handlers = {

  player_joined(msg) {
    updatePlayerList(msg.players);
    promoteHostIfNeeded(msg.players);
  },

  player_rejoined(msg) {
    updatePlayerList(msg.players);
    showToast(`${msg.nickname} reconnected`);
  },

  player_left(msg) {
    updatePlayerList(msg.players);
    showToast(`${msg.nickname} disconnected`);
  },

  game_started() {
    showView("question");
    $("question-text").textContent = "Loading questions…";
    $("choices-container").innerHTML = "";
    $("answer-status").classList.add("hidden");
    $("skip-btn").classList.add("hidden");
    stopTimer();
    $("timer-text").textContent = "–";
  },

  question(msg) {
    hasAnswered = false;
    myAnswer = null;
    showView("question");
    renderQuestion(msg);
    startTimer(msg.time_limit);

    // Show skip button for host (not shown if already reconnecting mid-answer)
    if (isHost) {
      $("skip-btn").classList.remove("hidden");
    }

    // Reconnected mid-game — show a brief notice
    if (msg.reconnect) {
      const banner = document.createElement("div");
      banner.className = "reconnect-banner";
      banner.textContent = "⚡ Reconnected — jump back in!";
      $("question-text").before(banner);
      setTimeout(() => banner.remove(), 4000);
    }
  },

  answer_ack(msg) {
    const statusEl = $("answer-status");
    if (msg.correct) {
      if (msg.points === 200) {
        statusEl.textContent = `🥇 Correct! First to answer – +200 pts`;
      } else {
        statusEl.textContent = `✅ Correct! Someone was faster – +100 pts`;
      }
      statusEl.className = "answer-status correct";
    } else if (msg.timeout) {
      statusEl.textContent = "⏱ Not answered – 0 pts";
      statusEl.className = "answer-status wrong";
    } else {
      statusEl.textContent = "✗ Wrong answer – 100 pts";
      statusEl.className = "answer-status wrong";
    }
    statusEl.classList.remove("hidden");
    $("skip-btn").classList.add("hidden");

    // Color the submitted button correct (green) or wrong (red); skip if timed out
    if (!msg.timeout) {
      document.querySelectorAll(".choice-btn").forEach(btn => {
        if (btn.dataset.answer === myAnswer) {
          btn.classList.remove("selected-pending");
          btn.classList.add(msg.correct ? "selected-correct" : "selected-wrong");
        }
        btn.disabled = true;
      });
    }
  },

  answer_reveal(msg) {
    stopTimer();
    localScores = msg.scores || localScores;
    renderReveal(msg);
    showView("reveal");
  },

  final_results(msg) {
    stopTimer();
    localScores = msg.scores || localScores;
    renderResults(msg);
    showView("results");
    if (isHost) {
      $("play-again-btn").classList.remove("hidden");
      $("waiting-host").classList.add("hidden");
    } else {
      $("waiting-host").classList.remove("hidden");
    }
  },

  // Host pressed Play Again — everyone returns to lobby
  game_reset(msg) {
    localScores = {};
    stopTimer();
    updatePlayerList(msg.players);
    promoteHostIfNeeded(msg.players);
    $("play-again-btn").classList.add("hidden");
    $("start-btn").disabled = false;
    $("start-btn").textContent = "Start Game";
    showView("lobby");
  },

  error(msg) {
    showToast(`Error: ${msg.message}`);
    // Re-enable start button if it was disabled by a failed start attempt
    $("start-btn").disabled = false;
    $("start-btn").textContent = "Start Game";
  },
};

// ── Actions ────────────────────────────────────────────────────────────────

function joinGame() {
  const input = $("nickname-input");
  const nickname = input.value.trim();
  if (!nickname) { input.focus(); return; }

  myNickname = nickname;
  ws.send(JSON.stringify({ type: "join", nickname }));
  input.disabled = true;
  $("join-btn").disabled = true;
}

function startGame() {
  const source = $("source-select").value;
  const msg = { type: "start", source };

  if (source === "claude") {
    msg.category   = $("category-select").value;
    msg.difficulty = $("difficulty-select").value;
    msg.count      = parseInt($("count-select").value);
  } else {
    msg.filename = $("filename-select").value;
    if (!msg.filename) { showToast("No question file selected."); return; }
  }

  $("start-btn").disabled = true;
  $("start-btn").textContent = "Generating questions…";
  ws.send(JSON.stringify(msg));
}

function submitAnswer(text) {
  if (hasAnswered) return;
  hasAnswered = true;
  myAnswer = text;

  // Show pending state on clicked button; disable all buttons while waiting
  document.querySelectorAll(".choice-btn").forEach(btn => {
    if (btn.dataset.answer === text) btn.classList.add("selected-pending");
    btn.disabled = true;
  });

  ws.send(JSON.stringify({ type: "answer", text }));
}

function skipQuestion() {
  if (!isHost) return;
  $("skip-btn").disabled = true;
  ws.send(JSON.stringify({ type: "skip" }));
}

function playAgain() {
  ws.send(JSON.stringify({ type: "play_again" }));
  $("play-again-btn").classList.add("hidden");
}

function toggleSourceOptions() {
  const source = $("source-select").value;
  $("claude-options").classList.toggle("hidden", source !== "claude");
  $("file-options").classList.toggle("hidden",   source !== "file");
}

// ── Rendering ──────────────────────────────────────────────────────────────

function promoteHostIfNeeded(players) {
  if (myNickname && players[0] === myNickname && !isHost) {
    isHost = true;
    $("host-controls").classList.remove("hidden");
  }
}

function updatePlayerList(players) {
  $("player-list").innerHTML = players
    .map((p, i) => {
      const me = p === myNickname;
      const crown = i === 0 ? "👑 " : "";
      return `<div class="player-chip ${me ? "me" : ""}">${crown}${escHtml(p)}</div>`;
    })
    .join("");
}

function renderQuestion(msg) {
  $("q-number").textContent = `Q${msg.number} / ${msg.total}`;
  $("question-text").textContent = msg.text;
  $("answer-status").classList.add("hidden");
  $("skip-btn").disabled = false;

  const container = $("choices-container");
  container.innerHTML = (msg.choices || [])
    .map(
      c => `<button class="choice-btn" data-answer="${escAttr(c)}"
                    onclick="submitAnswer(this.dataset.answer)">${escHtml(c)}</button>`
    )
    .join("");

  renderScoresSidebar(localScores);
}

function renderScoresSidebar(scores) {
  $("scores-sidebar").innerHTML =
    `<h3>Scores</h3>` +
    sortedScores(scores)
      .map(([name, pts]) =>
        `<div class="score-row ${name === myNickname ? "me" : ""}">
           <span>${escHtml(name)}</span>
           <span class="pts">${pts}</span>
         </div>`
      )
      .join("");
}

function renderReveal(msg) {
  const skippedLabel = msg.skipped ? " <span style='font-size:.7em;opacity:.6'>(skipped)</span>" : "";
  $("reveal-answer").innerHTML =
    `✓ Correct answer: <strong>${escHtml(msg.correct_answer)}</strong>${skippedLabel}`;

  $("reveal-winner").textContent = msg.winner
    ? `🏆 ${msg.winner} answered first!`
    : msg.skipped ? "Question skipped by host" : "No one answered correctly";

  $("reveal-scores").innerHTML =
    `<h3>Leaderboard</h3>` +
    sortedScores(msg.scores)
      .map(([name, pts], i) =>
        `<div class="lb-row ${name === myNickname ? "me" : ""}">
           <span class="rank">${i + 1}</span>
           <span class="name">${escHtml(name)}</span>
           <span class="pts">${pts}</span>
         </div>`
      )
      .join("");
}

function renderResults(msg) {
  const sorted = sortedScores(msg.scores);
  const medals = ["🥇", "🥈", "🥉"];

  $("podium").innerHTML = sorted
    .slice(0, 3)
    .map(
      ([name, pts], i) =>
        `<div class="podium-item place-${i + 1}">
           <div class="medal">${medals[i]}</div>
           <div class="pname">${escHtml(name)}</div>
           <div class="pscore">${pts} pts</div>
         </div>`
    )
    .join("");

  $("final-scores").innerHTML =
    `<h3>All Scores</h3>` +
    sorted
      .map(([name, pts], i) =>
        `<div class="final-row">
           <span class="rank">${i + 1}</span>
           <span class="name">${escHtml(name)}</span>
           <span class="pts">${pts}</span>
         </div>`
      )
      .join("");
}

// ── Timer ──────────────────────────────────────────────────────────────────

function startTimer(seconds) {
  stopTimer();

  const bar  = $("timer-bar");
  const text = $("timer-text");

  bar.style.transition = "none";
  bar.style.width = "100%";
  bar.classList.remove("urgent");
  void bar.offsetWidth;  // force reflow

  bar.style.transition = `width ${seconds}s linear`;
  bar.style.width = "0%";

  let remaining = seconds;
  text.textContent = remaining;

  timerInterval = setInterval(() => {
    remaining -= 1;
    text.textContent = Math.max(0, remaining);
    if (remaining <= 5) bar.classList.add("urgent");
    if (remaining <= 0) stopTimer();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

// ── Utilities ──────────────────────────────────────────────────────────────

function sortedScores(scores) {
  return Object.entries(scores || {}).sort((a, b) => b[1] - a[1]);
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escAttr(str) {
  return String(str).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// ── Keyboard shortcuts ────────────────────────────────────────────────────

document.addEventListener("keydown", e => {
  if (e.key === "Enter" && $("view-lobby").classList.contains("active")) {
    if (!$("join-btn").disabled) joinGame();
  }
});
