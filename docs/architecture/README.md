# PDFStract Architecture Documentation

## Overview

PDFStract is a unified, production-grade platform for **PDF extraction, conversion, text chunking, and embedding**. It provides three entry points — **CLI**, **Web API**, and **Python Library** — all backed by a sophisticated factory-based architecture supporting 25+ implementations across three core layers: **Converters**, **Chunkers**, and **Embeddings**.

### Key Architectural Principles

- **Factory Pattern:** Lazy-loading implementations with on-demand module imports and credential validation
- **Async-First:** Dual sync/async APIs using asyncio with graceful Jupyter notebook support
- **Extensible:** Plugin architecture for adding new converters, chunkers, and embedding providers
- **Type-Safe:** Comprehensive dataclasses and type hints for all public APIs
- **Observable:** Loguru-based logging with structured output and database persistence

---

## Architecture Diagrams (C4 Model)

### Level 3: Component Diagram

#### [01 — System Context & Components](01-system-context-components.mmd)

**Shows:** Users, entry points (CLI/Web/Library), three service factories, 25+ implementations, support services, and external system integrations.

**Key Elements:**
- **Users:** CLI operators, Web UI consumers, Python developers
- **Entry Points:** Click CLI, FastAPI Web, PDFStract Library class
- **Factories:** ConverterFactory (9 implementations), ChunkerFactory (10 implementations), EmbeddingsFactory (6 providers)
- **Converters:** PyMuPDF4LLM, Marker, Docling, PaddleOCR, DeepSeekOCR, Pytesseract, Unstructured, MarkItDown, MinerU
- **Chunkers:** Token, Sentence, Recursive, Semantic, Code, Table, Late, Neural, Fast, Slumber
- **Embeddings:** OpenAI, Azure OpenAI, Google, Ollama, Sentence-Transformers, Model2Vec
- **External Systems:** PDF files, OCR engines, LLM APIs, Model caches, SQLite
- **Support Services:** Database, Queue Manager, Results Manager, Logger

**Use This Diagram When:** Explaining the system to stakeholders, understanding how components communicate, or planning integrations.

---

### Level 4: Class Diagrams

#### [02 — Converter Layer Classes](02-converter-layer-classes.mmd)

**Shows:** `PDFConverter` abstract base, 9 concrete converter implementations, enums, and factory classes.

**Key Classes:**
- `PDFConverter` (abstract): Base interface for all PDF extraction strategies
- **Converters:**
  - `PyMuPDF4LLMConverter` — Fast non-ML extraction
  - `MarkerConverter` — High-quality layout-aware extraction
  - `DoclingConverter` — ML-powered structure detection
  - `PaddleOCRConverter` — OCR for scanned documents
  - `DeepSeekOCRConverter` — Advanced multilingual OCR
  - `PytesseractConverter` — Lightweight OCR wrapper
  - `UnstructuredConverter` — Multi-format extraction
  - `MarkItDownConverter` — Fast markdown conversion
  - `MinerUConverter` — CLI-based offline extraction
- `OutputFormat` (enum): MARKDOWN, JSON, PYMUPDF, TEXT
- `DownloadStatus` (enum): SUCCESS, FAILED, PARTIAL
- `CLILazyFactory` — CLI-optimized converter factory (lazy-loads on first call)
- `OCRFactory` — Specialized factory for OCR-based converters with batch model preparation

**Use This Diagram When:** Implementing new converters, understanding converter inheritance, or debugging conversion failures.

---

#### [03 — Chunker Layer Classes](03-chunker-layer-classes.mmd)

**Shows:** `BaseChunker` abstract base, 10 concrete chunker implementations, result dataclasses, and chunker factory.

**Key Classes:**
- `BaseChunker` (abstract): Base interface for all text chunking strategies
- **Dataclasses:**
  - `Chunk` — Individual text segment with metadata (text, start/end indices, token count, metadata dict)
  - `ChunkingResult` — Aggregated result with chunks, statistics, and parameters
