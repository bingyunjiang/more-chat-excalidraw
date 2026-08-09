"use strict";
/**
 * Shared server-side SVG renderer for .excalidraw v2 scenes.
 *
 * Renders the core element types (rectangle / ellipse / diamond / text /
 * arrow / line / frame) without the full @excalidraw library. Good enough
 * for real-time preview and sandbox fallback rendering.
 *
 * Used by:
 *   - render_preview.js  (--no-server fallback path)
 *   - preview_server.js  (/api/diagram.svg, /api/preview)
 */

const CJK_RE = /[\u2E80-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF]/;

function cssFontStack(data, el, text) {
  if (CJK_RE.test(String(text))) {
    const custom = el?.customData || {};
    const state = data.appState || {};
    const primary = state.cjkFontFamily || custom.cjkFontFamily;
    const fallbacks = state.cjkFontFallbacks || custom.cjkFontFallbacks || [];
    if (primary) {
      return [...new Set([primary, ...fallbacks])]
        .map((name) => `&quot;${escapeXml(name)}&quot;`)
        .concat("sans-serif")
        .join(", ");
    }
  }
  if (el?.fontFamily === 3) return "&quot;Cascadia Code&quot;, monospace";
  if (el?.fontFamily === 2) return "Helvetica, Arial, sans-serif";
  return "Virgil, &quot;Comic Sans MS&quot;, cursive";
}

function textWithScriptRuns(data, el, text) {
  const value = String(text);
  if (!CJK_RE.test(value) || [...value].every((char) => CJK_RE.test(char))) {
    return escapeXml(value);
  }
  const runs = [];
  for (const char of value) {
    const cjk = CJK_RE.test(char);
    const previous = runs[runs.length - 1];
    if (previous && previous.cjk === cjk) previous.text += char;
    else runs.push({ cjk, text: char });
  }
  return runs.map((run) =>
    `<tspan font-family="${cssFontStack(data, el, run.cjk ? "中" : "A")}">${escapeXml(run.text)}</tspan>`
  ).join("");
}

