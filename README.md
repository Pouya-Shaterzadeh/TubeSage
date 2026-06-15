# 🧙 TubeSage

> *Don't watch it all. Know it all.*

**AI-powered YouTube summarizer & Q&A** — paste a video URL, get an instant summary and ask any question about the content. Powered by Groq, Cloudflare Workers AI, OpenRouter, LangChain, FAISS, and sentence-transformers.

---

## ✨ Features

- **Instant Summaries** — Get a concise, well-structured summary of any YouTube video in seconds
- **Smart Q&A** — Ask questions about the video and get accurate answers with timestamp references
- **RAG Architecture** — Uses FAISS vector search + LangChain for retrieval-augmented generation
- **Streaming Output** — Watch summaries and answers appear in real-time
- **Beautiful UI** — Cyberpunk-inspired dark theme with neon accents, animated constellation background, and rotating crystal logo

---

## 🚀 Live Demo

Deployed on Streamlit Cloud: **[tubesage.streamlit.app](https://tubesage.streamlit.app)**

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────┐
│                 STREAMLIT CLOUD                  │
│  ┌──────────┐  ┌─────────────────────────────┐  │
│  │ Streamlit│  │  sentence-transformers       │  │
│  │  UI      │──│  all-MiniLM-L6-v2 (CPU)     │  │
│  └──────────┘  │  FAISS (disk-persisted)     │  │
│                └─────────────────────────────┘  │
│                     │                            │
│                HTTPS API                         │
│                     ▼                            │
│  ┌──────────────────────────────────────────────┐  │
│  │  LLM Fallback Chain:                          │  │
│  │  1. Groq 70B (14K req/day free)               │  │
│  │  2. Cloudflare Workers AI (10K neurons/day)    │  │
│  │  3. OpenRouter (50 req/day free)              │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

| Component | Technology | Runtime |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Streamlit Cloud (free) |
| **LLM** | Groq → Cloudflare Workers AI → OpenRouter fallback chain | Free multi-provider |
| **Embeddings** | `all-MiniLM-L6-v2` via sentence-transformers | Runs in container (CPU) |
| **Vector Store** | FAISS | Disk-persisted per video |
| **Transcript** | `youtube-transcript-api` + `yt-dlp` (fallback) | Dual fetcher |
| **Orchestration** | LangChain (chains + prompts) | Python |

---

## 📦 Local Setup

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) (free tier — no credit card)
- Optional: [Cloudflare Workers AI](https://dash.cloudflare.com) API token (free, no credit card)
- Optional: [OpenRouter API key](https://openrouter.ai/keys) (free tier)

### Install

```bash
git clone https://github.com/Pouya-Shaterzadeh/TubeSage.git
cd TubeSage
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
# Create secrets file
cat > .streamlit/secrets.toml << EOF
GROQ_API_KEY = "gsk_your_key_here"
# Optional fallback providers:
# CLOUDFLARE_API_KEY = "your_cloudflare_api_token"
# CLOUDFLARE_ACCOUNT_ID = "your_cloudflare_account_id"
# OPENROUTER_API_KEY = "sk-or-v1-your_key_here"
EOF
```

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## ☁️ Deploy to Streamlit Cloud

1. Fork or clone this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create App**
3. Select repo: `your-username/TubeSage`, branch: `main`, main file: `app.py`
4. In app settings → **Secrets**, add:

```toml
GROQ_API_KEY = "gsk_your_key_here"
CLOUDFLARE_API_KEY = "your_cloudflare_api_token"  # optional
CLOUDFLARE_ACCOUNT_ID = "your_cloudflare_account_id"  # optional
OPENROUTER_API_KEY = "sk-or-v1-your_key_here"  # optional
```

5. Deploy — auto-redeploys on every push

---

## 🎨 Design

- **Theme**: Neo-Noir Cyberpunk — dark base, neon cyan `#00F0FF` and magenta `#FF00FF` accents
- **Typography**: Share Tech Mono (display) + Space Mono (body)
- **Background**: Animated Neon Constellation — SVG crystal orb + knowledge web with pulsing nodes
- **Logo**: Custom crystal octagon with play triangle, rotating continuously

---

## 📁 Project Structure

```
tubesage/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore
├── assets/
│   ├── logo.svg            # Vector logo
│   └── logo.png            # Raster favicon (256px)
├── .streamlit/
│   ├── config.toml         # Theme + server config
│   └── secrets.toml        # API keys (gitignored)
└── src/
    ├── config.py           # Central settings
    ├── models/
    │   ├── llm.py          # GroqLLM wrapper
    │   └── embeddings.py   # LocalEmbeddings (sentence-transformers)
    ├── youtube/
    │   └── transcript.py   # YouTube transcript + metadata
    └── rag/
        ├── vectorstore.py  # FAISS with disk persistence
        └── chains.py       # Summary + QA prompt chains
```

---

## 🔧 Configuration

The following can be set via environment variables or Streamlit secrets:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required**. Groq API key |
| `CLOUDFLARE_API_KEY` | — | Optional. Cloudflare Workers AI token |
| `CLOUDFLARE_ACCOUNT_ID` | — | Optional. Cloudflare account ID |
| `OPENROUTER_API_KEY` | — | Optional. OpenRouter API key |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model ID |
| `CLOUDFLARE_MODEL` | `@cf/meta/llama-3.1-8b-instruct-fp8-fast` | Cloudflare model |
| `OPENROUTER_MODEL` | `google/gemma-4-31b-it:free` | OpenRouter model |
| `LLM_TEMPERATURE` | `0.3` | 0-1, lower = more focused |
| `LLM_MAX_TOKENS` | `1024` | Max output tokens |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `CHUNK_SIZE` | `500` | Transcript chunk size |
| `CHUNK_OVERLAP` | `50` | Chunk overlap |
| `RETRIEVAL_K` | `5` | Number of chunks to retrieve for Q&A |
| `HF_TOKEN` | — | Optional — avoids HF download rate-limiting |

---

## 📄 License

MIT
