import React from 'react'
import SpikeMark from './SpikeMark.jsx'
import './Hero.css'

// A static dark "chat mockup" that mirrors the existing Streamlit agent's look,
// following the DESIGN.md product-mockup-card-dark treatment.
function HeroMockup() {
  return (
    <div className="mockup-card">
      <div className="mockup-topbar">
        <div className="window-dots">
          <span className="dot dot-a" />
          <span className="dot dot-b" />
          <span className="dot dot-c" />
        </div>
        <span className="mockup-title">
          <SpikeMark size={14} /> India Export AI — Agent
        </span>
      </div>

      <div className="mockup-body">
        <div className="msg msg-user">
          <span className="msg-avatar">👤</span>
          <div className="bubble bubble-user">
            What documents do I need to export mangoes to Germany?
          </div>
        </div>

        <div className="msg msg-agent">
          <span className="msg-avatar agent-avatar">🚢</span>
          <div className="bubble bubble-agent">
            <p className="bubble-badge">AI ANSWER · 5 sources</p>
            <p className="bubble-quick">Quick answer</p>
            <p>
              To export mangoes from India you'll first need an <b>IEC</b> (your
              export-import licence). You'll also need a Phytosanitary Certificate
              and FSSAI approval, plus the standard commercial documents.
            </p>
            <p className="bubble-quick">What to do next</p>
            <ul className="bubble-list">
              <li>Get your IEC from the DGFT portal</li>
              <li>Obtain FSSAI and Phytosanitary certificates</li>
              <li>Check Germany's EU import rules</li>
            </ul>
            <p className="bubble-source">📌 Source: DGFT · APEDA · FSSAI</p>
          </div>
        </div>
      </div>

      <div className="mockup-input">
        <span className="mic-icon">🎙️</span>
        <span className="input-placeholder">Ask about IEC, GST, RCMC, HS codes…</span>
        <span className="send-icon">➤</span>
      </div>
    </div>
  )
}

export default function Hero({ onOpenChat }) {
  return (
    <section className="hero" id="top">
      <div className="container hero-grid">
        <div className="hero-copy">
          <span className="badge-coral">🇮🇳 Powered by official GOI sources</span>
          <h1 className="hero-h1">
            Your thinking partner for <em>exporting from India</em>.
          </h1>
          <p className="hero-sub">
            A friendly AI agent that answers your export questions in plain
            language — IEC, GST, RCMC, HS codes, documents, customs and more —
            always backed by official government information.
          </p>
          <div className="hero-cta-row">
            <button className="btn btn-primary btn-lg" onClick={onOpenChat}>Start chatting</button>
            <a href="#how" className="btn btn-secondary btn-lg">How it works</a>
          </div>
          <div className="hero-trust">
            <span className="hero-stat">
              <strong>400+</strong> facts indexed
            </span>
            <span className="hero-stat">
              <strong>Always</strong> cites its sources
            </span>
            <span className="hero-stat">
              <strong>Free</strong> for first-time exporters
            </span>
          </div>
        </div>

        <div className="hero-visual">
          <HeroMockup />
        </div>
      </div>
    </section>
  )
}
