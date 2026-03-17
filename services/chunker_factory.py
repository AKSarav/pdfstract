"""
ChunkerFactory - Factory class for creating and managing text chunkers.

Provides a unified interface for all chunking strategies from the Chonkie library.
"""

from typing import Dict, List, Optional, Any
from services.chunkers.base import BaseChunker, Chunk, ChunkingResult
from services.logger import logger


class ChunkerFactory:
    """
    Factory class for creating and managing text chunkers.
    
    Implements a singleton-like pattern for chunker instances, providing
    a unified interface for all available chunking strategies.
    """
    
    def __init__(self):
        self._chunkers: Dict[str, BaseChunker] = {}
        self._register_default_chunkers()
        
    def get_default_chunker(self) -> Optional[BaseChunker]:
        """Get the default chunker (first available in priority order)"""
        for name, chunker in self._chunkers.items():
            if chunker.available:
                logger.info(f"Auto-Selected chunker: {name}")
                return chunker
        logger.warning("No available chunkers found for default selection")
        return None        
    
    def _register_default_chunkers(self):
        """Register all available chunker implementations"""
        # Import chunkers here to avoid circular imports
        from services.chunkers.token_chunker import TokenChunkerWrapper
        from services.chunkers.sentence_chunker import SentenceChunkerWrapper
        from services.chunkers.recursive_chunker import RecursiveChunkerWrapper
        from services.chunkers.table_chunker import TableChunkerWrapper
        
        chunkers = [
            TokenChunkerWrapper(),
            SentenceChunkerWrapper(),
            RecursiveChunkerWrapper(),
            TableChunkerWrapper(),
        ]
        
        # Try to import advanced chunkers (may require extra dependencies)
        try:
            from services.chunkers.semantic_chunker import SemanticChunkerWrapper
            chunkers.append(SemanticChunkerWrapper())
        except ImportError:
            logger.debug("SemanticChunker not available (requires chonkie[semantic])")
        
        try:
            from services.chunkers.code_chunker import CodeChunkerWrapper
            chunkers.append(CodeChunkerWrapper())
        except ImportError:
            logger.debug("CodeChunker not available (requires chonkie[code])")
        
        try:
            from services.chunkers.late_chunker import LateChunkerWrapper
            chunkers.append(LateChunkerWrapper())
        except ImportError:
            logger.debug("LateChunker not available (requires chonkie[st])")
        
        try:
            from services.chunkers.neural_chunker import NeuralChunkerWrapper
            chunkers.append(NeuralChunkerWrapper())
        except ImportError:
            logger.debug("NeuralChunker not available (requires chonkie[neural])")
        
        try:
            from services.chunkers.fast_chunker import FastChunkerWrapper
            chunkers.append(FastChunkerWrapper())
        except ImportError:
            logger.debug("FastChunker not available (requires chonkie[all])")
        
        try:
            from services.chunkers.slumber_chunker import SlumberChunkerWrapper
            chunkers.append(SlumberChunkerWrapper())
        except ImportError:
            logger.debug("SlumberChunker not available (requires chonkie[genie])")
        
        # Register chunkers
        for chunker in chunkers:
            self._chunkers[chunker.name] = chunker
            if chunker.available:
                logger.info(f"Registered chunker: {chunker.name}")
            else:
                logger.warning(f"Chunker {chunker.name} registered but not available: {chunker.error_message}")
    
    def get_chunker(self, name: str) -> Optional[BaseChunker]:
        """
        Get a chunker by name.
        
        Args:
            name: The chunker name/identifier
            
        Returns:
            BaseChunker instance or None if not found
        """
        return self._chunkers.get(name)
    
    def list_available_chunkers(self) -> List[str]:
        """
        List names of all available (ready to use) chunkers.
        
        Returns:
            List of chunker names that are available
        """
        return [name for name, chunker in self._chunkers.items() if chunker.available]
    
    def list_all_chunkers(self) -> List[Dict[str, Any]]:
        """
        List all chunkers with their availability status and parameters.
        
        Returns:
            List of dictionaries with chunker info
        """
        result = []
        for name, chunker in self._chunkers.items():
            result.append(chunker.get_info())
        return result
    
    async def chunk(
        self,
        chunker_name: str,
        text: str,
        **params
    ) -> List[Chunk]:
        """
        Chunk text using the specified chunker.
        
        Args:
            chunker_name: Name of the chunker to use
            text: Text to chunk
            **params: Chunker-specific parameters
            
        Returns:
            List of Chunk objects
            
        Raises:
            ValueError: If chunker not found or not available
        """
        chunker = self.get_chunker(chunker_name)
        
        if not chunker:
            chunker = self.get_default_chunker()
        
        if not chunker.available:
            raise ValueError(
                f"Chunker '{chunker_name}' is not available: {chunker.error_message}"
            )
        
        return await chunker.chunk(text, **params)
    
    async def chunk_with_result(
        self,
        chunker_name: str,
        text: str,
        **params
    ) -> ChunkingResult:
        """
        Chunk text and return a ChunkingResult with full metadata.
        
        Args:
            chunker_name: Name of the chunker to use
            text: Text to chunk
            **params: Chunker-specific parameters
            
        Returns:
            ChunkingResult with chunks and metadata
            
        Raises:
            ValueError: If chunker not found or not available
        """
        
        if chunker_name == 'auto':
            chunker = self.get_default_chunker()
            if not chunker:
                raise ValueError("No available chunkers found for auto-selection")
        else:
            if not (chunker := self.get_chunker(chunker_name)):
                raise ValueError(f"Chunker '{chunker_name}' not found")
        
        if not chunker.available:
            raise ValueError(
                f"Chunker '{chunker_name}' is not available: {chunker.error_message}"
            )
        
        return await chunker.chunk_with_result(text, **params)
    
    def get_chunker_schema(self, chunker_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the parameter schema for a specific chunker.
        
        Args:
            chunker_name: Name of the chunker
            
        Returns:
            Parameter schema dictionary or None if not found
        """
        chunker = self.get_chunker(chunker_name)
        if chunker:
            return chunker.parameters_schema
        return None


# Lazy initialization - factory will be created on first use
_factory: Optional[ChunkerFactory] = None


def get_chunker_factory() -> ChunkerFactory:
    """
    Get the global ChunkerFactory instance.
    
    Uses lazy initialization to avoid loading chunkers until needed.
    
    Returns:
        ChunkerFactory singleton instance
    """
    global _factory
    if _factory is None:
        _factory = ChunkerFactory()
    return _factory
