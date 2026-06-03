from __future__ import annotations

import re
from typing import Any


class KunsamuInterpreter:
    KINDS = {"COMUNIDAD", "TERRITORIO", "ELEMENTO", "PROYECTO", "CURSO", "PARTICIPANTE", "ACTIVIDAD", "PROGRAMA"}

    def __init__(self, root: Any):
        self.root = root

    def execute(self, query: str) -> dict[str, Any]:
        tokens = self._tokenize(query)
        if not tokens:
            return {"error": "Consulta vacía."}

        cmd = tokens[0].upper()
        rest = tokens[1:]

        if cmd == "BUSCAR":
            return self._buscar(rest)
        if cmd == "CONTAR":
            return self._contar(rest)
        if cmd == "LISTAR":
            return self._listar(rest)
        if cmd == "RUTA":
            return self._ruta(rest)
        if cmd == "REPORTE":
            return self._reporte()
        return {
            "error": (
                f'Comando desconocido: "{cmd}". '
                "Comandos disponibles: BUSCAR, CONTAR, LISTAR, RUTA, REPORTE."
            )
        }

    # ── tokenizer ────────────────────────────────────────────────────────────

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'"[^"]*"|\S+', text.strip())

    # ── AST traversal ────────────────────────────────────────────────────────

    def _walk(self, node: Any) -> list[Any]:
        result = [node]
        for child in node.children:
            result.extend(self._walk(child))
        return result

    def _collect(self, kind: str, scope_kind: str | None, scope_name: str | None) -> list[Any]:
        if scope_kind and scope_name:
            anchors = [
                n for n in self._walk(self.root)
                if n.kind == scope_kind and n.name and n.name.lower() == scope_name.lower()
            ]
            nodes: list[Any] = []
            for anchor in anchors:
                nodes.extend(n for n in self._walk(anchor) if n.kind == kind and n is not anchor)
            return nodes
        return [n for n in self._walk(self.root) if n.kind == kind]

    def _filter_where(self, nodes: list[Any], attr: str, op: str, value: str) -> list[Any]:
        out = []
        for node in nodes:
            raw = {k.upper(): v for k, v in node.attributes.items()}.get(attr)
            if raw is None:
                continue
            node_val = (
                str(raw.get("amount", "")).lower() if isinstance(raw, dict) else str(raw).lower()
            )
            if op == "=" and node_val == value:
                out.append(node)
            elif op == "!=" and node_val != value:
                out.append(node)
            elif op in (">", "<"):
                try:
                    passes = float(node_val) > float(value) if op == ">" else float(node_val) < float(value)
                    if passes:
                        out.append(node)
                except ValueError:
                    pass
        return out

    # ── clause parsers ───────────────────────────────────────────────────────

    def _parse_scope(self, tokens: list[str]) -> tuple[str | None, str | None, list[str]]:
        if len(tokens) >= 3 and tokens[0].upper() == "EN" and tokens[1].upper() in self.KINDS:
            return tokens[1].upper(), tokens[2].strip('"'), tokens[3:]
        return None, None, tokens

    def _parse_where(self, tokens: list[str]) -> tuple[str | None, str | None, str | None]:
        if len(tokens) >= 4 and tokens[0].upper() == "DONDE":
            return tokens[1].upper(), tokens[2], tokens[3].strip('"').lower()
        return None, None, None

    def _as_result(self, node: Any) -> dict[str, Any]:
        return {
            "kind": node.kind,
            "name": node.name,
            "attributes": node.attributes,
            "location": {"line": node.location.line, "column": node.location.column},
        }

    # ── commands ─────────────────────────────────────────────────────────────

    def _buscar(self, tokens: list[str]) -> dict[str, Any]:
        if not tokens:
            return {"error": "BUSCAR requiere un tipo de nodo. Ej: BUSCAR CURSO"}
        kind = tokens[0].upper()
        if kind not in self.KINDS:
            return {"error": f'Tipo desconocido: "{kind}". Tipos: COMUNIDAD, TERRITORIO, ELEMENTO, PROYECTO, CURSO, PARTICIPANTE, ACTIVIDAD'}
        scope_kind, scope_name, tokens = self._parse_scope(tokens[1:])
        attr, op, value = self._parse_where(tokens)

        nodes = self._collect(kind, scope_kind, scope_name)
        if attr:
            nodes = self._filter_where(nodes, attr, op, value)

        scope_str = f' en {scope_kind} "{scope_name}"' if scope_kind else ""
        where_str = f" donde {attr} {op} {value}" if attr else ""
        return {
            "results": [self._as_result(n) for n in nodes],
            "count": len(nodes),
            "summary": f"Se encontraron {len(nodes)} {kind.lower()}(s){scope_str}{where_str}.",
        }

    def _contar(self, tokens: list[str]) -> dict[str, Any]:
        if not tokens:
            return {"error": "CONTAR requiere un tipo de nodo. Ej: CONTAR CURSO"}
        kind = tokens[0].upper()
        if kind not in self.KINDS:
            return {"error": f'Tipo desconocido: "{kind}"'}
        scope_kind, scope_name, tokens = self._parse_scope(tokens[1:])
        attr, op, value = self._parse_where(tokens)

        nodes = self._collect(kind, scope_kind, scope_name)
        if attr:
            nodes = self._filter_where(nodes, attr, op, value)

        scope_str = f' en {scope_kind} "{scope_name}"' if scope_kind else ""
        where_str = f" donde {attr} {op} {value}" if attr else ""
        return {
            "count": len(nodes),
            "summary": f"Total de {kind.lower()}(s){scope_str}{where_str}: {len(nodes)}.",
        }

    def _listar(self, tokens: list[str]) -> dict[str, Any]:
        if not tokens:
            return {"error": "LISTAR requiere un tipo de nodo. Ej: LISTAR COMUNIDAD"}
        kind = tokens[0].upper()
        if kind not in self.KINDS:
            return {"error": f'Tipo desconocido: "{kind}"'}
        scope_kind, scope_name, _ = self._parse_scope(tokens[1:])

        nodes = self._collect(kind, scope_kind, scope_name)
        names = [n.name for n in nodes if n.name]

        scope_str = f' en {scope_kind} "{scope_name}"' if scope_kind else ""
        names_str = ", ".join(f'"{n}"' for n in names) if names else "ninguno"
        return {
            "names": names,
            "count": len(names),
            "summary": f"{kind}(s){scope_str}: {names_str}.",
        }

    def _ruta(self, tokens: list[str]) -> dict[str, Any]:
        if len(tokens) < 2:
            return {"error": 'RUTA requiere tipo y nombre. Ej: RUTA CURSO "Saberes de Origen"'}
        kind = tokens[0].upper()
        name = tokens[1].strip('"')

        path = self._find_path(self.root, kind, name, [])
        if not path:
            return {"error": f'No se encontró {kind} "{name}".'}

        labels = [f'{n.kind}: "{n.name}"' if n.name else n.kind for n in path]
        return {
            "path": [self._as_result(n) for n in path],
            "summary": " → ".join(labels),
        }

    def _find_path(self, node: Any, kind: str, name: str, current: list) -> list | None:
        path = current + [node]
        if node.kind == kind and node.name and node.name.lower() == name.lower():
            return path
        for child in node.children:
            result = self._find_path(child, kind, name, path)
            if result:
                return result
        return None

    def _reporte(self) -> dict[str, Any]:
        comunidades = [n for n in self._walk(self.root) if n.kind == "COMUNIDAD"]
        rows = []
        for com in comunidades:
            sub = self._walk(com)
            rows.append({
                "comunidad": com.name,
                "territorios": sum(1 for n in sub if n.kind == "TERRITORIO"),
                "elementos": sum(1 for n in sub if n.kind == "ELEMENTO"),
                "proyectos": sum(1 for n in sub if n.kind == "PROYECTO"),
                "cursos": sum(1 for n in sub if n.kind == "CURSO"),
                "participantes": sum(1 for n in sub if n.kind == "PARTICIPANTE"),
                "actividades": sum(1 for n in sub if n.kind == "ACTIVIDAD"),
            })

        lines = [
            f'Comunidad "{r["comunidad"]}": {r["territorios"]} territorio(s), '
            f'{r["proyectos"]} proyecto(s), {r["cursos"]} curso(s), '
            f'{r["participantes"]} participante(s), {r["actividades"]} actividad(es).'
            for r in rows
        ]
        return {
            "reporte": rows,
            "summary": "\n".join(lines) if lines else "No se encontraron comunidades.",
        }
