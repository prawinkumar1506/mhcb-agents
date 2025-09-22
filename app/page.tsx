'use client';

import React, { useEffect, useRef, useState } from 'react';

const ChatbotPage = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm here to support you with your mental health journey. I can help with anxiety, stress, depression, relationships, and more. How are you feeling today?", sender: 'bot' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [isTyping, setIsTyping] = useState(false);
  const [showCrisisBanner, setShowCrisisBanner] = useState(false);
  const chatMessagesRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const sendMessage = async () => {
    const message = inputValue.trim();
    if (!message) return;

    setMessages(prev => [...prev, { text: message, sender: 'user' }]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          user_id: userId,
          conversation_id: conversationId
        })
      });

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      setIsTyping(false);
      setMessages(prev => [...prev, { text: data.response, sender: 'bot' }]);

      if (data.crisis_detected) {
        setShowCrisisBanner(true);
      }

      if (data.escalation_triggered) {
        setMessages(prev => [...prev, { text: "I've detected that you might benefit from speaking with a human counselor. Would you like me to help you schedule an appointment?", sender: 'bot' }]);
      }

    } catch (error) {
      console.error('Error:', error);
      setIsTyping(false);
      setMessages(prev => [...prev, { text: "I'm sorry, I'm having trouble connecting right now. Please try again.", sender: 'bot' }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <>
      <style jsx global>{`
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        // body {
        //     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        //     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        //     height: 100vh;
        //     display: flex;
        //     align-items: center;
        //     justify-content: center;
        // }
        
        .chat-container {
            //width: 100vw;
            //max-width: 800px;
            height: 100vh;
            background: green;
           // border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: #4f46e5;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8fafc;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .message.bot .message-content {
            background: white;
            border: 1px solid #e2e8f0;
            color: #334155;
        }
        
        .message.user .message-content {
            background: #4f46e5;
            color: white;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #d1d5db;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .chat-input input:focus {
            border-color: #4f46e5;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        
        .chat-input button:hover {
            background: #4338ca;
        }
        
        .chat-input button:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            padding: 12px 16px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            color: #6b7280;
            font-style: italic;
            max-width: 70%;
        }
        
        .crisis-banner {
            background: #dc2626;
            color: white;
            padding: 10px 20px;
            text-align: center;
            font-size: 12px;
        }
      `}</style>
      <div className="chat-container">
        {showCrisisBanner && (
          <div className="crisis-banner" id="crisisBanner">
            🚨 If you're in crisis, please call: <strong>988 (US)</strong> or <strong>+91-9152987821 (India)</strong>
          </div>
        )}
        
        <div className="chat-header">
            <h1>Mental Health Support</h1>
            <p>Your compassionate AI companion for mental wellness</p>
        </div>
        
        <div className="chat-messages" ref={chatMessagesRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              <div className="message-content">
                {msg.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              AI is thinking...
            </div>
          )}
        </div>
        
        <div className="chat-input">
            <input 
              type="text" 
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..." 
            />
            <button onClick={sendMessage} disabled={isTyping}>Send</button>
        </div>
      </div>
    </>
  );
};

export default ChatbotPage;
