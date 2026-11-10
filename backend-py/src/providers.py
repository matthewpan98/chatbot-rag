"""Sceglie il modello (LLM + embedding) in base alle variabili d'ambiente.

Per cambiare modello basta una riga nel .env:
    LLM_PROVIDER=openai   (default)  -> serve OPENAI_API_KEY
    LLM_PROVIDER=ollama              -> gratis, modelli in locale con Ollama

Opzionali:
    LLM_MODEL          modello per le risposte (default dipende dal provider)
    EMBEDDING_MODEL    modello per gli embedding (default dipende dal provider)
    OLLAMA_BASE_URL    indirizzo di Ollama (default http://localhost:11434)

Per aggiungere un altro provider: aggiungi una voce a DEFAULTS e un ramo
in get_llm() e get_embeddings().
"""

import os

DEFAULTS = {
    "openai": {"llm": "gpt-4o-mini", "embedding": "text-embedding-3-small"},
    "ollama": {"llm": "llama3.2:3b", "embedding": "nomic-embed-text"},
}

PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()
if PROVIDER not in DEFAULTS:
    raise ValueError(f"LLM_PROVIDER '{PROVIDER}' non supportato. Valori ammessi: {', '.join(DEFAULTS)}")

LLM_MODEL = os.getenv("LLM_MODEL") or DEFAULTS[PROVIDER]["llm"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or DEFAULTS[PROVIDER]["embedding"]
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm(max_tokens=2000, temperature=0.6):
    """Modello che genera le risposte."""
    if PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, max_tokens=max_tokens, temperature=temperature)

    if PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL,
                          num_predict=max_tokens, temperature=temperature)


def get_embeddings():
    """Modello che trasforma i testi in vettori per la ricerca nei documenti."""
    if PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=EMBEDDING_MODEL)

    if PROVIDER == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def embedding_id():
    """Nome della cartella del database: cambia se cambia il modello di embedding,
    così un database creato con un modello non viene usato con un altro."""
    safe_model = EMBEDDING_MODEL.replace("/", "_").replace(":", "_")
    return f"{PROVIDER}-{safe_model}"


def count_tokens(messages):
    """Stima dei token (circa 4 caratteri per token), uguale per tutti i provider.
    Serve per tagliare la cronologia della chat senza dipendere dal tokenizer del modello."""
    total = 0
    for msg in messages:
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        total += len(content) // 4 + 4
    return total
