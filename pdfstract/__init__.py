"""
PDFStract - Unified PDF Extraction Library & CLI

A modern, unified interface for PDF extraction supporting multiple backend libraries
(Marker, PyMuPDF4LLM, Docling, Unstructured, and more).

Can be used as:
1. A Python library for integrating PDF extraction into applications
2. A command-line tool for batch processing
3. A service with REST API and web UI

Installation:
    pip install pdfstract

Quick Start (Library Usage):
    from pdfstract import PDFStract
    
    pdfstract = PDFStract()
    result = pdfstract.convert('sample.pdf', 'marker')
    print(result)

Quick Start (CLI):
    pdfstract convert sample.pdf --library marker --output-format markdown

Documentation:
    See README.md for comprehensive documentation
    See CLI_README.md for CLI usage details
    See services/ for implementation details
"""

from .api import PDFStract, convert_pdf, list_available_libraries, chunk_text, list_available_chunkers

# Version is managed in pyproject.toml
# Read it dynamically to keep a single source of truth
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Fallback for older Python

try:
    from pathlib import Path
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    __version__ = pyproject_data["project"]["version"]
except Exception:
    __version__ = "1.1.0"  # Fallback version

__author__ = "EPAM"
__license__ = "MIT"

__all__ = [
    "PDFStract",
    "convert_pdf",
    "list_available_libraries",
    "chunk_text",
    "list_available_chunkers",
    "__version__",
]

