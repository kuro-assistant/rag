from qdrant_client import QdrantClient
from qdrant_client.http import models
from common.proto import kuro_pb2
import uuid

class QdrantSubstrate:
    """
    VM 2: Qdrant Vector Substrate.
    Handles semantic retrieval of knowledge chunks.
    """
    def __init__(self, collection_name="kuro_knowledge", location=":memory:"):
        self.client = QdrantClient(location=location)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    def upsert_chunk(self, text: str, vector: list, metadata: dict):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": text, **metadata}
                )
            ]
        )

    def search(self, query_vector: list, limit=3) -> list:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        chunks = []
        for res in results:
            chunks.append(kuro_pb2.KnowledgeChunk(
                text=res.payload.get("text", ""),
                score=res.score,
                source=res.payload.get("source", "unknown")
            ))
        return chunks
