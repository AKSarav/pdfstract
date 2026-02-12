# PDFStract CLI - Command-Line Interface Guide

PDFStract now includes a powerful command-line interface for PDF extraction and conversion with support for batch processing, multi-library comparison, and production automation.

## Table of Contents

- [Installation](#installation)
- [Performance & Startup Time](#-performance--startup-time)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Batch Processing](#batch-processing)
- [Real-World Examples](#real-world-examples)
- [Integration Examples](#integration-examples)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)

## Installation

### Installation Tiers

PDFStract offers tiered installation based on the libraries you need:

| Tier | Libraries | Install Command | Best For |
|------|-----------|-----------------|----------|
| **Base** | pymupdf4llm, markitdown | `pip install pdfstract` | Fast extraction, simple PDFs |
| **Standard** | pytesseract, unstructured | `pip install pdfstract[standard]` | OCR support, structured docs |
| **Advanced** | marker, docling, paddleocr, deepseek | `pip install pdfstract[advanced]` | Best quality, ML-powered |
| **All** | All libraries combined | `pip install pdfstract[all]` | Complete RAG pipeline |

### From PyPI (Recommended)

```bash
# Base - Fast extractors only (pymupdf4llm, markitdown)
pip install pdfstract

# Standard - Adds OCR libraries (pytesseract, unstructured)
pip install pdfstract[standard]

# Advanced - Adds ML-powered libraries (marker, docling, paddleocr, deepseek)
pip install pdfstract[advanced]

# All - All converters combined (standard + advanced)
pip install pdfstract[all]
```

### From Source
```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract
pip install -e .
# or
uv sync
```

### Verify Installation
```bash
pdfstract --help
```

## ⚡ Performance & Startup Time

### Understanding CLI Startup

PDFStract CLI uses **lazy loading** to keep startup times fast:

| Command | Startup Time | Why |
|---------|--------------|-----|
| `pdfstract --help` | **< 1s** ⚡ | Only loads Click framework, no libraries |
| `pdfstract convert --help` | **< 1s** ⚡ | No library checking, just shows usage |
| `pdfstract libs` | **8-10s** | Checks all 8 libraries (one-time) |
| `pdfstract convert file.pdf -l X` | **3-8s** | Loads only library X, not others |
| `pdfstract batch ./docs -l X` | **3-8s** | Loads only library X for bulk processing |

### Why Is First Use Slow?

The 3-8s delay on first conversion is **NOT a PDFStract issue** - it's because the PDF libraries themselves are heavy:

- **torch** (~2-3s) - Machine learning framework
- **paddleocr/marker/docling** (~3-5s) - Load ML models on first use
- **Python imports** (~1-2s) - Module loading overhead

**This is a one-time cost per Python session.** After first use, conversions run faster because libraries stay loaded.

### How to Keep CLI Fast

1. **Help commands are instant:**
   ```bash
   pdfstract --help              # Instant
   pdfstract convert --help      # Instant
   pdfstract batch --help        # Instant
   ```

2. **Use fast libraries for quick conversions:**
   ```bash
   pdfstract convert file.pdf --library pymupdf4llm   # Fastest (~3s)
   pdfstract convert file.pdf --library markitdown    # Fast (~4s)
   pdfstract convert file.pdf --library marker        # Quality but slower (~8s)
   ```

3. **Batch processing amortizes startup cost:**
   ```bash
   # First file: 8s (includes startup)
   # Files 2-100: ~1-2s each (library already loaded)
   pdfstract batch ./docs --library unstructured --parallel 4
   ```

4. **For production scripts, keep process alive:**
   ```bash
   # Bad: Multiple 8s startups
   for file in *.pdf; do pdfstract convert "$file" -l unstructured; done
   
   # Better: Single 8s startup, then fast conversions
   python -c "
   from services.cli_factory import CLILazyFactory
   factory = CLILazyFactory()
   for file in glob('*.pdf'):
       factory.convert('unstructured', file)
   "
   ```

## Quick Start

### 1. List Available Libraries
```bash
pdfstract libs
```

Output shows which PDF extraction libraries are installed:
```
✓ Available: unstructured, marker, pymupdf4llm, docling, ...
✗ Unavailable: (with error reasons)
```

### 2. Convert a Single PDF
```bash
# Convert to markdown (default)
pdfstract convert document.pdf --library unstructured

# Save to file
pdfstract convert document.pdf --library unstructured --output result.md

# Different formats
pdfstract convert document.pdf --library marker --format json --output result.json
pdfstract convert document.pdf --library pymupdf4llm --format text
```

### 3. Test Multiple Libraries
```bash
pdfstract compare sample.pdf \
  -l unstructured \
  -l marker \
  -l pymupdf4llm \
  --format markdown \
  --output ./comparison_results
```

Results in:
```
comparison_results/
├─ unstructured_result.md
├─ marker_result.md
├─ pymupdf4llm_result.md
└─ comparison_summary.json
```

## Commands

### `pdfstract libs`
List all available PDF extraction libraries and their status.

```bash
pdfstract libs
```

**Output:**
- Shows 10+ libraries (PyMuPDF4LLM, MarkItDown, Marker, Docling, etc.)
- Displays availability status (✓ Available / ✗ Unavailable)
- Shows error messages for unavailable libraries

---

### `pdfstract convert`
Convert a single PDF file with a specified library.

```bash
pdfstract convert INPUT_FILE [OPTIONS]
```

**Options:**
- `-l, --library TEXT` (required) - Extraction library to use
- `-f, --format [markdown|json|text]` - Output format (default: markdown)
- `-o, --output PATH` - Output file path (optional, auto-generates if not specified)

**Auto-Generated Output:**
If `--output` is not specified, PDFStract automatically creates a file with the same name as the input PDF:
- `sample.pdf` → `sample.md` (markdown format)
- `document.pdf` → `document.json` (JSON format)
- `report.pdf` → `report.txt` (text format)

**Examples:**
```bash
# Auto-generates sample.md in current directory
pdfstract convert sample.pdf --library unstructured

# Auto-generates document.json
pdfstract convert document.pdf --library unstructured --format json

# Explicit output file path
pdfstract convert sample.pdf --library marker --output ./results/custom_name.md

# JSON format with custom path
pdfstract convert sample.pdf --library docling --format json --output result.json
```

---

### `pdfstract compare`
Compare multiple extraction libraries on a single PDF to find the best one.

```bash
pdfstract compare INPUT_FILE [OPTIONS]
```

**Options:**
- `-l, --libraries TEXT` (required, multiple) - Libraries to compare
- `-f, --format [markdown|json|text]` - Output format (default: markdown)
- `-o, --output PATH` (required) - Output directory for results

**Examples:**
```bash
# Compare 3 libraries
pdfstract compare sample.pdf \
  -l unstructured \
  -l marker \
  -l pymupdf4llm \
  --output ./test_results

# Compare with JSON output
pdfstract compare invoice.pdf \
  -l marker \
  -l docling \
  --format json \
  --output ./compare
```

**Output:**
- Individual result files for each library
- `comparison_summary.json` with metadata and stats

---

### `pdfstract batch`
Batch convert multiple PDFs in a directory with parallel processing.

```bash
pdfstract batch INPUT_DIRECTORY [OPTIONS]
```

**Options:**
- `-l, --library TEXT` (required) - Extraction library to use
- `-f, --format [markdown|json|text]` - Output format (default: markdown)
- `-o, --output PATH` (required) - Output directory
- `-p, --parallel INTEGER` - Number of parallel workers (default: 2)
- `--pattern TEXT` - File pattern to match (default: *.pdf)
- `--skip-errors` - Skip PDFs that fail conversion

**Examples:**
```bash
# Basic batch conversion
pdfstract batch ./documents \
  --library unstructured \
  --output ./converted

# With parallel processing
pdfstract batch ./documents \
  --library marker \
  --output ./converted \
  --parallel 4

# With error handling
pdfstract batch ./pdfs \
  --library docling \
  --format json \
  --output ./converted \
  --parallel 8 \
  --skip-errors

# Custom file pattern
pdfstract batch ./invoices \
  --library unstructured \
  --pattern "invoice_*.pdf" \
  --output ./structured
```

**Output:**
```
output_directory/
├─ file1.md
├─ file2.md
├─ file3.md
├─ ... (more files)
└─ batch_report.json
```

**Batch Report (batch_report.json):**
```json
{
  "input_directory": "/path/to/pdfs",
  "output_directory": "/path/to/output",
  "library": "unstructured",
  "format": "markdown",
  "total_files": 150,
  "statistics": {
    "success": 147,
    "failed": 2,
    "skipped": 1
  },
  "files": {
    "document1.pdf": {
      "status": "success",
      "size_bytes": 45230
    },
    "document2.pdf": {
      "status": "failed",
      "error": "Invalid PDF format"
    }
  }
}
```

---

### `pdfstract batch-compare`
Compare multiple extraction libraries across an entire corpus of PDFs.

```bash
pdfstract batch-compare INPUT_DIRECTORY [OPTIONS]
```

**Options:**
- `-l, --libraries TEXT` (required, multiple) - Libraries to compare
- `-f, --format [markdown|json|text]` - Output format (default: markdown)
- `-o, --output PATH` (required) - Output directory
- `--max-files INTEGER` - Limit number of files to process

**Examples:**
```bash
# Compare on all PDFs
pdfstract batch-compare ./papers \
  -l marker \
  -l unstructured \
  -l pymupdf4llm \
  --output ./library_comparison

# Quick test on sample
pdfstract batch-compare ./large_corpus \
  -l marker \
  -l unstructured \
  --max-files 50 \
  --output ./sample_test
```

**Output:**
- `batch_comparison_report.json` with per-library success rates
- Per-file results for all PDFs tested

## Batch Processing

### When to Use Batch Processing

Batch processing is perfect for:
- Converting 100+ PDFs with one library
- Testing multiple libraries on entire corpus
- Production automation jobs
- Legacy archive digitization
- Enterprise migrations

### Parallel Processing Guidelines

Choose workers based on library and hardware:

| Library | CPU Usage | Recommended Workers |
|---------|-----------|-------------------|
| PyMuPDF4LLM | Low | 8-16 |
| MarkItDown | Medium | 4-8 |
| Unstructured | Medium | 4-6 |
| Marker (ML) | High | 2-4 |
| OCR (Paddle/Tesseract) | Very High | 1-2 |

```bash
# Fast library, beefy server
pdfstract batch ./docs --library pymupdf4llm --parallel 16

# Slow ML library
pdfstract batch ./docs --library marker --parallel 2

# Medium library, balanced
pdfstract batch ./docs --library unstructured --parallel 6
```

### Error Handling

**Without --skip-errors (default):**
- Stops on first error
- Exit code 1 if failures occur
- Best for strict pipelines

**With --skip-errors:**
- Continues processing all files
- Failed files marked in report
- Exit code 0 (always succeeds)
- Best for best-effort processing

```bash
# Strict mode (fail on errors)
pdfstract batch ./docs --library unstructured --output ./result

# Best-effort mode (skip errors)
pdfstract batch ./docs --library unstructured --output ./result --skip-errors
```

### Parsing Batch Reports

Use `jq` to analyze batch reports:

```bash
# Overall statistics
jq '.statistics' batch_report.json

# Success rate
jq '.statistics.success / .total_files * 100' batch_report.json

# Failed files only
jq '.files | to_entries[] | select(.value.status=="failed")' batch_report.json

# Average output size
jq '.files | to_entries[] | select(.value.status=="success") | .value.size_bytes' batch_report.json | \
  awk '{sum+=$1; count++} END {print sum/count/1024 " KB"}'
```

## Real-World Examples

### Example 1: Law Firm Document Digitization

**Scenario:** Convert 5,000 case files to searchable markdown

```bash
# Step 1: Test on sample (5 cases)
pdfstract compare case_1.pdf case_2.pdf case_3.pdf \
  -l marker \
  -l unstructured \
  -l docling \
  --output ./test_results

# Step 2: Review outputs, pick best library (e.g., docling)

# Step 3: Full batch conversion (5,000 cases)
pdfstract batch ./all_cases \
  --library docling \
  --format markdown \
  --output ./converted_cases \
  --parallel 8 \
  --skip-errors

# Step 4: Monitor results
jq '.statistics' ./converted_cases/batch_report.json
```

**Results:** 2 months manual work → 12 hours automated. $100k labor cost → $500 compute cost.

---

### Example 2: Research Paper Quality Testing

**Scenario:** Find best extractor for 1,000 research papers

```bash
# Test on sample
pdfstract batch-compare ./papers \
  -l marker \
  -l unstructured \
  -l pymupdf4llm \
  --max-files 50 \
  --output ./library_test

# Review success rates, pick best

# Full batch with chosen library
pdfstract batch ./papers \
  --library marker \
  --format json \
  --output ./extracted_papers \
  --parallel 4
```

---

### Example 3: Invoice Processing Pipeline

**Scenario:** Daily automated invoice conversion

```bash
# Create batch scheduler config
pdfstract-scheduler create daily_invoices \
  ./daily_invoices_input \
  ./daily_invoices_output \
  --library unstructured \
  --parallel 4

# Run job
pdfstract-scheduler run daily_invoices

# View results
cat ./daily_invoices_output/batch_report.json
```

---

### Example 4: Legacy Archive Migration

**Scenario:** Modernize 50,000 legacy PDFs to JSON

```bash
pdfstract batch ./legacy_archive \
  --library marker \
  --format json \
  --output ./modern_archive \
  --parallel 16 \
  --skip-errors

# Monitor with tail
tail -f ./modern_archive/batch_report.json
```

## Integration Examples

### Bash Script: Nightly Batch Job

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
OUTPUT_DIR="./converted/$DATE"

pdfstract batch ./daily_pdfs \
  --library unstructured \
  --format markdown \
  --output "$OUTPUT_DIR" \
  --parallel 8 \
  --skip-errors

# Alert if failures
FAILED=$(jq '.statistics.failed' "$OUTPUT_DIR/batch_report.json")
if [ "$FAILED" -gt 0 ]; then
  echo "⚠️  $FAILED conversions failed on $DATE" | mail admin@company.com
fi
```

---

### Python: Programmatic Usage

```python
import subprocess
import json
from pathlib import Path

def batch_convert(pdf_dir: str, library: str, output_dir: str) -> dict:
    """Wrapper around CLI"""
    result = subprocess.run([
        'pdfstract', 'batch', pdf_dir,
        '--library', library,
        '--output', output_dir,
        '--parallel', '4'
    ])
    
    # Load and parse report
    report_file = Path(output_dir) / 'batch_report.json'
    with open(report_file) as f:
        report = json.load(f)
    
    success_rate = (report['statistics']['success'] / 
                   report['total_files'] * 100)
    print(f"Success Rate: {success_rate:.1f}%")
    return report
```

---

### Docker: Containerized Processing

```dockerfile
FROM python:3.13-slim
RUN pip install pdfstract

ENTRYPOINT ["pdfstract"]
CMD ["batch", "/data/input", "--library", "unstructured", "--output", "/data/output"]
```

```bash
# Build
docker build -t pdfstract .

# Run
docker run -v ./pdfs:/data/input -v ./converted:/data/output pdfstract
```

---

### CI/CD: GitHub Actions Example

```yaml
name: PDF Extraction

on: [push]

jobs:
  extract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install PDFStract
        run: pip install pdfstract
      
      - name: Extract PDFs
        run: |
          pdfstract batch ./source_pdfs \
            --library unstructured \
            --format json \
            --output ./extracted
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: extracted-pdfs
          path: extracted/
```

## Performance Tips

### 1. Test Before Large Batches
```bash
# Always test library first
pdfstract convert sample.pdf --library CHOSEN_LIB

# Then run batch
pdfstract batch ./1000_files --library CHOSEN_LIB --parallel 4
```

### 2. Choose Library Based on Speed vs Quality
- **Speed:** pymupdf4llm (--parallel 16)
- **Balanced:** unstructured (--parallel 6)
- **Quality:** marker (--parallel 2)

### 3. Monitor Long-Running Jobs
```bash
pdfstract batch ./files --library marker --parallel 2 2>&1 | tee job.log

# In another terminal
tail -f job.log
```

### 4. Retry Failed Conversions
```bash
# Extract failed files from report
jq -r '.files | to_entries[] | select(.value.status=="failed") | .key' \
  batch_report.json > failed.txt

# Retry with different library
while read file; do
  pdfstract convert "$file" --library marker --output "retry_results/${file%.pdf}.md"
done < failed.txt
```

## Troubleshooting

### CLI Takes Long to Start (8-10 seconds)

This is **normal and expected** for the first conversion. Here's why:

**What's happening:**
- First time you use `pdfstract convert`, Python loads the PDF libraries
- Libraries like torch, paddleocr, marker are large (~500MB-1GB)
- They need to initialize machine learning models on first use
- This happens **only once per Python session**

**Solutions:**

1. **Use fast libraries for quick results:**
   ```bash
   # Fast: ~3-4 seconds
   pdfstract convert file.pdf --library pymupdf4llm
   
   # Slow: ~8-10 seconds (but better quality)
   pdfstract convert file.pdf --library marker
   ```

2. **Help commands are instant (no startup delay):**
   ```bash
   pdfstract --help              # Instant!
   pdfstract convert --help      # Instant!
   ```

3. **Batch processing hides the delay:**
   ```bash
   # First file: ~10s total (includes library loading)
   # Files 2-100: ~1-2s each
   # Total for 100 files: ~120s instead of 1000s
   pdfstract batch ./pdfs --library unstructured --parallel 4
   ```

4. **Keep Python process alive for multiple conversions:**
   ```bash
   # Each call: 10s (wasteful!)
   pdfstract convert 1.pdf -l unstructured
   pdfstract convert 2.pdf -l unstructured
   
   # Better: Keep Python alive
   python -c "
   from services.cli_factory import CLILazyFactory
   factory = CLILazyFactory()
   factory.convert('unstructured', '1.pdf')
   factory.convert('unstructured', '2.pdf')  # ~1s each!
   "
   ```

### "Library 'X' not available"

**Solution:**
```bash
pdfstract libs  # See what's available

# Install missing library
uv add LIBRARY_NAME
# or
pip install LIBRARY_NAME
```

### "File is not a PDF"

Only PDF files are supported. Check:
- File extension is `.pdf`
- File is actually a PDF (not renamed)
- File is not corrupted

### Batch Job Very Slow

Reduce parallel workers:
```bash
# Instead of --parallel 8
pdfstract batch ./docs --library marker --parallel 2
```

Or distribute job across multiple machines.

### Memory Running Out

Reduce workers or process in smaller batches:
```bash
pdfstract batch ./docs --library marker --parallel 1
```

### DeepSeek-OCR Not Working

Requires CUDA GPU. Alternatives:
- PaddleOCR (no GPU needed)
- Pytesseract (no GPU needed)
- Unstructured (CPU-based)

## Batch Job Scheduler

For recurring jobs, use the batch scheduler:

```bash
# Create scheduled job
pdfstract-scheduler create daily_job \
  ./input_dir \
  ./output_dir \
  --library unstructured \
  --parallel 4

# Run job
pdfstract-scheduler run daily_job

# View execution history
pdfstract-scheduler history daily_job

# List all jobs
pdfstract-scheduler list
```

Add to cron for automated scheduling:
```bash
0 2 * * * pdfstract-scheduler run daily_job
```

## Next Steps

- Read [main README.md](README.md) for Web UI guide
- Check [batch processing use cases](CLI_README.md#real-world-examples)
- Join GitHub discussions for questions
- Open issues for bugs or feature requests

## Support

- **GitHub:** https://github.com/aksarav/pdfstract
- **Issues:** https://github.com/aksarav/pdfstract/issues
- **Discussions:** https://github.com/aksarav/pdfstract/discussions

---

**Happy extracting! 🚀📄✨**

