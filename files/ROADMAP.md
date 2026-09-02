# ROADMAP.md — What Comes When

## Phase 1 (build this first)
1. Set up project folders (see DESIGN.md)
2. Process your PDFs/Excel files into `knowledge_base.json` + `.xlsx` (see KNOWLEDGE_BASE.md)
3. Build the search index (ChromaDB)
4. Wire up the AI answer pipeline (Groq + prompt library)
5. Build the Streamlit chat website
6. Run the full testing checklist (see TESTING.md) and fix issues
7. Write the technical documentation
8. Demo to mentor

## Phase 1.5 — Voice (next, as you requested)
Goal: user can speak a question and hear the answer, on the same web app.
- **Speech-to-text (listening)**: use the browser's free built-in Web Speech API first — zero cost, works in Chrome. If quality isn't good enough later, upgrade to OpenAI's free/open **Whisper** model running locally (still free, just needs more setup).
- **Text-to-speech (speaking the answer)**: same approach — browser's built-in speech synthesis first (free, instant), with **edge-tts** (a free, open tool) as a more natural-sounding upgrade later.
- This slots into the existing `app.py` without touching the knowledge base or AI pipeline underneath — see DESIGN.md's "where future features plug in" section.

## Phase 2 (later, per the mentor's brief)
- **Decision-support dashboards** — visual summaries (e.g. charts of tariffs, scheme eligibility) built from the same knowledge base
- **Export readiness assessment** — a short questionnaire that scores how ready a business is to export, using the knowledge base's rules as the checklist
- **Buyer discovery (verified sources)** — connecting to trusted trade directories to suggest real potential buyers (needs careful source verification, not open web scraping)
- **Multilingual support** — mainly a prompt + interface change (see PROMPT_LIBRARY.md notes)
- **Predictive trade analytics** — forecasting trends from trade statistics data, a separate data-science module
- **Government portal/API integration** — direct connections to DGFT/ICEGATE where official APIs exist, so users could act (not just read guidance) — this is the most complex piece and depends on what official APIs are actually available publicly

## Design principle behind this order
Everything in Phase 1 is about **being right and trustworthy first** — a chatbot that gives correct answers with sources. Only once that foundation is solid does it make sense to add flashier features like dashboards or predictions, because those are only as good as the knowledge base underneath them.
