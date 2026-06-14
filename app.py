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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a1a2e 0%, #0a0a0f 60%, #050510 100%);
    }

    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, p, span, div {
        font-family: 'Share Tech Mono', 'Space Mono', 'Courier New', monospace !important;
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
    """Run summarization using map-reduce to handle long transcripts."""
    text = st.session_state.transcript_text
    if not text:
        return

    from src.rag.vectorstore import chunk_transcript

    placeholder = st.empty()
    chunks = chunk_transcript(text)
    system = (
        "You are an expert AI assistant that creates concise summaries of YouTube video segments. "
        "Write a brief summary of the key points from this transcript segment. Ignore timestamps."
    )

    # If short enough for one API call, summarize directly
    if len(chunks) <= 3:
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

    # Long transcript: map-reduce
    chunk_summaries = []
    status_text = st.empty()
    for i, chunk in enumerate(chunks):
        status_text.caption(f"Summarizing segment {i+1}/{len(chunks)}...")
        prompt = (
            "Summarize this transcript segment in 2-3 sentences capturing only the key points:\n\n"
            f"[Segment]\n{chunk}\n\n[Summary]"
        )
        full_chunk = ""
        for token in stream_groq(prompt, system_prompt=system):
            full_chunk += token
        chunk_summaries.append(full_chunk.strip())
    status_text.empty()

    if not chunk_summaries:
        return

    # Combine chunk summaries into final summary
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

st.markdown('<h1 class="app-title">TUBESAGE<span class="terminal-cursor"></span></h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">AI-Powered YouTube Summarizer & Q&A</p>', unsafe_allow_html=True)

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
    st.button("FETCH", key="fetch_btn", on_click=on_fetch, use_container_width=True)
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

    with st.expander("View Full Transcript", expanded=False):
        txt = st.session_state.transcript_text
        st.text_area("Transcript", value=txt[:10000] + ("..." if len(txt) > 10000 else ""), height=300, disabled=True, label_visibility="collapsed")

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
