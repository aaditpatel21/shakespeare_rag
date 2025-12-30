import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './App.css'

// Environment Variable for API URL (Falls back to localhost if not set)
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [userId, setUserId] = useState('')

  // 1. Generate Session ID
  useEffect(() => {
    let storedId = localStorage.getItem('shakespeare_user_id')
    if (!storedId) {
      storedId = 'user_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('shakespeare_user_id', storedId)
    }
    setUserId(storedId)
    
    // Welcome Message
    setHistory([{
      role: 'assistant',
      content: 'Greetings! I am the Shakespeare RAG bot. Ask me aught about the Bard\'s plays.'
    }])
  }, [])

  // Auto-scroll
  const messagesEndRef = useRef(null)
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  useEffect(scrollToBottom, [history, loading])

  // 2. Handle Send
  const handleSend = async () => {
    if (!query.trim()) return

    const userMsg = { role: 'user', content: query }
    setHistory(prev => [...prev, userMsg])
    setLoading(true)
    setQuery('')

    try {
      // Use the dynamic API_URL
      const res = await axios.post(`${API_URL}/chat/`, {
        prompt: userMsg.content 
      }, {
        headers: { 'x-user-id': userId }
      })

      const aiText = res.data.answer || res.data.response || "Error: No answer received."
      
      setHistory(prev => [...prev, { 
        role: 'assistant', 
        content: aiText,
        sources: res.data.sources 
      }])

    } catch (error) {
      console.error(error)
      setHistory(prev => [...prev, { 
        role: 'error', 
        content: 'Alas! The server responds not. Is the backend running?' 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <div className="header-content">
          <h1>🎭 Shakespeare RAG</h1>
          <span className="subtitle">Hybrid Semantic Search Engine</span>
        </div>
      </header>

      <div className="chat-window">
        {history.map((msg, idx) => (
          <div key={idx} className={`message-row ${msg.role}`}>
            {/* Avatar */}
            <div className="avatar">
              {msg.role === 'user' ? '👤' : (msg.role === 'error' ? '⚠️' : '🎭')}
            </div>
            
            <div className="message-bubble">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
              
              {/* Sources Section */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-container">
                  <p className="sources-label">📚 Cited Sources:</p>
                  <div className="sources-list">
                    {msg.sources.map((s, i) => (
                      <div key={i} className="source-chip" title={s.snippet}>
                        <span className="play-name">{s.play}</span>
                        <span className="citation">(Act {s.act}, Scene {s.scene})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Typing Indicator Bubble */}
        {loading && (
          <div className="message-row assistant">
            <div className="avatar">🎭</div>
            <div className="message-bubble typing">
              <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <input 
            type="text" 
            placeholder="Ask about Romeo, Hamlet, or the Merry War..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={loading}
          />
          <button onClick={handleSend} disabled={loading || !query.trim()}>
            Send ➢
          </button>
        </div>
      </div>
    </div>
  )
}

export default App