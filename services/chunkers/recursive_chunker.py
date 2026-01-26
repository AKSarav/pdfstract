"""
RecursiveChunker - Recursively chunks documents into smaller chunks.

Best for: Long documents with well-defined structure (books, research papers, etc.)
"""

import asyncio
from typing import List, Dict, Any, Optional
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie
try:
    from chonkie import RecursiveChunker as ChonkieRecursiveChunker
    from chonkie import RecursiveRules
    CHONKIE_AVAILABLE = True
except ImportError:
    CHONKIE_AVAILABLE = False
    ChonkieRecursiveChunker = None
    RecursiveRules = None


class RecursiveChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's RecursiveChunker.
    
    Recursively chunks documents into smaller chunks using configurable rules.
    Good for documents with well-defined structure like books or research papers.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "recursive"
    
    @property
    def available(self) -> bool:
        return CHONKIE_AVAILABLE
    
    @property
    def description(self) -> str:
        return "Recursively chunk documents into smaller chunks based on structure"
    
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
            "min_characters_per_chunk": {
                "type": "integer",
                "default": 24,
                "description": "Minimum number of characters per chunk",
                "minimum": 1
            },
            "recipe": {
                "type": "string",
                "default": "",
                "description": "Pre-defined recipe to use (markdown, etc.). Leave empty for default rules.",
                "enum": ["", "markdown"]
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        tokenizer: str,
        chunk_size: int,
        min_characters_per_chunk: int,
        recipe: str
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        if recipe and recipe != "":
            # Use recipe-based initialization
            chunker = ChonkieRecursiveChunker.from_recipe(
                recipe,
                lang="en"
            )
            # Override chunk_size if specified
            chunker.chunk_size = chunk_size
        else:
            # Use default rules
            chunker = ChonkieRecursiveChunker(
                tokenizer=tokenizer,
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
                metadata={"chunker": "recursive"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using RecursiveChunker.
        
        Args:
            text: The text to chunk
            tokenizer: Tokenizer to use (default: "character")
            chunk_size: Maximum tokens per chunk (default: 2048)
            min_characters_per_chunk: Minimum characters per chunk (default: 24)
            recipe: Pre-defined recipe (default: "" for default rules)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError("RecursiveChunker is not available. Install chonkie: pip install chonkie")
        
        validated = self.validate_params(params)
        tokenizer = validated.get("tokenizer", "character")
        chunk_size = validated.get("chunk_size", 2048)
        min_characters_per_chunk = validated.get("min_characters_per_chunk", 24)
        recipe = validated.get("recipe", "")
        
        logger.info(f"RecursiveChunker: chunking text with size={chunk_size}, recipe={recipe or 'default'}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            tokenizer,
            chunk_size,
            min_characters_per_chunk,
            recipe
        )
        
        logger.info(f"RecursiveChunker: created {len(chunks)} chunks")
        return chunks
