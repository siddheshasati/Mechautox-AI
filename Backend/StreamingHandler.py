import asyncio
import logging
from typing import AsyncIterator, Optional, Callable, Any
from functools import partial

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamConfig(BaseModel):
    """Configuration for streaming responses"""
    chunk_size: int = Field(default=10, description="Characters per chunk for UI updates")
    timeout: float = Field(default=30.0, description="Timeout for streaming in seconds")
    buffer_size: int = Field(default=1024, description="Buffer size for streaming")
    enable_logging: bool = Field(default=True, description="Enable detailed logging")


class StreamingChunk(BaseModel):
    """Structured streaming response chunk"""
    token: str
    chunk_index: int
    is_final: bool = False
    elapsed_time: float = 0.0


class AsyncStreamingHandler:

    def __init__(self, llm: ChatGroq, config: Optional[StreamConfig] = None):
        """
        Initialize streaming handler.
        
        Args:
            llm: ChatGroq language model instance
            config: Streaming configuration
        """
        self.llm = llm
        self.config = config or StreamConfig()
        self.parser = StrOutputParser()
        
        logger.info("✅ AsyncStreamingHandler initialized")

    async def stream_response(
        self,
        messages: list[BaseMessage],
        system_prompt: Optional[str] = None,
        on_chunk: Optional[Callable[[StreamingChunk], None]] = None,
    ) -> AsyncIterator[StreamingChunk]:
        """
        Stream response from LLM with LCEL.
        Args:
            messages: List of message objects
            system_prompt: Optional system prompt to prepend
            on_chunk: Optional callback for each chunk (for UI updates)
        Yields:
            StreamingChunk objects with tokens
        """
        if system_prompt:
            messages = [SystemMessage(content=system_prompt)] + messages

        try:
            # Build LCEL chain: LLM -> StrOutputParser
            chain = self.llm | self.parser

            chunk_index = 0
            accumulated = ""

            try:
                # Stream tokens directly using astream
                async for token in chain.astream(messages):
                    if token:
                        accumulated += token
                        # Yield chunk when buffer is filled
                        if len(accumulated) >= self.config.chunk_size:
                            chunk = StreamingChunk(
                                token=accumulated,
                                chunk_index=chunk_index,
                                is_final=False
                            )
                            chunk_index += 1

                            if on_chunk:
                                on_chunk(chunk)
                            yield chunk
                            accumulated = ""

                if accumulated:
                    chunk = StreamingChunk(
                        token=accumulated,
                        chunk_index=chunk_index,
                        is_final=True
                    )
                    if on_chunk:
                        on_chunk(chunk)
                    yield chunk

            except asyncio.TimeoutError:
                logger.error(" Streaming timeout")
                yield StreamingChunk(
                    token="[Response timed out]",
                    chunk_index=chunk_index,
                    is_final=True
                )

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield StreamingChunk(
                token=f"[Error: {str(e)}]",
                chunk_index=-1,
                is_final=True
            )

    async def stream_lcel_chain(
        self,
        chain,
        input_data: dict,
        on_chunk: Optional[Callable[[StreamingChunk], None]] = None,
    ) -> AsyncIterator[StreamingChunk]:
        """
        Stream from a custom LCEL chain with streaming callback.
        Args:
            chain: LCEL chain (e.g., prompt | llm | parser)
            input_data: Input dictionary for the chain
            on_chunk: Optional callback for each chunk
        Yields:
            StreamingChunk objects
        """
        try:
            chunk_index = 0
            accumulated = ""

            try:
                async for token in chain.astream(input_data):
                    if token:
                        accumulated += token
                        if len(accumulated) >= self.config.chunk_size:
                            chunk = StreamingChunk(
                                token=accumulated,
                                chunk_index=chunk_index,
                                is_final=False
                            )
                            chunk_index += 1
                            if on_chunk:
                                on_chunk(chunk)
                            yield chunk
                            accumulated = ""

                if accumulated:
                    chunk = StreamingChunk(
                        token=accumulated,
                        chunk_index=chunk_index,
                        is_final=True
                    )
                    if on_chunk:
                        on_chunk(chunk)
                    yield chunk

            except asyncio.TimeoutError:
                logger.error("⏱️ Chain streaming timeout")
                yield StreamingChunk(
                    token="[Chain execution timed out]",
                    chunk_index=chunk_index,
                    is_final=True
                )

        except Exception as e:
            logger.error(f"Chain streaming error: {e}")
            yield StreamingChunk(
                token=f"[Error: {str(e)}]",
                chunk_index=-1,
                is_final=True
            )

    async def collect_full_response(
        self,
        stream_iterator: AsyncIterator[StreamingChunk],
    ) -> str:
        """
        Collect all chunks from stream into full response.
        Args:
            stream_iterator: Async iterator of StreamingChunk objects
        Returns:
            Complete concatenated response
        """
        full_response = ""
        try:
            async for chunk in stream_iterator:
                full_response += chunk.token
                if self.config.enable_logging:
                    logger.debug(f"Chunk {chunk.chunk_index}: {chunk.token[:30]}...")
        except Exception as e:
            logger.error(f" Error collecting response: {e}")
        return full_response

    async def stream_with_timeout(
        self,
        stream_coro,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[StreamingChunk]:
        """
        Stream with configurable timeout.
        Args:
            stream_coro: Coroutine that yields StreamingChunk objects
            timeout: Timeout in seconds (defaults to config.timeout)
        Yields:
            StreamingChunk objects until timeout or completion
        """
        timeout = timeout or self.config.timeout
        try:
            async with asyncio.timeout(timeout):
                async for chunk in stream_coro:
                    yield chunk
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Streaming timed out after {timeout}s")
            yield StreamingChunk(
                token="[Response timed out - partial result above]",
                chunk_index=-1,
                is_final=True
            )


class StreamingUIAdapter:
    """
    Adapter to integrate streaming with PyQt5 UI.
    Handles signal emission and thread-safe updates.
    """

    def __init__(self, update_signal: Optional[Callable[[str], None]] = None):
        """
        Initialize UI adapter.
        Args:
            update_signal: PyQt5 signal for UI updates (e.g., textEdit.append)
        """
        self.update_signal = update_signal
        self.accumulated = ""

    def on_chunk_received(self, chunk: StreamingChunk) -> None:
        """
        Callback when chunk is received. Updates UI if signal available.
        Args:
            chunk: Streaming chunk
        """
        self.accumulated += chunk.token
        if self.update_signal:
            try:
                # For PyQt5, emit signal with accumulated text
                self.update_signal(chunk.token)
            except Exception as e:
                logger.error(f"UI update error: {e}")

    def get_full_response(self) -> str:
        """Get accumulated response"""
        return self.accumulated

    def reset(self) -> None:
        """Reset for new response"""
        self.accumulated = ""


async def pyqt5_streaming_example(
    llm: ChatGroq,
    query: str,
    on_update: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Example function for integrating with PyQt5.

    Args:
        llm: ChatGroq instance
        query: User query
        on_update: PyQt5 signal or callback for text updates
    Returns:
        Complete response
    """
    handler = AsyncStreamingHandler(llm)
    ui_adapter = StreamingUIAdapter(update_signal=on_update)

    # Create message
    messages = [HumanMessage(content=query)]

    # Stream response
    full_response = ""
    async for chunk in handler.stream_response(
        messages=messages,
        on_chunk=ui_adapter.on_chunk_received,
    ):
        full_response += chunk.token

    return full_response


if __name__ == "__main__":
    import os
    from dotenv import dotenv_values

    async def test_streaming():
        # Load Groq API key
        env = dotenv_values(".env")
        api_key = env.get("GroqAPIKey")

        if not api_key:
            logger.error("Groq API key not found in .env")
            return

        # Initialize LLM
        llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=api_key,
        )

        # Create handler
        handler = AsyncStreamingHandler(llm)

        # Test streaming
        messages = [HumanMessage(content="Explain quantum computing in 100 words")]

        logger.info("🚀 Starting streaming test...")
        full_response = await handler.collect_full_response(
            handler.stream_response(messages)
        )

        logger.info(f"Complete response:\n{full_response}")

    # Run test
    asyncio.run(test_streaming())
