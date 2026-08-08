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
 *   node scripts/mcp_server.js
 *
 * 依赖：@modelcontextprotocol/sdk（位于 scripts/web/node_modules）
 */

"use strict";

const path = require("path");
const fs = require("fs");
const os = require("os");
const { execFile } = require("child_process");

const SDK_DIR = path.join(__dirname, "web", "node_modules", "@modelcontextprotocol", "sdk");

function requireSdk() {
  // SDK ships ESM; load the CJS build directly for require() compatibility.
  for (const p of [
    path.join(SDK_DIR, "dist", "cjs", "index.js"),
    path.join(SDK_DIR, "dist", "esm", "index.js"),
    SDK_DIR,
  ]) {
    try {
      return require(p);
    } catch (err) {
      if (err.code !== "MODULE_NOT_FOUND" || !err.message.includes(p)) {
        throw err;
      }
    }
  }
  console.error(`[ERROR] MCP SDK not found in ${SDK_DIR}`);
  console.error("       Install it: cd scripts/web && npm install @modelcontextprotocol/sdk");
  process.exit(1);
}

function runPython(args) {
  return new Promise((resolve) => {
    execFile("python3", args, { encoding: "utf-8", timeout: 30000 }, (err, stdout, stderr) => {
      resolve({ ok: !err, stdout, stderr: err ? err.message + "\n" + stderr : stderr });
    });
  });
}

async function main() {
  const { McpServer } = requireSdk();
  const { StdioServerTransport } = requireSdk();

  const server = new McpServer({
    name: "more-chat-excalidraw",
    version: "0.5.0",
  });

  const irScript = path.join(__dirname, "ir_to_excalidraw.py");
  const validateScript = path.join(__dirname, "validate_excalidraw.py");
  const pushScript = path.join(__dirname, "push_preview.js");

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
        type: "object",
        properties: {
          ir: { type: "object", description: "IR JSON object" },
          output: { type: "string", description: "Output .excalidraw path" },
          layout: { type: "string", enum: ["dot", "neato", "twopi"], description: "Graphviz layout engine (optional)" },
        },
        required: ["ir", "output"],
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
        content: [{ type: "text", text: r.ok ? `Generated: ${output}` : `Error: ${r.stderr}` }],
      };
    }
  );

  server.registerTool(
    "validate_diagram",
    {
      title: "Validate Excalidraw file",
      description: "Validate a .excalidraw file: structure, reference integrity, and visual quality (overlap/dangling arrows).",
      inputSchema: {
        type: "object",
        properties: {
          file: { type: "string", description: "Path to .excalidraw file" },
          visual: { type: "boolean", description: "Include visual quality checks (default true)" },
        },
        required: ["file"],
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
      description: "Push a .excalidraw file to the running preview server (preview_server.js) for live updates.",
      inputSchema: {
        type: "object",
        properties: {
          file: { type: "string", description: "Path to .excalidraw file" },
          url: { type: "string", description: "Preview server base URL (default http://localhost:6060/)" },
        },
        required: ["file"],
      },
    },
    async ({ file, url }) => {
      const args = [pushScript, file];
      if (url) args.push("--url", url);
      // push_preview.js is a Node script (not python)
      return new Promise((resolve) => {
        execFile("node", args, { encoding: "utf-8", timeout: 15000 }, (err, stdout, stderr) => {
          resolve({
            content: [{ type: "text", text: err ? `Error: ${stderr || err.message}` : stdout }],
          });
        });
      });
    }
  );

  server.registerTool(
    "list_templates",
    {
      title: "List templates and themes",
      description: "List all available diagram templates and themes.",
      inputSchema: { type: "object", properties: {} },
    },
    async () => {
      const r = await runPython([
        path.join(__dirname, "template_selector.py"), "--list", "--json",
      ]);
      return { content: [{ type: "text", text: r.ok ? r.stdout : `Error: ${r.stderr}` }] };
    }
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[OK] more-chat-excalidraw MCP server running (stdio)");
}

main().catch((err) => {
  console.error(`[ERROR] ${err.message}`);
  process.exit(1);
});
