"""Demostracion del interprete KunsamuLang -- ejecutar con: python demo_interpreter.py"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

from interpreter import KunsamuInterpreter
from parser_engine import KunsamuLexer, KunsamuParser
from visitors.ast_builder import ASTBuilder

SOURCE = Path("examples/valid_full.kunsamu").read_text(encoding="utf-8")

tokens, _ = KunsamuLexer().tokenize(SOURCE)
parsed, _, _ = KunsamuParser(tokens).parse()
ast_root = ASTBuilder().visit_program(parsed)
interp = KunsamuInterpreter(ast_root)

QUERIES = [
    "LISTAR COMUNIDAD",
    "LISTAR TERRITORIO",
    "BUSCAR CURSO",
    "BUSCAR CURSO DONDE ENFOQUE = ambiental",
    "BUSCAR ELEMENTO EN TERRITORIO \"Sierra Nevada\"",
    "CONTAR PARTICIPANTE EN PROYECTO \"Escuela de Saberes\"",
    "RUTA CURSO \"Saberes de Origen\"",
    "REPORTE",
]

SEP = "-" * 60

for query in QUERIES:
    print(f"\n{SEP}")
    print(f"  > {query}")
    print(SEP)
    result = interp.execute(query)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        continue

    if not result.get("path"):
        print(f"  {result['summary']}")

    if result.get("results"):
        for node in result["results"]:
            attrs = f"  attrs={node['attributes']}" if node["attributes"] else ""
            print(f"    [{node['kind']}] \"{node['name']}\" (línea {node['location']['line']}){attrs}")

    if result.get("names"):
        for name in result["names"]:
            print(f"    - {name}")

    if result.get("path"):
        labels = [f"{n['kind']}: \"{n['name']}\"" if n["name"] else n["kind"] for n in result["path"]]
        print(f"    {' → '.join(labels)}")

    if result.get("reporte"):
        print(f"  {'Comunidad':<20} {'Terr':>5} {'Proy':>5} {'Curs':>5} {'Part':>5} {'Act':>5} {'Elem':>5}")
        for row in result["reporte"]:
            print(f"  {row['comunidad']:<20} {row['territorios']:>5} {row['proyectos']:>5} "
                  f"{row['cursos']:>5} {row['participantes']:>5} {row['actividades']:>5} {row['elementos']:>5}")

print(f"\n{SEP}\n")
