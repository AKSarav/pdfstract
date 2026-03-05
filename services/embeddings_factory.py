from typing import Dict, Optional, List
import importlib
import asyncio
from services.embeddings_wrappers.base import BaseEmbeddingsWrapper
from services.logger import logger

class EmbeddingsFactory:
    def __init__(self):
        # mapping: name -> (module_path, class_name)
        self._provider_classes: Dict[str, tuple] = {
            "openai": ("services.embeddings_wrappers.openai_wrapper", "OpenAIEmbeddingsWrapper"),
            "azure-openai": ("services.embeddings_wrappers.azure_openai_wrapper", "AzureOpenAIEmbeddingsWrapper"),
            "google-generative": ("services.embeddings_wrappers.google_wrapper", "GoogleGenerativeAIEmbeddingsWrapper"),
            "ollama": ("services.embeddings_wrappers.ollama_wrapper", "OllamaEmbeddingsWrapper"),
            "sentence-transformers": ("services.embeddings_wrappers.sentence_transformers_wrapper", "SentenceTransformersWrapper"),
            "model2vec": ("services.embeddings_wrappers.model2vec_wrapper", "Model2VecWrapper"),
        }
        self._providers: Dict[str, BaseEmbeddingsWrapper] = {}

    def _load_provider(self, name: str) -> Optional[BaseEmbeddingsWrapper]:
        if name in self._providers:
            return self._providers[name]

        if name not in self._provider_classes:
            return None

        module_path, class_name = self._provider_classes[name]
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            inst = cls()
            if inst.available:
                self._providers[name] = inst
                return inst
            else:
                # still cache the instance so validate_credentials can return meaningful message
                self._providers[name] = inst
                return inst
        except Exception:
            return None

    def get_embedding(self, name: str) -> Optional[BaseEmbeddingsWrapper]:
        if name == "auto":
            default = self.get_default_embedding()
            logger.info(f"Selected default embedding: {default}")
            if default:
                return self._load_provider(default)
            return None
        logger.info(f"Selected embedding: {name}")
        return self._load_provider(name)

    def list_available_embeddings(self) -> List[str]:
        available = []
        for name in self._provider_classes.keys():
            inst = self._load_provider(name)
            if inst and inst.available:
                available.append(name)
        return available

    def get_default_embedding(self) -> Optional[str]:
        # Priority: openai, sentence-transformers
        for name in ["openai", "sentence-transformers"]:
            inst = self._load_provider(name)
            if inst and inst.available:
                return name
        return None

    def list_all_providers(self) -> List[Dict]:
        """List all providers with their availability and configuration status"""
        result = []
        for name in self._provider_classes.keys():
            inst = self._load_provider(name)
            available = inst.available if inst else False
            ok, msg = inst.validate_credentials() if inst else (False, "Provider could not be loaded")
            
            result.append({
                "name": name,
                "available": available,
                "configured": ok,
                "message": msg
            })
        return result


    async def embed_texts_async(self, model: str, texts: List[str]) -> List[List[float]]:
        provider = self.get_embedding(model)
        if not provider:
            raise ValueError(f"Embedding provider '{model}' not found or unavailable")

        ok, msg = provider.validate_credentials()
        if not ok:
            raise ValueError(f"Credentials/config validation failed for '{provider.name}': {msg}")

        return await provider.embed_texts(texts)

    def embed_texts(self, model: str, texts: List[str]) -> List[List[float]]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # running in async loop; return coroutine wrapper
            return asyncio.ensure_future(self.embed_texts_async(model, texts))
        else:
            return asyncio.run(self.embed_texts_async(model, texts))


# Module-level singleton
_factory: Optional[EmbeddingsFactory] = None


def get_embeddings_factory() -> EmbeddingsFactory:
    global _factory
    if _factory is None:
        _factory = EmbeddingsFactory()
    return _factory
