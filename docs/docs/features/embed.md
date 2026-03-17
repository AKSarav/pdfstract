---
sidebar_position: 3
---

# Embed (Vector Embeddings)

PDFStract supports multiple embedding providers to convert your text chunks into vector representations for semantic search, RAG pipelines, and vector databases.

## Quick Start

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Embed text with auto-selected provider
vectors = pdfstract.embed_texts(["Hello world", "Another sentence"], model='auto')

# Embed single text
vector = pdfstract.embed_text("Hello world", model='sentence-transformers')
print(f"Embedding dimension: {len(vector)}")
```

## Available Providers

| Provider | Type | Dimensions | Requirements |
|----------|------|------------|--------------|
| **openai** | Cloud API | 1536/3072 | `OPENAI_API_KEY` |
| **azure-openai** | Cloud API | 1536/3072 | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| **google-generative** | Cloud API | 768 | `GOOGLE_API_KEY` |
| **ollama** | Local | Varies | Local Ollama daemon |
| **sentence-transformers** | Local | 384/768 | No API key needed |
| **model2vec** | Local | Varies | Pre-trained vectors file |

## Configuration

### Environment Variables

Set up your preferred providers in your environment or `.env` file:

```bash
# OpenAI
export OPENAI_API_KEY=sk-your-key-here
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Optional

# Azure OpenAI
export AZURE_OPENAI_API_KEY=your-azure-key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # Optional
export AZURE_OPENAI_API_VERSION=2024-02-01  # Optional

# Google Generative AI
export GOOGLE_API_KEY=your-google-key
export GOOGLE_EMBEDDING_MODEL=gemini-embedding-001  # Optional

# Ollama (local)
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=nomic-embed-text  # Optional

# Sentence Transformers
export SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2  # Optional
```

### Provider Selection

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Auto-select best available provider
vectors = pdfstract.embed_texts(texts, model='auto')

# Use specific provider
vectors = pdfstract.embed_texts(texts, model='openai')
vectors = pdfstract.embed_texts(texts, model='sentence-transformers')
vectors = pdfstract.embed_texts(texts, model='ollama')
```

## Python API

### Embed Multiple Texts

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

texts = [
    "First document about machine learning",
    "Second document about natural language processing",
    "Third document about computer vision"
]

# Get embeddings
vectors = pdfstract.embed_texts(texts, model='sentence-transformers')

print(f"Generated {len(vectors)} embeddings")
print(f"Dimension: {len(vectors[0])}")
```

### Embed Single Text

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

text = "This is a sample document for embedding."
vector = pdfstract.embed_text(text, model='openai')

print(f"Embedding dimension: {len(vector)}")
```

### Async Embedding

```python
import asyncio
from pdfstract import PDFStract

async def embed_documents():
    pdfstract = PDFStract()
    
    texts = ["Document 1", "Document 2", "Document 3"]
    vectors = await pdfstract.embed_texts_async(texts, model='openai')
    
    return vectors

vectors = asyncio.run(embed_documents())
```

### List Available Providers

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Get available embedding providers
available = pdfstract.list_available_embeddings()
print(f"Available providers: {available}")
```

## CLI Usage

### Embed Text

```bash
# Embed text from command line
pdfstract embed-text --text "Your text to embed" --model sentence-transformers

# Embed from file
pdfstract embed-text --file document.txt --model openai --output embeddings.json
```

### Full Pipeline: Convert + Chunk + Embed

```bash
# Complete RAG pipeline in one command
pdfstract convert-chunk-embed document.pdf \
  --library marker \
  --chunker semantic \
  --embedding sentence-transformers \
  --chunk-size 512 \
  --output result.json

# With OpenAI embeddings
pdfstract convert-chunk-embed document.pdf \
  --library docling \
  --chunker token \
  --embedding openai \
  --output chunks_with_embeddings.json
```

### List Available Providers

```bash
pdfstract embeddings
```

## Provider Details

### OpenAI

Industry-standard embeddings with excellent quality.

```python
# Requires OPENAI_API_KEY
vectors = pdfstract.embed_texts(texts, model='openai')
```

**Models:**
- `text-embedding-3-small` (1536 dimensions, faster, cheaper)
- `text-embedding-3-large` (3072 dimensions, higher quality)
- `text-embedding-ada-002` (1536 dimensions, legacy)

**Configuration:**
```bash
export OPENAI_API_KEY=sk-your-key
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Optional
```

### Azure OpenAI

Enterprise-grade OpenAI embeddings via Azure.

```python
# Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
vectors = pdfstract.embed_texts(texts, model='azure-openai')
```

**Configuration:**
```bash
export AZURE_OPENAI_API_KEY=your-key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large
export AZURE_OPENAI_API_VERSION=2024-02-01
```

### Google Generative AI

Google's embedding models via Gemini API.

```python
# Requires GOOGLE_API_KEY
vectors = pdfstract.embed_texts(texts, model='google-generative')
```

**Configuration:**
```bash
export GOOGLE_API_KEY=your-google-key
export GOOGLE_EMBEDDING_MODEL=gemini-embedding-001
```

### Ollama (Local)

Run embeddings locally with Ollama.

```python
# Requires local Ollama daemon running
vectors = pdfstract.embed_texts(texts, model='ollama')
```

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Configure
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=nomic-embed-text
```

