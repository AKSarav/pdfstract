from pathlib import Path
import json

from click.testing import CliRunner

from cli import pdfstract


SAMPLES_DIR = Path(__file__).parent / "samples"


def test_cli_chunk_command_with_text_file(tmp_path):
    """
    Validate `pdfstract chunk` on a simple text file.

    This exercises the CLI chunking path (token chunker via PDFStract.chunk_text)
    without depending on any PDF converters.
    """
    runner = CliRunner()

    text_file = tmp_path / "sample.txt"
    text_file.write_text("This is a test sentence. " * 40, encoding="utf-8")

    output_path = tmp_path / "chunks.json"

    result = runner.invoke(
        pdfstract,
        [
            "chunk",
            str(text_file),
            "--chunker",
            "token",
            "--chunk-size",
            "128",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, f"CLI chunk failed: {result.output}"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "chunks" in data
    assert data["total_chunks"] >= 1


def test_cli_convert_chunk_pipeline(tmp_path):
    """
    Validate `pdfstract convert-chunk` end‑to‑end with a real PDF.

    Uses the pymupdf4llm converter and token chunker, writing a JSON
    output file and verifying its structure.
    """
    runner = CliRunner()

    pdf_path = SAMPLES_DIR / "sample1.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"

    output_path = tmp_path / "convert_chunk_cli.json"

    result = runner.invoke(
        pdfstract,
        [
            "convert-chunk",
            str(pdf_path),
            "--library",
            "pymupdf4llm",
            "--chunker",
            "token",
            "--format",
            "markdown",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, f"CLI convert-chunk failed: {result.output}"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "conversion" in data
    assert "chunking" in data
    assert "chunks" in data["chunking"]
    assert len(data["chunking"]["chunks"]) >= 1


def test_cli_convert_chunk_embed_with_fake_embeddings(tmp_path, monkeypatch):
    """
    Validate `pdfstract convert-chunk-embed` end‑to‑end without external embedding credentials.

    We monkeypatch the embeddings factory used by the pdfstract API so the
    CLI can successfully generate embeddings without real API keys.
    """
    import pdfstract.api as api_mod

    class FakeEmbeddingsFactory:
        async def embed_texts_async(self, model: str, texts):
            return [[0.0, 0.1, 0.2] for _ in texts]

    monkeypatch.setattr(api_mod, "get_embeddings_factory", lambda: FakeEmbeddingsFactory())

    runner = CliRunner()

    pdf_path = SAMPLES_DIR / "sample1.pdf"
    assert pdf_path.exists(), f"Missing sample PDF at {pdf_path}"

    output_path = tmp_path / "convert_chunk_embed_cli.json"

    result = runner.invoke(
        pdfstract,
        [
            "convert-chunk-embed",
            str(pdf_path),
            "--library",
            "pymupdf4llm",
            "--chunker",
            "token",
            "--embedding",
            "auto",
            "--format",
            "markdown",
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, f"CLI convert-chunk-embed failed: {result.output}"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "chunking" in data
    assert "embeddings" in data
    assert isinstance(data["chunking"]["chunks"], list)
    assert len(data["chunking"]["chunks"]) >= 1
    assert isinstance(data["embeddings"], list)
    assert len(data["embeddings"]) == len(data["chunking"]["chunks"])
