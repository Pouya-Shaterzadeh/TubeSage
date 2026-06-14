import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import (
    LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_K,
    get_groq_api_key,
)

# ─── Page Config ───
st.set_page_config(
    page_title="TubeSage — AI YouTube Summarizer",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* ── Base ── */
    .stApp {
        background: #06060E;
    }

    /* ── Constellation Background SVG ── */
    #tubesage-bg {
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -2;
        pointer-events: none;
    }

    /* ── Constellation Node Pulsing ── */
    .ts-node { animation: nodePulse 3s ease-in-out infinite; }
    .ts-node:nth-child(1)  { animation-delay: 0.0s; }
    .ts-node:nth-child(2)  { animation-delay: 0.3s; }
    .ts-node:nth-child(3)  { animation-delay: 0.6s; }
    .ts-node:nth-child(4)  { animation-delay: 0.9s; }
    .ts-node:nth-child(5)  { animation-delay: 1.2s; }
    .ts-node:nth-child(6)  { animation-delay: 1.5s; }
    .ts-node:nth-child(7)  { animation-delay: 1.8s; }
    .ts-node:nth-child(8)  { animation-delay: 2.1s; }
    .ts-node:nth-child(9)  { animation-delay: 2.4s; }
    .ts-node:nth-child(10) { animation-delay: 2.7s; }
    .ts-node:nth-child(11) { animation-delay: 1.0s; }
    .ts-node:nth-child(12) { animation-delay: 1.6s; }

    @keyframes nodePulse {
        0%, 100% { opacity: 0.35; r: 1.4; }
        50%      { opacity: 1;    r: 2.5; }
    }

    /* ── Connection Line Shimmer ── */
    .ts-line {
        stroke-dasharray: 4 12;
        animation: lineShimmer 4s linear infinite;
    }
    .ts-line:nth-child(odd)  { animation-duration: 5s; animation-delay: 0s; }
    .ts-line:nth-child(even) { animation-duration: 4s; animation-delay: 2s; }

    @keyframes lineShimmer {
        0%   { stroke-dashoffset: 0; }
        100% { stroke-dashoffset: 32; }
    }

    /* ── Crystal Rotation ── */
    .ts-crystal {
        animation: crystalRotate 20s linear infinite;
        transform-origin: 50px 50px;
    }
    @keyframes crystalRotate {
        0%   { transform: rotate(0deg) scale(1); }
        50%  { transform: rotate(180deg) scale(1.08); }
        100% { transform: rotate(360deg) scale(1); }
    }

    /* ── Crystal Glow Pulse ── */
    .ts-crystal-glow {
        animation: crystalGlow 4s ease-in-out infinite;
    }
    @keyframes crystalGlow {
        0%, 100% { opacity: 0.15; }
        50%      { opacity: 0.35; }
    }

    /* ── Starfield Drift ── */
    .ts-star { animation: starDrift 30s linear infinite; }
    @keyframes starDrift {
        0%   { opacity: 0.2; transform: translateY(0); }
        50%  { opacity: 0.6; transform: translateY(-3px); }
        100% { opacity: 0.2; transform: translateY(0); }
    }

    /* ── Subtle Scan Line Overlay ── */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 240, 255, 0.008) 2px,
            rgba(0, 240, 255, 0.008) 4px
        );
        pointer-events: none;
    }

    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown li, .stText {
        font-family: 'Share Tech Mono', 'Space Mono', 'Courier New', monospace !important;
    }

    /* Preserve Material Icons */
    [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] *,
    .st-emotion-cache-1dkvzay {
        font-family: "Material Icons", "Material Icons Outlined" !important;
    }

    /* Hide the sidebar collapse button entirely */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    .app-title {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        text-align: center;
        background: linear-gradient(135deg, #00F0FF 0%, #FF00FF 50%, #00F0FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        letter-spacing: 2px;
        animation: titleGlow 3s ease-in-out infinite;
    }
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 8px rgba(0,240,255,0.3)); }
        50% { filter: drop-shadow(0 0 20px rgba(255,0,255,0.4)); }
    }

    .app-subtitle {
        font-family: 'Space Mono', monospace !important;
        text-align: center;
        color: #6B7280;
        font-size: 0.9rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .terminal-cursor {
        display: inline-block;
        width: 10px;
        height: 20px;
        background: #00F0FF;
        animation: blink 1s step-end infinite;
        vertical-align: middle;
        margin-left: 2px;
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

    .glass-card {
        background: rgba(20, 20, 40, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(0,240,255,0.35);
        box-shadow: 0 4px 32px rgba(0,240,255,0.08), 0 0 0 1px rgba(0,240,255,0.1);
    }

    .neon-card {
        background: rgba(20,20,40,0.6);
        border: 1px solid rgba(255,0,255,0.25);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 0 20px rgba(255,0,255,0.08);
    }

    .video-info-bar {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background: rgba(0,240,255,0.05);
        border: 1px solid rgba(0,240,255,0.2);
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .stButton > button {
        font-family: 'Share Tech Mono', monospace !important;
        background: linear-gradient(135deg, rgba(0,240,255,0.15) 0%, rgba(255,0,255,0.1) 100%) !important;
        border: 1px solid rgba(0,240,255,0.3) !important;
        color: #00F0FF !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,240,255,0.25) 0%, rgba(255,0,255,0.2) 100%) !important;
        border-color: rgba(0,240,255,0.6) !important;
        box-shadow: 0 0 16px rgba(0,240,255,0.15) !important;
        color: #FFFFFF !important;
    }
    .stButton > button:active { transform: scale(0.98); }

    .primary-btn > button {
        background: linear-gradient(135deg, #00F0FF 0%, #0099CC 100%) !important;
        border: none !important;
        color: #0A0A0F !important;
        font-weight: 700 !important;
        box-shadow: 0 0 20px rgba(0,240,255,0.2) !important;
    }
    .primary-btn > button:hover {
        background: linear-gradient(135deg, #33F3FF 0%, #00B3E6 100%) !important;
        color: #0A0A0F !important;
        box-shadow: 0 0 32px rgba(0,240,255,0.35) !important;
    }

    .stTextInput > div > div > input {
        font-family: 'Space Mono', monospace !important;
        background: rgba(10,10,20,0.8) !important;
        border: 1px solid rgba(0,240,255,0.2) !important;
        color: #E0E0F0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(0,240,255,0.6) !important;
        box-shadow: 0 0 12px rgba(0,240,255,0.1) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #4a4a5e !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent !important; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace !important;
        background: transparent !important;
        color: #6B7280 !important;
        border: 1px solid transparent !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.5rem 1.5rem !important;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00F0FF !important;
        border-bottom: 2px solid #00F0FF !important;
        background: rgba(0,240,255,0.05) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #B0B0D0 !important;
        border-bottom: 2px solid rgba(0,240,255,0.3) !important;
    }

    .chat-msg {
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        border-radius: 10px;
        font-size: 0.9rem;
        line-height: 1.5;
        font-family: 'Space Mono', monospace !important;
    }
    .chat-msg.user {
        background: rgba(0,240,255,0.08);
        border: 1px solid rgba(0,240,255,0.2);
        margin-left: 2rem;
        color: #B0E0FF;
    }
    .chat-msg.assistant {
        background: rgba(255,0,255,0.06);
        border: 1px solid rgba(255,0,255,0.2);
        margin-right: 2rem;
        color: #E0C0FF;
    }

    [data-testid="stSidebar"] {
        background: rgba(10,10,25,0.95) !important;
        border-right: 1px solid rgba(0,240,255,0.1) !important;
    }
    .sidebar-header {
        font-family: 'Share Tech Mono', monospace !important;
        color: #00F0FF;
        font-size: 1.1rem;
        letter-spacing: 2px;
        border-bottom: 1px solid rgba(0,240,255,0.2);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #00F0FF, #FF00FF) !important;
    }

    .status-ok { color: #00FF88; font-family: 'Share Tech Mono', monospace !important; }
    .status-err { color: #FF3355; font-family: 'Share Tech Mono', monospace !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0A0A0F; }
    ::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,240,255,0.4); }

    .app-footer {
        text-align: center;
        padding: 2rem 0 0.5rem;
        color: #3a3a4e;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }

    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00FF88;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 4px #00FF88; }
        50% { opacity: 0.4; box-shadow: 0 0 12px #00FF88; }
    }
</style>
""", unsafe_allow_html=True)

st.html("""
<svg id="tubesage-bg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" preserveAspectRatio="xMidYMid slice">
    <defs>
        <radialGradient id="nodeGlowCyan" cx="50%" cy="50%">
            <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.9"/>
            <stop offset="100%" stop-color="#00F0FF" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="nodeGlowMagenta" cx="50%" cy="50%">
            <stop offset="0%" stop-color="#FF00FF" stop-opacity="0.9"/>
            <stop offset="100%" stop-color="#FF00FF" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="lineGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="#FF00FF" stop-opacity="0.15"/>
        </linearGradient>
        <linearGradient id="lineGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#FF00FF" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#00F0FF" stop-opacity="0.1"/>
        </linearGradient>
        <radialGradient id="crystalGrad" cx="50%" cy="50%">
            <stop offset="0%" stop-color="#00F0FF" stop-opacity="0.15"/>
            <stop offset="50%" stop-color="#FF00FF" stop-opacity="0.06"/>
            <stop offset="100%" stop-color="#00F0FF" stop-opacity="0"/>
        </radialGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
    </defs>

    <!-- Starfield -->
    <g class="ts-star" opacity="0.3">
        <circle cx="50" cy="80" r="0.8" fill="#00F0FF" style="animation-delay:0s"/>
        <circle cx="150" cy="30" r="0.6" fill="#FF00FF" style="animation-delay:2s"/>
        <circle cx="250" cy="120" r="0.7" fill="#00F0FF" style="animation-delay:5s"/>
        <circle cx="380" cy="45" r="0.9" fill="#FFFFFF" style="animation-delay:1s"/>
        <circle cx="480" cy="15" r="0.5" fill="#00F0FF" style="animation-delay:8s"/>
        <circle cx="560" cy="90" r="0.7" fill="#FF00FF" style="animation-delay:3s"/>
        <circle cx="650" cy="35" r="0.6" fill="#00F0FF" style="animation-delay:6s"/>
        <circle cx="750" cy="110" r="0.8" fill="#FFFFFF" style="animation-delay:4s"/>
        <circle cx="830" cy="50" r="0.5" fill="#FF00FF" style="animation-delay:7s"/>
        <circle cx="910" cy="85" r="0.7" fill="#00F0FF" style="animation-delay:1s"/>
        <circle cx="100" cy="180" r="0.6" fill="#00F0FF" style="animation-delay:9s"/>
        <circle cx="300" cy="250" r="0.5" fill="#FF00FF" style="animation-delay:2s"/>
        <circle cx="700" cy="200" r="0.8" fill="#00F0FF" style="animation-delay:5s"/>
        <circle cx="880" cy="260" r="0.6" fill="#FFFFFF" style="animation-delay:3s"/>
        <circle cx="120" cy="350" r="0.7" fill="#00F0FF" style="animation-delay:6s"/>
        <circle cx="620" cy="300" r="0.5" fill="#FF00FF" style="animation-delay:1s"/>
        <circle cx="820" cy="400" r="0.6" fill="#00F0FF" style="animation-delay:8s"/>
        <circle cx="200" cy="500" r="0.8" fill="#00F0FF" style="animation-delay:4s"/>
        <circle cx="400" cy="580" r="0.5" fill="#FF00FF" style="animation-delay:7s"/>
        <circle cx="600" cy="620" r="0.7" fill="#00F0FF" style="animation-delay:2s"/>
        <circle cx="800" cy="550" r="0.6" fill="#FFFFFF" style="animation-delay:5s"/>
        <circle cx="900" cy="630" r="0.5" fill="#00F0FF" style="animation-delay:9s"/>
        <circle cx="50" cy="620" r="0.7" fill="#FF00FF" style="animation-delay:1s"/>
        <circle cx="500" cy="680" r="0.6" fill="#00F0FF" style="animation-delay:3s"/>
    </g>

    <!-- Crystal Glow Background -->
    <circle cx="500" cy="350" r="120" fill="url(#crystalGrad)" class="ts-crystal-glow"/>

    <!-- Connection Lines (Knowledge Web) -->
    <g opacity="0.35">
        <line x1="120" y1="160" x2="300" y2="70" stroke="url(#lineGrad1)" stroke-width="0.8" class="ts-line"/>
        <line x1="300" y1="70" x2="520" y2="50" stroke="url(#lineGrad2)" stroke-width="0.8" class="ts-line"/>
        <line x1="520" y1="50" x2="780" y2="100" stroke="url(#lineGrad1)" stroke-width="0.8" class="ts-line"/>
        <line x1="780" y1="100" x2="900" y2="250" stroke="url(#lineGrad2)" stroke-width="0.8" class="ts-line"/>
        <line x1="900" y1="250" x2="850" y2="500" stroke="url(#lineGrad1)" stroke-width="0.8" class="ts-line"/>
        <line x1="850" y1="500" x2="650" y2="600" stroke="url(#lineGrad2)" stroke-width="0.8" class="ts-line"/>
        <line x1="650" y1="600" x2="350" y2="580" stroke="url(#lineGrad1)" stroke-width="0.8" class="ts-line"/>
        <line x1="350" y1="580" x2="100" y2="550" stroke="url(#lineGrad2)" stroke-width="0.8" class="ts-line"/>
        <line x1="100" y1="550" x2="40" y2="320" stroke="url(#lineGrad1)" stroke-width="0.8" class="ts-line"/>
        <line x1="40" y1="320" x2="120" y2="160" stroke="url(#lineGrad2)" stroke-width="0.8" class="ts-line"/>
        <!-- Inner web -->
        <line x1="300" y1="70" x2="500" y2="350" stroke="url(#lineGrad1)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
        <line x1="780" y1="100" x2="500" y2="350" stroke="url(#lineGrad2)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
        <line x1="850" y1="500" x2="500" y2="350" stroke="url(#lineGrad1)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
        <line x1="350" y1="580" x2="500" y2="350" stroke="url(#lineGrad2)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
        <line x1="120" y1="160" x2="500" y2="350" stroke="url(#lineGrad1)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
        <line x1="910" y1="250" x2="500" y2="350" stroke="url(#lineGrad2)" stroke-width="0.5" class="ts-line" opacity="0.5"/>
    </g>

    <!-- Constellations Nodes -->
    <g filter="url(#glow)">
        <circle cx="120" cy="160" r="2" fill="#FF00FF" class="ts-node"/>
        <circle cx="300" cy="70" r="2" fill="#00F0FF" class="ts-node"/>
        <circle cx="520" cy="50" r="2" fill="#FF00FF" class="ts-node"/>
        <circle cx="780" cy="100" r="2" fill="#00F0FF" class="ts-node"/>
        <circle cx="910" cy="250" r="2" fill="#FF00FF" class="ts-node"/>
        <circle cx="850" cy="500" r="2" fill="#00F0FF" class="ts-node"/>
        <circle cx="650" cy="600" r="2" fill="#FF00FF" class="ts-node"/>
        <circle cx="350" cy="580" r="2" fill="#00F0FF" class="ts-node"/>
        <circle cx="100" cy="550" r="2" fill="#FF00FF" class="ts-node"/>
        <circle cx="40" cy="320" r="2" fill="#00F0FF" class="ts-node"/>
        <circle cx="150" cy="450" r="1.5" fill="#FFFFFF" class="ts-node"/>
        <circle cx="780" cy="380" r="1.5" fill="#FFFFFF" class="ts-node"/>
    </g>

    <!-- Crystal (Octahedron Wireframe) -->
    <g class="ts-crystal" filter="url(#glow)">
        <!-- Outer diamond -->
        <polygon points="500,290 540,350 500,410 460,350" fill="none" stroke="#00F0FF" stroke-width="0.8" opacity="0.7"/>
        <!-- Inner diamond -->
        <polygon points="500,320 520,350 500,380 480,350" fill="none" stroke="#FF00FF" stroke-width="0.6" opacity="0.5"/>
        <!-- Cross lines -->
        <line x1="500" y1="290" x2="500" y2="410" stroke="#00F0FF" stroke-width="0.4" opacity="0.4"/>
        <line x1="460" y1="350" x2="540" y2="350" stroke="#FF00FF" stroke-width="0.4" opacity="0.4"/>
        <!-- Diagonal -->
        <line x1="480" y1="320" x2="520" y2="380" stroke="#00F0FF" stroke-width="0.3" opacity="0.3"/>
        <line x1="520" y1="320" x2="480" y2="380" stroke="#FF00FF" stroke-width="0.3" opacity="0.3"/>
    </g>
</svg>
""")

# ─── Lazy Imports ───
@st.cache_resource
def _load_embeddings():
    from src.models.embeddings import get_embeddings
    try:
        return get_embeddings()
    except Exception as e:
        st.error(f"Failed to load embedding model: {e}")
        st.stop()

@st.cache_resource
def _load_llm():
    from src.models.llm import get_llm
    return get_llm()


# ─── Session State ───
DEFAULTS = {
    "transcript_raw": None,
    "transcript_text": "",
    "video_id": None,
    "video_meta": None,
    "faiss_index_id": None,
    "summary_text": "",
    "chat_history": [],
    "fetch_error": "",
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─── Helpers ───
def format_duration(seconds):
    if not seconds:
        return ""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def stream_groq(prompt: str, system_prompt: str = ""):
    """Stream tokens from Groq."""
    from groq import Groq

    api_key = get_groq_api_key()
    if not api_key:
        yield "[Error: GROQ_API_KEY not set. Add it to .streamlit/secrets.toml]"
        return

    client = Groq(api_key=api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        stream = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=st.session_state.get("llm_temp", 0.3),
            max_tokens=st.session_state.get("llm_max_tokens", 1024),
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"\n\n[Error: {str(e)}]"


def _get_or_build_faiss(video_id: str, text: str):
    """Load cached FAISS index or build a new one."""
    from src.rag.vectorstore import load_faiss_index, build_faiss_index, chunk_transcript

    embeddings = _load_embeddings()
    index = load_faiss_index(video_id, embeddings)
    if index is None:
        chunks = chunk_transcript(text)
        index = build_faiss_index(video_id, chunks, embeddings)
        st.session_state.faiss_index_id = video_id
    return index


# ─── Callbacks ───
def on_fetch():
    """Fetch transcript from URL."""
    from src.youtube.transcript import get_transcript, format_transcript, get_video_metadata

    url = st.session_state.video_url_input.strip()
    if not url:
        return

    st.session_state.transcript_raw = None
    st.session_state.transcript_text = ""
    st.session_state.video_id = None
    st.session_state.video_meta = None
    st.session_state.faiss_index_id = None
    st.session_state.summary_text = ""
    st.session_state.chat_history = []

    try:
        raw, vid = get_transcript(url)
    except Exception as e:
        st.session_state.transcript_text = ""
        st.session_state.fetch_error = f"Transcript API error: {e}"
        return

    if raw is None:
        st.session_state.transcript_text = ""
        st.session_state.fetch_error = (
            "No English transcript found for this video. "
            "The video may not have captions, or the transcript could not be retrieved. "
            "Try a different video."
        )
        return

    st.session_state.fetch_error = ""
    st.session_state.transcript_raw = raw
    st.session_state.transcript_text = format_transcript(raw)
    st.session_state.video_id = vid
    st.session_state.video_meta = get_video_metadata(vid)


def on_summarize():
    """Run summarization using parallel map-reduce to handle long transcripts."""
    text = st.session_state.transcript_text
    if not text:
        return

    from src.rag.vectorstore import chunk_transcript
    from concurrent.futures import ThreadPoolExecutor, as_completed, wait
    from groq import Groq
    import time

    placeholder = st.empty()
    chunks = chunk_transcript(text)
    system = (
        "You are an expert AI assistant that creates concise summaries of YouTube video segments. "
        "Write a brief summary of the key points from this transcript segment. Ignore timestamps."
    )
    api_key = get_groq_api_key()
    llm_temp = st.session_state.get("llm_temp", 0.3)
    llm_max_tokens = st.session_state.get("llm_max_tokens", 1024)
    total_chunks = len(chunks)

    # Short transcript: summarize directly
    if total_chunks <= 5:
        prompt = (
            "Read the transcript below and create a concise summary capturing the core message, "
            "key points, and main insights. Write a single well-structured paragraph.\n\n"
            f"[Transcript]\n{text}\n\n[Summary]"
        )
        full = ""
        for token in stream_groq(prompt, system_prompt=system):
            full += token
            placeholder.markdown(f"""
            <div class="glass-card" style="font-family:'Space Mono',monospace; color:#E0E0F0; line-height:1.7; white-space:pre-wrap;">
            {full}
            </div>
            """, unsafe_allow_html=True)
        st.session_state.summary_text = full
        return

    # ── Parallel Map Phase ──
    def _summarize_one(chunk: str, idx: int) -> tuple[int, str]:
        """Summarize a single chunk with retry on rate-limit."""
        for attempt in range(3):
            try:
                client = Groq(api_key=api_key)
                resp = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Summarize this transcript segment in 2-3 sentences capturing only the key points:\n\n[Segment]\n{chunk}\n\n[Summary]"},
                    ],
                    temperature=llm_temp,
                    max_tokens=llm_max_tokens,
                )
                return (idx, resp.choices[0].message.content.strip())
            except Exception as e:
                err = str(e)
                if "429" in err or "rate_limit" in err.lower():
                    if attempt < 2:
                        time.sleep((attempt + 1) * 1.5)
                        continue
                if attempt < 2:
                    time.sleep(1)
                    continue
                return (idx, f"[Error: {err}]")
        return (idx, "[Error: summarization failed]")

    chunk_summaries: list = [None] * total_chunks
    completed = 0
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(_summarize_one, chunk, i): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            idx, summary = future.result()
            chunk_summaries[idx] = summary
            completed += 1
            status_text.caption(f"Summarizing chunks... {completed}/{total_chunks}")
    status_text.empty()

    chunk_summaries = [s for s in chunk_summaries if s and not s.startswith("[Error]")]
    if not chunk_summaries:
        st.error("Failed to summarize any chunks.")
        return

    # ── Reduce Phase (streamed) ──
    combined = "\n".join(f"[Segment {i+1}] {s}" for i, s in enumerate(chunk_summaries))

    reduce_system = (
        "You are an expert AI assistant that creates concise, insightful summaries of YouTube videos. "
        "Synthesize segment summaries into one well-structured paragraph. Be engaging and informative."
    )
    reduce_prompt = (
        "Below are summaries of different segments of a YouTube video. "
        "Synthesize them into one cohesive, well-written summary paragraph:\n\n"
        f"{combined}\n\n[Final Summary]"
    )

    full = ""
    for token in stream_groq(reduce_prompt, system_prompt=reduce_system):
        full += token
        placeholder.markdown(f"""
        <div class="glass-card" style="font-family:'Space Mono',monospace; color:#E0E0F0; line-height:1.7; white-space:pre-wrap;">
        {full}
        </div>
        """, unsafe_allow_html=True)
    st.session_state.summary_text = full


def on_ask(question: str):
    """Run RAG Q&A."""
    if not question or not st.session_state.transcript_text:
        return

    vid = st.session_state.video_id
    if not vid:
        return

    from src.rag.vectorstore import search_index

    index = _get_or_build_faiss(vid, st.session_state.transcript_text)
    results = search_index(index, question)
    context = "\n---\n".join([r.page_content for r in results])

    system = (
        "You are an expert answering questions about a YouTube video based on its transcript. "
        "Answer using ONLY the context below. Be precise and include timestamps (Start: X.X) where relevant. "
        "If the context doesn't contain enough info, say so honestly."
    )
    prompt = (
        f"[Context from Transcript]\n{context}\n\n"
        f"[Question]\n{question}\n\n[Answer]"
    )

    placeholder = st.empty()
    full = ""
    for token in stream_groq(prompt, system_prompt=system):
        full += token
        placeholder.markdown(f"""
        <div class="chat-msg assistant" style="font-family:'Space Mono',monospace; color:#E0C0FF; line-height:1.7; white-space:pre-wrap;">
        <strong style="color:#6B7280; font-size:0.75rem; letter-spacing:2px;">▹ TUBESAGE</strong><br>
        {full}
        </div>
        """, unsafe_allow_html=True)

    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": full})


# ═══════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════

st.markdown("""
<div style="text-align:center; margin-bottom:1rem;">
    <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjggMTI4IiBmaWxsPSJub25lIj4KICA8ZGVmcz4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iYm9yZGVyR3JhZCIgeDE9IjAiIHkxPSIwIiB4Mj0iMSIgeTI9IjEiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjMDBGMEZGIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iNDAlIiBzdG9wLWNvbG9yPSIjMDBCOEU2Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iNjAlIiBzdG9wLWNvbG9yPSIjRTYwMEU2Ii8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0ZGMDBGRiIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0ib3JiR3JhZCIgY3g9IjQ1JSIgY3k9IjQwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxQTJBNEEiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI2MCUiIHN0b3AtY29sb3I9IiMwRjEwMjUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMDYwNjBFIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJwbGF5R2xvdyIgY3g9IjUwJSIgY3k9IjUwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMwMEYwRkYiIHN0b3Atb3BhY2l0eT0iMC4yNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMEYwRkYiIHN0b3Atb3BhY2l0eT0iMCIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iYWNjZW50R2xvdyIgY3g9IjUwJSIgY3k9IjUwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRjAwRkYiIHN0b3Atb3BhY2l0eT0iMC4yMCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNGRjAwRkYiIHN0b3Atb3BhY2l0eT0iMCIvPgogICAgPC9yYWRpYWxHcmFkaWVudD4KICAgIDxmaWx0ZXIgaWQ9Im91dGVyR2xvdyIgeD0iLTMwJSIgeT0iLTMwJSIgd2lkdGg9IjE2MCUiIGhlaWdodD0iMTYwJSI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjIuNSIgcmVzdWx0PSJibHVyIi8+CiAgICAgIDxmZU1lcmdlPjxmZU1lcmdlTm9kZSBpbj0iYmx1ciIvPjxmZU1lcmdlTm9kZSBpbj0iU291cmNlR3JhcGhpYyIvPjwvZmVNZXJnZT4KICAgIDwvZmlsdGVyPgogICAgPGZpbHRlciBpZD0iaW5uZXJHbG93IiB4PSItNTAlIiB5PSItNTAlIiB3aWR0aD0iMjAwJSIgaGVpZ2h0PSIyMDAlIj4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iMS41IiByZXN1bHQ9ImJsdXIiLz4KICAgICAgPGZlTWVyZ2U+PGZlTWVyZ2VOb2RlIGluPSJibHVyIi8+PGZlTWVyZ2VOb2RlIGluPSJTb3VyY2VHcmFwaGljIi8+PC9mZU1lcmdlPgogICAgPC9maWx0ZXI+CiAgPC9kZWZzPgogIDxwb2x5Z29uIHBvaW50cz0iNjQsOCA5MiwyNCAxMTYsNTIgMTIwLDgwIDEwNCwxMDggNzYsMTIwIDQ4LDEyMCAyMCwxMDggOCw4MCAxMiw1MiAzNiwyNCIgZmlsbD0iIzBBMEEwRiIgc3Ryb2tlPSJ1cmwoI2JvcmRlckdyYWQpIiBzdHJva2Utd2lkdGg9IjEuOCIgZmlsdGVyPSJ1cmwoI291dGVyR2xvdykiIG9wYWNpdHk9IjAuOSIvPgogIDxjaXJjbGUgY3g9IjY0IiBjeT0iNjQiIHI9IjQ4IiBmaWxsPSJ1cmwoI29yYkdyYWQpIiBzdHJva2U9InVybCgjYm9yZGVyR3JhZCkiIHN0cm9rZS13aWR0aD0iMC44IiBvcGFjaXR5PSIwLjUiLz4KICA8Y2lyY2xlIGN4PSI2NCIgY3k9IjY0IiByPSI0NCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMDBGMEZGIiBzdHJva2Utd2lkdGg9IjAuNCIgb3BhY2l0eT0iMC4yIi8+CiAgPGcgb3BhY2l0eT0iMC4xMiIgZmlsdGVyPSJ1cmwoI2lubmVyR2xvdykiPgogICAgPGxpbmUgeDE9IjY0IiB5MT0iMjYiIHgyPSI2NCIgeTI9IjE2IiBzdHJva2U9IiMwMEYwRkYiIHN0cm9rZS13aWR0aD0iMSIvPgogICAgPGxpbmUgeDE9IjY0IiB5MT0iMTAyIiB4Mj0iNjQiIHkyPSIxMTIiIHN0cm9rZT0iIzAwRjBGRiIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgICA8bGluZSB4MT0iMjYiIHkxPSI2NCIgeDI9IjE2IiB5Mj0iNjQiIHN0cm9rZT0iIzAwRjBGRiIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgICA8bGluZSB4MT0iMTAyIiB5MT0iNjQiIHgyPSIxMTIiIHkyPSI2NCIgc3Ryb2tlPSIjMDBGMEZGIiBzdHJva2Utd2lkdGg9IjEiLz4KICAgIDxsaW5lIHgxPSIzOCIgeTE9IjM4IiB4Mj0iMzEiIHkyPSIzMSIgc3Ryb2tlPSIjRkYwMEZGIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogICAgPGxpbmUgeDE9IjkwIiB5MT0iMzgiIHgyPSI5NyIgeTI9IjMxIiBzdHJva2U9IiNGRjAwRkYiIHN0cm9rZS13aWR0aD0iMC43Ii8+CiAgICA8bGluZSB4MT0iMzgiIHkxPSI5MCIgeDI9IjMxIiB5Mj0iOTciIHN0cm9rZT0iI0ZGMDBGRiIgc3Ryb2tlLXdpZHRoPSIwLjciLz4KICAgIDxsaW5lIHgxPSI5MCIgeTE9IjkwIiB4Mj0iOTciIHkyPSI5NyIgc3Ryb2tlPSIjRkYwMEZGIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogIDwvZz4KICA8Y2lyY2xlIGN4PSI2NCIgY3k9IjY0IiByPSIzMiIgZmlsbD0idXJsKCNwbGF5R2xvdykiLz4KICA8cG9seWdvbiBwb2ludHM9IjUyLDQ0IDg4LDY0IDUyLDg0IiBmaWxsPSJub25lIiBzdHJva2U9InVybCgjYm9yZGVyR3JhZCkiIHN0cm9rZS13aWR0aD0iMi4yIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBmaWx0ZXI9InVybCgjaW5uZXJHbG93KSIvPgogIDxnIGZpbHRlcj0idXJsKCNpbm5lckdsb3cpIj4KICAgIDxjaXJjbGUgY3g9IjcyIiBjeT0iMzAiIHI9IjEuNSIgZmlsbD0iI0ZGMDBGRiIgb3BhY2l0eT0iMC44Ii8+CiAgICA8Y2lyY2xlIGN4PSI4OCIgY3k9IjQyIiByPSIxLjUiIGZpbGw9IiMwMEYwRkYiIG9wYWNpdHk9IjAuOCIvPgogICAgPGNpcmNsZSBjeD0iOTYiIGN5PSI2MCIgcj0iMS41IiBmaWxsPSIjRkYwMEZGIiBvcGFjaXR5PSIwLjYiLz4KICAgIDxjaXJjbGUgY3g9IjkyIiBjeT0iNzgiIHI9IjEuNSIgZmlsbD0iIzAwRjBGRiIgb3BhY2l0eT0iMC44Ii8+CiAgICA8Y2lyY2xlIGN4PSI3OCIgY3k9IjkyIiByPSIxLjUiIGZpbGw9IiNGRjAwRkYiIG9wYWNpdHk9IjAuOCIvPgogICAgPGNpcmNsZSBjeD0iNTYiIGN5PSI5NiIgcj0iMS41IiBmaWxsPSIjMDBGMEZGIiBvcGFjaXR5PSIwLjYiLz4KICAgIDxjaXJjbGUgY3g9IjM4IiBjeT0iODgiIHI9IjEuNSIgZmlsbD0iI0ZGMDBGRiIgb3BhY2l0eT0iMC44Ii8+CiAgICA8Y2lyY2xlIGN4PSIyNiIgY3k9IjcwIiByPSIxLjUiIGZpbGw9IiMwMEYwRkYiIG9wYWNpdHk9IjAuOCIvPgogICAgPGNpcmNsZSBjeD0iMjgiIGN5PSI0OCIgcj0iMS41IiBmaWxsPSIjRkYwMEZGIiBvcGFjaXR5PSIwLjYiLz4KICAgIDxjaXJjbGUgY3g9IjQwIiBjeT0iMzIiIHI9IjEuNSIgZmlsbD0iIzAwRjBGRiIgb3BhY2l0eT0iMC44Ii8+CiAgPC9nPgogIDxjaXJjbGUgY3g9IjU2IiBjeT0iMjIiIHI9IjAuOCIgZmlsbD0iIzAwRjBGRiIgb3BhY2l0eT0iMC41Ii8+CiAgPGNpcmNsZSBjeD0iNjQiIGN5PSIxMDYiIHI9IjAuOCIgZmlsbD0iI0ZGMDBGRiIgb3BhY2l0eT0iMC41Ii8+CiAgPGNpcmNsZSBjeD0iMzAiIGN5PSI2NCIgcj0iMC44IiBmaWxsPSIjMDBGMEZGIiBvcGFjaXR5PSIwLjUiLz4KICA8Y2lyY2xlIGN4PSI5OCIgY3k9IjY0IiByPSIwLjgiIGZpbGw9IiNGRjAwRkYiIG9wYWNpdHk9IjAuNSIvPgo8L3N2Zz4K" width="72" height="72" style="margin-bottom:0.5rem;">
</div>
""", unsafe_allow_html=True)
st.markdown('<h1 class="app-title">TUBESAGE</h1>', unsafe_allow_html=True)
st.markdown("<p class=\"app-subtitle\">Don't watch it all. Know it all.</p>", unsafe_allow_html=True)

# Video URL input
col_url, col_btn, _ = st.columns([5, 1, 1])
with col_url:
    st.text_input(
        "URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="video_url_input",
        label_visibility="collapsed",
    )
with col_btn:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    st.button("PROCESS", key="fetch_btn", on_click=on_fetch, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Video metadata bar
meta = st.session_state.video_meta
if meta and meta.get("title"):
    col_img, col_info, col_status = st.columns([1, 4, 1])
    with col_img:
        if meta.get("thumbnail"):
            st.image(meta["thumbnail"], use_container_width=True)
    with col_info:
        st.markdown(f"**{meta['title']}**")
        dur = format_duration(meta.get("duration", 0))
        st.caption(f"Channel: {meta.get('channel', '')}  ·  Duration: {dur}")
        if st.session_state.transcript_text:
            st.caption(f"Transcript: {len(st.session_state.transcript_text):,} characters loaded")
    with col_status:
        if st.session_state.transcript_text:
            st.markdown('<span class="status-ok"><span class="pulse-dot"></span>READY</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-err">NO TRANSCRIPT</span>', unsafe_allow_html=True)
    st.divider()

# No transcript state
if not st.session_state.transcript_text:
    if st.session_state.fetch_error:
        st.error(st.session_state.fetch_error)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem 1rem; margin:2rem 0;">
            <p style="font-size:1.2rem; color:#6B7280; letter-spacing:2px;">PASTE A YOUTUBE URL TO BEGIN</p>
            <p style="font-size:0.8rem; color:#3a3a4e; margin-top:1rem;">
            LLM: <span style="color:#00F0FF;">Llama 3.1 8B</span> via Groq
            &nbsp;·&nbsp;
            Embeddings: <span style="color:#FF00FF;">all-MiniLM-L6-v2</span>
            &nbsp;·&nbsp;
            FAISS Vector Search
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="app-footer">TubeSage v1.0 · Built with Streamlit · Deploy on Streamlit Cloud</div>', unsafe_allow_html=True)
    st.stop()

# ─── Tabs ───
tab1, tab2 = st.tabs(["Summary", "Ask Questions"])

with tab1:
    left, right = st.columns([3, 1])
    with left:
        st.markdown("### Video Summary")
    with right:
        st.button("GENERATE SUMMARY", key="summarize_btn", use_container_width=True)

    if st.session_state.summarize_btn:
        with st.spinner("Generating summary..."):
            on_summarize()

    elif st.session_state.summary_text:
        st.markdown(f"""
        <div class="glass-card" style="font-family:'Space Mono',monospace; color:#E0E0F0; line-height:1.7; white-space:pre-wrap;">
        {st.session_state.summary_text}
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### Ask Questions About This Video")

    for msg in st.session_state.chat_history:
        role_class = "user" if msg["role"] == "user" else "assistant"
        prefix = "▸ YOU" if msg["role"] == "user" else "▹ TUBESAGE"
        st.markdown(f"""
        <div class="chat-msg {role_class}">
            <strong style="color:#6B7280; font-size:0.75rem; letter-spacing:2px;">{prefix}</strong><br>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)

    col_q, col_a = st.columns([4, 1])
    with col_q:
        question = st.chat_input("Ask anything about this video...")
    with col_a:
        st.markdown("")  # spacer

    if question:
        with st.spinner("Searching transcript & generating answer..."):
            on_ask(question)
        st.rerun()


# ─── Sidebar ───
with st.sidebar:
    st.markdown('<p class="sidebar-header">CONTROLS</p>', unsafe_allow_html=True)

    st.markdown("**Model**")
    st.caption(f"LLM: `{LLM_MODEL}` via Groq")

    st.session_state.llm_temp = st.slider(
        "Temperature",
        min_value=0.0, max_value=1.0, value=0.3, step=0.05,
        help="Lower = focused, higher = creative",
    )
    st.session_state.llm_max_tokens = st.slider(
        "Max Output Tokens",
        min_value=128, max_value=4096, value=1024, step=128,
    )

    st.divider()
    st.markdown("**Chunking**")
    st.caption(f"Size: `{CHUNK_SIZE}` · Overlap: `{CHUNK_OVERLAP}` · Retrieval K: `{RETRIEVAL_K}`")

    st.divider()
    if st.button("CLEAR & RESET", use_container_width=True):
        for key in DEFAULTS:
            st.session_state[key] = DEFAULTS[key]
        st.rerun()

    st.divider()
    st.markdown(
        '<p style="font-size:0.7rem; color:#3a3a4e; text-align:center;">'
        'TubeSage v1.0<br>Groq · FAISS · LangChain'
        '</p>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="app-footer">TubeSage v1.0 · Built with Streamlit · Deploy on Streamlit Cloud</div>', unsafe_allow_html=True)
