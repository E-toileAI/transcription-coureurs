# 🚴 Transcription Coureurs Live – MVP

Cette application permet de transcrire les communications radio des coureurs cyclistes pendant une course, de manière automatique et visuelle.

---

## 🎯 Fonctionnalités

- Transcription automatique des fichiers `.wav` ou `.mp3` via Whisper (OpenAI)
- Interface web simple avec affichage des messages par segment (style chat)
- Champ pour nommer chaque course (ex : Étape 6 - Tour du Jura)
- Historique des transcriptions stockées et consultables
- Téléchargement direct des `.csv` générés

---

## 🛠 Prérequis

- Python 3.8+
- Environnement virtuel recommandé

### 📦 Installation des dépendances

```bash
pip install streamlit openai-whisper
