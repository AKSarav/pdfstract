# PDFStract — PDF Extraction & Benchmarking for RAG and AI Pipelines

CLI • Web UI • API — Extract structured data from PDFs, compare OCR & document-processing libraries, and benchmark conversion quality before building your RAG or AI pipelines.

<p align="center">
  <img src="https://img.shields.io/badge/Project-PDFStract-blue" />
  <img src="https://img.shields.io/badge/Type-CLI%20%7C%20Web%20UI%20%7C%20API-green" />
  <img src="https://img.shields.io/github/stars/AKSarav/pdfstract?style=social" />
  <img src="https://img.shields.io/github/license/AKSarav/pdfstract" />
</p>

<p align="center">
  <b>Supports:</b> PyMuPDF4LLM • Unstructured • Marker • Docling • Tesseract OCR • More coming soon
</p>

---

### 🚀 What is PDFStract?

PDFStract is a developer toolkit to:

- 🧾 Extract structured text, tables, and metadata from PDFs  
- 🔍 Benchmark & compare multiple PDF/OCR extraction libraries side-by-side  
- 🧪 Visualize results before integrating into RAG / AI pipelines  
- 🌐 Run as a CLI, Web UI, or API service

Use it to choose the **best extraction engine for your dataset** instead of guessing.


---

# WEB UI 

PDFstract can be run as a local web ui - it comes with FastAPI backend and react frontend 

Here are some quick screenshots of the Web UI

![UI Screenshot](UI.png)

![UI Screenshot 2](UI2.png)

![UI Screenshot 3](UI3.png)


## ✨ Features

- 🚀 **10+ Conversion Libraries**: PyMuPDF4LLM, MarkItDown, Marker, Docling, PaddleOCR, DeepSeek-OCR, Tesseract, MinerU, Unstructured, and more
- 📱 **Modern React UI**: Beautiful, responsive design with Tailwind CSS
- 💻 **Command-Line Interface**: Full CLI with batch processing, multi-library comparison, and automation
- 🎯 **Multiple Output Formats**: Markdown, JSON, and Plain Text
- ⏱️ **Performance Benchmarking**: Real-time timer shows conversion speed for each library
- 👁️ **Live Preview**: View converted content with syntax highlighting
- 🔄 **Library Status Dashboard**: See which libraries are available/unavailable with error messages
- 💾 **Easy Download**: Download results in your preferred format
- 🐳 **Docker Support**: One-command deployment
- 🔗 **REST API**: Programmatic access to conversion features
- ⚡ **Batch Processing**: Parallel conversion of 100+ PDFs with detailed reporting
- 🌙 **Dark Mode Ready**: Works seamlessly in light and dark themes

## 📚 Supported Libraries

| Library | Version | Type | Status | Notes |
|---------|---------|------|--------|-------|
| **pymupdf4llm** | >=0.0.26 | Text Extraction | Fast | Best for simple PDFs |
| **markitdown** | >=0.1.2 | Markdown | Balanced | Microsoft's conversion tool |
| **marker** | >=1.8.1 | Advanced ML | High Quality | Excellent results, slower |
| **docling** | >=2.41.0 | Document Intelligence | Advanced | IBM's document platform |
| **paddleocr** | >=3.3.2 | OCR | Accurate | Great for scanned PDFs |
| **unstructured** | >=0.15.0 | Document Parsing | Smart | Intelligent element extraction |
| **deepseekocr** | Latest | GPU OCR | Fast (GPU only) | Requires CUDA GPU |
| **pytesseract** | >=0.3.10 | OCR | Classic | Tesseract-based (requires system binary) |

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11+
- **UV**: Fast Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js**: 20+ (for frontend development)
- **Docker** (optional): For containerized deployment

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract
```

2. **Install Python dependencies**:
```bash
uv sync
```

3. **Install frontend dependencies**:
```bash
cd frontend
npm install
cd ..
```

### Running Locally

**Terminal 1: Start the FastAPI Backend**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2: Start the React Frontend (Development)**
```bash
cd frontend
npm run dev
```

**Access the Application**:
- Frontend: http://localhost:5173 (with hot-reload)
- Backend API: http://localhost:8000

**Note**: The frontend development server proxies API calls to the backend at port 8000 (configured in `frontend/vite.config.js`)

### Production Build

To build the React app for production:
```bash
cd frontend
npm run build
```

This creates an optimized build in `frontend/dist/` which gets copied to `/static` by the Docker build process.

### Running with Docker

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

---

# 🖥️ Command-Line Interface (CLI)

PDFStract includes a powerful CLI for batch processing and automation.

### Quick CLI Examples

```bash
# List available libraries
pdfstract libs

