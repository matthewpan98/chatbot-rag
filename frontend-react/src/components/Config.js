// Config starter code
import { createChatBotMessage } from "react-chatbot-kit";
import MyAvatar from './MyAvatar';
import MyCustomChatMessage from './MyCustomChatMessage';
import MyCustomAvatar from './MyCustomAvatar';
import MyCustomUserChatMessage from './MyCustomUserChatMessage';



const config = {
  // cambia questo con il messaggio che vuoi inviare all'utente quando apre per la prima volta il chatbot
  initialMessages: [createChatBotMessage(`Ciao, sono il tuo assistente virtuale. Come posso aiutarti oggi?`)],
  botName: "Assistente LLM",
  customStyles: {
    botMessageBox: {
      backgroundColor: '#123456',
    },
    chatButton: {
      backgroundColor: '#abcdef',
    },
  },
  customComponents: {
    header: () => <div style={{ backgroundColor: '#123456', padding: '10px', color: '#fff', textAlign: 'center' }}>ASSISTENTE VIRTUALE LLM - ERGON</div>,
    botAvatar: (props) => <MyAvatar {...props} />,
    botChatMessage: (props) => <MyCustomChatMessage {...props} />,
    userAvatar: (props) => <MyCustomAvatar {...props} />,
    userChatMessage: (props) => <MyCustomUserChatMessage {...props} />
  },
};

export default config;