- **Chunkers:**
  - `TokenChunkerWrapper` — Fixed-size token-based splitting
  - `SentenceChunkerWrapper` — Respects sentence boundaries
  - `RecursiveChunkerWrapper` — Hierarchical recursive splitting
  - `SemanticChunkerWrapper` — Similarity-based splitting with embeddings
  - `CodeChunkerWrapper` — AST-aware code chunking
  - `TableChunkerWrapper` — Markdown table extraction
  - `LateChunkerWrapper` — ColBERT-based retrieval chunking
  - `NeuralChunkerWrapper` — Neural boundary detection
  - `FastChunkerWrapper` — Regex-based splitting
  - `SlumberChunkerWrapper` — LLM-powered intelligent chunking
- `ChunkerFactory` — Central factory managing all chunker implementations
- `ChunkerType` (enum): TOKEN, FAST, SENTENCE, RECURSIVE, SEMANTIC, CODE, TABLE, LATE, NEURAL, SLUMBER

**Use This Diagram When:** Designing chunking pipelines, selecting chunk strategies, or understanding result structures.

---

#### [04 — Embedding Layer Classes](04-embedding-layer-classes.mmd)

**Shows:** `BaseEmbeddingsWrapper` abstract base, 6 concrete provider wrappers, result dataclasses, and embeddings factory.

**Key Classes:**
- `BaseEmbeddingsWrapper` (abstract): Base interface for all embedding providers
- **Dataclasses:**
  - `EmbeddingResult` — Individual embedding with vector, model name, and dimension
  - `EmbeddingsConfig` (interface) — Configuration protocol for credentials and settings
- **Provider Wrappers:**
  - `OpenAIEmbeddingsWrapper` — text-embedding-3-small/large with async support
  - `AzureOpenAIEmbeddingsWrapper` — Enterprise Azure endpoints
  - `GoogleEmbeddingsWrapper` — Gemini embedding models
  - `OllamaEmbeddingsWrapper` — Local Ollama models
  - `SentenceTransformersEmbeddingsWrapper` — Lightweight local transformers
  - `Model2VecEmbeddingsWrapper` — Gensim-based Model2Vec
- `EmbeddingsFactory` — Central factory managing all embedding providers
- `EmbeddingProvider` (enum): OPENAI, AZURE_OPENAI, GOOGLE, OLLAMA, SENTENCE_TRANSFORMERS, MODEL2VEC

**Use This Diagram When:** Integrating embedding providers, selecting models, or handling vector results.

---

## Architectural Patterns

#### [05 — Factory Pattern Architecture](05-factory-pattern-architecture.mmd)

**Shows:** How the three factories implement lazy-loading, dependency injection, dynamic imports, and caching.

**Key Mechanisms:**
1. **Registry:** Static mapping of provider name → module path + class name
2. **Lazy Loading:** `importlib.import_module()` loads only on first request
3. **Singleton Cache:** Instances are cached per provider (thread-safe with lock)
4. **Dynamic Import:** Uses `__import__()` and `getattr()` for runtime instantiation
5. **Dependency Injection:** Injects API keys, device selection, model paths at instantiation
6. **Credential Validation:** Runtime checks for API keys and configuration completeness
7. **Graceful Fallback:** Missing optional dependencies marked as unavailable; no hard failures

**Benefits:**
- Small startup time (modules loaded on-demand)
- Memory efficient (unused providers not loaded)
- Easy extensibility (add provider without modifying core)
- Clean error messages (if provider unavailable, lists alternatives)

**Use This Diagram When:** Adding new providers, understanding initialization flow, or debugging "provider not found" errors.

---

## Data & Control Flow

#### [06 — Data Flow](06-data-flow.mmd)

**Shows:** Request journey from entry points → factories → external systems → response.

**Flow Phases:**
1. **Entry:** CLI command, Web endpoint, or Library method invocation
2. **Validation:** Verify PDF path, validate configuration parameters
3. **Conversion:** Factory loads converter → reads PDF → extracts text
4. **Chunking:** Factory loads chunker → segments text → generates chunks
5. **Embedding:** Factory loads wrapper → calls LLM/local model → stores vectors
6. **Support:** Queue manager parallelizes work; results manager saves to disk; logger records all activity

