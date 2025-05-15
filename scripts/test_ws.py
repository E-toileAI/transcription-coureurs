import asyncio, websockets

async def test():
    uri = "ws://localhost:8000/ws/transcribe/maCourseTest"
    async with websockets.connect(uri) as ws:
        print("Connecté, envoi blob vide…")
        await ws.send(b"")
        print("Reçu :", await ws.recv())

asyncio.run(test())
