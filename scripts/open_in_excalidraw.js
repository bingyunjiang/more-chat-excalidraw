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
 * Options:
 *   --no-browser   Do not open the browser after pushing
 *   --check-only   Only check if the local Excalidraw is reachable
 *   --start        Try to start the Excalidraw service if not running
 *
 * Web root override: EXCALIDRAW_WEB_ROOT (default:
 * /Users/Bing/.local/share/excalidraw/excalidraw-app/build)
 *
 * Exit codes: 0 = OK, 1 = errors, 2 = usage error, 3 = sandbox restriction
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execFile, execSync } = require("child_process");

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

function isReachable(url) {
  try {
    const http = require("http");
    const req = http.get(url, (res) => {
      res.resume();
    });
    req.setTimeout(2000, () => {
      req.destroy();
    });
    return true;
  } catch (_) {
    return false;
  }
}

function checkServiceSync() {
  try {
    const result = execSync(`curl -s -o /dev/null -w "%{http_code}" ${URL} 2>/dev/null`, {
      timeout: 3000,
      encoding: "utf-8",
    });
    return result.trim() === "200";
  } catch (_) {
    return false;
  }
}

function startService() {
  try {
    execSync("launchctl start com.excalidraw.editor", {
      timeout: 5000,
      encoding: "utf-8",
    });
    console.log("[OK] Sent launchctl start com.excalidraw.editor");
    // Wait for service to come up
    for (let i = 0; i < 10; i++) {
      const sleep = (ms) => {
        const end = Date.now() + ms;
        while (Date.now() < end) {}
      };
      sleep(1000);
      if (checkServiceSync()) {
        console.log("[OK] Excalidraw service is now reachable");
        return true;
      }
    }
    console.error("[WARN] Service started but not reachable after 10s");
    return false;
  } catch (err) {
    console.error(`[WARN] Could not start service via launchctl: ${err.message}`);
    return false;
  }
}

function main() {
  const args = process.argv.slice(2);
  const noBrowser = args.includes("--no-browser");
  const checkOnly = args.includes("--check-only");
  const doStart = args.includes("--start");
  const sceneFile = args.find((a) => !a.startsWith("-"));

  if (checkOnly) {
    if (checkServiceSync()) {
      console.log(`[OK] Excalidraw is reachable at ${URL}`);
      process.exit(0);
    } else {
      console.error(`[ERROR] Excalidraw is NOT reachable at ${URL}`);
      if (doStart) {
        console.log("[INFO] Attempting to start the service...");
        if (startService()) {
          process.exit(0);
        }
      }
      console.error("[HINT] Run: launchctl start com.excalidraw.editor");
      process.exit(1);
    }
  }

  if (!sceneFile) {
    console.error("Usage: node open_in_excalidraw.js <file.excalidraw> [--no-browser] [--check-only] [--start]");
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

  // Check if service is reachable
  if (!checkServiceSync()) {
    if (doStart) {
      console.log("[INFO] Excalidraw not reachable, attempting to start...");
      startService();
    } else {
      console.error(`[WARN] Excalidraw is NOT reachable at ${URL}`);
      console.error("[HINT] Add --start to auto-start the service, or run: launchctl start com.excalidraw.editor");
    }
  }

  // Try to write to web root
  const prev = path.join(webRoot, "scene.excalidraw");
  const sceneDest = path.join(webRoot, "scene.excalidraw");
  const versionDest = path.join(webRoot, "scene.json");

  try {
    if (fs.existsSync(prev)) {
      fs.copyFileSync(prev, path.join(webRoot, "scene.excalidraw.bak"));
    }
    fs.copyFileSync(sceneFile, sceneDest);
    fs.writeFileSync(versionDest, JSON.stringify({ version: timestamp() }, null, 2));
    console.log(`[OK] scene.excalidraw updated in ${webRoot}`);
  } catch (err) {
    if (err.code === "EPERM" || err.code === "EACCES") {
      console.error("[WARN] Cannot write to web root (sandbox/permission restriction).");
      console.error("[INFO] Attempting via cp command...");
      try {
        const cpCmd = `cp "${sceneFile}" "${sceneDest}"`;
        execSync(cpCmd, { encoding: "utf-8" });
        execSync(`cat > "${versionDest}" << 'VEOF'\n${JSON.stringify({ version: timestamp() }, null, 2)}\nVEOF`, { encoding: "utf-8" });
        console.log(`[OK] scene.excalidraw updated via cp in ${webRoot}`);
      } catch (cpErr) {
        console.error(`[ERROR] Cannot write to web root via cp either: ${cpErr.message}`);
        console.error("[HINT] This script needs to write to the Excalidraw web root.");
        console.error("       Run with escalated privileges, or copy the file manually:");
        console.error(`       cp "${sceneFile}" "${sceneDest}"`);
        process.exit(3);
      }
    } else {
      console.error(`[ERROR] Failed to write to web root: ${err.message}`);
      process.exit(1);
    }
  }

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
