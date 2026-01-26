"""
Base classes for chunking service.

All chunker implementations inherit from BaseChunker and return Chunk objects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ChunkerType(Enum):
    """Supported chunker types"""
    TOKEN = "token"
    FAST = "fast"
    SENTENCE = "sentence"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    CODE = "code"
    TABLE = "table"
    LATE = "late"
    NEURAL = "neural"
    SLUMBER = "slumber"


@dataclass
class Chunk:
    """
    Represents a single chunk of text.
    
    Attributes:
        text: The chunk text content
        start_index: Starting position in the original text
        end_index: Ending position in the original text
        token_count: Number of tokens in the chunk
        metadata: Optional additional metadata (e.g., embedding, context)
    """
    text: str
    start_index: int
    end_index: int
    token_count: int
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation"""
        return asdict(self)
    
    def __len__(self) -> int:
        """Return the length of the chunk text"""
        return len(self.text)


@dataclass
class ChunkingResult:
    """
    Result of a chunking operation.
    
    Attributes:
        chunks: List of Chunk objects
        chunker_name: Name of the chunker used
        parameters: Parameters used for chunking
        total_chunks: Total number of chunks created
        total_tokens: Total tokens across all chunks
        original_length: Length of original text
    """
    chunks: List[Chunk]
    chunker_name: str
    parameters: Dict[str, Any]
    total_chunks: int = 0
    total_tokens: int = 0
    original_length: int = 0
    
    def __post_init__(self):
        self.total_chunks = len(self.chunks)
        self.total_tokens = sum(c.token_count for c in self.chunks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "chunker_name": self.chunker_name,
            "parameters": self.parameters,
            "total_chunks": self.total_chunks,
            "total_tokens": self.total_tokens,
            "original_length": self.original_length
        }


class BaseChunker(ABC):
    """
    Abstract base class for all chunker implementations.
    
    All chunkers must implement:
    - name: Property returning the chunker identifier
    - available: Property checking if dependencies are installed
    - parameters_schema: Property returning JSON schema for parameters
    - chunk: Async method to perform chunking
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name/identifier of the chunker"""
        pass
    
    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if the chunker's dependencies are available"""
        pass
    
    @property
    def error_message(self) -> Optional[str]:
        """Return error message if chunker is not available"""
        return None if self.available else f"{self.name} dependencies not installed"
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema describing the chunker's parameters.
        
        Each parameter should include:
        - type: The parameter type (string, integer, number, boolean, array, object)
        - default: Default value
        - description: Human-readable description
        - required: Whether the parameter is required (default: False)
        - enum: Optional list of allowed values
        - minimum/maximum: Optional numeric constraints
        
        Example:
            {
                "chunk_size": {
                    "type": "integer",
                    "default": 2048,
                    "description": "Maximum number of tokens per chunk",
                    "minimum": 1
                }
            }
        """
        pass
    
    @property
    def description(self) -> str:
        """Return a human-readable description of the chunker"""
        return f"{self.name} chunker"
    
    @abstractmethod
    async def chunk(self, text: str, **params) -> List[Chunk]:
        """
        Chunk the input text using the specified parameters.
        
        Args:
            text: The text to chunk
            **params: Chunker-specific parameters
            
        Returns:
            List of Chunk objects
        """
        pass
    
    async def chunk_with_result(self, text: str, **params) -> ChunkingResult:
        """
        Chunk text and return a ChunkingResult with metadata.
        
        Args:
            text: The text to chunk
            **params: Chunker-specific parameters
            
        Returns:
            ChunkingResult containing chunks and metadata
        """
        chunks = await self.chunk(text, **params)
        return ChunkingResult(
            chunks=chunks,
            chunker_name=self.name,
            parameters=params,
            original_length=len(text)
        )
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and apply defaults to parameters.
        
        Args:
            params: User-provided parameters
            
        Returns:
            Parameters with defaults applied
        """
        schema = self.parameters_schema
        validated = {}
        
        for param_name, param_spec in schema.items():
            if param_name in params:
                validated[param_name] = params[param_name]
            elif "default" in param_spec:
                validated[param_name] = param_spec["default"]
            elif param_spec.get("required", False):
                raise ValueError(f"Required parameter '{param_name}' not provided")
        
        return validated
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the chunker.
        
        Returns:
            Dictionary with chunker info including name, availability, parameters
        """
        return {
            "name": self.name,
            "available": self.available,
            "description": self.description,
            "parameters": self.parameters_schema,
            "error": self.error_message if not self.available else None
        }
