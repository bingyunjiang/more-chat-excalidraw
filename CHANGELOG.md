# Changelog

本项目的所有显著变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.0.1] - 2026-08-08

### 初始版本

通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。

- **核心闭环**：理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代
- **模板系统**：10 种图类型（流程图/架构图/时序图/思维导图/泳道图/ER图/层级图/关系图/对比图/时间线图）；语义色板（8 填充色 + 4 主题）；元素级构建块；50+ 技术组件样式；9 种视觉模式；动画关键帧模板
- **文案引擎**：IR 中间格式定义（19 种节点类型、边/分组/模板专用字段）；`template_selector.py` 意图推荐
- **JSON 生成**：`ir_to_excalidraw.py` IR → Excalidraw 转换器（10 种布局、4 套主题、自动绑定、动画元数据注入）；Graphviz 自动布局（dot/neato/twopi）
- **增量编辑**：`merge_excalidraw.py` merge（保留旧 id）/ patch（--set/--move）/ restore（备份回退）
- **Mermaid 转换**：`mermaid_to_excalidraw.js` 轻量解析 flowchart/sequenceDiagram 子集 → IR → Excalidraw
- **知识图谱**：`knowledge_graph.py` 从实体/关系描述自动分层生成架构图
- **实时预览**：`preview_server.js` 轮询 SVG 预览 + 内嵌完整 Excalidraw 编辑器（/editor）+ 动画播放页（/animate）+ 双向同步保存（/api/save）+ 多画布（/api/canvases）
- **多格式导出**：`render_preview.js` PNG / SVG / PDF（沙箱内自动降级 SVG）
- **自纠错质量门**：`validate_excalidraw.py --visual` 检查元素重叠、悬空箭头、布局密度
- **云架构图标库**：`icon_library.py` 自包含 67 个技术图标（SVG data URL），`ir_to_excalidraw.py --icons` 注入 image 元素 + files 资源（借鉴 excalidraw-icons-mcp）
- **动画 GIF 导出**：`render_animation_gif.py` 读取关键帧顺序合成 GIF（output/animation-demo.gif，借鉴 excalimate）
- **MCP 协议**：`mcp_server.mjs` 暴露 generate_diagram / validate_diagram / push_preview / list_templates 四个工具
- **测试**：e2e 24 项（生成 → 校验 → 渲染 → 预览 → 编辑器 → 保存 → 多画布 → 动画 → Mermaid → 知识图谱 → Graphviz → 增量编辑 → MCP）
- **CI**：GitHub Actions（validate + smoke + e2e）
