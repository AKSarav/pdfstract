from typing import Dict, Any, Optional
import asyncio
import shutil
import re
from pathlib import Path
from services.base import PDFConverter, DownloadStatus
from services.logger import logger

try:
    from marker.converters.pdf import PdfConverter  # type: ignore
    from marker.models import create_model_dict  # type: ignore
    from marker.output import text_from_rendered  # type: ignore
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    PdfConverter = None
    create_model_dict = None
    text_from_rendered = None

# Global async lock to prevent race conditions during model initialization
_init_lock = asyncio.Lock()

class MarkerConverter(PDFConverter):
    """Converter implementation for marker library"""
    
    def __init__(self):
        self._converter = None
        self._initialized = False
        self._download_status = DownloadStatus.NOT_STARTED
        self._download_error: Optional[str] = None
        self._is_downloading = False
    
    def _clear_datalab_cache(self):
        """Clear the entire datalab models cache to avoid 'already exists' errors"""
        cache_dirs = [
            Path("/root/.cache/datalab/models"),  # Docker container path
            Path.home() / ".cache" / "datalab" / "models",  # Local path
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                logger.warning(f"Marker: Clearing datalab model cache at {cache_dir}")
                try:
                    shutil.rmtree(cache_dir)
                    logger.info(f"Marker: Successfully cleared {cache_dir}")
                except Exception as e:
                    logger.warning(f"Marker: Could not clear {cache_dir}: {e}")
    
    def _clear_conflicting_cache(self, error_msg: str):
        """Clear the specific cache directory that's causing conflicts"""
        # Extract the path from error message like:
        # "Destination path '/root/.cache/datalab/models/text_detection/2025_05_07/manifest.json' already exists"
        match = re.search(r"['\"]([^'\"]+)['\"].*already exists", error_msg, re.IGNORECASE)
        if match:
            conflict_path = Path(match.group(1))
            # Get the model directory (parent of manifest.json)
            if conflict_path.name == "manifest.json":
                model_dir = conflict_path.parent
            else:
                model_dir = conflict_path
            
            if model_dir.exists():
                logger.warning(f"Marker: Clearing conflicting cache directory: {model_dir}")
                try:
                    shutil.rmtree(model_dir)
                    logger.info(f"Marker: Successfully cleared {model_dir}")
                except Exception as e:
                    logger.error(f"Marker: Failed to clear cache: {e}")
    
    def _create_model_dict_sync(self):
        """Synchronous helper to create model dict - handles model downloads"""
        import time
        max_retries = 2  # We only need 2 retries: first try, then after cache clear
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Marker: Starting model download/initialization (attempt {attempt + 1}/{max_retries})...")
                model_dict = create_model_dict()  # type: ignore
                logger.info("Marker: Model download/initialization completed")
                return model_dict
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.error(f"Marker: Attempt {attempt + 1} failed: {error_msg}")
                
                # If it's a file conflict, clear the ENTIRE datalab cache and retry
                # This is necessary because surya's internal retry doesn't clear cache
                if "already exists" in error_msg.lower():
                    logger.warning("Marker: File conflict detected, clearing entire datalab model cache...")
                    self._clear_datalab_cache()
                    # Give it a moment before retry
                    time.sleep(2)
                    continue
                else:
                    # For other errors, don't retry
                    break
        
        raise RuntimeError(f"Failed to initialize marker models after {max_retries} attempts: {last_error}")
    
    async def _ensure_initialized(self):
        """Lazy initialization - only create PdfConverter when actually needed"""
        if self._initialized:
            return
        
        if not MARKER_AVAILABLE:
            raise RuntimeError("marker is not available")
        
        # Use async lock to prevent multiple simultaneous initializations
        async with _init_lock:
            # Double-check after acquiring lock
            if self._initialized:
                return
            
            try:
                # Run model download in thread executor to avoid blocking
                # This also handles the blocking model download operation
                logger.info("Marker: Acquired initialization lock, starting model download...")
                model_dict = await asyncio.to_thread(self._create_model_dict_sync)
                
                # Create converter with the model dict
                self._converter = PdfConverter(artifact_dict=model_dict)  # type: ignore
                self._initialized = True
                logger.info("Marker: Converter initialized successfully")
            except Exception as e:
                logger.error(f"Marker: Initialization failed: {str(e)}")
                raise
    
    @property
    def name(self) -> str:
        return "marker"
    
    @property
    def available(self) -> bool:
        return MARKER_AVAILABLE
    
    @property
    def requires_download(self) -> bool:
        return True
    
    @property
    def download_status(self) -> DownloadStatus:
        if not MARKER_AVAILABLE:
            return DownloadStatus.NOT_STARTED
        if self._initialized:
            return DownloadStatus.READY
        if self._is_downloading:
            return DownloadStatus.DOWNLOADING
        if self._download_error:
            return DownloadStatus.FAILED
        return DownloadStatus.NOT_STARTED
    
    @property
    def download_error(self) -> Optional[str]:
        return self._download_error
    
    async def prepare(self) -> bool:
        """Download and prepare marker models"""
        if not MARKER_AVAILABLE:
            self._download_error = "marker library is not installed"
            self._download_status = DownloadStatus.FAILED
            return False
        
        if self._initialized:
            return True
        
        self._is_downloading = True
        self._download_error = None
        
        try:
            await self._ensure_initialized()
            self._is_downloading = False
            return True
        except Exception as e:
            self._is_downloading = False
            self._download_error = str(e)
            self._download_status = DownloadStatus.FAILED
            logger.error(f"Marker: Preparation failed: {e}")
            return False
    
    def _convert_sync(self, file_path: str) -> str:
        """Synchronous helper for convert_to_md - wraps all blocking operations"""
        try:
            rendered = self._converter(file_path)
            text, _, images = text_from_rendered(rendered)  # type: ignore
            return text
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Marker conversion failed: {str(e)}") from e
    
    async def convert_to_md(self, file_path: str) -> str:
        if not self.available:
            raise RuntimeError("marker is not available")
        await self._ensure_initialized()  # Now async
        # Run blocking operations in thread executor to avoid blocking the event loop
        try:
            return await asyncio.to_thread(self._convert_sync, file_path)
        except Exception as e:
            # Ensure exceptions are properly propagated
            raise
    
    async def convert_to_json(self, file_path: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("marker is not available")
        md_content = await self.convert_to_md(file_path)
        return {
            "content": md_content,
            "format": "markdown",
            "library": self.name
        }
    
    async def convert_to_text(self, file_path: str) -> str:
        return await self.convert_to_md(file_path)

