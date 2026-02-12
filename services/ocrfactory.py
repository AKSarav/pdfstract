from typing import Dict, Optional, List, Union, Any
from services.base import PDFConverter, OutputFormat, DownloadStatus
from services.converters.pymupdf4llm_converter import PyMuPDF4LLMConverter
from services.converters.markitdown_converter import MarkItDownConverter
from services.converters.marker_converter import MarkerConverter
from services.converters.docling_converter import DoclingConverter
from services.converters.paddleocr_converter import PaddleOCRConverter
from services.converters.deepseekocr_transformers_converter import DeepSeekOCRTransformersConverter
from services.converters.pytesseract_converter import PyTesseractConverter
from services.converters.unstructured_converter import UnstructuredConverter
from services.converters.mineru_converter import MinerUConverter
from services.logger import logger

class OCRFactory:
    """
    Factory class for creating and managing PDF converters.
    Implements singleton pattern for converter instances.
    
    Now supports on-demand model downloads via prepare() method.
    """
    
    def __init__(self):
        self._converters: Dict[str, PDFConverter] = {}
        self._all_converters: Dict[str, PDFConverter] = {}  # All converters including unavailable
        self._register_default_converters()
    
    def _register_default_converters(self):
        """Register all available converter implementations"""
        converters = [
            PyMuPDF4LLMConverter(),
            MarkItDownConverter(),
            MarkerConverter(),
            DoclingConverter(),
            PaddleOCRConverter(),
            DeepSeekOCRTransformersConverter(),
            PyTesseractConverter(),
            UnstructuredConverter(),
            MinerUConverter(),
        ]
        
        for converter in converters:
            # Store all converters for status queries
            self._all_converters[converter.name] = converter
            
            if converter.available:
                self._converters[converter.name] = converter
                logger.info(f"Registered converter: {converter.name}")
            else:
                # Provide more detailed error message if available
                error_msg = getattr(converter, 'error_message', 'Dependencies not installed')
                logger.warning(f"Converter {converter.name} is not available: {error_msg}")
    
    def get_converter(self, name: str) -> Optional[PDFConverter]:
        """Get a converter by name"""
        return self._converters.get(name)
    
    def list_available_converters(self) -> List[str]:
        """List all available converter names"""
        return list(self._converters.keys())
    
    def list_all_converters(self) -> List[Dict[str, Any]]:
        """List all converters with their availability and download status"""
        result = []
        for name, converter in self._all_converters.items():
            available = converter.available
            
            # Get download status info
            requires_download = getattr(converter, 'requires_download', False)
            download_status = getattr(converter, 'download_status', DownloadStatus.NOT_REQUIRED)
            download_error = getattr(converter, 'download_error', None)
            
            result.append({
                "name": name,
                "available": available,
                "error": None if available else getattr(converter, "error_message", "Unavailable"),
                "requires_download": requires_download,
                "download_status": download_status.value if hasattr(download_status, 'value') else str(download_status),
                "download_error": download_error
            })
        return result
    
    def get_converter_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status info for a specific converter"""
        converter = self._all_converters.get(name)
        if not converter:
            return None
        return converter.get_status_info()
    
    async def prepare_converter(self, name: str) -> Dict[str, Any]:
        """
        Prepare a converter by downloading its models.
        
        Args:
            name: Name of the converter to prepare
            
        Returns:
            Dict with success status and any error message
        """
        converter = self._all_converters.get(name)
        if not converter:
            return {
                "success": False,
                "error": f"Converter '{name}' not found"
            }
        
        if not converter.available:
            return {
                "success": False,
                "error": f"Converter '{name}' library is not installed"
            }
        
        if not converter.requires_download:
            return {
                "success": True,
                "message": f"Converter '{name}' does not require model downloads"
            }
        
        try:
            logger.info(f"Starting model download for {name}...")
            success = await converter.prepare()
            
            if success:
                # Register if not already registered
                if name not in self._converters:
                    self._converters[name] = converter
                return {
                    "success": True,
                    "message": f"Converter '{name}' models downloaded successfully"
                }
            else:
                return {
                    "success": False,
                    "error": converter.download_error or "Unknown error during preparation"
                }
        except Exception as e:
            logger.error(f"Failed to prepare converter {name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert(
        self,
        converter_name: str,
        file_path: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN
    ) -> Union[str, Dict]:
        """
        Convert PDF using specified converter and format (synchronous wrapper).
        For CLI usage, this uses asyncio.run() internally.
        
        Args:
            converter_name: Name of the converter to use
            file_path: Path to the PDF file
            output_format: Desired output format
            
        Returns:
            Converted content in the specified format
        """
        import asyncio
        return asyncio.run(self.convert_async(converter_name, file_path, output_format))
    
    async def convert_async(
        self,
        converter_name: str,
        file_path: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN
    ) -> Union[str, Dict]:
        """
        Async version of convert method.
        
        Args:
            converter_name: Name of the converter to use
            file_path: Path to the PDF file
            output_format: Desired output format
            
        Returns:
            Converted content in the specified format
        """
        converter = self.get_converter(converter_name)
        if not converter:
            raise ValueError(f"Converter '{converter_name}' is not available")
        
        if not converter.supports_format(output_format):
            raise ValueError(
                f"Converter '{converter_name}' does not support format '{output_format.value}'"
            )
        
        if output_format == OutputFormat.MARKDOWN:
            return await converter.convert_to_md(file_path)
        elif output_format == OutputFormat.JSON:
            return await converter.convert_to_json(file_path)
        elif output_format == OutputFormat.TEXT:
            return await converter.convert_to_text(file_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
