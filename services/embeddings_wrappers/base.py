from typing import List, Tuple, Optional


class BaseEmbeddingsWrapper:
    """Base interface for embeddings provider wrappers.

    Implementations must provide:
      - name: str
      - available: bool
      - async def embed_texts(texts: List[str]) -> List[List[float]]
      - def validate_credentials() -> Tuple[bool, Optional[str]]  # (ok, message)
    """

    name: str = "base"
    available: bool = False

    def __init__(self):
        pass

    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        """Return (True, None) if credentials/config are OK, otherwise (False, message).

        This method must not print secret values; only return which env var or config is missing.
        """
        return True, None

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts asynchronously. Must be implemented by subclasses."""
        raise NotImplementedError()

    async def embed_text(self, text: str) -> List[float]:
        vecs = await self.embed_texts([text])
        return vecs[0]
