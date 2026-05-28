from __future__ import annotations

import re
from typing import Any

from parser_engine import KunsamuLexer, KunsamuParser


class SourceManipulator:
    """Automatic source-code manipulation utilities for KunsamuLang programs."""

    def format_source(self, source: str) -> str:
        parsed = self._parse(source)
        return "\n\n".join(self._render_block(block, 0) for block in parsed).strip() + "\n"

    def auto_fix(self, source: str) -> str:
        parsed = self._parse(source)
        self._dedupe_children(parsed)
        for block in self._walk_blocks(parsed):
            attrs = block.setdefault("attributes", {})
            if block["kind"] == "ELEMENTO" and "MENSAJE" not in attrs:
                attrs["MENSAJE"] = f"Mensaje pendiente para {block.get('name', 'elemento')}"
            if block["kind"] == "CURSO":
                duration = attrs.get("DURACION")
                if not isinstance(duration, dict) or not duration.get("amount") or duration.get("amount", 0) <= 0:
                    attrs["DURACION"] = {"amount": 1, "unit": "mes"}
                if "ENFOQUE" not in attrs:
                    attrs["ENFOQUE"] = "intercultural"
        return "\n\n".join(self._render_block(block, 0) for block in parsed).strip() + "\n"

    def rename_symbol(self, source: str, kind: str, old_name: str, new_name: str) -> str:
        kind = kind.upper().strip()
        if kind not in {"COMUNIDAD", "TERRITORIO", "ELEMENTO", "PROYECTO", "CURSO", "PARTICIPANTE", "ACTIVIDAD"}:
            raise ValueError(f"Tipo de bloque no soportado: {kind}")
        pattern = re.compile(rf'(\b{re.escape(kind)}\s+")({re.escape(old_name)})(")', re.UNICODE)
        return pattern.sub(rf"\1{new_name}\3", source)

    def _parse(self, source: str) -> list[dict[str, Any]]:
        tokens, lexical_errors = KunsamuLexer().tokenize(source)
        if lexical_errors:
            raise ValueError(lexical_errors[0]["message"])
        parsed, syntax_errors, _parse_tree = KunsamuParser(tokens).parse()
        if syntax_errors:
            raise ValueError(syntax_errors[0]["message"])
        return parsed

    def _walk_blocks(self, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for block in blocks:
            result.append(block)
            result.extend(self._walk_blocks(block.get("children", [])))
        return result

    def _dedupe_children(self, blocks: list[dict[str, Any]]) -> None:
        seen: dict[tuple[str, str], int] = {}
        for block in blocks:
            key = (block.get("kind", ""), str(block.get("name", "")).lower())
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > 1:
                block["name"] = f'{block.get("name", "")} {seen[key]}'
            self._dedupe_children(block.get("children", []))

    def _render_block(self, block: dict[str, Any], indent: int) -> str:
        pad = " " * indent
        lines = [f'{pad}{block["kind"]} "{block.get("name", "")}" {{']
        for key, value in block.get("attributes", {}).items():
            lines.append(f"{pad}    {key}: {self._render_value(value)}")
        if block.get("attributes") and block.get("children"):
            lines.append("")
        for index, child in enumerate(block.get("children", [])):
            lines.append(self._render_block(child, indent + 4))
            if index < len(block.get("children", [])) - 1:
                lines.append("")
        lines.append(f"{pad}}}")
        return "\n".join(lines)

    def _render_value(self, value: Any) -> str:
        if isinstance(value, str):
            if value.lower() == value and re.fullmatch(r"[a-zA-Z_áéíóúÁÉÍÓÚñÑ-]+", value):
                return value
            return f'"{value}"'
        if isinstance(value, dict):
            amount = value.get("amount")
            unit = value.get("unit")
            amount_text = int(amount) if isinstance(amount, float) and amount.is_integer() else amount
            return f"{amount_text} {unit}".strip()
        if isinstance(value, list):
            return "[" + ", ".join(self._render_value(item) for item in value) + "]"
        return str(value)
