import grpc
from concurrent import futures
from common.proto import kuro_pb2
from common.proto import kuro_pb2_grpc
from rag.ingest.ingestor import KnowledgeIngestor
from rag.db.rag_db import RagDB

class RagServicer(kuro_pb2_grpc.RagServiceServicer):
    """
    gRPC Service for RAG Knowledge (VM 2).
    Uses Qdrant for semantic search.
    """
    def __init__(self):
        self.ingestor = KnowledgeIngestor()
        self.db = RagDB()

    def SearchKnowledge(self, request, context):
        """
        Perform semantic search against the knowledge base.
        """
        print(f"Searching knowledge for: {request.query}")
        response = kuro_pb2.SearchResponse()
        
        # Real query against SQLite
        results = self.db.search(request.query, limit=request.top_k)
        
        for content, source in results:
            response.chunks.append(kuro_pb2.KnowledgeChunk(
                text=content,
                score=0.9, # To be improved with real embeddings
                source=source
            ))
        else:
            # Fallback mock
            response.chunks.append(kuro_pb2.KnowledgeChunk(
                text=f"No direct knowledge found for '{request.query}'. Defaulting to general reasoning.",
                score=0.1,
                source="system_null"
            ))
        
        return response

    def IngestFile(self, request, context):
        """
        Manually trigger ingestion of a local file into the RAG DB.
        """
        chunks = self.ingestor.process_file(request.path)
        self.db.insert_chunks(chunks)
        return kuro_pb2.MemoryStatus(success=True, message=f"Ingested {len(chunks)} chunks from {request.path}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kuro_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("RAG Server starting on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
