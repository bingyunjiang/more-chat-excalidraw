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
4. **渲染预览**：运行 `node scripts/render_preview.js <file>` 生成同目录下的 PNG 预览。交付前先看预览，检查元素是否重叠、文字是否溢出、连线是否绑定正确；发现问题直接修正后重新渲染。
5. **打开与迭代**：运行 `node scripts/open_in_excalidraw.js <file>` 把画布推送到本地 Excalidraw（http://localhost:5001/）并打开浏览器；页面会自动刷新导入，用户可直接编辑。用户提出修改时增量更新元素（保持既有 `id` 不变，被替换的元素用新 `id`），不要整图重画。

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
- `render_preview.js`：无头浏览器渲染 `.excalidraw` 为 PNG（和 SVG），供 agent 自检与交付。
- `open_in_excalidraw.js`：把 `.excalidraw` 推送到本地 Excalidraw 的 `scene.excalidraw` 并打开 http://localhost:5001/，供用户即时编辑。

### references/

- `excalidraw-schema.md`：v2 JSON 结构、元素字段、箭头绑定、分组、文本与图片的完整说明。
- `diagram-templates.md`：六类常见图表的布局模板、色板与最小示例。
