"""
Quick Start Examples for LangChain Agentic RAG System
Copy-paste ready code examples for common use cases
"""

import asyncio
from pathlib import Path

# ======================== Example 1: Basic Chat ========================

def example_basic_chat():
    """Example 1: Simple chat without RAG or tools"""
    print("="*60)
    print("Example 1: Basic Chat")
    print("="*60)
    
    from Backend.Chatbot import EnhancedChatbot
    
    chatbot = EnhancedChatbot()
    
    # Single query
    response = chatbot.chat("What is machine learning?")
    print(f"Response: {response}\n")
    
    # Multiple queries
    queries = [
        "Explain neural networks",
        "How do I learn Python?",
        "What is the current time?"
    ]
    
    for query in queries:
        print(f"Q: {query}")
        print(f"A: {chatbot.chat(query)}\n")


# ======================== Example 2: RAG System ========================

def example_rag_system():
    """Example 2: Query your private knowledge base"""
    print("="*60)
    print("Example 2: RAG System - Query Private Documents")
    print("="*60)
    
    from Backend.RAGSystem import LocalRAGSystem, create_documents_from_text
    
    # Initialize RAG
    rag = LocalRAGSystem()
    
    # Add sample documents
    sample_documents = [
        "Our company was founded in 2020. We specialize in AI solutions.",
        "Product X is our flagship offering. It uses advanced ML algorithms.",
        "We have 50 employees across 3 offices in US, EU, and Asia."
    ]
    
    print("📚 Adding documents to knowledge base...")
    for i, text in enumerate(sample_documents):
        docs = create_documents_from_text(text, {"doc_type": "company_info"})
        result = rag.add_documents(docs, f"company_doc_{i}.txt")
        print(f"  ✅ Added: {result['chunks_created']} chunks")
    
    # Query with sources
    print("\n🔍 Querying knowledge base...")
    response = rag.query("When was the company founded?")
    
    print(f"Answer: {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Sources:")
    for source in response.sources:
        print(f"  - {source.document_name} (relevance: {source.relevance_score:.2f})")


# ======================== Example 3: Agent Tools ========================

def example_agent_tools():
    """Example 3: Use agent tools for automation"""
    print("="*60)
    print("Example 3: Agent Tools - Automation")
    print("="*60)
    
    from Backend.OrchestratorAgent import create_orchestrator
    
    orchestrator = create_orchestrator()
    
    # Query that triggers tools
    print("📝 Query: Open Visual Studio Code and search Google for Python tutorials\n")
    
    response = orchestrator.process_query(
        "Open Visual Studio Code and search Google for Python tutorials"
    )
    
    print(f"Response: {response.response}")
    print(f"Tools used: {response.used_tools}")
    print(f"Execution time: {response.execution_time:.2f}s")


# ======================== Example 4: Intelligent Routing ========================

def example_intelligent_routing():
    """Example 4: Orchestrator intelligently routes queries"""
    print("="*60)
    print("Example 4: Intelligent Query Routing")
    print("="*60)
    
    from Backend.OrchestratorAgent import create_orchestrator
    
    orchestrator = create_orchestrator()
    
    queries = [
        ("What is quantum computing?", "General knowledge"),
        ("Search YouTube for AI tutorials", "Tool automation"),
        ("What documents do I have uploaded?", "RAG knowledge base"),
    ]
    
    for query, category in queries:
        print(f"\n📝 [{category}] {query}")
        response = orchestrator.process_query(query)
        print(f"Response: {response.response[:100]}...")
        print(f"  Used RAG: {response.used_rag}")
        print(f"  Tools: {response.used_tools}")
        print(f"  Confidence: {response.confidence:.2f}")


# ======================== Example 5: Streaming Responses ========================

