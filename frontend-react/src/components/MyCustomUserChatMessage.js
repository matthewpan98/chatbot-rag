import React from 'react';

const MyCustomUserChatMessage = (props) => {
  return (
    <div className="my-custom-user-chat-message">
      {/* Implementa il tuo messaggio di chat utente personalizzato qui */}
      <p>{props.message}</p>
    </div>
  );
};

export default MyCustomUserChatMessage;