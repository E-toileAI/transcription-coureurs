# app.py

# 1️⃣ Charger les variables d’environnement
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DURATION        = int(os.getenv("DURATION", 5))
FS              = int(os.getenv("FS", 16000))

# 2️⃣ Imports principaux
import streamlit as st
import threading
import time
import tempfile
import csv
from pathlib import Path
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import pandas as pd
import requests
import subprocess
import sys
from streamlit.components.v1 import html


# 3️⃣ Config Streamlit
st.set_page_config(
    page_title="Transcription API • Coureurs",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 4️⃣ Dossier de sortie
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 5️⃣ Fonction pour appeler le service FastAPI

def transcribe_service(path: str, course: str) -> str:
    try:
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f, "audio/wav")}
            url = f"http://localhost:8000/transcribe/{course}"
            resp = requests.post(url, files=files, timeout=60)
        resp.raise_for_status()
        return resp.json().get("texte", "")
    except Exception as e:
        return f"Erreur transcription: {e}"

# 6️⃣ Style bulle

def style_bubble(ts: str, text: str):
    st.markdown(f"""
        <div style="
            background-color:#1c1c1e;
            padding:12px;border-radius:12px;
            margin-bottom:8px;color:white;
            max-width:75%;word-wrap:break-word;">
          <div style="color:gray;font-size:0.8em">🕒 {ts}</div>
          <div>{text}</div>
        </div>""", unsafe_allow_html=True)

# 7️⃣ Sidebar historique
st.sidebar.title("📂 Historique des transcriptions")
search_q = st.sidebar.text_input("🔍 Rechercher", placeholder="filtrer par nom…")
csvs = sorted(OUTPUT_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
filtered = [p for p in csvs if search_q.lower() in p.name.lower()]
choice = st.sidebar.selectbox("🔄 Choisir un fichier", ["(Nouveau)"] + [p.name for p in filtered])
if choice != "(Nouveau)":
    sel = OUTPUT_DIR/choice
    st.sidebar.download_button("📥 Télécharger CSV", sel.read_bytes(), file_name=sel.name)
    st.sidebar.markdown("### Aperçu")
    for row in csv.DictReader(sel.open(encoding="utf-8")):
        ts = row.get("timestamp") or row.get("timestamp (s)")
        style_bubble(ts, row.get("texte", ""))


st.title("🚴‍♂️ Transcription Live • Cyclistes")

course = st.text_input("📌 Nom de la course pour le live", "")
if course:
    html(f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <style>
        body {{ background:#111; color:#fff; font-family:sans-serif; padding:1rem; }}
        button {{ margin-right:1rem; padding:.5rem 1rem; font-size:1rem; }}
        #log {{ max-height:400px; overflow-y:auto; margin-top:1rem; }}
        .bubble {{
          background:#1c1c1e;
          padding:12px;
          border-radius:12px;
          margin-bottom:8px;
          max-width:75%;
        }}
        .ts {{ color:gray; font-size:.8em; margin-bottom:4px; }}
      </style>
    </head>
    <body>
      <h3>🎙️ Live Transcription</h3>
      <button id="start">▶️ Démarrer</button>
      <button id="stop" disabled>⏹️ Arrêter</button>
      <div id="log"></div>

      <script>
        const courseName = "{course}";
        const startBtn = document.getElementById('start');
        const stopBtn  = document.getElementById('stop');
        const log      = document.getElementById('log');
        let ws, stream;
        const CHUNK_MS = 5000;

        async function startLive() {{
          ws = new WebSocket(`ws://localhost:8000/ws/transcribe/${{courseName}}`);
          ws.binaryType = 'arraybuffer';
          ws.onmessage = e => {{
            const {{timestamp, texte}} = JSON.parse(e.data);
            const b = document.createElement('div');
            b.className = 'bubble';
            b.innerHTML = `<div class="ts">🕒 ${{timestamp}}</div><div>${{texte}}</div>`;
            log.appendChild(b);
            log.scrollTop = log.scrollHeight;
          }};

          stream = await navigator.mediaDevices.getUserMedia({{audio:true}});
          startSegment();
        }}

        function startSegment() {{
          const recorder = new MediaRecorder(stream, {{ mimeType:'audio/ogg; codecs=opus' }});
          recorder.ondataavailable = async ev => {{
            if (ev.data.size > 0 && ws.readyState === WebSocket.OPEN) {{
              const buf = await ev.data.arrayBuffer();
              ws.send(buf);
            }}
          }};
          recorder.onstop = () => startSegment();
          recorder.start();
          setTimeout(() => recorder.stop(), CHUNK_MS);
        }}

        startBtn.onclick = () => {{
          startBtn.disabled = true;
          stopBtn.disabled  = false;
          startLive();
        }};
        stopBtn.onclick = () => {{
          ws.close();
          stream.getTracks().forEach(t => t.stop());
          startBtn.disabled = false;
          stopBtn.disabled  = true;
        }};
      </script>
    </body>
    </html>
    """, height=650, scrolling=True)
else:
    st.info("📍 Renseigne un nom de course pour activer le live.")