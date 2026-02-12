---
sidebar_position: 1
---

# Web UI Overview

PDFStract includes a modern web interface built with React and Vite, providing an intuitive way to convert PDFs, chunk text, and preview results without writing any code.

## Features

🎨 **Modern Interface** - Clean, responsive React UI with dark/light mode  
📁 **Drag & Drop** - Easy file upload with visual feedback  
⚡ **Real-time Processing** - Watch conversions happen in real-time  
🔍 **Live Preview** - See extracted text and chunks immediately  
🛠️ **Tool Selection** - Choose from all available converters and chunkers  
📊 **Results Dashboard** - Detailed statistics and download options  
🌐 **Multi-format Export** - JSON, text, markdown output formats

## Getting Started

### Start the Web Server

```bash
# Start PDFStract web interface
pdfstract web

# Or specify custom port
pdfstract web --port 3000

# With custom host
pdfstract web --host 0.0.0.0 --port 8080
```

Open http://localhost:8000 in your browser.

### Using Docker (Recommended)

```bash
# Using make (downloads models + builds + starts)
make up

# Other useful commands:
make logs     # View container logs
make down     # Stop services
make status   # Show running containers
make rebuild  # Rebuild and restart
```

## Interface Walkthrough

### Home Screen

The main interface provides:

- **Upload Area**: Drag and drop PDFs or click to browse
- **Library Selection**: Choose PDF conversion library
- **Chunker Selection**: Select text chunking method
- **Settings Panel**: Configure chunk size, overlap, and output format

### Upload & Processing

1. **Select PDF**: Drag files to upload area or click "Choose Files"
2. **Choose Tools**: Select converter and chunker from dropdowns
3. **Configure Settings**: Set chunk size, overlap, and options
4. **Start Processing**: Click "Convert & Chunk" to begin
5. **Watch Progress**: Real-time progress bar and status updates

### Results View

After processing, you'll see:

- **Summary Statistics**: Total chunks, processing time, file info
- **Text Preview**: Extracted text with highlighting
- **Chunk Explorer**: Browse individual chunks with metadata
- **Download Options**: Export as JSON, text, or markdown

## Configuration Options

### PDF Conversion

**Library Selection**:
- **Docling** - Balanced performance and quality (default)
- **Marker** - Best for complex layouts and figures
- **PyMuPDF4LLM** - Fastest for simple documents  
- **Unstructured** - Great for document structure
- **PaddleOCR** - Best for scanned/image PDFs

**Options**:
- Extract images from PDF
- Preserve document structure
- Select specific page ranges
- Set processing timeout

### Text Chunking

**Chunker Selection**:
- **Token** - Simple token-based splitting (default)
- **Semantic** - AI-powered semantic chunking
- **Recursive** - Smart recursive text splitting
- **Sentence** - Sentence-boundary aware
- **Code** - Code-aware chunking

**Settings**:
- **Chunk Size**: Target size in tokens (default: 512)
- **Overlap**: Overlap between chunks (default: 50)
- **Min Size**: Minimum chunk size threshold
- **Max Size**: Maximum chunk size limit

## Advanced Features

### Batch Processing

Process multiple PDFs:

1. Select multiple files in upload area
2. Choose consistent settings for all files
3. Start batch processing
4. Download individual or combined results

### Comparison Mode

Compare different tools on the same document:

1. Upload a PDF
2. Enable "Comparison Mode" in settings  
3. Select multiple converters/chunkers to compare
4. View side-by-side results with performance metrics

### Custom Preprocessing

Configure text preprocessing options:

- Remove headers/footers
- Clean whitespace and formatting
- Filter by content type
- Apply custom regex patterns

## API Integration

The web interface is built on the same REST API you can use programmatically:

### Key Endpoints

```bash
# Upload and convert
POST /api/convert
{
  "file": "base64_encoded_pdf",
  "library": "docling",
  "options": {}
}

# Chunk text
POST /api/chunk  
{
  "text": "content to chunk",
  "chunker": "semantic",
  "chunk_size": 512,
  "chunk_overlap": 50
}

# Combined processing
POST /api/process
{
  "file": "base64_encoded_pdf", 
  "converter": "marker",
  "chunker": "semantic",
  "chunk_size": 1024
}
```

### Response Format

```json
{
  "success": true,
  "data": {
    "text": "extracted text...",
    "chunks": [
      {
        "chunk_id": 0,
        "text": "chunk content...",
        "metadata": {
          "tokens": 487,
          "start_pos": 0,
          "end_pos": 512
        }
      }
    ],
    "stats": {
      "total_chunks": 15,
      "total_tokens": 7320,
      "processing_time": 3.2,
      "converter_used": "docling",
      "chunker_used": "semantic"
    }
  }
}
```

## Customization

### Themes

The interface supports custom themes:

```css
/* Light theme (default) */
--primary-color: #2563eb;
--background: #ffffff;
--text-color: #1f2937;

/* Dark theme */
--primary-color: #3b82f6;
--background: #111827; 
--text-color: #f9fafb;
```

### Environment Variables

Configure the web server:

```bash
# Server settings
export PDFSTRACT_HOST=0.0.0.0
export PDFSTRACT_PORT=8000
export PDFSTRACT_DEBUG=false

# Processing settings  
export PDFSTRACT_MAX_FILE_SIZE=50MB
export PDFSTRACT_TIMEOUT=300
export PDFSTRACT_CACHE_DIR=/tmp/pdfstract

# Security
export PDFSTRACT_CORS_ORIGINS=http://localhost:3000
export PDFSTRACT_API_KEY_REQUIRED=false
```

## Deployment

### Production Setup

For production deployment:

```bash
# Build optimized web assets
cd frontend
npm run build

# Start production server
pdfstract web --host 0.0.0.0 --port 8000 --production
```

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  pdfstract-web:
    image: aksarav/pdfstract:latest
    ports:
      - "8000:8000"
    environment:
      - PDFSTRACT_HOST=0.0.0.0
      - PDFSTRACT_PORT=8000
    volumes:
      - ./uploads:/app/uploads
      - ./cache:/app/cache
    command: web --production
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name pdfstract.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Handle file uploads
    client_max_body_size 100M;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
```

## Troubleshooting

### Common Issues

**Web interface won't start**:
```bash
# Check if port is available
lsof -i :8000

# Try different port
pdfstract web --port 8080
```

**File upload fails**:
- Check file size limits (default: 50MB)
- Verify file permissions
- Check available disk space

**Conversion errors**:
- Enable verbose logging: `pdfstract web --verbose`
- Check browser developer console
- Try different conversion library

**Performance issues**:
- Reduce chunk size for faster processing
- Use simpler converters (pymupdf4llm)
- Enable caching for repeated files

### Development

To contribute to the web interface:

```bash
# Clone repository
git clone https://github.com/aksarav/pdfstract.git
cd pdfstract

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev

# In another terminal, start backend
cd ..
python run.py
```

## Next Steps

Continue exploring PDFStract:

- **[Python API](../api/overview)** - Use in your applications
- **[CLI Guide](../cli/overview)** - Command-line interface
- **[Installation](../installation)** - Advanced installation options

Ready to try the visual interface? Run `pdfstract web` and open http://localhost:8000! 🚀