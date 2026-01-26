"""
SlumberChunker - AI-powered agentic chunking using LLM genies.

Best for: Intelligent chunking using LLM reasoning for optimal split points.
Requires: chonkie[genie] - pip install chonkie[genie]
Note: Requires API keys (e.g., GOOGLE_API_KEY for Gemini, OPENAI_API_KEY for OpenAI)
"""

import asyncio
from typing import List, Dict, Any, Optional
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie slumber chunker and genies
CHONKIE_SLUMBER_AVAILABLE = False
ChonkieSlumberChunker = None
GeminiGenie = None
OpenAIGenie = None

try:
    from chonkie import SlumberChunker as ChonkieSlumberChunker
    CHONKIE_SLUMBER_AVAILABLE = True
    
    # Try to import genies
    try:
        from chonkie.genie import GeminiGenie
    except ImportError:
        GeminiGenie = None
    
    try:
        from chonkie.genie import OpenAIGenie
    except ImportError:
        OpenAIGenie = None
        
except ImportError:
    pass


class SlumberChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's SlumberChunker.
    
    Uses LLM-based "genies" for intelligent, agentic chunking decisions.
    The LLM analyzes text structure and identifies optimal split points.
    
    Note: Requires API keys set as environment variables:
    - GOOGLE_API_KEY for Gemini genie
    - OPENAI_API_KEY for OpenAI genie
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "slumber"
    
    @property
    def available(self) -> bool:
        return CHONKIE_SLUMBER_AVAILABLE and (GeminiGenie is not None or OpenAIGenie is not None)
    
    @property
    def error_message(self) -> Optional[str]:
        if not CHONKIE_SLUMBER_AVAILABLE:
            return "SlumberChunker requires: pip install chonkie[genie]"
        if GeminiGenie is None and OpenAIGenie is None:
            return "No genie providers available. Install chonkie[genie] and set API keys."
        return None
    
    @property
    def description(self) -> str:
        return "AI-powered agentic chunking using LLM reasoning (requires API key)"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "genie_provider": {
                "type": "string",
                "default": "gemini",
                "description": "LLM provider to use for chunking decisions",
                "enum": ["gemini", "openai"]
            },
            "tokenizer": {
                "type": "string",
                "default": "character",
                "description": "Tokenizer to use for counting",
                "enum": ["character", "word", "gpt2"]
            },
            "chunk_size": {
                "type": "integer",
                "default": 1024,
                "description": "Target maximum tokens per chunk",
                "minimum": 1
            },
            "candidate_size": {
                "type": "integer",
                "default": 128,
                "description": "Tokens around split point for LLM to examine",
                "minimum": 1
            },
            "min_characters_per_chunk": {
                "type": "integer",
                "default": 24,
                "description": "Minimum characters per chunk",
                "minimum": 1
            }
        }
    
    def _create_genie(self, provider: str):
        """Create a genie instance based on provider"""
        if provider == "gemini" and GeminiGenie is not None:
            return GeminiGenie("gemini-2.0-flash")
        elif provider == "openai" and OpenAIGenie is not None:
            return OpenAIGenie("gpt-4o-mini")
        elif GeminiGenie is not None:
            return GeminiGenie("gemini-2.0-flash")
        elif OpenAIGenie is not None:
            return OpenAIGenie("gpt-4o-mini")
        else:
            raise RuntimeError("No genie provider available. Set GOOGLE_API_KEY or OPENAI_API_KEY.")
    
    def _chunk_sync(
        self, 
        text: str, 
        genie_provider: str,
        tokenizer: str,
        chunk_size: int,
        candidate_size: int,
        min_characters_per_chunk: int
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        genie = self._create_genie(genie_provider)
        
        chunker = ChonkieSlumberChunker(
            genie=genie,
            tokenizer=tokenizer,
            chunk_size=chunk_size,
            candidate_size=candidate_size,
            min_characters_per_chunk=min_characters_per_chunk,
            verbose=False
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count if hasattr(c, 'token_count') else 0,
                metadata={"chunker": "slumber", "genie_provider": genie_provider}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using SlumberChunker (agentic LLM-powered chunking).
        
        Args:
            text: The text to chunk
            genie_provider: LLM provider - gemini or openai (default: gemini)
            tokenizer: Tokenizer for counting (default: character)
            chunk_size: Target max tokens per chunk (default: 1024)
            candidate_size: Tokens for LLM to examine (default: 128)
            min_characters_per_chunk: Minimum chars per chunk (default: 24)
            
        Returns:
            List of Chunk objects
            
        Note:
            Requires API keys as environment variables:
            - GOOGLE_API_KEY for gemini
            - OPENAI_API_KEY for openai
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        genie_provider = validated.get("genie_provider", "gemini")
        tokenizer = validated.get("tokenizer", "character")
        chunk_size = validated.get("chunk_size", 1024)
        candidate_size = validated.get("candidate_size", 128)
        min_characters_per_chunk = validated.get("min_characters_per_chunk", 24)
        
        logger.info(f"SlumberChunker: chunking with {genie_provider} genie")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            genie_provider,
            tokenizer,
            chunk_size,
            candidate_size,
            min_characters_per_chunk
        )
        
        logger.info(f"SlumberChunker: created {len(chunks)} chunks")
        return chunks