async def example_streaming():
    """Example 5: Stream responses for real-time UI updates"""
    print("="*60)
    print("Example 5: Streaming Responses")
    print("="*60)
    
    from Backend.StreamingHandler import AsyncStreamingHandler
    from Backend.Chatbot import EnhancedChatbot
    from langchain_core.messages import HumanMessage
    
    chatbot = EnhancedChatbot()
    handler = chatbot.orchestrator.streaming_handler
    
    print("🚀 Streaming response (real-time):\n")
    
    messages = [HumanMessage(content="Explain machine learning in detail")]
    
    full_response = ""
    chunk_count = 0
    
    async for chunk in handler.stream_response(messages):
        # In real app, this updates UI in real-time
        print(chunk.token, end="", flush=True)
        full_response += chunk.token
        chunk_count += 1
    
    print(f"\n\n✅ Complete! ({chunk_count} chunks)")


# ======================== Example 6: Document Upload & Indexing ========================

def example_document_upload():
    """Example 6: Upload and index documents to knowledge base"""
    print("="*60)
    print("Example 6: Document Upload & Indexing")
    print("="*60)
    
    from Backend.UploadProcessor import process_uploaded_file, get_indexed_documents
    
    print("📁 Currently indexed documents:")
    docs = get_indexed_documents()
    for doc in docs:
        print(f"  - {doc}")
    
    print("\n📥 To upload a document:")
    print("  from Backend.UploadProcessor import process_uploaded_file")
    print("  result = process_uploaded_file('path/to/document.pdf')")
    print("  print(result)")
    
    print("\n❓ Then query it:")
    print("  from Backend.OrchestratorAgent import create_orchestrator")
    print("  orchestrator = create_orchestrator()")
    print("  response = orchestrator.process_query('What is in my document?')")


# ======================== Example 7: Conversation History ========================

def example_conversation_history():
    """Example 7: Manage conversation history"""
    print("="*60)
    print("Example 7: Conversation History Management")
    print("="*60)
    
    from Backend.Chatbot import EnhancedChatbot
    
    chatbot = EnhancedChatbot()
    
    # Simulate conversation
    conversation = [
        "What is Python?",
        "How do I learn it?",
        "What are decorators?"
    ]
    
    print("📝 Simulating conversation...\n")
    for query in conversation:
        print(f"User: {query}")
        response = chatbot.chat(query)
        print(f"Bot: {response[:80]}...\n")
    
    # View stats
    stats = chatbot.get_conversation_stats()
    print(f"📊 Conversation Stats:")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Assistant: {stats['assistant_name']}")
    
    # Export
    print("\n💾 Export conversation:")
    print("  chatbot.orchestrator.export_conversation('conversation.json')")


# ======================== Example 8: Custom RAG Config ========================

def example_custom_rag_config():
    """Example 8: RAG with custom configuration"""
    print("="*60)
    print("Example 8: Custom RAG Configuration")
    print("="*60)
    
    from Backend.RAGSystem import LocalRAGSystem, RAGConfig
    
    # High accuracy configuration
    config = RAGConfig(
        chunk_size=1000,           # Larger chunks
        chunk_overlap=200,         # More overlap
        temperature=0.2,           # More deterministic
        max_tokens=2048,           # Longer answers
        search_kwargs={"k": 5}     # More context
    )
    
    print("🔧 High-Accuracy RAG Configuration:")
    print(f"  Chunk Size: {config.chunk_size}")
    print(f"  Chunk Overlap: {config.chunk_overlap}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Max Tokens: {config.max_tokens}")
    print(f"  Search K: {config.search_kwargs['k']}")
    
    # Real-time configuration
    fast_config = RAGConfig(
        chunk_size=300,
        chunk_overlap=50,
        temperature=0.7,
        max_tokens=512,
        search_kwargs={"k": 2}
    )
    
    print("\n⚡ Fast/Real-Time RAG Configuration:")
    print(f"  Chunk Size: {fast_config.chunk_size}")
    print(f"  Chunk Overlap: {fast_config.chunk_overlap}")
    print(f"  Temperature: {fast_config.temperature}")
    print(f"  Max Tokens: {fast_config.max_tokens}")
    print(f"  Search K: {fast_config.search_kwargs['k']}")
    
    # Usage
    print("\n💻 Usage:")
    print("  rag = LocalRAGSystem(config=config)")


