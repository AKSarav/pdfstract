"""
SemanticChunker - Chunks text based on semantic similarity.

Best for: Creating contextually meaningful chunks using embeddings.
Requires: chonkie[semantic] - pip install chonkie[semantic]
"""

import asyncio
from typing import List, Dict, Any
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie semantic chunker
try:
    from chonkie import SemanticChunker as ChonkieSemanticChunker
    CHONKIE_SEMANTIC_AVAILABLE = True
except ImportError:
    CHONKIE_SEMANTIC_AVAILABLE = False
    ChonkieSemanticChunker = None


class SemanticChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's SemanticChunker.
    
    Groups sentences based on semantic similarity using embeddings.
    Produces contextually coherent chunks by finding natural break points.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "semantic"
    
    @property
    def available(self) -> bool:
        return CHONKIE_SEMANTIC_AVAILABLE
    
    @property
    def error_message(self) -> str:
        if self.available:
            return None
        return "SemanticChunker requires extra dependencies. Install with: pip install chonkie[semantic]"
    
    @property
    def description(self) -> str:
        return "Chunk text based on semantic similarity using embeddings"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "embedding_model": {
                "type": "string",
                "default": "minishlab/potion-base-32M",
                "description": "Embedding model to use for similarity calculation"
            },
            "chunk_size": {
                "type": "integer",
                "default": 2048,
                "description": "Maximum number of tokens per chunk",
                "minimum": 1
            },
            "threshold": {
                "type": "number",
                "default": 0.8,
                "description": "Similarity threshold (0-1) for grouping sentences",
                "minimum": 0,
                "maximum": 1
            },
            "similarity_window": {
                "type": "integer",
                "default": 3,
                "description": "Window size for similarity calculation",
                "minimum": 1
            },
            "skip_window": {
                "type": "integer",
                "default": 0,
                "description": "Skip-and-merge window (0=disabled). Enable for SDPM-like behavior.",
                "minimum": 0
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        embedding_model: str,
        chunk_size: int,
        threshold: float,
        similarity_window: int,
        skip_window: int
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = ChonkieSemanticChunker(
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            threshold=threshold,
            similarity_window=similarity_window,
            skip_window=skip_window
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "semantic"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using SemanticChunker.
        
        Args:
            text: The text to chunk
            embedding_model: Embedding model for similarity (default: minishlab/potion-base-32M)
            chunk_size: Maximum tokens per chunk (default: 2048)
            threshold: Similarity threshold 0-1 (default: 0.8)
            similarity_window: Window for similarity calc (default: 3)
            skip_window: Skip-and-merge window (default: 0)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        embedding_model = validated.get("embedding_model", "minishlab/potion-base-32M")
        chunk_size = validated.get("chunk_size", 2048)
        threshold = validated.get("threshold", 0.8)
        similarity_window = validated.get("similarity_window", 3)
        skip_window = validated.get("skip_window", 0)
        
        logger.info(f"SemanticChunker: chunking with threshold={threshold}, model={embedding_model}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            embedding_model,
            chunk_size,
            threshold,
            similarity_window,
            skip_window
        )
        
        logger.info(f"SemanticChunker: created {len(chunks)} chunks")
        return chunks
