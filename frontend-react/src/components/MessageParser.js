import LangchainProcessor from './LangchainProcessor';

class MessageParser {
    constructor(actionProvider, state, createChatBotMessage) {
        this.actionProvider = actionProvider;
        this.state = state;
        this.createChatBotMessage = createChatBotMessage;
    }

    async parse(incomingMessage) {
        try {
            // Use the processor to get a reply
            const reply = await LangchainProcessor(incomingMessage, this.state.messages);

            // Send the reply using the actionProvider
            this.actionProvider.sendBotResponse(reply);
        } catch (error) {
            console.error(error);
            this.actionProvider.sendBotResponse(
                "Si è verificato un errore nel contattare il server. Riprova tra qualche istante."
            );
        }
    }
}

export default MessageParser;
