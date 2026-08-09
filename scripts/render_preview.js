#!/usr/bin/env node
/**
 * Render a .excalidraw file to PNG (+ SVG) using the local render bundle and
 * a headless Chromium. Produces a preview the agent can inspect before delivery.
 *
 * Usage:
 *   node render_preview.js <file.excalidraw> [outdir] [--format png|svg|pdf|both]
 *
 * Options:
 *   --format   Output format: png (default), svg, pdf, or both
 *   --no-server  Skip Playwright HTTP server, use fallback SVG render
 *
 * The render bundle is self-contained at scripts/render-bundle/
 * (index.html + render-entry.js + render-bundle.js). Override with
 * EXCALIDRAW_RENDER_BUNDLE if you have a custom bundle.
 *
 * Exit codes: 0 = OK, 1 = errors, 2 = usage error.
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const DEFAULT_BUNDLE = path.join(__dirname, "render-bundle");
const REQUIRED_BUNDLE_FILES = ["index.html", "render-entry.js", "render-bundle.js"];
const CJK_FONT_UPSTREAM = {
  "/__cjk-font/LongCang.woff2": "/fonts/LongCang/LongCang-Regular.woff2",
  "/__cjk-font/MaShanZheng.woff2": "/fonts/MaShanZheng/MaShanZheng-Regular.woff2",
  "/__cjk-font/LiuJianMaoCao.woff2": "/fonts/LiuJianMaoCao/LiuJianMaoCao-Regular.woff2",
};

function proxyCjkFont(urlPath, res) {
  const upstreamPath = CJK_FONT_UPSTREAM[urlPath];
  if (!upstreamPath) return false;
  const upstream = http.get(`http://localhost:5001${upstreamPath}`, (fontRes) => {
    if (fontRes.statusCode !== 200) {
      res.writeHead(404);
      res.end("font unavailable");
      fontRes.resume();
      return;
    }
    res.writeHead(200, {
      "Content-Type": "font/woff2",
      "Cache-Control": "public, max-age=3600",
    });
    fontRes.pipe(res);
  });
  upstream.on("error", () => {
    if (!res.headersSent) res.writeHead(404);
    res.end("local Excalidraw font service unavailable");
  });
  return true;
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const positional = [];
  const opts = { format: "png", noServer: false, checkBrowser: false };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--format" || a === "-f") { opts.format = args[++i]; continue; }
    if (a.startsWith("--format=")) { opts.format = a.split("=")[1]; continue; }
    if (a === "--no-server") { opts.noServer = true; continue; }
    if (a === "--check-browser") { opts.checkBrowser = true; continue; }
    if (a === "--help" || a === "-h") { opts.help = true; continue; }
    positional.push(a);
  }
  return { positional, opts };
}

function findPlaywright() {
  try {
    return require("playwright");
  } catch (_) {
    // Fallback: probe npm's global root (npm root -g) for a playwright install.
    try {
      const { execSync } = require("child_process");
      const npmRoot = execSync("npm root -g", { encoding: "utf-8" }).trim();
      const candidates = [
        path.join(npmRoot, "playwright"),
        path.join(npmRoot, "@playwright", "cli", "node_modules", "playwright"),
      ];
      for (const p of candidates) {
        try {
          return require(p);
        } catch (_) {
          /* try next candidate */
        }
      }
    } catch (_) {
      /* npm not available */
    }
    return null;
  }
}

function playwrightCacheRoot() {
  const configured = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (configured && configured !== "0") return configured;
  if (process.platform === "darwin") {
    return path.join(os.homedir(), "Library", "Caches", "ms-playwright");
  }
  if (process.platform === "win32") {
    return path.join(process.env.LOCALAPPDATA || os.homedir(), "ms-playwright");
  }
  return path.join(os.homedir(), ".cache", "ms-playwright");
}

