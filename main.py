from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import asyncio
import json
import uuid
import traceback
from datetime import datetime
from pathlib import Path

from services.ocrfactory import OCRFactory
from services.base import OutputFormat
from services.logger import logger
from services.db_service import DatabaseService
from services.queue_manager import QueueManager
from services.results_manager import ResultsManager
from services.chunker_factory import get_chunker_factory

app = FastAPI(title="PDFStract - Unified PDF extraction wrapper", description="Convert PDF files to Markdown using various libraries")

# Global exception handler to prevent crashes (but don't catch HTTPExceptions)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions to prevent process crashes"""
    # Don't handle HTTPExceptions - let FastAPI handle those
    if isinstance(exc, HTTPException):
        raise exc
    
    error_msg = str(exc)
    error_traceback = traceback.format_exc()
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {error_msg}")
    logger.error(f"Traceback: {error_traceback}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {error_msg}"}
    )

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if they exist (built React app)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lazy initialization - factory will be created on first use
_factory = None
def get_factory():
    """Lazy factory initialization to avoid blocking startup with model downloads"""
    global _factory
    if _factory is None:
        _factory = OCRFactory()
    return _factory

# Initialize comparison services
db_service = DatabaseService()
queue_manager = QueueManager(db_service)
results_manager = ResultsManager()

