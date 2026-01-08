import sqlite3
import datetime

class RagDB:
    """
    Persistence layer for VM 2 RAG Knowledge.
    Ensures knowledge chunks are stored on disk, not in memory.
    """
    def __init__(self, db_path="rag/db/kuro_rag.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    source TEXT,
                    embedding BLOB,
                    created_at TIMESTAMP
                )
            """)

    def insert_chunks(self, chunks):
        now = datetime.datetime.now()
        with self.conn:
            for chunk in chunks:
                self.conn.execute("""
                    INSERT INTO knowledge_chunks (content, source, created_at)
                    VALUES (?, ?, ?)
                """, (chunk.text, chunk.source, now))

    def search(self, query: str, limit: int = 3):
        # Basic keyword search since we aren't using a heavy embedding model yet
        with self.conn:
            cursor = self.conn.execute("""
                SELECT content, source FROM knowledge_chunks 
                WHERE content LIKE ? 
                LIMIT ?
            """, (f"%{query}%", limit))
            return cursor.fetchall()
