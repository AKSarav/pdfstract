"""
Lightweight factory for CLI - doesn't check library availability on startup
Only loads libraries when actually needed (lazy loading)
"""

from typing import Dict, Optional, List, Union, Any
from services.base import PDFConverter, OutputFormat, DownloadStatus
from services.logger import logger


class CLILazyFactory:
    """
    Lightweight CLI factory that lazy-loads converters only when needed.
    Much faster startup time than OCRFactory.
    Supports MinerU, download status, and prepare_converter for parity with OCRFactory.
    """
    
    def __init__(self):
        self._converters: Dict[str, PDFConverter] = {}
        self._all_converters: Dict[str, PDFConverter] = {}
        self._converter_classes = {
            'pymupdf4llm': ('services.converters.pymupdf4llm_converter', 'PyMuPDF4LLMConverter'),
            'markitdown': ('services.converters.markitdown_converter', 'MarkItDownConverter'),
            'marker': ('services.converters.marker_converter', 'MarkerConverter'),
            'docling': ('services.converters.docling_converter', 'DoclingConverter'),
            'paddleocr': ('services.converters.paddleocr_converter', 'PaddleOCRConverter'),
            'deepseekocr': ('services.converters.deepseekocr_transformers_converter', 'DeepSeekOCRTransformersConverter'),
            'pytesseract': ('services.converters.pytesseract_converter', 'PyTesseractConverter'),
            'unstructured': ('services.converters.unstructured_converter', 'UnstructuredConverter'),
            'mineru': ('services.converters.mineru_converter', 'MinerUConverter'),
        }
    
    def _load_converter(self, name: str) -> Optional[PDFConverter]:
        """Lazy load a converter only when needed. Always caches in _all_converters; adds to _converters only if available."""
        if name in self._all_converters:
            return self._all_converters[name]
        
        if name not in self._converter_classes:
            return None
        
        try:
            module_path, class_name = self._converter_classes[name]
            import importlib
            module = importlib.import_module(module_path)
            converter_class = getattr(module, class_name)
            converter = converter_class()
            self._all_converters[name] = converter
            if converter.available:
                self._converters[name] = converter
                logger.debug(f"Loaded converter: {name}")
            else:
                logger.debug(f"Converter {name} not available")
            return converter
        except Exception as e:
            logger.debug(f"Failed to load converter {name}: {e}")
            return None
    
    def get_converter(self, name: str) -> Optional[PDFConverter]:
        """Get converter (lazy load if needed). Returns only available converters for conversion."""
        if name == 'auto':
            for converter_name in self._converter_classes.keys():
                converter = self._load_converter(converter_name)
                if converter and converter.available:
                    logger.info(f"Auto-selected converter: {converter_name}")
                    return converter
            logger.info("No available converters found for auto-selection")
            return None
        converter = self._load_converter(name)
        return converter if (converter and converter.available) else None
    
    def list_available_converters(self) -> List[str]:
        """List all available converters (lazy check)"""
        available = []
        for name in self._converter_classes.keys():
            converter = self._load_converter(name)
            if converter and converter.available:
                available.append(name)
        return available
    
    def list_all_converters(self) -> List[Dict[str, Any]]:
        """List all converters with availability and download status (OCRFactory-aligned shape)."""
        result = []
        for name in self._converter_classes.keys():
            converter = self._load_converter(name)
            if not converter:
                result.append({
                    "name": name,
                    "available": False,
                    "error": "Not installed",
                    "requires_download": False,
                    "download_status": DownloadStatus.NOT_REQUIRED.value,
                    "download_error": None,
                })
                continue
            available = converter.available
            requires_download = getattr(converter, "requires_download", False)
            download_status = getattr(converter, "download_status", DownloadStatus.NOT_REQUIRED)
            download_error = getattr(converter, "download_error", None)
            result.append({
                "name": name,
                "available": available,
                "error": None if available else getattr(converter, "error_message", "Unavailable"),
                "requires_download": requires_download,
                "download_status": download_status.value if hasattr(download_status, "value") else str(download_status),
                "download_error": download_error,
            })
        return result
    
    def get_converter_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status info for a specific converter."""
        converter = self._load_converter(name)
        if not converter:
            return None
        return converter.get_status_info()
    
    async def prepare_converter(self, name: str) -> Dict[str, Any]:
        """Prepare a converter by downloading its models. Same contract as OCRFactory."""
        converter = self._load_converter(name)
        if not converter:
            return {"success": False, "error": f"Converter '{name}' not found"}
        if not converter.available:
            return {"success": False, "error": f"Converter '{name}' library is not installed"}
        if not getattr(converter, "requires_download", False):
            return {"success": True, "message": f"Converter '{name}' does not require model downloads"}
        try:
            logger.info(f"Starting model download for {name}...")
            success = await converter.prepare()
            if success:
                if name not in self._converters:
                    self._converters[name] = converter
                return {"success": True, "message": f"Converter '{name}' models downloaded successfully"}
            return {
                "success": False,
                "error": getattr(converter, "download_error", None) or "Unknown error during preparation",
            }
        except Exception as e:
            logger.error(f"Failed to prepare converter {name}: {e}")
            return {"success": False, "error": str(e)}
    
    def convert(
        self,
        converter_name: str,
        file_path: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN
    ) -> Union[str, Dict]:
        """Convert PDF (synchronous)"""
        import asyncio
        return asyncio.run(self.convert_async(converter_name, file_path, output_format))
    
    async def convert_async(
        self,
        converter_name: str,
        file_path: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN
    ) -> Union[str, Dict]:
        """Convert PDF (asynchronous)"""
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

    def get_default_library(self) -> Optional[str]:
        """Get the default library (first available in priority order)"""
        for name in self._converter_classes.keys():
            converter = self._load_converter(name)
            if converter and converter.available:
                logger.info(f"Auto-Selected library: {name}")
                return name
        logger.warning("No available libraries found for default selection")
        return None