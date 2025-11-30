# PDFStract - PDF Extraction & Conversion

A modern web application for converting PDFs to multiple formats using various state-of-the-art extraction libraries. Built with **FastAPI** backend and **React** frontend with a beautiful, responsive UI.

![UI Screenshot](UI.png)

![UI Screenshot 2 ](UI2.png)

## ✨ Features

- 🚀 **10+ Conversion Libraries**: PyMuPDF4LLM, MarkItDown, Marker, Docling, PaddleOCR, DeepSeek-OCR, Tesseract, MinerU, Unstructured, and more
- 📱 **Modern React UI**: Beautiful, responsive design with Tailwind CSS
- 🎯 **Multiple Output Formats**: Markdown, JSON, and Plain Text
- ⏱️ **Performance Benchmarking**: Real-time timer shows conversion speed for each library
- 👁️ **Live Preview**: View converted content with syntax highlighting
- 🔄 **Library Status Dashboard**: See which libraries are available/unavailable with error messages
- 💾 **Easy Download**: Download results in your preferred format
- 🐳 **Docker Support**: One-command deployment
- 🔗 **REST API**: Programmatic access to conversion features
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
| **mineru** | >=2.6.4 | Advanced | Premium | Separate venv installation |

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.13+
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

4. **Setup MinerU (optional)**:
```bash
bash scripts/setup-mineru.sh
```

### Running Locally

**Option 1: Development Mode with Auto-reload**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 2: Using Python directly**
```bash
uv run python main.py
```

**Open your browser**:
```
http://localhost:8000
```

### Running with Docker

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

### Running with VS Code Debugger

1. Press `F5` or go to Run → Start Debugging
2. The debugger will use the configuration in `.vscode/launch.json`
3. Set breakpoints and debug your FastAPI backend

## 📖 Usage

### Web Interface

1. **Upload PDF**: Drag & drop or click to select a PDF file
2. **Select Library**: Choose your preferred conversion library from the dropdown
3. **Choose Format**: Select output format (Markdown, JSON, or Plain Text)
4. **Convert**: Click "Convert PDF" button
5. **View Results**: 
   - See original PDF on the left
   - View converted content on the right
   - Switch between "Source" and "Preview" tabs
6. **Download**: Click "Download" to save the results
7. **Benchmark**: Check the time taken to compare library performance

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
├── main.py                          # FastAPI application
├── pyproject.toml                   # Python dependencies (uv)
├── uv.lock                          # Locked dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker compose setup
├── README.md                        # This file
│
├── frontend/                        # React application
│   ├── src/
│   │   ├── App.jsx                 # Main React component
│   │   ├── components/
│   │   │   └── ui/                 # UI components (button, card, etc.)
│   │   └── index.css               # Global styles
│   ├── vite.config.js              # Vite configuration
│   ├── tailwind.config.js          # Tailwind CSS config
│   ├── package.json                # Node dependencies
│   └── index.html                  # HTML entry point
│
├── services/                        # Backend services
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
│   └── setup-mineru.sh             # MinerU setup script
│
├── templates/                       # Legacy templates
│   └── index.html
│
├── uploads/                         # Temporary file storage
└── .vscode/
    └── launch.json                 # VS Code debugger config
```

## 🔧 Configuration

### Environment Variables

Currently, no environment variables are required. The application is configured via:
- `main.py`: Core FastAPI setup
- `pyproject.toml`: Python dependencies
- `docker-compose.yml`: Docker configuration

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

**Issue**: MinerU not working
- **Solution**: Run `bash scripts/setup-mineru.sh` to set up the separate environment

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

**For MinerU**:
- Runs in isolated venv to avoid dependency conflicts
- Requires: Python 3.13, sufficient disk space (~2GB)

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
| mineru | ⚡ | ⭐⭐⭐ | Scanned PDFs |

**NOTE**: The performance comparison is based on the performance of the libraries when used with the default settings of the application. The performance may vary depending on the complexity of the PDF and the settings of the library.

## 🔐 Security

- File uploads are stored temporarily and deleted after conversion
- No data is persisted or logged
- Use HTTPS in production
- API endpoints are not authenticated (add authentication for production)

## 📝 Development

### Frontend Development

```bash
cd frontend
npm run dev
```

Frontend will hot-reload at `http://localhost:5173`

### Debug Backend

Use VS Code's Run & Debug feature (F5) configured in `.vscode/launch.json`

### Add Frontend Dependencies

```bash
cd frontend
npm install <package-name>
```

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
