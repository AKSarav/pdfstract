---
sidebar_position: 1
---

# CLI Overview

PDFStract provides a powerful command-line interface for PDF extraction and text chunking with support for batch processing, multi-library comparison, and production automation.

## Installation

```bash
# Base - Fast extractors (pymupdf4llm, markitdown)
pip install pdfstract

# Standard - Adds OCR (pytesseract, unstructured)
pip install pdfstract[standard]

# Advanced - ML-powered (marker, docling, paddleocr, deepseek)
pip install pdfstract[advanced]

# All - Everything including chunking
pip install pdfstract[all]
```

## Quick Start

After installation, use PDFStract from the command line:

```bash
# Complete RAG pipeline in one command: Extract + Chunk + Embed
pdfstract convert-chunk-embed document.pdf --library auto --chunker auto --embedding auto

# Convert a single PDF
pdfstract convert document.pdf

# Convert with specific library
pdfstract convert document.pdf --library marker

# Batch process multiple files
pdfstract batch ./pdfs/ --output ./results/
```

:::tip One Command RAG Pipeline
Use `convert-chunk-embed` to extract text, chunk it, and generate embeddings in a single command—ready for your vector database!
:::

## Available Libraries by Tier

| Tier | Libraries Available |
|------|---------------------|
| **Base** | pymupdf4llm, markitdown |
| **Standard** | pytesseract, unstructured |
| **Advanced** | + marker, docling, paddleocr, deepseek |

## Main Commands

### convert

Convert a single PDF to text:

```bash
# Auto mode (selects best available library)
pdfstract convert document.pdf --library auto

# With specific converter
pdfstract convert document.pdf --library docling

# Save to specific file
pdfstract convert document.pdf --library marker --output result.txt

# Convert specific pages
pdfstract convert document.pdf --library auto --pages 1-5,10
```

:::tip Auto Library Selection
Use `--library auto` to automatically select the best available converter based on your installation tier. This makes your commands portable across different environments!
:::

### chunk  

Chunk text using various methods:

```bash
# Auto mode (selects best available chunker)
pdfstract chunk text_file.txt --chunker auto

# With specific chunker
pdfstract chunk text_file.txt --chunker semantic --size 512

# Chunk PDF directly with auto selection
pdfstract chunk document.pdf --chunker auto --overlap 50

# Recursive chunking
pdfstract chunk document.pdf --chunker recursive --overlap 50
```

:::tip Auto Chunker Selection
Use `--chunker auto` to automatically select the best available chunking method. Great for scripts that need to work across different installations!
:::

### convert-chunk

Convert and chunk in one command:

```bash
# One-step processing
pdfstract convert-chunk document.pdf --chunker semantic --chunk-size 1024

# With specific tools
pdfstract convert-chunk document.pdf \
  --library marker \
  --chunker semantic \
  --chunk-size 512 \
  --chunk-overlap 100
```

### convert-chunk-embed

Complete RAG pipeline: convert PDF, chunk text, and generate embeddings:

```bash
# Full pipeline with auto-selection
pdfstract convert-chunk-embed document.pdf

# With specific options
pdfstract convert-chunk-embed document.pdf \
  --library marker \
  --chunker semantic \
  --embedding sentence-transformers \
  --chunk-size 512 \
  --chunk-overlap 50 \
  --output result.json

# Using OpenAI embeddings
pdfstract convert-chunk-embed document.pdf \
  --library docling \
  --chunker token \
  --embedding openai \
  --output chunks_with_vectors.json

# Save converted text separately
pdfstract convert-chunk-embed document.pdf \
  --library marker \
  --embedding sentence-transformers \
  --save-converted converted_text.md
```

**Options:**
- `--library, -l`: PDF conversion library (default: auto)
- `--chunker, -c`: Chunking method (default: auto)
- `--embedding, -e`: Embedding provider (default: auto)
- `--chunk-size`: Target chunk size in tokens (default: 512)
- `--chunk-overlap`: Overlap between chunks (default: 50)
- `--format, -f`: Output format (markdown, text, json)
- `--output, -o`: Save results to JSON file
- `--save-converted`: Save converted text to separate file

**Available Embedding Providers:**
- `sentence-transformers` - Local, no API key needed
- `openai` - Requires `OPENAI_API_KEY`
- `azure-openai` - Requires `AZURE_OPENAI_API_KEY`
- `google-generative` - Requires `GOOGLE_API_KEY`
- `ollama` - Requires local Ollama daemon

### batch

Process multiple files:

```bash
# Basic batch processing
pdfstract batch ./input-folder/ --output ./output-folder/

# With parallel processing
pdfstract batch ./pdfs/ --output ./results/ --parallel 4

# With specific tools
pdfstract batch ./docs/ \
  --converter docling \
  --chunker semantic \
  --size 1024
```

## Performance & Startup Time

### Understanding CLI Startup

PDFStract CLI uses **lazy loading** to keep startup times fast:

| Command | Startup Time | Description |
|---------|--------------|-------------|
| `pdfstract --help` | **< 1s** ⚡ | Only loads Click framework |
| `pdfstract convert --help` | **< 1s** ⚡ | Shows usage without library loading |
| `pdfstract libs` | **8-10s** | Checks all libraries (one-time) |
| `pdfstract convert file.pdf` | **3-8s** | Loads specific library |

The initial delay is due to heavy ML libraries (torch, transformers), not PDFStract itself.

### Optimization Tips

1. **Use fast libraries for quick conversions:**
   ```bash
   pdfstract convert file.pdf --library pymupdf4llm   # Fastest (~3s)
   pdfstract convert file.pdf --library markitdown    # Fast (~4s) 
   pdfstract convert file.pdf --library marker        # Quality (~8s)
   ```

