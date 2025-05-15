from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import openai, os, tempfile
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import sqlite3

# ─── 1) Chargement API key & Stream configuration ─────────────────────────────
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("API key manquante")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 2) Initialisation SQLite ────────────────────────────────────────────────
DB_PATH = Path("transcripts.db")
conn    = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("""
CREATE TABLE IF NOT EXISTS msgs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    course    TEXT,
    timestamp TEXT,
    texte     TEXT
)
""")
conn.commit()

# ─── 3) Gestion WebSocket ────────────────────────────────────────────────────
clients: set[WebSocket] = set()

@app.websocket("/ws/transcribe/{course}")
async def websocket_endpoint(ws: WebSocket, course: str):
    await ws.accept()
    clients.add(ws)
    print(f"🔌 Client connecté pour la course «{course}»")

    try:
        while True:
            try:
                # → On attend un chunk audio binaire
                chunk_bytes = await ws.receive_bytes()
                print(f"📥 Reçu chunk de {len(chunk_bytes)} bytes")
            except WebSocketDisconnect:
                print("🛑 Client déconnecté (WebSocketDisconnect)")
                break
            except Exception as e:
                print("❌ Erreur réception chunk :", e)
                break

            # --- 4) Traitement Whisper & broadcast/persist ---
            tmp = None
            try:
                # a) Sauvegarde temporaire
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
                tmp.write(chunk_bytes)
                tmp.flush()

                # b) Appel Whisper
                with open(tmp.name, "rb") as f:
                    resp = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="text",
                        language="fr"
                    )
                texte = resp.strip()
                ts    = datetime.utcnow().isoformat()

                # c) Broadcast à tous les WebSocket connectés
                payload = {"timestamp": ts, "texte": texte}
                for client in list(clients):
                    await client.send_json(payload)
                print(f"📤 Broadcast texte «{texte[:30]}...»")

                # d) Persistance en SQLite
                conn.execute(
                    "INSERT INTO msgs (course, timestamp, texte) VALUES (?, ?, ?)",
                    (course, ts, texte)
                )
                conn.commit()

            except Exception as chunk_err:
                print("❌ Erreur traitement chunk :", chunk_err)

            finally:
                # → Nettoyage du fichier temporaire
                if tmp is not None:
                    Path(tmp.name).unlink(missing_ok=True)

    finally:
        # → Déconnexion finale
        clients.discard(ws)
        print("🔒 Connexion fermée, client retiré")
