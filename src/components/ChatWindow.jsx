import { useState, useEffect, useRef } from 'react'
import './ChatWindow.css'

function ChatWindow({ setCandidates, setInterviewers }) {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: 'bot',
            text: 'Hello! I am your AI interview scheduler.'
        }
    ])
    const [inputText, setInputText] = useState('')
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    async function handleSend() {
        if (inputText.trim() === '') return

        const userMessage = {
            id: messages.length + 1,
            role: 'user',
            text: inputText
        }

        setMessages(prev => [...prev, userMessage])
        setInputText('')

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: inputText })
            })

            const data = await response.json()

            // Fetch updated data from backend
            const updatedData = await fetch('http://127.0.0.1:8000/data')
            const freshData = await updatedData.json()

            // Update UI state using passed props
            setCandidates(freshData.candidates)
            setInterviewers(freshData.interviewers)

            // We first show the main reply from the bot
            let botText = data.scheduled ? `✅ ${data.reply}` : `❌ ${data.reply}`;
            // If the interview was successfully scheduled, we add the details
            if (data.scheduled) {
                botText += `
👤 Candidate: ${data.data?.candidate?.name}
🧑‍💼 Interviewer: ${data.data?.interviewer?.name}
📧 Candidate Email: ${data.data?.candidate_email}
📧 Interviewer Email: ${data.data?.interviewer_email}
🗓️ Interview Time: ${data.data?.candidate?.interviewTime}`;
            }
            const botReply = {
                id: messages.length + 2,
                role: 'bot',
                text: botText
            };

            setMessages(prev => [...prev, botReply])

        } catch (error) {
            const errorMessage = {
                id: messages.length + 2,
                role: 'bot',
                text: 'Something went wrong. Is the backend running?'
            }
            setMessages(prev => [...prev, errorMessage])
        }
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