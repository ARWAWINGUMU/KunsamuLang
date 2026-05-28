from pathlib import Path

from pipeline import KunsamuPipeline


def test_valid_example_has_no_errors():
    source = Path("examples/valid_full.kunsamu").read_text(encoding="utf-8")
    result = KunsamuPipeline().analyze(source)

    assert result["success"] is True
    assert result["metrics"]["comunidades"] == 1
    assert result["metrics"]["cursos"] == 2
    assert result["metrics"]["elementos"] == 2


def test_invalid_example_reports_semantic_errors():
    source = Path("examples/invalid_semantic.kunsamu").read_text(encoding="utf-8")
    result = KunsamuPipeline().analyze(source)

    messages = " ".join(item["message"] for item in result["diagnostics"])
    assert result["success"] is False
    assert "Nombre duplicado" in messages
    assert "ENFOQUE" in messages
    assert "duración inválida" in messages
