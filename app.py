from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from interpreter import KunsamuInterpreter
from manipulators import SourceManipulator
from parser_engine import KunsamuLexer, KunsamuParser
from pipeline import KunsamuPipeline
from visitors.ast_builder import ASTBuilder


BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "web" / "templates"),
    static_folder=str(BASE_DIR / "web" / "static"),
)


@app.get("/")
def index():
    example = (BASE_DIR / "examples" / "valid_full.kunsamu").read_text(encoding="utf-8")
    return render_template("index.html", example=example)


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    result = KunsamuPipeline().analyze(source)
    return jsonify(result)


@app.post("/api/format")
def format_source():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    try:
        formatted = SourceManipulator().format_source(source)
        return jsonify({"success": True, "source": formatted})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/autofix")
def auto_fix():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    try:
        fixed = SourceManipulator().auto_fix(source)
        return jsonify({"success": True, "source": fixed})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/rename")
def rename_symbol():
    payload = request.get_json(silent=True) or {}
    try:
        renamed = SourceManipulator().rename_symbol(
            payload.get("source", ""),
            payload.get("kind", "CURSO"),
            payload.get("oldName", ""),
            payload.get("newName", ""),
        )
        return jsonify({"success": True, "source": renamed})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/query")
def query_source():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    query = payload.get("query", "").strip()

    if not query:
        return jsonify({"error": "Consulta vacía."}), 400

    tokens, lex_errors = KunsamuLexer().tokenize(source)
    if lex_errors:
        return jsonify({"error": lex_errors[0]["message"]}), 400

    parsed, syn_errors, _ = KunsamuParser(tokens).parse()
    if syn_errors:
        return jsonify({"error": syn_errors[0]["message"]}), 400

    ast_root = ASTBuilder().visit_program(parsed)
    result = KunsamuInterpreter(ast_root).execute(query)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
