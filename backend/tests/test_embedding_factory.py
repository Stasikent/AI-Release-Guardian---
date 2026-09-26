import pytest

from app.rag.embeddings import HashingEmbedder
from app.rag.sentence_transformer import build_embedder


def test_embedding_factory_defaults_to_lightweight(monkeypatch):
    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
    assert isinstance(build_embedder(), HashingEmbedder)


def test_embedding_factory_falls_back_when_optional_backend_is_unavailable(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence-transformers")
    monkeypatch.setenv("EMBEDDING_FALLBACK", "true")
    monkeypatch.setattr(
        "app.rag.sentence_transformer.SentenceTransformerEmbedder",
        lambda _model: (_ for _ in ()).throw(RuntimeError("missing optional dependency")),
    )
    assert isinstance(build_embedder(), HashingEmbedder)


def test_embedding_factory_can_fail_closed(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence-transformers")
    monkeypatch.setenv("EMBEDDING_FALLBACK", "false")
    monkeypatch.setattr(
        "app.rag.sentence_transformer.SentenceTransformerEmbedder",
        lambda _model: (_ for _ in ()).throw(RuntimeError("missing optional dependency")),
    )
    with pytest.raises(RuntimeError):
        build_embedder()
