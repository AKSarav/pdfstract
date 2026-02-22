import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class SentenceTransformersWrapper(BaseEmbeddingsWrapper):
    name = "sentence-transformers"
    available = False

    def __init__(self, model_name: str | None = None):
        try:
            import importlib
            st = importlib.import_module("sentence_transformers")
            self._st = st
            self.model_name = model_name or os.environ.get("SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2")
            # Don't load the heavy model at import time; load lazily
            self._model = None
            self.available = True
        except Exception:
            self._st = None
            self._model = None
            self.available = False

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        # sentence-transformers requires no API keys; only package availability
        if not self.available:
            return False, "sentence-transformers package not installed"
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("sentence-transformers not available")

        # Load model lazily (may download weights on first use)
        if self._model is None:
            # blocking load - run in executor
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._load_model)

        # Use executor for encoding
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._encode_sync, texts)

    def _load_model(self):
        self._model = self._st.SentenceTransformer(self.model_name)

    def _encode_sync(self, texts: List[str]) -> List[List[float]]:
        arr = self._model.encode(texts, show_progress_bar=False)
        # Convert numpy arrays to lists if necessary
        try:
            return arr.tolist()
        except Exception:
            return [list(x) for x in arr]
