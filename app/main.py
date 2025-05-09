import os
import streamlit as st
import csv
from pathlib import Path
from datetime import datetime

from app.transcription import transcribe_audio
from app.file_utils import list_transcripts, write_csv, rename_file, OUTPUT_DIR
from app.audio_capture import record_chunk
from app.ui import style_bubble

# === CONFIG STREAMLIT ===
st.set_page_config(page_title="Transcription Audio - Coureurs", layout="wide")

# === SIDEBAR : historique ===
st.sidebar.title("📂 Historique des transcriptions")
query = st.sidebar.text_input("🔍 Rechercher", "")
files = list_transcripts(query)
choice = st.sidebar.selectbox("🔄 Choisir un enregistrement", ["(Nouveau)"] + [f.name for f in files])

if choice != "(Nouveau)":
    path = OUTPUT_DIR / choice
    # Télécharger
    st.sidebar.download_button("📥 Télécharger CSV", data=path.read_bytes(), file_name=path.name)
    # Renommer
    new_name = st.sidebar.text_input("✏️ Renommer", value=choice)
    if st.sidebar.button("💾 Enregistrer nom"):
        rename_file(path, new_name)
        st.sidebar.success(f"Renommé en {new_name}")
    # Aperçu
    st.sidebar.markdown("### Aperçu")
    for row in csv.DictReader(path.open(encoding="utf-8")):
        style_bubble(row["timestamp (s)"], row["texte"], row.get("tag","None"))

# === MAIN ===
st.title("🚴‍♂️ Transcription Audio - Coureurs")
mode = st.selectbox("⚙️ Mode", ["Upload", "Live"], index=0)
course = st.text_input("📌 Nom de la course", placeholder="ex : Étape 1 - Paris-Nice")

if mode == "Upload":
    audio_file = st.file_uploader("🎧 .wav/.mp3", type=["wav","mp3"])
    if audio_file and course:
        # sauvegarde temporaire
        tmp = record_chunk(duration=0)  # on crée juste le fichier
        # écriture manuellement
        with open(tmp, "wb") as f:
            f.write(audio_file.read())
        texte = transcribe_audio(str(tmp))
        st.subheader("📝 Résultat")
        st.write(texte)
        # Enregistrement CSV
        ts0 = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = OUTPUT_DIR / f"{course}_{ts0}.csv"
        write_csv(out_path, [[0, texte, "None"]], header=["timestamp (s)","texte","tag"])
        st.success(f"Transcription sauvegardée : {out_path.name}")
        os.remove(tmp)

elif mode == "Live":
    # état
    if "on" not in st.session_state:
        st.session_state.on = False
        st.session_state.csv = None
        st.session_state.msgs = []

    col1, col2 = st.columns([1,1])
    # Démarrer
    if not st.session_state.on:
        if col1.button("▶️ Démarrer", key="start"):
            if course.strip():
                st.session_state.on = True
                # init CSV unique
                ts0 = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                st.session_state.csv = OUTPUT_DIR / f"{course}_{ts0}.csv"
                write_csv(st.session_state.csv, [], header=["timestamp (s)","texte","tag"])
            else:
                st.error("Entrez un nom de course.")
    else:
        # Stop
        if col1.button("⏹️ Arrêter", key="stop"):
            st.session_state.on = False
    # capture tant que live_on
    if st.session_state.on and st.session_state.csv:
        tmp = record_chunk()
        texte = transcribe_audio(str(tmp))
        ts = datetime.now().strftime("%H:%M:%S")
        tag = "Important" if col2.button("🚩 Important", key=ts) else "None"
        st.session_state.msgs.append((ts, texte, tag))
        write_csv(st.session_state.csv, [[ts, texte, tag]])
        os.remove(tmp)
        # affichage fil
        st.subheader("💬 Live")
        for t,m,ta in reversed(st.session_state.msgs):
            style_bubble(t, m, ta)
        # relance
        st.experimental_rerun()