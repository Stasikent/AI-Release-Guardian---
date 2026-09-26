from types import SimpleNamespace

from app.rag.embeddings import HashingEmbedder, cosine_similarity
from app.rag.hybrid import hybrid_retrieve


class StubEmbedder:
    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "purchase" in lowered or "checkout" in lowered:
                vectors.append([1.0, 0.0])
            elif "authentication" in lowered or "login" in lowered:
                vectors.append([0.0, 1.0])
            else:
                vectors.append([0.0, 0.0])
        return vectors


def test_hashing_embedder_is_deterministic_and_normalized():
    embedder = HashingEmbedder(dimensions=64)
    first, second = embedder.encode(["checkout payment", "checkout payment"])
    assert first == second
    assert round(cosine_similarity(first, first), 6) == 1.0


def test_hybrid_retrieval_can_use_injected_semantic_signal():
    docs = [
        SimpleNamespace(id=1, title="Checkout", source="spec", content="Purchase flow must remain available."),
        SimpleNamespace(id=2, title="Authentication", source="spec", content="Login requires email and password."),
    ]
    result = hybrid_retrieve("checkout regression", docs, limit=2, embedder=StubEmbedder())
    assert result[0].document_id == 1
    assert len(result) == 1
    assert result[0].score > 0


def test_hybrid_retrieval_ranks_semantically_matching_document_first():
    docs = [
        SimpleNamespace(id=1, title="Checkout", source="spec", content="Purchase flow must remain available."),
        SimpleNamespace(id=2, title="Authentication", source="spec", content="Login requires email and password."),
    ]

    class BroadSignalEmbedder:
        def encode(self, texts: list[str]) -> list[list[float]]:
            vectors = []
            for index, text in enumerate(texts):
                lowered = text.lower()
                if index == 0 or "checkout" in lowered or "purchase" in lowered:
                    vectors.append([1.0, 0.0])
                else:
                    vectors.append([0.25, 0.75])
            return vectors

    result = hybrid_retrieve("checkout regression", docs, limit=2, embedder=BroadSignalEmbedder())
    assert len(result) == 2
    assert result[0].document_id == 1
    assert result[0].score > result[1].score
