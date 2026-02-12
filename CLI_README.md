# PDFStract

**The first layer in your RAG pipeline** — Extract, chunk, and prepare PDFs for AI.

[![PyPI](https://img.shields.io/pypi/v/pdfstract)](https://pypi.org/project/pdfstract/)
[![Python](https://img.shields.io/pypi/pyversions/pdfstract)](https://pypi.org/project/pdfstract/)
[![License](https://img.shields.io/github/license/AKSarav/pdfstract)](https://github.com/AKSarav/pdfstract/blob/main/LICENSE)

PDFStract converts PDFs to text using 10+ extraction libraries and chunks them using 10+ methods — all through a simple Python API, CLI, or Web UI.

## Installation

```bash
# Base (fast extractors)
pip install pdfstract

# Standard (+ OCR support)
pip install pdfstract[standard]

# Advanced (+ ML-powered extractors)
pip install pdfstract[advanced]

# All libraries
pip install pdfstract[all]
```

## Quick Start — Python Module

### Convert a PDF

```python
from pdfstract import convert_pdf

# One-liner conversion
text = convert_pdf('document.pdf', library='marker')
print(text)
```

### Convert and Chunk for RAG

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Extract text
text = pdfstract.convert('document.pdf', library='docling')

# Chunk for embeddings
chunks = pdfstract.chunk(text, chunker='semantic', chunk_size=512)

print(f"Created {chunks['total_chunks']} chunks")
for chunk in chunks['chunks']:
    print(f"- {chunk['text'][:50]}...")
```

### List Available Libraries

```python
from pdfstract import PDFStract

pdfstract = PDFStract()
print(pdfstract.list_available_libraries())
# ['pymupdf4llm', 'markitdown', 'marker', 'docling', ...]

print(pdfstract.list_chunkers())
# ['token', 'sentence', 'semantic', 'recursive', ...]
```

### Batch Processing

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

results = pdfstract.batch_convert(
    pdf_directory='./pdfs',
    library='pymupdf4llm',
    parallel_workers=4
)
print(f"Converted {results['success']} files")
```

### Async Support

```python
import asyncio
from pdfstract import PDFStract

async def process():
    pdfstract = PDFStract()
    result = await pdfstract.convert_async('doc.pdf', library='marker')
    return result

asyncio.run(process())
```

## Quick Start — CLI

```bash
# List available libraries
pdfstract libs

# Convert a PDF
pdfstract convert document.pdf --library marker --output result.md

# Convert and chunk
pdfstract convert-chunk document.pdf --library docling --chunker semantic

# Batch convert directory
pdfstract batch ./pdfs --library pymupdf4llm --parallel 4 --output ./converted

# Compare libraries
pdfstract compare sample.pdf -l marker -l docling -l pymupdf4llm
```

## Supported Libraries

| Library | Type | Best For |
|---------|------|----------|
| **pymupdf4llm** | Fast | Simple PDFs, speed |
| **markitdown** | Balanced | General documents |
| **marker** | ML | Complex layouts |
| **docling** | ML | Document intelligence |
| **paddleocr** | OCR | Scanned PDFs |
| **unstructured** | Smart | Structured extraction |
| **pytesseract** | OCR | Classic OCR |
| **mineru** | ML | Best quality (Docker) |

## Supported Chunkers

| Chunker | Best For |
|---------|----------|
| **token** | Fixed-size chunks |
| **sentence** | Natural boundaries |
| **semantic** | Topic-coherent chunks |
| **recursive** | Structured documents |
| **code** | Source code |
| **fast** | High throughput |

## Web UI & Docker

```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract
make up
```

Open http://localhost:3000 for Web UI, http://localhost:8000 for API.

## Documentation

📖 **[pdfstract.com](https://pdfstract.com)** — Full documentation, guides, and examples

**Legacy:** [aksarav.github.io/pdfstract](https://aksarav.github.io/pdfstract)

- [Installation Guide](https://aksarav.github.io/pdfstract/installation)
- [Python Module Reference](https://aksarav.github.io/pdfstract/api/overview)
- [CLI Guide](https://aksarav.github.io/pdfstract/cli/overview)
- [Web UI Guide](https://aksarav.github.io/pdfstract/web-ui/overview)

## Links

- **GitHub:** [github.com/aksarav/pdfstract](https://github.com/aksarav/pdfstract)
- **PyPI:** [pypi.org/project/pdfstract](https://pypi.org/project/pdfstract)
- **Issues:** [github.com/aksarav/pdfstract/issues](https://github.com/aksarav/pdfstract/issues)

## License

MIT License — see [LICENSE](https://github.com/aksarav/pdfstract/blob/main/LICENSE)

---

**Made with ❤️ for AI RAG pipelines**

