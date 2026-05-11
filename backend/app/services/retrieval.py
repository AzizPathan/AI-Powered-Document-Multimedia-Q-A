from dataclasses import dataclass
import hashlib
import math
import re
from collections import Counter

from app.models import TranscriptSegment
from app.services.text import chunk_text

try:
    import faiss
    import numpy as np
except ImportError:
    faiss = None
    np = None

VECTOR_DIMENSIONS = 384


@dataclass
class RetrievedChunk:
    text: str
    score: float
    start_seconds: float | None = None
    end_seconds: float | None = None


def build_corpus(text: str, segments: list[TranscriptSegment]) -> list[RetrievedChunk]:
    if segments:
        return [
            RetrievedChunk(segment.text, 1.0, segment.start_seconds, segment.end_seconds)
            for segment in segments
            if segment.text.strip()
        ]
    return [RetrievedChunk(chunk, 1.0) for chunk in chunk_text(text)]


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(token) > 2]


def retrieval_backend_name() -> str:
    return "faiss" if faiss is not None and np is not None else "tfidf"


def hashed_embedding(text: str, dimensions: int = VECTOR_DIMENSIONS) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        return vector
    return [value / norm for value in vector]


def faiss_search(question: str, corpus: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
    if faiss is None or np is None:
        return []

    matrix = np.array([hashed_embedding(item.text) for item in corpus], dtype="float32")
    query = np.array([hashed_embedding(question)], dtype="float32")
    if not matrix.size or not query.any():
        return []

    index = faiss.IndexFlatIP(VECTOR_DIMENSIONS)
    index.add(matrix)
    scores, indices = index.search(query, min(top_k, len(corpus)))

    results: list[RetrievedChunk] = []
    for score, index_value in zip(scores[0], indices[0]):
        if index_value < 0:
            continue
        item = corpus[int(index_value)]
        if float(score) > 0 or top_k == 1:
            results.append(
                RetrievedChunk(
                    text=item.text,
                    score=float(score),
                    start_seconds=item.start_seconds,
                    end_seconds=item.end_seconds,
                )
            )
    return results


def tfidf_vectors(documents: list[str]) -> list[dict[str, float]]:
    tokenized = [tokenize(document) for document in documents]
    doc_count = len(documents)
    document_frequency: Counter[str] = Counter()
    for tokens in tokenized:
        document_frequency.update(set(tokens))

    vectors: list[dict[str, float]] = []
    for tokens in tokenized:
        counts = Counter(tokens)
        total = max(len(tokens), 1)
        vector = {
            term: (count / total) * math.log((1 + doc_count) / (1 + document_frequency[term])) + 1
            for term, count in counts.items()
        }
        vectors.append(vector)
    return vectors


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[term] * right[term] for term in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def retrieve(question: str, text: str, segments: list[TranscriptSegment], top_k: int = 3) -> list[RetrievedChunk]:
    corpus = build_corpus(text, segments)
    if not corpus:
        return []

    faiss_results = faiss_search(question, corpus, top_k)
    if faiss_results:
        return faiss_results

    documents = [item.text for item in corpus]
    vectors = tfidf_vectors(documents + [question])
    query = vectors[-1]
    scores = [cosine(query, vector) for vector in vectors[:-1]]
    order = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)[:top_k]
    return [
        RetrievedChunk(
            text=corpus[index].text,
            score=float(scores[index]),
            start_seconds=corpus[index].start_seconds,
            end_seconds=corpus[index].end_seconds,
        )
        for index in order
        if scores[index] > 0 or top_k == 1
    ] or corpus[:top_k]


def find_topic_segments(topic: str, segments: list[TranscriptSegment], top_k: int = 5) -> list[RetrievedChunk]:
    return retrieve(topic, "", segments, top_k=top_k)
