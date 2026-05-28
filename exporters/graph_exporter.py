from __future__ import annotations

from typing import Any


class GraphExporter:
    def export(self, root: Any) -> dict[str, list[dict[str, Any]]]:
        nodes: list[dict[str, Any]] = []
        links: list[dict[str, str]] = []
        self._visit(root, None, nodes, links, 0)
        return {"nodes": nodes, "links": links}

    def _visit(self, node: Any, parent_id: str | None, nodes: list[dict[str, Any]], links: list[dict[str, str]], index: int) -> int:
        node_id = f"n{index}"
        nodes.append({"id": node_id, "label": node.tree_label(), "kind": node.kind})
        if parent_id:
            links.append({"source": parent_id, "target": node_id})
        next_index = index + 1
        for child in node.children:
            next_index = self._visit(child, node_id, nodes, links, next_index)
        return next_index
