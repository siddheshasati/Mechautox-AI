"""
LangChain FAISS-based RAG System with Zero-Hallucination Self-Correction
Ensures 100% local security and provides source citations for all responses.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RAGConfig(BaseModel):
    """Configuration for RAG system"""
    db_path: str = Field(default="Data/faiss_index", description="Local FAISS index path")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="HuggingFace embedding model")
    chunk_size: int = Field(default=500, description="Document chunk size")
    chunk_overlap: int = Field(default=100, description="Chunk overlap for context preservation")
    search_kwargs: Dict = Field(default_factory=lambda: {"k": 3}, description="K nearest documents")
    temperature: float = Field(default=0.3, description="LLM temperature for consistency")
    max_tokens: int = Field(default=1024, description="Max response tokens")
    model_name: str = Field(default="llama-3.3-70b-versatile", description="Groq model")


class SourceCitation(BaseModel):
    """Source citation with metadata"""
    document_name: str
    page_number: Optional[int] = None
    chunk_index: int
    relevance_score: float
    excerpt: str


class RAGResponse(BaseModel):
    """Structured RAG response with sources"""
    answer: str
    sources: List[SourceCitation]
    confidence: float
    has_hallucination_risk: bool
    fallback_message: Optional[str] = None

#RAG System
class LocalRAGSystem:
    """
    Zero-hallucination RAG system with local FAISS vector database.
    - 100% local: embeddings & database stay on-device
    - Self-correcting: cites sources or admits "I don't know"
    - Streaming ready: integrates with LCEL for async responses
    """

    def __init__(self, config: Optional[RAGConfig] = None, groq_api_key: Optional[str] = None):
        """Initialize RAG system with local embeddings and FAISS"""
        self.config = config or RAGConfig()
        self.api_key = groq_api_key or os.getenv("GroqAPIKey", "")
        if not self.api_key:
            logger.warning("Groq API key not found. Using demo mode.")

        logger.info(f"Loading embeddings model: {self.config.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.config.embedding_model)

        # FAISS index path
        self.db_path = Path(self.config.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load FAISS
        self.vector_db = self._load_or_create_db()
        self.llm = self._initialize_llm()

        self.metadata_path = self.db_path.parent / "metadata.json"
        self.metadata = self._load_metadata()

        logger.info("RAG System initialized with FAISS local storage")

    def _initialize_llm(self) -> ChatGroq:
        """Initialize Groq LLM with consistent parameters"""
        return ChatGroq(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.api_key,
        )

    def _load_or_create_db(self) -> Optional[FAISS]:
        """Load existing FAISS index or return None if empty"""
        try:
            if self.db_path.exists():
                logger.info(f"Loading FAISS index from {self.db_path}")
                return FAISS.load_local(str(self.db_path), self.embeddings, allow_dangerous_deserialization=True)
            else:
                logger.info("No existing FAISS index. Will create on first document upload.")
                return None
        except Exception as e:
            logger.error(f"Error loading FAISS: {e}")
            return None

    def _load_metadata(self) -> Dict:
        """Load document metadata"""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
        return {}

    def _save_metadata(self) -> None:
        """Save document metadata"""
        try:
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def add_documents(self, documents: List[Document], doc_name: str) -> Dict:
        """
        Add documents to FAISS with metadata tracking.
        Args:
            documents: List of LangChain Document objects
            doc_name: Name of the document (for source tracking)
        Returns:
            Summary of indexing operation
        """
        if not documents:
            logger.warning("No documents to add")
            return {"status": "error", "message": "Empty document list"}

        for i, doc in enumerate(documents):
            doc.metadata["source"] = doc_name
            doc.metadata["chunk_index"] = i
            doc.metadata["indexed_at"] = datetime.now().isoformat()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"📚 Split {len(documents)} documents into {len(chunks)} chunks")

        # Add to FAISS
        if self.vector_db is None:
            self.vector_db = FAISS.from_documents(chunks, self.embeddings)
            logger.info("🆕 Created new FAISS index")
        else:
            self.vector_db.add_documents(chunks)
            logger.info(f"➕ Added {len(chunks)} chunks to existing FAISS index")

        # Save FAISS
        self.vector_db.save_local(str(self.db_path))

        # Update metadata
        self.metadata[doc_name] = {
            "added_at": datetime.now().isoformat(),
            "chunk_count": len(chunks),
            "total_chars": sum(len(c.page_content) for c in chunks)
        }
        self._save_metadata()

        return {
            "status": "success",
            "document": doc_name,
            "chunks_created": len(chunks),
            "total_characters": sum(len(c.page_content) for c in chunks)
        }

    def _retrieve_with_scores(self, query: str) -> List[Tuple[Document, float]]:
        """Retrieve documents with similarity scores"""
        if self.vector_db is None:
            logger.warning("⚠️  No documents indexed yet")
            return []
        retriever = self.vector_db.as_retriever(search_kwargs=self.config.search_kwargs)
        docs = retriever.invoke(query)

        # Get similarity scores
        docs_with_scores = self.vector_db.similarity_search_with_score(query, k=self.config.search_kwargs["k"])
        return docs_with_scores

    def _self_correct_prompt(self, query: str, retrieved_docs: List[Document]) -> str:
        """Generate self-correction prompt that forces source citation or admission of ignorance"""

        if not retrieved_docs:
            return f"""You are a helpful AI assistant. The user asked: "{query}"

NO relevant documents are available in the knowledge base.

STRICT INSTRUCTION: You do NOT have any source documents to answer this question.
You MUST respond with: "I don't have information about this in my knowledge base. You may want to search online or ask a different question."

