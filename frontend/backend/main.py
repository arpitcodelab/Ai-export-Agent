"""
main.py — FastAPI backend bridge for the AI Export Facilitation Agent landing page.

This backend REUSES the existing, untouched Python agent pipeline
(export-agent/src/agent.py, voice.py, nlp.py) and exposes it as a clean
JSON API for the React frontend.

Endpoints:
  GET  /health        -> system + knowledge base status
  POST /chat          -> {question} -> {text, sources, is_faq, is_fallback, chunks_count, intent}
  POST /voice/stt     -> audio upload bytes -> {text}
  POST /voice/tts     -> {text, lang?}     -> {audio: base64 mp3}

It does NOT modify any file inside export-agent/. It imports from that
folder at runtime by adding it to sys.path.
"""

import base64
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Point at the existing export-agent pipeline ─────────────────────────────
# The agent pipeline lives in <AI export>/export-agent/src. We import it
# directly so there is exactly ONE source of truth (no duplicated logic).
AGENT_SRC = Path(__file__).resolve().parent.parent.parent / "export-agent" / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from agent import answer as agent_answer                        # noqa: E402
from agent import check_api_keys                                # noqa: E402
from nlp import process_question                                # noqa: E402
from retriever import get_retriever                             # noqa: E402
from voice import transcribe_audio, text_to_speech, is_groq_configured  # noqa: E402

app = FastAPI(title="India Export AI — Landing API", version="1.0.0")

# ── CORS ─────────────────────────────────────────────────────────────────────
# Origins are read from an env var so each deployment (local dev, staging,
# production) can set its own allow-list instead of the API being open to
# every website on the internet. Defaults cover the Vite dev server only.
#
# Set in .env, e.g.:
#   ALLOWED_ORIGINS=https://your-frontend-domain.com,https://staging.your-frontend-domain.com
_default_dev_origins = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", _default_dev_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API key auth (optional) ─────────────────────────────────────────────────
# If API_KEY is set in the environment, every request must send it via the
# `X-API-Key` header, or it's rejected with 401. If API_KEY is left unset
# (e.g. local development), auth is skipped entirely — nothing breaks for
# people running this locally without configuring anything extra.
API_KEY = os.getenv("API_KEY", "").strip()


async def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not API_KEY:
        return  # auth disabled — no key configured
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header")


# ── Request / response models ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class TTSRequest(BaseModel):
    text: str
    lang: Optional[str] = "en"


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    kb_status = {"status": "unknown", "chunks": 0, "collection": None}
    try:
        r = get_retriever()
        kb = r.health_check()
        kb_status = {
            "status": kb.get("status"),
            "chunks": kb.get("chunks_indexed", 0),
            "collection": kb.get("collection"),
        }
    except Exception as e:
        kb_status = {"status": "error", "chunks": 0, "error": str(e)[:200]}

    return {
        "ok": True,
        "knowledge_base": kb_status,
        "apis": check_api_keys(),
        "voice_configured": is_groq_configured(),
        "name": "India Export AI",
    }


# ── Chat ────────────────────────────────────────────────────────────────────

@app.post("/chat", dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    question = (req.question or "").strip()
    if not question:
        return {"error": "Empty question"}

    # Run NLP pre-processing (normalise + intent) for better understanding.
    nlp = process_question(question)

    # Call the existing agent (no codebase changes).
    result = agent_answer(question, top_k=req.top_k) if req.top_k else agent_answer(question)

    return {
        "question": question,
        "normalized": nlp["normalized"],
        "intent": nlp["intent"],
        "intent_label": nlp["intent_label"],
        "text": result.text,
        "sources": result.sources,
        "is_faq": result.is_faq,
        "is_fallback": result.is_fallback,
        "chunks_count": len(result.chunks_used),
    }


# ── Voice: speech-to-text ───────────────────────────────────────────────────

@app.post("/voice/stt", dependencies=[Depends(require_api_key)])
async def voice_stt(audio: UploadFile = File(...), language: str = Form("en")):
    data = await audio.read()
    text = transcribe_audio(data, language=language)
    if text:
        return {"text": text}
    return {"error": "Could not transcribe audio", "text": None}


# ── Voice: text-to-speech ───────────────────────────────────────────────────

@app.post("/voice/tts", dependencies=[Depends(require_api_key)])
def voice_tts(req: TTSRequest):
    if not req.text:
        return {"error": "Empty text"}
    mp3 = text_to_speech(req.text, lang=req.lang or "en")
    if mp3:
        return {"audio": base64.b64encode(mp3).decode("utf-8"), "mime": "audio/mp3"}
    return {"error": "Text-to-speech failed", "audio": None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
