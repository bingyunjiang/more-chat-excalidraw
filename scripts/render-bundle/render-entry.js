import { exportToSvg, restoreElements } from "@excalidraw/excalidraw";

const CJK_RE = /[\u2E80-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF]/;
const CJK_FONT_ASSETS = {
  "Long Cang": "LongCang.woff2",
  "Ma Shan Zheng": "MaShanZheng.woff2",
  "Liu Jian Mao Cao": "LiuJianMaoCao.woff2",
};

const CJK_FONT_BY_FAMILY_ID = {
  11: "Ma Shan Zheng",
  12: "Long Cang",
  13: "Liu Jian Mao Cao",
};

function getCjkFontConfig(sceneData) {
  const appState = sceneData.appState || {};
  const textConfig = (sceneData.elements || [])
    .find((el) => el.type === "text" && el.customData?.cjkFontFamily)?.customData || {};
  const primary = appState.cjkFontFamily || textConfig.cjkFontFamily;
  const fallbacks = appState.cjkFontFallbacks || textConfig.cjkFontFallbacks || [];
  const elementFonts = (sceneData.elements || [])
    .filter((el) => el.type === "text" && CJK_RE.test(el.text || ""))
    .map((el) => CJK_FONT_BY_FAMILY_ID[el.fontFamily])
    .filter(Boolean);
  return [...new Set([primary, ...fallbacks, ...elementFonts].filter(Boolean))];
}

function getElementFontForText(sceneData, value) {
  const normalized = (value || "").replace(/\s+/g, "");
  if (!normalized) return null;
  const textElements = (sceneData.elements || [])
    .filter((el) => el.type === "text" && CJK_RE.test(el.text || ""));
  const exact = textElements.find((el) =>
    (el.text || "").replace(/\s+/g, "") === normalized
  );
  const partial = exact || textElements.find((el) =>
    (el.text || "").replace(/\s+/g, "").includes(normalized)
  );
  return CJK_FONT_BY_FAMILY_ID[partial?.fontFamily] || null;
}

function getElementFontForNode(sceneData, node) {
  const candidateId = node.getAttribute("data-element-id") || node.getAttribute("data-id");
  if (candidateId) {
    const element = (sceneData.elements || []).find((el) => el.id === candidateId);
    const mapped = CJK_FONT_BY_FAMILY_ID[element?.fontFamily];
    if (mapped) return mapped;
  }
  return getElementFontForText(sceneData, node.textContent || "");
}

function fontStack(primary, configured) {
  const ordered = [
    primary,
    ...configured.filter((name) => name !== primary),
    "sans-serif",
  ].filter(Boolean);
  return ordered
    .map((name) => name === "sans-serif" ? name : `"${name.replaceAll('"', '\\\"')}"`)
    .join(", ");
}

async function applyCjkFont(svg, sceneData) {
  const configured = [...new Set(getCjkFontConfig(sceneData))];
  if (!configured.length) return;
  for (const name of configured) {
    const asset = CJK_FONT_ASSETS[name];
    if (!asset) continue;
    try {
      const face = new FontFace(name, `url("./__cjk-font/${asset}") format("woff2")`);
      document.fonts.add(await face.load());
    } catch (_) {
      // The local Excalidraw font service is optional; continue to local fonts.
    }
  }
  await document.fonts.ready;
  const selected = configured.find((name) =>
    document.fonts.check(`16px "${name}"`, "中文手绘")
  ) || configured[0];
  for (const node of svg.querySelectorAll("text")) {
    const value = node.textContent || "";
    if (!CJK_RE.test(value)) continue;
    const elementFont = getElementFontForNode(sceneData, node);
    const cssStack = fontStack(elementFont || selected, configured);
    const runs = [];
    for (const char of value) {
      const cjk = CJK_RE.test(char);
      const previous = runs[runs.length - 1];
      if (previous && previous.cjk === cjk) previous.text += char;
      else runs.push({ cjk, text: char });
    }
    if (runs.every((run) => run.cjk)) {
      node.setAttribute("font-family", cssStack);
      continue;
    }
    // A single editable Excalidraw text element can contain both scripts but
    // only one numeric fontFamily. Keep its Latin runs explicitly on Virgil
    // even when the source element uses native Long Cang (12).
    const latinStack = "Virgil, Segoe UI Emoji";
    node.textContent = "";
    for (const run of runs) {
      const span = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
      span.setAttribute("font-family", run.cjk ? cssStack : latinStack);
      span.textContent = run.text;
      node.appendChild(span);
    }
  }
  svg.dataset.cjkFont = selected;
  svg.dataset.cjkFonts = configured.join(",");
}

async function main() {
  const container = document.getElementById("excalidraw-container");
  const statusEl = document.getElementById("status");
  const infoEl = document.getElementById("info");
  const noteEl = document.querySelector(".note");

  const scene = new URLSearchParams(window.location.search).get("scene") || "fixture-smoke.excalidraw";
  if (noteEl) noteEl.textContent = `Fixture: ${scene} | Rendered by @excalidraw/excalidraw 0.18.1`;

  let sceneData;
  try {
    const resp = await fetch(`./${scene}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    sceneData = await resp.json();
    statusEl.textContent = `Loaded: ${sceneData.elements?.length || 0} elements`;
    statusEl.style.color = "#2f9e44";
  } catch (e) {
    statusEl.textContent = `Failed to load scene: ${e.message}`;
    statusEl.style.color = "#e03131";
    return;
  }

  const elements = restoreElements(sceneData.elements || [], null);
  const appState = sceneData.appState || {};

  try {
    const svg = await exportToSvg({
      elements,
      appState: {
        ...appState,
        exportBackground: true,
        viewBackgroundColor: appState.viewBackgroundColor || "#ffffff",
      },
      files: sceneData.files || null,
      exportWithDarkMode: appState.theme === "dark",
    });

    await applyCjkFont(svg, sceneData);

    container.appendChild(svg);

    const rects = elements.filter(e => e.type === "rectangle").length;
    const texts = elements.filter(e => e.type === "text").length;
    const lines = elements.filter(e => e.type === "line").length;
    const arrows = elements.filter(e => e.type === "arrow").length;
    infoEl.textContent = `Rects: ${rects} | Texts: ${texts} | Lines: ${lines} | Arrows: ${arrows}`;
    statusEl.textContent = "Render complete";
  } catch (e) {
    statusEl.textContent = `Render failed: ${e.message}`;
    statusEl.style.color = "#e03131";
    console.error(e);
  }
}

main();
