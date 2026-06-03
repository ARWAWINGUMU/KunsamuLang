from __future__ import annotations

from dataclasses import dataclass
from typing import Any


KEYWORDS = {
    "COMUNIDAD",
    "TERRITORIO",
    "ELEMENTO",
    "MENSAJE",
    "PROYECTO",
    "CURSO",
    "DURACION",
    "ENFOQUE",
    "PARTICIPANTE",
    "ACTIVIDAD",
}


@dataclass
class Token:
    type: str
    text: str
    line: int
    column: int

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "text": self.text, "line": self.line, "column": self.column}


class KunsamuLexer:
    SYMBOLS = {"{": "LBRACE", "}": "RBRACE", "[": "LBRACK", "]": "RBRACK", ":": "COLON", ",": "COMMA"}

    def tokenize(self, source: str) -> tuple[list[Token], list[dict[str, Any]]]:
        tokens: list[Token] = []
        errors: list[dict[str, Any]] = []
        i = 0
        line = 1
        column = 0

        while i < len(source):
            ch = source[i]
            if ch in " \t\r":
                i += 1
                column += 1
                continue
            if ch == "\n":
                i += 1
                line += 1
                column = 0
                continue
            if source.startswith("//", i):
                while i < len(source) and source[i] != "\n":
                    i += 1
                    column += 1
                continue
            if source.startswith("/*", i):
                start_line, start_col = line, column
                i += 2
                column += 2
                closed = False
                while i < len(source):
                    if source.startswith("*/", i):
                        i += 2
                        column += 2
                        closed = True
                        break
                    if source[i] == "\n":
                        i += 1
                        line += 1
                        column = 0
                    else:
                        i += 1
                        column += 1
                if not closed:
                    errors.append({"level": "error", "message": "Comentario de bloque sin cerrar.", "line": start_line, "column": start_col})
                continue
            if ch in self.SYMBOLS:
                tokens.append(Token(self.SYMBOLS[ch], ch, line, column))
                i += 1
                column += 1
                continue
            if ch == '"':
                start_line, start_col = line, column
                i += 1
                column += 1
                value = []
                closed = False
                while i < len(source):
                    current = source[i]
                    if current == "\\" and i + 1 < len(source):
                        value.append(source[i + 1])
                        i += 2
                        column += 2
                        continue
                    if current == '"':
                        i += 1
                        column += 1
                        closed = True
                        break
                    if current == "\n":
                        errors.append({"level": "error", "message": "String sin cerrar antes del salto de línea.", "line": start_line, "column": start_col})
                        break
                    value.append(current)
                    i += 1
                    column += 1
                if closed:
                    tokens.append(Token("STRING", "".join(value), start_line, start_col))
                elif i >= len(source):
                    errors.append({"level": "error", "message": "String sin cerrar.", "line": start_line, "column": start_col})
                continue
            if ch.isdigit():
                start_col = column
                number = []
                while i < len(source) and (source[i].isdigit() or source[i] == "."):
                    number.append(source[i])
                    i += 1
                    column += 1
                tokens.append(Token("NUMBER", "".join(number), line, start_col))
                continue
            if ch.isalpha() or ch == "_" or ch in "áéíóúÁÉÍÓÚñÑ":
                start_col = column
                ident = []
                while i < len(source) and (source[i].isalnum() or source[i] in "_-áéíóúÁÉÍÓÚñÑ"):
                    ident.append(source[i])
                    i += 1
                    column += 1
                text = "".join(ident)
                tokens.append(Token(text.upper() if text.upper() in KEYWORDS else "ID", text, line, start_col))
                continue
            errors.append({"level": "error", "message": f"Carácter no reconocido: {ch}", "line": line, "column": column})
            i += 1
            column += 1

        tokens.append(Token("EOF", "<EOF>", line, column))
        return tokens, errors


