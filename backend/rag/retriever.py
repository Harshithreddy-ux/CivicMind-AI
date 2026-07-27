import os
import faiss
import numpy as np
import logging
import asyncio
from google import genai
from backend.rag.document_loader import load_all_documents_in_directory

logger = logging.getLogger("civicmind.rag")

class RAGRetriever:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.index = None
        self.chunks = []
        self.embedding_model = 'text-embedding-004'
        self.is_initialized = False
        self.client = None
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"RAG failed to create GenAI client: {e}")

    def initialize(self):
        if self.is_initialized:
            return
        
        if not self.client:
            logger.warning("RAG: No Gemini API client available. RAG will remain disabled.")
            return

        logger.info("Initializing RAG vector database indexing...")
        self.chunks = load_all_documents_in_directory(self.data_dir)
        if not self.chunks:
            logger.info("RAG: No document chunks loaded.")
            return

        try:
            embeddings = []
            for chunk in self.chunks:
                response = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=chunk,
                    config=dict(task_type="RETRIEVAL_DOCUMENT")
                )
                embeddings.append(response.embeddings[0].values)
            
            embedding_matrix = np.array(embeddings).astype('float32')
            dimension = embedding_matrix.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embedding_matrix)
            self.is_initialized = True
            logger.info(f"RAG Vector Database successfully initialized with {len(self.chunks)} chunks.")
        except Exception as e:
            logger.error(f"Error initializing RAG embeddings: {e}")

    async def initialize_async(self):
        """Asynchronously initializes the RAG store in a background thread."""
        if self.is_initialized:
            return
        await asyncio.to_thread(self.initialize)

    def query(self, question: str, top_k: int = 3) -> str:
        if not self.is_initialized or not self.index or not self.client:
            return ""
        
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=question,
                config=dict(task_type="RETRIEVAL_QUERY")
            )
            query_embedding = np.array([response.embeddings[0].values]).astype('float32')
            
            distances, indices = self.index.search(query_embedding, top_k)
            results = []
            for i in indices[0]:
                if 0 <= i < len(self.chunks):
                    results.append(self.chunks[i])
            
            return "\n...\n".join(results)
        except Exception as e:
            logger.error(f"Error querying RAG retriever: {e}")
            return ""

    async def query_async(self, question: str, top_k: int = 3) -> str:
        """Asynchronously queries the RAG store in a thread pool."""
        if not self.is_initialized:
            await self.initialize_async()
        if not self.is_initialized or not self.index:
            return ""
        return await asyncio.to_thread(self.query, question, top_k)

# Singleton instance
rag_system = RAGRetriever(data_dir=os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))