**Popular Ollama embedding models:**
- `nomic-embed-text` (768 dimensions)
- `mxbai-embed-large` (1024 dimensions)
- `all-minilm` (384 dimensions)

### Sentence Transformers (Local)

Fast, free local embeddings. No API key required.

```python
# No configuration needed
vectors = pdfstract.embed_texts(texts, model='sentence-transformers')
```

**Configuration (optional):**
```bash
export SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2
```

**Popular models:**
- `all-MiniLM-L6-v2` (384 dimensions, fast)
- `all-mpnet-base-v2` (768 dimensions, higher quality)
- `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, multilingual)

### Model2Vec

Use pre-trained word vectors (gensim KeyedVectors format).

```python
# Requires MODEL2VEC_PATH pointing to .kv file
vectors = pdfstract.embed_texts(texts, model='model2vec')
```

**Configuration:**
```bash
export MODEL2VEC_PATH=/path/to/keyed_vectors.kv
```

## Full RAG Pipeline

### Python: Convert + Chunk + Embed

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Complete pipeline in one call
result = pdfstract.convert_chunk_embed(
    'document.pdf',
    library='marker',
    chunker='semantic',
    embedding='sentence-transformers',
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

### Async Pipeline

```python
import asyncio
from pdfstract import PDFStract

async def process_document():
    pdfstract = PDFStract()
    
    result = await pdfstract.convert_chunk_embed_async(
        'document.pdf',
        library='docling',
        chunker='semantic',
        embedding='openai'
    )
    
    return result

result = asyncio.run(process_document())
```

### Store in Vector Database

```python
from pdfstract import PDFStract
import chromadb  # Example: ChromaDB

pdfstract = PDFStract()

# Process document
result = pdfstract.convert_chunk_embed(
    'document.pdf',
    library='marker',
    chunker='semantic',
    embedding='sentence-transformers'
)

# Store in ChromaDB
client = chromadb.Client()
collection = client.create_collection("documents")

for chunk in result['chunking_result']['chunks']:
    collection.add(
        ids=[f"chunk_{chunk['chunk_id']}"],
        embeddings=[chunk['embedding']],
        documents=[chunk['text']],
        metadatas=[{'source': 'document.pdf', 'chunk_id': chunk['chunk_id']}]
    )

# Query
results = collection.query(
    query_embeddings=[pdfstract.embed_text("What is machine learning?")],
    n_results=5
)
```

## Embedding Comparison

| Provider | Speed | Quality | Cost | Privacy |
|----------|-------|---------|------|---------|
| **OpenAI** | Fast | Excellent | $$$ | Cloud |
| **Azure OpenAI** | Fast | Excellent | $$$ | Cloud (Enterprise) |
| **Google** | Fast | Very Good | $$ | Cloud |
| **Ollama** | Medium | Good | Free | Local |
| **Sentence Transformers** | Fast | Good | Free | Local |

## Error Handling

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

try:
    vectors = pdfstract.embed_texts(texts, model='openai')
except ValueError as e:
    if "OPENAI_API_KEY" in str(e):
        print("OpenAI API key not set, falling back to local model")
        vectors = pdfstract.embed_texts(texts, model='sentence-transformers')
    else:
        raise
```

## Best Practices

1. **Use local models for development**: Sentence Transformers is free and fast
2. **Use cloud models for production**: OpenAI/Azure for best quality
3. **Batch your embeddings**: More efficient than one-at-a-time
4. **Match embedding model to retrieval**: Use same model for queries and documents
5. **Consider privacy**: Use local models for sensitive data

## Dimension Guidelines

| Use Case | Recommended Dimensions |
|----------|----------------------|
| Quick prototyping | 384 (MiniLM) |
| Production RAG | 768-1536 |
| Maximum quality | 3072 (text-embedding-3-large) |

## Next Steps

- **[Extract](./extract)** - PDF conversion options
- **[Chunk](./chunk)** - Text chunking methods
- **[CLI Guide](../cli/overview)** - Full command reference
- **[Python API](../api/overview)** - Complete API documentation
