import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model(name: str = "base"):
    """Charge et met en cache le modèle Whisper."""
    return whisper.load_model(name)

MODEL = load_whisper_model()

def transcribe_audio(path: str, language: str = "fr") -> str:
    """
    Transcrit le fichier audio donné en utilisant Whisper.
    Retourne le texte (vide en cas d'erreur).
    """
    try:
        with st.spinner("🔊 Transcription en cours…"):
            res = MODEL.transcribe(path, language=language)
            return res.get("text", "").strip()
    except Exception as e:
        st.error(f"Erreur de transcription : {e}")
        return ""