function findExecutable(root, names) {
  if (!root || !fs.existsSync(root)) return null;
  const pending = [root];
  while (pending.length) {
    const current = pending.shift();
    let entries;
    try {
      entries = fs.readdirSync(current, { withFileTypes: true })
        .sort((a, b) => a.name.localeCompare(b.name));
    } catch (_) {
      continue;
    }
    for (const entry of entries) {
      const candidate = path.join(current, entry.name);
      if (entry.isDirectory()) pending.push(candidate);
      else if (names.has(entry.name)) return candidate;
    }
  }
  return null;
}

function findChromium(playwright = null) {
  const override = process.env.EXCALIDRAW_CHROMIUM_EXECUTABLE;
  if (override) return fs.existsSync(override) ? override : null;

  const cacheRoot = playwrightCacheRoot();
  let dirs = [];
  try {
    dirs = fs.readdirSync(cacheRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && /^chromium_headless_shell-\d+$/.test(entry.name))
      .map((entry) => ({
        name: entry.name,
        revision: Number(entry.name.match(/(\d+)$/)[1]),
      }));
  } catch (_) {
    return null;
  }

  // Match Playwright's expected revision when possible. Headless shell avoids
  // registering a GUI application with macOS, which can abort inside an agent
  // sandbox and display a "Google Chrome for Testing" crash dialog.
  let expectedRevision = null;
  try {
    const expectedPath = playwright?.chromium?.executablePath?.() || "";
    const match = expectedPath.match(/chromium(?:_headless_shell)?-(\d+)/);
    if (match) expectedRevision = Number(match[1]);
  } catch (_) {
    /* fall back to the newest complete headless shell */
  }
  dirs.sort((a, b) => {
    if (a.revision === expectedRevision) return -1;
    if (b.revision === expectedRevision) return 1;
    return b.revision - a.revision;
  });

  const names = new Set(["chrome-headless-shell", "headless_shell", "chrome-headless-shell.exe"]);
  for (const entry of dirs) {
    const dir = path.join(cacheRoot, entry.name);
    if (!fs.existsSync(path.join(dir, "INSTALLATION_COMPLETE"))) continue;
    const executable = findExecutable(dir, names);
    if (executable) return executable;
  }
  return null;
}

function createServer(dir) {
  const server = http.createServer((req, res) => {
    let urlPath;
    try {
      urlPath = decodeURIComponent(new URL(req.url, "http://127.0.0.1").pathname);
    } catch (_) {
      res.writeHead(400);
      res.end("bad url");
      return;
    }
    if (proxyCjkFont(urlPath, res)) return;
    const file = path.normalize(path.join(dir, urlPath));
    if (!file.startsWith(dir)) {
      res.writeHead(403);
      res.end("forbidden");
      return;
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end("not found");
        return;
      }
      const ext = path.extname(file);
      const mime =
        ext === ".html" ? "text/html; charset=utf-8"
          : ext === ".js" ? "text/javascript; charset=utf-8"
          : ext === ".json" ? "application/json; charset=utf-8"
          : "application/octet-stream";
      res.writeHead(200, { "Content-Type": mime });
      res.end(data);
    });
  });
  return server;
}

function startServer(server) {
  return new Promise((resolve, reject) => {
    server.on("error", (err) => {
      reject(err);
    });
    server.listen(0, "127.0.0.1", () => {
      resolve(server);
    });
  });
}

/**
 * Fallback SVG render: extract a simple SVG from the .excalidraw JSON
 * without needing the Excalidraw render bundle or HTTP server.
 * Uses Playwright to set SVG content and screenshot to PNG.
 */
