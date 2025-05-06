import streamlit as st
import whisper
import tempfile
import os
import csv
import re
from datetime import datetime

# 👉 Obligatoire en tout début
st.set_page_config(page_title="Transcription Coureurs", layout="centered")

# === 💾 Création dossier outputs si nécessaire ===
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# === 📚 Historique des transcriptions dans la sidebar ===
csv_files = sorted([f for f in os.listdir("outputs") if f.endswith(".csv")], reverse=True)
selected_file = st.sidebar.selectbox("📁 Historique des transcriptions", ["(Nouveau fichier)"] + csv_files)

# === 🧾 Si consultation d’un ancien fichier ===
if selected_file != "(Nouveau fichier)":
    st.markdown("<h1 style='text-align: center;'>📂 Consultation d’une transcription</h1>", unsafe_allow_html=True)
    with open(f"outputs/{selected_file}", "r", encoding="utf-8") as file:
        lines = file.readlines()[1:]
        for line in lines:
            timestamp, text = line.strip().split(",", 1)
            st.markdown(f"""
                <div class="message-bubble">
                    <div class="timestamp">🕒 {timestamp} sec</div>
                    <div>{text}</div>
                </div>
            """, unsafe_allow_html=True)
    st.stop()

# === 🎧 Interface d’upload de nouveau fichier ===
st.markdown("<h1 style='text-align: center;'>🚴‍♂️ Transcription Audio - Coureurs Live</h1>", unsafe_allow_html=True)

course_name = st.text_input("📌 Nom de la course", placeholder="ex : Étape 5 - Paris-Nice")
audio_file = st.file_uploader("🎧 Dépose un fichier audio (.wav ou .mp3)", type=["wav", "mp3"])

# === CSS custom pour style "chat" ===
st.markdown("""
    <style>
    .message-bubble {
        background-color: #1c1c1e;
        color: white;
        padding: 12px 15px;
        margin-bottom: 10px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .timestamp {
        color: #999;
        font-size: 0.8rem;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# === 🚀 Traitement du fichier ===
if audio_file and course_name:
    st.audio(audio_file, format="audio/wav")
    st.write("⏳ Transcription en cours...")

    # 🔧 Sauvegarde du fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    # 🧠 Transcription via Whisper local
    model = whisper.load_model("base")  # tu peux changer par "medium" si plus puissant
    result = model.transcribe(tmp_path, language="fr")

    # 📝 Affichage des segments dans des bulles
    st.subheader("📝 Messages détectés")
    for segment in result["segments"]:
        start = round(segment["start"], 1)
        text = segment["text"].strip()
        st.markdown(f"""
            <div class="message-bubble">
                <div class="timestamp">🕒 {start} sec</div>
                <div>{text}</div>
            </div>
        """, unsafe_allow_html=True)

    # 💾 Sauvegarde dans CSV
    safe_name = re.sub(r'\W+', '_', course_name.lower())
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_filename = f"{safe_name}_{date_str}.csv"
    csv_path = os.path.join("outputs", csv_filename)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp (s)", "message"])
        for segment in result["segments"]:
            writer.writerow([round(segment["start"], 1), segment["text"].strip()])

    # ✅ Confirmation et bouton de téléchargement
    st.success(f"✅ Transcription enregistrée sous : `{csv_filename}`")
    st.download_button("📥 Télécharger la transcription (.csv)", data=open(csv_path, "rb").read(), file_name=csv_filename, mime="text/csv")

elif audio_file and not course_name:
    st.warning("❗ Merci de renseigner un nom de course avant d’envoyer un fichier audio.")
