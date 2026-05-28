const editor = document.querySelector("#sourceEditor");
const lineNumbers = document.querySelector("#lineNumbers");
const highlightLayer = document.querySelector("#highlightLayer");
const analyzeBtn = document.querySelector("#analyzeBtn");
const metricGrid = document.querySelector("#metricGrid");
const invalidExample = `COMUNIDAD "Seynimin" {
  TERRITORIO "Sierra Nevada" {
    ELEMENTO "Agua" {
      MENSAJE: "El agua representa la vida"
    }
    ELEMENTO "Agua" {
    }
  }

  PROYECTO "Escuela de Saberes" {
    CURSO "Saberes de Origen" {
      DURACION: 0 siglos
    }
  }
}`;

function updateLineNumbers() {
  const lines = editor.value.split("\n").length;
  lineNumbers.textContent = Array.from({ length: lines }, (_, index) => index + 1).join("\n");
  document.querySelector("#sourceStats").textContent = `${lines} líneas`;
  highlightLayer.innerHTML = highlight(editor.value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function highlight(source) {
  return escapeHtml(source)
    .replace(/(\/\/.*)$/gm, '<span class="comment">$1</span>')
    .replace(/(&quot;.*?&quot;)/g, '<span class="str">$1</span>')
    .replace(/\b(COMUNIDAD|TERRITORIO|ELEMENTO|MENSAJE|PROYECTO|CURSO|DURACION|ENFOQUE|PARTICIPANTE|ACTIVIDAD)\b/g, '<span class="kw">$1</span>')
    .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="num">$1</span>')
    .replace(/([{}\[\]:,])/g, '<span class="sym">$1</span>');
}

async function analyze() {
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analizando...";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: editor.value }),
    });
    const result = await response.json();
    render(result);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analizar";
  }
}

function render(result) {
  renderMetrics(result.metrics);
  renderTokens(result.tokens);
  renderDiagnostics(result.diagnostics, result.success);
  renderAst(result.ast, document.querySelector("#astTree"));
  renderParseTree(result.parseTree, document.querySelector("#parseTree"));
  document.querySelector("#jsonOutput").textContent = result.json;
  document.querySelector("#xmlOutput").textContent = result.xml;
  renderGraph(result.graph);
}

function renderMetrics(metrics) {
  const labels = {
    comunidades: "Comunidades",
    territorios: "Territorios",
    proyectos: "Proyectos",
    cursos: "Cursos",
    elementos: "Elementos",
    participantes: "Participantes",
    actividades: "Actividades",
    profundidad: "Profundidad",
  };
  metricGrid.innerHTML = Object.entries(labels)
    .map(([key, label]) => `<div class="metric"><strong>${metrics[key] ?? 0}</strong><span>${label}</span></div>`)
    .join("");
}

function renderTokens(tokens) {
  const rows = tokens.map((token) => `
    <tr>
      <td><code>${escapeHtml(token.text)}</code></td>
      <td>${escapeHtml(token.type)}</td>
      <td>${token.line}</td>
      <td>${token.column}</td>
    </tr>`).join("");
  document.querySelector("#tokensTable").innerHTML = `
    <thead><tr><th>Token</th><th>Tipo</th><th>Línea</th><th>Columna</th></tr></thead>
    <tbody>${rows}</tbody>`;
}

function renderDiagnostics(items, success) {
  const list = document.querySelector("#diagnosticsList");
  if (items.length === 0) {
    list.innerHTML = `<div class="diagnostic success"><strong>Análisis exitoso</strong><p>No se encontraron errores léxicos, sintácticos ni semánticos.</p></div>`;
    return;
  }
  list.innerHTML = items.map((item) => `
    <article class="diagnostic ${escapeHtml(item.level)}">
      <strong>[${escapeHtml(item.stage ?? "semántico").toUpperCase()}] ${escapeHtml(item.level).toUpperCase()}</strong>
      <p>${escapeHtml(item.message)}</p>
      <small>Línea ${item.line ?? "-"}, columna ${item.column ?? "-"}</small>
    </article>`).join("");
}

function renderAst(node, container) {
  container.innerHTML = astNode(node);
}

