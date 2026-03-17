import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class OllamaEmbeddingsWrapper(BaseEmbeddingsWrapper):
    name = "ollama"
    available = False

    def __init__(self):
        try:
            import importlib
            pack = importlib.import_module("langchain_ollama")
            self._pack = pack
            self.available = True
        except Exception:
            self._pack = None
            self.available = False

        # Default host
        self.host = os.environ.get("OLLAMA_HOST")
        self.model = os.environ.get("OLLAMA_MODEL")
        
        if not self.host or not self.model:
            print("OLLAMA_HOST or OLLAMA_MODEL not set; OllamaEmbeddingsWrapper will be unavailable")
            self.available = False

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        if not self.available:
            return False, "langchain_ollama package not installed"
        # Ollama typically runs locally; no API key required. Check reachability optionally.
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("langchain_ollama package not available for Ollama wrapper")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        if self._pack is None:
            raise RuntimeError("langchain_ollama package not loaded")
        if not self.host or not self.model:
            raise RuntimeError("OLLAMA_HOST and OLLAMA_MODEL must be set in environment variables")
        try:
            embeddings = self._pack.OllamaEmbeddings(model=self.model, base_url=self.host)
            return embeddings.embed_documents(texts)
        except Exception as e:
            raise RuntimeError(f"Ollama embedding failed: {str(e)}")        
