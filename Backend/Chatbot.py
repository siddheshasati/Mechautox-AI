"""
Chatbot using LangChain Agentic Orchestrator
- Seamless integration with RAG for document queries
- Streaming responses for sub-second UI latency
- Auto-routing to tools for automation tasks
- Full conversation history management
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import dotenv_values, set_key
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

try:
    from .OrchestratorAgent import AgenticOrchestrator, create_orchestrator
    from .StreamingHandler import AsyncStreamingHandler
except ImportError:
    from OrchestratorAgent import AgenticOrchestrator, create_orchestrator
    from StreamingHandler import AsyncStreamingHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
env_vars = dotenv_values(env_path)
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "MechautoX")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

if "Assistantname" not in env_vars or env_vars.get("Assistantname") != "MechautoX":
    set_key(str(env_path), "Assistantname", "MechautoX")
    logger.info("Updated Assistantname to: MechautoX")

if not GroqAPIKey:
    logger.error("Groq API key not found in .env file.")
    exit(1)

CHAT_LOG_PATH = Path("Data/ChatLog.json")
CHAT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

class EnhancedChatbot:
    """
    LangChain-based chatbot with RAG, Tools, and Streaming.
    Replaces the old Groq-only implementation with full agentic capabilities.
    """

    def __init__(self):
        """Initialize enhanced chatbot with orchestrator"""
        self.orchestrator = create_orchestrator(
            enable_rag=True,
            enable_tools=True,
            enable_streaming=True,
        )

        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
            api_key=GroqAPIKey,
        )

        self.system_prompt = self._build_system_prompt()
        self.chat_history = self._load_chat_history()
        logger.info(f"🤖 {Assistantname} initialized and ready")

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        return f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}.

CORE BEHAVIORS:
*** Do not tell time unless asked.***
*** Give useful, informative answers without padding. For simple questions, use 4-8 clear lines. For research, learning, planning, debugging, coding, or problem-solving questions, give a fuller structured answer with steps, examples, or reasoning as needed. ***
*** Do not add unnecessary notes or disclaimers. ***
*** When giving code, return the code in fenced Markdown blocks with the correct language name, proper indentation, and only a short setup line if needed. ***

SPECIAL CAPABILITIES:
- You have access to a private knowledge base for document queries
- You can automate tasks like opening applications, sending WhatsApp messages, searching the web
- You can read PDF files and manage files
- Always acknowledge which capability you're using

Response Guidelines:
- Be concise and direct
- Use markdown for formatting when appropriate
- Cite sources when using knowledge base
- Explain actions taken with tools"""

    def _load_chat_history(self) -> list:
        """Load previous chat history"""
        try:
            if CHAT_LOG_PATH.exists():
                with open(CHAT_LOG_PATH, "r") as f:
                    return json.load(f)[-50:]  # Keep last 50 messages
        except Exception as e:
            logger.warning(f"Could not load chat history: {e}")
        return []

    def _save_chat_history(self) -> None:
        """Save chat history to file"""
        try:
            with open(CHAT_LOG_PATH, "w") as f:
                json.dump(self.chat_history[-50:], f, indent=4)
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")

    def _get_realtime_info(self) -> str:
        """Get current date and time"""
        now = datetime.now()
        return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}."

    def chat(self, query: str) -> str:

        try:
            if any(kw in query.lower() for kw in ["time", "date", "day", "current"]):
                query_with_time = f"{query}\n\nCurrent context: {self._get_realtime_info()}"
            else:
                query_with_time = query

            # Process through orchestrator
            response = self.orchestrator.process_query(query_with_time)
            answer = response.response


            self.chat_history.append({"role": "user", "content": query, "timestamp": datetime.now().isoformat()})
            self.chat_history.append({"role": "assistant", "content": answer, "timestamp": datetime.now().isoformat()})

            self._save_chat_history()

            logger.info(f"Response generated. RAG used: {response.used_rag}, Tools: {response.used_tools}")
            return answer

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"An error occurred: {str(e)}"

    async def stream_chat(self, query: str, on_update=None):
        """
        Stream response for real-time UI updates.
        Args:
            query: User query
            on_update: Callback function for streaming chunks
        Yields:
            Streaming chunks
        """
        try:
            handler = AsyncStreamingHandler(self.llm)
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=query),
            ]

            full_response = ""
            async for chunk in handler.stream_response(messages, on_chunk=on_update):
                full_response += chunk.token
                yield chunk.token

            self.chat_history.append({"role": "user", "content": query, "timestamp": datetime.now().isoformat()})
            self.chat_history.append({"role": "assistant", "content": full_response, "timestamp": datetime.now().isoformat()})
            self._save_chat_history()

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            yield f"Error: {str(e)}"

    def get_conversation_stats(self) -> dict:
        """Get conversation statistics"""
        return {
            "total_messages": len(self.chat_history),
            "rag_stats": self.orchestrator.get_rag_stats(),
            "assistant_name": Assistantname,
            "username": Username,
        }


def ChatBot(Query: str) -> str:
    """
    Backward compatible ChatBot function.
    Maps to EnhancedChatbot for seamless migration.
    """
    chatbot = EnhancedChatbot()
    return chatbot.chat(Query)


if __name__ == "__main__":
    # Initialize chatbot
    chatbot = EnhancedChatbot()

    logger.info(f"Starting {Assistantname} chatbot. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(f"\n{Username}: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                logger.info("Goodbye!")
                break

            print(f"\n{Assistantname}: ", end="", flush=True)
            response = chatbot.chat(user_input)
            print(response)

            response_obj = chatbot.orchestrator.process_query(user_input)
            if response_obj.used_rag or response_obj.used_tools:
                print(f"\n[Execution time: {response_obj.execution_time:.2f}s, RAG: {response_obj.used_rag}, Tools: {', '.join(response_obj.used_tools) or 'None'}]")

        except KeyboardInterrupt:
            logger.info("Chat interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