# Convert a single PDF
pdfstract convert document.pdf --library unstructured --output result.md

# Compare multiple libraries on one PDF
pdfstract compare sample.pdf -l unstructured -l marker -l pymupdf4llm --output ./comparison

# Batch convert 100+ PDFs in parallel
pdfstract batch ./documents --library unstructured --output ./converted --parallel 4

# Test which library works best on your corpus
pdfstract batch-compare ./papers -l marker -l unstructured --max-files 50 --output ./test
```

### CLI Features

✨ **Full Features:**
- Single file conversion
- Multi-library comparison
- Parallel batch processing (1-16 workers)
- Batch quality testing across corpus
- JSON reporting with detailed statistics
- Error handling and retry options
- Progress indicators and rich formatting

📊 **Batch Processing:**
- Convert 1000+ PDFs with parallel workers
- Detailed JSON reports (success rate, per-file status)
- Automatic error handling and logging
- Perfect for production jobs and legacy migrations

→ **[Full CLI Documentation](CLI_README.md)** - See complete guide with real-world examples

---

# API 

**Check available libraries**:
```bash
curl http://localhost:8000/libraries
```

Response:
```json
{
  "libraries": [
    {
      "name": "pymupdf4llm",
      "available": true,
      "error": null
    },
    {
      "name": "deepseekocr",
      "available": false,
      "error": "GPU required but not available"
    }
  ]
}
```

**Convert a PDF**:
```bash
curl -X POST \
  -F "file=@sample.pdf" \
  -F "library=unstructured" \
  -F "output_format=markdown" \
  http://localhost:8000/convert
```

Response:
```json
{
  "success": true,
  "library_used": "unstructured",
  "filename": "sample.pdf",
  "format": "markdown",
  "content": "# Document Title\n\n... extracted markdown ..."
}
```

**For Batch Processing:** Use the CLI instead
```bash
pdfstract batch ./documents --library unstructured --output ./converted --parallel 4
```

Advantages of CLI for batch jobs:
- Parallel processing with configurable workers
- JSON report with statistics (success rate, per-file status)
- Error handling and retry options
- Perfect for production automation
- See [CLI_README.md](CLI_README.md) for full batch documentation

## API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|-----------|
| `/` | GET | Web interface | - |
| `/health` | GET | Health check | - |
| `/libraries` | GET | List available libraries | - |
| `/convert` | POST | Convert PDF | `file`, `library`, `output_format` |


## 📊 Performance Comparison ( Based on our evaluation )

Use the built-in timer feature to benchmark:

| Library | Speed | Quality | Best For |
|---------|-------|---------|----------|
| pymupdf4llm | ⚡⚡⚡ | ⭐⭐ | Simple text extraction |
| unstructured | ⚡⚡ | ⭐⭐⭐ | Complex layouts |
| markitdown | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| marker | ⚡ | ⭐⭐⭐⭐ | Highest quality (ML-based) |
| docling | ⚡ | ⭐⭐⭐⭐ | Document intelligence |
| paddleocr | ⚡ | ⭐⭐⭐ | Scanned PDFs |
| deepseekocr | ⚡ | ⭐⭐⭐ | Scanned PDFs |
| pytesseract | ⚡ | ⭐⭐⭐ | Scanned PDFs |

**NOTE**: The performance comparison is based on the performance of the libraries when used with the default settings of the application. The performance may vary depending on the complexity of the PDF and the settings of the library.

## 🔐 Security

- File uploads are stored temporarily and deleted after conversion
- No data is persisted or logged
- Use HTTPS in production
- API endpoints are not authenticated (add authentication for production)


## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## 📞 Support

If you encounter issues or have questions - please create an issue

## 🌟 Please leave a star if you find this project useful

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **React**: UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Beautiful icon library
- All the amazing PDF extraction libraries (PyMuPDF, Marker, Docling, etc.)

---

**Made with ❤️ for PDF enthusiasts **
