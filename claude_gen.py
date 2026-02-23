import json
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


def generate_questions(category: str, difficulty: str, count: int) -> list[dict]:
    """
    Generate trivia questions via Claude API.
    Returns a list of dicts with keys: question, answer, wrong_answers.
    """
    prompt = (
        f"Generate {count} {difficulty} trivia questions about {category}.\n"
        "Return ONLY a JSON array, no other text. Each item must have:\n"
        '- "question": the question text\n'
        '- "answer": correct answer (1-5 words, no articles needed)\n'
        '- "wrong_answers": list of exactly 3 plausible but incorrect answers'
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    return json.loads(text)
