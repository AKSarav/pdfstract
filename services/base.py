from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class OutputFormat(Enum):
    """Supported output formats"""
    MARKDOWN = "markdown"
    JSON = "json"
    TEXT = "text"
    HTML = "html"


class DownloadStatus(Enum):
    """Status of model download/preparation"""
    NOT_STARTED = "not_started"
    DOWNLOADING = "downloading"
    READY = "ready"
    FAILED = "failed"
    NOT_REQUIRED = "not_required"  # For converters that don't need downloads


class PDFConverter(ABC):
    """
    Abstract base class for PDF converters (Go-style interface).
    All converters must implement these methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the converter library"""
        pass
    
    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if the converter library is available/installed"""
        pass
    
    @property
    def requires_download(self) -> bool:
        """
        Check if this converter requires model downloads.
        Override in subclass if models need to be downloaded.
        """
        return False
    
    @property
    def download_status(self) -> DownloadStatus:
        """
        Get the current download/preparation status.
        Override in subclass for converters with downloads.
        """
        return DownloadStatus.NOT_REQUIRED
    
    @property
    def download_error(self) -> Optional[str]:
        """Get error message if download failed"""
        return None
    
    async def prepare(self) -> bool:
        """
        Prepare the converter by downloading models/dependencies.
        
        Returns:
            True if preparation succeeded, False otherwise.
            
        Override in subclass for converters that need downloads.
        Default implementation returns True (no preparation needed).
        """
        return True
    
    @abstractmethod
    async def convert_to_md(self, file_path: str) -> str:
        """Convert PDF to Markdown"""
        pass
    
    @abstractmethod
    async def convert_to_json(self, file_path: str) -> Dict[str, Any]:
        """Convert PDF to JSON"""
        pass
    
    @abstractmethod
    async def convert_to_text(self, file_path: str) -> str:
        """Convert PDF to plain text"""
        pass
    
    def supports_format(self, format_type: OutputFormat) -> bool:
        """Check if converter supports a specific output format"""
        # Default implementation - can be overridden
        return format_type in [
            OutputFormat.MARKDOWN,
            OutputFormat.JSON,
            OutputFormat.TEXT
        ]
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information about the converter"""
        return {
            "name": self.name,
            "available": self.available,
            "requires_download": self.requires_download,
            "download_status": self.download_status.value,
            "download_error": self.download_error
        }

