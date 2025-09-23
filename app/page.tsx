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
        
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f0fdf4; /* Light green background */
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            width: 100vw;
            max-width: 800px;
            height: 100vh;
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: #10b981; /* Green header */
            color: white;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #059669;
        }
        
        .chat-header h1 {
            font-size: 28px;
            margin-bottom: 5px;
            font-weight: 700;
        }
        
        .chat-header p {
            opacity: 0.95;
            font-size: 15px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f0fdf4; /* Light green message area */
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
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 20px;
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        
        .message.bot .message-content {
            background: #e0ffe0; /* Very light green for bot messages */
            border: 1px solid #a7f3d0;
            color: #1f2937;
            border-bottom-left-radius: 5px;
        }
        
        .message.user .message-content {
            background: #34d399; /* Green for user messages */
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .chat-input {
            padding: 15px 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 18px;
            border: 1px solid #d1d5db;
            border-radius: 25px;
            outline: none;
            font-size: 15px;
            transition: border-color 0.2s;
        }
        
        .chat-input input:focus {
            border-color: #10b981; /* Green focus border */
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
        }
        
        .chat-input button {
            padding: 12px 25px;
            background: #10b981; /* Green send button */
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        
        .chat-input button:hover {
            background: #059669; /* Darker green on hover */
        }
        
        .chat-input button:disabled {
            background: #a7f3d0;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px 18px;
            background: #e0ffe0;
            border: 1px solid #a7f3d0;
            border-radius: 20px;
            min-width: 75px;
            min-height: 40px;
            border-bottom-left-radius: 5px;
            box-sizing: border-box;
            /* Ensure the container itself is visible */
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Add a subtle shadow to make it pop */
        }

        .typing-indicator span {
            display: inline-block; /* Ensure proper rendering for animation */
            width: 10px;
            height: 10px;
            margin: 0 4px;
            background-color: #10b981;
            border-radius: 50%;
            opacity: 0.8; /* Further increased opacity */
            animation: pulse 1.2s infinite ease-in-out; /* Slightly faster animation */
            vertical-align: middle; /* Align dots vertically */
        }

        .typing-indicator span:nth-child(1) {
            animation-delay: -0.4s; /* Adjusted delay */
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: -0.2s; /* Adjusted delay */
        }

        .typing-indicator span:nth-child(3) {
            animation-delay: 0s;
        }

        @keyframes pulse {
            0%, 80%, 100% {
                opacity: 0.4;
                transform: scale(1);
            }
            40% {
                opacity: 1;
                transform: scale(1.2);
            }
        }
        
        .crisis-banner {
            background: #ef4444; /* Red for crisis banner */
            color: white;
            padding: 10px 20px;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
        }
        
        .bold-text {
            font-weight: bold;
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
              <div 
                className="message-content" 
                dangerouslySetInnerHTML={{ __html: msg.text.replace(/\*\*(.*?)\*\*/g, '<span class="bold-text">$1</span>').replace(/\n/g, '<br />') }}
              ></div>
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <span></span><span></span><span></span>
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
