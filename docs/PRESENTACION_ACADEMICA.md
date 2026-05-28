# Presentación académica: KunsamuLang

## Diapositiva 1. Título

**KunsamuLang**  
Lenguaje de Dominio Específico para la Representación y Transformación de Saberes Ancestrales Arhuacos.

## Diapositiva 2. Problema

Los saberes culturales pueden representarse de manera textual, pero suelen carecer de validación formal, estructura transformable y visualización automatizada.

## Diapositiva 3. Propuesta

Crear un DSL con sintaxis propia para modelar comunidades, territorios, elementos naturales, proyectos, cursos, participantes y actividades.

## Diapositiva 4. Stack

Python 3, ANTLR4, Visitor Pattern, Flask, HTML5, CSS3, JavaScript, Bootstrap, D3.js, JSON y XML.

## Diapositiva 5. Sintaxis del DSL

Mostrar `examples/valid_full.kunsamu` y explicar bloques, atributos, listas, strings, números y jerarquías.

## Diapositiva 6. Gramática ANTLR4

Explicar `grammar/KunsamuLang.g4`: reglas `program`, `comunidad`, `territorio`, `elemento`, `proyecto`, `curso`, `attribute` y `value`.

## Diapositiva 7. Pipeline

Código fuente → tokens → parse tree → AST → análisis semántico → JSON/XML → grafo.

## Diapositiva 8. AST

Mostrar el árbol:

```text
COMUNIDAD
├── TERRITORIO
│   ├── ELEMENTO
│   └── ELEMENTO
└── PROYECTO
    ├── CURSO
    └── CURSO
```

## Diapositiva 9. Análisis semántico

Validaciones implementadas:

- nombres duplicados,
- bloques obligatorios,
- atributos obligatorios,
- duración válida,
- enfoques recomendados,
- estructuras inconsistentes.

## Diapositiva 10. Exportación

Mostrar JSON y XML generados automáticamente desde el AST.

## Diapositiva 11. Demo web

Flujo de exposición:

1. Cargar ejemplo válido.
2. Presionar **Analizar**.
3. Mostrar tokens, AST, JSON, XML, métricas y grafo.
4. Cargar ejemplo inválido.
5. Explicar errores semánticos.

## Diapositiva 12. Resultados

KunsamuLang funciona como herramienta académica de análisis de lenguajes y como plataforma visual para representar conocimiento estructurado.

## Diapositiva 13. Conclusiones

El proyecto demuestra dominio de gramáticas, parsing, AST, visitors, análisis semántico, serialización y visualización en una arquitectura modular.

## Diapositiva 14. Trabajos futuros

Autocompletado, resaltado avanzado, persistencia, validaciones culturales enriquecidas e integración directa con artefactos ANTLR generados.
