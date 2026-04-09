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
    const [isTyping, setIsTyping] = useState(false) // ✅ added
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isTyping]) // ✅ updated

    async function handleSend() {
        if (inputText.trim() === '') return

        const userMessage = {
            id: Date.now(), // ✅ better id
            role: 'user',
            text: inputText
        }

        setMessages(prev => [...prev, userMessage])
        setInputText('')
        setIsTyping(true) // ✅ start typing

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: inputText,
                    history: messages // This sends all previous messages to the backend
                })
            })

            const data = await response.json()

            // Fetch updated data
            const updatedData = await fetch('/data')
            const freshData = await updatedData.json()

            setCandidates(freshData.candidates)
            setInterviewers(freshData.interviewers)

            let botText = data.reply;

            if (data.scheduled) {
                botText += `
Candidate: ${data.data?.candidate?.name}
Interviewer: ${data.data?.interviewer?.name}
Candidate Email: ${data.data?.candidate_email}
Interviewer Email: ${data.data?.interviewer_email}
Interview Time: ${data.data?.candidate?.interviewTime}`;
            }

            const botMessage = {
                id: Date.now() + 1,
                role: 'bot',
                text: botText,
                isError: data.is_error
            }

            setMessages(prev => [...prev, botMessage])

        } catch (error) {
            const errorMessage = {
                id: Date.now() + 2,
                role: 'bot',
                text: 'Something went wrong. Is the backend running?'
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setIsTyping(false) // ✅ always stop typing
        }
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault()
            handleSend()
        }
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

                {/* ✅ Typing Indicator */}
                {isTyping && (
                    <div className="message message-bot">
                        <span className="message-label">ai agent</span>
                        <div className="message-bubble typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}

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