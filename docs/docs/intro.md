---
sidebar_position: 1
---

# PDFStract Documentation

Welcome to **PDFStract** — the data preparation layer for RAG. Extract. Chunk. Embed.

PDFStract is a comprehensive tool for converting PDFs into vector-ready content for AI applications.

**One unified API.** Switch between 10+ extraction libraries, 10+ chunking methods, and multiple embedding providers with a single parameter change. Focus on your RAG outcomes, not library dependencies.

## What is PDFStract?

PDFStract handles the complete data preparation pipeline for RAG:

- **Extract**: Convert PDFs using 10+ libraries (Marker, Docling, PyMuPDF4LLM, Unstructured, PaddleOCR, and more)
- **Chunk**: Split text into optimal segments using 10+ methods (Token, Semantic, Recursive, Code-aware, and more)  
- **Embed**: Generate vector embeddings with multiple providers (OpenAI, Sentence Transformers, Ollama, and more)
- **Multiple Interfaces**: Use as Python library, CLI tool, or Web UI

## Key Features

🚀 **10+ PDF Conversion Libraries**: Choose the best tool for your documents  
✂️ **10+ Chunking Methods**: From simple token-based to advanced semantic chunking  
📱 **Modern Web UI**: Beautiful React interface with real-time preview  
💻 **Full CLI Support**: Batch processing and automation  
🐳 **Docker Ready**: One-command deployment  
⚡ **High Performance**: Parallel processing and optimized workflows  

## Quick Example

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# 1. Convert PDF
text = pdfstract.convert('document.pdf', library='docling')

# 2. Chunk for RAG
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=512)

# 3. Generate embeddings
vectors = pdfstract.embed_texts([c['text'] for c in chunks['chunks']], model='auto')

print(f"Ready for vector DB: {len(vectors)} embeddings")
```

Or use the all-in-one pipeline:

```python
# Complete RAG pipeline in one call
result = pdfstract.convert_chunk_embed(
    'document.pdf',
    library='marker',
    chunker='semantic',
    embedding='sentence-transformers'
)
# Each chunk now has an embedding attached!
```

## Installation Tiers

Choose the right tier for your needs:

```bash
# Base - Fast extractors (pymupdf4llm, markitdown)
pip install pdfstract

# Standard - Adds OCR (pytesseract, unstructured)
pip install pdfstract[standard]

# Advanced - ML-powered (marker, docling, paddleocr, deepseek)
pip install pdfstract[advanced]

# All - All converters combined
pip install pdfstract[all]
```

| Tier | Libraries | Best For |
|------|-----------|----------|
| **Base** | pymupdf4llm, markitdown | Fast extraction, simple PDFs |
| **Standard** | pytesseract, unstructured | OCR support, structured docs |
| **Advanced** | marker, docling, paddleocr, deepseek | Best quality, ML-powered |
| **All** | All libraries combined | Complete RAG pipeline |

## Get Started

Ready to dive in? Here are some great starting points:

- **[Quick Start Guide](quick-start)** - Get up and running in 5 minutes
- **[Installation](installation)** - Install PDFStract in your environment

### Core Features

- **[Extract](features/extract)** - PDF conversion with 10+ libraries
- **[Chunk](features/chunk)** - Text splitting with 10+ methods
- **[Embed](features/embed)** - Vector embeddings with multiple providers

### Interfaces

- **[Python API](api/overview)** - Integrate into your applications
- **[CLI Guide](cli/overview)** - Use from the command line
- **[Web UI](web-ui/overview)** - Try the visual interface

## Architecture

PDFStract follows a modular architecture:

```
PDF Input → Converter Library → Raw Text → Chunker → Structured Chunks → Your RAG Pipeline
```

Each step is configurable, allowing you to choose the best tools for your specific use case.

## Community

- **GitHub**: [aksarav/pdfstract](https://github.com/aksarav/pdfstract)
- **Issues**: Report bugs or request features
- **Discussions**: Share use cases and get help

Let's get started! 🚀
