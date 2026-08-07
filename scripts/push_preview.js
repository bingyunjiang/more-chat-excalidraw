#!/usr/bin/env node
/**
 * Push a .excalidraw file to a running preview server (preview_server.js).
 *
 * Usage:
 *   node scripts/push_preview.js <file.excalidraw> [--url http://localhost:6060]
 *
 * Exit codes: 0 = OK, 1 = error, 2 = usage error.
 */

"use strict";

const fs = require("fs");
const http = require("http");

const DEFAULT_URL = "http://localhost:6060/";

function parseArgs(argv) {
  const args = argv.slice(2);
  const positional = [];
  const opts = { url: process.env.PREVIEW_URL || DEFAULT_URL };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--url" || a === "-u") opts.url = args[++i];
    else if (a.startsWith("--url=")) opts.url = a.split("=")[1];
    else if (a === "--help" || a === "-h") opts.help = true;
    else positional.push(a);
  }
  if (!/\/$/.test(opts.url)) opts.url += "/";
  return { positional, opts };
}

function post(url, body) {
  return new Promise((resolve, reject) => {
    const target = new URL(url);
    const payload = JSON.stringify(body);
    const req = http.request(
      {
        hostname: target.hostname,
        port: target.port || 80,
        path: "/api/current-diagram",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(payload),
        },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve({ status: res.statusCode, body: data }));
      }
    );
    req.on("error", reject);
    req.setTimeout(5000, () => {
      req.destroy(new Error("Timed out connecting to preview server"));
    });
    req.end(payload);
  });
}

async function main() {
  const { positional, opts } = parseArgs(process.argv);
  if (opts.help) {
    console.log(`Usage: node scripts/push_preview.js <file.excalidraw> [--url http://localhost:6060]

Push a .excalidraw file to the running preview server. The open preview page
updates in real time (polls every ~1.5s).
`);
    process.exit(0);
  }

  const sceneFile = positional[0];
  if (!sceneFile) {
    console.error("Usage: node scripts/push_preview.js <file.excalidraw> [--url ...]");
    process.exit(2);
  }
  if (!fs.existsSync(sceneFile)) {
    console.error(`[ERROR] Scene not found: ${sceneFile}`);
    process.exit(1);
  }

  let data;
  try {
    data = JSON.parse(fs.readFileSync(sceneFile, "utf-8"));
  } catch (err) {
    console.error(`[ERROR] Invalid JSON in ${sceneFile}: ${err.message}`);
    process.exit(1);
  }
  if (!Array.isArray(data.elements)) {
    console.error(`[ERROR] ${sceneFile} does not look like an .excalidraw document (missing elements)`);
    process.exit(1);
  }

  try {
    const result = await post(opts.url, data);
    if (result.status === 200) {
      const info = JSON.parse(result.body);
      console.log(`[OK] Pushed ${sceneFile} (${data.elements.length} elements)`);
      console.log(`[OK] Preview: ${opts.url} (updates live in ~1.5s)`);
    } else {
      console.error(`[ERROR] Preview server returned HTTP ${result.status}: ${result.body}`);
      process.exit(1);
    }
  } catch (err) {
    console.error(`[ERROR] Could not reach preview server at ${opts.url}`);
    console.error("       Start it with: node scripts/preview_server.js [--port 6060]");
    console.error(`       (${err.message})`);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(`[ERROR] ${err.message}`);
  process.exit(1);
});
