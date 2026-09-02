"""
agent.py — Pipeline B (Steps 2–3): AI Answer Generation
=========================================================
Orchestrates the full answer pipeline:
  1. Check FAQ shortcuts (instant pre-written answers)
  2. Retrieve relevant chunks from ChromaDB
  3. Build prompt (system prompt + retrieved facts + category add-ons)
  4. Call LLM (Groq primary, Gemini fallback)
  5. Return formatted answer with sources

Usage (standalone test):
  python src/agent.py "What is IEC?"

Requires: GROQ_API_KEY (or GEMINI_API_KEY) in .env file.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Ensure stdout handles UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── Load environment variables from .env ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ── Import local modules ──────────────────────────────────────────────────────
sys.path.insert(0, str(ROOT / "src"))
from prompts import (
    build_prompt,
    get_faq_answer,
    NO_ANSWER_FALLBACK,
    CORE_SYSTEM_PROMPT,
    CATEGORY_ADDONS,
)
from retriever import retrieve, get_retriever
from nlp import normalize_query, detect_intent, intent_label

# ── LLM Settings from environment ────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TOP_K = int(os.getenv("TOP_K_RESULTS", "5"))

# Placeholder values from .env.example — treat as "not configured"
_PLACEHOLDER_KEYS = {
    "your_groq_api_key_here",
    "your_gemini_api_key_here",
}


def is_api_key_configured(key: str) -> bool:
    """Return True only when a real (non-placeholder) API key is set."""
    return bool(key and key.strip() and key.strip() not in _PLACEHOLDER_KEYS)


# Models to try in order if primary fails.
# Includes only currently-active Groq production models so a fallback can't
# fail with model_not_found. `openai/gpt-oss-20b` is fast + widely available.
GROQ_FALLBACK_MODELS = list(dict.fromkeys([
    GROQ_MODEL,
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
]))

# How many times to retry a provider on transient rate-limit (429) errors.
RATE_LIMIT_RETRIES = 3
# Base seconds for exponential backoff between retries.
BACKOFF_SECONDS = 1.5


def _sleep_backoff(attempt: int) -> None:
    """Sleep with exponential backoff on transient errors."""
    import time
    time.sleep(BACKOFF_SECONDS * (2 ** attempt))


def _is_rate_limit(e: Exception) -> bool:
    """Best-effort check whether an exception is a transient 429 / quota error."""
    text = str(e).lower()
    return any(k in text for k in ["429", "rate limit", "quota", "too many requests",
                                   "resources exhausted", "insufficient_quota"])


# ─────────────────────────────────────────────────────────────────────────────
# LLM Clients
# ─────────────────────────────────────────────────────────────────────────────

def call_groq(prompt: str) -> str:
    """Call Groq API (free tier) and return the answer text."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq package not installed. Run: pip install groq")
    
    if not is_api_key_configured(GROQ_API_KEY):
        raise RuntimeError(
            "GROQ_API_KEY not set. "
            "Get a free key at https://console.groq.com and add it to your .env file."
        )
    
    client = Groq(api_key=GROQ_API_KEY)
    
    last_err = None
    # Try models in fallback order
    for model_name in GROQ_FALLBACK_MODELS:
        for attempt in range(RATE_LIMIT_RETRIES):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=4096,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                last_err = e
                # Retry transient rate-limit errors with backoff, then move on.
                if _is_rate_limit(e) and attempt < RATE_LIMIT_RETRIES - 1:
                    _sleep_backoff(attempt)
                    continue
                break  # non-rate-limit or retries exhausted -> try next model
        continue
            
    raise RuntimeError(f"Groq API call failed across all models: {last_err}")


