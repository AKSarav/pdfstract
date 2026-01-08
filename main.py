from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import os
import tempfile
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

from services.ocrfactory import OCRFactory
from services.base import OutputFormat
from services.logger import logger
from services.db_service import DatabaseService
from services.queue_manager import QueueManager
from services.results_manager import ResultsManager

app = FastAPI(title="PDFStract - Unified PDF extraction wrapper", description="Convert PDF files to Markdown using various libraries")

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

# Initialize comparison services
db_service = DatabaseService()
# Initialize factory (singleton pattern) with DB service
factory = OCRFactory(db_service)
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
    """Get list of available conversion libraries"""
    return {"libraries": factory.list_all_converters()}

@app.post("/libraries/status")
async def set_library_status(
    library_name: str = Form(...),
    is_enabled: bool = Form(...)
):
    """Enable or disable a library"""
    try:
        # Update DB
        db_service.set_library_status(library_name, is_enabled)
        
        # Refresh factory
        factory.refresh_converters()
        
        return {
            "status": "success", 
            "library": library_name, 
            "enabled": is_enabled,
            "message": f"Library {library_name} {'enabled' if is_enabled else 'disabled'}"
        }
    except Exception as e:
        logger.error(f"Error setting library status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        logger.info(f"Starting conversion with library: {library}, format: {output_format}")
        # Convert using factory
        result = await factory.convert_async(
            converter_name=library,
            file_path=temp_file_path,
            output_format=format_enum
        )
        
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
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


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
        converter = factory.get_converter(library_name)
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
        api_prefixes = ("libraries", "convert", "compare", "history", "stats", "health", "static")
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