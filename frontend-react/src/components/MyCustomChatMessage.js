import React from 'react';
import ReactMarkdown from 'react-markdown';

const MyCustomChatMessage = (props) => {
  return (
    <div className="my-custom-chat-message">
      <ReactMarkdown>{props.message}</ReactMarkdown>
    </div>
  );
};

export default MyCustomChatMessage;