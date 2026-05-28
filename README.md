# KunsamuLang

**Lenguaje de Dominio Específico para la Representación y Transformación de Saberes Ancestrales Arhuacos**

KunsamuLang es una plataforma académica de procesamiento de lenguajes construida con Python, ANTLR4 y Flask. Permite escribir código en un DSL propio, analizar tokens, validar sintaxis y semántica, construir AST, exportar a JSON/XML y visualizar la estructura del conocimiento como grafo interactivo.

## Arquitectura

```text
KunsamuLang/
├── grammar/KunsamuLang.g4       # Gramática ANTLR4
├── generated/                   # Lexer, Parser y Visitor generados
├── ast/nodes.py                 # Nodos del AST simplificado
├── visitors/ast_builder.py      # Visitor-style AST builder
├── semantic/analyzer.py         # Reglas semánticas
├── exporters/                   # JSON, XML y grafo
├── web/templates/index.html     # Demo Flask
├── web/static/css/styles.css
├── web/static/js/app.js
├── examples/                    # Programas válidos e inválidos
├── tests/                       # Pruebas automatizadas
├── docs/INFORME_ACADEMICO.md
├── parser_engine.py             # Lexer/parser operativo para la demo
├── pipeline.py                  # Orquestación del análisis
└── app.py
```

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Para generar los artefactos ANTLR4:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/generate_antlr.ps1
```

## Ejecución

```bash
python app.py
```

Abre `http://127.0.0.1:5000`.

## Demo web

La interfaz incluye:

- editor oscuro con numeración de líneas,
- tabla de tokens con línea y columna,
- panel de errores léxicos, sintácticos y semánticos,
- AST expandible,
- parse tree,
- JSON formateado,
- XML formateado,
- grafo interactivo con D3.js,
- métricas de comunidades, territorios, proyectos, cursos, elementos y profundidad.

## Ejemplo DSL

```kunsamu
COMUNIDAD "Seynimin" {
    TERRITORIO "Sierra Nevada" {
        ELEMENTO "Agua" {
            MENSAJE: "El agua representa la vida"
        }
    }

    PROYECTO "Escuela de Saberes" {
        CURSO "Saberes de Origen" {
            DURACION: 5 meses
            ENFOQUE: intercultural
        }
    }
}
```

## Reglas semánticas

- Una `COMUNIDAD` debe declarar al menos un `TERRITORIO`.
- Un `PROYECTO` debe contener al menos un `CURSO`.
- Un `ELEMENTO` debe tener `MENSAJE`.
- Un `CURSO` debe tener `DURACION` y `ENFOQUE`.
- La duración debe ser positiva y usar unidades válidas.
- No debe haber nombres duplicados dentro del mismo bloque padre.

## AST y Visitor Pattern

El AST simplifica la salida del parser en nodos uniformes con `kind`, `name`, `attributes`, `children` y `location`. El módulo `visitors/ast_builder.py` aplica un enfoque Visitor para transformar la estructura parseada en nodos semánticamente útiles.

## Screenshots simulados

```text
[Editor KunsamuLang]        [Métricas]
COMUNIDAD "Seynimin" {      Comunidades: 1 | Cursos: 2 | Profundidad: 5
  TERRITORIO ...            Tokens | Errores | AST | JSON | XML | Grafo
}
```

```text
PROGRAMA
└── COMUNIDAD: Seynimin
    ├── TERRITORIO: Sierra Nevada
    │   ├── ELEMENTO: Agua
    │   └── ELEMENTO: Montaña
    └── PROYECTO: Escuela de Saberes
        ├── CURSO: Saberes de Origen
        └── CURSO: Lecturaleza
```

## Pruebas

```bash
pytest
```

## Entregables académicos

El informe con introducción, justificación, motivación, objetivos, marco teórico, arquitectura, implementación, pruebas, resultados, conclusiones, trabajos futuros y referencias IEEE está en `docs/INFORME_ACADEMICO.md`.

La guía de sustentación por diapositivas está en `docs/PRESENTACION_ACADEMICA.md`.
