import hashlib
import math
import re
from collections import Counter
from typing import Protocol

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-я0-9_]{2,}")


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Dependency-free local embedding baseline for semantic retrieval plumbing.

    It uses signed feature hashing over word tokens and character trigrams.
    This is intentionally lightweight and deterministic; production deployments
    can inject a sentence-transformer or remote embedding provider through the
    same encode() interface.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _features(self, text: str) -> Counter[str]:
        normalized = " ".join(TOKEN_RE.findall(text.lower()))
        words = normalized.split()
        features = Counter(f"w:{word}" for word in words)
        compact = normalized.replace(" ", "_")
        features.update(f"c3:{compact[i:i+3]}" for i in range(max(0, len(compact) - 2)))
        return features

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for feature, count in self._features(text).items():
                digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
                bucket = int.from_bytes(digest[:4], "big") % self.dimensions
                sign = 1.0 if digest[4] & 1 else -1.0
                vector[bucket] += sign * count
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append([value / norm for value in vector] if norm else vector)
        return vectors


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    return sum(x * y for x, y in zip(a, b))
