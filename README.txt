KunsamuLang
Lenguaje de Dominio Específico para la Representación, Análisis y Manipulación Automática de Código Fuente sobre Saberes Ancestrales Arhuacos

INSTALACIÓN
1. Crear entorno virtual:
   python -m venv .venv

2. Activar entorno:
   .venv\Scripts\activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Generar artefactos ANTLR4:
   powershell -ExecutionPolicy Bypass -File scripts\generate_antlr.ps1

EJECUCIÓN
python app.py

Abrir en el navegador:
http://127.0.0.1:5000

FUNCIONALIDADES
- Análisis léxico con tokens, tipos, línea y columna.
- Análisis sintáctico y parse tree.
- Construcción de AST.
- Visitor-style AST builder.
- Análisis semántico.
- Exportación JSON y XML.
- Visualización gráfica.
- Métricas del código fuente.
- Manipulación automática del código fuente KunsamuLang:
  formateo, auto-corrección semántica básica y renombrado de símbolos.

EJEMPLOS
- Entrada válida: examples\valid_full.kunsamu
- Entrada inválida: examples\invalid_semantic.kunsamu
- Salidas esperadas: examples\outputs\
