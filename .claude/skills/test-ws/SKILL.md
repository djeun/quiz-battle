---
name: test-ws
description: Test the WebSocket server by simulating players joining and answering questions. Run with /test-ws.
user-invocable: true
allowed-tools: Bash
---

Run the WebSocket integration test to verify game flow works end-to-end.

```bash
cd C:\Users\Administrator\quiz-battle
python -c "
import asyncio, websockets, json

async def test():
    uri = 'ws://localhost:8000/ws'
    async with websockets.connect(uri) as ws1:
        async with websockets.connect(uri) as ws2:
            # Player 1 joins (becomes host)
            await ws1.send(json.dumps({'type': 'join', 'nickname': 'Alice'}))
            print('Alice joined:', await ws1.recv())

            # Player 2 joins
            await ws2.send(json.dumps({'type': 'join', 'nickname': 'Bob'}))
            print('Bob joined:', await ws2.recv())

            # Host starts game with custom file
            await ws1.send(json.dumps({'type': 'start', 'source': 'file', 'filename': 'example.json'}))
            q = await ws1.recv()
            print('Question received:', q[:100])

            # Alice answers
            data = json.loads(q)
            if data.get('type') == 'question':
                await ws1.send(json.dumps({'type': 'answer', 'text': 'test answer'}))
                print('Answer ack:', await ws1.recv())

asyncio.run(test())
"
```

Server must be running (`/run`) before executing this test.