2. **Batch processing amortizes startup cost:**
   ```bash
   # First file: 8s (includes startup)
   # Files 2-100: ~1-2s each (library stays loaded)
   pdfstract batch ./docs --library unstructured --parallel 4
   ```

## Available Libraries

### PDF Converters

List all available converters:

```bash
pdfstract libs
```

Common converters:
- **docling** - Great all-around performance
- **marker** - Excellent for complex layouts  
- **pymupdf4llm** - Fastest for simple documents
- **unstructured** - Best for document structure
- **paddleocr** - Good for scanned documents

### Text Chunkers

- **token** - Simple token-based splitting
- **semantic** - AI-powered semantic chunking
- **recursive** - Smart recursive text splitting
- **sentence** - Sentence-boundary aware
- **code** - Code-aware chunking

### Embedding Providers

List available embedding providers:

```bash
pdfstract embeddings-list
```

- **sentence-transformers** - Local, no API key (default)
- **openai** - OpenAI API
- **azure-openai** - Azure OpenAI
- **google-generative** - Google Gemini
- **ollama** - Local Ollama

## Common Usage Patterns

### Convert Single Document

```bash
# Default conversion
pdfstract convert report.pdf

# High-quality conversion
pdfstract convert report.pdf --library marker --output report.txt

# Fast conversion
pdfstract convert report.pdf --library pymupdf4llm
```

### Batch Processing

```bash
# Process all PDFs in a folder
pdfstract batch ./documents/ --output ./results/

# Parallel processing with 4 workers
pdfstract batch ./pdfs/ --parallel 4 --library docling

# Specific file pattern
pdfstract batch ./reports/ --pattern "*.pdf" --chunker semantic
```

### RAG Pipeline Preparation

```bash
# Convert and chunk for RAG
pdfstract convert-chunk document.pdf \
  --library docling \
  --chunker semantic \
  --chunk-size 512 \
  --chunk-overlap 50 \
  --output chunks.json

# Full pipeline with embeddings
pdfstract convert-chunk-embed document.pdf \
  --library marker \
  --chunker semantic \
  --embedding sentence-transformers \
  --chunk-size 512 \
  --output ready_for_vectordb.json

# Batch process for RAG
pdfstract batch ./knowledge-base/ \
  --library marker \
  --chunker semantic \
  --chunk-size 1024 \
  --format json
```

## Command Reference

### Global Options

```bash
--verbose, -v          # Verbose output
--quiet, -q           # Suppress output
--config CONFIG       # Use config file  
--cache-dir DIR       # Set cache directory
--no-cache           # Disable caching
```

### Convert Options

```bash
--library, -l LIBRARY     # Conversion library
--output, -o FILE         # Output file
--pages PAGES            # Page range (1-5,10)
--preserve-structure     # Keep document structure
--extract-images         # Extract images
--timeout SECONDS        # Conversion timeout
```

### Chunk Options  

```bash
--chunker, -c CHUNKER    # Chunking method
--size, -s SIZE          # Chunk size in tokens
--overlap, -r OVERLAP    # Overlap between chunks
--format FORMAT          # Output format (text/json)
--metadata              # Include chunk metadata
```

### Batch Options

```bash
--output, -o DIR         # Output directory
--parallel, -p WORKERS   # Parallel workers
--pattern PATTERN        # File pattern
--recursive, -R          # Recursive directory scan
--continue-on-error      # Don't stop on errors
--progress              # Show progress bar
```

## Output Formats

### Text Output (Default)

```bash
pdfstract convert document.pdf
# Outputs plain text to stdout or file
```

### JSON Output

```bash
pdfstract process document.pdf --format json --output result.json
```

JSON structure:
```json
{
  "file": "document.pdf",
  "converter": "docling",
  "chunker": "semantic", 
  "chunks": [
    {
      "chunk_id": 0,
      "text": "chunk content...",
      "metadata": {}
    }
  ],
  "total_chunks": 10,
  "processing_time": 5.2
}
```

## Configuration Files

Create a `pdfstract.toml` config file:

```toml
[defaults]
converter = "docling"
chunker = "semantic"
chunk_size = 512
chunk_overlap = 50

[batch]
parallel_workers = 4
continue_on_error = true

[output]
format = "json"
include_metadata = true
```

Use with:
```bash
pdfstract --config pdfstract.toml convert document.pdf
```

## Error Handling

PDFStract provides detailed error messages:

```bash
# Enable verbose output for debugging
pdfstract convert document.pdf --verbose

# Continue processing despite errors (batch mode)
pdfstract batch ./docs/ --continue-on-error

# Set timeout for problematic files
pdfstract convert large.pdf --timeout 300
```

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# Process all PDFs in inbox
for pdf in inbox/*.pdf; do
    echo "Processing $pdf..."
    pdfstract process "$pdf" \
        --converter docling \
        --chunker semantic \
        --output "processed/$(basename "$pdf" .pdf).json"
done
```

### GitHub Actions

```yaml
name: Process Documents
on: [push]
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install pdfstract
      - run: pdfstract batch ./docs --output ./processed
```

## Next Steps

Continue exploring PDFStract:

### Feature Guides
- **[Extract](../features/extract)** - All PDF conversion options
- **[Chunk](../features/chunk)** - Text chunking methods
- **[Embed](../features/embed)** - Embedding providers and configuration

### Interface Guides
- **[Python API](../api/overview)** - Use in your applications
- **[Web UI](../web-ui/overview)** - Visual interface
- **[Installation](../installation)** - Advanced installation options

Need help? Use `pdfstract COMMAND --help` for detailed command information!