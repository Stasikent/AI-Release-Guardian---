import math
from collections import Counter

from app.models.knowledge import RetrievedContext
from app.rag.chunking import chunk_text
from app.rag.embeddings import HashingEmbedder, cosine_similarity
from app.rag.retriever import tokens


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[t] * b[t] for t in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _coverage(query: list[str], document: list[str]) -> float:
    q = set(query)
    return len(q & set(document)) / len(q) if q else 0.0


def hybrid_retrieve(query: str, documents: list, limit: int = 5, embedder=None) -> list[RetrievedContext]:
    embedder = embedder or HashingEmbedder()
    q = tokens(query)
    qc = Counter(q)
    raw_candidates = []

    for doc in documents:
        for chunk in chunk_text(doc.content):
            text = f"{doc.title} {chunk.text}"
            dt = tokens(text)
            lexical = _cosine(qc, Counter(dt))
            coverage = _coverage(q, dt)
            title_coverage = _coverage(q, tokens(doc.title))
            raw_candidates.append((doc, chunk, text, lexical, coverage, title_coverage))

    if not raw_candidates:
        return []

    vectors = embedder.encode([query] + [item[2] for item in raw_candidates])
    query_vector = vectors[0]
    candidates = []

    for item, vector in zip(raw_candidates, vectors[1:]):
        doc, chunk, _text, lexical, coverage, title_coverage = item
        semantic = max(0.0, cosine_similarity(query_vector, vector))
        score = 0.45 * semantic + 0.30 * lexical + 0.20 * coverage + 0.05 * title_coverage
        if score > 0:
            candidates.append(
                RetrievedContext(
                    document_id=doc.id,
                    title=doc.title,
                    source=f"{doc.source}#chunk-{chunk.index}",
                    excerpt=chunk.text,
                    score=round(score, 4),
                )
            )

    candidates.sort(key=lambda x: x.score, reverse=True)
    result = []
    seen = set()
    for item in candidates:
        key = (item.document_id, item.excerpt)
        if key not in seen:
            result.append(item)
            seen.add(key)
        if len(result) >= limit:
            break
    return result
