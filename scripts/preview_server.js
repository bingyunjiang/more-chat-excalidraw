#!/usr/bin/env node
/**
 * Real-time preview server for .excalidraw diagrams.
 *
 * Pattern borrowed from al1y/mcp-excalidraw: an in-memory diagram plus a
 * polling API. The preview page polls the server and swaps in the latest
 * SVG, so edits pushed via push_preview.js appear live without reloads and
 * without writing into the Excalidraw app's web root.
 *
 * Endpoints:
 *   GET  /                       -> preview page (auto-refreshes by polling)
 *   GET  /editor                  -> full Excalidraw editor (in-browser editing)
 *   GET  /editor-bundle.js        -> bundled Excalidraw editor (esbuild output)
 *   GET  /api/current-diagram    -> {elements, appState, timestamp}
 *   POST /api/current-diagram    -> accept {elements, appState} or raw .excalidraw JSON
 *   GET  /api/diagram.svg        -> server-rendered SVG of the current diagram
 *   GET  /api/preview            -> {svg, stats, updated} (one fetch per poll tick)
 *   GET  /api/status             -> {stats, updated, clients}
 *   POST /api/save               -> persist editor scene (write-through to scene file)
 *   GET  /api/canvases           -> list canvases (multi-canvas management)
 *   POST /api/canvases           -> create/switch canvas {name, elements, appState}
 *   GET  /api/canvases/:name     -> fetch a named canvas
 *
 * Usage:
 *   node scripts/preview_server.js [file.excalidraw] [--port 6060] [--open]
 *
 * Note: binding a port needs privileges outside the Codex sandbox; run with
 * escalated permissions (or under launchd) when used from an agent session.
 */

"use strict";

const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");
const { execFile } = require("child_process");
const { renderSvgFromScene } = require("./lib/svg_render");

const DEFAULT_PORT = 6060;
const POLL_INTERVAL_MS = 1500;
const CJK_FONT_UPSTREAM = {
  "/cjk-font/LongCang.woff2": "/fonts/LongCang/LongCang-Regular.woff2",
  "/cjk-font/MaShanZheng.woff2": "/fonts/MaShanZheng/MaShanZheng-Regular.woff2",
  "/cjk-font/LiuJianMaoCao.woff2": "/fonts/LiuJianMaoCao/LiuJianMaoCao-Regular.woff2",
};

function proxyCjkFont(pathname, res) {
  const upstreamPath = CJK_FONT_UPSTREAM[pathname];
  if (!upstreamPath) return false;
  const upstream = http.get(`http://localhost:5001${upstreamPath}`, (fontRes) => {
    if (fontRes.statusCode !== 200) {
      res.writeHead(404);
      res.end("font unavailable");
      fontRes.resume();
      return;
    }
    res.writeHead(200, { "Content-Type": "font/woff2", "Cache-Control": "public, max-age=3600" });
    fontRes.pipe(res);
  });
  upstream.on("error", () => {
    if (!res.headersSent) res.writeHead(404);
    res.end("local Excalidraw font service unavailable");
  });
  return true;
}

// In-memory store of the latest diagram (same pattern as mcp-excalidraw).
let current = { elements: [], appState: {}, timestamp: 0 };

// Multi-canvas store: name -> { elements, appState, timestamp }.
const canvases = {};

// Optional write-through target: set via positional arg; /api/save writes here.
let sceneFile = null;

function registerCanvas(name, scene) {
  const existing = canvases[name] || { timestamp: 0 };
  canvases[name] = {
    elements: scene.elements || [],
    appState: scene.appState || {},
    timestamp: Date.now(),
    created: existing.created || Date.now(),
  };
  return canvases[name];
}

function switchCurrent(name) {
  const c = canvases[name];
  if (c) {
    current = { elements: c.elements, appState: c.appState, timestamp: c.timestamp };
    return true;
  }
  return false;
}

function persistCurrent() {
  if (!sceneFile) return false;
  try {
    fs.writeFileSync(
      sceneFile,
      JSON.stringify(
        {
          type: "excalidraw",
          version: 2,
          source: "https://excalidraw.com",
          elements: current.elements,
          appState: current.appState,
        },
        null,
        2
      )
    );
    console.log(`[OK] persisted to ${sceneFile} (${current.elements.length} elements)`);
    return true;
  } catch (err) {
    console.error(`[ERROR] failed to persist ${sceneFile}: ${err.message}`);
    return false;
  }
}

