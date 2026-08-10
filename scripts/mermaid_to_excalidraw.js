#!/usr/bin/env node
/**
 * Mermaid → Excalidraw 转换（C.6，轻量子集解析器）
 *
 * 支持 flowchart（TD/LR/RL/BT）与 sequenceDiagram 子集，先解析为 IR 中间格式，
 * 再调用 ir_to_excalidraw.py 完成布局/配色/绑定。完全本地、无浏览器依赖。
 *
 * 用法：
 *   node scripts/mermaid_to_excalidraw.js <input.mmd> [--output out.excalidraw]
 *   node scripts/mermaid_to_excalidraw.js --string "graph TD; A-->B" [--output out.excalidraw]
 *
 * 支持的 Mermaid 语法（子集）：
 *   flowchart: graph/flowchart TD|LR|RL|BT; A[文本] A(圆角) A{菱形} A((圆形);
 *              A-->B A---B A-- 标签 ---B A-.->B
 *   sequence:  sequenceDiagram; participant A; A->>B: 消息
 */

"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

// ─── Mermaid 子集解析器 ───────────────────────────────────────────────────

function stripComments(src) {
  return src
    .split("\n")
    .filter((line) => !/^\s*%%/.test(line))
    .join("\n");
}

function parseFlowchart(src) {
  const ir = {
    version: 1,
    template: "flowchart",
    theme: "default",
    nodes: [],
    edges: [],
    groups: [],
    metadata: { source: "mermaid", sourceFormat: "flowchart" },
  };

  // Split on newlines AND semicolons (mermaid allows one-liners: graph TD; A-->B; B-->C)
  const statements = stripComments(src)
    .split("\n")
    .flatMap((l) => l.split(";"))
    .map((l) => l.trim())
    .filter((l) => l);
  const lines = statements.filter((l) => !/^(graph|flowchart)\s/.test(l));

  // Node registry: id -> {id, label, type, raw}
  const nodes = new Map();
  const nodeShapeOf = (raw) => {
    if (raw.startsWith("{{")) return "start";
    if (raw.endsWith("}}")) return "end";
    if (raw.startsWith("{")) return "decision";
    if (raw.startsWith("(")) return "process";
    if (raw.startsWith("((")) return "start";
    return "process";
  };
  const cleanLabel = (raw) => {
    return raw
      .replace(/^\{+|\}+$/g, "")
      .replace(/^\(+\)+$/g, "")
      .replace(/^\(+|\+\)$/g, "")
      .replace(/^\(+|\)+$/g, "")
      .replace(/^\(\(|\)\)$/g, "")
      .trim();
  };
  const ensureNode = (token) => {
    if (nodes.has(token)) return token;
    // Split "A[标签]" into id A and label 标签
    const m = token.match(/^([A-Za-z0-9_\u4e00-\u9fff]+)(.*)$/s);
    const id = m ? m[1] : token;
    const rest = m ? m[2] : "";
    const type = rest ? nodeShapeOf(rest) : "process";
    let label = cleanLabel(rest);
    if (!label) label = id;
    nodes.set(id, { id, label, type });
    return id;
  };

  for (const line of lines) {
    // Edge: A --> B, A-- label ---B, A-.->B, A ==> B
    const edgeMatch = line.match(
      /^([^\s-]+)\s*(--[^]*?--\s*|==>\s*|-\.->\s*|-->\s*|---\s*|--\s*)/ 
    );
    if (edgeMatch) {
      // handle label: A-- text ---B
      const m = line.match(
        /^([^\s-]+)\s*(?:--\s*(.*?)\s*---?|==>\s*|-->|-\.->|---?)\s*([^\s;]+)/
      );
      if (m) {
        const from = ensureNode(m[1]);
        const to = ensureNode(m[3]);
        const label = (m[2] || "").trim() || null;
        if (from !== to) {
          ir.edges.push({ id: `e${ir.edges.length + 1}`, from, to, label });
        }
        continue;
      }
      // fallback simple edge without label
      const m2 = line.match(/^([^\s-]+)\s*(?:-->|---|-\.->|==>)\s*([^\s;]+)/);
      if (m2) {
        const from = ensureNode(m2[1]);
        const to = ensureNode(m2[2]);
        if (from !== to) {
          ir.edges.push({ id: `e${ir.edges.length + 1}`, from, to, label: null });
        }
        continue;
      }
    }
    // Node-only line: A[标签]; A{决策}
    const nodeMatch = line.match(/^([A-Za-z0-9_\u4e00-\u9fff]+)((?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?)\s*;?$/);
    if (nodeMatch) {
      ensureNode(nodeMatch[1] + nodeMatch[2]);
      continue;
    }
    // Subgraph: subgraph name / end — treat subgraph name as a group
    const sub = line.match(/^subgraph\s+([^\s;]+)(.*)$/);
    if (sub) {
      const name = (sub[2] || sub[1]).trim();
      ir.groups.push({ id: `g${ir.groups.length + 1}`, name, nodes: [], level: 0 });
      continue;
    }
  }

  // Emit nodes in registry order
  for (const [, n] of nodes) {
    ir.nodes.push(n);
  }

  // Subgraph membership: not tracked precisely in this subset; assign level 0.
  return ir;
}

function parseSequence(src) {
  const ir = {
    version: 1,
    template: "sequence",
    theme: "default",
    nodes: [],
    edges: [],
    groups: [],
    metadata: { source: "mermaid", sourceFormat: "sequenceDiagram" },
  };

  const statements = stripComments(src)
    .split("\n")
    .flatMap((l) => l.split(";"))
    .map((l) => l.trim())
    .filter((l) => l);
  const lines = statements.filter(
    (l) => !l.startsWith("sequenceDiagram") && !/^\s*$/.test(l)
  );

  const actors = new Map();
  const ensureActor = (name) => {
    if (!actors.has(name)) {
      const id = `a${actors.size + 1}`;
      actors.set(name, id);
      ir.nodes.push({ id, label: name, type: "actor" });
    }
    return actors.get(name);
  };

  let order = 1;
  for (const line of lines) {
    const participant = line.match(/^participant\s+([^\s:]+)(?:\s+as\s+(.+))?$/);
    if (participant) {
      ensureActor(participant[1]);
      const actor = ir.nodes.find((node) => node.id === actors.get(participant[1]));
      if (actor && participant[2]) actor.label = participant[2].trim();
      continue;
    }
    // A->>B: message  (also ->, -->, ->>, -->>, -x, -))
    const msg = line.match(
      /^(.+?)\s*(-->>|->>|-->|->|-{1,2}[x)])\s*([^\s:]+)\s*:\s*(.+)$/
    );
    if (msg) {
      const from = ensureActor(msg[1]);
      const to = ensureActor(msg[3]);
      const label = msg[4].trim();
      ir.edges.push({ id: `e${order}`, from, to, label, style: "solid" });
      order++;
      continue;
    }
    // Note over A, B: text — skip in subset (render as free text later)
  }

  return ir;
}

