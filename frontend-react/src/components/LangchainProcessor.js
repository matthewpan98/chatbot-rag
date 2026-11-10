// this component is responsible for processing new messages from the user and getting a reply from OpenAI
// it uses a human/system messages array that is sent in continously to OpenAI

const LangchainProcessor = async (newMessage, oldMessages) => {
    const requestBody = {
        newMessage: newMessage,
        oldMessages: oldMessages
    };

    const response = await fetch("http://localhost:5002/process_message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
    });

    const responseText = await response.text(); // Leggi la risposta come testo
    console.log("Server response:", responseText); // Logga la risposta del server

    if (!response.ok) {
        throw new Error("Failed to get a response from the server.");
    }

    const data = JSON.parse(responseText); // Parsea il testo come JSON

    // Convert the markdown response to HTML
    // const htmlResponse = markdown.render(data.response);
    // data.response = htmlResponse;

    return data.response;

    
};

export default LangchainProcessor;