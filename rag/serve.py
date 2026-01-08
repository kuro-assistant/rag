import grpc
from concurrent import futures
from rag.db.qdrant_wrapper import QdrantSubstrate
from common.proto import kuro_pb2
from common.proto import kuro_pb2_grpc

class RagServicer(kuro_pb2_grpc.RagServiceServicer):
    """
    VM 2: RAG Knowledge Substrate Service.
    Now utilizes Qdrant for vector-based semantic retrieval.
    """
    def __init__(self):
        # In a real environment, location would be the Qdrant service IP.
        self.db = QdrantSubstrate(location=":memory:")

    def SearchKnowledge(self, request, context):
        print(f"RAG: Searching for pulse '{request.query}'")
        
        # Placeholder vector generation (size 384 for all-MiniLM-L6-v2)
        # In Phase 2B/C we would integrate a real embedding model here.
        dummy_vector = [0.0] * 384
        
        chunks = self.db.search(dummy_vector, limit=request.top_k)
        
        return kuro_pb2.SearchResponse(chunks=chunks)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kuro_pb2_grpc.add_RagServiceServicer_to_server(RagServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("RAG Knowledge Substrate (VM 2) starting on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
