import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "Backend"))

from dotenv import load_dotenv
load_dotenv(".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_rag_system():
    """Test FAISS-based RAG system"""
    print("\n" + "="*60)
    print("Testing RAG System")
    print("="*60)

    try:
        from Backend.RAGSystem import LocalRAGSystem, create_documents_from_text

        logger.info(" Initializing RAG system...")
        rag = LocalRAGSystem()

        test_docs = [
            "Python is a high-level programming language created by Guido van Rossum. It's known for its simplicity and readability.",
            "Machine Learning is a subset of AI that focuses on training models with data to make predictions.",
            "LangChain is a framework for developing applications powered by language models."
        ]

        for i, text in enumerate(test_docs):
            docs = create_documents_from_text(text, {"source": f"test_doc_{i}"})
            result = rag.add_documents(docs, f"test_doc_{i}.txt")
            logger.info(f" Document {i+1} added: {result['chunks_created']} chunks")

        queries = [
            "What is Python?",
            "Tell me about Machine Learning",
            "Explain LangChain"
        ]

        for query in queries:
            response = rag.query(query)
            logger.info(f"\nQuery: {query}")
            logger.info(f" Answer: {response.answer[:100]}...")
            logger.info(f" Confidence: {response.confidence:.2f}")
            logger.info(f" Sources: {[s.document_name for s in response.sources]}")

        stats = rag.get_db_stats()
        logger.info(f"\nRAG Stats: {stats}")
        print("\nRAG System Test PASSED")
        return True
    except Exception as e:
        logger.error(f" RAG System Test FAILED: {e}")
        return False


def test_agent_tools():
    """Test LangChain StructuredTools"""
    print("\n" + "="*60)
    print("Testing Agent Tools")
    print("="*60)
    try:
        from Backend.AgentTools import get_agent_tools, web_search, google_search

        logger.info("Loading agent tools...")
        tools = get_agent_tools()
        logger.info(f"Loaded {len(tools)} tools:")

        for tool in tools:
            logger.info(f"  • {tool.name}: {tool.description}")

        logger.info("\nTesting web search tool...")
        result = google_search.invoke({"query": "Python programming language"})
        logger.info(f"Result: {result}")

        print("\nAgent Tools Test PASSED")
        return True

    except Exception as e:
        logger.error(f"Agent Tools Test FAILED: {e}")
        return False


def test_orchestrator():
    """Test Agentic Orchestrator"""
    print("\n" + "="*60)
    print("🧪 Testing Agentic Orchestrator")
    print("="*60)

    try:
        from Backend.OrchestratorAgent import create_orchestrator

        logger.info("🤖 Creating orchestrator...")
        orchestrator = create_orchestrator(
            enable_rag=True,
            enable_tools=True,
            enable_streaming=True
        )

        test_queries = [
            ("What is the capital of France?", "general reasoning"),
            ("Search for machine learning tutorials", "tool routing"),
            ("What knowledge base documents do I have?", "RAG routing"),
        ]

        for query, query_type in test_queries:
            logger.info(f"\n📝 Testing {query_type}...")
            logger.info(f"Query: {query}")

            response = orchestrator.process_query(query)
            logger.info(f"Response: {response.response[:100]}...")
            logger.info(f"Used RAG: {response.used_rag}")
            logger.info(f"Tools: {response.used_tools}")
            logger.info(f"Confidence: {response.confidence:.2f}")
            logger.info(f"Execution time: {response.execution_time:.2f}s")

        stats = orchestrator.get_rag_stats()
        logger.info(f"\nRAG Stats: {stats}")

        print("\nOrchestrator Test PASSED")
        return True

    except Exception as e:
        logger.error(f" Orchestrator Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming():
    """Test async streaming with LCEL"""
    print("\n" + "="*60)
    print("🧪 Testing Streaming Handler")
    print("="*60)

    try:
        from Backend.StreamingHandler import AsyncStreamingHandler, StreamingUIAdapter
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage
        from dotenv import dotenv_values

        env = dotenv_values(".env")
        api_key = env.get("GroqAPIKey")

        if not api_key:
            logger.warning("⚠️  Groq API key not found, skipping streaming test")
            return True

        logger.info("⚡ Initializing streaming handler...")
        llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=api_key,
        )
        handler = AsyncStreamingHandler(llm)

        logger.info("Testing streaming response...")
        messages = [HumanMessage(content="Explain quantum computing in 50 words")]
        chunk_count = 0
        full_response = ""
        async for chunk in handler.stream_response(messages):
            chunk_count += 1
            full_response += chunk.token
            if chunk_count % 5 == 0:  # Log every 5 chunks
                logger.info(f" Received {chunk_count} chunks...")

        logger.info(f"Streaming complete: {chunk_count} chunks")
        logger.info(f"Response preview: {full_response[:100]}...")
        print("\nStreaming Handler Test PASSED")
        return True

    except Exception as e:
        logger.error(f"Streaming Handler Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot():
    """Test enhanced chatbot"""
    print("\n" + "="*60)
    print(" Testing Enhanced Chatbot")
    print("="*60)

    try:
        from Backend.Chatbot import EnhancedChatbot

        logger.info("🤖 Initializing chatbot...")
        chatbot = EnhancedChatbot()
        test_queries = [
            "Hello, how are you?",
            "What is Python?",
            "Current time and date",
        ]
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            response = chatbot.chat(query)
            logger.info(f"Response: {response[:100]}...")
        stats = chatbot.get_conversation_stats()
        logger.info(f"\nConversation stats: {stats}")
        print("\nEnhanced Chatbot Test PASSED")
        return True
    except Exception as e:
        logger.error(f"Enhanced Chatbot Test FAILED: {e}")
        return False


def test_upload_processor():
    """Test upload processor with FAISS integration"""
    print("\n" + "="*60)
    print("Testing Upload Processor")
    print("="*60)

    try:
        from Backend.UploadProcessor import get_indexed_documents
        logger.info("Checking indexed documents...")
        docs = get_indexed_documents()
        logger.info(f"Indexed documents: {docs}")
        logger.info("Note: Upload a PDF/DOCX to test indexing")
        logger.info("Example: from Backend.UploadProcessor import process_uploaded_file")
        logger.info("         result = process_uploaded_file('path/to/file.pdf')")

        print("\nUpload Processor Test PASSED")
        return True

    except Exception as e:
        logger.error(f"Upload Processor Test FAILED: {e}")
        return False


async def run_all_tests():
    """Run all component tests"""
    print("\n" + "="*80)
    print("🧪 LangChain Agentic RAG System - Comprehensive Test Suite")
    print("="*80)
    results = {}

    # Run synchronous tests
    results["RAG System"] = test_rag_system()
    results["Agent Tools"] = test_agent_tools()
    results["Orchestrator"] = test_orchestrator()
    results["Chatbot"] = test_chatbot()
    results["Upload Processor"] = test_upload_processor()

    # Run async tests
    results["Streaming Handler"] = await test_streaming()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for component, result in results.items():
        status = "PASS" if result else " FAIL"
        print(f"{component:.<40} {status}")
    print("="*80)
    print(f"Total: {passed}/{total} tests passed")
    if passed == total:
        print("All tests passed! System is ready to use.")
    else:
        print(f"{total - passed} test(s) failed. Check logs above.")
    print("="*80)
    return passed == total


if __name__ == "__main__":

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
