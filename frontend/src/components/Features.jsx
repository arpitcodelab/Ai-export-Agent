import React, { useEffect, useRef } from 'react'
import './Features.css'

const FEATURES = [
  {
    icon: '🎙️',
    title: 'Talk, don’t type',
    desc: 'Record your question by voice — the agent understands it and answers back, with text-to-speech so you can listen too.',
  },
  {
    icon: '🧠',
    title: 'Natural language understanding',
    desc: 'The agent expands jargon and detects your intent, so a question like “how do I get my IEC” is understood instantly, even on the phone.',
  },
  {
    icon: '📚',
    title: 'Grounded in official sources',
    desc: 'Every answer is drawn from official Government of India documents — DGFT, CBIC, RBI, APEDA, FSSAI — and cites them at the end.',
  },
]

export default function Features() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    // Guard: if IntersectionObserver is unavailable, just show everything.
    if (!('IntersectionObserver' in window)) { el.classList.add('visible'); return }
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target) } })
    }, { threshold: 0.15 })
    el.querySelectorAll('.reveal').forEach((node) => obs.observe(node))
    return () => obs.disconnect()
  }, [])

  return (
    <section className="features section" id="features" ref={ref}>
      <div className="container">
        <div className="section-head reveal">
          <span className="badge-coral">Features</span>
          <h2 className="display-lg">An agent built for first-time exporters</h2>
          <p className="section-intro">
            Everything you need to go from “I have no idea” to “I know my next step”.
          </p>
        </div>

        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div className="feature-card reveal" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
