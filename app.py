import streamlit as st
import os
from llama_cpp import Llama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereRerank
from langchain_community.retrievers import BM25Retriever

st.set_page_config(page_title="CyberSOC RAG Chatbot", page_icon="🛡️")

# --- BARRE LATÉRALE : AUTHENTIFICATION & INSTRUCTIONS ---
with st.sidebar:
    st.header("🔑 Authentification")

    st.markdown("""
    **Comment obtenir une clé API Cohere ?**
    1. Créez un compte gratuit sur [Cohere Dashboard](https://dashboard.cohere.com/register)
    2. Allez dans la section **API Keys** (menu de gauche).
    3. Générez une clé "Trial Key" (entièrement gratuite).
    """)

    st.info("💡 Pour des raisons de sécurité, aucune clé API n'est codée en dur dans le code source.")

    cohere_api_key_input = st.text_input("Saisissez votre clé API Cohere :", type="password")
    if not cohere_api_key_input:
        st.warning("⚠️ Veuillez entrer votre clé pour activer le système RAG.")

st.title("🛡️ CyberSOC Assistant (Hybride + Rerank)")

@st.cache_resource
def load_resources():
    # 1. Embeddings et Base Vectorielle (Local)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.load_local("faiss_index_cyber", embeddings, allow_dangerous_deserialization=True)

    # --- PRÉPARATION DES DEUX CHERCHEURS ---
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    docs = list(vector_store.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = 5

    # 2. Le modèle LLM (Mistral local)
    llm = Llama(model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf", n_ctx=2048)

    # On renvoie les DEUX chercheurs séparément
    return faiss_retriever, bm25_retriever, llm

faiss_retriever, bm25_retriever, llm = load_resources()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Posez une question sur une CVE 2024..."):
    if not cohere_api_key_input:
        st.error("🔒 Accès refusé : Veuillez d'abord saisir votre clé API Cohere dans le menu de gauche.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # ========================================================
            # 🧠 NOTRE PROPRE MOTEUR HYBRIDE FAIT MAISON
            # ========================================================
            # 1A. On cherche par le SENS (FAISS)
            docs_faiss = faiss_retriever.invoke(prompt)
            # 1B. On cherche par MOTS-CLÉS (BM25)
            docs_bm25 = bm25_retriever.invoke(prompt)

            # 1C. On fusionne les deux listes en supprimant les doublons
            tous_les_docs = docs_faiss + docs_bm25
            docs_bruts_uniques = []
            textes_vus = set()

            for d in tous_les_docs:
                if d.page_content not in textes_vus:
                    textes_vus.add(d.page_content)
                    docs_bruts_uniques.append(d)
            # ========================================================

            try:
                # 2. Cohere fait le Reranking sur notre liste fusionnée
                reranker = CohereRerank(
                    cohere_api_key=cohere_api_key_input,
                    model="rerank-multilingual-v3.0",
                    top_n=3
                )
                docs_tries = reranker.compress_documents(documents=docs_bruts_uniques, query=prompt)

                # 3. Préparation du contexte pour Mistral
                context = "\n\n".join([d.page_content for d in docs_tries])
                full_prompt = f"[INST] En tant qu'expert CyberSOC, réponds précisément en utilisant ce contexte :\n\n{context}\n\nQuestion: {prompt} [/INST]"

                # 4. Génération
                response = llm(full_prompt, max_tokens=256)["choices"][0]["text"]
                st.markdown(response)

                with st.expander("📚 Sources validées par Reranking"):
                    for d in docs_tries:
                        st.write(f"- {d.metadata.get('cve_id', 'Inconnu')}")

                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error("❌ Erreur d'authentification avec Cohere. Vérifiez votre clé API.")
