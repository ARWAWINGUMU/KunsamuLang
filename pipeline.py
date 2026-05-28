from __future__ import annotations

import json
from typing import Any

from exporters.graph_exporter import GraphExporter
from exporters.json_exporter import JSONExporter
from exporters.xml_exporter import XMLExporter
from parser_engine import KunsamuLexer, KunsamuParser
from semantic.analyzer import SemanticAnalyzer
from visitors.ast_builder import ASTBuilder


class KunsamuPipeline:
    def analyze(self, source: str) -> dict[str, Any]:
        lexer = KunsamuLexer()
        tokens, lexical_errors = lexer.tokenize(source)

        parser = KunsamuParser(tokens)
        parsed, syntax_errors, parse_tree = parser.parse()

        ast_root = ASTBuilder().visit_program(parsed)
        semantic_diagnostics, metrics = SemanticAnalyzer().analyze(ast_root)

        json_text = JSONExporter().export(ast_root)
        xml_text = XMLExporter().export(ast_root)
        graph = GraphExporter().export(ast_root)

        diagnostics = [
            *[{**item, "stage": "léxico"} for item in lexical_errors],
            *[{**item, "stage": "sintáctico"} for item in syntax_errors],
            *[{**item, "stage": "semántico"} for item in semantic_diagnostics],
        ]

        return {
            "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
            "parseTree": parse_tree,
            "ast": ast_root.to_dict(),
            "diagnostics": diagnostics,
            "json": json_text,
            "xml": xml_text,
            "graph": graph,
            "metrics": metrics,
            "success": not any(item.get("level") == "error" for item in diagnostics),
            "jsonObject": json.loads(json_text),
        }
