import React from 'react'
import './Coverage.css'

const TOPICS = [
  'Import Export Code (IEC)',
  'GST for exports',
  'AD Code',
  'RCMC',
  'Customs procedures',
  'Shipping Bill',
  'ICEGATE',
  'DGFT services',
  'RBI export payments',
  'Export documentation',
  'Export incentives',
  'Product certifications',
  'HS Codes',
  'Incoterms',
  'Logistics',
  'Payment methods',
  'Country-specific compliance',
  'Trade promotion schemes',
  'Trade fairs',
  'FAQs',
]

export default function Coverage() {
  return (
    <section className="coverage section" id="coverage">
      <div className="container">
        <div className="coverage-head">
          <span className="badge-coral">What it covers</span>
          <h2 className="display-lg">Everything a first-time exporter asks</h2>
          <p className="coverage-intro">
            Ask about any of these — the agent pulls the answer from official,
            verifiable sources and explains it in plain language.
          </p>
        </div>

        <div className="topic-grid">
          {TOPICS.map((t) => (
            <div className="topic-tile" key={t}>
              <span className="tile-mark">✦</span>
              <span className="tile-label">{t}</span>
            </div>
          ))}
        </div>

        <div className="coverage-note">
          <span className="status-dot" /> Always answers with a source — never guesses.
        </div>
      </div>
    </section>
  )
}
