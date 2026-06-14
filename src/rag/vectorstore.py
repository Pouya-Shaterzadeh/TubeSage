import hashlib
from pathlib import Path

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from src.config import CHUNK_SIZE, CHUNK_OVERLAP, FAISS_INDEX_DIR
from src.models.embeddings import LocalEmbeddings


def _get_index_path(video_id: str) -> Path:
    digest = hashlib.sha256(video_id.encode()).hexdigest()[:16]
    return FAISS_INDEX_DIR / f"{digest}"


def chunk_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(transcript)


def build_faiss_index(video_id: str, chunks: list[str], embeddings: LocalEmbeddings) -> FAISS:
    index = FAISS.from_texts(chunks, embeddings)
    path = _get_index_path(video_id)
    index.save_local(str(path))
    return index


def load_faiss_index(video_id: str, embeddings: LocalEmbeddings) -> FAISS | None:
    path = _get_index_path(video_id)
    if not path.exists():
        return None
    try:
        return FAISS.load_local(str(path), embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None


def search_index(index: FAISS, query: str, k: int = 5) -> list:
    from src.config import RETRIEVAL_K
    return index.similarity_search(query, k=k or RETRIEVAL_K)