def call_gemini(prompt: str) -> str:
    """Call Google Gemini API (free tier) and return the answer text."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError(
            "google-generativeai not installed. Run: pip install google-generativeai"
        )
    
    if not is_api_key_configured(GEMINI_API_KEY):
        raise RuntimeError(
            "GEMINI_API_KEY not set. "
            "Get a free key at https://aistudio.google.com/app/apikey and add it to .env."
        )
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    last_err = None
    for attempt in range(RATE_LIMIT_RETRIES):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                )
            )
            return response.text.strip()
        except Exception as e:
            last_err = e
            if _is_rate_limit(e) and attempt < RATE_LIMIT_RETRIES - 1:
                _sleep_backoff(attempt)
                continue
            break
    
    raise RuntimeError(f"Gemini API call failed: {last_err}")


def call_llm(prompt: str) -> str:
    """
    Call the configured LLM. Tries primary provider first, falls back to the other.
    """
    errors = []
    
    # Primary provider
    if LLM_PROVIDER == "groq" and is_api_key_configured(GROQ_API_KEY):
        try:
            return call_groq(prompt)
        except Exception as e:
            errors.append(f"Groq failed: {e}")
    
    if LLM_PROVIDER == "gemini" and is_api_key_configured(GEMINI_API_KEY):
        try:
            return call_gemini(prompt)
        except Exception as e:
            errors.append(f"Gemini failed: {e}")
    
    # Fallback to the other provider
    if LLM_PROVIDER == "groq" and is_api_key_configured(GEMINI_API_KEY):
        try:
            print("  [Agent] Groq unavailable, falling back to Gemini...")
            return call_gemini(prompt)
        except Exception as e:
            errors.append(f"Gemini fallback failed: {e}")
    
    if LLM_PROVIDER == "gemini" and is_api_key_configured(GROQ_API_KEY):
        try:
            print("  [Agent] Gemini unavailable, falling back to Groq...")
            return call_groq(prompt)
        except Exception as e:
            errors.append(f"Groq fallback failed: {e}")
    
    # Both failed
    error_details = "\n".join(f"  - {e}" for e in errors)
    raise RuntimeError(
        f"No LLM available. All providers failed:\n{error_details}\n\n"
        "Check your API keys in .env file and ensure they are valid.\n"
        "Get a free Groq key at: https://console.groq.com\n"
        "Get a free Gemini key at: https://aistudio.google.com/app/apikey"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Answer dataclass
# ─────────────────────────────────────────────────────────────────────────────

class Answer:
    """
    Structured response from the agent.
    
    Attributes:
        text: The answer text to show the user
        sources: List of source dicts [{"name": ..., "url": ..., "type": ...}]
        chunks_used: Raw chunks that were retrieved (for debugging)
        is_faq: True if answered from FAQ shortcut (no LLM call)
        is_fallback: True if no relevant chunks found (I don't know response)
    """
    def __init__(
        self,
        text: str,
        sources: list[dict] = None,
        chunks_used: list[dict] = None,
        is_faq: bool = False,
        is_fallback: bool = False,
    ):
        self.text = text
        self.sources = sources or []
        self.chunks_used = chunks_used or []
        self.is_faq = is_faq
        self.is_fallback = is_fallback
    
    def __repr__(self):
        return f"Answer(is_faq={self.is_faq}, is_fallback={self.is_fallback}, sources={len(self.sources)})"


def extract_sources(chunks: list[dict]) -> list[dict]:
    """Extract unique sources from retrieved chunks."""
    seen = set()
    sources = []
    for chunk in chunks:
        key = chunk.get("source_name", "")
        if key and key not in seen:
            seen.add(key)
            sources.append({
                "name": chunk.get("source_name", ""),
                "url": chunk.get("source_url", ""),
                "type": chunk.get("source_type", ""),
                "last_verified": chunk.get("last_verified_date", ""),
            })
    return sources


# ─────────────────────────────────────────────────────────────────────────────
# Main Agent function
# ─────────────────────────────────────────────────────────────────────────────

def answer(question: str, top_k: int = TOP_K) -> Answer:
    """
    Main agent function: given a question, return a structured Answer.
    
    Pipeline:
    1. Check FAQ shortcuts → instant answer if matched
    2. Retrieve top-K relevant chunks from ChromaDB
    3. If no relevant chunks → return "I don't know" fallback
    4. Build prompt with retrieved facts + category add-ons
    5. Call LLM → return cited answer
    
    Args:
        question: The user's question
        top_k: Number of knowledge base chunks to retrieve
    
    Returns:
        Answer object with text, sources, and metadata
    """
    
    # ── Step 0: NLP preprocessing ────────────────────────────────────────────
    # Normalise the query (expand abbreviations, clean filler) so the retriever
    # matches better, and detect intent for smarter routing.
    normalized_question = normalize_query(question)
    intent = detect_intent(question)

    # ── Step 1: FAQ Shortcut ─────────────────────────────────────────────────
    faq_answer = get_faq_answer(question)
    if faq_answer:
        return Answer(
            text=faq_answer,
            sources=[],
            chunks_used=[],
            is_faq=True,
            is_fallback=False,
        )
    
    # ── Step 2: Semantic Retrieval (uses normalised query for better match) ──
    try:
        chunks = retrieve(normalized_question, top_k=top_k)
    except RuntimeError as e:
        # Index not built yet
        return Answer(
            text=(
                f"⚠️ The knowledge base index is not ready yet.\n\n"
                f"Please run: `python src/build_index.py` to build it.\n\n"
                f"Technical details: {e}"
            ),
            is_fallback=True,
        )
    
    # ── Step 3: No Relevant Results → Fallback ───────────────────────────────
    if not chunks:
        return Answer(
            text=NO_ANSWER_FALLBACK,
            sources=[],
            chunks_used=[],
            is_faq=False,
            is_fallback=True,
        )
    
    # ── Step 4: Build Prompt ─────────────────────────────────────────────────
    # Identify categories in retrieved chunks (for add-on prompts)
    categories = list(set(c.get("category", "") for c in chunks))
    
    prompt = build_prompt(
        user_question=question,
        retrieved_chunks=chunks,
        categories=categories,
        intent=intent_label(intent),
    )
    
    # ── Step 5: Call LLM ─────────────────────────────────────────────────────
    try:
        llm_response = call_llm(prompt)
    except RuntimeError as e:
        return Answer(
            text=(
                f"⚠️ Could not connect to AI service.\n\n"
                f"Please check your API key in the `.env` file.\n\n"
                f"Error: {e}"
            ),
            sources=extract_sources(chunks),
            chunks_used=chunks,
            is_fallback=True,
        )
    
    # ── Step 6: Return structured answer ────────────────────────────────────
    return Answer(
        text=llm_response,
        sources=extract_sources(chunks),
        chunks_used=chunks,
        is_faq=False,
        is_fallback=False,
    )


def check_api_keys() -> dict:
    """
    Check which API keys are configured.
    Returns dict with status for each provider.
    """
    return {
        "groq": {
            "configured": is_api_key_configured(GROQ_API_KEY),
            "provider": "Groq (llama-3.3-70b)",
            "model": GROQ_MODEL,
        },
        "gemini": {
            "configured": is_api_key_configured(GEMINI_API_KEY),
            "provider": "Google Gemini",
            "model": GEMINI_MODEL,
        },
        "active_provider": LLM_PROVIDER,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI (for testing)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        question = "What is an IEC and how do I get one?"
    else:
        question = " ".join(sys.argv[1:])
    
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    # Check API keys
    keys = check_api_keys()
    print(f"Active LLM: {keys['active_provider']} ({keys[keys['active_provider']]['model']})")
    if not keys["groq"]["configured"] and not keys["gemini"]["configured"]:
        print("[WARN] WARNING: No API keys configured. Add GROQ_API_KEY to .env")
    
    result = answer(question)
    
    print(f"\n{'-'*60}")
    if result.is_faq:
        print("[FAQ SHORTCUT - pre-written answer]")
    elif result.is_fallback and not result.chunks_used:
        print("[FALLBACK - no relevant knowledge found]")
    elif result.is_fallback:
        print("[FALLBACK - AI service unavailable]")
    else:
        print(f"[AI answer using {len(result.chunks_used)} chunks]")
    
    print(f"\n{result.text}")
    
    if result.sources:
        print(f"\n{'-'*60}")
        print("Sources used:")
        for s in result.sources:
            url_str = f" ({s['url']})" if s['url'] else ""
            print(f"  * {s['name']}{url_str}")
