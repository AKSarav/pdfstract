"""
FastChunker - High-speed chunking using regex patterns.

Best for: Fast processing of large documents with predictable delimiters.
Requires: chonkie[all] - pip install chonkie[all]
"""

import asyncio
from typing import List, Dict, Any, Union
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie fast chunker
try:
    from chonkie import FastChunker as ChonkieFastChunker
    CHONKIE_FAST_AVAILABLE = True
except ImportError:
    CHONKIE_FAST_AVAILABLE = False
    ChonkieFastChunker = None


class FastChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's FastChunker.
    
    Uses regex-based splitting for extremely fast chunking.
    Ideal for high-throughput scenarios with predictable delimiters.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "fast"
    
    @property
    def available(self) -> bool:
        return CHONKIE_FAST_AVAILABLE
    
    @property
    def error_message(self) -> str:
        if self.available:
            return None
        return "FastChunker requires extra dependencies. Install with: pip install chonkie[all]"
    
    @property
    def description(self) -> str:
        return "High-speed regex-based chunking"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "chunk_size": {
                "type": "integer",
                "default": 4096,
                "description": "Maximum number of bytes per chunk",
                "minimum": 1
            },
            "delimiters": {
                "type": "string",
                "default": "\n.?!",
                "description": "Single-byte delimiter characters to split on (e.g., '.?!\\n')"
            },
            "pattern": {
                "type": "string",
                "default": "",
                "description": "Multi-byte pattern to split on (overrides delimiters if set)"
            },
            "prefix": {
                "type": "boolean",
                "default": False,
                "description": "Keep delimiter at start of next chunk instead of end of current"
            },
            "consecutive": {
                "type": "boolean",
                "default": False,
                "description": "Split at START of consecutive delimiter runs"
            },
            "forward_fallback": {
                "type": "boolean",
                "default": False,
                "description": "Search forward for delimiter if none found in backward window"
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        chunk_size: int,
        delimiters: str,
        pattern: str,
        prefix: bool,
        consecutive: bool,
        forward_fallback: bool
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        kwargs = {
            "chunk_size": chunk_size,
            "prefix": prefix,
            "consecutive": consecutive,
            "forward_fallback": forward_fallback
        }
        
        # Use pattern if provided, otherwise use delimiters
        # Note: delimiters is a string of single-byte characters like "\n.?!"
        if pattern:
            kwargs["pattern"] = pattern
        else:
            kwargs["delimiters"] = delimiters
        
        chunker = ChonkieFastChunker(**kwargs)
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count if hasattr(c, 'token_count') else 0,
                metadata={"chunker": "fast"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using FastChunker (SIMD-accelerated, 100+ GB/s).
        
        Args:
            text: The text to chunk
            chunk_size: Maximum bytes per chunk (default: 4096)
            delimiters: Single-byte delimiter chars (default: "\\n.?!")
            pattern: Multi-byte pattern (default: "")
            prefix: Keep delimiter at start of next chunk (default: False)
            consecutive: Split at start of consecutive delimiters (default: False)
            forward_fallback: Search forward if no delimiter found (default: False)
            
        Returns:
            List of Chunk objects (token_count is always 0 for speed)
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        chunk_size = validated.get("chunk_size", 4096)
        delimiters = validated.get("delimiters", "\n.?!")
        pattern = validated.get("pattern", "")
        prefix = validated.get("prefix", False)
        consecutive = validated.get("consecutive", False)
        forward_fallback = validated.get("forward_fallback", False)
        
        logger.info(f"FastChunker: chunking with size={chunk_size} bytes")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            chunk_size,
            delimiters,
            pattern,
            prefix,
            consecutive,
            forward_fallback
        )
        
        logger.info(f"FastChunker: created {len(chunks)} chunks")
        return chunks
