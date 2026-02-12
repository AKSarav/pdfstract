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
# Check version
pdfstract --version

# Get help
pdfstract --help

# Convert a single PDF
pdfstract convert document.pdf

# Convert with specific library
pdfstract convert document.pdf --library marker

# Batch process multiple files
pdfstract batch ./pdfs/ --output ./results/
```

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
# Basic conversion
pdfstract convert document.pdf

# With specific converter
pdfstract convert document.pdf --library docling

# Save to specific file
pdfstract convert document.pdf --output result.txt

# Convert specific pages
pdfstract convert document.pdf --pages 1-5,10
```

### chunk  

Chunk text using various methods:

```bash
# Chunk a text file
pdfstract chunk text_file.txt

# With specific chunker
pdfstract chunk text_file.txt --chunker semantic --size 512

# Chunk PDF directly
pdfstract chunk document.pdf --chunker recursive --overlap 50
```

### process

Convert and chunk in one command:

```bash
# One-step processing
pdfstract process document.pdf --chunker semantic --size 1024

# With specific tools
pdfstract process document.pdf \
  --converter marker \
  --chunker semantic \
  --size 512 \
  --overlap 100
```

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
pdfstract process document.pdf \
  --converter docling \
  --chunker semantic \
  --size 512 \
  --overlap 50 \
  --output chunks.json

# Batch process for RAG
pdfstract batch ./knowledge-base/ \
  --converter marker \
  --chunker semantic \
  --size 1024 \
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

- **[Python Module](../api/overview)** - Use in your applications
- **[Web UI](../web-ui/overview)** - Visual interface
- **[Installation](../installation)** - Advanced installation options

Need help? Use `pdfstract COMMAND --help` for detailed command information!