function astNode(node) {
  const attrs = node.attributes && Object.keys(node.attributes).length
    ? `<div class="node-attrs">${escapeHtml(JSON.stringify(node.attributes, null, 2))}</div>`
    : "";
  const children = (node.children || []).map(astNode).join("");
  return `<details open><summary>${escapeHtml(node.kind)}${node.name ? ` · ${escapeHtml(node.name)}` : ""}</summary>${attrs}${children}</details>`;
}

function renderParseTree(node, container) {
  container.innerHTML = parseNode(node);
}

function parseNode(node) {
  const label = node.label ? ` · ${node.label}` : node.value !== undefined ? `: ${JSON.stringify(node.value)}` : "";
  const children = (node.children || []).map(parseNode).join("");
  return `<details open><summary>${escapeHtml(node.rule)}${escapeHtml(label)}</summary>${children}</details>`;
}

function renderGraph(graph) {
  const svg = document.querySelector("#graphCanvas");
  svg.innerHTML = "";
  const width = 960;
  const height = 560;
  if (!window.d3) {
    renderStaticGraph(svg, graph, width, height);
    return;
  }
  const color = d3.scaleOrdinal()
    .domain(["PROGRAMA", "COMUNIDAD", "TERRITORIO", "ELEMENTO", "PROYECTO", "CURSO"])
    .range(["#d5a94c", "#55c2a4", "#4ea1d3", "#90c85a", "#d7785a", "#c084fc"]);

  const simulation = d3.forceSimulation(graph.nodes.map((node) => ({ ...node })))
    .force("link", d3.forceLink(graph.links).id((d) => d.id).distance(92))
    .force("charge", d3.forceManyBody().strength(-420))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(42));

  const link = d3.select(svg).append("g")
    .selectAll("line")
    .data(graph.links)
    .join("line")
    .attr("class", "graph-link");

  const node = d3.select(svg).append("g")
    .selectAll("circle")
    .data(simulation.nodes())
    .join("circle")
    .attr("class", "graph-node")
    .attr("r", 19)
    .attr("fill", (d) => color(d.kind))
    .call(drag(simulation));

  const label = d3.select(svg).append("g")
    .selectAll("text")
    .data(simulation.nodes())
    .join("text")
    .attr("class", "graph-label")
    .attr("text-anchor", "middle")
    .text((d) => d.label.length > 22 ? `${d.label.slice(0, 21)}…` : d.label);

  simulation.on("tick", () => {
    link.attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y).attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y);
    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    label.attr("x", (d) => d.x).attr("y", (d) => d.y + 35);
  });
}

function drag(simulation) {
  return d3.drag()
    .on("start", (event) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    })
    .on("drag", (event) => {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    })
    .on("end", (event) => {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    });
}

function renderStaticGraph(svg, graph, width, height) {
  const gap = height / Math.max(graph.nodes.length + 1, 2);
  graph.nodes.forEach((node, index) => {
    const x = 100 + (index % 4) * 230;
    const y = gap * (index + 1);
    node.x = x;
    node.y = y;
  });
  graph.links.forEach((link) => {
    const source = graph.nodes.find((node) => node.id === link.source);
    const target = graph.nodes.find((node) => node.id === link.target);
    svg.insertAdjacentHTML("beforeend", `<line class="graph-link" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>`);
  });
  graph.nodes.forEach((node) => {
    svg.insertAdjacentHTML("beforeend", `<circle class="graph-node" cx="${node.x}" cy="${node.y}" r="18" fill="#d5a94c"></circle><text class="graph-label" x="${node.x}" y="${node.y + 34}" text-anchor="middle">${escapeHtml(node.label)}</text>`);
  });
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab, .tab-content").forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`#${tab.dataset.target}`).classList.add("active");
  });
});

editor.addEventListener("input", updateLineNumbers);
editor.addEventListener("scroll", () => {
  lineNumbers.scrollTop = editor.scrollTop;
  highlightLayer.scrollTop = editor.scrollTop;
  highlightLayer.scrollLeft = editor.scrollLeft;
});
document.querySelector("#loadValid").addEventListener("click", () => { editor.value = window.KUNSAMU_VALID_EXAMPLE; updateLineNumbers(); analyze(); });
document.querySelector("#loadInvalid").addEventListener("click", () => { editor.value = invalidExample; updateLineNumbers(); analyze(); });
analyzeBtn.addEventListener("click", analyze);

updateLineNumbers();
analyze();
