from __future__ import annotations

from collections import Counter, defaultdict
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
walk = _nodes.walk
max_depth = _nodes.max_depth


class SemanticAnalyzer:
    VALID_ENFOQUES = {"intercultural", "ambiental", "espiritual", "territorial", "linguistico", "cultural"}
    VALID_DURATION_UNITS = {"dia", "dias", "semana", "semanas", "mes", "meses", "ano", "anos", "año", "años"}

    def analyze(self, root: Any) -> tuple[list[dict[str, Any]], dict[str, int]]:
        diagnostics: list[dict[str, Any]] = []
        self._check_duplicate_names(root, diagnostics)
        self._check_required_structure(root, diagnostics)
        self._check_attributes(root, diagnostics)
        return diagnostics, self._metrics(root)

    def _emit(self, diagnostics: list[dict[str, Any]], level: str, node: Any, message: str) -> None:
        diagnostics.append(
            {
                "level": level,
                "message": message,
                "line": getattr(node.location, "line", 1),
                "column": getattr(node.location, "column", 0),
                "node": node.tree_label(),
            }
        )

    def _check_duplicate_names(self, root: Any, diagnostics: list[dict[str, Any]]) -> None:
        grouped: dict[tuple[int, str], list[Any]] = defaultdict(list)
        for parent in walk(root):
            for child in parent.children:
                if child.name:
                    grouped[(id(parent), child.kind, child.name.lower())].append(child)
        for nodes in grouped.values():
            if len(nodes) > 1:
                self._emit(diagnostics, "error", nodes[1], f'Nombre duplicado "{nodes[1].name}" en bloques {nodes[1].kind}.')

    def _check_required_structure(self, root: Any, diagnostics: list[dict[str, Any]]) -> None:
        for node in walk(root):
            child_kinds = Counter(child.kind for child in node.children)
            if node.kind == "COMUNIDAD":
                if child_kinds["TERRITORIO"] == 0:
                    self._emit(diagnostics, "error", node, f'La comunidad "{node.name}" debe declarar al menos un TERRITORIO.')
                if child_kinds["PROYECTO"] == 0:
                    self._emit(diagnostics, "warning", node, f'La comunidad "{node.name}" no declara PROYECTO.')
            if node.kind == "TERRITORIO" and child_kinds["ELEMENTO"] == 0:
                self._emit(diagnostics, "warning", node, f'El territorio "{node.name}" no contiene ELEMENTO natural.')
            if node.kind == "PROYECTO" and child_kinds["CURSO"] == 0:
                self._emit(diagnostics, "error", node, f'El proyecto "{node.name}" debe contener al menos un CURSO.')

    def _check_attributes(self, root: Any, diagnostics: list[dict[str, Any]]) -> None:
        for node in walk(root):
            attrs = {key.upper(): value for key, value in node.attributes.items()}
            if node.kind == "ELEMENTO" and "MENSAJE" not in attrs:
                self._emit(diagnostics, "error", node, f'El elemento "{node.name}" debe tener MENSAJE.')
            if node.kind == "CURSO":
                if "DURACION" not in attrs:
                    self._emit(diagnostics, "error", node, f'El curso "{node.name}" no tiene atributo DURACION.')
                else:
                    duration = attrs["DURACION"]
                    amount = duration.get("amount") if isinstance(duration, dict) else None
                    unit = duration.get("unit") if isinstance(duration, dict) else None
                    if amount is None or amount <= 0:
                        self._emit(diagnostics, "error", node, f'El curso "{node.name}" tiene una duración inválida.')
                    if unit not in self.VALID_DURATION_UNITS:
                        self._emit(diagnostics, "error", node, f'La unidad de duración "{unit}" no es válida.')
                if "ENFOQUE" not in attrs:
                    self._emit(diagnostics, "error", node, f'El curso "{node.name}" no tiene atributo ENFOQUE.')
                elif str(attrs["ENFOQUE"]).lower() not in self.VALID_ENFOQUES:
                    self._emit(diagnostics, "warning", node, f'El enfoque "{attrs["ENFOQUE"]}" no está en el catálogo recomendado.')

    def _metrics(self, root: Any) -> dict[str, int]:
        nodes = walk(root)
        return {
            "comunidades": sum(1 for node in nodes if node.kind == "COMUNIDAD"),
            "territorios": sum(1 for node in nodes if node.kind == "TERRITORIO"),
            "proyectos": sum(1 for node in nodes if node.kind == "PROYECTO"),
            "cursos": sum(1 for node in nodes if node.kind == "CURSO"),
            "elementos": sum(1 for node in nodes if node.kind == "ELEMENTO"),
            "participantes": sum(1 for node in nodes if node.kind == "PARTICIPANTE"),
            "actividades": sum(1 for node in nodes if node.kind == "ACTIVIDAD"),
            "profundidad": max_depth(root),
        }
