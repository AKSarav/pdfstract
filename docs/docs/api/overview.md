---
sidebar_position: 1
---

# Python Module Overview

The PDFStract Python Module provides a powerful and flexible interface for converting PDFs and chunking text. This guide covers the main classes and methods.

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
# Auto mode (selects best available library)
text = pdfstract.convert('document.pdf', library='auto')

# Explicit library selection
text = pdfstract.convert('document.pdf', library='marker')

# With options
text = pdfstract.convert('document.pdf',
                        library='unstructured',
                        preserve_structure=True,
                        extract_images=False)
```

**Parameters:**
- `file_path` (str): Path to PDF file
- `library` (str, **required**): Conversion library ('auto', 'docling', 'marker', 'pymupdf4llm', etc.)
  - Use `library='auto'` to automatically select the best available library
- `preserve_structure` (bool): Keep document structure
- `extract_images` (bool): Extract embedded images
- `pages` (list): Specific pages to convert
- `**kwargs`: Library-specific options

**Returns:** Extracted text as string

:::info Auto Selection Priority
When using `library='auto'`, libraries are selected in this order:
1. pymupdf4llm (fastest)
2. markitdown (balanced)
3. marker (high quality)
4. docling (document intelligence)
5. paddleocr, unstructured, pytesseract (if installed)
:::

### chunk()

Split text into chunks for RAG applications:

```python
# Auto mode (selects best available chunker)
chunks = pdfstract.chunk(text, chunker='auto')

# Explicit chunker selection
chunks = pdfstract.chunk(text, chunker='semantic')

# With full options
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
- `chunker` (str, **required**): Chunking method ('auto', 'token', 'semantic', 'recursive', etc.)
  - Use `chunker='auto'` to automatically select the best available chunker
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

### embed_text() / embed_texts()

Generate vector embeddings for text using pluggable providers.

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Embed multiple texts
vectors = pdfstract.embed_texts(["First sentence.", "Second sentence."], model='auto')
print(f"Dimension: {len(vectors[0])}")

# Embed single text
vector = pdfstract.embed_text("Hello world", model='sentence-transformers')
```

**Parameters:**
- `text` / `texts` (str / List[str]): Text(s) to embed
- `model` (str): Provider name or `'auto'` to select best available

**Available Providers:**

| Provider | Dimensions | Requirements |
|----------|------------|--------------|
| `openai` | 1536/3072 | `OPENAI_API_KEY` |
| `azure-openai` | 1536/3072 | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| `google-generative` | 768 | `GOOGLE_API_KEY` |
| `ollama` | Varies | Local Ollama daemon |
| `sentence-transformers` | 384/768 | No API key needed |
| `model2vec` | Varies | `MODEL2VEC_PATH` |

**Returns:** List of float vectors (one per input text)

:::tip Local Embeddings
Use `model='sentence-transformers'` for free, local embeddings with no setup required!
:::

### list_available_embeddings()

List available embedding providers:

```python
available = pdfstract.list_available_embeddings()
print(f"Available: {available}")
```

### convert_chunk_embed()

Complete RAG pipeline: convert PDF, chunk text, and generate embeddings in one call.

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

result = pdfstract.convert_chunk_embed(
    'document.pdf',
    library='marker',           # PDF converter
    chunker='semantic',         # Chunking method
    embedding='sentence-transformers',  # Embedding provider
    output_format='markdown',
    chunker_params={'chunk_size': 512, 'chunk_overlap': 50}
)

# Access results
print(f"Extracted: {len(result['extracted_content'])} chars")
print(f"Chunks: {result['chunking_result']['total_chunks']}")
print(f"Embeddings: {len(result['embeddings'])} vectors")

# Each chunk has its embedding attached
for chunk in result['chunking_result']['chunks']:
    print(f"Chunk {chunk['chunk_id']}: {len(chunk['embedding'])} dims")
```

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `library` (str): Extraction library ('auto', 'marker', 'docling', etc.)
- `chunker` (str): Chunking method ('auto', 'token', 'semantic', etc.)
- `embedding` (str): Embedding provider ('auto', 'openai', 'sentence-transformers', etc.)
- `output_format` (str): Output format for extraction (default: 'markdown')
- `chunker_params` (dict): Optional chunker parameters (chunk_size, chunk_overlap, etc.)

**Returns:** Dictionary with:
- `extracted_content`: Raw extracted text
- `chunking_result`: Chunking results with chunks list
- `embeddings`: List of embedding vectors

### Async Variants

All embedding methods have async variants:

```python
import asyncio

async def process():
    pdfstract = PDFStract()
    
    # Async embedding
    vectors = await pdfstract.embed_texts_async(texts, model='openai')
    
    # Async full pipeline
    result = await pdfstract.convert_chunk_embed_async(
        'document.pdf',
        library='marker',
        chunker='semantic',
        embedding='openai'
    )
    
    return result

result = asyncio.run(process())
```

Use a single `PDFStract()` instance for all operations. Instantiate once and reuse.

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

Continue exploring PDFStract:

### Feature Guides
- **[Extract](../features/extract)** - All PDF conversion options
- **[Chunk](../features/chunk)** - Text chunking methods
- **[Embed](../features/embed)** - Embedding providers and configuration

### Interface Guides
- **[Quick Start](../quick-start)** - Get started quickly
- **[CLI Guide](../cli/overview)** - Command-line interface
- **[Web UI](../web-ui/overview)** - Visual interface

Ready to integrate PDFStract into your application? Explore the API methods above!