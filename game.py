import re
import time
from enum import Enum


class GamePhase(str, Enum):
    LOBBY = "lobby"
    QUESTION = "question"
    ANSWER_REVEAL = "answer_reveal"
    FINAL_RESULTS = "final_results"


class GameState:
    def __init__(self):
        self.phase = GamePhase.LOBBY
        self.players: list[str] = []           # ordered nicknames; index 0 = host
        self.scores: dict[str, int] = {}       # nickname → cumulative score
        self.disconnected: set[str] = set()    # mid-game disconnects (score kept)
        self.questions: list[dict] = []
        self.current_index: int = -1
        self.current_choices: list[str] = []   # shuffled choices for active question
        self.answered: set[str] = set()        # nicknames who answered this question
        self.first_correct: str | None = None  # first player to answer correctly
        self.question_start_time: float = 0.0
        self.time_limit: int = 15              # seconds per question

    # ── Player management ──────────────────────────────────────────────────

    def add_player(self, nickname: str) -> tuple[bool, bool]:
        """
        Try to add / reconnect a player.
        Returns (accepted, is_reconnect).
        """
        if self.phase == GamePhase.LOBBY:
            if nickname in self.players or len(self.players) >= 4:
                return False, False
            self.players.append(nickname)
            self.scores[nickname] = 0
            self.disconnected.discard(nickname)
            return True, False

        # Mid-game reconnect — only allowed if they were previously in this game
        if nickname in self.disconnected:
            self.players.append(nickname)
            self.disconnected.discard(nickname)
            return True, True

        return False, False

    def remove_player(self, nickname: str):
        if nickname not in self.players:
            return
        self.players.remove(nickname)
        if self.phase == GamePhase.LOBBY:
            self.scores.pop(nickname, None)
        else:
            # Keep score — player may reconnect
            self.disconnected.add(nickname)

    @property
    def host(self) -> str | None:
        return self.players[0] if self.players else None

    # ── Game flow ──────────────────────────────────────────────────────────

    def load_questions(self, questions: list[dict]):
        self.questions = questions
        self.current_index = -1

    def advance_question(self) -> dict | None:
        """Move to next question. Returns question dict, or None if game over."""
        self.current_index += 1
        if self.current_index >= len(self.questions):
            self.phase = GamePhase.FINAL_RESULTS
            return None
        self.phase = GamePhase.QUESTION
        self.current_choices = []
        self.answered = set()
        self.first_correct = None
        self.question_start_time = time.time()
        return self.current_question

    @property
    def current_question(self) -> dict | None:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def time_remaining(self) -> float:
        elapsed = time.time() - self.question_start_time
        return max(0.0, self.time_limit - elapsed)

    # ── Answer handling ────────────────────────────────────────────────────

    def submit_answer(self, nickname: str, answer_text: str) -> tuple[bool, int]:
        """
        Process an answer submission.
        Returns (is_correct, points_earned).
        Returns (False, 0) if wrong phase or already answered.
        """
        if self.phase != GamePhase.QUESTION:
            return False, 0
        if nickname in self.answered:
            return False, 0

        self.answered.add(nickname)
        question = self.current_question
        correct = _is_correct(answer_text, question["answer"])

        if correct:
            if self.first_correct is None:
                # First to answer correctly
                points = 200
                self.first_correct = nickname
            else:
                # Someone already answered correctly
                points = 100
            self.scores[nickname] += points
            return True, points

        return False, 0

    def all_answered(self) -> bool:
        return len(self.players) > 0 and len(self.answered) >= len(self.players)

    def get_reveal_payload(self) -> dict:
        q = self.current_question
        return {
            "correct_answer": q["answer"],
            "winner": self.first_correct,
            "scores": dict(self.scores),
        }

    def reset(self, keep_players: list[str] | None = None):
        """Reset to lobby for play-again. Pass keep_players to set the roster."""
        roster = keep_players if keep_players is not None else list(self.players)
        self.__init__()
        for name in roster:
            self.players.append(name)
            self.scores[name] = 0


# ── Answer checking ─────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, strip leading articles, collapse punctuation/whitespace."""
    text = text.strip().lower()
    text = re.sub(r"^(the|a|an)\s+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein distance between two strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    row = list(range(len(b) + 1))
    for ch in a:
        new_row = [row[0] + 1]
        for j, d in enumerate(b):
            new_row.append(min(new_row[-1] + 1, row[j + 1] + 1, row[j] + (ch != d)))
        row = new_row
    return row[-1]


def _is_correct(submitted: str, correct: str) -> bool:
    s = _normalize(submitted)
    c = _normalize(correct)

    if not s:
        return False
    if s == c or c in s:
        return True

    # Typo tolerance: 1 edit for 4-6 char answers, 2 edits for 7+ char answers
    threshold = 0
    if len(c) >= 7:
        threshold = 2
    elif len(c) >= 4:
        threshold = 1

    if threshold and _edit_distance(s, c) <= threshold:
        return True

    return False
