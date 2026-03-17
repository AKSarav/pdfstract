---
sidebar_position: 2
---

# Chunk (Text Splitting)

PDFStract provides 10+ chunking methods to split your extracted text into optimal segments for RAG applications. Proper chunking is critical for retrieval quality—too large and you lose precision, too small and you lose context.

## Quick Start

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Extract and chunk in one step
text = pdfstract.convert('document.pdf', library='auto')
chunks = pdfstract.chunk(text, chunker='token', chunk_size=512)

print(f"Created {chunks['total_chunks']} chunks")
```

## Available Chunkers

| Chunker | Description | Best For |
|---------|-------------|----------|
| **token** | Token-based splitting with overlap | General purpose, fast |
| **sentence** | Sentence boundary aware | Preserving complete thoughts |
| **semantic** | AI-powered semantic boundaries | High-quality RAG |
| **recursive** | Hierarchical text splitting | Structured documents |
| **sdpm** | Semantic double-pass merge | Complex documents |
| **late** | Late chunking strategy | Long documents |
| **slumber** | Sliding window chunking | Overlapping context |
| **code** | Code-aware chunking | Source code, technical docs |
| **neural** | Neural network-based | Maximum quality |

## Python API

### Basic Chunking

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Simple token chunking
chunks = pdfstract.chunk(text, chunker='token', chunk_size=512)

# With overlap for context preservation
chunks = pdfstract.chunk(text, chunker='token', chunk_size=512, chunk_overlap=50)

# Semantic chunking for better boundaries
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=1024)
```

### Chunk Result Structure

```python
result = pdfstract.chunk(text, chunker='token', chunk_size=512)

# Result structure
{
    'chunks': [
        {
            'chunk_id': 0,
            'text': 'First chunk content...',
            'start_index': 0,
            'end_index': 512,
            'token_count': 487
        },
        {
            'chunk_id': 1,
            'text': 'Second chunk content...',
            'start_index': 462,
            'end_index': 974,
            'token_count': 502
        }
    ],
    'chunker_name': 'token',
    'total_chunks': 15,
    'total_tokens': 7320
}
```

### Async Chunking

```python
import asyncio
from pdfstract import PDFStract

async def process_text():
    pdfstract = PDFStract()
    result = await pdfstract.chunk_async(text, chunker='semantic')
    return result

chunks = asyncio.run(process_text())
```

### List Available Chunkers

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Get available chunker names
available = pdfstract.list_available_chunkers()
print(f"Available: {available}")

# Get detailed chunker info
chunkers = pdfstract.list_chunkers()
for c in chunkers:
    print(f"{c['name']}: {c['available']}")

# Get specific chunker schema
info = pdfstract.get_chunker_info('semantic')
print(f"Parameters: {info}")
```

## CLI Usage

### Chunk Text File

```bash
# Basic chunking
pdfstract chunk text_file.txt --chunker token --size 512

# With overlap
pdfstract chunk text_file.txt --chunker token --size 512 --overlap 50

# Semantic chunking
pdfstract chunk text_file.txt --chunker semantic --size 1024
```

### Convert and Chunk (Combined)

```bash
# Extract PDF and chunk in one command
pdfstract convert-chunk document.pdf --library marker --chunker semantic

# With custom parameters
pdfstract convert-chunk document.pdf \
  --library docling \
  --chunker token \
  --chunk-size 512 \
  --chunk-overlap 50 \
  --output chunks.json
