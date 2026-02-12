"""
MinerU Converter - High-quality PDF extraction using magic-pdf CLI.

MinerU is a tool that converts PDFs into machine-readable formats (markdown, JSON),
with excellent support for complex layouts, formulas, tables, and OCR.

Uses the MinerU CLI: mineru -p <input_path> -o <output_path> -b pipeline
Requires: magic-pdf[full] - pip install "magic-pdf[full]"
Documentation: https://opendatalab.github.io/MinerU/usage/
"""

from typing import Dict, Any, Optional
import asyncio
import subprocess
import re
from pathlib import Path
from services.base import PDFConverter, DownloadStatus
from services.logger import logger

# Check if mineru CLI is available
def _check_mineru_available() -> bool:
    try:
        result = subprocess.run(
            ["mineru", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

MINERU_AVAILABLE = _check_mineru_available()

# Global async lock for conversion
_init_lock = asyncio.Lock()


class MinerUConverter(PDFConverter):
    """
    Converter implementation for MinerU (magic-pdf) via CLI.
    
    Runs: mineru -p <input_path> -o <output_path> -b pipeline
    MinerU provides high-quality PDF extraction with formula recognition,
    table recognition, layout analysis, and OCR support.
    """
    
    def __init__(self):
        self._initialized = True  # No lazy init needed for CLI
        self._download_status = DownloadStatus.NOT_REQUIRED
        self._download_error: Optional[str] = None
        self._is_downloading = False
    
    @property
    def name(self) -> str:
        return "mineru"
    
    @property
    def available(self) -> bool:
        return MINERU_AVAILABLE
    
    @property
    def error_message(self) -> Optional[str]:
        if not MINERU_AVAILABLE:
            return "Install with: pip install 'magic-pdf[full]'. Use Docker for full support."
        return None
    
    @property
    def requires_download(self) -> bool:
        return False  # CLI handles models; no on-demand download from our side
    
    @property
    def download_status(self) -> DownloadStatus:
        return DownloadStatus.NOT_REQUIRED
    
    @property
    def download_error(self) -> Optional[str]:
        return self._download_error
    
    async def prepare(self) -> bool:
        """No-op for CLI-based MinerU; models are handled by the mineru command."""
        return MINERU_AVAILABLE
    
    def _convert_sync(self, file_path: str, output_format: str = "markdown") -> str:
        """
        Convert PDF using MinerU CLI: mineru -p <input_path> -o <output_path> -b pipeline
        Then read the generated markdown from the output directory.
        """
        input_path = Path(file_path).resolve()
        if not input_path.exists():
            raise RuntimeError(f"MinerU: Input file not found: {file_path}")
        
        # Use a temp dir for output; MinerU creates a subdir named after the PDF
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "mineru_out"
            out_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "mineru",
                "-p", str(input_path),
                "-o", str(out_dir),
                "-b", "pipeline",
            ]
            logger.info(f"MinerU: Running {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(out_dir),
            )
            
            # print the result
            logger.info(f"MinerU: Result: {result.stdout} {result.stderr}")

            if result.returncode != 0:
                err = result.stderr or result.stdout or f"Exit code {result.returncode}"
                raise RuntimeError(f"MinerU CLI failed: {err}")
            
            # MinerU typically writes to <out_dir>/<pdf_stem>/<pdf_stem>.md
            stem = input_path.stem
            possible_md = [
                out_dir / stem / f"{stem}.md",
                out_dir / f"{stem}.md",
            ]
            for p in possible_md:
                if p.exists():
                    content = p.read_text(encoding="utf-8")
                    logger.info(f"MinerU: Successfully converted, output length: {len(content)}")
                    return content
            
            # Fallback: find any .md file under out_dir
            md_files = list(out_dir.rglob("*.md"))
            if md_files:
                content = md_files[0].read_text(encoding="utf-8")
                logger.info(f"MinerU: Successfully converted (found {md_files[0]}), length: {len(content)}")
                return content
            
            raise RuntimeError("MinerU: No markdown output generated")
    
    async def convert_to_md(self, file_path: str) -> str:
        """Convert PDF to Markdown using MinerU CLI"""
        if not self.available:
            raise RuntimeError("MinerU is not available")
        
        try:
            return await asyncio.to_thread(self._convert_sync, file_path, "markdown")
        except Exception as e:
            logger.error(f"MinerU: Conversion failed: {e}")
            raise RuntimeError(f"MinerU conversion failed: {e}") from e
    
    async def convert_to_json(self, file_path: str) -> Dict[str, Any]:
        """Convert PDF to JSON using MinerU (returns markdown in content field)."""
        if not self.available:
            raise RuntimeError("MinerU is not available")
        
        md_content = await self.convert_to_md(file_path)
        return {
            "content": md_content,
            "format": "markdown",
            "library": self.name,
        }
    
    async def convert_to_text(self, file_path: str) -> str:
        """Convert PDF to plain text using MinerU (strip markdown)."""
        md_content = await self.convert_to_md(file_path)
        text = md_content
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        return text
