import { exportToSvg, restoreElements } from "@excalidraw/excalidraw";

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
