# Utiliser une image Python officielle légère
FROM python:3.10-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . /app

# Installer les dépendances (inclus le module hybride BM25)
RUN pip install --no-cache-dir streamlit langchain langchain-huggingface langchain-community langchain-cohere faiss-cpu llama-cpp-python rank_bm25

# Exposer le port de Streamlit
EXPOSE 8501

# Lancer l'application CyberSOC
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
