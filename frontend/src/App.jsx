import { useState, useRef, useEffect, useMemo } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './App.css'

// --- CONFIGURATION ---
// List ALL your background images here exactly as they are named.
// Make sure the extensions (.png, .jpg) match your files!
const BACKGROUND_IMAGES = [
  '/backgrounds/1.png',
  '/backgrounds/2.png',
  '/backgrounds/3.png',
  '/backgrounds/4.png',
  '/backgrounds/5.png',
  '/backgrounds/6.png',
  '/backgrounds/7.png',
  '/backgrounds/8.png',
  '/backgrounds/9.png',
  '/backgrounds/10.png',
  '/backgrounds/11.png',
  '/backgrounds/12.png', 
  // Add more here if needed: '/backgrounds/9.jpg',
]

// Environment Variable
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [query, setQuery] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [userId, setUserId] = useState('')

  // Generate positions using a Dynamic Grid
  const collageItems = useMemo(() => {
    // 1. Shuffle the list so images appear in different spots every refresh
    const shuffledImages = [...BACKGROUND_IMAGES].sort(() => 0.5 - Math.random())
    
    // 2. Calculate optimal grid size based on image count
    // Example: 8 images -> 3 columns, 3 rows (3x3=9 slots)
    const count = shuffledImages.length;
    const cols = Math.ceil(Math.sqrt(count)); 
    const rows = Math.ceil(count / cols);

    const colWidth = 100 / cols;
    const rowHeight = 100 / rows;

    return shuffledImages.map((src, index) => {
      // Assign to grid cell
      const col = index % cols;
      const row = Math.floor(index / cols);

      // Base Position
      const baseLeft = col * colWidth;
      const baseTop = row * rowHeight;

      // Random Jitter (Stay within your cell)
      // Allow moving up to 40% of the cell's dimension
      const randomLeft = baseLeft + (Math.random() * (colWidth * 0.4));
      const randomTop = baseTop + (Math.random() * (rowHeight * 0.4));

      return {
        src,
        style: {
          top: `${randomTop}%`,
          left: `${randomLeft}%`,
          width: `${Math.max(colWidth * 0.8, 15)}vw`, // Responsive width
          maxWidth: '300px',
          transform: `rotate(${Math.random() * 30 - 15}deg) scale(${0.85 + Math.random() * 0.15})`,
          animationDelay: `${index * 0.1}s`
        }
      }
    })
  }, [])

  // Initialize Session ID
  useEffect(() => {
    let storedId = localStorage.getItem('shakespeare_user_id')
    if (!storedId) {
      storedId = 'user_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('shakespeare_user_id', storedId)
    }
    setUserId(storedId)
    
    setHistory([{
      role: 'assistant',
      content: 'Greetings! I am the Shakespeare RAG bot. Ask me aught about the Bard\'s plays.'
    }])
  }, [])

  const messagesEndRef = useRef(null)
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  useEffect(scrollToBottom, [history, loading])

  const handleSend = async () => {
    if (!query.trim()) return

    const userMsg = { role: 'user', content: query }
    setHistory(prev => [...prev, userMsg])
    setLoading(true)
    setQuery('')

    try {
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

  // Helper to hide broken images & log why
  const handleImageError = (e) => {
    console.warn(`Failed to load image: ${e.target.src}`);
    e.target.style.display = 'none';
  }

  return (
    <>
      <div className="collage-container">
        {collageItems.map((item, idx) => (
          <img 
            key={idx}
            src={item.src} 
            className="collage-item" 
            style={item.style} 
            alt=""
            onError={handleImageError} 
          />
        ))}
        <div className="collage-overlay"></div>
      </div>

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
              <div className="avatar">
                {msg.role === 'user' ? '👤' : (msg.role === 'error' ? '⚠️' : '🎭')}
              </div>
              
              <div className="message-bubble">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
                
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
              placeholder="Ask about Romeo, Hamlet, or any of William Shakespeare's literature..." 
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
    </>
  )
}

export default App