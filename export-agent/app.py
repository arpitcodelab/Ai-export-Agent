"""
app.py — AI Export Facilitation Agent: Streamlit Chat Interface
================================================================
Run with:  streamlit run app.py

This is the main web UI. It:
  1. Shows a professional chat interface
  2. Takes the user's question
  3. Calls agent.py to get a cited answer
  4. Displays the answer with sources prominently
  5. Shows "I don't know" honestly when needed
"""

import os
import sys
from pathlib import Path
import streamlit as st

# ── Add src/ to path ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

# ── Load env ──────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

APP_TITLE = os.getenv("APP_TITLE", "AI Export Facilitation Agent")
APP_SUBTITLE = os.getenv("APP_SUBTITLE", "Your trusted guide to exporting from India")

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Professional, clean design
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Header area */
    .hero-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(79, 70, 229, 0.35);
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: white;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.82);
        margin: 0;
        font-weight: 400;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: white;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 18px;
        margin: 8px 0 8px 60px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .agent-message {
        background: rgba(30, 41, 59, 0.9);
        color: #e2e8f0;
        border-radius: 18px 18px 18px 4px;
        padding: 16px 20px;
        margin: 8px 60px 8px 0;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    .faq-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .fallback-badge {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .ai-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Sources block */
    .sources-block {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 12px;
        font-size: 0.84rem;
    }
    .sources-title {
        color: #818cf8;
        font-weight: 600;
        margin-bottom: 6px;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .source-item {
        color: #94a3b8;
        margin: 3px 0;
        padding-left: 12px;
        border-left: 2px solid rgba(99, 102, 241, 0.4);
    }
    .source-link {
        color: #60a5fa;
        text-decoration: none;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 14px 18px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4) !important;
    }
    
    /* Category pills */
    .category-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 16px;
    }
    .category-pill {
        background: rgba(99, 102, 241, 0.1);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .category-pill:hover {
        background: rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    /* Sidebar content */
    .sidebar-section {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 14px;
    }
    .sidebar-section-title {
        color: #818cf8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    .sidebar-item {
        color: #94a3b8;
        font-size: 0.85rem;
        padding: 4px 0;
        cursor: pointer;
    }
    .sidebar-item:hover {
        color: #e2e8f0;
    }
    
    /* Status indicators */
    .status-ok {
        color: #10b981;
        font-size: 0.8rem;
    }
    .status-warn {
        color: #f59e0b;
        font-size: 0.8rem;
    }
    .status-err {
        color: #ef4444;
        font-size: 0.8rem;
    }
    
    /* Scroll to bottom */
    .chat-container {
        max-height: 65vh;
        overflow-y: auto;
        padding-right: 4px;
    }
    
    /* Hide default Streamlit header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    hr {border-color: rgba(99, 102, 241, 0.15);}
    
    /* Metric cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #818cf8;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

if "agent_error" not in st.session_state:
    st.session_state.agent_error = None


# ─────────────────────────────────────────────────────────────────────────────
# Initialise Agent (cached so it only loads once per session)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading knowledge base...")
def load_agent():
    """Load and cache the retriever (ChromaDB connection)."""
    try:
        from retriever import get_retriever
        r = get_retriever()
        health = r.health_check()
        return {"retriever": r, "health": health, "error": None}
    except Exception as e:
        return {"retriever": None, "health": None, "error": str(e)}


@st.cache_resource(show_spinner="Checking API configuration...")
def load_agent_config():
    """Load and cache the agent configuration check."""
    try:
        from agent import check_api_keys
        return check_api_keys()
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style='margin-bottom:20px;'>
            <span style='font-size:1.8rem;'>🚢</span>
            <span style='font-weight:700; color:#e2e8f0; font-size:1rem; margin-left:8px;'>Export Agent</span>
        </div>
    """, unsafe_allow_html=True)
    
    # System status
    agent_data = load_agent()
    api_config = load_agent_config()
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)
    
    if agent_data["error"]:
        st.markdown(f'<div class="status-err">❌ Knowledge Base: Not Ready<br><small>{agent_data["error"][:80]}...</small></div>', unsafe_allow_html=True)
        st.info("Run `python src/build_index.py` to build the index.", icon="ℹ️")
    else:
        health = agent_data["health"]
        count = health.get("chunks_indexed", 0) if health else 0
        st.markdown(f'<div class="status-ok">✅ Knowledge Base: {count} facts indexed</div>', unsafe_allow_html=True)
    
    # API key status
    groq_ok = api_config.get("groq", {}).get("configured", False)
    gemini_ok = api_config.get("gemini", {}).get("configured", False)
    provider = api_config.get("active_provider", os.getenv("LLM_PROVIDER", "groq"))
    
    if groq_ok or gemini_ok:
        active = "Groq" if (groq_ok and provider == "groq") else "Gemini"
        st.markdown(f'<div class="status-ok">✅ AI ({active}): API key configured</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="status-warn">⚠️ AI: No API key set<br>'
            '<small>Add GROQ_API_KEY to .env (get a free key at console.groq.com)</small></div>',
            unsafe_allow_html=True,
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Stats
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Session Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.question_count}</div><div class="metric-label">Questions</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.messages)}</div><div class="metric-label">Messages</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Topic categories
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">📚 Topics Covered</div>', unsafe_allow_html=True)
    
    topics = [
        "🏁 How to start exporting",
        "📄 Documents & procedures",
        "🔢 IEC, GST, AD Code, RCMC",
        "🏷️ HS Codes",
        "🌐 Incoterms (FOB, CIF...)",
        "🚛 Logistics & customs",
        "💳 Payment methods",
        "🎁 Incentives & schemes",
        "✅ Certifications",
        "🌍 Country requirements",
        "📊 Trade intelligence",
        "🎪 Trade fairs",
        "❓ FAQs",
    ]
    for topic in topics:
        st.markdown(f'<div class="sidebar-item">{topic}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()
    
    # About
    st.markdown("""
    <div style='margin-top:20px; font-size:0.72rem; color:#475569; line-height:1.5;'>
    <strong style='color:#64748b;'>About</strong><br>
    Built on Groq + ChromaDB + Streamlit.<br>
    All answers are sourced from official Indian government documents.<br>
    This agent never guesses — if it doesn't know, it says so.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main Chat Area
# ─────────────────────────────────────────────────────────────────────────────

# Hero header
st.markdown(f"""
<div class="hero-header">
    <div class="hero-badge">🇮🇳 India Export AI — Powered by Official Government Sources</div>
    <div class="hero-title">🚢 {APP_TITLE}</div>
    <div class="hero-subtitle">{APP_SUBTITLE}</div>
</div>
""", unsafe_allow_html=True)

# Welcome message if no chat yet
if not st.session_state.messages:
    st.markdown("""
    <div style='
        background: rgba(30, 41, 59, 0.5);
        border: 1px dashed rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    '>
        <div style='font-size:2.5rem; margin-bottom:10px;'>👋</div>
        <div style='font-size:1.05rem; font-weight:600; color:#e2e8f0; margin-bottom:8px;'>
            Ask me anything about exporting from India
        </div>
        <div style='font-size:0.88rem; color:#64748b; margin-bottom:18px;'>
            I'll give you a clear, official-source-backed answer. I'll always tell you where the information comes from.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick-start example questions
    st.markdown("**💡 Try one of these questions:**")
    
    EXAMPLE_QUESTIONS = [
        "How do I start exporting from India?",
        "What is an IEC and how do I get one?",
        "What documents do I need to export to Germany?",
        "What is RoDTEP and am I eligible?",
        "What does FOB mean in a contract?",
        "Do I need FSSAI to export food products?",
        "What is the HS code for cotton bedsheets?",
        "How does customs clearance work for exports?",
        "What is a Letter of Credit?",
        "What are India-UAE CEPA benefits?",
    ]
    
    cols = st.columns(2)
    for i, q in enumerate(EXAMPLE_QUESTIONS):
        col = cols[i % 2]
        with col:
            if st.button(q, key=f"example_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.session_state.question_count += 1
                # Process immediately
                with st.spinner("🔍 Finding relevant information..."):
                    from agent import answer as get_answer
                    result = get_answer(q)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.text,
                    "sources": result.sources,
                    "is_faq": result.is_faq,
                    "is_fallback": result.is_fallback,
                    "chunks_count": len(result.chunks_used),
                })
                st.rerun()


# ── Display chat history ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🚢"):
            # Determine badge
            if msg.get("is_faq"):
                st.caption("⚡ **INSTANT FAQ ANSWER**")
            elif msg.get("is_fallback"):
                st.caption("❓ **KNOWLEDGE BASE LIMIT**")
            else:
                count = msg.get("chunks_count", 0)
                st.caption(f"🤖 **AI ANSWER** ({count} source documents used)")
            
            # Display text
            st.markdown(msg["content"])
            
            # Text-to-speech playback option
            if msg.get("content"):
                with st.expander("🔊 Listen to the answer", expanded=False):
                    try:
                        from voice import text_to_speech
                        audio = text_to_speech(msg["content"])
                        if audio:
                            st.audio(audio, format="audio/mp3")
                            st.caption("▶️ Click play to hear the answer read aloud.")
                        else:
                            st.caption("Audio not available right now.")
                    except Exception:
                        st.caption("Audio not available right now.")
            
            # Sources expander / list
            sources = msg.get("sources", [])
            if sources:
                with st.expander("📌 **Sources Used**", expanded=True):
                    for s in sources:
                        name = s.get("name", "")
                        url = s.get("url", "")
                        verified = s.get("last_verified", "")
                        if url:
                            st.markdown(f"- 📎 [{name}]({url}) *(verified: {verified})*")
                        else:
                            st.markdown(f"- 📎 **{name}** *(verified: {verified})*")


# ─────────────────────────────────────────────────────────────────────────────
# Input Area (always at bottom)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

# ── Voice input toggle ──────────────────────────────────────────────────────
st.markdown("### 🎙️ Voice Input (optional)")
with st.expander("🗣️ Click to record your question by voice", expanded=False):
    audio_bytes = st.audio_input(
        "Record your question",
        label_visibility="collapsed",
    )
    if audio_bytes is not None:
        with st.spinner("🎙️ Transcribing your voice..."):
            from voice import transcribe_audio
            voice_text = transcribe_audio(audio_bytes.getvalue(), language="auto")
        if voice_text:
            st.success(f"📝 Heard: **{voice_text}**")
            st.session_state.voice_transcription = voice_text
        else:
            st.warning("Couldn't understand the audio. Please try again or type your question.")

st.markdown("<br>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_input(
            label="Ask your export question",
            placeholder="e.g. What documents do I need to export spices to the USA?",
            label_visibility="collapsed",
            key="user_input_field",
        )
    
    with col_btn:
        submitted = st.form_submit_button("Send 🚀", use_container_width=True)


if submitted and user_input.strip():
    question = user_input.strip()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.question_count += 1
    
    # Get answer
    with st.spinner("🔍 Searching knowledge base and generating answer..."):
        try:
            from agent import answer as get_answer
            result = get_answer(question)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.text,
                "sources": result.sources,
                "is_faq": result.is_faq,
                "is_fallback": result.is_fallback,
                "chunks_count": len(result.chunks_used),
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ An error occurred: {str(e)}\n\nPlease check your setup and API keys in the `.env` file.",
                "sources": [],
                "is_faq": False,
                "is_fallback": True,
                "chunks_count": 0,
            })
    
    st.rerun()


# ── Process voice transcription if present ───────────────────────────────────
if "voice_transcription" in st.session_state and st.session_state.voice_transcription:
    voice_q = st.session_state.pop("voice_transcription")
    st.session_state.messages.append({"role": "user", "content": voice_q})
    st.session_state.question_count += 1
    with st.spinner("🔍 Searching knowledge base and generating answer..."):
        try:
            from agent import answer as get_answer
            result = get_answer(voice_q)
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.text,
                "sources": result.sources,
                "is_faq": result.is_faq,
                "is_fallback": result.is_fallback,
                "chunks_count": len(result.chunks_used),
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ An error occurred: {str(e)}\n\nPlease check your setup and API keys in the `.env` file.",
                "sources": [],
                "is_faq": False,
                "is_fallback": True,
                "chunks_count": 0,
            })
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='
    margin-top: 24px;
    padding: 14px;
    text-align: center;
    font-size: 0.75rem;
    color: #475569;
    border-top: 1px solid rgba(99, 102, 241, 0.1);
'>
    ⚠️ <strong style='color:#64748b;'>Disclaimer:</strong> 
    This agent provides guidance based on official government sources. 
    For binding legal or customs advice, always consult a licensed customs broker or trade consultant.
    Rules and fees change — verify important decisions against the current official source.
    <br><br>
    Sources: DGFT · CBIC · ICEGATE · RBI · FIEO · APEDA · FSSAI · BIS
</div>
""", unsafe_allow_html=True)
