import os
import hashlib
from rag.db.qdrant_wrapper import QdrantSubstrate
from common.proto import kuro_pb2

class KnowledgeIngestor:
    """
    Handles chunking and "embedding" of documents for VM 2.
    In a real implementation, this would use a local Transformer model.
    """
    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size

    def process_file(self, file_path: str) -> list:
        """
        Reads a file, chunks it, and returns a list of KnowledgeChunk messages.
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return []

        chunks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic chunking logic
        for i in range(0, len(content), self.chunk_size):
            text_chunk = content[i:i + self.chunk_size]
            chunk_hash = hashlib.sha256(text_chunk.encode()).hexdigest()[:8]
            
            chunks.append(kuro_pb2.KnowledgeChunk(
                text=text_chunk,
                score=1.0, # Base score during ingestion
                source=f"{os.path.basename(file_path)}#{chunk_hash}"
            ))
            
        return chunks

    def ingest_to_qdrant(self, chunks: list):
        """
        Sends chunks to Qdrant with placeholder vectors.
        """
        db = QdrantSubstrate(location=":memory:")
        for chunk in chunks:
            # Placeholder: Generate a dummy vector (size 384)
            # In Phase 2B/C, this will be a real embedding.
            dummy_vector = [0.0] * 384
            db.upsert_chunk(chunk.text, dummy_vector, {"source": chunk.source})
        print(f"Successfully ingested {len(chunks)} chunks into Qdrant substrate.")
