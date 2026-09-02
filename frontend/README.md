# India Export AI — Landing Page (Frontend)

A responsive landing page that lets users **chat, talk, and listen** to the
existing AI Export Facilitation Agent — restyled using the Claude warm-canvas
editorial design system (`DESIGN.md`).

It does **not modify** the working codebase in `export-agent/`. Instead it runs
a small FastAPI bridge that reuses the agent pipeline as-is.

## Structure

```
frontend/
├── backend/
│   ├── main.py            # FastAPI bridge → reuses export-agent/src/*
│   └── requirements.txt   # fastapi, uvicorn, python-multipart
├── src/                   # React (Vite) landing page
│   ├── App.jsx
│   ├── api.js             # client for the FastAPI endpoints
│   ├── components/        # TopNav, Hero, Features, Coverage, Chat, CTA, FAQ, Footer
│   └── styles/            # tokens.css (DESIGN.md tokens) + global.css
├── index.html
├── package.json
└── vite.config.js
```

## How to run

### 1) Start the FastAPI backend bridge

From the `frontend/` folder (use your Windows Python where the agent deps live):

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

> The bridge adds `export-agent/src` to the import path automatically, so it
> picks up the same `agent.py`, `nlp.py`, `voice.py`, and `retriever.py` your
> Streamlit app already uses — zero changes to that codebase.

### 2) Start the React frontend

```bash
npm install
npm run dev
```

Open http://localhost:5173 .

Vite proxies `/api/*` to `http://localhost:8000` (see `vite.config.js`) so the
frontend talks to the backend with no extra configuration.

### 3) Production build

```bash
npm run build        # outputs static files to dist/
npm run preview
```

## API endpoints exposed by the bridge

| Method | Path          | Purpose                                     |
|--------|---------------|---------------------------------------------|
| GET    | `/health`     | Knowledge base + API key status             |
| POST   | `/chat`       | `{question}` → answer text, sources, intent |
| POST   | `/voice/stt`  | audio upload → transcribed text (Groq Whisper) |
| POST   | `/voice/tts`  | `{text}` → base64 mp3 audio (gTTS)          |

## Design reference

All colors, typography, spacing, radii, and components follow `DESIGN.md`
(cream canvas `#faf9f5`, warm coral `#cc785c`, dark navy surfaces `#181715`,
serif display via Cormorant Garamond, sans body via Inter).
