#!/usr/bin/env node
/**
 * more-chat-excalidraw MCP 服务器（D.6，借鉴 excalidraw/excalidraw-mcp，5069★）
 *
 * 通过 MCP 协议向 agent 暴露图表能力：
 *   - generate_diagram   : IR JSON → .excalidraw 文件（复用 ir_to_excalidraw.py）
 *   - validate_diagram   : 校验 .excalidraw 文件（结构 + 引用 + 视觉）
 *   - push_preview       : 推送 .excalidraw 到运行中的预览服务器
 *   - list_templates     : 列出可用模板与主题
 *
 * 运行方式（stdio，供 Codex/Claude 等 MCP 客户端连接）：
 *   node scripts/mcp_server.mjs
 *
 * 依赖：@modelcontextprotocol/sdk（位于 scripts/web/node_modules，ESM 入口）
 */

import path from "node:path";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { execFile } from "node:child_process";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const zodPath = require.resolve("zod", { paths: [path.join(__dirname, "web", "node_modules")] });
const { z } = await import(pathToFileURL(zodPath).href);
const SDK_ROOT = path.join(__dirname, "web", "node_modules", "@modelcontextprotocol", "sdk");

let McpServer, StdioServerTransport;
try {
  ({ McpServer } = await import(path.join(SDK_ROOT, "dist", "esm", "server", "mcp.js")));
  ({ StdioServerTransport } = await import(path.join(SDK_ROOT, "dist", "esm", "server", "stdio.js")));
} catch (err) {
  console.error(`[ERROR] MCP SDK not found: ${err.message}`);
  console.error("       Install it: cd scripts/web && npm install @modelcontextprotocol/sdk");
  process.exit(1);
}

function runPython(args) {
  return new Promise((resolve) => {
    execFile("python3", args, { encoding: "utf-8", timeout: 30000 }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout, stderr: err ? `${err.message}\n${stderr}` : stderr });
    });
  });
}

function runNode(args) {
  return new Promise((resolve) => {
    execFile("node", args, { encoding: "utf-8", timeout: 15000 }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout, stderr: err ? `${err.message}\n${stderr}` : stderr });
    });
  });
}

const server = new McpServer({
  name: "more-chat-excalidraw",
  version: "0.1.0",
});

const irScript = path.join(__dirname, "ir_to_excalidraw.py");
const validateScript = path.join(__dirname, "validate_excalidraw.py");
const pushScript = path.join(__dirname, "push_preview.js");
const selectorScript = path.join(__dirname, "template_selector.py");

server.registerTool(
  "generate_diagram",
  {
    title: "Generate Excalidraw diagram from IR",
    description:
      "Convert an IR (intermediate representation) JSON object into a .excalidraw file. " +
      "IR fields: version, title, template (flowchart/architecture/sequence/mindmap/swimlane/erd/" +
      "hierarchy/relationship/comparison/timeline), theme (default/sketch/blueprint/minimal), " +
      "nodes [{id,label,type}], edges [{id,from,to,label}], groups [{id,name,nodes,level}]. " +
      "Optionally layout: dot/neato/twopi for Graphviz auto-layout.",
    inputSchema: {
      ir: z.record(z.any()).describe("IR JSON object"),
      output: z.string().describe("Output .excalidraw path"),
      layout: z.enum(["dot", "neato", "twopi"]).optional().describe("Graphviz layout engine"),
    },
  },
  async ({ ir, output, layout }) => {
    const tmpIr = path.join(os.tmpdir(), `mcp-ir-${Date.now()}.json`);
    fs.writeFileSync(tmpIr, JSON.stringify(ir, null, 2));
    const args = [irScript, tmpIr, "--output", output, "--validate"];
    if (layout) args.push("--layout", layout);
    const r = await runPython(args);
    try { fs.unlinkSync(tmpIr); } catch (_) {}
    return {
      content: [{ type: "text", text: r.ok ? `Generated: ${output}\n${r.stdout}` : `Error: ${r.stderr}` }],
    };
  }
);

server.registerTool(
  "validate_diagram",
  {
    title: "Validate Excalidraw file",
    description:
      "Validate a .excalidraw file: structure, reference integrity, and visual quality (overlap/dangling arrows).",
    inputSchema: {
      file: z.string().describe("Path to .excalidraw file"),
      visual: z.boolean().optional().describe("Include visual quality checks (default true)"),
    },
  },
  async ({ file, visual }) => {
    const args = [validateScript, file];
    if (visual !== false) args.push("--visual");
    const r = await runPython(args);
    return {
      content: [{ type: "text", text: r.ok ? r.stdout : `Errors:\n${r.stdout}\n${r.stderr}` }],
    };
  }
);

server.registerTool(
  "push_preview",
  {
    title: "Push diagram to preview server",
    description:
      "Push a .excalidraw file to the running preview server (preview_server.js) for live updates.",
    inputSchema: {
      file: z.string().describe("Path to .excalidraw file"),
      url: z.string().optional().describe("Preview server base URL (default http://localhost:6060/)"),
    },
  },
  async ({ file, url }) => {
    const args = [pushScript, file];
    if (url) args.push("--url", url);
    const r = await runNode(args);
    return {
      content: [{ type: "text", text: r.ok ? r.stdout : `Error: ${r.stderr}` }],
    };
  }
);

server.registerTool(
  "list_templates",
  {
    title: "List templates and themes",
    description: "List all available diagram templates and themes.",
    inputSchema: {},
  },
  async () => {
    const r = await runPython([selectorScript, "--list", "--json"]);
    return { content: [{ type: "text", text: r.ok ? r.stdout : `Error: ${r.stderr}` }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("[OK] more-chat-excalidraw MCP server running (stdio)");