**Orthogonal Flows:**
- Database write (metadata persistence)
- Queue distribution (parallel processing)
- Results persistence (`~/.pdfstract/results/<task_id>/`)
- Structured logging (`~/.pdfstract/logs/`)

**Use This Diagram When:** Tracing a full request lifecycle, understanding parallelization, or planning performance optimizations.

---

#### [07 — Interaction Sequence](07-interaction-sequence.mmd)

**Shows:** Temporal, message-based interaction between components during a typical workflow.

**Sequence:**
1. User invokes `convert(pdf, converter, chunker, provider)` (CLI/Web/Library)
2. Validator checks inputs
3. **Converter Factory** retrieves/caches converter
4. **Converter** reads PDF, calls OCR if needed, extracts text
5. **Chunker Factory** retrieves/caches chunker
6. **Chunker** segments text into chunks
7. **Embeddings Factory** retrieves/caches embedding wrapper
8. **Embedding Wrapper** batches chunks, calls external API or local model
9. **Result Formatter** assembles final response
10. User receives `ChunkingResult` with metadata, chunks, and embeddings

**Key Insights:**
- Factory calls are cached (fast on repeat calls)
- Each layer is independent (swappable implementations)
- External calls (PDF read, OCR, LLM) are isolated
- Batch processing improves throughput

**Use This Diagram When:** Understanding API contracts, adding instrumentation, or debugging request failures.

---

## Module Structure

```
pdfstract/
├── api.py                           # Main library API (sync + async methods)
├── cli.py                           # Click CLI (convert, chunk, embed commands)
├── main.py                          # FastAPI web server
│
services/
├── base.py                          # BaseFactory, BaseConfigure mixins
├── logger.py                        # Loguru setup
├── db_service.py                    # SQLite persistence
├── queue_manager.py                 # Thread pool / parallelization
├── results_manager.py               # File-based result storage
│
├── converters/
│   ├── base.py                      # PDFConverter abstract base
│   ├── pymupdf4llm.py               # PyMuPDF4LLMConverter
│   ├── marker.py                    # MarkerConverter
│   ├── docling.py                   # DoclingConverter
│   ├── paddleocr.py                 # PaddleOCRConverter
│   ├── deepseek_ocr.py              # DeepSeekOCRConverter
│   ├── pytesseract.py               # PytesseractConverter
│   ├── unstructured.py              # UnstructuredConverter
│   ├── markitdown.py                # MarkItDownConverter
│   ├── mineru.py                    # MinerUConverter
│   └── __init__.py                  # Converter exports
├── cli_factory.py                   # CLILazyFactory (converter factory)
├── ocrfactory.py                    # OCRFactory (OCR-specific)
│
├── chunkers/
│   ├── base.py                      # BaseChunker abstract base
│   ├── token_chunker.py             # TokenChunkerWrapper
│   ├── sentence_chunker.py          # SentenceChunkerWrapper
│   ├── recursive_chunker.py         # RecursiveChunkerWrapper
│   ├── semantic_chunker.py          # SemanticChunkerWrapper
│   ├── code_chunker.py              # CodeChunkerWrapper
│   ├── table_chunker.py             # TableChunkerWrapper
│   ├── late_chunker.py              # LateChunkerWrapper
│   ├── neural_chunker.py            # NeuralChunkerWrapper
│   ├── fast_chunker.py              # FastChunkerWrapper
│   ├── slumber_chunker.py           # SlumberChunkerWrapper
│   └── __init__.py                  # Chunker exports
├── chunker_factory.py               # ChunkerFactory
│
├── embeddings_wrappers/
│   ├── base.py                      # BaseEmbeddingsWrapper abstract base
│   ├── openai.py                    # OpenAIEmbeddingsWrapper
│   ├── azure_openai.py              # AzureOpenAIEmbeddingsWrapper
│   ├── google.py                    # GoogleEmbeddingsWrapper
│   ├── ollama.py                    # OllamaEmbeddingsWrapper
│   ├── sentence_transformers.py     # SentenceTransformersEmbeddingsWrapper
│   ├── model2vec.py                 # Model2VecEmbeddingsWrapper
│   └── __init__.py                  # Wrapper exports
└── embeddings_factory.py            # EmbeddingsFactory

tests/
├── test_cli.py                      # CLI command tests
├── test_cli_embeddings.py           # Embedding CLI tests
└── test_embeddings_wrappers.py      # Wrapper unit tests
```

