import json
import pytest
from click.testing import CliRunner


def test_embeddings_list_cli(monkeypatch):
    """Test `pdfstract embeddings-list` returns exit code 0 and prints table header."""
    from cli import pdfstract
    runner = CliRunner()

    # Run command
    result = runner.invoke(pdfstract, ["embeddings-list"])
    assert result.exit_code == 0
    assert "Embedding Providers" in result.output


def test_embed_text_cli(monkeypatch, tmp_path):
    from cli import pdfstract
    runner = CliRunner()

    # Monkeypatch factory to avoid real external calls
    import services.embeddings_factory as efmod

    class FakeFactory:
        def embed_texts(self, model, texts):
            return [[0.0, 0.1, 0.2] for _ in texts]
        def get_converter_status(self, name):
            return None

    monkeypatch.setattr(efmod, "get_embeddings_factory", lambda: FakeFactory())

    # Provide text via --text
    result = runner.invoke(pdfstract, ["embed-text", "--text", "hello world", "--model", "openai"]) 
    assert result.exit_code == 0
    assert "Generated embedding of length" in result.output

    # Provide via stdin
    result = runner.invoke(pdfstract, ["embed-text", "--model", "openai"], input="stdin text")
    assert result.exit_code == 0
