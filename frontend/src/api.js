// api.js — thin client for the FastAPI bridge.
// In dev, Vite proxies /api -> http://localhost:8000 (see vite.config.js).
// The proxy strips the /api prefix, so we call relative paths here.

const BASE = '/api'

async function handle(res) {
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`Request failed (${res.status}): ${body}`)
  }
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`)
  return handle(res)
}

export async function chat(question, topK = null) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  })
  return handle(res)
}

// Speech-to-text: upload audio bytes to the Whisper-backed endpoint.
export async function speechToText(audioBlob, language = 'en') {
  const form = new FormData()
  form.append('audio', audioBlob, 'voice.webm')
  form.append('language', language)
  const res = await fetch(`${BASE}/voice/stt`, {
    method: 'POST',
    body: form,
  })
  return handle(res)
}

// Text-to-speech: get base64 mp3 bytes for the given text.
export async function textToSpeech(text, lang = 'en') {
  const res = await fetch(`${BASE}/voice/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, lang }),
  })
  return handle(res)
}
