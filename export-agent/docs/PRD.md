# PRD — AI Export Facilitation Agent

## 1. What is this, in one line?
A chatbot that helps Indian exporters (especially first-timers) get correct, government-backed answers about how to export — documents needed, codes required, costs, rules, and where to find official help — instead of them getting confused by scattered websites and agents.

## 2. Who is it for?
- **Primary user**: A small business owner or new exporter in India who wants to sell products abroad but doesn't know the process.
- **Secondary user**: Someone already exporting who wants a quick answer (e.g. "what's the HS code for X" or "which countries have an FTA with India for my product").

## 3. The problem
Export information in India is correct but scattered — RBI, DGFT, ICEGATE, customs, FIEO, embassies, etc. A first-time exporter has to piece it together themselves, and one wrong document or code can delay a shipment by weeks. This agent is meant to be a single, trustworthy starting point.

## 4. What the agent must do (Phase 1)

The agent answers questions in these 13 areas (from the mentor's brief):

| # | Topic | Example question it should answer |
|---|-------|-------------------------------------|
| 1 | How to export from India | "I want to start exporting handicrafts, where do I begin?" |
| 2 | Export procedures & documentation | "What documents do I need for a shipment to Germany?" |
| 3 | IEC, GST, AD Code, RCMC | "What is an IEC and how do I get one?" |
| 4 | HS Code guidance | "What's the HS code for cotton bedsheets?" |
| 5 | Incoterms | "What does FOB mean and who pays for what?" |
| 6 | Logistics & Customs | "How does customs clearance work for exports?" |
| 7 | Export payment methods | "What's a Letter of Credit and is it safe?" |
| 8 | Export incentives & govt schemes | "Am I eligible for RoDTEP?" |
| 9 | Product certifications & compliance | "Does my food product need FSSAI export clearance?" |
| 10 | Country-specific import requirements | "What does the USA require to import textiles?" |
| 11 | Trade intelligence | "Which countries are importing more Indian spices this year?" |
| 12 | Trade fairs & export promotion events | "Any upcoming trade fairs for leather goods?" |
| 13 | FAQs | Common repeated questions, answered instantly |

**Golden rule for every answer**: the agent must always say *where* the information came from (which government source/document), and must never invent a rule, code, or number it isn't sure about. If it doesn't know, it says so and points to the right official source instead of guessing.

## 5. What Phase 1 is NOT
To keep this buildable for a first version, Phase 1 does **not** include:
- Dashboards or analytics screens
- Automated "export readiness score" for a business
- Finding/verifying real buyers abroad
- Multiple languages (English only for now)
- Predicting future trade trends
- Direct integration with government portals (e.g. auto-filing on DGFT) — the agent gives *guidance*, it doesn't submit forms on the government's behalf

These are planned for the **next phase** (see ROADMAP.md), so the system should be built in a way that doesn't block adding them later, but we are not building them now.

## 6. Interface
- **Phase 1**: a web-based chat app (like a simple ChatGPT-style page), so it's easy to demo and test.
- **Planned soon after**: a WhatsApp/Telegram bot, since many small exporters are more comfortable there than on a website.
- **Voice**: to be added right after the web version is stable (speak a question, hear an answer) — see ROADMAP.md.

## 7. What "done" looks like for Phase 1
- [ ] A working chat website where anyone can type an export-related question and get a clear, correct, cited answer
- [ ] All the user's knowledge PDFs/Excel content is loaded into the knowledge base and the agent uses it (not just general AI guesses)
- [ ] A knowledge base file (Excel/JSON) that lists every fact/rule the agent knows, and which source it came from
- [ ] A prompt library (the exact instructions given to the AI, saved and reusable)
- [ ] A source mapping document — a table of every government source used and what topic it covers
- [ ] A testing report showing the agent was asked real questions and its answers were checked for accuracy
- [ ] Technical documentation explaining how the whole system works, so anyone (technical or not) can understand and maintain it

## 8. Success measures (how we'll know it's good)
- Accuracy: in testing, the agent's answers should match official government guidance (checked manually against source documents)
- Honesty: the agent should say "I'm not sure, please check [source]" rather than guess, when it doesn't have the information
- Speed: an answer should come back in a few seconds, not minutes
- Cost: the whole system should run on free-tier tools only (no paid subscriptions), per the mentor's constraint

## 9. Risks to keep in mind
- **Wrong information = real business harm.** A wrong HS code or missed document can cost an exporter money and time. This is why citing sources and refusing to guess is non-negotiable, not a "nice to have."
- **Rules change over time** (schemes, tariffs, FTAs update). The knowledge base needs a way to be refreshed later — it shouldn't be treated as permanently frozen.
- **Free-tier limits**: free AI APIs have rate limits (a cap on how many questions per minute/day). This is fine for a prototype/demo but should be documented so it's not a surprise later.
