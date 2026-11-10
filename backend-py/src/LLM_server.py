from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, trim_messages
from typing import List, TypedDict
import requests
from dotenv import load_dotenv

# Variabili d'ambiente
load_dotenv(dotenv_path="../.env")

# Il modello si sceglie con LLM_PROVIDER nel .env (vedi providers.py)
from providers import get_llm, count_tokens, PROVIDER, LLM_MODEL

# Definisci lo Stato con cronologia dei messaggi e contesti separati
class State(TypedDict):
    messages: List[HumanMessage | AIMessage | SystemMessage]
    general_context: str
    document_context: List[Document]

# Inizializza il LLM
llm = get_llm(max_tokens=2000, temperature=0.6)
print(f"LLM: {PROVIDER} / {LLM_MODEL}")

# Configura il trimmer
trimmer = trim_messages(
    max_tokens=200,
    strategy="last",
    token_counter=count_tokens,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Funzione per recuperare documenti simili dal database vettoriale
def retrieve(state: State):
    state["document_context"] = []

    if not state["messages"]:
        print("Nessun messaggio disponibile per effettuare la ricerca.")
        return state

    try:
        print([state["messages"][-1].content])

        # Se sto runnando il server in locale
        # response = requests.post(
        #     'http://localhost:5001/similarity_search',
        #     json={"query": [state["messages"][-1].content]}
        # )

        # Se sto runnando il server in un container
        response = requests.post(
            'http://rag_server:5001/similarity_search',
            json={"query": [state["messages"][-1].content]}
        )

        response.raise_for_status()
        retrieved_docs = response.json().get("results", [])
        state["document_context"] = [Document(page_content=doc) for doc in retrieved_docs]
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il recupero dei documenti: {e}")
    
    return state

# Funzione per generare una risposta
def generate(state: State):
    try:
        previous_messages = trimmer.invoke(state["messages"])
    except Exception as e:
        print(f"Errore durante il trimming dei messaggi: {e}")
        return state

    document_context = "\n\n".join(doc.page_content for doc in state["document_context"])

    # Istruzioni e documenti vanno all'inizio; la conversazione deve finire con la domanda
    # dell'utente, altrimenti i modelli più piccoli tendono a ripetere la risposta precedente.
    system_prompt = (
        "Sei un assistente virtuale esperto, progettato per fornire risposte precise, esaustive e professionali "
        "riguardanti l'azienda Ergon Informatica. Rispondi alle domande in italiano con un tono professionale, "
        "ma accessibile e amichevole, e fai riferimento alle informazioni fornite dall'azienda.\n"
        "Rispondi sempre all'ultima domanda dell'utente, usando le informazioni del contesto qui sotto.\n\n"
        f"Contesto:\n\n{document_context}"
    )

    new_messages = [
        {"role": "system", "content": system_prompt},
        *[
            {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
            for msg in previous_messages
        ],
    ]

    try:
        response = llm.invoke(new_messages)
        state["messages"].append(AIMessage(content=response.content))
    except Exception as e:
        print(f"Errore durante l'invocazione dell'LLM: {e}")
    
    return state

# Configurazione dell'app Flask
app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le route

@app.route('/process_message', methods=['POST'])
def process_message():
    data = request.json
    new_message = data['newMessage']
    old_messages = data['oldMessages']

    # I messaggi del frontend hanno type "bot" o "user": li convertiamo nel ruolo giusto
    history = [
        AIMessage(content=msg['message']) if msg.get('type') == 'bot' else HumanMessage(content=msg['message'])
        for msg in old_messages
    ]

    # Evita di contare due volte la domanda se è già in coda alla cronologia
    if history and isinstance(history[-1], HumanMessage) and history[-1].content == new_message:
        history.pop()

    state = {
        "messages": history,
        "general_context": "",
        "document_context": [],
    }

    state["messages"].append(HumanMessage(content=new_message))

    state = retrieve(state)
    state = generate(state)

    # Se l'LLM ha fallito l'ultimo messaggio è ancora la domanda: non rimandarla indietro come risposta
    if not isinstance(state["messages"][-1], AIMessage):
        return jsonify({"error": "Errore durante la generazione della risposta"}), 500

    return jsonify({"response": state["messages"][-1].content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
