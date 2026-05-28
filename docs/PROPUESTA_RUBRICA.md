# Propuesta formal para la rúbrica

## Título

KunsamuLang: aplicación de análisis y manipulación automática de código fuente para un DSL de representación de saberes ancestrales Arhuacos.

## Integrantes

- Nombre del integrante 1
- Nombre del integrante 2
- Nombre del integrante 3

## Descripción general

KunsamuLang es una aplicación real de procesamiento de lenguajes que analiza y manipula automáticamente código fuente escrito en un lenguaje de dominio específico diseñado para representar comunidades, territorios, elementos naturales, proyectos educativos, cursos, participantes y actividades. El sistema usa una gramática ANTLR4, aplica el patrón Visitor para construir un AST simplificado, ejecuta validaciones semánticas, calcula métricas, transforma la información a JSON/XML, visualiza la estructura mediante un grafo y ofrece operaciones de manipulación automática del código fuente como formateo, auto-corrección semántica básica y renombrado de símbolos.

## Alineación con la asignatura

La aplicación procesa código fuente KunsamuLang como entrada textual formal. Sobre ese código ejecuta análisis léxico, parsing, construcción de árbol, análisis semántico y transformaciones automáticas. De esta manera, el proyecto se alinea con el objetivo de desarrollar una aplicación real basada en procesadores de lenguajes de programación.

## Gramática

La gramática principal está en `grammar/KunsamuLang.g4`. Los artefactos `Lexer`, `Parser` y `Visitor` se generan con `scripts/generate_antlr.ps1`.

## Manipulación automática implementada

- Formateo automático del código fuente.
- Auto-corrección de atributos semánticos faltantes o inválidos.
- Renombrado automático de símbolos por tipo de bloque.
- Transformación estructural a JSON.
- Transformación estructural a XML.

## Escenarios de prueba

- Programa válido con comunidad, territorio, elementos, proyecto, cursos, participantes y actividades.
- Programa inválido con nombre duplicado, elemento sin mensaje, curso sin enfoque y duración inválida.
- Aplicación de auto-corrección sobre el programa inválido.
- Renombrado de un curso y posterior reanálisis.
- Exportación JSON/XML y visualización gráfica.
