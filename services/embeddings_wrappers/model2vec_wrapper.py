import os
from typing import List, Tuple, Optional
import asyncio
from .base import BaseEmbeddingsWrapper


class Model2VecWrapper(BaseEmbeddingsWrapper):
    name = "model2vec"
    available = False

    def __init__(self):
        try:
            import importlib
            gensim = importlib.import_module("gensim")
            self._gensim = gensim
            self._kv = None
            self.available = True
        except Exception:
            self._gensim = None
            self.available = False

        # Path to keyed vectors file can be provided via env
        self.model_path = os.environ.get("MODEL2VEC_PATH")

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        if not self.available:
            return False, "gensim package not installed"
        if not self.model_path:
            return False, "missing MODEL2VEC_PATH environment variable pointing to keyed vectors"
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.available:
            raise RuntimeError("gensim not available for Model2Vec wrapper")

        if self._kv is None:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._load_kv)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _load_kv(self):
        # load KeyedVectors from path
        self._kv = self._gensim.models.KeyedVectors.load(self.model_path)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        # simple approach: average word vectors; skip unknown words
        result = []
        for t in texts:
            words = t.split()
            vectors = []
            for w in words:
                if w in self._kv:
                    vectors.append(self._kv[w])
            if not vectors:
                result.append([0.0] * self._kv.vector_size)
            else:
                import numpy as _np
                arr = _np.mean(_np.stack(vectors), axis=0)
                result.append(arr.tolist())
        return result
