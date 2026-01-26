"""
SentenceChunker - Splits text into chunks while preserving sentence boundaries.

Best for: Maintaining semantic completeness at the sentence level.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie
try:
    from chonkie import SentenceChunker as ChonkieSentenceChunker
    CHONKIE_AVAILABLE = True
except ImportError:
    CHONKIE_AVAILABLE = False
    ChonkieSentenceChunker = None


class SentenceChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's SentenceChunker.
    
    Splits text into chunks while preserving complete sentences, ensuring 
    that each chunk maintains proper sentence boundaries and context.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "sentence"
    
    @property
    def available(self) -> bool:
        return CHONKIE_AVAILABLE
    
    @property
    def description(self) -> str:
        return "Split text into chunks while preserving sentence boundaries"
    
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
            },
            "min_sentences_per_chunk": {
                "type": "integer",
                "default": 1,
                "description": "Minimum number of sentences in each chunk",
                "minimum": 1
            },
            "min_characters_per_sentence": {
                "type": "integer",
                "default": 12,
                "description": "Minimum number of characters per sentence",
                "minimum": 1
            },
            "delim": {
                "type": "string",
                "default": ".,!?\n",
                "description": "Sentence delimiters (as a single string of characters)"
            }
        }
    
    def _get_cache_key(self, **params) -> str:
        """Generate a cache key from parameters"""
        return "_".join(str(v) for v in sorted(params.items()))
    
    def _chunk_sync(
        self, 
        text: str, 
        tokenizer: str,
        chunk_size: int, 
        chunk_overlap: int,
        min_sentences_per_chunk: int,
        min_characters_per_sentence: int,
        delim: Union[str, List[str]]
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        # Convert delim string to list if needed
        if isinstance(delim, str):
            delim_list = list(delim)
        else:
            delim_list = delim
        
        chunker = ChonkieSentenceChunker(
            tokenizer=tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_sentences_per_chunk=min_sentences_per_chunk,
            min_characters_per_sentence=min_characters_per_sentence,
            delim=delim_list
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "sentence"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using SentenceChunker.
        
        Args:
            text: The text to chunk
            tokenizer: Tokenizer to use (default: "character")
            chunk_size: Maximum tokens per chunk (default: 2048)
            chunk_overlap: Overlapping tokens between chunks (default: 0)
            min_sentences_per_chunk: Minimum sentences per chunk (default: 1)
            min_characters_per_sentence: Minimum characters per sentence (default: 12)
            delim: Sentence delimiters (default: ".,!?\n")
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError("SentenceChunker is not available. Install chonkie: pip install chonkie")
        
        validated = self.validate_params(params)
        tokenizer = validated.get("tokenizer", "character")
        chunk_size = validated.get("chunk_size", 2048)
        chunk_overlap = validated.get("chunk_overlap", 0)
        min_sentences_per_chunk = validated.get("min_sentences_per_chunk", 1)
        min_characters_per_sentence = validated.get("min_characters_per_sentence", 12)
        delim = validated.get("delim", ".,!?\n")
        
        logger.info(f"SentenceChunker: chunking text with size={chunk_size}, min_sentences={min_sentences_per_chunk}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            tokenizer,
            chunk_size,
            chunk_overlap,
            min_sentences_per_chunk,
            min_characters_per_sentence,
            delim
        )
        
        logger.info(f"SentenceChunker: created {len(chunks)} chunks")
        return chunks