```

### List Available Chunkers

```bash
pdfstract chunkers
```

## Chunker Details

### Token Chunker

Splits text by token count with configurable overlap. Fast and predictable.

```python
chunks = pdfstract.chunk(text, 
    chunker='token',
    chunk_size=512,      # Target tokens per chunk
    chunk_overlap=50     # Overlap between chunks
)
```

**Parameters:**
- `chunk_size` (int): Target chunk size in tokens (default: 512)
- `chunk_overlap` (int): Number of overlapping tokens (default: 50)

**Best for:** General purpose, when you need predictable chunk sizes.

### Sentence Chunker

Respects sentence boundaries to avoid cutting mid-thought.

```python
chunks = pdfstract.chunk(text,
    chunker='sentence',
    chunk_size=512
)
```

**Parameters:**
- `chunk_size` (int): Maximum tokens per chunk
- `min_sentences` (int): Minimum sentences per chunk (default: 1)

**Best for:** Narrative text, articles, documents where sentence integrity matters.

### Semantic Chunker

Uses AI to identify natural semantic boundaries in text.

```python
chunks = pdfstract.chunk(text,
    chunker='semantic',
    chunk_size=1024
)
```

**Parameters:**
- `chunk_size` (int): Target chunk size
- `similarity_threshold` (float): Threshold for semantic similarity (default: 0.5)

**Best for:** High-quality RAG applications where retrieval precision is critical.

### Recursive Chunker

Hierarchically splits text using multiple separators (paragraphs → sentences → words).

```python
chunks = pdfstract.chunk(text,
    chunker='recursive',
    chunk_size=512,
    separators=['\n\n', '\n', '. ', ' ']
)
```

**Parameters:**
- `chunk_size` (int): Target chunk size
- `separators` (list): Hierarchy of separators to use

**Best for:** Structured documents, technical documentation.

### Code Chunker

Understands code structure—functions, classes, imports.

```python
chunks = pdfstract.chunk(code_text,
    chunker='code',
    language='python'
)
```

**Parameters:**
- `language` (str): Programming language (python, javascript, etc.)
- `chunk_size` (int): Maximum tokens per chunk

**Best for:** Source code, technical documentation with code blocks.

### SDPM Chunker

Semantic Double-Pass Merge—two-pass algorithm for optimal boundaries.

```python
chunks = pdfstract.chunk(text,
    chunker='sdpm',
    chunk_size=1024
)
```

**Best for:** Complex documents requiring high-quality semantic splits.

## Combined Pipelines

### Convert + Chunk

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# One-step convert and chunk
result = pdfstract.convert_chunk(
    'document.pdf',
    library='marker',
    chunker='semantic',
    chunker_params={'chunk_size': 512, 'chunk_overlap': 50}
)

print(f"Extracted: {len(result['extracted_content'])} chars")
print(f"Chunks: {result['chunking_result']['total_chunks']}")
```

### Convert + Chunk + Embed

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Full RAG pipeline
result = pdfstract.convert_chunk_embed(
    'document.pdf',
    library='marker',
    chunker='semantic',
    embedding='sentence-transformers',
    chunker_params={'chunk_size': 512}
)

# Each chunk now has an embedding vector
for chunk in result['chunking_result']['chunks']:
    print(f"Chunk {chunk['chunk_id']}: {len(chunk['embedding'])} dimensions")
```

## Chunking Strategies

### For RAG Applications

```python
# Recommended: Semantic chunking with moderate size
chunks = pdfstract.chunk(text,
    chunker='semantic',
    chunk_size=512,
    chunk_overlap=50
)
```

**Why:** Semantic boundaries improve retrieval relevance. 512 tokens balances context with precision.

### For Long Documents

```python
# Use recursive with larger chunks
chunks = pdfstract.chunk(text,
    chunker='recursive',
    chunk_size=1024,
    chunk_overlap=100
)
```

**Why:** Larger chunks preserve more context. Recursive respects document structure.

### For Code Documentation

```python
# Code-aware chunking
chunks = pdfstract.chunk(text,
    chunker='code',
    language='python',
    chunk_size=512
)
```

**Why:** Keeps functions/classes intact. Understands code structure.

### For Speed

```python
# Fast token chunking
chunks = pdfstract.chunk(text,
    chunker='token',
    chunk_size=512,
    chunk_overlap=50
)
```

**Why:** Token chunking is fastest. Good enough for many use cases.

## Chunk Size Guidelines

| Use Case | Recommended Size | Overlap |
|----------|------------------|---------|
| General RAG | 512 tokens | 50 |
| Detailed Q&A | 256 tokens | 25 |
| Summarization | 1024 tokens | 100 |
| Code search | 512 tokens | 50 |
| Long documents | 1024+ tokens | 100 |

## Error Handling

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

try:
    chunks = pdfstract.chunk(text, chunker='semantic')
except ValueError as e:
    print(f"Chunking error: {e}")
    # Fallback to token chunker
    chunks = pdfstract.chunk(text, chunker='token')
```

## Best Practices

1. **Match chunker to content**: Use semantic for prose, code for source files
2. **Include overlap**: Prevents losing context at boundaries
3. **Test chunk sizes**: Experiment to find optimal size for your retrieval
4. **Use auto mode**: `chunker='auto'` selects best available method
5. **Consider downstream use**: Smaller chunks for precise retrieval, larger for summarization

## Next Steps

- **[Extract](./extract)** - PDF conversion options
- **[Embed](./embed)** - Generate vector embeddings
- **[CLI Guide](../cli/overview)** - Full command reference
- **[Python API](../api/overview)** - Complete API documentation
