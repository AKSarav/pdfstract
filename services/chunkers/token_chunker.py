"""
TokenChunker - Splits text into fixed-size token chunks with configurable overlap.

Best for: Maintaining consistent chunk sizes and working with token-based models.
"""

import asyncio
from typing import List, Dict, Any, Optional
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie
try:
    from chonkie import TokenChunker as ChonkieTokenChunker
    CHONKIE_AVAILABLE = True
except ImportError:
    CHONKIE_AVAILABLE = False
    ChonkieTokenChunker = None


class TokenChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's TokenChunker.
    
    Splits text into chunks based on token count, ensuring each chunk 
    stays within specified token limits.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "token"
    
    @property
    def available(self) -> bool:
        return CHONKIE_AVAILABLE
    
    @property
    def description(self) -> str:
        return "Split text into fixed-size token chunks with configurable overlap"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "tokenizer": {
                "type": "string",
                "default": "character",
                "description": "Tokenizer to use (character, word, byte, gpt2, or custom)",
                "enum": ["character", "word", "byte", "gpt2"]
            },
            "chunk_size": {
                "type": "integer",
                "default": 2048,
                "description": "Maximum number of tokens per chunk",
                "minimum": 1
            },
            "chunk_overlap": {
                "type": "integer",
                "default": 0,
                "description": "Number of overlapping tokens between chunks",
                "minimum": 0
            }
        }
    
    def _get_chunker(self, tokenizer: str, chunk_size: int, chunk_overlap: int):
        """Get or create a cached chunker instance"""
        cache_key = f"{tokenizer}_{chunk_size}_{chunk_overlap}"
        
        if cache_key not in self._chunker_cache:
            self._chunker_cache[cache_key] = ChonkieTokenChunker(
                tokenizer=tokenizer,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        
        return self._chunker_cache[cache_key]
    
    def _chunk_sync(self, text: str, tokenizer: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = self._get_chunker(tokenizer, chunk_size, chunk_overlap)
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "token"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using TokenChunker.
        
        Args:
            text: The text to chunk
            tokenizer: Tokenizer to use (default: "character")
            chunk_size: Maximum tokens per chunk (default: 2048)
            chunk_overlap: Overlapping tokens between chunks (default: 0)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError("TokenChunker is not available. Install chonkie: pip install chonkie")
        
        validated = self.validate_params(params)
        tokenizer = validated.get("tokenizer", "character")
        chunk_size = validated.get("chunk_size", 2048)
        chunk_overlap = validated.get("chunk_overlap", 0)
        
        logger.info(f"TokenChunker: chunking text with size={chunk_size}, overlap={chunk_overlap}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync, text, tokenizer, chunk_size, chunk_overlap
        )
        
        logger.info(f"TokenChunker: created {len(chunks)} chunks")
        return chunks
