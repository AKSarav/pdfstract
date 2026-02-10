---
sidebar_position: 2
---

# Installation

This guide covers all the ways to install PDFStract, from simple pip installation to development setups with Docker.

## Basic Installation

### Using pip (Recommended)

Install the latest stable version:

```bash
pip install pdfstract
```

### Using conda

```bash
conda install -c conda-forge pdfstract
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
```

### With Development Dependencies

To install with all development tools:

```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Install with dev dependencies
pip install -e ".[dev]"
```

## Optional Dependencies

PDFStract uses different libraries for PDF conversion and text chunking. Install only what you need:

### Conversion Libraries

```bash
# Install specific converters
pip install pdfstract[marker]      # Marker converter
pip install pdfstract[docling]     # Docling converter  
pip install pdfstract[unstructured] # Unstructured converter
pip install pdfstract[paddleocr]   # PaddleOCR converter
pip install pdfstract[tesseract]   # Tesseract OCR
pip install pdfstract[mineru]      # MinerU converter

# Install all converters
pip install pdfstract[all-converters]
```

### Chunking Libraries

```bash
# Advanced chunking methods
pip install pdfstract[semantic]    # Semantic chunking
pip install pdfstract[neural]      # Neural chunking
pip install pdfstract[embeddings]  # Embedding-based chunking

# Install all chunkers
pip install pdfstract[all-chunkers]
```

### Complete Installation

To install everything:

```bash
pip install pdfstract[all]
```

## Docker Installation

### Using Docker Compose (Recommended)

The easiest way to get everything running:

```bash
# Clone the repository
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Start all services
docker-compose up -d
```

This starts:
- Web UI at http://localhost:3000
- API server at http://localhost:8000
- Background processing queue

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