async function renderFallbackSvg(sceneFile, outdir, opts) {
  // Fallback path must work without Playwright (pure SVG rendering).
  // Playwright is only needed for PNG/PDF branches below.
  const { renderSvgFromScene } = require("./lib/svg_render");
  const sceneData = JSON.parse(fs.readFileSync(sceneFile, "utf-8"));
  const { svg, stats } = renderSvgFromScene(sceneData);
  const viewBox = stats?.viewBox || {};
  const vw = Math.min(16384, Math.max(320, Math.ceil(viewBox.width || 1600)));
  const vh = Math.min(16384, Math.max(240, Math.ceil(viewBox.height || 1200)));

  fs.mkdirSync(outdir, { recursive: true });
  const base = path.basename(sceneFile, path.extname(sceneFile));

  let svgSaved = false;
  if (opts.format === "svg" || opts.format === "both") {
    const svgPath = path.join(outdir, `${base}.svg`);
    fs.writeFileSync(svgPath, svg);
    console.log(`[OK] ${svgPath} (fallback SVG)`);
    svgSaved = true;
  }

  if (opts.format === "png" || opts.format === "both") {
    const playwright = findPlaywright();
    if (!playwright) {
      console.error("[WARN] Playwright not found. PNG skipped; SVG is available.");
      if (opts.format === "both") return true; // SVG already saved
      if (!svgSaved) {
        const svgPath = path.join(outdir, `${base}.svg`);
        fs.writeFileSync(svgPath, svg);
        console.log(`[OK] ${svgPath} (fallback SVG, PNG unavailable)`);
      }
      return true;
    }
    const executablePath = findChromium(playwright);
    if (!executablePath) {
      console.error("[WARN] Safe Chromium headless shell not found. PNG skipped; SVG is available.");
      if (!svgSaved) {
        const svgPath2 = path.join(outdir, `${base}.svg`);
        fs.writeFileSync(svgPath2, svg);
        console.log(`[OK] ${svgPath2} (fallback SVG, safe headless browser unavailable)`);
      }
      return true;
    }
    let browser;
    try {
      browser = await playwright.chromium.launch({
        headless: true,
        executablePath: executablePath || undefined,
      });
    } catch (err) {
      if (err.message && (err.message.includes("EPERM") || err.message.includes("closed"))) {
        console.error("[WARN] Cannot launch Chromium in sandbox. PNG skipped; SVG is available.");
        if (opts.format === "both") return true; // SVG already saved
        // If only PNG was requested, still save SVG as a fallback
        if (!svgSaved) {
          const svgPath2 = path.join(outdir, `${base}.svg`);
          fs.writeFileSync(svgPath2, svg);
          console.log(`[OK] ${svgPath2} (fallback SVG, PNG unavailable in sandbox)`);
        }
        return true;
      }
      console.error(`[ERROR] Failed to launch Chromium for PNG: ${err.message}`);
      if (opts.format === "both") return true; // SVG already saved
      return false;
    }
    try {
      const page = await browser.newPage({ viewport: { width: vw, height: vh } });
      await page.setContent(
        `<style>html,body{margin:0;padding:0;background:#fff}svg{display:block}</style>${svg}`,
        { waitUntil: "load" },
      );
      const pngPath = path.join(outdir, `${base}.png`);
      const svgLocator = page.locator("svg").first();
      await svgLocator.screenshot({ path: pngPath });
      console.log(`[OK] ${pngPath} (fallback PNG from SVG)`);
    } catch (err) {
      console.error(`[ERROR] PNG screenshot failed: ${err.message}`);
      return false;
    } finally {
      await browser.close();
    }
  }

  if (opts.format === "pdf") {
    // PDF requires Playwright + Chromium; in sandbox fallback to SVG.
    if (fs.existsSync(path.join(outdir, `${base}.svg`)) || svgSaved) {
      console.error("[WARN] PDF requires Chromium; SVG already saved as fallback.");
    } else {
      const svgPath = path.join(outdir, `${base}.svg`);
      fs.writeFileSync(svgPath, svg);
      console.log(`[OK] ${svgPath} (fallback SVG, PDF unavailable in sandbox)`);
    }
  }

  return true;
}

