import React, { useState, useEffect } from 'react'
import SpikeMark from './SpikeMark.jsx'
import './TopNav.css'

const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how' },
  { label: 'Coverage', href: '#coverage' },
  { label: 'FAQ', href: '#faq' },
]

export default function TopNav({ onOpenChat }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleChat = () => {
    setMenuOpen(false)
    if (onOpenChat) onOpenChat()
  }

  return (
    <header className={`top-nav ${scrolled ? 'top-nav-scrolled' : ''}`}>
      <div className="container top-nav-inner">
        <a href="#top" className="brand">
          <SpikeMark size={22} />
          <span className="brand-wordmark">India Export AI</span>
        </a>

        <nav className="top-nav-menu">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="nav-link">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="top-nav-actions">
          <button className="btn-text sign-in" onClick={handleChat}>Try the Agent</button>
          <button className="btn btn-primary" onClick={handleChat}>Chat now</button>
        </div>

        <button
          className="hamburger"
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span className="bar" />
          <span className="bar" />
          <span className="bar" />
        </button>
      </div>

      {menuOpen && (
        <div className="mobile-menu">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="mobile-link" onClick={() => setMenuOpen(false)}>
              {l.label}
            </a>
          ))}
          <button className="btn btn-primary mobile-cta" onClick={handleChat}>
            Chat now
          </button>
        </div>
      )}
    </header>
  )
}
