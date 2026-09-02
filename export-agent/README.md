# AI Export Facilitation Agent

> A RAG-based chatbot that gives Indian exporters **correct, government-backed answers** about how to export — with every answer citing its source.

## What it does

A user types an export question (e.g. *"What documents do I need to export to Germany?"*) and gets back a **plain-English answer with a source citation** — drawn from a curated knowledge base of official government documents (DGFT, ICEGATE, FIEO, RBI, CBIC).

The agent is designed to **never guess**. If it doesn't know something, it says so and points to the right official source.

## Architecture (RAG pipeline)

```
data/raw/ (your PDFs + Excel)
     │
     ▼
[ingest.py] → knowledge_base.json + knowledge_base.xlsx
     │
     ▼
[build_index.py] → ChromaDB vector index (data/vector_store/)
     │
     ▼
User question (Streamlit chat)
     │
     ▼
[retriever.py] → top-5 relevant chunks from ChromaDB
     │
     ▼
[agent.py] → Groq LLM → cited answer
     │
     ▼
Answer shown to user with source
```

## Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- A free Groq API key from [console.groq.com](https://console.groq.com)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_key_here
```

### 4. Add your documents
Place your PDF and Excel files in `data/raw/`. Then run:
```bash
# Step 1: Process documents into knowledge base
python src/ingest.py

# Step 2: Build the searchable index
python src/build_index.py
```

### 5. Run the chat app
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

## Project Structure

```
export-agent/
├── data/
│   ├── raw/              ← Put your PDFs/Excel files here
│   ├── processed/        ← Auto-generated: knowledge_base.json + .xlsx
│   └── vector_store/     ← Auto-generated: ChromaDB search index
├── src/
│   ├── ingest.py         ← Reads raw/ files → knowledge_base.json
│   ├── build_index.py    ← JSON → ChromaDB searchable index
│   ├── retriever.py      ← Finds relevant chunks for a question
│   ├── agent.py          ← Sends question + facts to LLM → answer
│   └── prompts.py        ← All AI prompt templates
├── app.py                ← Streamlit chat website
├── tests/
│   ├── test_questions.json
│   └── testing_report.md
├── docs/                 ← All specification documents
├── .env.example          ← API key template (copy to .env)
├── requirements.txt
└── README.md
```

## Topics Covered (13 categories)

| # | Topic |
|---|-------|
| 1 | How to export from India |
| 2 | Export procedures & documentation |
| 3 | IEC, GST, AD Code, RCMC |
| 4 | HS Code guidance |
| 5 | Incoterms |
| 6 | Logistics & Customs |
| 7 | Export payment methods |
| 8 | Export incentives & govt schemes |
| 9 | Product certifications & compliance |
| 10 | Country-specific import requirements |
| 11 | Trade intelligence |
| 12 | Trade fairs & export promotion |
| 13 | FAQs |

## Cost
**100% free.** Uses Groq free tier (LLM), sentence-transformers (local embeddings), ChromaDB (local vector DB), and Streamlit (web UI). No credit card required.

## Rules for this system
See `docs/AGENT_RULES.md` for the non-negotiable rules this system follows:
- Every answer must cite a source
- The AI never answers from general knowledge — only from the knowledge base
- No hard-coded facts in code — all knowledge lives in `knowledge_base.json`
- API keys stay in `.env`, never in code

## Adding New Documents
1. Drop new PDF/Excel files into `data/raw/`
2. Run `python src/ingest.py` 
3. Run `python src/build_index.py`
4. Restart the Streamlit app

## Tech Stack
| Component | Tool |
|---|---|
| LLM | Groq API (llama-3.3-70b) — free tier |
| Backup LLM | Google Gemini — free tier |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) — local, free |
| Vector DB | ChromaDB — local, free |
| Web UI | Streamlit — free |
| Hosting | Streamlit Community Cloud — free |
