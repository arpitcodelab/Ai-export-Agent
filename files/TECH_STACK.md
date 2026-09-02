# TECH STACK — Everything Free, Explained Simply

This project is a **RAG chatbot**. RAG stands for "Retrieval-Augmented Generation" — in plain words: *"look up the answer in our own documents first, then let the AI explain it nicely."* This is important because it stops the AI from making things up (it must answer from your PDFs/Excel files, not from its own guesses).

## The 4 building blocks

### 1. The "brain" that writes answers (LLM)
**Choice: Groq API** (free tier)
- Why: Groq gives free, very fast access to strong open-source models (like Llama 3.3). No credit card needed to start, generous free daily limits.
- Backup option: **Google Gemini API free tier** — also genuinely free, slightly slower but very reliable, good backup if Groq's limits are hit.
- Avoid for Phase 1: OpenAI/Claude paid APIs — they work great but cost money per question, which breaks the "free" requirement. (We can switch to these later once the project has a budget — the design below makes that an easy swap, not a rebuild.)

### 2. The "librarian" that finds the right facts (Retrieval)
**Choice: ChromaDB** (free, open-source, runs on your own computer/server — no signup)
- This stores all your knowledge (from PDFs/Excel) as searchable "chunks."
- Paired with **sentence-transformers** (a free, open-source tool from Hugging Face) that turns text into a format the computer can search by meaning, not just keywords. Runs locally, no API cost.

### 3. The website / chat interface
**Choice for the working prototype: Streamlit** (free Python tool for building chat-style web apps quickly)
- Why: fastest way to get a real, working, demo-able website without heavy frontend coding. Perfect for a mentor demo and Phase 1 testing.
- Hosting: **Streamlit Community Cloud** (free) — one click to put it online with a shareable link.
- **Upgrade path**: once this is proven and you want a more "production" polished look (and to support voice + WhatsApp later), we migrate the interface to a simple **React + FastAPI** setup, still 100% free (hosted on Vercel + Render free tiers). This is a planned, expected step — not a mistake if Streamlit "looks basic" at first.

### 4. Where the knowledge base lives
**Choice: Plain files, not a paid database**
- Source knowledge: your PDFs and Excel files, converted into a clean **JSON** format (Excel as backup/human-readable version) — see KNOWLEDGE_BASE.md
- Searchable index: ChromaDB, stored as local files (a free built-in mode called "persistent client" — no server needed)

## Full picture (plain-English diagram)

```
Your PDFs/Excel files
        │
        ▼
 [Knowledge Base Builder]  →  turns documents into clean JSON + searchable index (ChromaDB)
        │
        ▼
 User asks a question on the website (Streamlit)
        │
        ▼
 [Retriever] finds the most relevant facts from ChromaDB
        │
        ▼
 [LLM: Groq/Gemini] writes a clear answer using ONLY those facts + cites the source
        │
        ▼
 Answer shown to user, with source reference
```

## Cost summary
| Component | Tool | Cost |
|---|---|---|
| AI brain | Groq API (backup: Gemini) | Free tier |
| Knowledge search | ChromaDB + sentence-transformers | Free, open-source |
| Website | Streamlit | Free |
| Hosting | Streamlit Community Cloud | Free |
| Voice (later) | Browser's built-in Web Speech API | Free |

No paid subscriptions anywhere in Phase 1. If free-tier limits ever become a real bottleneck (e.g. too many users), that's a future business decision, not something we need to solve now.

## What your coding agent needs installed
- Python 3.10+
- Packages: `streamlit`, `chromadb`, `sentence-transformers`, `groq` (or `google-generativeai`), `pandas`, `openpyxl` (for Excel), `pypdf` or `pdfplumber` (for reading your PDFs)
- All free/open-source, installable with `pip install`
