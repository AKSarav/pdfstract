---
sidebar_position: 1
---

# Python API Overview

The PDFStract Python API provides a powerful and flexible interface for converting PDFs and chunking text. This guide covers the main classes and methods.

## Core Class: PDFStract

The main entry point for all PDFStract operations:

```python
from pdfstract import PDFStract

# Initialize with default settings
pdfstract = PDFStract()

# Or with custom configuration
pdfstract = PDFStract(
    default_converter='marker',
    default_chunker='semantic',
    cache_dir='./cache',
    max_workers=4
)
```

## Quick Start Example

```python
from pdfstract import PDFStract

# Initialize
pdfstract = PDFStract()

# Convert PDF to text
text = pdfstract.convert('document.pdf', library='docling')

# Chunk the text
chunks = pdfstract.chunk(text, 
                        chunker='semantic',
                        chunk_size=512,
                        chunk_overlap=50)

print(f"Converted PDF to {chunks['total_chunks']} chunks")
```

## Main Methods

### convert()

Convert PDFs to text using various libraries:

```python
# Basic conversion
text = pdfstract.convert('document.pdf')

# With specific library
text = pdfstract.convert('document.pdf', library='marker')

# With options
text = pdfstract.convert('document.pdf',
                        library='unstructured',
                        preserve_structure=True,
                        extract_images=False)
```

**Parameters:**
- `file_path` (str): Path to PDF file
- `library` (str): Conversion library ('docling', 'marker', 'pymupdf4llm', etc.)
- `preserve_structure` (bool): Keep document structure
- `extract_images` (bool): Extract embedded images
- `pages` (list): Specific pages to convert
- `**kwargs`: Library-specific options

**Returns:** Extracted text as string

### chunk()

Split text into chunks for RAG applications:

```python
# Basic chunking
chunks = pdfstract.chunk(text)

# Semantic chunking
chunks = pdfstract.chunk(text, 
                        chunker='semantic',
                        chunk_size=1024,
                        chunk_overlap=100)

# Code-aware chunking
chunks = pdfstract.chunk(code_text,
                        chunker='code',
                        language='python')
```

**Parameters:**
- `text` (str): Text to chunk
- `chunker` (str): Chunking method ('token', 'semantic', 'recursive', etc.)
- `chunk_size` (int): Target chunk size in tokens
- `chunk_overlap` (int): Overlap between chunks
- `**kwargs`: Chunker-specific options

**Returns:** Dictionary with chunk information:
```python
{
    'chunks': [
        {
            'chunk_id': 0,
            'text': 'chunk content...',
            'start_pos': 0,
            'end_pos': 512,
            'metadata': {}
        }
    ],
    'total_chunks': 10,
    'total_tokens': 5120,
    'chunker_info': {
        'method': 'semantic',
        'chunk_size': 512,
        'overlap': 50
    }
}
```

### process()

Combined convert and chunk operation:

```python
# One-step processing
result = pdfstract.process('document.pdf',
                          converter='docling',
                          chunker='semantic',
                          chunk_size=512)

print(f"Processed: {result['total_chunks']} chunks")
```

## Utility Methods

### List Available Tools

```python
# List conversion libraries
converters = pdfstract.list_converters()
print("Available converters:", converters)

# List chunking methods  
chunkers = pdfstract.list_chunkers()
print("Available chunkers:", chunkers)
```

### Get Tool Information

```python
# Get converter details
info = pdfstract.get_converter_info('marker')
print(f"Marker info: {info}")

# Get chunker details
info = pdfstract.get_chunker_info('semantic')
print(f"Semantic chunker: {info}")
```

## Convenience Functions

PDFStract also provides standalone functions for quick operations:

### PDF Conversion Functions

```python
from pdfstract import (
    convert_with_docling,
    convert_with_marker, 
    convert_with_pymupdf4llm,
    convert_with_unstructured
)

# Use specific converters directly
text = convert_with_marker('document.pdf')
text = convert_with_docling('document.pdf', extract_images=True)
```

### Chunking Functions

```python
from pdfstract import (
    chunk_by_tokens,
    chunk_semantically,
    chunk_recursively,
    chunk_by_sentences
)

# Use specific chunkers directly
chunks = chunk_semantically(text, chunk_size=512)
chunks = chunk_by_tokens(text, chunk_size=1024, overlap=100)
```

## Error Handling

PDFStract provides detailed error information:

```python
from pdfstract import PDFStract, PDFStrACtError

pdfstract = PDFStract()

try:
    text = pdfstract.convert('document.pdf', library='marker')
except PDFStrACtError as e:
    print(f"Conversion failed: {e}")
    print(f"Error type: {e.error_type}")
    print(f"Details: {e.details}")
```

## Configuration

### Global Configuration

```python
from pdfstract import PDFStract, set_global_config

# Set global defaults
set_global_config(
    default_converter='docling',
    default_chunker='semantic',
    cache_enabled=True,
    max_workers=6
)

# All instances will use these defaults
pdfstract = PDFStract()
```

### Instance Configuration

```python
# Configure specific instance
pdfstract = PDFStract(
    default_converter='marker',
    default_chunker='recursive', 
    cache_dir='./my-cache',
    max_workers=2,
    timeout=300
)
```

## Advanced Usage

### Batch Processing

```python
import os
from pdfstract import PDFStract

pdfstract = PDFStract()

# Process multiple files
pdf_files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']

for pdf_file in pdf_files:
    try:
        result = pdfstract.process(pdf_file, 
                                  chunker='semantic',
                                  chunk_size=512)
        
        # Save results
        output_file = f"chunks_{os.path.basename(pdf_file)}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        print(f"Failed to process {pdf_file}: {e}")
```

### Custom Preprocessing

```python
def preprocess_text(text):
    """Custom text preprocessing"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers
    text = re.sub(r'Page \d+', '', text)
    return text.strip()

# Apply preprocessing
text = pdfstract.convert('document.pdf')
text = preprocess_text(text)
chunks = pdfstract.chunk(text, chunker='semantic')
```

## Next Steps

Explore specific components:

- **[PDF Conversion](pdf-conversion)** - Detailed converter guide
- **[Text Chunking](text-chunking)** - Complete chunking reference
- **[Error Handling](error-handling)** - Robust error management
- **[Performance](performance)** - Optimization techniques
- **[Examples](examples)** - Real-world use cases
- **[Configuration](configuration)** - Advanced configuration

Ready to integrate PDFStract into your application? Check out our [examples](examples) and [best practices](../guides/best-practices)!