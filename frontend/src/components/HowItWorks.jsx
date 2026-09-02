import React from 'react'
import './HowItWorks.css'

const STEPS = [
  {
    n: '01',
    title: 'Ask',
    desc: 'Type your question or record it by voice — in any natural phrasing.',
  },
  {
    n: '02',
    title: 'Understand',
    desc: 'The agent normalises your words, detects intent, and finds the exact facts in the knowledge base.',
  },
  {
    n: '03',
    title: 'Answer with sources',
    desc: 'A clear, plain-English answer appears alongside the official documents it used.',
  },
]

export default function HowItWorks() {
  return (
    <section className="how section" id="how">
      <div className="container how-grid">
        <div className="how-copy">
          <span className="badge-coral">How it works</span>
          <h2 className="display-lg">Three steps to a reliable answer</h2>
          <p className="how-intro">
            The same best-in-class pipeline that runs your data — re-capped in
            minutes, with voice and natural-language understanding on top.
          </p>

          <div className="steps">
            {STEPS.map((s) => (
              <div className="step" key={s.n}>
                <div className="step-num">{s.n}</div>
                <div>
                  <h3 className="step-title">{s.title}</h3>
                  <p className="step-desc">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="how-visual">
          <div className="code-window">
            <div className="code-header">
              <span>pipeline</span>
              <span className="code-dot">●</span>
            </div>
            <pre className="code-body">
{`# India Export AI
> "documents for mangoes → DE?"

1  nlp.process_question()
   → intent: documents
2  retriever.query(normalized)
   → 5 best chunks found
3  agent.answer(question)
   → cited, plain-English reply

[✓] 400 facts indexed
[✓] all answers source-backed`}
            </pre>
          </div>
        </div>
      </div>
    </section>
  )
}