async function renderWithPlaywright(sceneFile, outdir, opts) {
  const bundleDir = process.env.EXCALIDRAW_RENDER_BUNDLE || DEFAULT_BUNDLE;
  const missing = REQUIRED_BUNDLE_FILES.filter((f) => !fs.existsSync(path.join(bundleDir, f)));
  if (missing.length) {
    console.error(
      `[ERROR] Render bundle incomplete at ${bundleDir}, missing: ${missing.join(", ")}\n` +
        "Set EXCALIDRAW_RENDER_BUNDLE to a directory with index.html, render-entry.js, render-bundle.js"
    );
    return false;
  }

  const playwright = findPlaywright();
  if (!playwright) {
    console.error("[ERROR] Playwright not found.");
    return false;
  }

  const executablePath = findChromium(playwright);
  if (!executablePath) {
    console.error("[WARN] Safe Chromium headless shell not found. Falling back to SVG render.");
    return renderFallbackSvg(sceneFile, outdir, opts);
  }

  const workdir = fs.mkdtempSync(path.join(os.tmpdir(), "excalidraw-render-"));
  fs.copyFileSync(sceneFile, path.join(workdir, "scene.excalidraw"));
  for (const f of REQUIRED_BUNDLE_FILES) {
    fs.copyFileSync(path.join(bundleDir, f), path.join(workdir, f));
  }

  const server = createServer(workdir);
  let port;
  try {
    await startServer(server);
    port = server.address().port;
  } catch (err) {
    if (err.code === "EPERM" || err.code === "EACCES") {
      console.error("[WARN] Cannot start HTTP server (sandbox/permission restriction).");
      console.error("[INFO] Falling back to direct SVG render...");
      fs.rmSync(workdir, { recursive: true, force: true });
      return renderFallbackSvg(sceneFile, outdir, opts);
    }
    console.error(`[ERROR] Failed to start HTTP server: ${err.message}`);
    fs.rmSync(workdir, { recursive: true, force: true });
    return false;
  }

  let browser;
  try {
    browser = await playwright.chromium.launch({
      headless: true,
      executablePath: executablePath || undefined,
    });
  } catch (err) {
    console.error(`[ERROR] Failed to launch Chromium: ${err.message}`);
    server.close();
    fs.rmSync(workdir, { recursive: true, force: true });
    return false;
  }

  try {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
    const url = `http://127.0.0.1:${port}/index.html?scene=${encodeURIComponent("scene.excalidraw")}`;
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForFunction(
      () => {
        const t = (document.querySelector("#status") || {}).textContent || "";
        return t.includes("Render complete") || t.startsWith("Failed") || t.startsWith("Render failed");
      },
      { timeout: 30000 }
    );
    const status = await page.evaluate(() => (document.querySelector("#status") || {}).textContent);
    if (!status.includes("Render complete")) {
      console.error(`[ERROR] Render did not complete: ${status}`);
      return false;
    }

    fs.mkdirSync(outdir, { recursive: true });
    const base = path.basename(sceneFile, path.extname(sceneFile));

    const svgLocator = page.locator("#excalidraw-container svg").first();
    const svgBox = await svgLocator.boundingBox();
    if (!svgBox || svgBox.width <= 0 || svgBox.height <= 0) {
      throw new Error("Rendered SVG has no measurable bounds");
    }

    if (opts.format === "png" || opts.format === "both") {
      const png = path.join(outdir, `${base}.png`);
      await new Promise((resolve) => setTimeout(resolve, 300));
      // Capture the diagram itself, not the verification page chrome. This
      // removes the debug header/note and avoids viewport-sized whitespace.
      await svgLocator.screenshot({ path: png });
      console.log(`[OK] ${png}`);
    }

    if (opts.format === "svg" || opts.format === "both") {
      const svgPath = path.join(outdir, `${base}.svg`);
      const svg = await page.evaluate(
        () => document.querySelector("#excalidraw-container svg")?.outerHTML || ""
      );
      if (svg) {
        fs.writeFileSync(svgPath, svg);
        console.log(`[OK] ${svgPath}`);
      }
    }

    if (opts.format === "pdf" || opts.format === "both") {
      const pdfPath = path.join(outdir, `${base}.pdf`);
      const pdfWidth = Math.max(1, Math.ceil(svgBox.width));
      const pdfHeight = Math.max(1, Math.ceil(svgBox.height));
      await page.evaluate(({ width, height, title }) => {
        document.title = title;
        document.querySelector("#header")?.remove();
        document.querySelector(".note")?.remove();
        const container = document.querySelector("#excalidraw-container");
        if (container) {
          container.style.padding = "0";
          container.style.margin = "0";
          container.style.width = `${width}px`;
          container.style.height = `${height}px`;
          container.style.overflow = "hidden";
        }
        const svg = container?.querySelector("svg");
        if (svg) {
          svg.style.margin = "0";
          svg.style.boxShadow = "none";
        }
        document.documentElement.style.margin = "0";
        document.documentElement.style.padding = "0";
        document.body.style.margin = "0";
        document.body.style.padding = "0";
        document.body.style.width = `${width}px`;
        document.body.style.height = `${height}px`;
        document.body.style.background = "#ffffff";
      }, { width: pdfWidth, height: pdfHeight, title: base });
      await page.pdf({
        path: pdfPath,
        width: `${pdfWidth}px`,
        height: `${pdfHeight}px`,
        printBackground: true,
        margin: { top: "0", right: "0", bottom: "0", left: "0" },
      });
      console.log(`[OK] ${pdfPath}`);
    }

    const info = await page.evaluate(() => (document.querySelector("#info") || {}).textContent);
    console.log(`[INFO] ${info || ""}`.trim());
    return true;
  } catch (err) {
    console.error(`[ERROR] ${err.message}`);
    return false;
  } finally {
    await browser.close();
    server.close();
    fs.rmSync(workdir, { recursive: true, force: true });
  }
}

