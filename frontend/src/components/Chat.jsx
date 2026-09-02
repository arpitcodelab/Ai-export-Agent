import React, { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { chat, speechToText, textToSpeech, getHealth } from '../api.js'
import SpikeMark from './SpikeMark.jsx'
import './Chat.css'

const SUGGESTIONS = [
  'How do I start exporting from India?',
  'What documents do I need to export to Germany?',
  'What is an IEC and how do I get one?',
  'Do I need FSSAI approval to export food products?',
]

// A tiny markdown renderer with safe, light styling for chat bubbles.
function Md({ children }) {
  return (
    <div className="md">
      <ReactMarkdown
        components={{
          a: ({ node, ...props }) => <a {...props} target="_blank" rel="noreferrer" className="md-link" />,
          ul: ({ node, ...props }) => <ul {...props} className="md-list" />,
          ol: ({ node, ...props }) => <ol {...props} className="md-list" />,
          li: ({ node, ...props }) => <li {...props} className="md-li" />,
          strong: ({ node, ...props }) => <strong {...props} className="md-strong" />,
          h1: ({ node, ...props }) => <h1 {...props} className="md-h" />,
          h2: ({ node, ...props }) => <h2 {...props} className="md-h" />,
          h3: ({ node, ...props }) => <h3 {...props} className="md-h" />,
          p: ({ node, ...props }) => <p {...props} className="md-p" />,
          code: ({ node, ...props }) => <code {...props} className="md-code" />,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}

export default function ChatPanel({ open, onClose }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [recording, setRecording] = useState(false)
  const [listeningId, setListeningId] = useState(null)
  const [health, setHealth] = useState(null)
  const [repo, setRepo] = useState({ error: null })
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])
  const bottomRef = useRef(null)
  const audioRef = useRef(new Audio())
  const inputRef = useRef(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setRepo({ error: 'Backend not reachable. Start the FastAPI server.' }))
  }, [])

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  // Focus the input when the panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150)
    }
  }, [open])

  // Close on Escape
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const send = async (question) => {
    const q = (question ?? input).trim()
    if (!q || busy) return
    setInput('')
    setBusy(true)
    setMessages((m) => [...m, { role: 'user', content: q }])
    try {
      const data = await chat(q)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: data.text,
          sources: data.sources || [],
          is_faq: data.is_faq,
          is_fallback: data.is_fallback,
          intent: data.intent_label,
          chunks: data.chunks_count,
        },
      ])
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `⚠️ ${e.message}`, is_error: true },
      ])
    } finally {
      setBusy(false)
    }
  }

  // ---- Voice recording (STT) ----
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)
      audioChunks.current = []
      mr.ondataavailable = (e) => audioChunks.current.push(e.data)
      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(audioChunks.current, { type: 'audio/webm' })
        setBusy(true)
        try {
          const res = await speechToText(blob, 'en')
          if (res.text) {
            setInput(res.text)
          } else {
            setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${res.error || 'Could not understand audio.'}`, is_error: true }])
          }
        } catch (e) {
          setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${e.message}`, is_error: true }])
        } finally {
          setBusy(false)
        }
      }
      mr.start()
      mediaRecorder.current = mr
      setRecording(true)
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `⚠️ Microphone access denied: ${e.message}`, is_error: true }])
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop()
    }
    setRecording(false)
  }

  // ---- Text-to-speech (listen to an answer) ----
  const listen = async (index, text) => {
    if (listeningId === index) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setListeningId(null)
      return
    }
    try {
      const res = await textToSpeech(text, 'en')
      if (res.audio) {
        const url = `data:${res.mime || 'audio/mp3'};base64,${res.audio}`
        audioRef.current.src = url
        audioRef.current.onended = () => setListeningId(null)
        audioRef.current.play()
        setListeningId(index)
      }
    } catch (e) {
      /* ignore TTS failures */
    }
  }

  return (
    <>
      {/* Overlay */}
      <div className={`chat-overlay ${open ? 'open' : ''}`} onClick={onClose} />

      {/* Slide-over panel */}
      <aside className={`chat-panel ${open ? 'open' : ''}`} aria-hidden={!open}>
        <div className="panel-header">
          <div className="panel-brand">
            <SpikeMark size={20} />
            <span>Export Agent</span>
          </div>
          <div className="panel-status">
            {health?.knowledge_base?.status === 'ok' ? (
              <span className="status-dot" />
            ) : (
              <span className="status-dot status-dot-amber" />
            )}
            <span className="panel-status-text">
              {health ? `${health.knowledge_base.chunks} facts indexed` : 'Connecting…'}
            </span>
          </div>
          <button className="panel-close" onClick={onClose} aria-label="Close chat">
            ✕
          </button>
        </div>

        {repo.error && (
          <div className="repo-error">
            ⚠️ {repo.error}
          </div>
        )}

        <div className="chat-log">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="empty-icon">🚢</div>
              <p>Ask anything about exporting from India.</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="suggestion" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={`msgrow msg-${m.role}`}>
                <div className="msgrow-avatar">{m.role === 'user' ? '👤' : '🚢'}</div>
                <div className="msgrow-body">
                  {m.role === 'assistant' && !m.is_error && (
                    <div className="msg-meta">
                      {m.is_faq ? (
                        <span className="meta-badge meta-faq">⚡ Instant answer</span>
                      ) : m.is_fallback ? (
                        <span className="meta-badge meta-fallback">❓ Knowledge base limit</span>
                      ) : (
                        <span className="meta-badge meta-ai">
                          AI answer · {m.chunks} source{m.chunks === 1 ? '' : 's'}
                        </span>
                      )}
                      {m.intent && <span className="meta-intent">{m.intent}</span>}
                    </div>
                  )}
                  <div className={`bubble ${m.role === 'user' ? 'b-user' : 'b-agent'} ${m.is_error ? 'b-error' : ''}`}>
                    {m.role === 'user' ? (
                      m.content
                    ) : (
                      <Md>{m.content}</Md>
                    )}
                  </div>
                  {m.role === 'assistant' && m.sources && m.sources.length > 0 && (
                    <div className="sources">
                      <div className="sources-title">📌 Sources used</div>
                      {m.sources.map((s, j) => (
                        <div className="source-line" key={j}>
                          {s.url ? (
                            <a href={s.url} target="_blank" rel="noreferrer" className="source-link">
                              📎 {s.name}
                            </a>
                          ) : (
                            <span>📎 <b>{s.name}</b></span>
                          )}
                          {s.last_verified && <span className="source-verified"> · verified {s.last_verified}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                  {m.role === 'assistant' && !m.is_error && (
                    <button className="listen-btn" onClick={() => listen(i, m.content)}>
                      {listeningId === i ? '⏸ Stop' : '🔊 Listen'}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
          {busy && (
            <div className="msgrow msg-assistant">
              <div className="msgrow-avatar">🚢</div>
              <div className="typing">
                <span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input">
          <button
            className={`mic-btn ${recording ? 'mic-rec' : ''}`}
            onClick={recording ? stopRecording : startRecording}
            title="Record your question"
          >
            {recording ? '🔴' : '🎙️'}
          </button>
          <textarea
            ref={inputRef}
            className="input chat-textarea"
            placeholder="Ask about IEC, GST, documents, customs…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                send()
              }
            }}
            rows={1}
          />
          <button className="btn btn-primary" onClick={() => send()} disabled={!input.trim() || busy}>
            Send
          </button>
        </div>
        {recording && <div className="rec-bar">🔴 Recording… click the red mic to stop</div>}
      </aside>
    </>
  )
}
