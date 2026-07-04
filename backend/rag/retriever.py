import os
import faiss
import numpy as np
import google.generativeai as genai
import asyncio
from backend.rag.document_loader import load_and_chunk_pdf

class RAGRetriever:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.index = None
        self.chunks = []
        self.embedding_model = 'models/embedding-001'
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return
        
        pdf_path = os.path.join(self.data_dir, "variables_description_indofloods.pdf")
        if not os.path.exists(pdf_path):
            print(f"RAG Warning: {pdf_path} not found.")
            return

        self.chunks = load_and_chunk_pdf(pdf_path)
        if not self.chunks:
            return

        try:
            # Generate embeddings for all chunks
            embeddings = []
            for chunk in self.chunks:
                response = genai.embed_content(
                    model=self.embedding_model,
                    content=chunk,
                    task_type="retrieval_document"
                )
                embeddings.append(response['embedding'])
            
            embedding_matrix = np.array(embeddings).astype('float32')
            dimension = embedding_matrix.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embedding_matrix)
            self.is_initialized = True
            print(f"RAG Initialized with {len(self.chunks)} chunks.")
        except Exception as e:
            print(f"Error initializing RAG: {e}")

    async def initialize_async(self):
        """Asynchronously initializes the RAG store in a background thread."""
        if self.is_initialized:
            return
        await asyncio.to_thread(self.initialize)

    def query(self, question: str, top_k: int = 3) -> str:
        if not self.is_initialized or not self.index:
            return ""
        
        try:
            response = genai.embed_content(
                model=self.embedding_model,
                content=question,
                task_type="retrieval_query"
            )
            query_embedding = np.array([response['embedding']]).astype('float32')
            
            distances, indices = self.index.search(query_embedding, top_k)
            results = []
            for i in indices[0]:
                if i >= 0 and i < len(self.chunks):
                    results.append(self.chunks[i])
            
            return "\n...\n".join(results)
        except Exception as e:
            print(f"Error querying RAG: {e}")
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
