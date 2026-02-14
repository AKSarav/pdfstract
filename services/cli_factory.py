"""
Lightweight factory for CLI - doesn't check library availability on startup
Only loads libraries when actually needed (lazy loading)
"""

from typing import Dict, Optional, List, Union
from services.base import PDFConverter, OutputFormat
from services.logger import logger


class CLILazyFactory:
    """
    Lightweight CLI factory that lazy-loads converters only when needed.
    Much faster startup time than OCRFactory.
    """
    
    def __init__(self):
        self._converters: Dict[str, PDFConverter] = {}
        self._converter_classes = {
            'pymupdf4llm': ('services.converters.pymupdf4llm_converter', 'PyMuPDF4LLMConverter'),
            'markitdown': ('services.converters.markitdown_converter', 'MarkItDownConverter'),
            'marker': ('services.converters.marker_converter', 'MarkerConverter'),
            'docling': ('services.converters.docling_converter', 'DoclingConverter'),
            'paddleocr': ('services.converters.paddleocr_converter', 'PaddleOCRConverter'),
            'deepseekocr': ('services.converters.deepseekocr_transformers_converter', 'DeepSeekOCRTransformersConverter'),
            'pytesseract': ('services.converters.pytesseract_converter', 'PyTesseractConverter'),
            'unstructured': ('services.converters.unstructured_converter', 'UnstructuredConverter'),
        }
    
    def _load_converter(self, name: str) -> Optional[PDFConverter]:
        """Lazy load a converter only when needed"""
        if name in self._converters:
            return self._converters[name]
        
        if name not in self._converter_classes:
            return None
        
        try:
            # Import dynamically to avoid loading unused heavy dependencies
            module_path, class_name = self._converter_classes[name]
            
            # Dynamic import to avoid importing all converters on startup
            import importlib
            module = importlib.import_module(module_path)
            converter_class = getattr(module, class_name)
            converter = converter_class()
            
            if converter.available:
                self._converters[name] = converter
                logger.debug(f"Loaded converter: {name}")
                return converter
            else:
                logger.debug(f"Converter {name} not available")
                return None
        except Exception as e:
            logger.debug(f"Failed to load converter {name}: {e}")
            return None
    
    def get_converter(self, name: str) -> Optional[PDFConverter]:
        """Get converter (lazy load if needed)"""
        if name == 'auto':
            # Auto-select the first available converter based on priority
            for converter_name in self._converter_classes.keys():
                converter = self._load_converter(converter_name)
                if converter and converter.available:
                    logger.info(f"Auto-selected converter: {converter_name}")
                    return converter
            logger.info("No available converters found for auto-selection")
            return None
        return self._load_converter(name)
    
    def list_available_converters(self) -> List[str]:
        """List all available converters (lazy check)"""
        available = []
        for name in self._converter_classes.keys():
            if self._load_converter(name):
                available.append(name)
        return available
    
    def list_all_converters(self) -> List[Dict]:
        """List all converters with availability status"""
        result = []
        for name in self._converter_classes.keys():
            converter = self._load_converter(name)
            available = converter is not None and converter.available
            result.append({
                "name": name,
                "available": available,
                "error": None if available else getattr(converter, "error_message", "Unavailable") if converter else "Not installed"
            })
        return result
    
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