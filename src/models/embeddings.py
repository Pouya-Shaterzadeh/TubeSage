from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from typing import List


class LocalEmbeddings(Embeddings):
    """LangChain-compatible local sentence-transformers embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self._model = SentenceTransformer(model_name, device=device)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self._model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()


def get_embeddings() -> LocalEmbeddings:
    from src.config import EMBEDDING_MODEL, EMBEDDING_DEVICE
    return LocalEmbeddings(model_name=EMBEDDING_MODEL, device=EMBEDDING_DEVICE)
