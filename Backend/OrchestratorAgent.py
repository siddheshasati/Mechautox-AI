import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from dotenv import dotenv_values
from pydantic import BaseModel, Field

try:
    from .RAGSystem import LocalRAGSystem, RAGResponse
    from .AgentTools import get_agent_tools
    from .StreamingHandler import AsyncStreamingHandler, StreamingChunk
except ImportError:
    from RAGSystem import LocalRAGSystem, RAGResponse
    from AgentTools import get_agent_tools
    from StreamingHandler import AsyncStreamingHandler, StreamingChunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)



class OrchestratorConfig(BaseModel):
    """Configuration for the Agentic Orchestrator"""
    model_name: str = Field(default="llama-3.3-70b-versatile", description="Groq model name")
    temperature: float = Field(default=0.3, description="LLM temperature")
    max_tokens: int = Field(default=2048, description="Max response tokens")
    max_iterations: int = Field(default=10, description="Max agent iterations")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    enable_rag: bool = Field(default=True, description="Enable RAG system")
    enable_tools: bool = Field(default=True, description="Enable agent tools")
    enable_streaming: bool = Field(default=True, description="Enable streaming responses")


class AgentResponse(BaseModel):
    """Structured agent response"""
    response: str
    used_rag: bool = False
    used_tools: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgenticOrchestrator:

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        groq_api_key: Optional[str] = None,
    ):

        self.config = config or OrchestratorConfig()
        env_path = Path(__file__).parent.parent / ".env"
        self.api_key = groq_api_key or os.getenv("GroqAPIKey") or dotenv_values(env_path).get("GroqAPIKey", "")

        if not self.api_key:
            logger.warning("Groq API key not found")

        # Initialize LLM
        self.llm = ChatGroq(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.api_key,
        )

        # Initialize RAG system
        self.rag_system = None
        if self.config.enable_rag:
            try:
                self.rag_system = LocalRAGSystem(groq_api_key=self.api_key)
                logger.info("RAG system initialized")
            except Exception as e:
                logger.warning(f"RAG initialization failed: {e}")

        # Initialize agent tools
        self.tools = []
        if self.config.enable_tools:
            self.tools = get_agent_tools()
            logger.info(f"Loaded {len(self.tools)} agent tools")

        # Initialize streaming handler
        self.streaming_handler = None
        if self.config.enable_streaming:
            self.streaming_handler = AsyncStreamingHandler(self.llm)
            logger.info("Streaming handler initialized")

        # Initialize agent executor
        self.agent_executor = self._create_agent_executor()

        # Conversation history
        self.conversation_history = []

        logger.info("AgenticOrchestrator ready")

    def _create_agent_executor(self) -> Optional[object]:

        if not self.tools:
            logger.warning("No tools available. Agent will use reasoning only.")
            return None

        logger.warning("Agent executor creation skipped for compatibility with installed langchain. Tools will be unavailable via agent executor.")
        return None

    def _should_use_rag(self, query: str) -> bool:
        """
        Determine if RAG should be used for this query.

        Args:
            query: User query
        Returns:
            True if RAG should be queried
        """
        rag_keywords = [
            "document", "pdf", "file", "knowledge", "base", "private", "search my files",
            "what do i have", "find in", "based on", "from the", "uploaded", "my data"
        ]
        return any(keyword in query.lower() for keyword in rag_keywords)

    def _should_use_tools(self, query: str) -> bool:
        """
        Determine if tools should be used for this query.
        Args:
            query: User query
        Returns:
            True if tools should be invoked
        """
        tool_keywords = [
            "open", "close", "search", "whatsapp", "message", "volume", "brightness",
            "play", "youtube", "web", "google", "read file", "list files", "send"
        ]
        return any(keyword in query.lower() for keyword in tool_keywords)

    def process_query(self, query: str) -> AgentResponse:
        """
        Process user query with intelligent routing.
        Args:
            query: User query
        Returns:
            AgentResponse with result
        """
        start_time = datetime.now()
        rag_used = False
        tools_used = []
        metadata = {}

        logger.info(f"Processing query: {query}")

        try:
            if self.config.enable_rag and self._should_use_rag(query):
                logger.info("Routing to RAG system")
                rag_response = self.rag_system.query(query)
                rag_used = True
                metadata["rag_confidence"] = rag_response.confidence
                metadata["rag_sources"] = [s.document_name for s in rag_response.sources]
                response = rag_response.answer

            elif self.config.enable_tools and self._should_use_tools(query):
                logger.info("🔧 Routing to agent executor")
                if self.agent_executor:
                    input_data = {
                        "input": query,
                        "chat_history": self.conversation_history,
                        "agent_scratchpad": "",
                        "current_time": datetime.now().isoformat(),
                    }
                    result = self.agent_executor.invoke(input_data)
                    response = result.get("output", "Action completed")
                    tools_used = self._extract_tool_names(query)
                else:
                    response = "Tool execution unavailable"
            else:
                logger.info("Using pure LLM reasoning")
                messages = [
                    SystemMessage(content=self._get_system_prompt()),
                    HumanMessage(content=query),
                ]
                result = self.llm.invoke(messages)
                response = result.content

            self.conversation_history.append(HumanMessage(content=query))
            self.conversation_history.append(AIMessage(content=response))

            # Keep last 50 messages
            if len(self.conversation_history) > 100:
                self.conversation_history = self.conversation_history[-100:]

            execution_time = (datetime.now() - start_time).total_seconds()

            agent_response = AgentResponse(
                response=response,
                used_rag=rag_used,
                used_tools=tools_used,
                confidence=0.9 if rag_used else 0.8,
                execution_time=execution_time,
                metadata=metadata,
            )

            logger.info(f"Query processed in {execution_time:.2f}s")
            return agent_response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return AgentResponse(
                response=f"Error: {str(e)}",
                confidence=0.0,
                execution_time=execution_time,
            )

    def _get_system_prompt(self) -> str:
        """Get system prompt for pure LLM reasoning"""
        return """You are a helpful, accurate, and intelligent AI assistant.
        Guidelines:
        - Provide clear, concise answers
        - Use structured formatting when appropriate
        - Admit uncertainty when you're not sure
        - Offer follow-up suggestions when relevant
        Current time: {}""".format(datetime.now().isoformat())

    def _extract_tool_names(self, query: str) -> List[str]:
        """Extract tool names that might be used for a query"""
        tool_map = {
            "whatsapp": "send_whatsapp",
            "search": "web_search",
            "open": "open_app",
            "close": "close_app",
            "youtube": "youtube",
            "volume": "volume_control",
            "brightness": "brightness_control",
            "pdf": "read_pdf",
            "file": "list_files",
        }

        tools_used = []
        for keyword, tool_name in tool_map.items():
            if keyword in query.lower():
                tools_used.append(tool_name)
        return tools_used

    def add_rag_documents(self, documents, doc_name: str) -> Dict:
        """
        Add documents to RAG system.
        Args:
            documents: List of Document objects
            doc_name: Document name for tracking
        Returns:
            Status dictionary
        """
        if not self.rag_system:
            return {"status": "error", "message": "RAG system not available"}

        return self.rag_system.add_documents(documents, doc_name)

    def get_rag_stats(self) -> Dict:
        """Get RAG system statistics"""
        if not self.rag_system:
            return {"status": "unavailable"}
        return self.rag_system.get_db_stats()

    def clear_conversation_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🗑️  Conversation history cleared")

    def export_conversation(self, file_path: str) -> bool:
        """
        Export conversation to JSON file.
        Args:
            file_path: Path to save conversation
        Returns:
            True if successful
        """
        try:
            import json
            conversation_data = [
                {
                    "role": msg.type,
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                }
                for msg in self.conversation_history
            ]
            with open(file_path, "w") as f:
                json.dump(conversation_data, f, indent=4)
            logger.info(f"Conversation exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False


def create_orchestrator(
    enable_rag: bool = True,
    enable_tools: bool = True,
    enable_streaming: bool = True,
) -> AgenticOrchestrator:
    """
    Factory function to create orchestrator with custom settings.
    Args:
        enable_rag: Enable RAG system
        enable_tools: Enable agent tools
        enable_streaming: Enable streaming responses
    Returns:
        Configured AgenticOrchestrator instance
    """
    config = OrchestratorConfig(
        enable_rag=enable_rag,
        enable_tools=enable_tools,
        enable_streaming=enable_streaming,
        verbose=True,
    )
    return AgenticOrchestrator(config=config)


if __name__ == "__main__":
    orchestrator = create_orchestrator()

    # Test queries
    test_queries = [
        "What is the capital of France?", #GK
        "Search for machine learning tutorials on YouTube",  # Tools
        "What documents do I have in my knowledge base?",  # RAG
    ]

    for query in test_queries:
        logger.info(f"\n Query: {query}")
        response = orchestrator.process_query(query)
        print(f"Response: {response.response}")
        print(f"Used RAG: {response.used_rag}")
        print(f"Tools: {response.used_tools}")
        print(f"Execution time: {response.execution_time:.2f}s\n")