async function main() {
  const { positional, opts } = parseArgs(process.argv);

  if (opts.help) {
    console.log(`Usage: node render_preview.js <file.excalidraw> [outdir] [--format png|svg|pdf|both] [--no-server]

Render a .excalidraw file to PNG and/or SVG using the local render bundle.

Options:
  --format png|svg|pdf|both   Output format (default: png)
  --no-server             Skip HTTP server, use fallback SVG render
  --check-browser         Print the safe headless browser selected for rendering

Environment:
  EXCALIDRAW_RENDER_BUNDLE  Path to render bundle directory (default: scripts/render-bundle)
  EXCALIDRAW_CHROMIUM_EXECUTABLE  Explicit trusted headless Chromium executable
`);
    process.exit(0);
  }

  if (opts.checkBrowser) {
    const executablePath = findChromium(findPlaywright());
    if (!executablePath) {
      console.error("[ERROR] No safe Chromium headless shell found.");
      process.exit(3);
    }
    console.log(executablePath);
    process.exit(0);
  }

  const sceneFile = positional[0];
  const outdir = positional[1] || (sceneFile ? path.dirname(sceneFile) : ".");

  if (!sceneFile) {
    console.error("Usage: node render_preview.js <file.excalidraw> [outdir] [--format png|svg|both]");
    process.exit(2);
  }
  if (!fs.existsSync(sceneFile)) {
    console.error(`[ERROR] Scene not found: ${sceneFile}`);
    process.exit(1);
  }

  if (!["png", "svg", "pdf", "both"].includes(opts.format)) {
    console.error(`[ERROR] Invalid format: ${opts.format}. Use png, svg, pdf, or both.`);
    process.exit(2);
  }

  if (opts.noServer) {
    const ok = await renderFallbackSvg(sceneFile, outdir, opts);
    process.exit(ok ? 0 : 1);
  } else {
    const ok = await renderWithPlaywright(sceneFile, outdir, opts);
    process.exit(ok ? 0 : 1);
  }
}

main().catch((err) => {
  console.error(`[ERROR] ${err.stack || err.message}`);
  process.exit(1);
});