function normalizeDiagram(data) {
  if (!data || typeof data !== "object") return null;
  // Accept either {elements, appState} or a raw .excalidraw JSON document.
  let elements = Array.isArray(data.elements) ? data.elements : null;
  if (elements === null && Array.isArray(data.scene?.elements)) {
    elements = data.scene.elements;
  }
  if (elements === null) return null;
  const appState =
    (data.appState && typeof data.appState === "object" ? data.appState : null) ||
    (data.scene?.appState && typeof data.scene.appState === "object" ? data.scene.appState : null) ||
    {};
  return { elements, appState };
}

function updateDiagram(data) {
  const normalized = normalizeDiagram(data);
  if (!normalized) return null;
  current = { ...normalized, timestamp: Date.now() };
  return current;
}

function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 64 * 1024 * 1024) {
        req.destroy();
        reject(new Error("Body too large"));
      }
    });
    req.on("end", () => {
      if (!body) return resolve(null);
      try {
        resolve(JSON.parse(body));
      } catch (err) {
        reject(new Error(`Invalid JSON: ${err.message}`));
      }
    });
    req.on("error", reject);
  });
}

function json(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-cache",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  });
  res.end(body);
}

function svgResponse(res, svg) {
  res.writeHead(200, {
    "Content-Type": "image/svg+xml; charset=utf-8",
    "Cache-Control": "no-cache",
  });
  res.end(svg);
}

/**
 * Collect unique animate.order values present in the scene (sorted ascending),
 * plus the list of element ids per order for frame-by-frame playback.
 */
function collectAnimationFrames(scene) {
  const orders = new Map();
  for (const el of scene.elements || []) {
    const order = el.customData?.animate?.order;
    if (order === undefined) continue;
    if (!orders.has(order)) orders.set(order, []);
    orders.get(order).push(el.id);
  }
  const sorted = [...orders.keys()].sort((a, b) => a - b);
  return sorted.map((order) => ({
    order,
    elementIds: orders.get(order),
  }));
}

