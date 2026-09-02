import React, { useState, useEffect } from 'react'
import TopNav from './components/TopNav.jsx'
import Hero from './components/Hero.jsx'
import Features from './components/Features.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Coverage from './components/Coverage.jsx'
import Faq from './components/Faq.jsx'
import Cta from './components/Cta.jsx'
import Footer from './components/Footer.jsx'
import Chat from './components/Chat.jsx'
import './App.css'

export default function App() {
  const [chatOpen, setChatOpen] = useState(false)

  const openChat = () => setChatOpen(true)
  const closeChat = () => setChatOpen(false)

  // Lock page scroll while the chat panel is open
  useEffect(() => {
    document.body.style.overflow = chatOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [chatOpen])

  return (
    <>
      <TopNav onOpenChat={openChat} />
      <main>
        <Hero onOpenChat={openChat} />
        <Features />
        <HowItWorks />
        <Coverage />
        <Faq />
        <Cta onOpenChat={openChat} />
      </main>
      <Footer onOpenChat={openChat} />

      {/* Floating chat launcher */}
      <button className="chat-fab" onClick={openChat} aria-label="Open chat">
        <span className="fab-icon">🚢</span>
        <span className="fab-label">Chat</span>
      </button>

      <Chat open={chatOpen} onClose={closeChat} />
    </>
  )
}
