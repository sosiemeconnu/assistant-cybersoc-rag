# 🛡️ Assistant CyberSOC - Architecture RAG Hybride & Souverain

> **Projet de fin de semestre / Ingénierie Cybersécurité**
> *Conçu pour l'assistance à l'analyse de vulnérabilités (CVE) en environnement Zero-Trust.*

L'**Assistant CyberSOC** est un outil d'Intelligence Artificielle Générative développé pour les analystes SOC. Face à l'impossibilité d'utiliser des modèles Cloud publics en entreprise (risques de fuite de données et hallucinations), ce projet propose une architecture **RAG (Retrieval-Augmented Generation) 100% locale, souveraine et vérifiable**.

L'outil élimine le temps de recherche documentaire fastidieux et synthétise les menaces avec une fiabilité mathématiquement prouvée (évaluée via le framework RAGAS), transformant ainsi l'expert en véritable "Analyste Augmenté".

## ✨ Fonctionnalités Clés

* **Zéro Hallucination :** Le modèle ne répond qu'en se basant sur la documentation technique fournie (Base NVD).
* **Moteur de Recherche Hybride "Fait Maison" :** Combinaison de la recherche sémantique (**FAISS**) et de la recherche lexicale par mots-clés (**BM25**) pour une précision absolue sur les identifiants CVE.
* **Filtrage Intelligent (Reranking) :** Utilisation de l'API Cohere Rerank pour extraire le contexte de plus haute précision et gérer les requêtes multilingues.
* **Souveraineté Totale :** Génération de texte assurée par **Mistral-7B** (quantifié en 4-bits) tournant localement sur processeur (CPU).
* **Déploiement Sécurisé :** Application conteneurisée via **Docker** pour une intégration isolée sur l'infrastructure du SOC.

## 🏗️ Architecture Technique

* **Orchestration :** Framework LangChain
* **Embeddings :** Hugging Face (`all-MiniLM-L6-v2`)
* **Vector Store :** FAISS + Algorithme BM25
* **Reranker :** Cohere (`rerank-multilingual-v3.0`)
* **LLM Local :** Mistral-7B-Instruct (format GGUF `Q4_K_M` via `llama.cpp`)
* **Interface Utilisateur :** Streamlit

---

## 🚀 Guide d'Installation et de Déploiement

### 1. Prérequis
Pour des raisons de taille et de sécurité, le modèle LLM n'est pas inclus dans ce dépôt. 
* Téléchargez le modèle **Mistral-7B-Instruct-v0.1.Q4_K_M.gguf** (environ 4 Go) depuis Hugging Face.
* Placez ce fichier `.gguf` à la racine du projet (au même niveau que `app.py`).

### 2. Déploiement via Docker (Recommandé pour les SOC)
Assurez-vous d'avoir [Docker](https://www.docker.com/) installé sur votre machine ou votre serveur.

Construisez l'image Docker :
```bash
docker build -t cybersoc-assistant .
