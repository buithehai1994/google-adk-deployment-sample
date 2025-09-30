# memory_service.py
import os
import sqlite3
import json
import logging
from pathlib import Path
from threading import Lock
from datetime import datetime
from typing import List, Dict, Any, Union
import hashlib

import numpy as np
from dotenv import load_dotenv
import faiss
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingSessionService:
    """Manages text embeddings for an agent's memory using SQLite and FAISS."""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.embedding_model = "models/text-embedding-004"
        self.embedding_dim = 768
        self.index = None
        self.index_to_event_id: List[str] = []
        self.index_lock = Lock()
        self._embedding_cache = {}

        try:
            self._create_vector_table_if_not_exists()
            self._load_index_from_db()
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingSessionService: {e}")
            raise

    def _create_vector_table_if_not_exists(self) -> None:
        """Creates the SQLite table for embeddings if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL UNIQUE,
                        session_id TEXT,
                        timestamp DATETIME,
                        content_text TEXT,
                        embedding_vector BLOB
                    )
                """)
                conn.commit()
                logger.info("Vector table created or already exists.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create vector table: {e}")
            raise

    def _save_index_to_disk(self) -> None:
        """Saves the FAISS index and event ID mapping to disk for fast loading."""
        if self.index and self.index.ntotal > 0:
            try:
                faiss.write_index(self.index, str(self.db_path.parent / "faiss_index.bin"))
                with open(self.db_path.parent / "index_to_event_id.json", "w") as f:
                    json.dump(self.index_to_event_id, f)
                logger.info("Faiss index saved to disk.")
            except Exception as e:
                logger.warning(f"Failed to save Faiss index: {e}")

    def _load_index_from_db(self) -> None:
        """Loads embeddings from disk or database and builds the FAISS index."""
        logger.info("Loading embeddings and building Faiss index...")
        index_file = self.db_path.parent / "faiss_index.bin"
        event_id_file = self.db_path.parent / "index_to_event_id.json"

        if index_file.exists() and event_id_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(event_id_file, "r") as f:
                    self.index_to_event_id = json.load(f)
                logger.info(f"Loaded Faiss index from disk with {self.index.ntotal} vectors.")
                return
            except Exception as e:
                logger.warning(f"Failed to load FAISS index from disk: {e}. Rebuilding from database.")

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT event_id, embedding_vector FROM event_embeddings ORDER BY timestamp ASC")
                rows = cursor.fetchall()

            self.index = faiss.IndexFlatIP(self.embedding_dim)
            if not rows:
                logger.info("No existing embeddings found. Initialized empty index.")
                return

            vectors = []
            self.index_to_event_id = []
            for row in rows:
                vector = np.frombuffer(row['embedding_vector'], dtype=np.float32)
                if vector.shape[0] != self.embedding_dim:
                    logger.warning(f"Skipping invalid vector for {row['event_id']}")
                    continue
                vectors.append(vector)
                self.index_to_event_id.append(row['event_id'])

            if vectors:
                vector_matrix = np.array(vectors).astype('float32')
                faiss.normalize_L2(vector_matrix)
                self.index.add(vector_matrix)
                self._save_index_to_disk()
                logger.info(f"FAISS index built with {self.index.ntotal} vectors.")
        except (sqlite3.Error, ValueError, faiss.FaissError) as e:
            logger.error(f"Failed to load index from DB: {e}")
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.warning("Initializing a new, empty FAISS index due to load failure.")

    def _get_text_hash(self, text: str) -> str:
        """Generates a hash for text to use as a cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def embed_text(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> Union[List[float], str]:
        """
        Generates an embedding for a given text with caching.
        
        Args:
            text: The text to embed.
            task_type: The task type for the embedding model (e.g., "RETRIEVAL_DOCUMENT").
            
        Returns:
            A list of floats (embedding) or an error string.
        """
        if not text or not text.strip():
            return "Cannot embed empty or invalid text."
        
        cache_key = f"{task_type}:{self._get_text_hash(text)}"
        if cache_key in self._embedding_cache:
            logger.info(f"Using cached embedding for text hash: {cache_key}")
            return self._embedding_cache[cache_key]
        
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type=task_type
            )
            embedding_vector = result['embedding']
            
            if len(embedding_vector) != self.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {len(embedding_vector)}")
            
            self._embedding_cache[cache_key] = embedding_vector
            logger.info(f"Generated and cached embedding for text hash: {cache_key}")
            
            return embedding_vector
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return f"Failed to generate embedding: {e}"

    def save_embedding(self, text: str, embedding: List[float]) -> str:
        """
        Saves a text and its embedding to the database and FAISS index.
        
        Args:
            text: The original text.
            embedding: The pre-computed embedding vector.
            
        Returns:
            A success message with the event_id or an error string.
        """
        if not text or not text.strip():
            return "Cannot save empty or invalid text."
        
        if isinstance(embedding, str):
            return f"Cannot save embedding due to error: {embedding}"
        
        try:
            vector_np = np.array(embedding, dtype=np.float32)
            if vector_np.shape[0] != self.embedding_dim:
                return f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {vector_np.shape[0]}"
            
            vector_bytes = vector_np.tobytes()
            event_id = f"mem_{datetime.now().timestamp()}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO event_embeddings (event_id, timestamp, content_text, embedding_vector) VALUES (?, ?, ?, ?)",
                    (event_id, datetime.now().isoformat(), text, vector_bytes)
                )
                conn.commit()

            with self.index_lock:
                faiss.normalize_L2(vector_np.reshape(1, -1))
                self.index.add(vector_np.reshape(1, -1))
                self.index_to_event_id.append(event_id)
                self._save_index_to_disk()

            return f"Saved: {event_id}"
            
        except Exception as e:
            logger.error(f"Failed to save embedding: {e}")
            return f"Failed to save embedding: {e}"

    def embed_and_save(self, text: str) -> str:
        """A convenience method that combines embedding and saving a text string."""
        embedding = self.embed_text(text, "RETRIEVAL_DOCUMENT")
        return self.save_embedding(text, embedding)

    def search_similar(self, query_embedding: List[float], k: int = 3) -> Union[List[Dict[str, Any]], str]:
        """
        Searches for similar embeddings using a pre-computed query embedding.
        
        Args:
            query_embedding: The pre-computed embedding for the search query.
            k: The number of results to return.
            
        Returns:
            A list of result dictionaries or an error string.
        """
        if isinstance(query_embedding, str):
            return f"Cannot search with invalid embedding: {query_embedding}"
        
        if not self.index or self.index.ntotal == 0:
            return "Memory is empty. Nothing to search."

        try:
            query_vector = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query_vector)

            with self.index_lock:
                distances, indices = self.index.search(query_vector, k)

            results = []
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                for i, idx in enumerate(indices[0]):
                    if idx < 0 or idx >= len(self.index_to_event_id):
                        continue
                    event_id = self.index_to_event_id[idx]
                    
                    similarity_score = float(distances[0][i])
                    
                    cursor.execute("SELECT content_text, timestamp FROM event_embeddings WHERE event_id = ?", (event_id,))
                    content_row = cursor.fetchone()
                    
                    if content_row:
                        results.append({
                            "similarity": similarity_score,
                            "content": content_row['content_text'],
                            "timestamp": content_row['timestamp'],
                            "event_id": event_id
                        })

            return results if results else "No relevant memories found."
            
        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            return f"Failed to search memory: {e}"

def setup_embedding_service(db_path: Path) -> EmbeddingSessionService:
    """Factory function to create and return an EmbeddingSessionService instance."""
    return EmbeddingSessionService(db_path=db_path)