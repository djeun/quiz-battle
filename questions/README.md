# Custom Question Packs

Place `.json` files in this folder to use them as a question source.

## Format

Each file must be a JSON array. Every item must have:

```json
[
  {
    "question": "What is the capital of France?",
    "answer": "Paris",
    "wrong_answers": ["London", "Berlin", "Madrid"]
  }
]
```

| Field          | Type            | Notes                                            |
|----------------|-----------------|--------------------------------------------------|
| `question`     | string          | The trivia question text                         |
| `answer`       | string          | The correct answer (1–5 words recommended)       |
| `wrong_answers`| array of 3 strings | Plausible distractors shown as choices        |

## Tips

- Keep answers short (1–5 words). Answers are checked case-insensitively.
- Include exactly **3** wrong answers so the UI shows a clean 4-choice grid.
- File name must end in `.json`.
- Use UTF-8 encoding.

## Example

See `example.json` for a ready-to-use pack of 20 general-knowledge questions.
