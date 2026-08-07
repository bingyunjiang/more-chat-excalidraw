#!/usr/bin/env node
/**
 * Push a .excalidraw file into the local Excalidraw web app (http://localhost:5001/).
 *
 * The local app polls `scene.json` in its web root; when `version` changes it
 * auto-imports `scene.excalidraw`. This script copies the file there, bumps the
 * version, and opens the page. An already-open tab refreshes itself within ~2s.
 *
 * Usage:
 *   node open_in_excalidraw.js <file.excalidraw> [--no-browser]
 *
 * Web root override: EXCALIDRAW_WEB_ROOT (default:
 * /Users/Bing/.local/share/excalidraw/excalidraw-app/build)
 *
 * Note: overwrites the live scene.excalidraw; keeps the previous one as
 * scene.excalidraw.bak.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execFile } = require("child_process");

const DEFAULT_WEB_ROOT = path.join(
  os.homedir(),
  ".local",
  "share",
  "excalidraw",
  "excalidraw-app",
  "build"
);
const URL = process.env.EXCALIDRAW_URL || "http://localhost:5001/";

function timestamp() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return (
    `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}` +
    `${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
  );
}

function main() {
  const sceneFile = process.argv[2];
  const noBrowser = process.argv.includes("--no-browser");
  if (!sceneFile) {
    console.error("Usage: node open_in_excalidraw.js <file.excalidraw> [--no-browser]");
    process.exit(2);
  }
  if (!fs.existsSync(sceneFile)) {
    console.error(`[ERROR] Scene not found: ${sceneFile}`);
    process.exit(1);
  }

  const webRoot = process.env.EXCALIDRAW_WEB_ROOT || DEFAULT_WEB_ROOT;
  if (!fs.existsSync(path.join(webRoot, "index.html"))) {
    console.error(`[ERROR] Local Excalidraw web root not found: ${webRoot}`);
    console.error("Set EXCALIDRAW_WEB_ROOT to the directory served at localhost:5001.");
    process.exit(1);
  }

  const prev = path.join(webRoot, "scene.excalidraw");
  if (fs.existsSync(prev)) {
    fs.copyFileSync(prev, path.join(webRoot, "scene.excalidraw.bak"));
  }
  fs.copyFileSync(sceneFile, prev);
  fs.writeFileSync(
    path.join(webRoot, "scene.json"),
    JSON.stringify({ version: timestamp() }, null, 2)
  );

  console.log(`[OK] scene.excalidraw updated in ${webRoot}`);
  console.log(`[OK] ${URL}`);
  if (!noBrowser) {
    execFile("open", [URL], (err) => {
      if (err) {
        console.error(`[WARN] Failed to open browser: ${err.message}`);
      } else {
        console.log("[OK] Browser opened (an already-open tab auto-refreshes within ~2s)");
      }
    });
  }
}

main();
