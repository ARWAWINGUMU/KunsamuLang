from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from manipulators import SourceManipulator
from pipeline import KunsamuPipeline


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


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
