// useChatHistory.js — persists chat sessions (like ChatGPT/Claude's history)
// in localStorage, so conversations survive a page refresh or closing the
// chat panel. No backend changes required for this version.
//
// Storage shape (localStorage key SESSIONS_KEY):
//   [{ id, title, createdAt, updatedAt, messages: [...] }, ...]
//
// A session is created lazily — opening the chat panel does NOT create a
// session; one is created the moment the user sends their first message,
// same as ChatGPT's "New chat" behaviour. This avoids littering history
// with empty sessions from people who just peek at the panel.

import { useCallback, useEffect, useState } from 'react'

const SESSIONS_KEY = 'exportAgent.chatSessions.v1'
const ACTIVE_KEY = 'exportAgent.activeSessionId.v1'
const MAX_SESSIONS = 50 // keep localStorage from growing unbounded

function loadSessions() {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    // Corrupt or inaccessible localStorage — fail soft, start empty.
    return []
  }
}

function saveSessions(sessions) {
  try {
    // Trim to the most recently updated MAX_SESSIONS before persisting.
    const trimmed = [...sessions]
      .sort((a, b) => b.updatedAt - a.updatedAt)
      .slice(0, MAX_SESSIONS)
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(trimmed))
  } catch {
    // Storage full or disabled (e.g. private browsing) — degrade silently;
    // the chat still works for the current tab, it just won't persist.
  }
}

function titleFromFirstMessage(text) {
  const clean = text.trim().replace(/\s+/g, ' ')
  return clean.length > 48 ? clean.slice(0, 48) + '…' : clean || 'New chat'
}

export function useChatHistory() {
  const [sessions, setSessions] = useState(() => loadSessions())
  const [activeId, setActiveId] = useState(() => {
    try {
      return localStorage.getItem(ACTIVE_KEY) || null
    } catch {
      return null
    }
  })

  // Persist sessions whenever they change.
  useEffect(() => {
    saveSessions(sessions)
  }, [sessions])

  // Persist which session is active.
  useEffect(() => {
    try {
      if (activeId) localStorage.setItem(ACTIVE_KEY, activeId)
      else localStorage.removeItem(ACTIVE_KEY)
    } catch {
      /* ignore */
    }
  }, [activeId])

  const activeSession = sessions.find((s) => s.id === activeId) || null
  const messages = activeSession?.messages || []

  // Replace the message list of the active session (creating one on first
  // use if none is active yet — this is the "lazy session creation" step).
  const setMessages = useCallback(
    (updater) => {
      setSessions((prev) => {
        let id = activeId
        let list = prev

        if (!id || !prev.some((s) => s.id === id)) {
          id = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
          list = [
            {
              id,
              title: 'New chat',
              createdAt: Date.now(),
              updatedAt: Date.now(),
              messages: [],
            },
            ...prev,
          ]
          setActiveId(id)
        }

        return list.map((s) => {
          if (s.id !== id) return s
          const nextMessages = typeof updater === 'function' ? updater(s.messages) : updater
          const firstUserMsg = nextMessages.find((m) => m.role === 'user')
          return {
            ...s,
            messages: nextMessages,
            updatedAt: Date.now(),
            title: firstUserMsg ? titleFromFirstMessage(firstUserMsg.content) : s.title,
          }
        })
      })
    },
    [activeId]
  )

  const newSession = useCallback(() => {
    setActiveId(null) // next sent message will lazily create a fresh session
  }, [])

  const switchSession = useCallback((id) => {
    setActiveId(id)
  }, [])

  const deleteSession = useCallback(
    (id) => {
      setSessions((prev) => prev.filter((s) => s.id !== id))
      if (id === activeId) setActiveId(null)
    },
    [activeId]
  )

  const clearAllHistory = useCallback(() => {
    setSessions([])
    setActiveId(null)
  }, [])

  return {
    sessions: [...sessions].sort((a, b) => b.updatedAt - a.updatedAt),
    activeId,
    messages,
    setMessages,
    newSession,
    switchSession,
    deleteSession,
    clearAllHistory,
  }
}
