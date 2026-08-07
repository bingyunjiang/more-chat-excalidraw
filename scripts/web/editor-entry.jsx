/**
 * In-browser Excalidraw editor entry — bundled with esbuild into
 * scripts/web/editor-bundle.js and served by preview_server.js.
 *
 * Exposes window.ExcalidrawEditor with mount/unmount + scene sync.
 */
import React, { useRef, useState, useCallback, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { Excalidraw } from "@excalidraw/excalidraw";

function EditorApp({ initialElements, initialAppState, onChange }) {
  const excalidrawRef = useRef(null);
  const [sceneData, setSceneData] = useState({
    elements: initialElements || [],
    appState: initialAppState || {},
  });
  const [status, setStatus] = useState("就绪");
  const [mode, setMode] = useState("editor");

  const onSceneChange = useCallback(
    (elements, appState) => {
      const next = { elements, appState };
      setSceneData(next);
      if (onChange) onChange(next);
    },
    [onChange]
  );

  const exportSvg = useCallback(async () => {
    try {
      const { exportToSvg, serializeAsJSON } = await import("@excalidraw/excalidraw");
      const svg = await exportToSvg({
        elements: sceneData.elements,
        appState: sceneData.appState,
        files: {},
      });
      const blob = new Blob([svg.outerHTML], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "diagram.svg";
      a.click();
      URL.revokeObjectURL(url);
      setStatus("已导出 SVG");
    } catch (e) {
      setStatus("导出失败: " + e.message);
    }
  }, [sceneData]);

  const exportJson = useCallback(() => {
    const blob = new Blob([JSON.stringify(sceneData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diagram.excalidraw";
    a.click();
    URL.revokeObjectURL(url);
    setStatus("已导出 .excalidraw JSON");
  }, [sceneData]);

  const saveToServer = useCallback(async () => {
    try {
      const resp = await fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sceneData),
      });
      const data = await resp.json();
      setStatus(data.success ? "已保存到服务器" : "保存失败: " + (data.error || ""));
    } catch (e) {
      setStatus("保存失败: " + e.message);
    }
  }, [sceneData]);

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", background: "#f8f9fa", borderBottom: "1px solid #e0e0e0" }}>
        <strong style={{ fontSize: 14 }}>Excalidraw 编辑器</strong>
        <button onClick={saveToServer} style={btnStyle}>保存到服务器</button>
        <button onClick={exportSvg} style={btnStyle}>导出 SVG</button>
        <button onClick={exportJson} style={btnStyle}>导出 JSON</button>
        <span style={{ marginLeft: "auto", fontSize: 12, color: "#868e96" }}>{status}</span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <Excalidraw
          initialData={{ elements: sceneData.elements, appState: sceneData.appState }}
          onChange={onSceneChange}
          ref={excalidrawRef}
        />
      </div>
    </div>
  );
}

const btnStyle = {
  padding: "4px 10px",
  fontSize: 12,
  borderRadius: 6,
  border: "1px solid #ced4da",
  background: "#fff",
  cursor: "pointer",
};

window.ExcalidrawEditor = {
  mount(container, initialScene, onChange) {
    if (!container) throw new Error("mount: container is required");
    const root = createRoot(container);
    root.render(
      <EditorApp
        initialElements={(initialScene && initialScene.elements) || []}
        initialAppState={(initialScene && initialScene.appState) || {}}
        onChange={onChange}
      />
    );
    return root;
  },
};
