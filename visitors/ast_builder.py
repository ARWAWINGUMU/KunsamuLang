from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
from typing import Any


_nodes_path = Path(__file__).resolve().parents[1] / "ast" / "nodes.py"
_spec = importlib.util.spec_from_file_location("kunsamu_ast_nodes", _nodes_path)
_nodes = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules[_spec.name] = _nodes
_spec.loader.exec_module(_nodes)

KunsamuNode = _nodes.KunsamuNode
SourceLocation = _nodes.SourceLocation


class ASTBuilder:
    """Visitor-style builder that maps parsed dictionaries into AST nodes."""

    def visit_program(self, parsed: list[dict[str, Any]]) -> Any:
        root = KunsamuNode(kind="PROGRAMA", name="KunsamuLang")
        for item in parsed:
            root.add_child(self.visit_block(item))
        return root

    def visit_block(self, block: dict[str, Any]) -> Any:
        node = KunsamuNode(
            kind=block["kind"],
            name=block.get("name"),
            attributes=block.get("attributes", {}),
            location=SourceLocation(block.get("line", 1), block.get("column", 0)),
        )
        for child in block.get("children", []):
            node.add_child(self.visit_block(child))
        return node
