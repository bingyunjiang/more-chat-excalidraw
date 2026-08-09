#!/usr/bin/env node
// Verify direct and transitive web dependencies are represented in package-lock.
import fs from "node:fs";
const scriptsDir = new URL("./", import.meta.url).pathname;
const pkg = JSON.parse(fs.readFileSync(`${scriptsDir}web/package.json`, "utf8"));
const lock = JSON.parse(fs.readFileSync(`${scriptsDir}web/package-lock.json`, "utf8"));
const packages = lock.packages || {};
const direct = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
const missing = [];
const resolveKey = (name, fromKey) => {
  const parts = fromKey.split("/node_modules/")[0];
  const candidate = `${parts}/node_modules/${name}`;
  if (packages[candidate]) return candidate;
  const suffix = `/node_modules/${name}`;
  return Object.keys(packages).find((key) => key.endsWith(suffix)) || `node_modules/${name}`;
};
const queue = Object.keys(direct).map((name) => [`node_modules/${name}`, name]);
const seen = new Set();
while (queue.length) {
  const [key, name] = queue.shift();
  if (seen.has(key)) continue;
  seen.add(key);
  const entry = packages[key] || packages[resolveKey(name, key)];
  if (!entry) { missing.push(key); continue; }
  for (const dep of Object.keys(entry.dependencies || {})) queue.push([resolveKey(dep, key), dep]);
  for (const dep of Object.keys(entry.optionalDependencies || {})) queue.push([resolveKey(dep, key), dep]);
  for (const dep of Object.keys(entry.peerDependencies || {})) {
    if (!entry.peerDependenciesMeta?.[dep]?.optional) queue.push([resolveKey(dep, key), dep]);
  }
}
if (missing.length) {
  console.error(`Missing lock entries (${missing.length}):\n${missing.join("\n")}`);
  process.exit(1);
}
console.log(`lock ok: ${seen.size} dependency entries checked`);