class KunsamuParser:
    BLOCKS = {"COMUNIDAD", "TERRITORIO", "ELEMENTO", "PROYECTO", "CURSO", "PARTICIPANTE", "ACTIVIDAD"}
    ATTRIBUTE_KEYWORDS = {"MENSAJE", "DURACION", "ENFOQUE"}
    VALUE_KEYWORDS = BLOCKS | ATTRIBUTE_KEYWORDS

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.errors: list[dict[str, Any]] = []

    def parse(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        while not self._check("EOF"):
            if self._check("COMUNIDAD"):
                blocks.append(self._block("COMUNIDAD", {"TERRITORIO", "PROYECTO", "PARTICIPANTE", "ACTIVIDAD"}))
            else:
                self._error(self._peek(), "Se esperaba un bloque COMUNIDAD al nivel superior.")
                self._advance()
        parse_tree = {"rule": "program", "children": [self._tree_from_block(block) for block in blocks]}
        return blocks, self.errors, parse_tree

    def _block(self, kind: str, allowed_children: set[str]) -> dict[str, Any]:
        keyword = self._consume(kind, f"Se esperaba {kind}.")
        name = self._consume("STRING", f"El bloque {kind} requiere un nombre entre comillas.")
        block = {"kind": kind, "name": name.text if name else None, "line": keyword.line, "column": keyword.column, "attributes": {}, "children": []}
        self._consume("LBRACE", f"El bloque {kind} requiere '{{'.")
        while not self._check("RBRACE") and not self._check("EOF"):
            token = self._peek()
            if token.type in allowed_children:
                child_allowed = self._allowed_for(token.type)
                block["children"].append(self._block(token.type, child_allowed))
            elif token.type in self.ATTRIBUTE_KEYWORDS or token.type == "ID":
                key, value = self._attribute()
                if key:
                    block["attributes"][key] = value
            else:
                self._error(token, f"Elemento inesperado dentro de {kind}: {token.text}.")
                self._advance()
        self._consume("RBRACE", f"El bloque {kind} requiere '}}'.")
        return block

    def _allowed_for(self, kind: str) -> set[str]:
        return {
            "COMUNIDAD": {"TERRITORIO", "PROYECTO", "PARTICIPANTE", "ACTIVIDAD"},
            "TERRITORIO": {"ELEMENTO"},
            "ELEMENTO": set(),
            "PROYECTO": {"CURSO", "PARTICIPANTE", "ACTIVIDAD"},
            "CURSO": {"PARTICIPANTE", "ACTIVIDAD"},
            "PARTICIPANTE": set(),
            "ACTIVIDAD": set(),
        }[kind]

    def _attribute(self) -> tuple[str | None, Any]:
        key = self._advance()
        self._consume("COLON", f"El atributo {key.text} requiere ':'.")
        if key.type == "DURACION":
            number = self._consume("NUMBER", "DURACION requiere una cantidad numérica.")
            unit = self._consume("ID", "DURACION requiere unidad de tiempo.")
            amount = None
            if number:
                try:
                    amount = float(number.text)
                except ValueError:
                    self._error(number, f"Número inválido: {number.text}.")
            return key.type, {"amount": amount, "unit": unit.text.lower() if unit else None}
        value = self._value()
        return key.type if key.type != "ID" else key.text.upper(), value

    def _value(self) -> Any:
        if self._match("STRING"):
            return self._previous().text
        if self._match("NUMBER"):
            raw = self._previous().text
            value = float(raw) if "." in raw else int(raw)
            if self._match("ID"):
                return {"amount": value, "unit": self._previous().text.lower()}
            return value
        if self._match("ID"):
            return self._previous().text
        if self._check(*self.VALUE_KEYWORDS):
            return self._advance().text.lower()
        if self._match("LBRACK"):
            values = []
            if not self._check("RBRACK"):
                values.append(self._value())
                while self._match("COMMA"):
                    values.append(self._value())
            self._consume("RBRACK", "La lista requiere ']'.")
            return values
        self._error(self._peek(), "Se esperaba un valor.")
        self._advance()
        return None

    def _tree_from_block(self, block: dict[str, Any]) -> dict[str, Any]:
        attribute_nodes = [{"rule": "attribute", "label": key, "value": value} for key, value in block.get("attributes", {}).items()]
        return {
            "rule": block["kind"],
            "label": block.get("name"),
            "children": attribute_nodes + [self._tree_from_block(child) for child in block.get("children", [])],
        }

    def _match(self, *types: str) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    def _consume(self, token_type: str, message: str) -> Token | None:
        if self._check(token_type):
            return self._advance()
        self._error(self._peek(), message)
        return None

    def _check(self, *types: str) -> bool:
        return self._peek().type in types

    def _advance(self) -> Token:
        if not self._check("EOF"):
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, token: Token, message: str) -> None:
        self.errors.append({"level": "error", "message": message, "line": token.line, "column": token.column, "token": token.text})
