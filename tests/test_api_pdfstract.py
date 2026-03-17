import json
from pathlib import Path

import pytest

from pdfstract import PDFStract


SAMPLES_DIR = Path(__file__).parent / "samples"


@pytest.mark.parametrize("library", ["pymupdf4llm"])
def test_convert_sync_and_async_roundtrip(library: str):
    """Basic smoke tests for PDFStract.convert() and convert_async()."""
    pdf_path = SAMPLES_DIR / "sample1.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"

    ps = PDFStract()

    # Synchronous
    md = ps.convert(pdf_path, library=library, output_format="markdown")
    assert isinstance(md, str)
    assert len(md) > 0

    # Async
    import asyncio

    async def _run():
        return await ps.convert_async(pdf_path, library=library, output_format="markdown")

    md_async = asyncio.run(_run())
    assert isinstance(md_async, str)
    assert len(md_async) > 0


def test_chunk_text_token_basic():
    """Chunk a simple string with the token chunker."""
    text = "This is a short sentence. " * 50
    ps = PDFStract()

    result = ps.chunk_text(text, chunker="token", chunk_size=64, chunk_overlap=0)
    assert isinstance(result, dict)
    assert "chunks" in result
    assert result["total_chunks"] >= 1
    assert result["total_tokens"] >= 1


def test_list_libraries_and_chunkers():
    """Ensure list_libraries / list_available_libraries / list_chunkers work."""
    ps = PDFStract()

    libs_full = ps.list_libraries()
    libs_names = ps.list_available_libraries()
    chunkers = ps.list_chunkers()

    assert isinstance(libs_full, list)
    assert all("name" in lib for lib in libs_full)
    assert isinstance(libs_names, list)
    assert all(isinstance(name, str) for name in libs_names)
    assert isinstance(chunkers, list)
    assert all("name" in c for c in chunkers)


def test_convert_chunk_pipeline(tmp_path: Path):
    """End‑to‑end convert+chunk pipeline using convert_chunk()."""
    pdf_path = SAMPLES_DIR / "sample2.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"

    ps = PDFStract()

    result = ps.convert_chunk(
        pdf_path=pdf_path,
        library="pymupdf4llm",
        chunker="token",
        output_format="markdown",
        chunker_params={"chunk_size": 256, "chunk_overlap": 0},
    )

    assert isinstance(result, dict)
    assert "extracted_content" in result
    assert "chunking_result" in result
    chunks = result["chunking_result"]["chunks"]
    assert isinstance(chunks, list)
    assert len(chunks) >= 1

    # Optionally write output for manual inspection
    out_path = tmp_path / "convert_chunk_result.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert out_path.exists()


def test_convert_chunk_embed_with_fake_embeddings(monkeypatch, tmp_path: Path):
    """
    Test convert_chunk_embed() end‑to‑end without requiring real embedding credentials.

    We monkeypatch the get_embeddings_factory used by pdfstract.api.embed_texts_async
    to avoid hitting OpenAI / other providers or requiring API keys.
    """
    import pdfstract.api as api_mod

    class FakeEmbeddingsFactory:
        async def embed_texts_async(self, model: str, texts):
            # Return a small fixed‑size vector per input text
            return [[0.0, 0.1, 0.2] for _ in texts]

    # Monkeypatch the function name imported into pdfstract.api
    monkeypatch.setattr(api_mod, "get_embeddings_factory", lambda: FakeEmbeddingsFactory())

    pdf_path = SAMPLES_DIR / "sample1.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"

    ps = PDFStract()

    # Use explicit library/chunker so we don't rely on 'auto' for this test
    result = ps.convert_chunk_embed(
        pdf_path=pdf_path,
        library="pymupdf4llm",
        chunker="token",
        embedding="auto",
        output_format="markdown",
        chunker_params={"chunk_size": 256, "chunk_overlap": 0},
    )

    # Basic structure checks
    assert "extracted_content" in result
    assert "chunking_result" in result
    assert "embeddings" in result

    chunking_result = result["chunking_result"]
    chunks = chunking_result["chunks"]
    embeddings = result["embeddings"]

    assert isinstance(chunks, list) and len(chunks) >= 1
    assert isinstance(embeddings, list)
    assert len(embeddings) == len(chunks)

    # Each chunk should now carry an embedding field
    for chunk in chunks:
        assert "embedding" in chunk
        assert isinstance(chunk["embedding"], list)
        assert len(chunk["embedding"]) == 3

    out_path = tmp_path / "convert_chunk_embed_result.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert out_path.exists()

