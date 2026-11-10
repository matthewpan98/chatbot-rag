# Backend (Python)

Due server [Flask](https://flask.palletsprojects.com/) che insieme rispondono alle domande usando i documenti aziendali (RAG).

> Per avviare tutta l'app (frontend + backend) usa il `docker-compose.yml` nella cartella principale: vedi il [README principale](../README.md).

## Server

### RAG server (`src/RAG_server.py`, porta 5001)

Tiene i documenti in un database vettoriale [FAISS](https://github.com/facebookresearch/faiss). Gli embedding usano il provider scelto (vedi [Scelta del modello](#scelta-del-modello)).

All'avvio:
1. se esiste già un database per il modello di embedding attuale (`database/vector_store/<provider>-<modello>`), lo carica;
2. altrimenti legge i file `.txt` e `.pdf` di `DATA_DIR` (default `demo_data/`), li divide in pezzi da 3000 caratteri e li salva lì.

Così, se cambi modello di embedding, il database viene ricreato in automatico.

| Endpoint | Metodo | Cosa fa |
|---|---|---|
| `/similarity_search` | POST | `{"query": ["domanda"]}` → i 4 pezzi di testo più simili |
| `/add_document` | POST | `{"documents": [{"page_content": "..."}]}` → aggiunge testi al database |
| `/save_vector_store` | POST | salva il database su disco |
| `/load_vector_store` | POST | ricarica il database dal disco |

### LLM server (`src/LLM_server.py`, porta 5002)

Riceve le domande dal frontend, chiede al RAG server i documenti pertinenti e genera la risposta con il modello scelto. La cronologia della chat viene tagliata agli ultimi ~200 token.

| Endpoint | Metodo | Cosa fa |
|---|---|---|
| `/process_message` | POST | `{"newMessage": "...", "oldMessages": [{"type": "user", "message": "..."}]}` → `{"response": "..."}` |

Il comportamento del chatbot (tono, azienda, lingua) si cambia nel messaggio di sistema dentro la funzione `generate`.

## Scelta del modello

Tutta la scelta del modello sta in [`src/providers.py`](src/providers.py): i server non chiamano mai OpenAI o Ollama direttamente. Si cambia con **una riga** nel `.env`:

| `LLM_PROVIDER` | Risposte (default) | Embedding (default) | Serve |
|---|---|---|---|
| `openai` | `gpt-4o-mini` | `text-embedding-3-small` | `OPENAI_API_KEY` |
| `ollama` | `llama3.2:3b` | `nomic-embed-text` | [Ollama](https://ollama.com) avviato, con i modelli scaricati (`ollama pull ...`) |

Per aggiungere un altro fornitore: una voce in `DEFAULTS` e un ramo in `get_llm()` e `get_embeddings()` di `providers.py`, più il pacchetto LangChain corrispondente in `requirements.txt`.

## Variabili d'ambiente

Vanno nel file `.env` nella cartella principale del progetto (vedi `.env.example`):

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `LLM_PROVIDER` | no | `openai` (default) oppure `ollama` |
| `OPENAI_API_KEY` | solo con `openai` | chiave API di OpenAI |
| `LLM_MODEL` | no | modello per le risposte (default del provider) |
| `EMBEDDING_MODEL` | no | modello per gli embedding (default del provider) |
| `OLLAMA_BASE_URL` | no | indirizzo di Ollama (default `http://localhost:11434`; in Docker `http://host.docker.internal:11434`) |
| `LANGCHAIN_API_KEY` | no | chiave LangSmith, per il tracciamento delle chiamate |
| `LANGCHAIN_TRACING_V2` | no | `true` per attivare il tracciamento |
| `DATA_DIR` | no | cartella dei documenti da caricare (default `demo_data/`) |

## Documenti

- `demo_data/`: documenti di esempio con **dati inventati**.
- Per usare documenti propri: mettili in `demo_data/` (o nella cartella indicata da `DATA_DIR`), cancella la cartella `database/vector_store` e riavvia il RAG server.

## Avvio senza Docker

Serve Python 3.12.

```bash
cd backend-py
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

In `src/LLM_server.py`, nella funzione `retrieve`, cambia l'indirizzo del RAG server da `http://rag_server:5001` a `http://localhost:5001`. Poi avvia i due server in due terminali, dalla cartella `src`:

```bash
python RAG_server.py
```

```bash
python LLM_server.py
```

Le variabili vengono lette da `../.env` rispetto alla cartella `src`: copia il file `.env` anche in `backend-py/`, oppure esporta le variabili nel terminale. Con Ollama, l'indirizzo predefinito `http://localhost:11434` funziona già senza modifiche.

## Script di utilità

Da lanciare con il RAG server avviato:

- `doc_loader.py`: carica i documenti di `demo_data/` nel RAG server (utile per aggiungerli senza riavviare)
- `db_interact.py`: salva o ricarica il database su disco (`save` / `load`)
- `database/read_metadata.py`: mostra le informazioni di un file FAISS, es. `python database/read_metadata.py database/vector_store/openai-text-embedding-3-small/index.faiss`
- `trimming.py`: esempio di come viene tagliata la cronologia dei messaggi

I log del RAG server vengono scritti in `src/server.log`.
