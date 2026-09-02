"""
voice.py — Speech-to-Text (STT) and Text-to-Speech (TTS) helpers
================================================================
Adds voice input and voice output to the agent.

STT: Uses Groq's free Whisper API (uses the existing GROQ_API_KEY).
     In the Streamlit app, the browser records audio (st.audio_input),
     and this module sends the audio bytes to Groq for transcription.

TTS: Uses gTTS (Google Text-to-Speech) to convert answers to audio,
     returned as a playable bytes object for the Streamlit UI.

Both are free to use. STT requires an internet connection.
"""

import io
import os
from pathlib import Path
from typing import Optional

# ── Load env (for GROQ_API_KEY) ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent


def is_groq_configured() -> bool:
    """Check whether a real Groq API key is present in the environment."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    key = os.getenv("GROQ_API_KEY", "").strip()
    placeholders = {"your_groq_api_key_here"}
    return bool(key and key not in placeholders)


def transcribe_audio(audio_bytes: bytes, language: str = "en") -> Optional[str]:
    """
    Transcribe recorded audio bytes to text using Groq's Whisper API.

    Args:
        audio_bytes: Raw audio file bytes (e.g. from st.audio_input).
        language: Optional ISO language code hint (e.g. 'en', 'hi', 'auto').

    Returns:
        Transcribed text, or None on failure.
    """
    if not audio_bytes:
        return None
    if not is_groq_configured():
        return None

    try:
        from groq import Groq
    except ImportError:
        return None

    client = Groq(api_key=os.getenv("GROQ_API_KEY").strip())

    try:
        # Groq expects an audio file: wrap bytes so the SDK uploads correctly.
        transcription = client.audio.transcriptions.create(
            file=("voice_input.webm", audio_bytes, "audio/webm"),
            model="whisper-large-v3-turbo",
            language=language if language != "auto" else None,
        )
        text = transcription.text.strip()
        return text if text else None
    except Exception:
        return None


def text_to_speech(text: str, lang: str = "en") -> Optional[bytes]:
    """
    Convert answer text to speech audio using gTTS.

    Args:
        text: The text to speak.
        lang: Language code (default 'en').

    Returns:
        MP3 audio bytes, or None on failure.
    """
    if not text:
        return None
    try:
        from gtts import gTTS
    except ImportError:
        return None

    try:
        # Strip markdown formatting so the speech isn't read verbatim.
        clean = strip_markdown(text)
        # Split into chunks smaller than Google's ~100 char-per-request limit
        # is handled internally by gTTS; just cap overall length for speed.
        if len(clean) > 3000:
            clean = clean[:3000]

        tts = gTTS(text=clean, lang=lang, slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception:
        return None


def strip_markdown(text: str) -> str:
    """
    Remove common markdown symbols so TTS reads naturally.
    E.g. '**Quick answer**' -> 'Quick answer', bullet markers removed.
    """
    import re

    # Remove bold/italic markers
    text = re.sub(r"\*\*|__|\*|~~", "", text)
    # Remove markdown link syntax [text](url) -> text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Remove heading hashes
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Remove bullet markers
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)
    # Squeeze blank lines and whitespace
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
