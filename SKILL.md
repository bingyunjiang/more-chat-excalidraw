---
name: more-chat-excalidraw
description: 通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。当用户想"画一张图/流程图/架构图/时序图/思维导图"、要求把对话内容做成 Excalidraw 图表、修改已有的 .excalidraw 文件、或让 agent 用 Excalidraw 呈现思路时使用。覆盖 .excalidraw v2 JSON 生成、结构校验、SVG/PNG 预览渲染，以及打开本地 Excalidraw（http://localhost:5001/）查看与迭代。
---

# Chat-to-Excalidraw（笔谈）

## Overview

把用户的自然语言转化为可打开的 `.excalidraw` v2 画布文件，并在本地 Excalidraw 中展示。核心闭环：理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代。

## Workflow

1. **理解意图**：确定图表类型（流程图、架构图、时序图、思维导图、ER 图、泳道图等）、节点、连线关系和要强调的内容。类型与布局规范见 [references/diagram-templates.md](references/diagram-templates.md)。
2. **生成 `.excalidraw` JSON**：先读 [references/excalidraw-schema.md](references/excalidraw-schema.md) 了解 v2 结构，再按模板生成合法文件。默认输出到当前工作区，文件名建议 `output/<topic>-YYYYMMDD-HHMM.excalidraw`。
3. **校验**：运行 `python3 scripts/validate_excalidraw.py <file>`，修复所有 error 后再交付。
4. **实时预览**：启动 `node scripts/preview_server.js [<file>] [--open]`（默认端口 6060，预览页会轮询 API 实时刷新，模式参考 al1y/mcp-excalidraw）。之后每次生成或修改 `.excalidraw`，用 `node scripts/push_preview.js <file>` 推送，已打开的预览页约 1.5 秒内自动更新。交付前先看预览，检查元素是否重叠、文字是否溢出、连线是否绑定正确；发现问题直接修正后重新推送。
5. **静态渲染**（可选，出图）：需要 PNG/SVG 文件时运行 `node scripts/render_preview.js <file> --format both` 生成同目录预览文件；沙箱内无法起浏览器时自动降级为纯 SVG。
6. **打开与迭代**：运行 `node scripts/open_in_excalidraw.js <file>` 把画布推送到本地 Excalidraw（http://localhost:5001/）并打开浏览器；页面会自动刷新导入，用户可直接编辑。用户提出修改时增量更新元素（保持既有 `id` 不变，被替换的元素用新 `id`），不要整图重画。

## 质量规则

- 每个元素必须有唯一 `id`、正确的 `type` 和数值型 `x/y/width/height`。
- 文字标签用 `containerId` 绑定到图形（图形同时声明 `boundElements`），不要用独立文本框拼凑。
- 箭头用 `startBinding/endBinding` 绑定节点，保证移动节点时连线跟随。
- 默认配色：节点描边 `#1e1e1e`、填充 `#ffffff` 或模板色板，连线 `#868e96`；同图内色板保持一致。
- 文本宽度不超过所在图形宽度（经验值：宽度 ≈ 字号 × 中文字数 × 1.0），必要时放大图形或换行。
- 同一逻辑分区的元素放入同一 `groupIds` 分组；顶层框架用 `frame` 元素承载标题区。

## Resources

### scripts/

- `validate_excalidraw.py`：校验 `.excalidraw` 文件结构与引用完整性，返回非零退出码表示有错误。
- `preview_server.js`：实时预览服务器（轮询 API 模式）。启动后 `push_preview.js` 推送的图会实时出现在预览页，无需写本地 Excalidraw web root。
- `push_preview.js`：把 `.excalidraw` 推送到运行中的预览服务器。
- `render_preview.js`：无头浏览器渲染 `.excalidraw` 为 PNG（和 SVG），供 agent 自检与交付。
- `open_in_excalidraw.js`：把 `.excalidraw` 推送到本地 Excalidraw 的 `scene.excalidraw` 并打开 http://localhost:5001/，供用户即时编辑。

### references/

- `excalidraw-schema.md`：v2 JSON 结构、元素字段、箭头绑定、分组、文本与图片的完整说明。
- `diagram-templates.md`：**10 种**图表模板（流程图、架构图、时序图、思维导图、泳道图、ER图、层级图、关系图、对比图、时间线图），含完整 JSON 示例与布局参数。
- `color-palette.md`：按语义组织的颜色体系（8 种语义填充色 + 3 种分层背景色），以及 4 套一键切换主题（default/sketch/blueprint/minimal）。
- `element-templates.md`：元素级构建块模板，按需组合生成（rectangle / ellipse / diamond / arrow / text / line / frame），标注必填字段与默认值。
- `tech-node-templates.md`：**50+** 常见技术组件（Kafka / PostgreSQL / Redis / K8s 等）预定义样式，架构图生成时自动匹配形状/颜色。
- `visual-patterns.md`：常见关系模式模板（扇出、汇聚、时间线、分组、请求-响应、流水线、星型、矩阵、循环），每种模式提供 DSL 描述与 JSON 骨架。
- `animation-template.md`：动画关键帧模板，支持 `customData.animate` 字段，定义 7 级动画顺序规则，可拖入 excalidraw-animate 生成动画。
