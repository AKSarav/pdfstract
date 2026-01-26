"""
LateChunker - Late interaction chunking for ColBERT-style retrieval.

Best for: Creating chunks optimized for late interaction retrieval models.
Requires: chonkie[st] - pip install chonkie[st]
"""

import asyncio
from typing import List, Dict, Any
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie late chunker
try:
    from chonkie import LateChunker as ChonkieLateChunker
    from chonkie import RecursiveRules
    CHONKIE_LATE_AVAILABLE = True
except ImportError:
    CHONKIE_LATE_AVAILABLE = False
    ChonkieLateChunker = None
    RecursiveRules = None


class LateChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's LateChunker.
    
    Creates chunks optimized for late interaction retrieval models like ColBERT.
    Preserves token-level embeddings for fine-grained similarity matching.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "late"
    
    @property
    def available(self) -> bool:
        return CHONKIE_LATE_AVAILABLE
    
    @property
    def error_message(self) -> str:
        if self.available:
            return None
        return "LateChunker requires extra dependencies. Install with: pip install chonkie[st]"
    
    @property
    def description(self) -> str:
        return "Chunk text for late interaction retrieval (ColBERT-style)"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "embedding_model": {
                "type": "string",
                "default": "nomic-ai/modernbert-embed-base",
                "description": "Embedding model for late interaction"
            },
            "chunk_size": {
                "type": "integer",
                "default": 2048,
                "description": "Maximum number of tokens per chunk",
                "minimum": 1
            },
            "min_characters_per_chunk": {
                "type": "integer",
                "default": 24,
                "description": "Minimum characters per chunk",
                "minimum": 1
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        embedding_model: str,
        chunk_size: int,
        min_characters_per_chunk: int
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = ChonkieLateChunker(
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            rules=RecursiveRules(),
            min_characters_per_chunk=min_characters_per_chunk
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "late"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using LateChunker.
        
        Args:
            text: The text to chunk
            embedding_model: Model for late interaction (default: nomic-ai/modernbert-embed-base)
            chunk_size: Maximum tokens per chunk (default: 2048)
            min_characters_per_chunk: Minimum chars per chunk (default: 24)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        embedding_model = validated.get("embedding_model", "nomic-ai/modernbert-embed-base")
        chunk_size = validated.get("chunk_size", 2048)
        min_characters_per_chunk = validated.get("min_characters_per_chunk", 24)
        
        logger.info(f"LateChunker: chunking with model={embedding_model}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            embedding_model,
            chunk_size,
            min_characters_per_chunk
        )
        
        logger.info(f"LateChunker: created {len(chunks)} chunks")
        return chunks
