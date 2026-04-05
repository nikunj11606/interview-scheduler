import { useState, useEffect, useRef } from 'react'
import './ChatWindow.css'

function ChatWindow() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: 'bot',
            text: 'Hello! I am your AI interview scheduler. Try saying something like "Schedule interview of Nikunj at 5 PM tomorrow"'
        }
    ])
    const [inputText, setInputText] = useState('')
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    function handleSend() {
        if (inputText.trim() === '') return

        const userMessage = {
            id: messages.length + 1,
            role: 'user',
            text: inputText
        }

        const botReply = {
            id: messages.length + 2,
            role: 'bot',
            text: 'Got it! Processing your request...'
        }

        setMessages([...messages, userMessage, botReply])
        setInputText('')
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter') handleSend()
    }

    return (
        <div className="chat-container">
            <div className="chat-header">
                <span className="chat-header-title">Chat</span>
                <div className="chat-online">
                    <span className="chat-online-dot" />
                    online
                </div>
            </div>

            <div className="chat-history">
                {messages.map(message => (
                    <div
                        key={message.id}
                        className={`message ${message.role === 'user' ? 'message-user' : 'message-bot'}`}
                    >
                        <span className="message-label">
                            {message.role === 'user' ? 'you' : 'ai agent'}
                        </span>
                        <div className="message-bubble">
                            {message.text}
                        </div>
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>

            <div className="chat-input-area">
                <div className="chat-input-wrapper">
                    <input
                        className="chat-input"
                        type="text"
                        placeholder='e.g. "Schedule interview of Nikunj at 5 PM tomorrow"'
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />
                    <button className="send-btn" onClick={handleSend}>
                        <svg viewBox="0 0 24 24" fill="none" strokeWidth="2"
                            strokeLinecap="round" strokeLinejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ChatWindow