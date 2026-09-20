// useLanguage.js — English / Hindi switching for the chat panel.
//
// Two things depend on this choice:
//   1. The language the AI writes its answer in (sent to /chat as `language`)
//   2. The language the answer is read aloud in (sent to /voice/tts as `lang`)
//
// The UI labels below are translated too, so switching to Hindi doesn't
// leave a Hindi answer sitting under English buttons.
//
// The choice is saved to localStorage so it survives a refresh.

import { useCallback, useEffect, useState } from 'react'

const LANG_KEY = 'exportAgent.language.v1'

export const LANGUAGES = [
  { code: 'en', label: 'English', short: 'EN' },
  { code: 'hi', label: 'हिंदी', short: 'हि' },
]

// UI strings for each language. Keep keys identical across both objects.
export const UI_TEXT = {
  en: {
    title: 'Export Agent',
    connecting: 'Connecting…',
    factsIndexed: (n) => `${n} facts indexed`,
    placeholder: 'Ask anything about exporting from India…',
    send: 'Send',
    listen: 'Listen',
    stop: 'Stop',
    sourcesUsed: 'Sources used',
    pastChats: 'Past chats',
    noSavedChats: 'No saved chats yet.',
    newChat: 'New chat',
    chatHistory: 'Chat history',
    deleteChat: 'Delete chat',
    closeChat: 'Close chat',
    recording: 'Recording… click the mic to stop',
    recordTitle: 'Record your question',
    instantAnswer: 'Instant answer',
    kbLimit: 'Knowledge base limit',
    emptyTitle: 'Ask me about exporting from India',
    emptyHint: 'Registrations, documents, shipping, payments, schemes — try a question below.',
    lightMode: 'Switch to light mode',
    darkMode: 'Switch to dark mode',
    language: 'Language',
    verified: 'verified',
  },
  hi: {
    title: 'एक्सपोर्ट एजेंट',
    connecting: 'जुड़ रहे हैं…',
    factsIndexed: (n) => `${n} जानकारियाँ मौजूद`,
    placeholder: 'भारत से export के बारे में कुछ भी पूछें…',
    send: 'भेजें',
    listen: 'सुनें',
    stop: 'रोकें',
    sourcesUsed: 'स्रोत',
    pastChats: 'पुरानी बातचीत',
    noSavedChats: 'अभी कोई पुरानी बातचीत नहीं है।',
    newChat: 'नई बातचीत',
    chatHistory: 'पुरानी बातचीत',
    deleteChat: 'बातचीत हटाएँ',
    closeChat: 'बंद करें',
    recording: 'रिकॉर्ड हो रहा है… रोकने के लिए mic दबाएँ',
    recordTitle: 'अपना सवाल बोलें',
    instantAnswer: 'तुरंत जवाब',
    kbLimit: 'जानकारी उपलब्ध नहीं',
    emptyTitle: 'भारत से export के बारे में पूछें',
    emptyHint: 'रजिस्ट्रेशन, दस्तावेज़, शिपिंग, पेमेंट, सरकारी योजनाएँ — नीचे से कोई सवाल चुनें।',
    lightMode: 'लाइट मोड चुनें',
    darkMode: 'डार्क मोड चुनें',
    language: 'भाषा',
    verified: 'जाँचा गया',
  },
}

function getInitialLanguage() {
  try {
    const saved = localStorage.getItem(LANG_KEY)
    if (saved === 'en' || saved === 'hi') return saved
  } catch {
    /* localStorage unavailable — fall back to English */
  }
  return 'en'
}

export function useLanguage() {
  const [language, setLanguage] = useState(getInitialLanguage)

  useEffect(() => {
    try {
      localStorage.setItem(LANG_KEY, language)
    } catch {
      /* best-effort only */
    }
  }, [language])

  const toggleLanguage = useCallback(() => {
    setLanguage((l) => (l === 'en' ? 'hi' : 'en'))
  }, [])

  // t = the UI strings for the currently selected language
  return { language, setLanguage, toggleLanguage, t: UI_TEXT[language] || UI_TEXT.en }
}
