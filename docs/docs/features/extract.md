---
sidebar_position: 1
---

# Extract (PDF Conversion)

PDFStract provides 10+ PDF extraction libraries to convert your documents into structured text ready for AI applications. Each library has different strengths, making it easy to choose the right tool for your specific documents.

## Quick Start

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Auto-select best available library
text = pdfstract.convert('document.pdf', library='auto')

# Use specific library
text = pdfstract.convert('document.pdf', library='marker')
```

## Available Libraries

### By Installation Tier

| Tier | Libraries | Install Command |
|------|-----------|-----------------|
| **Base** | pymupdf4llm, markitdown | `pip install pdfstract` |
| **Standard** | + pytesseract, unstructured | `pip install pdfstract[standard]` |
| **Advanced** | + marker, docling, paddleocr, deepseek | `pip install pdfstract[advanced]` |
| **All** | All libraries combined | `pip install pdfstract[all]` |

### Library Comparison

| Library | Speed | Quality | OCR | Best For |
|---------|-------|---------|-----|----------|
| **pymupdf4llm** | ⚡ Fast | Good | ❌ | Simple text PDFs, quick extraction |
| **markitdown** | ⚡ Fast | Good | ❌ | Markdown output, Microsoft docs |
| **marker** | 🔄 Medium | Excellent | ✅ | Complex layouts, figures, tables |
| **docling** | 🔄 Medium | Excellent | ✅ | Document intelligence, structure |
| **unstructured** | 🔄 Medium | Very Good | ✅ | Structured documents, forms |
| **pytesseract** | 🐢 Slow | Good | ✅ | Scanned PDFs, legacy documents |
| **paddleocr** | 🔄 Medium | Very Good | ✅ | Multi-language OCR |
| **deepseek** | ⚡ Fast | Very Good | ✅ | GPU-accelerated OCR |
| **mineru** | 🔄 Medium | Excellent | ✅ | Scientific papers, LaTeX |

## Python API

### Basic Conversion

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Convert with auto-selection
text = pdfstract.convert('document.pdf', library='auto')

# Convert with specific library
text = pdfstract.convert('document.pdf', library='docling')

# Different output formats
markdown = pdfstract.convert('document.pdf', library='marker', output_format='markdown')
json_data = pdfstract.convert('document.pdf', library='docling', output_format='json')
plain_text = pdfstract.convert('document.pdf', library='pymupdf4llm', output_format='text')
```

### Async Conversion

```python
import asyncio
from pdfstract import PDFStract

async def process_pdf():
    pdfstract = PDFStract()
    result = await pdfstract.convert_async('document.pdf', library='marker')
    return result

text = asyncio.run(process_pdf())
```

### Batch Conversion

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Process all PDFs in a directory
results = pdfstract.batch_convert(
    pdf_directory='./documents/',
    library='docling',
    output_format='markdown',
    parallel_workers=4
)

print(f"Success: {results['success']}, Failed: {results['failed']}")

for filename, content in results['results'].items():
    if 'error' not in content:
        print(f"✓ {filename}: {len(content)} chars")
```

### List Available Libraries

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

# Get all libraries with status
libraries = pdfstract.list_libraries()
for lib in libraries:
    status = "✓" if lib['available'] else "✗"
    print(f"{status} {lib['name']}")

# Get only available library names
available = pdfstract.list_available_libraries()
print(f"Available: {available}")
```

## CLI Usage

### Convert Single PDF

```bash
# Auto-select best library
pdfstract convert document.pdf --library auto

# Use specific library
pdfstract convert document.pdf --library marker

# Save to file
pdfstract convert document.pdf --library docling --output result.md

# Different output formats
pdfstract convert document.pdf --library marker --format json
pdfstract convert document.pdf --library pymupdf4llm --format text
```

### Batch Processing

```bash
# Process all PDFs in folder
pdfstract batch ./documents/ --output ./results/

# With parallel workers
pdfstract batch ./pdfs/ --library docling --parallel 4

# With specific output format
pdfstract batch ./docs/ --library marker --format json
```

### Compare Libraries

```bash
# Compare multiple libraries on same document
pdfstract compare document.pdf --libraries marker,docling,pymupdf4llm
```

### List Available Libraries

```bash
# Show all libraries with status
pdfstract libs
```

## Output Formats

PDFStract supports multiple output formats:

| Format | Description | Use Case |
|--------|-------------|----------|
| `markdown` | Markdown with headers, lists, tables | RAG, documentation |
| `text` | Plain text | Simple processing |
| `json` | Structured JSON with metadata | Programmatic access |
| `html` | HTML markup | Web display |

```python
# Markdown (default)
md = pdfstract.convert('doc.pdf', library='marker', output_format='markdown')

# JSON with structure
data = pdfstract.convert('doc.pdf', library='docling', output_format='json')

# Plain text
text = pdfstract.convert('doc.pdf', library='pymupdf4llm', output_format='text')
```

## Library Details

### pymupdf4llm

Fast, lightweight extraction using PyMuPDF. Best for simple text PDFs.

```python
text = pdfstract.convert('simple.pdf', library='pymupdf4llm')
```

**Pros:** Very fast, low memory, no GPU needed  
**Cons:** No OCR, struggles with complex layouts

### marker

ML-powered extraction with excellent quality. Handles complex layouts, figures, and tables.

```python
text = pdfstract.convert('complex.pdf', library='marker')
```

**Pros:** Excellent quality, handles tables/figures, OCR support  
**Cons:** Requires model download, slower than basic extractors

### docling

IBM's document intelligence platform. Great for structured documents.

```python
text = pdfstract.convert('report.pdf', library='docling')
```

**Pros:** Document structure understanding, metadata extraction  
**Cons:** Requires model download, heavier dependencies

### unstructured

Smart document parsing with element detection.

```python
text = pdfstract.convert('form.pdf', library='unstructured')
```

**Pros:** Element detection, form handling, structure preservation  
**Cons:** Moderate speed, requires additional dependencies

### paddleocr

Accurate OCR engine with multi-language support.

```python
text = pdfstract.convert('scanned.pdf', library='paddleocr')
```

**Pros:** Multi-language, accurate OCR, GPU acceleration  
**Cons:** Requires PaddlePaddle installation

## Model Downloads

Some libraries require model downloads before first use:

```bash
# Download models for specific library
pdfstract download marker
pdfstract download docling

# Download all available models
pdfstract download --all
```

```python
# Check download status
pdfstract = PDFStract()
status = pdfstract.get_converter_status('marker')
print(f"Download status: {status['download_status']}")

# Prepare/download models
result = pdfstract.prepare_converter('marker')
print(f"Ready: {result['success']}")
```

## Error Handling

```python
from pdfstract import PDFStract

pdfstract = PDFStract()

try:
    text = pdfstract.convert('document.pdf', library='marker')
except FileNotFoundError:
    print("PDF file not found")
except ValueError as e:
    print(f"Conversion error: {e}")
```

## Best Practices

1. **Use `auto` for portability**: Your code works regardless of installed tier
2. **Match library to document type**: Use OCR libraries for scanned PDFs
3. **Batch process for efficiency**: Amortizes library loading time
4. **Download models in advance**: Avoid first-run delays in production

## Next Steps

- **[Chunk](./chunk)** - Split extracted text for RAG
- **[Embed](./embed)** - Generate vector embeddings
- **[CLI Guide](../cli/overview)** - Full command reference
- **[Python API](../api/overview)** - Complete API documentation
