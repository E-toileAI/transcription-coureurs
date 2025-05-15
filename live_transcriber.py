# live_transcriber.py

import os
import time
import csv
import tempfile
from pathlib import Path
from datetime import datetime
import argparse

import sounddevice as sd
from scipy.io.wavfile import write
import openai

from dotenv import load_dotenv
import os

load_dotenv()
# DEBUG : afficher ce qui est lu
print("DEBUG: OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

def transcribe_api(path: str) -> str:
    """Appelle l'API Whisper et renvoie la transcription brute."""
    try:
        with open(path, "rb") as f:
            resp = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                language="fr"
            )
        return resp.strip()
    except Exception as e:
        print(f"[!] Erreur transcription API : {e}")
        return None  # signale l'erreur

def record_and_transcribe(csv_path: Path, chunk_sec: int, fs: int):
    """Enregistre un chunk audio, le transcrit et l'ajoute au CSV."""
    # 1) Record
    audio = sd.rec(int(chunk_sec * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    # 2) Temp WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        write(tmp.name, fs, audio)
        tmp_path = tmp.name
    # 3) Transcription
    text = transcribe_api(tmp_path)
    # nettoie le temp
    try: os.remove(tmp_path)
    except: pass
    if text is None:
        return False  # arrêt en cas d'erreur
    # 4) Timestamp & write CSV
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([ts, text])
    print(f"[+] {ts} → {len(text)} chars")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Live transcription via API Whisper"
    )
    parser.add_argument("--course", required=True,
                        help="Nom de la course (será in CSV)")
    parser.add_argument("--duration", type=int, default=3600,
                        help="Durée totale en secondes (défaut : 3600 = 1 h)")
    parser.add_argument("--chunk", type=int, default=5,
                        help="Taille des tranches en secondes (défaut : 5)")
    parser.add_argument("--fs", type=int, default=16000,
                        help="Fréquence d'échantillonnage (défaut :16000)")
    parser.add_argument("--out", default="outputs",
                        help="Dossier de sortie CSV")
    args = parser.parse_args()

    # 1) Prépa API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("❌ Il faut définir OPENAI_API_KEY dans ton .env ou l'env.")
        return

    # 2) Prépare le CSV
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    start_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_path = out_dir / f"{args.course}_{start_ts}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp (s)", "texte"])

    # 3) Boucle principale
    print(f"▶️ Démarrage transcription live pour {args.duration}s "
          f"({args.chunk}s/chunk) dans `{csv_path}`")
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed >= args.duration:
            print("⏹️ Durée atteinte, arrêt.")
            break
        ok = record_and_transcribe(csv_path, args.chunk, args.fs)
        if not ok:
            print("⚠️ Arrêt anticipé suite à une erreur API.")
            break
        # petite pause pour éviter chevauchement
        time.sleep(0.1)

    print("✅ Session terminée. Fichier :", csv_path)

if __name__ == "__main__":
    main()
