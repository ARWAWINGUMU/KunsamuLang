from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceLocation:
    line: int = 1
    column: int = 0


@dataclass
class KunsamuNode:
    kind: str
    name: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    children: list["KunsamuNode"] = field(default_factory=list)
    location: SourceLocation = field(default_factory=SourceLocation)

    def add_child(self, node: "KunsamuNode") -> None:
        self.children.append(node)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "attributes": self.attributes,
            "location": {"line": self.location.line, "column": self.location.column},
            "children": [child.to_dict() for child in self.children],
        }

    def tree_label(self) -> str:
        return f"{self.kind}: {self.name}" if self.name else self.kind


def max_depth(node: KunsamuNode) -> int:
    if not node.children:
        return 1
    return 1 + max(max_depth(child) for child in node.children)


def walk(node: KunsamuNode) -> list[KunsamuNode]:
    nodes = [node]
    for child in node.children:
        nodes.extend(walk(child))
    return nodes
