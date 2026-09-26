from __future__ import annotations

import os
from typing import Any

from app.rag.embeddings import HashingEmbedder


class SentenceTransformerEmbedder:
    """Optional production-grade local embedder.

    sentence-transformers is imported lazily so the default CI/API image stays
    lightweight. Set EMBEDDING_PROVIDER=sentence-transformers and install the
    optional dependency to enable it.
    """

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed; install optional embedding dependencies"
            ) from exc
        self.model_name = model_name
        self.model: Any = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() if hasattr(vector, "tolist") else list(vector) for vector in vectors]


def build_embedder():
    provider = os.getenv("EMBEDDING_PROVIDER", "hashing").strip().lower()
    if provider in {"hashing", "lightweight"}:
        return HashingEmbedder()
    if provider in {"sentence-transformers", "sentence_transformers", "st"}:
        model = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        try:
            return SentenceTransformerEmbedder(model)
        except RuntimeError:
            fallback = os.getenv("EMBEDDING_FALLBACK", "true").strip().lower()
            if fallback in {"1", "true", "yes", "on"}:
                return HashingEmbedder()
            raise
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")
