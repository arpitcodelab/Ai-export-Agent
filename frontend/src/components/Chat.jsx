import React, { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { chat, speechToText, textToSpeech, getHealth } from '../api.js'
import { useChatHistory } from '../hooks/useChatHistory.js'
import { useTheme } from '../hooks/useTheme.js'
import { useLanguage, UI_TEXT } from '../hooks/useLanguage.js'
import SpikeMark from './SpikeMark.jsx'
import {
  IconHistory,
  IconPlus,
  IconClose,
  IconTrash,
  IconShip,
  IconUser,
  IconMic,
  IconStop,
  IconSpeaker,
  IconPin,
  IconPaperclip,
  IconWarning,
  IconSun,
  IconMoon,
  IconGlobe,
} from './Icons.jsx'
import './Chat.css'

const SUGGESTIONS = {
  en: [
    'How do I start exporting from India?',
    'What documents do I need to export to Germany?',
    'What is an IEC and how do I get one?',
    'Do I need FSSAI approval to export food products?',
  ],
  hi: [
    'भारत से export कैसे शुरू करें?',
    'Germany भेजने के लिए कौन-कौन से दस्तावेज़ चाहिए?',
    'IEC क्या होता है और कैसे मिलता है?',
    'खाने के सामान के export के लिए FSSAI मंज़ूरी चाहिए क्या?',
  ],
}

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
  const {
    sessions,
    activeId,
    messages,
    setMessages,
    newSession,
    switchSession,
    deleteSession,
  } = useChatHistory()
  const { isDark, toggleTheme } = useTheme()
  const { language, setLanguage, t } = useLanguage()
  const [historyOpen, setHistoryOpen] = useState(false)
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
      const data = await chat(q, null, language)
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
          // Remember which language THIS answer was written in, so the
          // Listen button reads it correctly even if the user switches
          // language afterwards.
          language: data.language || language,
        },
      ])
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `${e.message}`, is_error: true },
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
          const res = await speechToText(blob, language)
          if (res.text) {
            setInput(res.text)
          } else {
            setMessages((m) => [...m, { role: 'assistant', content: `${res.error || 'Could not understand audio.'}`, is_error: true }])
          }
        } catch (e) {
          setMessages((m) => [...m, { role: 'assistant', content: `${e.message}`, is_error: true }])
        } finally {
          setBusy(false)
        }
      }
      mr.start()
      mediaRecorder.current = mr
      setRecording(true)
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Microphone access denied: ${e.message}`, is_error: true }])
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop()
    }
    setRecording(false)
  }

  // ---- Text-to-speech (listen to an answer) ----
  const listen = async (index, text, msgLang) => {
    if (listeningId === index) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setListeningId(null)
      return
    }
    try {
      // Speak in the language the answer itself is in — falling back to
      // the currently selected language for older saved messages that
      // don't have a language recorded.
      const res = await textToSpeech(text, msgLang || language)
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
            <span>{t.title}</span>
          </div>
          <div className="panel-status">
            {health?.knowledge_base?.status === 'ok' ? (
              <span className="status-dot" />
            ) : (
              <span className="status-dot status-dot-amber" />
            )}
            <span className="panel-status-text">
              {health ? t.factsIndexed(health.knowledge_base.chunks) : t.connecting}
            </span>
          </div>

          {/* Language selector — English / Hindi */}
          <div className="lang-switch" title={t.language}>
            <IconGlobe size={14} />
            <button
              className={`lang-opt ${language === 'en' ? 'lang-opt-active' : ''}`}
              onClick={() => setLanguage('en')}
              aria-pressed={language === 'en'}
            >
              EN
            </button>
            <span className="lang-sep">/</span>
            <button
              className={`lang-opt ${language === 'hi' ? 'lang-opt-active' : ''}`}
              onClick={() => setLanguage('hi')}
              aria-pressed={language === 'hi'}
            >
              हिं
            </button>
          </div>

          {/* Light / dark mode */}
          <button
            className="panel-icon-btn"
            onClick={toggleTheme}
            aria-label={isDark ? t.lightMode : t.darkMode}
            title={isDark ? t.lightMode : t.darkMode}
          >
            {isDark ? <IconSun /> : <IconMoon />}
          </button>

          <button
            className="panel-icon-btn"
            onClick={() => setHistoryOpen((v) => !v)}
            aria-label={t.chatHistory}
            title={t.chatHistory}
          >
            <IconHistory />
          </button>
          <button
            className="panel-icon-btn"
            onClick={() => {
              newSession()
              setHistoryOpen(false)
            }}
            aria-label={t.newChat}
            title={t.newChat}
          >
            <IconPlus />
          </button>
          <button className="panel-close" onClick={onClose} aria-label={t.closeChat}>
            <IconClose />
          </button>
        </div>

        {historyOpen && (
          <div className="history-panel">
            <div className="history-panel-title">{t.pastChats}</div>
            {sessions.length === 0 ? (
              <div className="history-empty">{t.noSavedChats}</div>
            ) : (
              <div className="history-list">
                {sessions.map((s) => (
                  <div
                    key={s.id}
                    className={`history-item ${s.id === activeId ? 'history-item-active' : ''}`}
                    onClick={() => {
                      switchSession(s.id)
                      setHistoryOpen(false)
                    }}
                  >
                    <div className="history-item-title">{s.title}</div>
                    <button
                      className="history-item-delete"
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSession(s.id)
                      }}
                      aria-label={`${t.deleteChat}: ${s.title}`}
                      title={t.deleteChat}
                    >
                      <IconTrash />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {repo.error && (
          <div className="repo-error">
            <IconWarning /> {repo.error}
          </div>
        )}

        <div className="chat-log">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="empty-icon"><IconShip size={40} /></div>
              <p>{t.emptyTitle}</p>
              <div className="suggestions">
                {(SUGGESTIONS[language] || SUGGESTIONS.en).map((s) => (
                  <button key={s} className="suggestion" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={`msgrow msg-${m.role}`}>
                <div className="msgrow-avatar">{m.role === 'user' ? <IconUser size={16} /> : <IconShip size={16} />}</div>
                <div className="msgrow-body">
                  {m.role === 'assistant' && !m.is_error && (
                    <div className="msg-meta">
                      {m.is_faq ? (
                        <span className="meta-badge meta-faq">{t.instantAnswer}</span>
                      ) : m.is_fallback ? (
                        <span className="meta-badge meta-fallback">{t.kbLimit}</span>
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
                      <div className="sources-title"><IconPin size={11} /> {t.sourcesUsed}</div>
                      {m.sources.map((s, j) => (
                        <div className="source-line" key={j}>
                          {s.url ? (
                            <a href={s.url} target="_blank" rel="noreferrer" className="source-link">
                              <IconPaperclip size={11} /> {s.name}
                            </a>
                          ) : (
                            <span><IconPaperclip size={11} /> <b>{s.name}</b></span>
                          )}
                          {s.last_verified && <span className="source-verified"> · {t.verified} {s.last_verified}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                  {m.role === 'assistant' && !m.is_error && (
                    <button className="listen-btn" onClick={() => listen(i, m.content, m.language)}>
                      {listeningId === i ? <><IconStop size={12} /> {t.stop}</> : <><IconSpeaker size={12} /> {t.listen}</>}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
          {busy && (
            <div className="msgrow msg-assistant">
              <div className="msgrow-avatar"><IconShip size={16} /></div>
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
            title={t.recordTitle}
          >
            <IconMic />
          </button>
          <textarea
            ref={inputRef}
            className="input chat-textarea"
            placeholder={t.placeholder}
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
            {t.send}
          </button>
        </div>
        {recording && (
          <div className="rec-bar">
            <span className="rec-dot" /> {t.recording}
          </div>
        )}
      </aside>
    </>
  )
}
