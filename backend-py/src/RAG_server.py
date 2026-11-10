import logging
from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os

from dotenv import load_dotenv

# Variabili d'ambiente
# Carica le variabili d'ambiente dal file .env
load_dotenv(dotenv_path="../.env")

# Il modello si sceglie con LLM_PROVIDER nel .env (vedi providers.py)
from providers import get_embeddings, embedding_id

# Inizializza il modello di embedding
embedding_model = get_embeddings()

# Inizializza un vector store vuoto
vector_store = FAISS.from_texts([""], embedding=embedding_model)

# Percorso del vector store: una cartella per ogni modello di embedding
# (es. database/vector_store/openai-text-embedding-3-small)
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "../database/vector_store", embedding_id())

# Cartella con i documenti da caricare all'avvio (default: documenti demo)
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "../demo_data"))

# Configurazione dell'app Flask
app = Flask(__name__)

# Configura il logger
logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')


@app.route('/add_document', methods=['POST'])
def add_documents():
    documents = request.json['documents']
    
    # Converti i dizionari in istanze di Document
    document_objects = [Document(page_content=doc['page_content']) for doc in documents]
    
    vector_store.add_documents(document_objects)
    
    # Stampa informazioni sull'operazione
    print(f"Added {len(document_objects)} documents to vector store")
    
    return jsonify({"status": "success"})


@app.route('/similarity_search', methods=['POST'])
def similarity_search():
    query_embedding = request.json['query']
    results = vector_store.similarity_search(query_embedding[0], k=4)
    
    # Log informazioni sull'operazione
    logging.info(f"Performed similarity search with query: {query_embedding}")
    logging.info(f"Results: {[doc.page_content for doc in results]}")
    
    return jsonify({"results": [doc.page_content for doc in results]})


@app.route('/save_vector_store', methods=['POST'])
def save_vector_store():
    vector_store.save_local(VECTOR_STORE_PATH)
    
    # Log informazioni sull'operazione
    logging.info(f"Saved vector store to {VECTOR_STORE_PATH}")
    
    return jsonify({"status": "vector store saved"})


@app.route('/load_vector_store', methods=['POST'])
def load_vector_store():
    global vector_store
    # Controlla se il file del vector store esiste
    if os.path.exists(VECTOR_STORE_PATH):
        # Carica il vector store dal file
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings=embedding_model, 
            allow_dangerous_deserialization=True # Abilita questo se ti fidi della fonte dei dati
        )
        
        # Log informazioni sul vector store caricato
        file_size = os.path.getsize(VECTOR_STORE_PATH + "/index.faiss")
        logging.info(f"Size of the FAISS file: {file_size / (1024 * 1024):.2f} MB")
        logging.info(f"Number of vectors: {vector_store.index.ntotal}")
        logging.info(f"Dimension of vectors: {vector_store.index.d}")
        logging.info(f"Metric type: {vector_store.index.metric_type}")
        
        return jsonify({"status": "vector store loaded"})
    else:
        # Log errore se il file del vector store non viene trovato
        logging.error(f"Vector store file not found at {VECTOR_STORE_PATH}")
        return jsonify({"status": "vector store file not found"}), 404


def load_documents_from_dir(directory):
    """Legge i file .txt e .pdf di una cartella e li divide in pezzi."""
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    docs = []
    for filename in sorted(os.listdir(directory)):
        path = os.path.join(directory, filename)
        if filename.endswith(".txt"):
            docs.extend(TextLoader(path, encoding="utf-8").load())
        elif filename.endswith(".pdf"):
            docs.extend(PyPDFLoader(path).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
    return splitter.split_documents(docs)


def init_vector_store():
    """All'avvio: carica il database salvato, oppure lo crea dai documenti in DATA_DIR."""
    global vector_store

    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings=embedding_model,
            allow_dangerous_deserialization=True,
        )
        print(f"Vector store caricato da {VECTOR_STORE_PATH} ({vector_store.index.ntotal} vettori)")
        return

    if not os.path.isdir(DATA_DIR):
        print(f"Nessun vector store salvato e nessuna cartella documenti in {DATA_DIR}: parto vuoto")
        return

    chunks = load_documents_from_dir(DATA_DIR)
    if not chunks:
        print(f"Nessun documento .txt o .pdf in {DATA_DIR}: parto vuoto")
        return

    vector_store = FAISS.from_documents(chunks, embedding=embedding_model)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Caricati {len(chunks)} pezzi di testo da {DATA_DIR} e salvati in {VECTOR_STORE_PATH}")


if __name__ == '__main__':
    init_vector_store()
    app.run(host='0.0.0.0', port=5001)