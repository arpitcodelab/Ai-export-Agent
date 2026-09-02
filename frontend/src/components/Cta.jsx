import React from 'react'
import './Cta.css'

export default function Cta({ onOpenChat }) {
  return (
    <section className="cta section">
      <div className="container">
        <div className="cta-band">
          <h2 className="cta-title">Turn “I don’t know how” into “I know my next step.”</h2>
          <p className="cta-sub">
            Ask the agent anything about exporting from India — it’s free, fast, and grounded in official Government of India sources.
          </p>
          <div className="cta-actions">
            <button className="btn btn-on-coral" onClick={onOpenChat}>Start chatting now</button>
            <a href="#coverage" className="btn btn-text cta-text-link">See what it covers</a>
          </div>
        </div>
      </div>
    </section>
  )
}
