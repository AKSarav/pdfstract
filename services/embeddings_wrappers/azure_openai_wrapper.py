import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class AzureOpenAIEmbeddingsWrapper(BaseEmbeddingsWrapper):
    name = "azure-openai"
    available = False

    def __init__(self):
        try:
            import importlib
            # prefer azure.ai.openai if available
            azure_mod = None
            try:
                azure_mod = importlib.import_module("langchain_openai")
            except Exception:
                azure_mod = None
            self._client_module = azure_mod
            self.available = True if azure_mod is not None else False
        except Exception:
            self._client_module = None
            self.available = False

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        if not self.available:
            return False, "AzureOpenAIEmbeddings package not installed"
        if not os.environ.get("AZURE_OPENAI_API_KEY"):
            return False, "missing AZURE_OPENAI_API_KEY"
        if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
            return False, "missing AZURE_OPENAI_ENDPOINT"
        if not os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL"):
            return False, "missing AZURE_OPENAI_EMBEDDING_MODEL"
        if not os.environ.get("AZURE_OPENAI_API_VERSION"):
            return False, "missing AZURE_OPENAI_API_VERSION"
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("AzureOpenAIEmbeddings client not available")

        # Use executor for blocking network calls
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        # Minimal implementation using AzureOpenAIEmbeddings SDK
        mod = self._client_module
        if mod is None:
            raise RuntimeError("AzureOpenAIEmbeddings module not loaded")
        
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        model = os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL")
        version= os.environ.get("AZURE_OPENAI_API_VERSION")
        
        if None in (api_key, endpoint, model, version):
            raise RuntimeError("Missing one of AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_EMBEDDING_MODEL, AZURE_OPENAI_API_VERSION")    
        
        print(f"Using Azure OpenAI with endpoint {endpoint} and model {model} (version {version})")
        
        # Import here to avoid module-level dependency
        embed_model = mod.AzureOpenAIEmbeddings(
            api_key=api_key,
            azure_endpoint=endpoint, 
            model=model, 
            openai_api_version=version
            )
        try:
            return embed_model.embed_documents(texts)
        except Exception as e:
            raise RuntimeError(f"Error embedding documents: {e}")
