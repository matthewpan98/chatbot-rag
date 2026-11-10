# Frontend (React)

Interfaccia della chat, costruita con [React](https://react.dev/) e [react-chatbot-kit](https://fredrikoseberg.github.io/react-chatbot-kit-docs/).

> Per avviare tutta l'app (frontend + backend) usa il `docker-compose.yml` nella cartella principale: vedi il [README principale](../README.md).

## Struttura

- `src/App.js`: punto d'ingresso, monta il componente della chat
- `src/components/Config.js`: configurazione della chat (messaggio iniziale, header, avatar)
- `src/components/MessageParser.js` e `ActionProvider.js`: ricevono il messaggio dell'utente e gestiscono la risposta
- `src/components/LangchainProcessor.js`: invia il messaggio al backend
- `src/components/MyCustom*.js`, `MyAvatar.js`: componenti grafici dei messaggi e degli avatar
- `public/img/`: immagini degli avatar

## Collegamento al backend

Il frontend invia le domande a `http://localhost:5002/process_message` (il server LLM), con questo formato:

```json
{ "newMessage": "testo della domanda", "oldMessages": [{ "message": "..." }] }
```

Per cambiare indirizzo modifica `src/components/LangchainProcessor.js`.

## Sviluppo in locale

Serve Node.js (versione 20 consigliata).

```bash
npm install
npm start
```

L'app si apre su http://localhost:3000 e si ricarica a ogni modifica. Il backend deve essere già avviato.

Altri comandi:

- `npm run build`: crea la versione di produzione nella cartella `build/`
- `npm test`: avvia i test

## Solo il frontend con Docker

L'immagine compila l'app e la serve con Nginx sulla porta 80:

```bash
docker build -t chatbot-frontend .
docker run -d --name chatbot-frontend -p 3000:80 chatbot-frontend
```