function parseMermaid(src) {
  const trimmed = src.trim();
  if (/^(sequenceDiagram|sequence diagram)/i.test(trimmed)) {
    return parseSequence(trimmed);
  }
  if (/^(graph|flowchart)\s+(TD|TB|LR|RL|BT)/i.test(trimmed)) {
    return parseFlowchart(trimmed);
  }
  // Default: try flowchart, fall back to sequence
  return /^(sequenceDiagram)/i.test(trimmed) ? parseSequence(trimmed) : parseFlowchart(trimmed);
}

// ─── IR → Excalidraw（复用 ir_to_excalidraw.py）───────────────────────────

function irToExcalidraw(ir, outPath) {
  const script = path.join(__dirname, "ir_to_excalidraw.py");
  const tmpIr = path.join(require("os").tmpdir(), `mermaid-ir-${Date.now()}.json`);
  fs.writeFileSync(tmpIr, JSON.stringify(ir, null, 2));
  try {
    execFileSync("python3", [script, tmpIr, "--output", outPath, "--validate"], {
      encoding: "utf-8",
    });
  } finally {
    try { fs.unlinkSync(tmpIr); } catch (_) {}
  }
}

// ─── CLI ──────────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  const positional = [];
  const opts = { output: null };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--output" || a === "-o") opts.output = args[++i];
    else if (a.startsWith("--output=")) opts.output = a.split("=")[1];
    else if (a === "--string" || a === "-s") opts.string = args[++i];
    else if (a === "--help" || a === "-h") opts.help = true;
    else positional.push(a);
  }
  return { positional, opts };
}

function main() {
  const { positional, opts } = parseArgs(process.argv);

  if (opts.help) {
    console.log(`Usage: node scripts/mermaid_to_excalidraw.js <input.mmd> [--output out.excalidraw]
       node scripts/mermaid_to_excalidraw.js --string "graph TD; A-->B"

Convert Mermaid source to .excalidraw v2 JSON (flowchart + sequenceDiagram subset).

Options:
  --string, -s <mermaid>  Convert inline Mermaid source
  --output, -o <path>     Output .excalidraw file (default: <input>.excalidraw)
`);
    process.exit(0);
  }

  let src = null;
  let inputLabel = null;
  if (opts.string) {
    src = opts.string;
    inputLabel = "(inline)";
  } else if (positional[0]) {
    const input = positional[0];
    if (!fs.existsSync(input)) {
      console.error(`[ERROR] Mermaid file not found: ${input}`);
      process.exit(1);
    }
    src = fs.readFileSync(input, "utf-8");
    inputLabel = input;
  } else {
    console.error("Usage: node scripts/mermaid_to_excalidraw.js <input.mmd> [--output out.excalidraw]");
    process.exit(2);
  }

  try {
    const ir = parseMermaid(src);
    if (ir.nodes.length === 0) {
      console.error("[WARN] No nodes parsed. Mermaid syntax may be unsupported.");
    }
    const outPath =
      opts.output ||
      (positional[0]
        ? positional[0].replace(/\.(mmd|mermaid|md|txt)$/i, "") + ".excalidraw"
        : `output/mermaid-${Date.now()}.excalidraw`);
    irToExcalidraw(ir, outPath);
    console.log(`[OK] Converted ${inputLabel} → ${outPath} (${ir.nodes.length} nodes, ${ir.edges.length} edges)`);
  } catch (err) {
    console.error(`[ERROR] Conversion failed: ${err.message}`);
    process.exit(1);
  }
}

main();
