# AGENT_RULES.md — Read This First (For Your Coding Agent)

If you're using Claude Code, Cursor, Replit AI, or any other AI coding tool to build this — paste/point it to this file first. These are the ground rules for this specific project.

## Before writing any code
1. Read `PRD.md`, `DESIGN.md`, `TECH_STACK.md`, `KNOWLEDGE_BASE.md`, and `PROMPT_LIBRARY.md` in this `docs/` folder. Don't start coding from assumptions — the shape of the knowledge base and the prompt rules are already decided.
2. Build in the order laid out in `ROADMAP.md` — knowledge base first, then search, then AI answers, then the website, then testing. Don't build the website before the knowledge base exists; there will be nothing real to demo.

## Hard rules (do not deviate without asking the user)
1. **No paid tools or API keys that require a credit card / paid plan.** Only Groq (free tier), Gemini (free tier), ChromaDB, sentence-transformers, Streamlit — all as specified in TECH_STACK.md.
2. **Never hard-code export facts, HS codes, fees, or rules directly in the source code.** They live in `knowledge_base.json` only. Code should be "dumb" (just retrieves and formats) — the knowledge lives in data files, not code, so a non-coder can update facts later without touching code.
3. **Every AI answer must cite a source.** If the retrieval step finds nothing relevant, the agent must say it doesn't know — it must never let the LLM answer from general/pretrained knowledge alone. This is the single most important rule in the whole project.
4. **Secrets (API keys) go in a `.env` file, never in code, never committed to version control.** Provide a `.env.example` with blank placeholders.
5. **Keep it simple.** This is a Phase 1 prototype. Don't add authentication systems, databases, or complex infrastructure unless the PRD asks for it — extra complexity now makes it harder to demo and test.

## When something is ambiguous
If a requirement in the PRD is unclear or you (the coding agent) need to make an assumption, state the assumption out loud in your response and proceed — don't silently guess and don't block on it unless it would mean building the wrong thing entirely.

## Definition of "working prototype" for this project
A person should be able to:
1. Open a web link
2. Type a real export question
3. Get back a plain-English answer with a source cited
4. See the agent honestly say "I don't know" for something outside its knowledge base, instead of making something up

If that loop works end-to-end, Phase 1's core is done — everything else (nicer UI, voice, more documents) builds on top of that working loop.
