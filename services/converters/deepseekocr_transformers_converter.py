from typing import Dict, Any, Optional
import re
import asyncio
import tempfile
from pathlib import Path
from services.base import PDFConverter, DownloadStatus
from services.logger import logger

try:
    from transformers import AutoProcessor, AutoModelForVision2Seq
    import torch
    import pdf2image
    from PIL import Image
    DEEPSEEKOCR_TRANSFORMERS_AVAILABLE = True
except ImportError:
    DEEPSEEKOCR_TRANSFORMERS_AVAILABLE = False
    AutoProcessor = None
    AutoModelForVision2Seq = None
    torch = None
    pdf2image = None
    Image = None

class DeepSeekOCRTransformersConverter(PDFConverter):
    """Converter implementation for DeepSeek-OCR using transformers (works on CPU or GPU)"""
    
    def __init__(self):
        self._model = None
        self._processor = None
        self._device = torch.device("cuda" if DEEPSEEKOCR_TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else "cpu") if DEEPSEEKOCR_TRANSFORMERS_AVAILABLE else None
        self._init_error = None
        self._model_loaded = False
        self._max_new_tokens = 2048
        self._is_downloading = False
        self._download_error: Optional[str] = None
        
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE:
            self._init_error = "Required dependencies not installed: transformers, torch, pdf2image, pillow"
    
    def _ensure_model_loaded(self):
        """Lazy load the model only when needed"""
        if self._model_loaded:
            return
        
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE:
            raise RuntimeError("Required dependencies not installed: transformers, torch, pdf2image, pillow")
        
        try:
            model_name = 'deepseek-ai/DeepSeek-OCR'
            logger.info(f"Loading DeepSeek-OCR processor and model: {model_name}")
            
            self._patch_flash_attention()
            self._processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            
            if self._device is None:
                self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            dtype = torch.bfloat16 if (self._device.type == "cuda" and torch.cuda.is_available()) else torch.float32
            
            self._model = AutoModelForVision2Seq.from_pretrained(
                model_name,
                torch_dtype=dtype,
                trust_remote_code=True
            )
            self._model = self._model.to(self._device)
            self._model.eval()
            logger.info(f"DeepSeek-OCR model ready on device: {self._device}")
            
            self._model_loaded = True
            self._init_error = None
                    
        except Exception as e:
            self._model = None
            self._processor = None
            error_msg = str(e)
            self._init_error = error_msg
            logger.error(f"DeepSeek-OCR model loading failed: {error_msg}")
            logger.exception("Full error traceback:")
            raise RuntimeError(f"Failed to load DeepSeek-OCR model: {error_msg}")
    
    @property
    def name(self) -> str:
        return "deepseekocr"
    
    @property
    def available(self) -> bool:
        # Available if dependencies are installed (model will be loaded lazily)
        return DEEPSEEKOCR_TRANSFORMERS_AVAILABLE and torch.cuda.is_available()
    
    @property
    def error_message(self) -> str:
        """Get error message explaining why converter is unavailable"""
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE:
            return "Required dependencies not installed: transformers, torch, pdf2image, pillow. Also requires poppler (brew install poppler)."
        elif self._init_error:
            return f"Initialization failed: {self._init_error}"
        elif self._download_error:
            return self._download_error
        return "Available only on CUDA-enabled GPUs (downloads ~6.7GB on first use)."
    
    @property
    def requires_download(self) -> bool:
        return True
    
    @property
    def download_status(self) -> DownloadStatus:
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE:
            return DownloadStatus.NOT_STARTED
        if self._model_loaded:
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
        """Download and prepare DeepSeek-OCR models"""
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE:
            self._download_error = "Required dependencies not installed"
            return False
        
        if not torch.cuda.is_available():
            self._download_error = "DeepSeek-OCR requires a CUDA-enabled GPU"
            return False
        
        if self._model_loaded:
            return True
        
        self._is_downloading = True
        self._download_error = None
        
        try:
            logger.info("DeepSeek-OCR: Starting model download (~6.7GB)...")
            await asyncio.to_thread(self._ensure_model_loaded)
            self._is_downloading = False
            return True
        except Exception as e:
            self._is_downloading = False
            self._download_error = str(e)
            logger.error(f"DeepSeek-OCR: Preparation failed: {e}")
            return False

    def _patch_flash_attention(self):
        """Provide a stub for LlamaFlashAttention2 if transformers tries to import it."""
        if not DEEPSEEKOCR_TRANSFORMERS_AVAILABLE or torch is None:
            return
        try:
            from transformers.models.llama.modeling_llama import LlamaFlashAttention2  # type: ignore
            _ = LlamaFlashAttention2  # noqa
        except ImportError:
            import importlib
            llama_module = importlib.import_module("transformers.models.llama.modeling_llama")
            if hasattr(llama_module, "LlamaFlashAttention2"):
                return
            class LlamaFlashAttention2(torch.nn.Module):  # type: ignore
                def __init__(self, *args, **kwargs):
                    super().__init__()

                def forward(self, *args, **kwargs):
                    raise RuntimeError("flash_attention_2 is not available in this environment")
            llama_module.LlamaFlashAttention2 = LlamaFlashAttention2
            logger.info("Patched transformers LlamaFlashAttention2 with CPU-friendly stub")
    
    def _pdf_to_images(self, file_path: str, dpi: int = 200):
        """Convert PDF pages to PIL Images"""
        try:
            images = pdf2image.convert_from_path(file_path, dpi=dpi)
            return images
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error message for poppler missing
            if 'poppler' in error_msg.lower() or 'unable to get page count' in error_msg.lower():
                raise RuntimeError(
                    "Failed to convert PDF to images: Poppler is not installed. "
                    "Install with one of:\n"
                    "  macOS: brew install poppler\n"
                    "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                    "  Windows: https://github.com/oschwartz10612/poppler-windows/releases/"
                )
            raise RuntimeError(f"Failed to convert PDF to images: {error_msg}")

    def _generate_markdown_from_image(self, image, prompt: str) -> str:
        """Run DeepSeek-OCR model on a single image."""
        if not self._processor or not self._model:
            raise RuntimeError("DeepSeek-OCR model is not initialized")
        
        inputs = self._processor(images=image, text=prompt, return_tensors="pt")
        inputs = {k: v.to(self._device) if hasattr(v, "to") else v for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=self._max_new_tokens,
                do_sample=False,
                temperature=0.0,
            )
        text = self._processor.batch_decode(outputs, skip_special_tokens=True)
        return text[0].strip() if text else ""
    
    def _detect_pdf_content_type(self, file_path: str) -> str:
        """Detect if PDF contains mostly text or images"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                sample_pages = min(3, len(pdf_reader.pages))
                image_count = 0
                has_extractable_text = False
                
                for page_num in range(sample_pages):
                    page = pdf_reader.pages[page_num]
                    
                    # Count images
                    if '/Resources' in page and '/XObject' in page['/Resources']:
                        try:
                            xobjects = page['/Resources']['/XObject'].get_object()
                            for obj in xobjects:
                                if xobjects[obj]['/Subtype'] == '/Image':
                                    image_count += 1
                        except (KeyError, AttributeError):
                            pass
                    
                    # Check for extractable text
                    try:
                        text = page.extract_text()
                        if text and len(text.strip()) > 50:
                            has_extractable_text = True
                    except Exception:
                        pass
                
                if has_extractable_text and image_count == 0:
                    return 'text'
                elif image_count > 0:
                    return 'mixed' if has_extractable_text else 'image'
                else:
                    return 'image'
                    
        except Exception:
            return 'mixed'
    
    async def convert_to_md(self, file_path: str) -> str:
        if not self.available:
            raise RuntimeError("deepseekocr is not available. Requires CUDA-enabled GPU.")
        
        # Load model on first use (lazy loading)
        if not self._model_loaded:
            logger.info("Loading DeepSeek-OCR model (first use)...")
            self._ensure_model_loaded()
            logger.info("DeepSeek-OCR model ready")
        
        try:
            logger.info(f"Converting PDF to markdown: {file_path}")
            content_type = self._detect_pdf_content_type(file_path)
            logger.debug(f"PDF content type detected: {content_type}")
            
            if content_type == 'text':
                raise ValueError(
                    "DeepSeek-OCR is designed for image-based PDFs (scanned documents, PDFs with images). "
                    "This PDF appears to be text-only. Please use other converters like 'pymupdf4llm', "
                    "'markitdown', 'marker', or 'docling' for text-based PDFs."
                )
            
            dpi = 300 if content_type in ['image', 'mixed'] else 200
            logger.debug(f"Converting PDF to images with DPI: {dpi}")
            images = self._pdf_to_images(file_path, dpi=dpi)
            
            if not images:
                raise RuntimeError("No pages found in PDF")
            
            logger.info(f"Processing {len(images)} page(s) with DeepSeek-OCR")
            
            markdown_parts = []
            prompt = "<image>\n<|grounding|>Convert the document to markdown."
            
            for idx, image in enumerate(images):
                logger.debug(f"Processing page {idx + 1}/{len(images)}")
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                md_content = self._generate_markdown_from_image(image, prompt)
                if md_content and md_content.strip():
                    if len(images) > 1:
                        markdown_parts.append(f"## Page {idx + 1}\n\n{md_content}")
                    else:
                        markdown_parts.append(md_content)
            
            return "\n\n".join(markdown_parts) if markdown_parts else ""
            
        except ValueError as e:
            # User-friendly error for text-only PDFs
            logger.warning(f"DeepSeek-OCR conversion rejected: {str(e)}")
            raise
        except RuntimeError as e:
            error_msg = str(e)
            # Don't re-raise RuntimeErrors that we've already handled (like CUDA fallback)
            if 'cuda' in error_msg.lower() and ('not available' in error_msg.lower() or 'not compiled' in error_msg.lower()):
                # This should have been handled by the fallback, but if it still fails, provide helpful message
                logger.error(f"CUDA error persisted after fallback: {error_msg}")
                raise RuntimeError(
                    "DeepSeek-OCR conversion failed: CUDA is not available and CPU fallback failed. "
                    "Please ensure the model is properly loaded on CPU. "
                    "If you have a GPU, ensure PyTorch with CUDA support is installed."
                )
            else:
                raise
        except Exception as e:
            error_msg = str(e)
            # Provide user-friendly error messages
            if 'poppler' in error_msg.lower():
                error_msg = (
                    "DeepSeek-OCR conversion failed: Poppler is not installed. "
                    "Please install it: macOS: brew install poppler"
                )
            else:
                error_msg = f"DeepSeek-OCR conversion failed: {error_msg}"
            
            logger.error(error_msg)
            logger.exception("Full error traceback:")
            raise RuntimeError(error_msg)
    
    async def convert_to_json(self, file_path: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("deepseekocr is not available. Requires CUDA-enabled GPU.")
        
        # Load model on first use (lazy loading)
        if not self._model_loaded:
            self._ensure_model_loaded()
        
        try:
            content_type = self._detect_pdf_content_type(file_path)
            
            if content_type == 'text':
                raise ValueError(
                    "DeepSeek-OCR is designed for image-based PDFs (scanned documents, PDFs with images). "
                    "This PDF appears to be text-only. Please use other converters like 'pymupdf4llm', "
                    "'markitdown', 'marker', or 'docling' for text-based PDFs."
                )
            
            dpi = 300 if content_type in ['image', 'mixed'] else 200
            images = self._pdf_to_images(file_path, dpi=dpi)
            
            if not images:
                raise RuntimeError("No pages found in PDF")
            
            prompt = "<image>\n<|grounding|>Convert the document to markdown."
            pages_data = []
            
            for idx, image in enumerate(images):
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                md_content = self._generate_markdown_from_image(image, prompt)
                pages_data.append({
                    "page": idx + 1,
                    "content": md_content,
                    "format": "markdown"
                })
            
            return {
                "content": pages_data if len(pages_data) > 1 else (pages_data[0] if pages_data else {}),
                "format": "json",
                "library": self.name,
                "total_pages": len(images)
            }
            
        except ValueError as e:
            # User-friendly error for text-only PDFs
            logger.warning(f"DeepSeek-OCR JSON conversion rejected: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"DeepSeek-OCR JSON conversion failed: {str(e)}"
            logger.error(error_msg)
            logger.exception("Full error traceback:")
            raise RuntimeError(error_msg)
    
    async def convert_to_text(self, file_path: str) -> str:
        # Convert to markdown first, then extract plain text
        md_content = await self.convert_to_md(file_path)
        # Simple markdown to text conversion
        text = re.sub(r'#+\s+', '', md_content)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.*?)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text

