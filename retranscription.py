import whisper
import os
from datetime import datetime

# === Config ===
AUDIO_FILE = "audios/test.mp3"
OUTPUT_PATH = "outputs/transcription.txt"

# === Étape 1 : Chargement du modèle Whisper ===
model = whisper.load_model("tiny")  # Tu peux tester avec "small" ou "medium" aussi

# === Étape 2 : Transcription ===
print(f"⏳ Transcription de : {AUDIO_FILE}")
result = model.transcribe(AUDIO_FILE, language="fr")

# === Étape 3 : Sauvegarde du résultat ===
with open(OUTPUT_PATH, "w") as f:
    f.write(result["text"])

print(f"✅ Transcription terminée. Résultat enregistré dans : {OUTPUT_PATH}")

for segment in result["segments"]:
    start = round(segment["start"], 1)
    end = round(segment["end"], 1)
    text = segment["text"].strip()
    print(f"[{start}s - {end}s] {text}")
