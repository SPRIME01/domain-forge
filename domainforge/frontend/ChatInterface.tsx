import React, { useState } from 'react';
import axios from 'axios';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>('');

  const handleSend = async () => {
    if (input.trim()) {
      setMessages([...messages, `You: ${input}`]);
      try {
        const response = await axios.post('/api/chat/send', { content: input });
        const aiMessages = response.data.messages;
        setMessages((prevMessages) => [...prevMessages, ...aiMessages.map((msg: string) => `AI: ${msg}`)]);
      } catch (error) {
        console.error('Error sending message:', error);
      }
      setInput('');
    }
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            {msg}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          aria-label="message input"
        />
        <button onClick={handleSend} aria-label="send">Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