const EDITOR_PAGE = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excalidraw 编辑器</title>
<link rel="stylesheet" href="/excalidraw-css">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  #editor-mount { height: 100vh; }
</style>
</head>
<body>
<div id="editor-mount"></div>
<script src="/editor-bundle.js"></script>
<script>
  (async function () {
    const mount = document.getElementById("editor-mount");
    let scene = { elements: [], appState: {} };
    try {
      const resp = await fetch("/api/current-diagram", { cache: "no-store" });
      if (resp.ok) scene = await resp.json();
    } catch (e) { /* start empty */ }

    // Excalidraw's Virgil font has no Chinese glyphs.  When a generated scene
    // declares a CJK handwriting stack, register its first installed local font
    // as Virgil's CJK-only face so the editable canvas matches exported previews.
    const cjkPrimary = scene.appState && scene.appState.cjkFontFamily;
    const cjkFallbacks = (scene.appState && scene.appState.cjkFontFallbacks) || [];
    if (cjkPrimary) {
      const names = [...new Set([cjkPrimary, ...cjkFallbacks])]
        .map((name) => String(name).replace(/["\\]/g, ""));
      const assets = {"Long Cang":"LongCang.woff2","Ma Shan Zheng":"MaShanZheng.woff2","Liu Jian Mao Cao":"LiuJianMaoCao.woff2"};
      const face = document.createElement("style");
      face.dataset.cjkHandwriting = "true";
      face.textContent = '@font-face{font-family:"Virgil";src:' +
        names.flatMap((name) => [assets[name] ? 'url("/cjk-font/' + assets[name] + '") format("woff2")' : null, 'local("' + name + '")']).filter(Boolean).join(",") +
        ';unicode-range:U+2E80-2FFF,U+3000-303F,U+31C0-31EF,U+3400-4DBF,U+4E00-9FFF,U+F900-FAFF,U+FF00-FFEF;}';
      document.head.appendChild(face);
      await document.fonts.load('16px "Virgil"', "中文手绘");
    }

    window.ExcalidrawEditor.mount(mount, scene, async (next) => {
      // Throttle auto-save: persist to server on each change is expensive;
      // the "保存到服务器" button does the write-through. We still update the
      // server's in-memory copy so /api/current-diagram stays fresh.
      try {
        await fetch("/api/current-diagram", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(next),
        });
      } catch (e) { /* ignore */ }
    });
  })();
</script>
</body>
</html>`;

const ANIMATE_PAGE = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excalidraw 动画预览</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }
  #header { padding: 12px 20px; background: #fff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  #header h1 { font-size: 15px; font-weight: 600; }
  button { padding: 6px 14px; font-size: 13px; border-radius: 6px; border: 1px solid #ced4da; background: #fff; cursor: pointer; }
  button:hover { background: #f1f3f5; }
  #frame-info { font-size: 13px; color: #868e96; }
  #canvas { padding: 24px; overflow: auto; display: flex; justify-content: center; }
  #canvas svg { display: block; box-shadow: 0 1px 3px rgba(0,0,0,0.12); background: #fff; max-width: 100%; height: auto; transition: opacity 0.25s; }
  #empty { padding: 60px; text-align: center; color: #adb5bd; font-size: 14px; }
  #progress { height: 4px; background: #e0e0e0; border-radius: 2px; width: 100%; margin-top: 8px; }
  #progress > div { height: 100%; background: #4dabf7; border-radius: 2px; transition: width 0.3s; }
</style>
</head>
<body>
<div id="header">
  <h1>Excalidraw 动画预览</h1>
  <button id="play">▶ 播放</button>
  <button id="prev">◀ 上一帧</button>
  <button id="next">下一帧 ▶</button>
  <span id="frame-info">加载中...</span>
</div>
<div id="progress"><div id="progress-bar" style="width:0%"></div></div>
<div id="canvas"><div id="empty">正在加载动画序列...</div></div>
<script>
  const canvas = document.getElementById("canvas");
  const infoEl = document.getElementById("frame-info");
  const bar = document.getElementById("progress-bar");
  let frames = [];
  let idx = 0;
  let timer = null;

  function render() {
    if (!frames.length) return;
    const frame = frames[idx];
    canvas.innerHTML = frame.svg;
    infoEl.textContent = "第 " + (idx + 1) + " / " + frames.length + " 帧（order " + frame.order + "，元素 " + frame.elementIds.length + " 个）";
    bar.style.width = (((idx + 1) / frames.length) * 100) + "%";
  }

  function play() {
    stop();
    if (!frames.length) return;
    idx = 0;
    render();
    timer = setInterval(() => {
      idx++;
      if (idx >= frames.length) { stop(); return; }
      render();
    }, 1200);
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  document.getElementById("play").onclick = () => (timer ? stop() : play());
  document.getElementById("prev").onclick = () => { stop(); if (frames.length) { idx = Math.max(0, idx - 1); render(); } };
  document.getElementById("next").onclick = () => { stop(); if (frames.length) { idx = Math.min(frames.length - 1, idx + 1); render(); } };

  (async () => {
    try {
      const resp = await fetch("/api/animate?t=" + Date.now(), { cache: "no-store" });
      const data = await resp.json();
      frames = data.frames || [];
      if (frames.length === 0) {
        canvas.innerHTML = '<div id="empty">该画布没有动画元数据（customData.animate）。用 ir_to_excalidraw.py 生成后自动注入。</div>';
        infoEl.textContent = "无动画帧";
        return;
      }
      render();
    } catch (err) {
      canvas.innerHTML = '<div id="empty">加载失败: ' + err.message + "</div>";
    }
  })();
</script>
</body>
</html>`;

const PREVIEW_PAGE = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excalidraw 实时预览</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }
  #header { padding: 12px 20px; background: #fff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  #header h1 { font-size: 15px; font-weight: 600; }
  #status { font-size: 13px; color: #868e96; }
  #updated { font-size: 12px; color: #adb5bd; margin-left: auto; }
  #canvas { padding: 24px; overflow: auto; display: flex; justify-content: center; }
  #canvas svg { display: block; box-shadow: 0 1px 3px rgba(0,0,0,0.12); background: #fff; max-width: 100%; height: auto; }
  #empty { padding: 60px; text-align: center; color: #adb5bd; font-size: 14px; }
</style>
</head>
<body>
<div id="header">
  <h1>Excalidraw 实时预览</h1>
  <span id="status">等待数据...</span>
  <span id="updated"></span>
</div>
<div id="canvas"><div id="empty">推送 .excalidraw 文件后，这里会实时刷新。</div></div>
<script>
  const canvas = document.getElementById("canvas");
  const statusEl = document.getElementById("status");
  const updatedEl = document.getElementById("updated");
  let lastSvg = "";

  async function tick() {
    try {
      const resp = await fetch("/api/preview?t=" + Date.now(), { cache: "no-store" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      const data = await resp.json();
      const stats = data.stats || {};
      const total = stats.total || 0;
      const byType = stats.by_type || {};
      const detail = Object.entries(byType)
        .map(([k, v]) => k + ": " + v)
        .join(" | ");
      statusEl.textContent = total ? total + " 元素 (" + detail + ")" : "画布为空";
      updatedEl.textContent = data.updated
        ? "更新于 " + new Date(data.updated).toLocaleTimeString()
        : "";
      if (data.svg && data.svg !== lastSvg) {
        lastSvg = data.svg;
        canvas.innerHTML = data.svg;
      } else if (!data.svg && canvas.querySelector("#empty") === null) {
        canvas.innerHTML = '<div id="empty">画布为空</div>';
        lastSvg = "";
      }
    } catch (err) {
      statusEl.textContent = "连接预览服务器失败: " + err.message;
    }
  }

  tick();
  setInterval(tick, ${POLL_INTERVAL_MS});
</script>
</body>
</html>`;

function createServer() {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://127.0.0.1");
    const pathname = url.pathname;

    if (req.method === "GET" && proxyCjkFont(pathname, res)) return;

    if (req.method === "OPTIONS") {
      res.writeHead(200, { "Access-Control-Allow-Origin": "*" });
      res.end();
      return;
    }

    if (pathname === "/" && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(PREVIEW_PAGE);
      return;
    }

    if (pathname === "/editor" && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(EDITOR_PAGE);
      return;
    }

    if (pathname === "/animate" && req.method === "GET") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(ANIMATE_PAGE);
      return;
    }

    if (pathname === "/editor-bundle.js" && req.method === "GET") {
      const bundlePath = path.join(__dirname, "web", "editor-bundle.js");
      try {
        const body = fs.readFileSync(bundlePath);
        res.writeHead(200, { "Content-Type": "application/javascript; charset=utf-8" });
        res.end(body);
      } catch (err) {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("editor-bundle.js not found. Build it with: cd scripts/web && npm run build");
      }
      return;
    }

    if (pathname === "/excalidraw-css" && req.method === "GET") {
      const cssPath = path.join(
        __dirname,
        "web",
        "node_modules",
        "@excalidraw",
        "excalidraw",
        "dist",
        "prod",
        "index.css"
      );
      try {
        const body = fs.readFileSync(cssPath);
        res.writeHead(200, { "Content-Type": "text/css; charset=utf-8" });
        res.end(body);
      } catch (err) {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("excalidraw index.css not found");
      }
      return;
    }

    if (pathname === "/api/current-diagram" && req.method === "GET") {
      json(res, 200, current);
      return;
    }

    if (pathname === "/api/current-diagram" && req.method === "POST") {
      try {
        const body = await readJsonBody(req);
        const updated = updateDiagram(body);
        if (!updated) {
          json(res, 400, { error: 'Body must contain "elements" array (or raw .excalidraw JSON)' });
          return;
        }
        console.log(
          `[OK] diagram updated: ${updated.elements.length} elements (${new Date(updated.timestamp).toISOString()})`
        );
        json(res, 200, { success: true, timestamp: updated.timestamp });
      } catch (err) {
        json(res, 400, { error: err.message });
      }
      return;
    }

    if (pathname === "/api/save" && req.method === "POST") {
      try {
        const body = await readJsonBody(req);
        const normalized = normalizeDiagram(body);
        if (!normalized) {
          json(res, 400, { error: 'Body must contain "elements" array' });
          return;
        }
        current = { ...normalized, timestamp: Date.now() };
        const persisted = persistCurrent();
        json(res, 200, { success: true, persisted, timestamp: current.timestamp });
      } catch (err) {
        json(res, 400, { error: err.message });
      }
      return;
    }

    if (pathname === "/api/canvases" && req.method === "GET") {
      json(res, 200, {
        canvases: Object.entries(canvases).map(([name, c]) => ({
          name,
          elements: c.elements.length,
          updated: c.timestamp,
          created: c.created,
        })),
        current: Object.keys(canvases).find(
          (n) =>
            canvases[n].timestamp === current.timestamp &&
            canvases[n].elements === current.elements
        ) || null,
      });
      return;
    }

    if (pathname === "/api/canvases" && req.method === "POST") {
      try {
        const body = await readJsonBody(req);
        const name = body && body.name;
        if (!name || typeof name !== "string") {
          json(res, 400, { error: 'Body must contain "name" string' });
          return;
        }
        const scene = normalizeDiagram(body) || { elements: [], appState: {} };
        const registered = registerCanvas(name, scene);
        switchCurrent(name);
        json(res, 200, {
          success: true,
          canvas: { name, elements: registered.elements.length, updated: registered.timestamp },
        });
      } catch (err) {
        json(res, 400, { error: err.message });
      }
      return;
    }

    if (pathname.startsWith("/api/canvases/") && req.method === "GET") {
      const name = decodeURIComponent(pathname.slice("/api/canvases/".length));
      const c = canvases[name];
      if (!c) {
        json(res, 404, { error: `Canvas not found: ${name}` });
        return;
      }
      json(res, 200, { name, elements: c.elements, appState: c.appState, timestamp: c.timestamp });
      return;
    }

    if (pathname === "/api/diagram.svg" && req.method === "GET") {
      const { svg } = renderSvgFromScene(current, { padding: 40 });
      svgResponse(res, svg);
      return;
    }

    if (pathname === "/api/preview" && req.method === "GET") {
      const { svg, stats } = renderSvgFromScene(current, { padding: 40 });
      json(res, 200, { svg, stats, updated: current.timestamp });
      return;
    }

    if (pathname === "/api/animate" && req.method === "GET") {
      // Animation sequence playback (excalimate-style): frame-by-frame SVG.
      const frames = collectAnimationFrames(current);
      const sequence = frames.map((frame) => {
        const { svg } = renderSvgFromScene(current, { padding: 40, maxOrder: frame.order });
        return { ...frame, svg };
      });
      json(res, 200, {
        total: frames.length,
        frames: sequence,
        updated: current.timestamp,
      });
      return;
    }

    if (pathname === "/api/status" && req.method === "GET") {
      json(res, 200, {
        stats: renderSvgFromScene(current, { padding: 40 }).stats,
        updated: current.timestamp,
        clients: 0,
      });
      return;
    }

    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Not Found");
  });
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const positional = [];
  const opts = { port: DEFAULT_PORT, open: false };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--port" || a === "-p") opts.port = Number(args[++i]);
    else if (a.startsWith("--port=")) opts.port = Number(a.split("=")[1]);
    else if (a === "--open" || a === "-o") opts.open = true;
    else if (a === "--help" || a === "-h") opts.help = true;
    else positional.push(a);
  }
  return { positional, opts };
}

function main() {
  const { positional, opts } = parseArgs(process.argv);
  if (opts.help) {
    console.log(`Usage: node scripts/preview_server.js [file.excalidraw] [--port 6060] [--open]

Real-time preview server for .excalidraw diagrams (polling API pattern).

Endpoints:
  GET  /                       preview page
  GET  /api/current-diagram    current diagram JSON
  POST /api/current-diagram    push {elements, appState} or raw .excalidraw JSON
  GET  /api/diagram.svg        server-rendered SVG
  GET  /api/preview            {svg, stats, updated}

Push updates with: node scripts/push_preview.js <file.excalidraw>
`);
    process.exit(0);
  }

  sceneFile = positional[0];
  if (sceneFile && !fs.existsSync(sceneFile)) {
    console.error(`[ERROR] Scene not found: ${sceneFile}`);
    process.exit(1);
  }

  const server = createServer();
  server.on("error", (err) => {
    if (err.code === "EADDRINUSE") {
      console.error(`[ERROR] Port ${opts.port} already in use. Use --port to pick another.`);
    } else {
      console.error(`[ERROR] ${err.message}`);
    }
    process.exit(1);
  });

  server.listen(opts.port, "127.0.0.1", () => {
    const address = server.address();
    const port = typeof address === "object" && address ? address.port : opts.port;
    const url = `http://localhost:${port}/`;
    console.log(`[OK] Preview server running at ${url}`);
    console.log(`PREVIEW_URL=${url}`);

    if (sceneFile) {
      try {
        const data = JSON.parse(fs.readFileSync(sceneFile, "utf-8"));
        const updated = updateDiagram(data);
        if (updated) {
          console.log(`[OK] Loaded ${sceneFile}: ${updated.elements.length} elements`);
        } else {
          console.error(`[WARN] ${sceneFile} does not look like an .excalidraw document`);
        }
      } catch (err) {
        console.error(`[ERROR] Failed to load ${sceneFile}: ${err.message}`);
      }
    }

    if (opts.open) {
      execFile("open", [url], (err) => {
        if (err) console.error(`[WARN] Failed to open browser: ${err.message}`);
      });
    }
  });

  process.on("SIGINT", () => {
    server.close(() => process.exit(0));
  });
}

main();
