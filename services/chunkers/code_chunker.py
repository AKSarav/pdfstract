"""
CodeChunker - Chunks code using AST-aware parsing.

Best for: Code files, preserving function/class boundaries.
Requires: chonkie[code] - pip install chonkie[code]
"""

import asyncio
from typing import List, Dict, Any
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie code chunker
try:
    from chonkie import CodeChunker as ChonkieCodeChunker
    CHONKIE_CODE_AVAILABLE = True
except ImportError:
    CHONKIE_CODE_AVAILABLE = False
    ChonkieCodeChunker = None


class CodeChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's CodeChunker.
    
    Uses tree-sitter for AST-aware code chunking, preserving
    function and class boundaries for better code understanding.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "code"
    
    @property
    def available(self) -> bool:
        return CHONKIE_CODE_AVAILABLE
    
    @property
    def error_message(self) -> str:
        if self.available:
            return None
        return "CodeChunker requires extra dependencies. Install with: pip install chonkie[code]"
    
    @property
    def description(self) -> str:
        return "Chunk code files using AST-aware parsing"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "language": {
                "type": "string",
                "default": "python",
                "description": "Programming language of the code",
                "enum": [
                    "python", "javascript", "typescript", "java", "c", "cpp", 
                    "go", "rust", "ruby", "php", "c_sharp", "kotlin", "scala",
                    "swift", "bash", "sql", "html", "css", "json", "yaml", "markdown"
                ]
            },
            "tokenizer": {
                "type": "string",
                "default": "character",
                "description": "Tokenizer to use for counting",
                "enum": ["character", "word", "byte", "gpt2"]
            },
            "chunk_size": {
                "type": "integer",
                "default": 2048,
                "description": "Maximum number of tokens per chunk",
                "minimum": 1
            },
            "include_nodes": {
                "type": "boolean",
                "default": False,
                "description": "Include AST node information in output"
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        language: str,
        tokenizer: str,
        chunk_size: int,
        include_nodes: bool
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = ChonkieCodeChunker(
            language=language,
            tokenizer=tokenizer,
            chunk_size=chunk_size,
            include_nodes=include_nodes
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "code", "language": language}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk code using CodeChunker.
        
        Args:
            text: The code to chunk
            language: Programming language (default: python)
            tokenizer: Tokenizer to use (default: character)
            chunk_size: Maximum tokens per chunk (default: 2048)
            include_nodes: Include AST nodes (default: False)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        language = validated.get("language", "python")
        tokenizer = validated.get("tokenizer", "character")
        chunk_size = validated.get("chunk_size", 2048)
        include_nodes = validated.get("include_nodes", False)
        
        logger.info(f"CodeChunker: chunking {language} code with size={chunk_size}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            language,
            tokenizer,
            chunk_size,
            include_nodes
        )
        
        logger.info(f"CodeChunker: created {len(chunks)} chunks")
        return chunks
