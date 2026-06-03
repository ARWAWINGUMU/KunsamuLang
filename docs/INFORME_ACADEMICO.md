# KunsamuLang: Informe académico

## 1. Introducción

KunsamuLang es un lenguaje de dominio específico orientado a representar comunidades, territorios, elementos naturales, proyectos educativos, cursos, participantes y actividades asociadas a saberes ancestrales Arhuacos. El proyecto integra análisis léxico, análisis sintáctico, construcción de AST, validación semántica, transformación a JSON/XML y visualización gráfica.

## 2. Justificación

La pertinencia de este trabajo radica en la necesidad de emplear mecanismos tecnológicos que permitan la preservación de la memoria colectiva de la comunidad arahuaca. Históricamente, el conocimiento ancestral Arhuaco, regido por la Ley de Origen, se ha transmitido de forma oral, lo que presenta retos de persistencia frente a la globalización y la digitalización externa.

Los DSL permiten modelar problemas con vocabularios cercanos al dominio. Para este caso, el lenguaje usa una sintaxis declarativa para expresar estructuras culturales y educativas de forma verificable, transformable y visualizable y pedagógico.


## 3. Motivación

La asignatura de Lenguajes de Programación requiere evidenciar conceptos de compiladores en un artefacto funcional. KunsamuLang convierte esos conceptos en una herramienta demostrable, con interfaz web y análisis reproducible.

## 4. Objetivos

- Diseñar un DSL con bloques jerárquicos y atributos.
- Construir gramática ANTLR4 con Lexer, Parser y Visitor.
- Implementar AST simplificado y análisis semántico.
- Exportar la estructura a JSON y XML.
- Manipular automáticamente el código fuente mediante formateo, auto-corrección y renombrado.
- Visualizar el conocimiento mediante un grafo interactivo.
- Presentar una demo web profesional.

## 5. Marco teórico

**DSL.** Un Domain Specific Language expresa soluciones dentro de un dominio particular con sintaxis y semántica especializadas.

**Parsing.** El parsing transforma una secuencia de tokens en una estructura gramatical que representa la forma del programa.

**ANTLR4.** ANTLR4 genera analizadores léxicos y sintácticos a partir de gramáticas formales, e incluye soporte para visitors y listeners.

**AST.** El Abstract Syntax Tree elimina detalles gramaticales innecesarios y conserva la estructura semánticamente útil.

**Visitors.** El patrón Visitor separa operaciones de recorrido de las estructuras visitadas, facilitando transformaciones y validaciones.

**Análisis semántico.** Revisa reglas que no son puramente sintácticas: duplicados, obligatoriedad de atributos, duración válida y coherencia jerárquica.

## 6. Arquitectura

El sistema se organiza por responsabilidades: `grammar/` contiene la especificación ANTLR4, `parser_engine.py` realiza análisis operativo para la demo, `visitors/` construye AST, `semantic/` valida reglas de dominio, `exporters/` produce JSON/XML/grafo y `web/` contiene la experiencia Flask.

## 7. Implementación

La sintaxis usa bloques como `COMUNIDAD`, `TERRITORIO`, `ELEMENTO`, `PROYECTO` y `CURSO`. Cada bloque puede contener atributos y subbloques permitidos. El pipeline ejecuta tokenización, parsing, construcción de AST, análisis semántico, manipulación automática de código fuente y exportación.

Las operaciones de manipulación implementadas son:

- formateo automático,
- auto-corrección semántica básica,
- renombrado de símbolos,
- transformación a JSON,
- transformación a XML.

## 8. Pruebas

Se incluyen pruebas con `pytest` para validar un escenario correcto, un escenario con errores semánticos y operaciones de manipulación automática sobre el código fuente.

## 9. Resultados

La herramienta produce tokens con línea/columna, parse tree, AST, diagnósticos, JSON, XML, métricas y un grafo interactivo útil para sustentación.

## 10. Conclusiones

KunsamuLang demuestra los componentes esenciales de procesamiento de lenguajes y los conecta con una interfaz de análisis visual, logrando un proyecto académico con separación clara de responsabilidades.

## 11. Trabajos futuros

- Integrar los artefactos generados por ANTLR4 directamente en producción.
- Añadir autocompletado y resaltado avanzado en el editor.
- Incorporar persistencia de documentos y comparación entre versiones.
- Ampliar el catálogo semántico con reglas culturales más ricas.

## 12. Referencias IEEE

[1] T. Parr, *The Definitive ANTLR 4 Reference*. Pragmatic Bookshelf, 2013.

[2] A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed. Pearson, 2006.

[3] M. Fowler, *Domain-Specific Languages*. Addison-Wesley, 2010.
