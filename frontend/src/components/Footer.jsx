import React from 'react'
import SpikeMark from './SpikeMark.jsx'
import './Footer.css'

const COLUMNS = [
  {
    title: 'Agent',
    links: [
      { label: 'Ask a question', href: '#chat', chat: true },
      { label: 'Voice input', href: '#chat', chat: true },
      { label: 'How it works', href: '#how' },
      { label: 'What it covers', href: '#coverage' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing & FAQ', href: '#faq' },
      { label: 'Official sources', href: '#faq' },
    ],
  },
  {
    title: 'Official sources',
    links: [
      { label: 'DGFT', href: 'https://www.dgft.gov.in' },
      { label: 'ICEGATE', href: 'https://www.icegate.gov.in' },
      { label: 'RBI', href: 'https://www.rbi.org.in' },
      { label: 'CBIC', href: 'https://www.cbic.gov.in' },
      { label: 'APEDA', href: 'https://apeda.gov.in' },
    ],
  },
]

export default function Footer({ onOpenChat }) {
  const handleClick = (e, href, isChat) => {
    if (isChat) {
      e.preventDefault()
      if (onOpenChat) onOpenChat()
    }
  }
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-brand">
          <SpikeMark size={22} color="#faf9f5" />
          <span className="footer-wordmark">India Export AI</span>
        </div>

        <div className="footer-grid">
          {COLUMNS.map((col) => (
            <div className="footer-col" key={col.title}>
              <div className="footer-col-title">{col.title}</div>
              {col.links.map((l) => (
                <a
                  key={l.label}
                  href={l.href}
                  className="footer-link"
                  onClick={(e) => handleClick(e, l.href, l.chat)}
                  {...(l.href.startsWith('http') ? { target: '_blank', rel: 'noreferrer' } : {})}
                >
                  {l.label}
                </a>
              ))}
            </div>
          ))}
          <div className="footer-col">
            <div className="footer-col-title">Disclaimer</div>
            <p className="footer-disclaimer">
              Guidance is based on official Government of India sources. For binding
              legal or customs advice, consult a licensed customs broker or trade
              consultant. Rules change — verify against current official sources.
            </p>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} India Export AI</span>
          <span className="footer-note">Sources: DGFT · CBIC · ICEGATE · RBI · FIEO · APEDA · FSSAI · BIS</span>
        </div>
      </div>
    </footer>
  )
}
