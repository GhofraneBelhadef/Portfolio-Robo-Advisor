# rag_engine.py

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Chargement des documents (exemple : un fichier texte)
loader = TextLoader("data/faq_investment.txt")  # Modifie ce chemin vers tes docs
docs = loader.load()

# Split des documents en chunks plus petits
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(docs)

# Initialisation des embeddings HuggingFace (modèle léger)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

try:
    # Création de la base vectorielle FAISS avec les chunks
    vectordb = FAISS.from_documents(split_docs, embeddings)
except ImportError:
    print("Erreur embeddings FAISS: Veuillez installer faiss-cpu ou faiss-gpu")

def get_recommendation_for_profile(profile: str, threshold: float = 1.0) -> str:
    if 'vectordb' not in globals():
        return "La base vectorielle n'est pas initialisée."

    # Enrichir la requête pour améliorer la recherche
    query = f"Profil investisseur: {profile}"

    try:
        results = vectordb.similarity_search_with_score(query, k=3)
    except Exception:
        # Fallback si pas supporté
        results = [(doc, 0) for doc in vectordb.similarity_search(query, k=3)]

    # Debug : afficher scores dans la console
    for doc, score in results:
        print(f"Score: {score:.4f} — Contenu extrait: {doc.page_content[:100]}...")

    # Filtrer les docs par score (distance faible = plus proche)
    filtered = [doc.page_content.strip() for doc, score in results if score < threshold]

    if not filtered:
        return "Aucune recommandation trouvée."

    return "\n---\n".join(filtered)
