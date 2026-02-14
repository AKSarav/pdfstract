"""
PDFStract Python Library API

Simple, clean interface for using PDFStract as a Python library.
Enables non-CLI users to integrate PDF extraction into their applications.

Examples:
    >>> from pdfstract import PDFStract
    >>> pdfstract = PDFStract()
    >>> result = pdfstract.convert('sample.pdf', 'marker')
    
    >>> # Quick conversion
    >>> from pdfstract import convert_pdf
    >>> result = convert_pdf('sample.pdf', library='marker')
    
    >>> # Batch processing
    >>> results = pdfstract.batch_convert('./pdfs', 'marker')
    >>> print(f"Converted {results['success']} files")
    
    >>> # Async usage
    >>> import asyncio
    >>> async def main():
    ...     result = await pdfstract.convert_async('sample.pdf', 'marker')
    >>> asyncio.run(main())
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from concurrent.futures import ThreadPoolExecutor

# Use relative imports for package context
# Try relative import first (when installed as package), fall back to absolute
try:
    from services.cli_factory import CLILazyFactory
    from services.base import OutputFormat
except ImportError:
    # Fallback for non-package usage (development)
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.cli_factory import CLILazyFactory
    from services.base import OutputFormat

# Version management - reads from pyproject.toml to keep single source of truth
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Fallback for older Python

try:
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        _pyproject_data = tomllib.load(f)
    __version__ = _pyproject_data["project"]["version"]
except Exception:
    __version__ = "1.1.0"  # Fallback version


class PDFStract:
    """Main library API for PDFStract
    
    Provides a clean interface for PDF extraction without CLI overhead.
    Supports sync, async, and batch operations.
    """
    
    def __init__(self):
        """Initialize PDFStract library with lazy-loading factory"""
        self._factory = CLILazyFactory()
    
    def list_libraries(self) -> list[Dict[str, Any]]:
        """List all available PDF extraction libraries with their status
        
        Returns:
            List of library info dicts with 'name', 'available', and 'error' keys
            
        Example:
            >>> pdfstract = PDFStract()
            >>> libs = pdfstract.list_libraries()
            >>> for lib in libs:
            ...     print(f"{lib['name']}: {lib['available']}")
        """
        return self._factory.list_all_converters()
    
    def list_available_libraries(self) -> list[str]:
        """List names of available extraction libraries only
        
        Returns:
            List of library names that are installed and ready to use
            
        Example:
            >>> pdfstract = PDFStract()
            >>> available = pdfstract.list_available_libraries()
            >>> print(available)
            ['marker', 'pymupdf4llm', 'docling', ...]
        """
        return self._factory.list_available_converters()
    
    def convert(
        self,
        pdf_path: Union[str, Path],
        library: str,
        output_format: str = "markdown"
    ) -> Union[str, Dict]:
        """Convert a PDF file to structured output (synchronous)
        
        Args:
            pdf_path: Path to the PDF file to convert
            library: Name of extraction library to use
                    (e.g., 'marker', 'pymupdf4llm', 'docling', 'unstructured')
            output_format: Output format - 'markdown', 'json', 'text', or 'html'
                          Default: 'markdown'
        
        Returns:
            Extracted content as string (for markdown/text/html) or dict (for JSON)
        
        Raises:
            ValueError: If library is not found or conversion fails
            FileNotFoundError: If PDF file doesn't exist
        
        Example:
            >>> pdfstract = PDFStract()
            >>> result = pdfstract.convert('sample.pdf', 'marker')
            >>> print(result)
            
            >>> # JSON output
            >>> result = pdfstract.convert('sample.pdf', 'docling', 'json')
        """
        # Check library availability first (before checking file)
        converter = self._factory.get_converter(library)
        if not converter:
            available = self.list_available_libraries()
            raise ValueError(
                f"Library '{library}' not available. Available: {available}"
            )
        
        # Then check if file exists
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            return self._factory.convert(
                converter_name=library,
                file_path=str(pdf_path),
                output_format=OutputFormat(output_format)
            )
        except Exception as e:
            raise ValueError(f"Conversion failed: {str(e)}")
    
    async def convert_async(
        self,
        pdf_path: Union[str, Path],
        library: str,
        output_format: str = "markdown"
    ) -> Union[str, Dict]:
        """Convert a PDF file asynchronously (non-blocking)
        
        Useful for non-blocking I/O in async applications, web servers, etc.
        
        Args:
            pdf_path: Path to the PDF file to convert
            library: Name of extraction library to use
            output_format: Output format - 'markdown', 'json', 'text', or 'html'
        
        Returns:
            Extracted content as string or dict
        
        Raises:
            ValueError: If library is not found or conversion fails
            FileNotFoundError: If PDF file doesn't exist
        
        Example:
            >>> import asyncio
            >>> async def process_pdfs():
            ...     pdfstract = PDFStract()
            ...     result = await pdfstract.convert_async('sample.pdf', 'marker')
            ...     return result
            >>> asyncio.run(process_pdfs())
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        converter = self._factory.get_converter(library)
        if not converter:
            available = self.list_available_libraries()
            raise ValueError(
                f"Library '{library}' not available. Available: {available}"
            )
        
        try:
            return await self._factory.convert_async(
                converter_name=library,
                file_path=str(pdf_path),
                output_format=OutputFormat(output_format)
            )
        except Exception as e:
            raise ValueError(f"Conversion failed: {str(e)}")
    
    def batch_convert(
        self,
        pdf_directory: Union[str, Path],
        library: str,
        output_format: str = "markdown",
        parallel_workers: int = 2
    ) -> Dict[str, Any]:
        """Batch convert multiple PDF files with parallelization
        
        Processes all PDF files in a directory using multiple workers.
        
        Args:
            pdf_directory: Directory containing PDF files
            library: Extraction library to use
            output_format: Output format for all files
            parallel_workers: Number of parallel conversion workers (default: 2)
        
        Returns:
            Results dict with:
                - 'success': Number of successfully converted files
                - 'failed': Number of failed conversions
                - 'results': Dict mapping filename -> content or error
        
        Raises:
            ValueError: If library not found or directory is empty
        
        Example:
            >>> pdfstract = PDFStract()
            >>> results = pdfstract.batch_convert('./pdfs', 'marker')
            >>> print(f"Success: {results['success']}, Failed: {results['failed']}")
            >>> for filename, content in results['results'].items():
            ...     if 'error' not in content:
            ...         print(f"✓ {filename} converted")
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise ValueError(f"Directory not found: {pdf_dir}")
        
        pdf_files = sorted(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            return {"success": 0, "failed": 0, "results": {}}
        
        converter = self._factory.get_converter(library)
        if not converter:
            available = self.list_available_libraries()
            raise ValueError(
                f"Library '{library}' not available. Available: {available}"
            )
        
        results = {"success": 0, "failed": 0, "results": {}}
        output_format_enum = OutputFormat(output_format)
        
        def convert_pdf(pdf_file: Path) -> tuple:
            """Helper to convert a single PDF"""
            try:
                result = self._factory.convert(
                    converter_name=library,
                    file_path=str(pdf_file),
                    output_format=output_format_enum
                )
                return (pdf_file.name, "success", None, result)
            except Exception as e:
                return (pdf_file.name, "failed", str(e), None)
        
        with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
            futures = [executor.submit(convert_pdf, pdf) for pdf in pdf_files]
            
            for future in futures:
                filename, status, error, result = future.result()
                
                if status == "success":
                    results["success"] += 1
                    results["results"][filename] = result
                else:
                    results["failed"] += 1
                    results["results"][filename] = {"error": error}
        
        return results
    
    # ===== CHUNKING API =====
    
    def chunk_text(
        self,
        text: str,
        chunker: str = "token",
        **kwargs
    ) -> Dict[str, Any]:
        """Chunk text using specified chunker (synchronous)
        
        Args:
            text: Text to chunk
            chunker: Name of chunker to use
                    (e.g., 'token', 'sentence', 'semantic', 'recursive', 'code')
            **kwargs: Chunker-specific parameters (e.g., chunk_size, overlap)
        
        Returns:
            Dict with:
                - 'chunks': List of chunk dicts with text, start_index, end_index, token_count
                - 'chunker_name': Name of chunker used
                - 'total_chunks': Number of chunks created
                - 'total_tokens': Total tokens across all chunks
        
        Raises:
            ValueError: If chunker not found or not available
        
        Example:
            >>> pdfstract = PDFStract()
            >>> result = pdfstract.chunk_text("Long text here...", chunker="token", chunk_size=512)
            >>> print(f"Created {result['total_chunks']} chunks")
            
            >>> # Semantic chunking
            >>> result = pdfstract.chunk_text("Long text...", chunker="semantic")
        """
        import asyncio
        return asyncio.run(self.chunk_text_async(text, chunker, **kwargs))
    
    async def chunk_text_async(
        self,
        text: str,
        chunker: str = "token",
        **kwargs
    ) -> Dict[str, Any]:
        """Chunk text asynchronously
        
        Args:
            text: Text to chunk
            chunker: Name of chunker to use
            **kwargs: Chunker-specific parameters
        
        Returns:
            Dict with chunking results
        
        Example:
            >>> import asyncio
            >>> async def main():
            ...     pdfstract = PDFStract()
            ...     result = await pdfstract.chunk_text_async("Long text...", chunker="semantic")
            ...     return result
            >>> asyncio.run(main())
        """
        from services.chunker_factory import get_chunker_factory
        
        factory = get_chunker_factory()
        available = factory.list_available_chunkers()
        
        if chunker == 'auto':
            chunker_instance = factory.get_default_chunker()
            if not chunker_instance:
                raise ValueError("No available chunkers found for auto-selection")
            chunker = chunker_instance.name
        
        if chunker not in available:
            raise ValueError(
                f"Chunker '{chunker}' not available. Available: {available}"
            )
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        result = await factory.chunk_with_result(chunker, text, **kwargs)
        return result.to_dict()
    
    def chunk(
        self,
        text: str,
        chunker: str = "token",
        **kwargs
    ) -> Dict[str, Any]:
        """Alias for chunk_text() - chunks text synchronously
        
        Convenient shorthand: pdfstract.chunk(text) instead of pdfstract.chunk_text(text)
        """
        return self.chunk_text(text, chunker, **kwargs)
    
    async def chunk_async(
        self,
        text: str,
        chunker: str = "token",
        **kwargs
    ) -> Dict[str, Any]:
        """Alias for chunk_text_async() - chunks text asynchronously"""
        return await self.chunk_text_async(text, chunker, **kwargs)
    
    def list_available_chunkers(self) -> List[str]:
        """List all available chunkers
        
        Returns:
            List of chunker names that are available
        
        Example:
            >>> pdfstract = PDFStract()
            >>> print(pdfstract.list_available_chunkers())
            >>> # Output: ['token', 'sentence', 'semantic', ...]
        """
        from services.chunker_factory import get_chunker_factory
        
        factory = get_chunker_factory()
        return factory.list_available_chunkers()
    
    def list_chunkers(self) -> List[Dict[str, Any]]:
        """List all chunkers with detailed info
        
        Returns:
            List of dicts with chunker details (name, availability, parameters)
        
        Example:
            >>> pdfstract = PDFStract()
            >>> chunkers = pdfstract.list_chunkers()
            >>> for c in chunkers:
            ...     print(f"{c['name']}: {c['available']}")
        """
        from services.chunker_factory import get_chunker_factory
        
        factory = get_chunker_factory()
        return factory.list_all_chunkers()
    
    def get_chunker_info(self, chunker: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a specific chunker
        
        Args:
            chunker: Name of the chunker
        
        Returns:
            Dict with chunker parameters schema or None if not found
        
        Example:
            >>> pdfstract = PDFStract()
            >>> info = pdfstract.get_chunker_info("semantic")
            >>> print(info)
        """
        from services.chunker_factory import get_chunker_factory
        
        factory = get_chunker_factory()
        return factory.get_chunker_schema(chunker)
    
    def get_converter_info(self, library: str) -> Optional[Dict]:
        """Get detailed information about a specific converter
        
        Args:
            library: Library name
        
        Returns:
            Converter info dict with 'name', 'available', 'error' or None if not found
            
        Example:
            >>> pdfstract = PDFStract()
            >>> info = pdfstract.get_converter_info('marker')
            >>> print(f"Available: {info['available']}")
        """
        all_libs = self.list_libraries()
        return next((lib for lib in all_libs if lib["name"] == library), None)

    async def convert_chunk_async(
        self,
        pdf_path: Union[str, Path],
        library: str,
        chunker: str,
        output_format: str = "markdown",
        chunker_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert PDF and chunk the extracted text in one step (asynchronous)
        
        Args:
            pdf_path: Path to PDF file
            library: Extraction library to use
            chunker: Chunker to use for chunking extracted text
            output_format: Output format for extraction (default: 'markdown')
            chunker_params: Optional dict of parameters to pass to the chunker
            
        Returns:
            Dict with 'extracted_content' and 'chunking_result'
        """
        extracted_content = await self.convert_async(pdf_path, library, output_format)
        chunking_result = await self.chunk_text_async(
            text=extracted_content if isinstance(extracted_content, str) else str(extracted_content),
            chunker=chunker,
            **(chunker_params or {})
        )
        return {
            "extracted_content": extracted_content,
            "chunking_result": chunking_result
        }

    def convert_chunk(
        self,
        pdf_path: Union[str, Path],
        library: str,
        chunker: str,
        output_format: str = "markdown",
        chunker_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert PDF and chunk the extracted text in one step
        
        Args:
            pdf_path: Path to PDF file
            library: Extraction library to use
            chunker: Chunker to use for chunking extracted text
            output_format: Output format for extraction (default: 'markdown')
            chunker_params: Optional dict of parameters to pass to the chunker
            
        Returns:
            Dict with 'extracted_content' and 'chunking_result'
        """
        import asyncio
        return asyncio.run(
            self.convert_chunk_async(
                pdf_path, library, chunker, output_format, chunker_params or {}
            )
        )

# ============================================================================
# Convenience functions for quick usage
# ============================================================================

def convert_pdf(
    pdf_path: Union[str, Path],
    library: str = "pymupdf4llm",
    output_format: str = "markdown"
) -> Union[str, Dict]:
    """Quick PDF conversion function
    
    One-liner convenience function for simple conversions.
    
    Args:
        pdf_path: Path to PDF file
        library: Extraction library (default: 'pymupdf4llm')
        output_format: Output format (default: 'markdown')
    
    Returns:
        Extracted content
    
    Example:
        >>> from pdfstract import convert_pdf
        >>> result = convert_pdf('sample.pdf', 'marker')
        >>> print(result)
    """
    pdfstract = PDFStract()
    return pdfstract.convert(pdf_path, library, output_format)


def list_available_libraries() -> list[str]:
    """Quick function to list available libraries
    
    Example:
        >>> from pdfstract import list_available_libraries
        >>> print(list_available_libraries())
    """
    pdfstract = PDFStract()
    return pdfstract.list_available_libraries()


def chunk_text(
    text: str,
    chunker: str = "token",
    **kwargs
) -> Dict[str, Any]:
    """Quick text chunking function
    
    One-liner convenience function for simple chunking operations.
    
    Args:
        text: Text to chunk
        chunker: Chunker to use (default: 'token')
        **kwargs: Chunker-specific parameters
    
    Returns:
        Chunking result dict
    
    Example:
        >>> from pdfstract import chunk_text
        >>> result = chunk_text("Long text...", chunker="semantic", chunk_size=512)
        >>> print(f"Created {result['total_chunks']} chunks")
    """
    pdfstract = PDFStract()
    return pdfstract.chunk_text(text, chunker, **kwargs)


def list_available_chunkers() -> List[str]:
    """Quick function to list available chunkers
    
    Example:
        >>> from pdfstract import list_available_chunkers
        >>> print(list_available_chunkers())
    """
    pdfstract = PDFStract()
    return pdfstract.list_available_chunkers()
