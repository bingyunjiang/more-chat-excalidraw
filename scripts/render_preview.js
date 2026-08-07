#!/usr/bin/env node
/**
 * Render a .excalidraw file to PNG (+ SVG) using the local render bundle and
 * a headless Chromium. Produces a preview the agent can inspect before delivery.
 *
 * Usage:
 *   node render_preview.js <file.excalidraw> [outdir]
 *
 * The render bundle is located at $EXCALIDRAW_RENDER_BUNDLE or defaults to
 * /Users/Bing/WorkSpace/render-test (index.html + render-entry.js + render-bundle.js).
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");

const DEFAULT_BUNDLE = path.join(os.homedir(), "WorkSpace", "render-test");
const REQUIRED_BUNDLE_FILES = ["index.html", "render-entry.js", "render-bundle.js"];

function findPlaywright() {
  try {
    return require("playwright");
  } catch (_) {
    const globalPath =
      "/Users/Bing/.npm-global/lib/node_modules/@playwright/cli/node_modules/playwright";
    try {
      return require(globalPath);
    } catch (err) {
      throw new Error(
        `Playwright module not found. Install it or run from a machine with @playwright/cli. (${err.message})`
      );
    }
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

function serveDir(dir) {
  return http
    .createServer((req, res) => {
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
          ext === ".html"
            ? "text/html; charset=utf-8"
            : ext === ".js"
              ? "text/javascript; charset=utf-8"
              : ext === ".json"
                ? "application/json; charset=utf-8"
                : "application/octet-stream";
        res.writeHead(200, { "Content-Type": mime });
        res.end(data);
      });
    })
    .listen(0, "127.0.0.1");
}

async function main() {
  const sceneFile = process.argv[2];
  const outdir = process.argv[3] || path.dirname(sceneFile);
  if (!sceneFile) {
    console.error("Usage: node render_preview.js <file.excalidraw> [outdir]");
    process.exit(2);
  }
  if (!fs.existsSync(sceneFile)) {
    console.error(`[ERROR] Scene not found: ${sceneFile}`);
    process.exit(1);
  }

  const bundleDir = process.env.EXCALIDRAW_RENDER_BUNDLE || DEFAULT_BUNDLE;
  const missing = REQUIRED_BUNDLE_FILES.filter((f) => !fs.existsSync(path.join(bundleDir, f)));
  if (missing.length) {
    console.error(
      `[ERROR] Render bundle incomplete at ${bundleDir}, missing: ${missing.join(", ")}\n` +
        "Set EXCALIDRAW_RENDER_BUNDLE to a directory with index.html, render-entry.js, render-bundle.js"
    );
    process.exit(1);
  }

  const workdir = fs.mkdtempSync(path.join(os.tmpdir(), "excalidraw-render-"));
  fs.copyFileSync(sceneFile, path.join(workdir, "scene.excalidraw"));
  for (const f of REQUIRED_BUNDLE_FILES) {
    fs.copyFileSync(path.join(bundleDir, f), path.join(workdir, f));
  }

  const server = serveDir(workdir);
  await new Promise((resolve) => server.once("listening", resolve));
  const port = server.address().port;

  const playwright = findPlaywright();
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
    process.exit(1);
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
      process.exitCode = 1;
    } else {
      fs.mkdirSync(outdir, { recursive: true });
      const base = path.basename(sceneFile, path.extname(sceneFile));
      const png = path.join(outdir, `${base}.png`);
      const svgPath = path.join(outdir, `${base}.svg`);
      await new Promise((resolve) => setTimeout(resolve, 300));
      await page.screenshot({ path: png, fullPage: true });
      const svg = await page.evaluate(
        () => document.querySelector("#excalidraw-container svg")?.outerHTML || ""
      );
      if (svg) fs.writeFileSync(svgPath, svg);
      const info = await page.evaluate(() => (document.querySelector("#info") || {}).textContent);
      console.log(`[OK] ${png}`);
      if (svgPath && fs.existsSync(svgPath)) console.log(`[OK] ${svgPath}`);
      console.log(`[INFO] ${info || ""}`.trim());
    }
  } catch (err) {
    console.error(`[ERROR] ${err.message}`);
    process.exitCode = 1;
  } finally {
    await browser.close();
    server.close();
    fs.rmSync(workdir, { recursive: true, force: true });
  }
}

main().catch((err) => {
  console.error(`[ERROR] ${err.stack || err.message}`);
  process.exit(1);
});
