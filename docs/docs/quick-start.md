---
sidebar_position: 1
---

# Quick Start

Get up and running with PDFStract in just a few minutes! This guide will help you convert your first PDF and create chunks ready for RAG applications.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Installation

PDFStract offers tiered installation based on your needs:

| Tier | Libraries | Install Command |
|------|-----------|-----------------|
| **Base** | pymupdf4llm, markitdown | `pip install pdfstract` |
| **Standard** | pytesseract, unstructured | `pip install pdfstract[standard]` |
| **Advanced** | marker, docling, paddleocr, deepseek | `pip install pdfstract[advanced]` |
| **All** | All libraries combined | `pip install pdfstract[all]` |

```bash
# Quick start with base libraries
pip install pdfstract

# Recommended for most users
pip install pdfstract[standard]

# Best quality (larger download)
pip install pdfstract[advanced]

# All converters combined
pip install pdfstract[all]
```

For development or latest features:

```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract
pip install -e .
```

## Your First Conversion

Let's convert a PDF to text using the simplest approach:

```python
from pdfstract import PDFStract

# Initialize PDFStract
pdfstract = PDFStract()

# Convert PDF to text
text = pdfstract.convert('your-document.pdf')

print("Extracted text:")
print(text[:500] + "...")  # Show first 500 characters
```

## Create Your First Chunks

Now let's chunk that text for RAG applications:

```python
# Chunk the text for RAG
chunks = pdfstract.chunk(text, chunk_size=512, chunk_overlap=50)

print(f"Created {chunks['total_chunks']} chunks")
print("First chunk:")
print(chunks['chunks'][0]['text'][:200] + "...")
```

## Available Libraries by Tier

### Base (pip install pdfstract)
- **pymupdf4llm** - Fast and lightweight
- **markitdown** - Microsoft's markdown converter

### Standard (pip install pdfstract[standard])
- All Base libraries plus:
- **pytesseract** - OCR for scanned PDFs
- **unstructured** - Smart document parsing

### Advanced (pip install pdfstract[advanced])
- All Standard libraries plus:
- **marker** - Excellent for complex layouts
- **docling** - IBM's document intelligence
- **paddleocr** - Accurate OCR engine
- **deepseek** - GPU-accelerated OCR

Example with specific tools:

```python
# Use Marker for PDF conversion and semantic chunking
text = pdfstract.convert('document.pdf', library='marker')
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=1024)
```

## Web Interface

Try the visual interface:

```bash
# Start the web server
pdfstract web

# Open http://localhost:8000 in your browser
```

## CLI Usage

Use PDFStract from the command line:

```bash
# Convert a single PDF
pdfstract convert document.pdf

# Convert and chunk in one command
pdfstract process document.pdf --chunker semantic --chunk-size 512

# Batch process multiple files
pdfstract batch ./pdfs/ --output ./results/
```

## Next Steps

Now that you have the basics down, explore more advanced features:

- **[Installation Guide](installation)** - Advanced installation options
- **[Python API](api/overview)** - Complete API reference
- **[CLI Guide](cli/overview)** - Full command-line interface
- **[Web UI](web-ui/overview)** - Using the visual interface

## Common Use Cases

### For RAG Applications
```python
# Optimized for RAG pipelines
text = pdfstract.convert('research-paper.pdf', library='docling')
chunks = pdfstract.chunk(text, 
                        chunker='semantic', 
                        chunk_size=512,
                        chunk_overlap=100)

# Chunks are ready for embedding!
for chunk in chunks['chunks']:
    print(f"Chunk {chunk['chunk_id']}: {len(chunk['text'])} chars")
```

### For Document Analysis
```python
# Extract with structure preservation  
text = pdfstract.convert('report.pdf', 
                        library='unstructured',
                        preserve_structure=True)

# Use recursive chunking to maintain context
chunks = pdfstract.chunk(text, chunker='recursive')
```

Ready to dive deeper? Check out the detailed guides for your specific use case! 🚀