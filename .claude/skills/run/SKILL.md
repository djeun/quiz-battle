---
name: run
description: Start the Quiz Battle server locally for testing. Run with /run.
user-invocable: true
allowed-tools: Bash
---

Start the server and verify it launches without errors.

```bash
cd C:\Users\Administrator\quiz-battle
pip install -r requirements.txt -q
python server.py
```

After running, open `http://localhost:8000/static/index.html` in a browser to verify the UI loads.
Press Ctrl+C to stop the server.
