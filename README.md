# PDFStract - Extract Data from PDF and Benchmark - CLI - WEBUI - API

A modern web application for converting PDFs to multiple formats using various state-of-the-art extraction libraries. Built with **FastAPI** backend and **React** frontend with a beautiful, responsive UI.

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

### Running with VS Code Debugger

1. Press `F5` or go to Run → Start Debugging
2. The debugger will use the configuration in `.vscode/launch.json`
3. Set breakpoints and debug your FastAPI backend

## 🖥️ Command-Line Interface (CLI)

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

## 📖 Usage

### Web Interface (React Frontend)

**Single Conversion**:
1. **Upload PDF**: Drag & drop or click to select a PDF file
2. **Select Library**: Choose your preferred conversion library from the dropdown
3. **Choose Format**: Select output format (Markdown, JSON, or Plain Text)
4. **Convert**: Click "Convert PDF" button
5. **View Results**: 
   - See original PDF on the left
   - View converted content on the right
   - Switch between "Source" and "Preview" tabs
6. **Download**: Click "Download" to save the results
7. **Performance**: Real-time timer shows conversion speed

**Compare Multiple Models** (New Feature):
1. **Upload PDF**: Select a PDF file
2. **Click "Compare Models"**: Opens library selection modal
3. **Select Libraries**: Choose 1-3 converters to compare
4. **Watch Progress**: Real-time progress bar shows which models are running
5. **View Results Grid**: See all conversions in a table with:
   - Time taken for each
   - Output file size
   - Success/Failed/Timeout status
6. **Expand Details**: Click a row to see full content
7. **Download**: Download individual or all results
8. **History**: Recent comparisons shown in left sidebar

### API Usage

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

## 🏗️ Project Structure

```
pdfstract/
├── main.py                          # FastAPI application with endpoints
├── pyproject.toml                   # Python dependencies (uv)
├── uv.lock                          # Locked dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker compose setup
├── README.md                        # This file
│
├── frontend/                        # React application (Vite + Tailwind)
│   ├── src/
│   │   ├── App.jsx                 # Main React component & routes
│   │   ├── components/
│   │   │   ├── CompareModal.jsx           # Library selection modal
│   │   │   ├── RecentComparisons.jsx      # History sidebar
│   │   │   ├── ComparisonResults.jsx      # Results display grid
│   │   │   └── ui/                       # UI components (button, card, etc.)
│   │   ├── index.css               # Global styles
│   │   └── main.jsx                # React entry point
│   ├── dist/                       # Built frontend (production)
│   ├── vite.config.js              # Vite configuration & proxy setup
│   ├── tailwind.config.js          # Tailwind CSS config
│   ├── package.json                # Node dependencies
│   └── index.html                  # HTML entry point
│
├── services/                        # Backend services
│   ├── db_service.py               # SQLite database operations
│   ├── queue_manager.py            # Parallel execution (max 3)
│   ├── results_manager.py          # File storage for results
│   ├── ocrfactory.py               # Converter factory & registry
│   ├── base.py                     # Base converter class
│   ├── logger.py                   # Logging configuration
│   └── converters/                 # Converter implementations
│       ├── pymupdf4llm_converter.py
│       ├── unstructured_converter.py
│       ├── mineru_converter.py
│       ├── marker_converter.py
│       ├── paddleocr_converter.py
│       └── ... (more converters)
│
├── scripts/
│   └── setup-mineru.sh             # MinerU separate venv setup
│
├── data/
│   └── tasks.db                    # SQLite database (auto-created)
│
├── results/                        # Conversion results storage
│   └── task_*/                     # Per-task directories
│
└── .vscode/
    └── launch.json                 # VS Code debugger config
```

## 🔧 Configuration

### Environment Variables

Currently, no environment variables are required. The application is configured via:
- `main.py`: Core FastAPI setup
- `pyproject.toml`: Python dependencies
- `docker-compose.yml`: Docker configuration

### Frontend Configuration

The React frontend is configured via:
- `frontend/vite.config.js`: Vite build config with API proxy
- `frontend/tailwind.config.js`: Tailwind CSS theming
- `frontend/package.json`: Node dependencies

### API Proxy Setup

The frontend development server proxies API calls to the backend:
```javascript
// frontend/vite.config.js
server: {
  proxy: {
    '/libraries': { target: 'http://localhost:8000' },
    '/convert': { target: 'http://localhost:8000' },
    '/compare': { target: 'http://localhost:8000' },
    '/history': { target: 'http://localhost:8000' },
    '/health': { target: 'http://localhost:8000' },
  }
}
```

### Customization

**Add a new converter**:

1. Create a new file in `services/converters/`:
```python
from services.base import PDFConverter

class MyConverter(PDFConverter):
    @property
    def name(self) -> str:
        return "myconverter"
    
    @property
    def available(self) -> bool:
        return True
    
    async def convert_to_md(self, file_path: str) -> str:
        # Implementation
        pass
```

2. Register in `services/ocrfactory.py`:
```python
from services.converters.myconverter import MyConverter

# In _register_default_converters():
converters.append(MyConverter())

# In list_all_converters():
all_converters.append("myconverter")
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Library shows as unavailable
- **Solution**: Check dependencies with `uv sync` and verify system requirements

**Issue**: DeepSeek-OCR unavailable
- **Solution**: Requires CUDA GPU. Install CUDA toolkit or use CPU-only alternatives

**Issue**: Docker container can't find dependencies
- **Solution**: Rebuild with `docker-compose up --build` (no cache)

**Issue**: Large PDF timeout
- **Solution**: Some libraries (marker, unstructured) are slower. Try pymupdf4llm for faster processing

### System Requirements

**For OCR libraries** (PaddleOCR, Tesseract, DeepSeek-OCR):
- macOS/Linux: System libraries may be needed
- Windows: May require Visual C++ build tools

## 📊 Performance Comparison

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

## 📝 Development

### Frontend Development (Hot Reload)

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173` with hot-reload enabled.

### Backend Development (With Debugger)

Use VS Code's Run & Debug feature:
1. Press `F5` or go to Run → Start Debugging
2. Breakpoints and debugging work via `.vscode/launch.json`
3. Backend reloads on file changes via `--reload` flag

### Adding Frontend Dependencies

```bash
cd frontend
npm install <package-name>
```

### Building Frontend for Production

```bash
cd frontend
npm run build
```

Output: `frontend/dist/` → Gets copied to `/app/static` in Docker

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes.

## 🌟 Features Roadmap

- [ ] Batch PDF conversion
- [ ] Convert and Compare multiple PDFs and Generate a Report
- [ ] Conversion history and Task Management
- [ ] Cloud storage integration - Read from and write to cloud storage
- [ ] REST API documentation (Swagger UI)

## 📞 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review converter-specific documentation
3. Open an issue on GitHub

## 🌟 Please leave a star if you find this project useful

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **React**: UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Beautiful icon library
- All the amazing PDF extraction libraries (PyMuPDF, Marker, Docling, etc.)

---

**Made with ❤️ for PDF enthusiasts **