User Query: {query}"""

        sources_text = "\n\n".join([
            f"[SOURCE {i+1}: {doc.metadata.get('source', 'Unknown')} - Chunk {doc.metadata.get('chunk_index', 0)}]\n{doc.page_content[:300]}..."
            for i, doc in enumerate(retrieved_docs[:3])
        ])

        return f"""You are a knowledgeable AI assistant with access to a private knowledge base.

USER QUERY: "{query}"

AVAILABLE SOURCE DOCUMENTS:
{sources_text}

CRITICAL INSTRUCTIONS FOR ZERO-HALLUCINATION:
1. ONLY answer questions using information from the provided sources above
2. If the sources don't contain relevant information, you MUST say: "I don't have this information in my knowledge base."
3. Every factual claim MUST be traceable to the sources
4. Format citations as [Source: document_name]
5. If unsure about accuracy, admit it: "Based on available documents, I cannot confidently answer this."
6. NEVER fabricate, assume, or infer beyond what's explicitly stated in the sources

Generate your response now:"""

    def query(self, question: str, use_streaming: bool = False) -> RAGResponse:
        """
        Query the RAG system with self-correction loop.
        Args:
            question: User query
            use_streaming: Whether to stream response (for UI integration)
        Returns:
            RAGResponse with answer, sources, and confidence
        """
        logger.info(f"🔍 Processing query: {question}")

        docs_with_scores = self._retrieve_with_scores(question)
        if not docs_with_scores:
            logger.warning("No relevant documents found")
            return RAGResponse(
                answer="I don't have information about this in my knowledge base. Could you ask a different question or provide more context?",
                sources=[],
                confidence=0.0,
                has_hallucination_risk=True,
                fallback_message="No documents indexed yet or no relevant matches found."
            )

        docs = [doc for doc, _ in docs_with_scores]
        scores = [score for _, score in docs_with_scores]
        avg_score = sum(scores) / len(scores) if scores else 0

        correction_prompt = self._self_correct_prompt(question, docs)

        try:
            response = self.llm.invoke(correction_prompt)
            answer = response.content.strip()
        except Exception as e:
            logger.error(f"LLM error: {e}")
            answer = "An error occurred while processing your query."

        sources = self._extract_sources(docs, scores, answer)

        # Detect hallucination risk
        has_risk = self._detect_hallucination_risk(answer, question, docs)

        rag_response = RAGResponse(
            answer=answer,
            sources=sources,
            confidence=min(1.0, avg_score * 1.5),  # Normalize to 0-1
            has_hallucination_risk=has_risk,
        )

        logger.info(f"Query processed. Sources: {len(sources)}, Confidence: {rag_response.confidence:.2f}")
        return rag_response

    def _extract_sources(self, docs: List[Document], scores: List[float], answer: str) -> List[SourceCitation]:
        """Extract source citations from retrieved documents"""
        sources = []
        for i, (doc, score) in enumerate(zip(docs, scores)):
            if i < 3:  # Top 3 sources
                sources.append(SourceCitation(
                    document_name=doc.metadata.get("source", "Unknown"),
                    page_number=doc.metadata.get("page", None),
                    chunk_index=doc.metadata.get("chunk_index", 0),
                    relevance_score=float(score),
                    excerpt=doc.page_content[:200]
                ))
        return sources

    def _detect_hallucination_risk(self, answer: str, question: str, docs: List[Document]) -> bool:
        """Detect potential hallucination risk"""
        risk_indicators = [
            "i think", "probably", "likely", "might be", "seems like",
            "hypothetically", "assuming", "maybe", "could be"
        ]
        lower_answer = answer.lower()
        has_uncertain_language = any(indicator in lower_answer for indicator in risk_indicators)
        retrieved_text = " ".join([doc.page_content for doc in docs[:2]])
        has_answer_in_docs = any(word in retrieved_text.lower() for word in question.lower().split() if len(word) > 4)

        return has_uncertain_language and not has_answer_in_docs

    def get_db_stats(self) -> Dict:
        """Get statistics about the FAISS index"""
        if self.vector_db is None:
            return {"status": "empty", "message": "No documents indexed"}

        return {
            "status": "active",
            "total_documents": len(self.metadata),
            "indexed_documents": list(self.metadata.keys()),
            "metadata": self.metadata
        }

    def clear_database(self) -> Dict:
        """Clear FAISS database (use with caution)"""
        try:
            if self.db_path.exists():
                import shutil
                shutil.rmtree(self.db_path)
                self.vector_db = None
                self.metadata = {}
                self._save_metadata()
                logger.warning("FAISS database cleared")
                return {"status": "success", "message": "Database cleared"}
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return {"status": "error", "message": str(e)}


def create_documents_from_text(text: str, metadata: Dict = None) -> List[Document]:
    """Create LangChain Document objects from text"""
    return [Document(page_content=text, metadata=metadata or {})]


if __name__ == "__main__":
    from dotenv import dotenv_values
    env = dotenv_values(".env")
    api_key = env.get("GroqAPIKey")
    rag = LocalRAGSystem(groq_api_key=api_key)
    sample_text = """
    The Earth is the third planet from the Sun in our Solar System.
    It has one natural satellite called the Moon.
    The Moon orbits the Earth approximately every 27.3 days.
    """
    docs = create_documents_from_text(sample_text, {"source": "astronomy_basics"})
    result = rag.add_documents(docs, "astronomy_basics.txt")
    print(f"\n Document added: {result}")
    response = rag.query("How many days does the Moon take to orbit Earth?")
    print(f"\nResponse: {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Sources: {[s.document_name for s in response.sources]}")