# ======================== Example 9: Error Handling ========================

def example_error_handling():
    """Example 9: Proper error handling"""
    print("="*60)
    print("Example 9: Error Handling")
    print("="*60)
    
    from Backend.OrchestratorAgent import create_orchestrator
    
    orchestrator = create_orchestrator()
    
    # Handle errors gracefully
    try:
        response = orchestrator.process_query("What should I do?")
        if response.confidence < 0.5:
            print(f"⚠️  Low confidence response: {response.confidence:.2f}")
            print("Consider reformulating the query")
        
        if response.has_hallucination_risk:
            print("⚠️  This response may contain inaccurate information")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Always check:")
    print("  - response.confidence (0.0-1.0)")
    print("  - response.has_hallucination_risk (bool)")
    print("  - response.used_rag (bool)")
    print("  - response.used_tools (list)")


# ======================== Example 10: Performance Monitoring ========================

def example_performance_monitoring():
    """Example 10: Monitor system performance"""
    print("="*60)
    print("Example 10: Performance Monitoring")
    print("="*60)
    
    from Backend.OrchestratorAgent import create_orchestrator
    import time
    
    orchestrator = create_orchestrator()
    
    # Performance test
    queries = [
        "What is AI?",
        "Explain machine learning",
        "Tell me about neural networks"
    ]
    
    print("⏱️  Performance Test:\n")
    
    total_time = 0
    for query in queries:
        start = time.time()
        response = orchestrator.process_query(query)
        elapsed = time.time() - start
        total_time += elapsed
        
        print(f"Query: {query}")
        print(f"  Time: {elapsed:.3f}s | Confidence: {response.confidence:.2f}")
    
    avg_time = total_time / len(queries)
    print(f"\n📊 Average time per query: {avg_time:.3f}s")
    
    if avg_time < 2.0:
        print("✅ Performance is excellent!")
    elif avg_time < 5.0:
        print("⚠️  Performance is acceptable")
    else:
        print("❌ Performance needs optimization")


# ======================== Main Menu ========================

async def main():
    """Run example menu"""
    examples = [
        ("Basic Chat", example_basic_chat),
        ("RAG System", example_rag_system),
        ("Agent Tools", example_agent_tools),
        ("Intelligent Routing", example_intelligent_routing),
        ("Streaming Responses", example_streaming),
        ("Document Upload", example_document_upload),
        ("Conversation History", example_conversation_history),
        ("Custom RAG Config", example_custom_rag_config),
        ("Error Handling", example_error_handling),
        ("Performance Monitoring", example_performance_monitoring),
        ("Run All Examples", None),
        ("Exit", None),
    ]
    
    print("\n" + "="*60)
    print("🎯 LangChain Agentic RAG System - Quick Start Examples")
    print("="*60)
    print()
    
    while True:
        print("\nSelect an example to run:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        
        try:
            choice = input("\nEnter choice (1-12): ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx < 0 or choice_idx >= len(examples):
                print("Invalid choice. Please try again.")
                continue
            
            name, func = examples[choice_idx]
            
            if name == "Exit":
                print("👋 Goodbye!")
                break
            
            if name == "Run All Examples":
                for i, (ex_name, ex_func) in enumerate(examples[:-2], 1):
                    if ex_func:
                        print(f"\n\n{'#'*60}")
                        print(f"Running Example {i}/{10}: {ex_name}")
                        print(f"{'#'*60}\n")
                        
                        if ex_name == "Streaming Responses":
                            await ex_func()
                        else:
                            ex_func()
                        
                        input("Press Enter to continue...")
            else:
                if name == "Streaming Responses":
                    await func()
                else:
                    func()
                
                input("\nPress Enter to continue...")
        
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
