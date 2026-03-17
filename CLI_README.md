# PDFStract

**The Data Preparation Layer for RAG** — Extract. Chunk. Embed.

[![PyPI](https://img.shields.io/pypi/v/pdfstract)](https://pypi.org/project/pdfstract/)
[![Python](https://img.shields.io/pypi/pyversions/pdfstract)](https://pypi.org/project/pdfstract/)
[![License](https://img.shields.io/github/license/AKSarav/pdfstract)](https://github.com/AKSarav/pdfstract/blob/main/LICENSE)

**One unified API.** Switch between 10+ extraction libraries, 10+ chunking methods, and multiple embedding providers with a single parameter change. Focus on your RAG outcomes, not library dependencies.

## Installation

```bash
pip install pdfstract              # Base - pymupdf4llm, markitdown
pip install pdfstract[standard]    # + OCR (pytesseract, unstructured)
pip install pdfstract[advanced]    # + ML-powered (marker, docling, paddleocr)
pip install pdfstract[all]         # Everything
```

## Python API

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Extract
text = pdfstract.convert('document.pdf', library='auto')

# Chunk
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=512)

# Embed
vectors = pdfstract.embed_texts([c['text'] for c in chunks['chunks']])

# Combined pipelines
result = pdfstract.convert_chunk('document.pdf', library='marker', chunker='token')
result = pdfstract.convert_chunk_embed('document.pdf', embedding='sentence-transformers')
```

### Extract Examples

```python
# Auto-select best available library
text = pdfstract.convert('document.pdf', library='auto')

# Use specific library
text = pdfstract.convert('document.pdf', library='marker')
text = pdfstract.convert('document.pdf', library='docling', output_format='json')

# Batch processing
results = pdfstract.batch_convert('./pdfs', library='pymupdf4llm', parallel_workers=4)

# Async
text = await pdfstract.convert_async('document.pdf', library='marker')
```

### Chunk Examples

```python
# Token-based chunking
chunks = pdfstract.chunk(text, chunker='token', chunk_size=512, chunk_overlap=50)

# Semantic chunking
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=1024)

# Code-aware chunking
chunks = pdfstract.chunk(code_text, chunker='code')

# Access results
for chunk in chunks['chunks']:
    print(f"Chunk {chunk['chunk_id']}: {chunk['token_count']} tokens")
```

### Embed Examples

```python
# Embed multiple texts
vectors = pdfstract.embed_texts(["First text", "Second text"], model='sentence-transformers')

# Embed single text
vector = pdfstract.embed_text("Hello world", model='openai')

# List available providers
providers = pdfstract.list_available_embeddings()
```

## CLI

```bash
pdfstract convert document.pdf --library marker
pdfstract convert-chunk document.pdf --chunker semantic
pdfstract convert-chunk-embed document.pdf --embedding sentence-transformers
pdfstract batch ./pdfs --parallel 4
```

## What's Included

| Tier | Libraries |
|------|-----------|
| **Base** | pymupdf4llm, markitdown |
| **Standard** | + pytesseract, unstructured |
| **Advanced** | + marker, docling, paddleocr, deepseek |

**Chunkers:** token, sentence, semantic, recursive, code, and more

**Embeddings:** OpenAI, Azure, Google, Ollama, Sentence Transformers

## Documentation

📖 **[pdfstract.com](https://pdfstract.com)** — Full docs, guides, and API reference

**GitHub:** [github.com/aksarav/pdfstract](https://github.com/aksarav/pdfstract) · [Issues](https://github.com/aksarav/pdfstract/issues) · [MIT License](https://github.com/aksarav/pdfstract/blob/main/LICENSE)
