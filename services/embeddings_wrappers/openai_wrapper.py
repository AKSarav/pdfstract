import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class OpenAIEmbeddingsWrapper(BaseEmbeddingsWrapper):
    name = "openai"
    available = False

    def __init__(self):
        # Do not import openai at module import time
        try:
            import importlib
            openai = importlib.import_module("langchain_openai")
            self._openai = openai
            self.available = True
        except Exception:
            self._openai = None
            self.available = False

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        # OpenAI requires OPENAI_API_KEY
        if not self.available:
            return False, "langchain-openai package not installed"
        if not os.environ.get("OPENAI_API_KEY"):
            return False, "missing env var OPENAI_API_KEY"
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("OpenAI client not available (missing package)")

        # Use thread executor for blocking HTTP calls
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        # Import here to ensure lazy loading
        openai = self._openai
        
        # model choice: prefer text-embedding-3-small if available
        model = os.environ.get("OPENAI_EMBEDDING_MODEL")
        if not model:
            print("Warning: OPENAI_EMBEDDING_MODEL not set, defaulting to text-embedding-3-small")
            model = "text-embedding-3-small"
        
        res = openai.OpenAIEmbeddings( 
            model=model
        )
        try:
            res = res.embed_documents(texts)
        except Exception as e:
            raise RuntimeError(f"OpenAI embedding failed: {str(e)}")
        
        return res