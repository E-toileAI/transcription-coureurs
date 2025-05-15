# transcriber_service_ws.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import openai, os, tempfile
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("API key manquante")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

clients: set[WebSocket] = set()

@app.websocket("/ws/transcribe/{course}")
async def websocket_endpoint(ws: WebSocket, course: str):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            chunk_bytes = await ws.receive_bytes()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            tmp.write(chunk_bytes); tmp.flush()
            with open(tmp.name, "rb") as f:
                resp = openai.audio.transcriptions.create(
                    model="whisper-1", file=f,
                    response_format="text", language="fr"
                )
            texte = resp.strip()
            ts = datetime.utcnow().isoformat()
            for client in list(clients):
                await client.send_json({"timestamp": ts, "texte": texte})
            Path(tmp.name).unlink()
    except Exception:
        pass
    finally:
        clients.remove(ws)
