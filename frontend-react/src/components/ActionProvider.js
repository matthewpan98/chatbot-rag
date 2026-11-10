class ActionProvider {
    constructor(createChatBotMessage, setStateFunc) {
        this.createChatBotMessage = createChatBotMessage;
        this.setState = setStateFunc;
    }

    sendBotResponse(message) {
        // Salva solo il testo grezzo nello stato
        const botMessage = this.createChatBotMessage(message); // Salva il messaggio come testo semplice
        this.updateChatbotState(botMessage);
    }

    updateChatbotState(message) {
        this.setState((prevState) => ({
            ...prevState,
            messages: [...prevState.messages, message],
        }));
    }
}

export default ActionProvider;
