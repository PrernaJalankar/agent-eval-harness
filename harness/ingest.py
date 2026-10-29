from __future__ import annotations
import os
import pathlib
import re

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

COLLECTION = "docs"
_model = None


def embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def client() -> QdrantClient:
    return QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        check_compatibility=False,
    )


def chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    chunks, cur = [], ""
    for p in re.split(r"\n\s*\n", text):
        if len(cur) + len(p) > size and cur:
            chunks.append(cur.strip())
            cur = cur[-overlap:]
        cur += "\n\n" + p
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def ingest(corpus: str = "corpus", size: int = 800, overlap: int = 100) -> int:
    c, m = client(), embedder()
    if c.collection_exists(COLLECTION):
        c.delete_collection(COLLECTION)
    c.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    items = []
    for p in sorted(pathlib.Path(corpus).glob("*")):
        if p.is_file():
            items += [(p.name, ch) for ch in chunk(p.read_text(errors="ignore"), size, overlap)]
    if not items:
        return 0
    vecs = m.encode([t for _, t in items], normalize_embeddings=True)
    c.upsert(
        COLLECTION,
        points=[
            PointStruct(id=i, vector=v.tolist(), payload={"doc": d, "text": t})
            for i, ((d, t), v) in enumerate(zip(items, vecs))
        ],
    )
    return len(items)
