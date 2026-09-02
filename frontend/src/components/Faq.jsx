import React, { useState } from 'react'
import './Faq.css'

const FAQS = [
  {
    q: 'Is this for complete beginners?',
    a: 'Yes. The agent is designed for first-time Indian exporters. It avoids jargon, explains every term in plain English, and walks through steps in order.',
  },
  {
    q: 'Where does the information come from?',
    a: 'Answers are grounded in official Government of India sources — DGFT, CBIC, ICEGATE, RBI, APEDA, MPEDA, GST Portal and the Ministry of Commerce — loaded into the knowledge base.',
  },
  {
    q: 'Can I speak instead of typing?',
    a: 'Absolutely. Tap the microphone to record your question; the agent transcribes it and answers. You can also hit “Listen” to hear any answer read aloud.',
  },
  {
    q: 'Is it free to use?',
    a: 'Yes. The agent runs on free-tier APIs and open-source tools, and it’s free for anyone to use while getting set up to export.',
  },
  {
    q: 'Does it give legal or customs advice?',
    a: 'It gives helpful guidance based on official documents, but for binding legal or customs decisions you should always confirm with a licensed customs broker or trade consultant.',
  },
]

export default function Faq() {
  const [open, setOpen] = useState(0)
  return (
    <section className="faq section" id="faq">
      <div className="container">
        <div className="faq-head">
          <span className="badge-coral">FAQ</span>
          <h2 className="display-lg">Questions, answered</h2>
        </div>
        <div className="faq-list">
          {FAQS.map((f, i) => (
            <div className={`faq-item ${open === i ? 'open' : ''}`} key={i}>
              <button className="faq-q" onClick={() => setOpen(open === i ? -1 : i)}>
                <span>{f.q}</span>
                <span className="faq-chev">{open === i ? '−' : '+'}</span>
              </button>
              {open === i && <div className="faq-a">{f.a}</div>}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
