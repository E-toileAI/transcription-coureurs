## 1️⃣ Installer les dépendances

\`\`\`bash
# Pour l'API (FastAPI + WebSocket + Whisper)
pip install -r api/requirements.txt  # fastapi, uvicorn, openai, python-dotenv, sqlite3, etc.

# Pour l'interface Streamlit
# dans ui/requirements.txt
pip install -r ui/requirements.txt   # streamlit, python-dotenv, etc.
\`\`\`

---

## 2️⃣ Lancer le micro-service FastAPI (backend)

\`\`\`bash
# Positionnez-vous dans le dossier api/
cd api

# Démarre Uvicorn avec reload pour le développement
uvicorn transcriber_service:app --reload --host 0.0.0.0 --port 8000
\`\`\`

> ⚙️ Le service écoute les WebSocket sur \`ws://localhost:8000/ws/transcribe/{course}\`

---

## 3️⃣ Lancer l'interface Streamlit (frontend)

\`\`\`bash
# Positionnez-vous dans le dossier ui/
cd ui

# Lance l'application Streamlit
streamlit run app.py --server.port 8501
\`\`\`

> 🚀 Accessible à http://localhost:8501

---

## 4️⃣ Interroger la base SQLite

\`\`\`bash
# Lancer le client SQLite
sqlite3 transcripts.db

# Exemples de requêtes SQL
sqlite> .tables                        # liste des tables
sqlite> SELECT * FROM msgs LIMIT 10;  # affiche les 10 premiers messages
\`\`\`

---

## 5️⃣ Dockerisation & Déploiement

\`\`\`bash
# 5.1) Construire l'image pour l'API
docker build -t transcription-api:latest ./api

# 5.2) Lancer le conteneur backend
docker run -d -p 8000:8000 transcription-api:latest

# 5.3) Construire l'image pour l'UI
docker build -t transcription-ui:latest ./ui

# 5.4) Lancer le conteneur frontend
docker run -d -p 8501:8501 transcription-ui:latest
\`\`\`

---

## 6️⃣ Tests unitaires & Qualité de code

\`\`\`bash
# Tests backend (avec pytest)
cd api
pytest --maxfail=1 --disable-warnings -q

# Linters (flake8, etc.)
flake8 .
\`\`\`

---

## 7️⃣ Nettoyage

\`\`\`bash
# Supprimer la base SQLite
rm -f transcripts.db

# Supprimer conteneurs Docker
docker rm -f \$(docker ps -aq)
# Supprimer images Docker
docker rmi \$(docker images -q)
\`\`\`

---

## 8️⃣ Gestion Git

\`\`\`bash
# Initialisation
git init

# Ajouter les fichiers
git add .

git commit -m "Initial commit"

# Lier un remote externe
git remote add origin <URL-de-ton-repo>

# Push
git push -u origin main
\`\`\`

---

