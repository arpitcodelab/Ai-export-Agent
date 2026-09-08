"""
main.py — FastAPI backend bridge for the AI Export Facilitation Agent landing page.

This backend REUSES the existing, untouched Python agent pipeline
(export-agent/src/agent.py, voice.py, nlp.py) and exposes it as a clean
JSON API for the React frontend while serving the React frontend itself.

Endpoints:
  GET  /health, /api/health        -> system + knowledge base status
  POST /chat,   /api/chat          -> {question} -> {text, sources, is_faq, is_fallback, chunks_count, intent}
  POST /voice/stt, /api/voice/stt  -> audio upload bytes -> {text}
  POST /voice/tts, /api/voice/tts  -> {text, lang?}     -> {audio: base64 mp3}
  GET  /                           -> React Landing Page (frontend/dist/index.html)
"""

import base64
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, File, Header, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Point at the existing export-agent pipeline ─────────────────────────────
AGENT_SRC = Path(__file__).resolve().parent.parent.parent / "export-agent" / "src"
if not AGENT_SRC.exists():
    AGENT_SRC = Path.cwd() / "export-agent" / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from agent import answer as agent_answer                        # noqa: E402
from agent import check_api_keys                                # noqa: E402
from nlp import process_question                                # noqa: E402
from retriever import get_retriever                             # noqa: E402
from voice import transcribe_audio, text_to_speech, is_groq_configured  # noqa: E402

app = FastAPI(title="India Export AI — Landing API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    try:
        chroma_file = Path(__file__).resolve().parent.parent.parent / "export-agent" / "data" / "vector_store" / "chroma.sqlite3"
        if not chroma_file.exists():
            print("ChromaDB index not found at startup — building now...")
            import subprocess
            build_script = Path(__file__).resolve().parent.parent.parent / "export-agent" / "src" / "build_index.py"
            if build_script.exists():
                subprocess.run([sys.executable, str(build_script)], check=True)
                print("ChromaDB index build completed.")
        get_retriever()
    except Exception as e:
        print(f"Warning: retriever warm-up failed: {e}")


# ── CORS ─────────────────────────────────────────────────────────────────────
raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
if raw_origins == "*":
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False
else:
    ALLOWED_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.strip()]
    ALLOW_CREDENTIALS = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API key auth (optional) ─────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "").strip()


async def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header")


# ── Request / response models ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class TTSRequest(BaseModel):
    text: str
    lang: Optional[str] = "en"


# ── API Routes (mounted on router for both /api and / prefixes) ─────────────
api_router = APIRouter()


@api_router.get("/health")
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


@api_router.post("/chat", dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    question = (req.question or "").strip()
    if not question:
        return {"error": "Empty question"}

    nlp = process_question(question)
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


@api_router.post("/voice/stt", dependencies=[Depends(require_api_key)])
async def voice_stt(audio: UploadFile = File(...), language: str = Form("en")):
    data = await audio.read()
    text = transcribe_audio(data, language=language)
    if text:
        return {"text": text}
    return {"error": "Could not transcribe audio", "text": None}


@api_router.post("/voice/tts", dependencies=[Depends(require_api_key)])
def voice_tts(req: TTSRequest):
    if not req.text:
        return {"error": "Empty text"}
    mp3 = text_to_speech(req.text, lang=req.lang or "en")
    if mp3:
        return {"audio": base64.b64encode(mp3).decode("utf-8"), "mime": "audio/mp3"}
    return {"error": "Text-to-speech failed", "audio": None}


# Mount routes at both /api and root level
app.include_router(api_router, prefix="/api")
app.include_router(api_router)


# ── Static Frontend Serving ─────────────────────────────────────────────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "dist"
if not FRONTEND_DIST.exists():
    alt_dist = Path.cwd() / "frontend" / "dist"
    if alt_dist.exists():
        FRONTEND_DIST = alt_dist

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
