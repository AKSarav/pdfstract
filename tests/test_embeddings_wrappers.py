import os
import asyncio
import pytest

from services.embeddings_wrappers.base import BaseEmbeddingsWrapper


def test_base_wrapper_interface():
    b = BaseEmbeddingsWrapper()
    ok, msg = b.validate_credentials()
    assert ok is True


@pytest.mark.parametrize("wrapper_path,cls_name,env_vars", [
    ("services.embeddings_wrappers.openai_wrapper", "OpenAIEmbeddingsWrapper", ["OPENAI_API_KEY"]),
    ("services.embeddings_wrappers.azure_openai_wrapper", "AzureOpenAIEmbeddingsWrapper", ["AZURE_OPENAI_API_KEY","AZURE_OPENAI_ENDPOINT","AZURE_OPENAI_EMBEDDING_MODEL","AZURE_OPENAI_API_VERSION"]),
    ("services.embeddings_wrappers.google_wrapper", "GoogleGenerativeAIEmbeddingsWrapper", ["GOOGLE_API_KEY"]),
    ("services.embeddings_wrappers.ollama_wrapper", "OllamaEmbeddingsWrapper", []),
    ("services.embeddings_wrappers.sentence_transformers_wrapper", "SentenceTransformersWrapper", []),
    ("services.embeddings_wrappers.model2vec_wrapper", "Model2VecWrapper", ["MODEL2VEC_PATH"]),
])
def test_wrapper_validate_and_embed_smoke(wrapper_path, cls_name, env_vars, monkeypatch):
    """Smoke test: instantiate wrapper, call validate_credentials and ensure embed_texts behaves predictably.

    We do not call real external services; instead when provider reports not available, embed_texts should raise.
    If provider is available (package present in environment), we avoid network by monkeypatching the embed_texts implementation.
    """
    import importlib
    mod = importlib.import_module(wrapper_path)
    cls = getattr(mod, cls_name)

    # Clear env vars for the test to exercise missing-credential paths
    for v in env_vars:
        monkeypatch.delenv(v, raising=False)

    inst = cls()

    # validate_credentials returns tuple
    ok, msg = inst.validate_credentials()
    assert isinstance(ok, bool)

    # If available is False, embed_texts should raise
    if not getattr(inst, "available", False):
        with pytest.raises(RuntimeError):
            asyncio.run(inst.embed_texts(["test"]))
    else:
        # If available, monkeypatch embed_texts to avoid external calls
        async def fake_embed(texts):
            return [[0.1, 0.2]] * len(texts)

        monkeypatch.setattr(inst, "embed_texts", fake_embed)
        vecs = asyncio.run(inst.embed_texts(["hello"]))
        assert isinstance(vecs, list)
        assert len(vecs) == 1
