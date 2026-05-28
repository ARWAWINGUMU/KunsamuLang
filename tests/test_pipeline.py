from pathlib import Path

from manipulators import SourceManipulator
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


def test_source_manipulator_formats_and_renames_symbols():
    source = 'COMUNIDAD "A"{TERRITORIO "T"{ELEMENTO "Agua"{MENSAJE:"Vida"}}PROYECTO "P"{CURSO "C"{DURACION:1 mes ENFOQUE:ambiental}}}'
    manipulator = SourceManipulator()

    formatted = manipulator.format_source(source)
    renamed = manipulator.rename_symbol(formatted, "CURSO", "C", "Curso Renombrado")

    assert 'COMUNIDAD "A" {' in formatted
    assert 'CURSO "Curso Renombrado"' in renamed


def test_source_manipulator_auto_fixes_missing_course_attributes():
    source = Path("examples/invalid_semantic.kunsamu").read_text(encoding="utf-8")

    fixed = SourceManipulator().auto_fix(source)

    assert "ENFOQUE: intercultural" in fixed
    assert "DURACION: 1 mes" in fixed
    assert "Mensaje pendiente para Agua 2" in fixed
    assert 'ELEMENTO "Agua 2"' in fixed
