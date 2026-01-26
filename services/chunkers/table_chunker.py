"""
TableChunker - Splits markdown tables into manageable chunks by row.

Best for: Processing, indexing, or embedding tabular data in LLM and RAG pipelines.
Preserves headers in each chunk.
"""

import asyncio
from typing import List, Dict, Any, Optional
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie
try:
    from chonkie import TableChunker as ChonkieTableChunker
    CHONKIE_AVAILABLE = True
except ImportError:
    CHONKIE_AVAILABLE = False
    ChonkieTableChunker = None


class TableChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's TableChunker.
    
    Splits large markdown tables into smaller, manageable chunks by row,
    always preserving the header. Great for tabular data in RAG and LLM pipelines.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "table"
    
    @property
    def available(self) -> bool:
        return CHONKIE_AVAILABLE
    
    @property
    def description(self) -> str:
        return "Split markdown tables into chunks by row, preserving headers"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "tokenizer": {
                "type": "string",
                "default": "row",
                "description": "Tokenizer mode: 'row' for row-based chunking, or token-based (character, gpt2)",
                "enum": ["row", "character", "gpt2"]
            },
            "chunk_size": {
                "type": "integer",
                "default": 3,
                "description": "Maximum number of rows (if tokenizer=row) or tokens per chunk",
                "minimum": 1
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        tokenizer: str,
        chunk_size: int
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = ChonkieTableChunker(
            tokenizer=tokenizer,
            chunk_size=chunk_size
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "table"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk markdown table text using TableChunker.
        
        Args:
            text: The markdown table text to chunk
            tokenizer: Tokenizer mode - 'row' for row-based (default), or token-based
            chunk_size: Max rows (if tokenizer=row) or tokens per chunk (default: 3)
            
        Returns:
            List of Chunk objects, each containing a valid markdown table segment
            
        Note:
            The input text should be a valid markdown table with:
            - Header row
            - Separator row (e.g., |---|---|)
            - Data rows
        """
        if not self.available:
            raise RuntimeError("TableChunker is not available. Install chonkie: pip install chonkie")
        
        validated = self.validate_params(params)
        tokenizer = validated.get("tokenizer", "row")
        chunk_size = validated.get("chunk_size", 3)
        
        logger.info(f"TableChunker: chunking table with tokenizer={tokenizer}, size={chunk_size}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            tokenizer,
            chunk_size
        )
        
        logger.info(f"TableChunker: created {len(chunks)} chunks")
        return chunks
