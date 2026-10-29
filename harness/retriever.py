from __future__ import annotations
from .ingest import COLLECTION, client, embedder


def retrieve(query: str, k: int = 4) -> list[dict]:
    v = embedder().encode(query, normalize_embeddings=True).tolist()
    hits = client().query_points(COLLECTION, query=v, limit=k).points
    return [
        {
            "id": h.id,
            "doc": h.payload["doc"],
            "text": h.payload["text"],
            "score": h.score,
        }
        for h in hits
    ]
