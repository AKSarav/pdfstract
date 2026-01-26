"""
NeuralChunker - Neural network-based boundary detection for chunking.

Best for: Finding natural breakpoints using trained models.
Requires: chonkie[neural] - pip install chonkie[neural]
"""

import asyncio
from typing import List, Dict, Any
from services.chunkers.base import BaseChunker, Chunk
from services.logger import logger

# Try to import chonkie neural chunker
try:
    from chonkie import NeuralChunker as ChonkieNeuralChunker
    CHONKIE_NEURAL_AVAILABLE = True
except ImportError:
    CHONKIE_NEURAL_AVAILABLE = False
    ChonkieNeuralChunker = None


class NeuralChunkerWrapper(BaseChunker):
    """
    Wrapper for Chonkie's NeuralChunker.
    
    Uses a trained neural network model to detect natural chunk boundaries
    in text, producing high-quality semantic chunks.
    """
    
    def __init__(self):
        self._chunker_cache: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        return "neural"
    
    @property
    def available(self) -> bool:
        return CHONKIE_NEURAL_AVAILABLE
    
    @property
    def error_message(self) -> str:
        if self.available:
            return None
        return "NeuralChunker requires extra dependencies. Install with: pip install chonkie[neural]"
    
    @property
    def description(self) -> str:
        return "Chunk text using neural network boundary detection"
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "model": {
                "type": "string",
                "default": "mirth/chonky_modernbert_base_1",
                "description": "Neural chunking model to use"
            },
            "device_map": {
                "type": "string",
                "default": "auto",
                "description": "Device mapping for model (auto, cpu, cuda)",
                "enum": ["auto", "cpu", "cuda"]
            },
            "min_characters_per_chunk": {
                "type": "integer",
                "default": 24,
                "description": "Minimum characters per chunk",
                "minimum": 1
            },
            "stride": {
                "type": "integer",
                "default": 256,
                "description": "Stride for sliding window processing",
                "minimum": 1
            }
        }
    
    def _chunk_sync(
        self, 
        text: str, 
        model: str,
        device_map: str,
        min_characters_per_chunk: int,
        stride: int
    ) -> List[Chunk]:
        """Synchronous chunking operation"""
        chunker = ChonkieNeuralChunker(
            model=model,
            device_map=device_map,
            min_characters_per_chunk=min_characters_per_chunk,
            stride=stride
        )
        
        chonkie_chunks = chunker.chunk(text)
        
        return [
            Chunk(
                text=c.text,
                start_index=c.start_index,
                end_index=c.end_index,
                token_count=c.token_count,
                metadata={"chunker": "neural"}
            )
            for c in chonkie_chunks
        ]
    
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk text using NeuralChunker.
        
        Args:
            text: The text to chunk
            model: Neural chunking model (default: mirth/chonky_modernbert_base_1)
            device_map: Device mapping (default: auto)
            min_characters_per_chunk: Minimum chars per chunk (default: 24)
            stride: Sliding window stride (default: 256)
            
        Returns:
            List of Chunk objects
        """
        if not self.available:
            raise RuntimeError(self.error_message)
        
        validated = self.validate_params(params)
        model = validated.get("model", "mirth/chonky_modernbert_base_1")
        device_map = validated.get("device_map", "auto")
        min_characters_per_chunk = validated.get("min_characters_per_chunk", 24)
        stride = validated.get("stride", 256)
        
        logger.info(f"NeuralChunker: chunking with model={model}, device={device_map}")
        
        # Run blocking operation in thread executor
        chunks = await asyncio.to_thread(
            self._chunk_sync,
            text,
            model,
            device_map,
            min_characters_per_chunk,
            stride
        )
        
        logger.info(f"NeuralChunker: created {len(chunks)} chunks")
        return chunks