function estimateTextWidth(text, fontSize) {
  let width = 0;
  for (const ch of text) {
    width += CJK_RE.test(ch) ? 1.0 : 0.6;
  }
  return width * fontSize;
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Wrap text into lines that fit within maxWidth (pixels), keeping explicit
 * newlines. Returns an array of line strings.
 */
function wrapText(text, fontSize, maxWidth) {
  const lines = [];
  for (const rawLine of String(text).split("\n")) {
    if (rawLine === "") {
      lines.push("");
      continue;
    }
    let current = "";
    for (const ch of rawLine) {
      const candidate = current + ch;
      if (estimateTextWidth(candidate, fontSize) > maxWidth && current) {
        lines.push(current);
        current = ch;
      } else {
        current = candidate;
      }
    }
    if (current) lines.push(current);
  }
  return lines;
}

function fillOrNone(color) {
  return !color || color === "transparent" ? "none" : color;
}

/**
 * Render an .excalidraw v2 scene (parsed JSON) to an SVG string.
 *
 * @param {object} data        parsed .excalidraw JSON (type/version/elements/appState)
 * @param {object} [opts]      { padding: number (default 60), minWidth, minHeight }
 * @returns {string} SVG markup
 */
function renderSvgFromScene(data, opts = {}) {
  let elements = (data.elements || []).filter((el) => el && !el.isDeleted);
  // Animation frame support: only keep elements whose animate.order <= maxOrder.
  // Elements without customData.animate are always included (maxOrder >= 1).
  if (typeof opts.maxOrder === "number") {
    elements = elements.filter((el) => {
      const order = el.customData?.animate?.order;
      if (order === undefined) return opts.maxOrder >= 1;
      return order <= opts.maxOrder;
    });
  }
  const bgColor = (data.appState || {}).viewBackgroundColor || "#ffffff";
  const padding = opts.padding ?? 60;

  // Bounding box over all visible elements.
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const el of elements) {
    if (typeof el.x !== "number" || typeof el.y !== "number") continue;
    const w = typeof el.width === "number" ? el.width : 0;
    const h = typeof el.height === "number" ? el.height : 0;
    if (el.x < minX) minX = el.x;
    if (el.y < minY) minY = el.y;
    if (el.x + w > maxX) maxX = el.x + w;
    if (el.y + h > maxY) maxY = el.y + h;
    // Include line/arrow control points.
    if (Array.isArray(el.points)) {
      for (const [px, py] of el.points) {
        const ax = el.x + px;
        const ay = el.y + py;
        if (ax < minX) minX = ax;
        if (ay < minY) minY = ay;
        if (ax > maxX) maxX = ax;
        if (ay > maxY) maxY = ay;
      }
    }
  }
  if (!Number.isFinite(minX)) {
    minX = 0;
    minY = 0;
    maxX = 400;
    maxY = 300;
  }
  minX -= padding;
  minY -= padding;
  maxX += padding;
  maxY += padding;

  const viewW = Math.max(maxX - minX, opts.minWidth || 400);
  const viewH = Math.max(maxY - minY, opts.minHeight || 300);

  const parts = [];
  parts.push(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${viewW}" height="${viewH}" ` +
      `viewBox="${minX} ${minY} ${viewW} ${viewH}">`
  );
  parts.push(
    `<rect x="${minX}" y="${minY}" width="${viewW}" height="${viewH}" fill="${bgColor}"/>`
  );
  parts.push(
    `<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" ` +
      `orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#868e96"/></marker></defs>`
  );

  // Frames first so boxes stay under their children.
  const frames = elements.filter((el) => el.type === "frame");
  for (const el of frames) {
    parts.push(
      `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" ` +
        `fill="none" stroke="#a5d8ff" stroke-width="2" stroke-dasharray="8 4"/>`
    );
    if (el.name) {
      parts.push(
        `<text x="${el.x + 8}" y="${el.y + 18}" font-size="16" font-family="${cssFontStack(data, el, el.name)}" ` +
          `fill="#1971c2">${textWithScriptRuns(data, el, el.name)}</text>`
      );
    }
  }

  const byType = {};
  for (const el of elements) {
    if (el.type === "frame") continue;
    byType[el.type] = (byType[el.type] || 0) + 1;

    if (el.type === "rectangle") {
      const rx = el.roundness ? 8 : 0;
      parts.push(
        `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" ` +
          `fill="${fillOrNone(el.backgroundColor)}" stroke="${el.strokeColor || "#1e1e1e"}" ` +
          `stroke-width="${el.strokeWidth || 2}" rx="${rx}"/>`
      );
    } else if (el.type === "ellipse") {
      parts.push(
        `<ellipse cx="${el.x + el.width / 2}" cy="${el.y + el.height / 2}" ` +
          `rx="${el.width / 2}" ry="${el.height / 2}" ` +
          `fill="${fillOrNone(el.backgroundColor)}" stroke="${el.strokeColor || "#1e1e1e"}" ` +
          `stroke-width="${el.strokeWidth || 2}"/>`
      );
    } else if (el.type === "diamond") {
      const cx = el.x + el.width / 2;
      const cy = el.y + el.height / 2;
      parts.push(
        `<polygon points="${cx},${el.y} ${el.x + el.width},${cy} ${cx},${el.y + el.height} ` +
          `${el.x},${cy}" fill="${fillOrNone(el.backgroundColor)}" ` +
          `stroke="${el.strokeColor || "#1e1e1e"}" stroke-width="${el.strokeWidth || 2}"/>`
      );
    } else if (el.type === "image") {
      // Embed the actual image data (dataURL from top-level files) when present.
      const fileId = el.fileId;
      const file = (data.files || {})[fileId];
      if (file && file.dataURL) {
        parts.push(
          `<image x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" ` +
            `href="${escapeXml(file.dataURL)}" preserveAspectRatio="xMidYMid meet"/>`
        );
      } else {
        parts.push(
          `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" ` +
            `fill="#f1f3f5" stroke="#868e96" stroke-width="1.5" stroke-dasharray="4 3"/>` +
            `<text x="${el.x + el.width / 2}" y="${el.y + el.height / 2}" ` +
            `text-anchor="middle" dominant-baseline="central" font-size="14" ` +
            `fill="#868e96">image</text>`
        );
      }
    } else if (el.type === "text" && el.text) {
      const fontSize = el.fontSize || 20;
      const container = el.containerId ? elements.find((e) => e.id === el.containerId) : null;
      const boxW = container ? container.width : el.width || 200;
      const anchor =
        el.textAlign === "left" ? "start" : el.textAlign === "right" ? "end" : "middle";
      const lines = wrapText(el.text, fontSize, Math.max(boxW - 8, 40));
      const lineH = fontSize * 1.25;
      const totalH = lineH * lines.length;
      const startY = container
        ? container.y + (container.height - totalH) / 2 + fontSize / 2.6
        : el.y + fontSize;
      lines.forEach((line, idx) => {
        const cx = container
          ? container.x + container.width / 2
          : anchor === "middle"
            ? el.x + (el.width || 0) / 2
            : anchor === "end"
              ? el.x + (el.width || 0)
              : el.x;
        parts.push(
          `<text x="${cx}" y="${startY + idx * lineH}" text-anchor="${anchor}" ` +
            `dominant-baseline="central" font-size="${fontSize}" font-family="${cssFontStack(data, el, line)}" ` +
            `fill="${el.strokeColor || "#1e1e1e"}">${textWithScriptRuns(data, el, line)}</text>`
        );
      });
    } else if ((el.type === "arrow" || el.type === "line") && Array.isArray(el.points)) {
      const pts = el.points.map((p) => [p[0] + el.x, p[1] + el.y]);
      const d = pts
        .map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(1) + "," + p[1].toFixed(1))
        .join(" ");
      const marker = el.type === "arrow" ? ' marker-end="url(#arrowhead)"' : "";
      parts.push(
        `<path d="${d}" fill="none" stroke="${el.strokeColor || "#868e96"}" ` +
          `stroke-width="${el.strokeWidth || 2}"${marker}/>`
      );
    }
    // freedraw / embeddable / other types: intentionally skipped in lightweight render.
  }

  parts.push("</svg>");
  return {
    svg: parts.join("\n"),
    stats: {
      total: elements.length,
      by_type: byType,
      viewBox: { minX, minY, width: viewW, height: viewH },
    },
  };
}

module.exports = { renderSvgFromScene, estimateTextWidth, wrapText };
