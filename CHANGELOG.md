# Changelog

本项目的所有显著变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.6.0] - 2026-08-08

### 新增

- **M9 MCP 协议集成（借鉴 excalidraw/excalidraw-mcp，5069★）**：`mcp_server.mjs` 通过 MCP stdio 协议暴露 generate_diagram / validate_diagram / push_preview / list_templates 四个工具，供 agent 直接调用
- e2e 测试从 23 项扩展到 24 项（MCP 工具注册）

## [0.5.0] - 2026-08-08

### 新增

- **M9 Graphviz 自动布局（借鉴 drawmode）**：`ir_to_excalidraw.py --layout dot|neato|twopi` 使用 Graphviz 层次/力导向/树形布局，自动换算坐标与节点尺寸，无 Graphviz 时回退内置布局
- e2e 测试从 20 项扩展到 23 项（Graphviz 布局）

## [0.4.0] - 2026-08-08

### 新增

- **M8 完整预览（Pillar D）**：预览服务器内嵌 Excalidraw 编辑器（`/editor`），支持浏览器内直接编辑、保存写回本地（`/api/save`）、多画布管理（`/api/canvases`）
- **M8 多格式导出**：`render_preview.js --format pdf` 新增 PDF 导出（A4，Chromium 渲染，沙箱内降级 SVG）
- **M9 关键帧动画（借鉴 excalimate）**：`ir_to_excalidraw.py` 自动注入 `customData.animate`（7 级顺序规则）；预览服务器新增 `/animate` 播放页与 `/api/animate` 帧序列端点
- **M9 Mermaid 转换（借鉴 al1y + axtonliu）**：`mermaid_to_excalidraw.js` 轻量解析 flowchart/sequenceDiagram 子集 → IR → Excalidraw，无浏览器依赖
- **M9 自纠错质量门**：`validate_excalidraw.py --visual` 新增元素重叠、悬空箭头、布局密度检查；`ir_to_excalidraw.py --validate` 自动附带视觉检查
- **M7 增量编辑**：`merge_excalidraw.py` 支持 merge（保留旧 id）/ patch（--set/--move）/ restore（备份回退）
- e2e 测试从 10 项扩展到 20 项（编辑器、保存写回、多画布、动画、Mermaid）

### 变更

- `package.json` 版本 0.3.0 → 0.4.0，补齐 npm script 注册表（mermaid/merge/editor/build:editor/test 等）

## [0.3.0] - 2026-08-07

### 新增

- **M5 模板系统**：10 种图类型（+层级/关系/对比/时间线）；语义色板（8 填充色 + 4 主题）；元素级构建块；50+ 技术组件样式；9 种视觉模式；动画关键帧模板
- **M5 交互脚本**：`template_selector.py`（意图推荐）、`list_templates.js`（模板列表 + SVG 预览）
- **M6 文案引擎**：IR 中间格式定义（19 种节点类型、边/分组/模板专用字段）
- **M7 JSON 生成**：`ir_to_excalidraw.py` IR → Excalidraw 转换器（10 种布局、4 套主题、自动绑定）

## [0.2.0] - 2026-08-07

### 新增

- 模板选择器与模板列表脚本（初版）

## [0.1.0] - 2026-08-07

### 新增

- 初始版本：核心闭环（理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代）
- 实时预览服务器（轮询 API，借鉴 al1y/mcp-excalidraw）
- `.excalidraw` v2 校验器（结构 + 引用完整性）
- 沙箱兼容的渲染/打开脚本（Playwright + SVG fallback）
- e2e 测试框架