---

## Technology Stack

### Core
- **Language:** Python 3.10+
- **Package Manager:** Poetry
- **Web Framework:** FastAPI (async-first)
- **CLI Framework:** Click
- **Async Runtime:** asyncio

### PDF Converters
- `pymupdf4llm` — Fast text extraction
- `marker` — Marker (ML-powered)
- `docling` — Docling (document intelligence)
- `paddleocr` — PaddleOCR (OCR)
- `deepseek-ocr` — DeepSeek (advanced OCR)
- `pytesseract` — Tesseract (simple OCR)
- `unstructured` — Unstructured I/O flexible extraction
- `markitdown` — MarkItDown (markdown conversion)
- Refer to CLI_README.md for `mineru`

### Text Chunkers
- Built-in tokenizers (tiktoken, transformers)
- `semantic-chunker` — Semantic chunking library
- `tree-sitter` — Code AST parsing
- `lingpy` —  Boundary detection

### Embeddings
- `openai` — OpenAI API
- `azure-ai-openai` — Azure endpoints
- `google-generative-ai` — Google Gemini
- `sentence-transformers` — Lightweight local
- `gensim` — Model2Vec embeddings
- `requests` — HTTP client for Ollama

### Data & Logging
- `sqlite3` — Standard SQLite
- `loguru` — Structured logging
- `sqlalchemy` — ORM (future expansion)

---

## Entry Points

### CLI (`cli.py`)
```bash
pdfstract convert <pdf> --converter marker --chunker semantic
pdfstract chunkers
pdfstract chunk "Your text here" --chunker token --chunk-size 512
pdfstract embeddings
pdfstract embed "Your text" --embedding openai
```

### Web API (`main.py`)
```
GET    /health                            # Health check
POST   /convert                           # Convert PDF
GET    /libraries                         # List converter info
POST   /download                          # Pre-download models
GET    /chunkers                          # List chunker info
POST   /chunk                             # Chunk text
GET    /embeddings                        # List embedding providers
POST   /embedding                         # Embed text
```

### Library (`pdfstract/api.py`)
```python
from pdfstract import PDFStract

pdf = PDFStract()
result = pdf.convert("document.pdf", converter="marker")
chunks = pdf.chunk(result, chunker="semantic")
embeddings = pdf.embed_text("chunk text", provider="openai")
```

---

## Configuration & Credentials

All configuration is environment-variable driven for security:

```bash
# Converters
export DOCLING_API_KEY=<key>           # if using remote Docling
export PADDLE_OCR_LANG=en              # PaddleOCR language

# Embeddings
export OPENAI_API_KEY=<key>
export AZURE_OPENAI_API_KEY=<key>
export AZURE_OPENAI_ENDPOINT=<url>
export GOOGLE_API_KEY=<key>
export OLLAMA_BASE_URL=http://localhost:11434

# Logging
export LOG_LEVEL=INFO
export LOG_DIR=~/.pdfstract/logs
```

---

## Design Patterns

### 1. **Factory Pattern (Lazy-Loading)**
Every factory (Converter, Chunker, Embeddings) uses lazy-loading:
- Modules imported on first request
- Instances cached per provider
- Graceful fallback if unavailable
- Metadata available without loading module

### 2. **Strategy Pattern**
Each layer (conversion, chunking, embedding) defines a strategy interface:
- `PDFConverter` — extraction strategies
- `BaseChunker` — chunking strategies
- `BaseEmbeddingsWrapper` — embedding strategies

### 3. **Adapter Pattern**
Provider wrappers adapt third-party libraries to unified interfaces:
- `OpenAIEmbeddingsWrapper` adapts OpenAI SDK
- `SentenceTransformersEmbeddingsWrapper` adapts HF models

### 4. **Async/Sync Dual API**
Core operations support both:
- `convert()` / `convert_async()`
- `embed()` / `embed_async()`
- Useful for CLI (sync) and async web servers