@app.get("/")
async def read_root():
    """Serve the React app"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        raise HTTPException(
            status_code=404,
            detail="React app not built. Run 'cd frontend && npm run build' to build the frontend."
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/libraries")
async def get_available_libraries():
    """Get list of available conversion libraries with download status"""
    return {"libraries": get_factory().list_all_converters()}


@app.get("/libraries/{library_name}/status")
async def get_library_status(library_name: str):
    """Get detailed status for a specific library"""
    status = get_factory().get_converter_status(library_name)
    if not status:
        raise HTTPException(status_code=404, detail=f"Library '{library_name}' not found")
    return status


@app.post("/libraries/{library_name}/download")
async def download_library_models(library_name: str):
    """
    Trigger on-demand model download for a specific library.
    
    This endpoint downloads required models for converters like marker, docling, etc.
    The download happens asynchronously and may take several minutes.
    """
    result = await get_factory().prepare_converter(library_name)
    
    if result["success"]:
        return JSONResponse({
            "success": True,
            "library": library_name,
            "message": result.get("message", "Models downloaded successfully")
        })
    else:
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Download failed")
        )


@app.post("/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    library: str = Form(...),
    output_format: str = Form("markdown")
):
    """Convert PDF using specified library and format"""
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate output format
    try:
        format_enum = OutputFormat(output_format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output format. Supported: {[f.value for f in OutputFormat]}"
        )
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()  # Ensure all data is written to disk
            temp_file_path = temp_file.name
        
        # Log file size for debugging
        file_size = os.path.getsize(temp_file_path)
        logger.info(f"Saved uploaded file to {temp_file_path}, size: {file_size} bytes")
        
        logger.info(f"Starting conversion with library: {library}, format: {output_format}")
        
        # Convert using factory with timeout protection
        try:
            result = await asyncio.wait_for(
                get_factory().convert_async(
                    converter_name=library,
                    file_path=temp_file_path,
                    output_format=format_enum
                ),
                timeout=300.0  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            error_msg = f"Conversion timed out after 5 minutes"
            logger.error(error_msg)
            raise HTTPException(status_code=504, detail=error_msg)
        
        logger.info(f"Conversion successful with {library}")
        response_data = {
            "success": True,
            "library_used": library,
            "filename": file.filename,
            "format": output_format
        }
        
        if format_enum == OutputFormat.JSON:
            response_data["data"] = result
        else:
            response_data["content"] = result
        
        return JSONResponse(response_data)
    
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except ValueError as e:
        # User-friendly errors (e.g., text-only PDF for DeepSeek-OCR)
        error_msg = str(e)
        logger.warning(f"Conversion rejected: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Conversion failed: {error_msg}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=error_msg)
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")


@app.post("/compare")
async def compare_pdf(
    file: UploadFile = File(...),
    libraries: str = Form(...),
    output_format: str = Form("markdown")
):
    """Start a comparison task with multiple libraries"""
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Parse libraries
    try:
        lib_list = json.loads(libraries)
    except:
        raise HTTPException(status_code=400, detail="Invalid libraries format")
    
    if not isinstance(lib_list, list) or len(lib_list) == 0:
        raise HTTPException(status_code=400, detail="No libraries selected")
    
    # Limit to max 3
    if len(lib_list) > 3:
        lib_list = lib_list[:3]
    
    # Validate output format
    try:
        format_enum = OutputFormat(output_format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output format. Supported: {[f.value for f in OutputFormat]}"
        )
    
    # Generate task ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        temp_file_path = tmp.name
    
    try:
        logger.info(f"Starting comparison task {task_id} with libraries: {lib_list}")
        
        # Create task record
        db_service.create_task(task_id, file.filename, len(content), output_format)
        
        # Create results directory
        results_manager.create_task_directory(task_id)
        
        # Start comparison asynchronously (don't wait)
        asyncio.create_task(
            _run_comparison_async(task_id, temp_file_path, lib_list, output_format)
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "filename": file.filename,
            "libraries": lib_list,
            "estimated_time": f"~{len(lib_list) * 3}s"
        }
    
    except Exception as e:
        logger.error(f"Error starting comparison: {str(e)}")
        db_service.complete_task(task_id, 'failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare/{task_id}")
async def get_comparison_status(task_id: str):
    """Get comparison status and progress"""
    task_data = db_service.get_task_with_comparisons(task_id)
    
    if not task_data['task']:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_data['task']
    comparisons = task_data['comparisons']
    
    completed = sum(1 for c in comparisons if c['status'] in ['success', 'failed', 'timeout'])
    total = len(comparisons) if comparisons else 0
    
    return {
        "task_id": task_id,
        "status": task['status'],
        "filename": task['filename'],
        "progress": {
            "completed": completed,
            "total": total,
            "percentage": int((completed / total * 100) if total > 0 else 0)
        },
        "comparisons": [
            {
                "library_name": c['library_name'],
                "status": c['status'],
                "duration_seconds": c['duration_seconds'],
                "output_size_bytes": c['output_size_bytes'],
                "error_message": c['error_message']
            }
            for c in comparisons
        ],
        "total_duration_seconds": task['total_duration_seconds']
    }


@app.get("/compare/{task_id}/results")
async def get_comparison_results(task_id: str):
    """Get detailed comparison results"""
    task_data = db_service.get_task_with_comparisons(task_id)
    
    if not task_data['task']:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_data


@app.get("/compare/{task_id}/content/{library}")
async def get_comparison_content(task_id: str, library: str):
    """Get conversion content for a specific library"""
    task_data = db_service.get_task_with_comparisons(task_id)
    
    if not task_data['task']:
        raise HTTPException(status_code=404, detail="Task not found")
    
    output_format = task_data['task']['output_format']
    content = results_manager.get_conversion_content(task_id, library, output_format)
    
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {"library": library, "content": content}


@app.get("/compare/{task_id}/download")
async def download_all_comparisons(task_id: str):
    """Download all comparison results as a zip file"""
    import zipfile
    
    task_data = db_service.get_task_with_comparisons(task_id)
    
    if not task_data['task']:
        raise HTTPException(status_code=404, detail="Task not found")
    
    output_format = task_data['task']['output_format']
    ext = 'json' if output_format == 'json' else 'md' if output_format == 'markdown' else 'txt'
    
    # Create zip in memory
    import io
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add metadata file
        metadata = {
            'task_id': task_data['task']['task_id'],
            'filename': task_data['task']['filename'],
            'created_at': task_data['task']['created_at'],
            'total_duration': task_data['task']['total_duration_seconds'],
            'output_format': output_format,
            'comparisons': task_data['comparisons']
        }
        zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        # Add conversion files
        for comparison in task_data['comparisons']:
            library = comparison['library_name']
            content = results_manager.get_conversion_content(task_id, library, output_format)
            if content:
                filename = f"{library}_result.{ext}"
                zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=comparison_{task_id}.zip"}
    )


@app.get("/history")
async def get_history(limit: int = 20):
    """Get task history"""
    tasks = db_service.get_recent_tasks(limit)
    return {"tasks": tasks}


@app.get("/stats/libraries")
async def get_library_stats():
    """Get statistics on all conversions"""
    stats = db_service.get_library_stats()
    return {"stats": stats}


# ============================================================================
# CHUNKING ENDPOINTS
# ============================================================================

@app.get("/chunkers")
async def get_available_chunkers():
    """Get list of available chunkers with their parameter schemas"""
    try:
        factory = get_chunker_factory()
        return {"chunkers": factory.list_all_chunkers()}
    except Exception as e:
        logger.error(f"Error listing chunkers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chunk")
async def chunk_text(
    text: str = Form(...),
    chunker: str = Form(...),
    params: str = Form("{}")
):
    """
    Chunk text using the specified chunker.
    
    Args:
        text: The text to chunk
        chunker: Name of the chunker to use (token, sentence, recursive, table, etc.)
        params: JSON string of chunker-specific parameters
        
    Returns:
        ChunkingResult with chunks and metadata
    """
    # Parse parameters
    try:
        chunker_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid params JSON format")
    
    try:
        factory = get_chunker_factory()
        
        logger.info(f"Chunking text with chunker: {chunker}, params: {chunker_params}")
        
        # Chunk with timeout protection
        result = await asyncio.wait_for(
            factory.chunk_with_result(chunker, text, **chunker_params),
            timeout=60.0  # 1 minute timeout for chunking
        )
        
        logger.info(f"Chunking successful: {result.total_chunks} chunks created")
        
        return JSONResponse({
            "success": True,
            "chunker": chunker,
            "result": result.to_dict()
        })
        
    except asyncio.TimeoutError:
        error_msg = "Chunking timed out after 1 minute"
        logger.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Chunking rejected: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Chunking failed: {error_msg}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/convert-and-chunk")
async def convert_and_chunk(
    file: UploadFile = File(...),
    library: str = Form(...),
    chunker: str = Form(...),
    output_format: str = Form("markdown"),
    chunker_params: str = Form("{}")
):
    """
    Convert PDF and chunk the result in one operation.
    
    Args:
        file: PDF file to convert
        library: Conversion library to use
        chunker: Chunker to use for splitting the converted text
        output_format: Output format (markdown, text)
        chunker_params: JSON string of chunker-specific parameters
        
    Returns:
        Combined conversion and chunking result
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate output format - chunking only works with text-based formats
    if output_format.lower() == "json":
        raise HTTPException(
            status_code=400, 
            detail="Chunking requires text-based output. Use 'markdown' or 'text' format."
        )
    
    try:
        format_enum = OutputFormat(output_format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output format. Supported: markdown, text"
        )
    
    # Parse chunker parameters
    try:
        chunk_params = json.loads(chunker_params) if chunker_params else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid chunker_params JSON format")
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            temp_file_path = temp_file.name
        
        logger.info(f"Starting convert-and-chunk: library={library}, chunker={chunker}")
        
        # Step 1: Convert PDF
        try:
            converted_text = await asyncio.wait_for(
                get_factory().convert_async(
                    converter_name=library,
                    file_path=temp_file_path,
                    output_format=format_enum
                ),
                timeout=300.0  # 5 minute timeout for conversion
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Conversion timed out after 5 minutes")
        
        logger.info(f"Conversion successful, text length: {len(converted_text)}")
        
        # Step 2: Chunk the converted text
        factory = get_chunker_factory()
        try:
            chunking_result = await asyncio.wait_for(
                factory.chunk_with_result(chunker, converted_text, **chunk_params),
                timeout=60.0  # 1 minute timeout for chunking
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Chunking timed out after 1 minute")
        
        logger.info(f"Chunking successful: {chunking_result.total_chunks} chunks")
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "library_used": library,
            "chunker_used": chunker,
            "format": output_format,
            "conversion": {
                "text_length": len(converted_text),
                "content": converted_text
            },
            "chunking": chunking_result.to_dict()
        })
        
    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Convert-and-chunk rejected: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Convert-and-chunk failed: {error_msg}")
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=error_msg)
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")


