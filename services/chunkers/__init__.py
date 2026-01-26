"""
Chonkie-based text chunking service for PDFStract.

Provides various chunking strategies for splitting text/markdown into smaller chunks
for RAG, embedding, and other NLP applications.

Phase 1 (base install):
- TokenChunker: Fixed-size token chunks
- SentenceChunker: Sentence-aware chunking
- RecursiveChunker: Recursive document splitting
- TableChunker: Markdown table chunking

Phase 2 (extra dependencies):
- SemanticChunker: Embedding-based semantic chunking (chonkie[semantic])
- CodeChunker: AST-aware code chunking (chonkie[code])
- LateChunker: ColBERT-style late interaction (chonkie[st])
- NeuralChunker: Neural boundary detection (chonkie[neural])
- FastChunker: High-speed regex chunking (chonkie[all])
- SlumberChunker: LLM-powered chunking (chonkie[genie])
"""

from services.chunkers.base import BaseChunker, Chunk, ChunkingResult, ChunkerType

__all__ = [
    "BaseChunker",
    "Chunk",
    "ChunkingResult",
    "ChunkerType",
]
