import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class GoogleGenerativeAIEmbeddingsWrapper(BaseEmbeddingsWrapper):
    name = "google-generative"
    available = False

    def __init__(self):
        try:
            import importlib
            gmod = importlib.import_module("langchain_google_genai")
            self._gmod = gmod
            self.available = True
        except Exception:
            self._gmod = None
            self.available = False

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        # Basic check: either GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS
        if not self.available:
            return False, "langchain_google_genai package not installed"
        if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_EMBEDDING_MODEL")):
            return False, "missing GOOGLE_API_KEY or GOOGLE_EMBEDDING_MODEL environment variable"
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("langchain_google_genai client not available")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        # Minimal usage - expects langchain_google_genai to be configured via env
        if self._gmod is None or self.validate_credentials()[0] is False:
            raise RuntimeError("langchain_google_genai package not loaded or credentials not valid")
        try:
            model = os.environ.get("GOOGLE_EMBEDDING_MODEL")
            embeddings = self._gmod.GoogleGenerativeAIEmbeddings(model=model)
            return embeddings.embed_documents(texts)
        except Exception as e:
            raise RuntimeError(f"Google Generative AI embedding failed: {str(e)}")
