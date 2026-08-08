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

function parseArgs(argv) {
  const args = argv.slice(2);
  const positional = [];
  const opts = { format: "png", noServer: false };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--format" || a === "-f") { opts.format = args[++i]; continue; }
    if (a.startsWith("--format=")) { opts.format = a.split("=")[1]; continue; }
    if (a === "--no-server") { opts.noServer = true; continue; }
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

function findChromium() {
  const cacheRoot = path.join(os.homedir(), "Library", "Caches", "ms-playwright");
  const candidates = [
    path.join(cacheRoot, "chromium-1228", "chrome-mac-arm64", "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing"),
    path.join(cacheRoot, "chromium-1208", "chrome-mac-arm64", "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing"),
    path.join(cacheRoot, "chromium_headless_shell-1228", "chrome-headless-shell-mac-arm64", "headless_shell"),
    path.join(cacheRoot, "chromium_headless_shell-1208", "chrome-headless-shell-mac-arm64", "headless_shell"),
  ];
  return candidates.find((p) => fs.existsSync(p)) || null;
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
  const playwright = findPlaywright();
  if (!playwright) {
    console.error("[ERROR] Playwright not found. Cannot render preview.");
    return false;
  }

  const { renderSvgFromScene } = require("./lib/svg_render");
  const sceneData = JSON.parse(fs.readFileSync(sceneFile, "utf-8"));
  const { svg } = renderSvgFromScene(sceneData);

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
    const executablePath = findChromium();
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
      await page.setContent(svg, { waitUntil: "load" });
      const pngPath = path.join(outdir, `${base}.png`);
      await page.screenshot({ path: pngPath, fullPage: true });
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

  const executablePath = findChromium();
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

    if (opts.format === "png" || opts.format === "both") {
      const png = path.join(outdir, `${base}.png`);
      await new Promise((resolve) => setTimeout(resolve, 300));
      await page.screenshot({ path: png, fullPage: true });
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
      await page.pdf({ path: pdfPath, format: "A4", printBackground: true });
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
  --format png|svg|both   Output format (default: png)
  --no-server             Skip HTTP server, use fallback SVG render

Environment:
  EXCALIDRAW_RENDER_BUNDLE  Path to render bundle directory (default: scripts/render-bundle)
`);
    process.exit(0);
  }

  const sceneFile = positional[0];
  const outdir = positional[1] || path.dirname(sceneFile);

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