### 5. **Pipeline Pattern**
Conversion → Chunking → Embedding as pluggable pipeline:
- Each stage can be replaced independently
- Conditional: embedding may not be requested
- Future: streaming chunk output

---

## Performance Considerations

### Initialization (Cold Start)
- **No embedding provider loaded** = ~100ms startup
- **One provider lazy-loaded** = ~500ms–2s (depends on provider)
- **Converter + chunker + embedding** = ~5–10s total (on first call)
- **Cached instances** = <1ms on subsequent calls

### Processing (One PDF)
- **Conversion:** ~1–5s (depends on PDF size, converter)
- **Chunking:** ~100–500ms (depends on strategy, text size)
- **Embedding:** ~1–10s (depends on chunk count, API latency)
- **Batching:** 100 chunks at a time to API to minimize RPC overhead

### Memory
- **Model caches:** Shared across wrappers (HF models in `~/.cache/huggingface`)
- **Worker threads:** 4–8 by default (QueueManager)
- **Database:** SQLite in-process (light)

### Scaling
- Use web API with async FastAPI for concurrent requests
- Enable multi-worker deployment (e.g., `gunicorn -w 4`)
- Parallel chunking/embedding via QueueManager

---

## Extension Points

### Adding a Converter
1. Subclass `PDFConverter` in `services/converters/<name>.py`
2. Implement `convert()`, `download_model()`, `validate_installation()`
3. Register in `CLILazyFactory._converters` mapping
4. Add optional dependency to `pyproject.toml`

### Adding a Chunker
1. Subclass `BaseChunker` in `services/chunkers/<name>_chunker.py`
2. Implement `chunk()`, `validate_params()`
3. Register in `ChunkerFactory.__init__()`
4. Update `ChunkerType` enum if needed

### Adding an Embedding Provider
1. Subclass `BaseEmbeddingsWrapper` in `services/embeddings_wrappers/<name>.py`
2. Implement `embed()`, `embed_batch()`, `validate_credentials()`
3. Register in `EmbeddingsFactory.__init__()`
4. Update `EmbeddingProvider` enum

---

## Known Limitations & Future Work

- **Streaming Results:** Currently accumulates all chunks in memory; streaming output planned
- **Distributed Processing:** Single-machine parallelization; multi-machine queue (Celery) planned
- **Fine-Tuning:** No native fine-tuning of embedding models; planned for v2
- **Fallback Strategies:** Limited automatic provider fallback; intelligent retry logic planned
- **Jupyter Support:** Requires `nest_asyncio` patch for async in notebooks; built-in support planned

---

## Debugging & Troubleshooting

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
pdfstract convert document.pdf
```

### Check Available Providers
```bash
pdfstract converters list
pdfstract chunkers list
pdfstract embeddings-list
```

### Validate Credentials
```python
from pdfstract import PDFStract
pdf = PDFStract()
pdf.validate_credentials("openai", api_key="sk-...")  # Returns True/False
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'openai'` | Optional dependency missing | `pip install openai` or `pip install pdfstract[embeddings]` |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | Jupyter notebook asyncio conflict | Use `await pdf.convert_async()` or `nest_asyncio.apply()` |
| `ValueError: Converter 'invalid' not found` | Invalid converter name | Run `pdfstract converters list` to see valid names |
| `URLError: <urlopen error …>` | Network error calling external API | Check API endpoint, internet connection, and rate limits |

---

## Related Documentation

- [README.md](../../README.md) — Project overview, installation, quickstart
- [CLI_README.md](../../CLI_README.md) — Detailed CLI reference
- [API Documentation](../api/) — OpenAPI/Swagger specs (auto-generated from FastAPI)
- [Quick Start Guide](../quick-start.md) — Step-by-step tutorials

---

## References

- **C4 Model:** [c4model.com](https://c4model.com) — Architecture visualization standards
- **Mermaid Diagrams:** [mermaid.js.org](https://mermaid.js.org) — Syntax and rendering
- **Design Patterns:** [refactoring.guru](https://refactoring.guru/design-patterns) — Gang of Four classics
- **Async Python:** [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)

---

**Generated:** 2025-01-XX | **Version:** 1.0 | **Author:** PDFStract Team
