---
sidebar_position: 1
---

# PDFStract Documentation

Welcome to **PDFStract** — the first layer in your RAG pipeline! PDFStract is a comprehensive tool for converting PDFs into structured, chunked content ready for AI applications.

## What is PDFStract?

PDFStract is designed to get your PDFs ready for AI by providing:

- ✅ **Extract**: Convert PDFs using 10+ libraries (Marker, Docling, PyMuPDF4LLM, Unstructured, PaddleOCR, and more)
- ✅ **Chunk**: Split text into smaller segments using 10+ methods (Token, Semantic, Recursive, Code-aware, and more)  
- ✅ **Embed**: Prepare chunks for embedding models and vector databases
- ✅ **Multiple Interfaces**: Use as Python library, CLI tool, or Web UI

## Key Features

🚀 **10+ PDF Conversion Libraries**: Choose the best tool for your documents  
✂️ **10+ Chunking Methods**: From simple token-based to advanced semantic chunking  
📱 **Modern Web UI**: Beautiful React interface with real-time preview  
💻 **Full CLI Support**: Batch processing and automation  
🐳 **Docker Ready**: One-command deployment  
⚡ **High Performance**: Parallel processing and optimized workflows  

## Quick Example

```python
from pdfstract = PDFStract()

# 1. Convert PDF
text = pdfstract.convert('document.pdf', library='docling')

# 2. Chunk for RAG
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=512)

# 3. Use chunks in your pipeline
print(f"Ready for embedding: {chunks['total_chunks']} chunks")
```

## Get Started

Ready to dive in? Here are some great starting points:

- **[Quick Start Guide](quick-start)** - Get up and running in 5 minutes
- **[Installation](installation)** - Install PDFStract in your environment  
- **[First Conversion](first-conversion)** - Convert your first PDF
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
