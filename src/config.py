import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def _get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return os.getenv(key, default)


def get_groq_api_key() -> str:
    return _get_secret("GROQ_API_KEY")


# ---- LLM ----
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# ---- Embeddings ----
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# ---- Chunking ----
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ---- Retrieval ----
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "5"))

# ---- Paths ----
FAISS_INDEX_DIR = Path(os.getenv("FAISS_INDEX_DIR", str(Path(__file__).parent.parent / "data" / "faiss_indexes")))
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
