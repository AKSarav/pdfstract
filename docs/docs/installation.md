---
sidebar_position: 2
---

# Installation

This guide covers all the ways to install PDFStract, from simple pip installation to development setups with Docker.

## Installation Tiers

PDFStract offers tiered installation based on the libraries you need:

| Tier | Libraries | Install Command | Best For |
|------|-----------|-----------------|----------|
| **Base** | pymupdf4llm, markitdown | `pip install pdfstract` | Fast extraction, simple PDFs |
| **Standard** | + pytesseract, unstructured | `pip install pdfstract[standard]` | OCR support, structured docs |
| **Premium** | + marker, docling, paddleocr, deepseek | `pip install pdfstract[premium]` | Best quality, ML-powered |
| **Full** | All above + chunking | `pip install pdfstract[full]` | Complete RAG pipeline |

## Basic Installation

### Using pip (Recommended)

```bash
# Base - Fast extractors only (pymupdf4llm, markitdown)
pip install pdfstract

# Standard - Adds OCR libraries (pytesseract, unstructured)
pip install pdfstract[standard]

# Premium - Adds ML-powered libraries (marker, docling, paddleocr, deepseek)
pip install pdfstract[premium]

# Full - Everything including chunking support
pip install pdfstract[full]

# Just add chunking to any tier
pip install pdfstract[standard,chunking]
```

### Using uv (Fast)

```bash
uv pip install pdfstract[full]
```

## Development Installation

### From Source

For the latest features or to contribute:

```bash
# Clone the repository
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Install in development mode
pip install -e .

# Or with uv
uv sync
```

### With All Dependencies

To install with all libraries for development:

```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Install full version in dev mode
pip install -e ".[full]"
```

## What's Included in Each Tier

### Base (Default)
Libraries visible in dropdown:
- **pymupdf4llm** - Fast, lightweight PDF extraction
- **markitdown** - Microsoft's markdown converter

```bash
pip install pdfstract
```

### Standard
All Base libraries plus:
- **pytesseract** - OCR for scanned PDFs (requires system tesseract)
- **unstructured** - Smart document parsing

```bash
pip install pdfstract[standard]
```

### Premium  
All Standard libraries plus:
- **marker** - ML-powered, excellent for complex layouts
- **docling** - IBM's document intelligence platform
- **paddleocr** - Accurate OCR engine
- **deepseek** - GPU-accelerated OCR

```bash
pip install pdfstract[premium]
```

### Full
All Premium libraries plus:
- **Chunking support** - 10+ chunking methods for RAG pipelines

```bash
pip install pdfstract[full]
```

### Chunking Only
Add chunking to any tier:

```bash
pip install pdfstract[chunking]
pip install pdfstract[standard,chunking]
```
```

### Complete Installation

To install everything:

```bash
pip install pdfstract[all]
```

## Docker Installation

### Using Make ( With Docker ) (Recommended)

The easiest way to get everything running with all libraries including MinerU:

> **why do we need make instead of direct docker** ?
we are downloading the necassary models from hugging face in your host machine as docker containers have limited bandwidth and memory
If you check the docker-compose.yaml you can find that we are mounting these models as a volume for smoother docker setup.


```bash
# Clone the repository
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Download models and start services (first time)
make up

# Or step by step:
make models   # Download HuggingFace/MinerU models (~10GB)
make build    # Build Docker images
make up       # Start services
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make up` | Build and start all services |
| `make down` | Stop all services |
| `make logs` | View container logs |
| `make status` | Show running containers |
| `make rebuild` | Rebuild and restart |
| `make clean` | Remove containers and volumes |
| `make models` | Download ML models only |

This starts:
- Web UI at http://localhost:3000
- API server at http://localhost:8000

### Using Docker Images

Pull and run individual components:

```bash
# Pull the latest image
docker pull aksarav/pdfstract:latest

# Run as a web service
docker run -p 8000:8000 aksarav/pdfstract:latest web

# Run CLI commands
docker run -v $(pwd):/workspace aksarav/pdfstract:latest convert /workspace/document.pdf
```

## Verification

Test your installation:

```python
import pdfstract

# Check version
print(f"PDFStract version: {pdfstract.__version__}")

# List available converters
pdfstract = pdfstract.PDFStract()
print("Available converters:", pdfstract.list_converters())
print("Available chunkers:", pdfstract.list_chunkers())
```

Or from command line:

```bash
# Check installation
pdfstract --version

# List available tools
pdfstract list-converters
pdfstract list-chunkers
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- 1GB disk space

### Recommended Requirements
- Python 3.10+
- 8GB RAM (for large documents)
- 5GB disk space (for all libraries)
- GPU (optional, for neural chunking)

### Platform Support

| Platform | Status | Notes |
|----------|--------|--------|
| Linux    | ✅ Full | All features supported |
| macOS    | ✅ Full | All features supported |
| Windows  | ✅ Full | All features supported |

## Troubleshooting

### Common Issues

**ImportError: No module named 'pdfstract'**
```bash
# Make sure you're in the right environment
pip list | grep pdfstract

# Reinstall if needed
pip uninstall pdfstract
pip install pdfstract
```

**Converter not found errors**
```bash
# Install missing converter
pip install pdfstract[marker]

# Or install all converters
pip install pdfstract[all-converters]
```

**Memory errors with large PDFs**
```bash
# Use streaming mode
pdfstract convert large.pdf --streaming

# Or process in chunks
pdfstract convert large.pdf --max-pages 10
```

### Environment Issues

**Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv pdfstract-env
source pdfstract-env/bin/activate  # Linux/Mac
# pdfstract-env\Scripts\activate     # Windows

pip install pdfstract
```

**Conda Environment**
```bash
# Create conda environment
conda create -n pdfstract python=3.10
conda activate pdfstract
pip install pdfstract
```

### GPU Support

For GPU-accelerated processing:

```bash
# Install with CUDA support
pip install pdfstract[gpu]

# Verify GPU detection
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Next Steps

Once installed, try these guides:

- **[Quick Start](quick-start)** - Convert your first PDF
- **[First Conversion](first-conversion)** - Detailed first example
- **[Python API](../api/overview)** - Use in your applications
- **[CLI Guide](../cli/overview)** - Command-line usage
- **[Web UI](../web-ui/overview)** - Visual interface

Need help? Check our [GitHub Issues](https://github.com/aksarav/pdfstract/issues) or start a [Discussion](https://github.com/aksarav/pdfstract/discussions)!