# ============================================================================
# END CHUNKING ENDPOINTS
# ============================================================================


@app.delete("/compare/{task_id}")
async def delete_comparison(task_id: str):
    """Delete comparison task and results"""
    db_service.delete_task(task_id)
    results_manager.delete_task_results(task_id)
    logger.info(f"Deleted task {task_id}")
    
    return {"status": "deleted", "task_id": task_id}


async def _run_comparison_async(task_id, file_path, libraries, output_format):
    """Background task to run comparisons"""
    try:
        # Run comparisons with queue manager
        results = await queue_manager.run_comparisons(
            file_path, 
            task_id, 
            libraries,
            output_format,
            _convert_single_library
        )
        
        # Mark task as completed
        db_service.complete_task(task_id, 'completed')
        logger.info(f"Comparison task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Comparison task {task_id} failed: {str(e)}")
        db_service.complete_task(task_id, 'failed')
    
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)


async def _convert_single_library(task_id, library_name, file_path, output_format):
    """Convert with a single library and save results"""
    import time
    
    start_time = time.time()
    
    try:
        # Get converter
        converter = get_factory().get_converter(library_name)
        if not converter:
            raise ValueError(f"Converter {library_name} not available")
        
        # Convert
        format_enum = OutputFormat(output_format)
        if format_enum == OutputFormat.MARKDOWN:
            result = await converter.convert_to_md(file_path)
        elif format_enum == OutputFormat.JSON:
            result = await converter.convert_to_json(file_path)
        else:
            result = await converter.convert_to_text(file_path)
        
        # Save result
        output_file, output_size = results_manager.save_conversion(
            task_id, library_name, result, output_format
        )
        
        # Record in DB
        duration = time.time() - start_time
        db_service.complete_comparison(
            task_id, library_name, duration, output_file, output_size
        )
        
        logger.info(f"Converted {library_name} for task {task_id} in {duration:.2f}s")
        
        return {"library": library_name, "status": "success", "duration": duration}
    
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        logger.error(f"Error converting {library_name} for task {task_id}: {error_msg}")
        
        # Record error in DB
        db_service.complete_comparison(
            task_id, library_name, duration, None, None, error_msg
        )
        
        raise

# Catch-all route for React Router (must be after all API routes)
# This only serves the React app for non-API paths
if static_dir.exists():
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Catch-all route to serve React app for client-side routing"""
        # Skip API routes - these should be 404 handled by FastAPI
        api_prefixes = ("libraries", "convert", "compare", "history", "stats", "health", "static", "chunkers", "chunk")
        if any(full_path.startswith(prefix) for prefix in api_prefixes):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve React app for all other routes (client-side routing)
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="React app not built")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 