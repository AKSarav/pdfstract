# Lightweight package init - do NOT import OCRFactory, embeddings_factory, or
# ocrfactory here, so that CLI startup (e.g. "from services.cli_factory import ...")
# does not pull in all converters and heavy deps (Paddle, torch, marker, etc.).
# Import those directly where needed: "from services.ocrfactory import OCRFactory".
from services.base import PDFConverter, OutputFormat

__all__ = ["PDFConverter", "OutputFormat"]
