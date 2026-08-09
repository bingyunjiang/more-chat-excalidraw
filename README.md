[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-6B46F7?logo=anthropic&logoColor=white)](https://github.com/bingyunjiang/more-chat-excalidraw)
[![Codex](https://img.shields.io/badge/Codex-Skill-0B1120?logo=openai&logoColor=white)](https://github.com/bingyunjiang/more-chat-excalidraw)
[![Hermes](https://img.shields.io/badge/Hermes-Skill-FF6B35)](https://github.com/nousresearch/hermes-skills)
[![Platform](https://img.shields.io/badge/macOS_|_Windows_|_Linux-lightgrey?logo=apple)]()

> **作者 / Author：** Dr. Jiang（Bingyun Jiang）　|　**微信 / WeChat：** Bingyunjiang　|　**邮箱 / Email：** bingyunjiang@qq.com　|　**GitHub：** [bingyunjiang/more-chat-excalidraw](https://github.com/bingyunjiang/more-chat-excalidraw)

# More Chat Excalidraw

把自然对话变成可编辑的 Excalidraw 画布  
Turn natural conversation into editable Excalidraw canvases

[![Version](https://img.shields.io/badge/version-v0.0.1-2f6feb)](#版本历史)
[![License](https://img.shields.io/badge/license-MIT-1f883d)](./LICENSE)
[![Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-8250df)](#项目表头)
[![Language](https://img.shields.io/badge/language-ZH%20primary%20%7C%20EN-f59e0b)](#项目表头)
[![Tests](https://img.shields.io/badge/tests-e2e%20suite-2f9e44)](scripts/test_e2e.sh)

**关键词 / Keywords：** Excalidraw · 流程图 · 架构图 · 时序图 · 思维导图 · 知识图谱 · Mermaid · Graphviz · 实时预览 · MCP · IR 中间格式 · 增量编辑 · 关键帧动画 · 本地优先 · auditable workflow

## More 系列索引

`more-*` 是一组强调过程透明、来源可追溯和结果可复核的 AI 工作流项目。

每个项目都独立安装、独立运行、独立验收；下面的索引用于选对工具，不表示这些 skill 会自动互相调用或共享项目状态。

| 项目 | 核心用途 |
| --- | --- |
| [more-paper-workflow](https://github.com/bingyunjiang/more-paper-workflow) | 论文定题、文献检索、证据组织、写作与引用审计 |
| [more-sci-figure](https://github.com/bingyunjiang/more-sci-figure) | 科研图表数据提取、人工复核、论文级重绘与交付验证 |
| [more-news-briefing](https://github.com/bingyunjiang/more-news-briefing) | 新闻与行业信息收集、去重、排序、核验和简报生成 |
| [more-comic-digitizer](https://github.com/bingyunjiang/more-comic-digitizer) | 儿童手绘漫画数字化、审核、共创与电子出版 |
| **[more-chat-excalidraw](https://github.com/bingyunjiang/more-chat-excalidraw)**（当前项目） | 自然对话生成、预览、打开和迭代编辑 Excalidraw 画布 |
| [more-excalidraw-feishu](https://github.com/bingyunjiang/more-excalidraw-feishu) | Excalidraw 画布到飞书可编辑白板的转换 |
| [more-feishu-excalidraw](https://github.com/bingyunjiang/more-feishu-excalidraw) | 飞书文档到 Excalidraw 画布的反向转换 |

系列主页：[github.com/bingyunjiang](https://github.com/bingyunjiang)

## 项目表头

| 字段 | 内容 |
| --- | --- |
| 名称 | `more-chat-excalidraw` |
| 版本 | `v0.0.1` |
| 类型 | AI Agent Skill / 图表生成技能 |
| 场景 | 流程图 / 架构图 / 时序图 / 思维导图 / ER 图 / 泳道图 / 层级图 / 关系图 / 对比图 / 时间线图 / 知识图谱 |
| 本地运行 | macOS / Windows / Linux，Node.js 18+，Python 3 |
| 关键词 | `Excalidraw`, `diagram`, `flowchart`, `architecture`, `Mermaid`, `Graphviz`, `MCP`, `IR`, `animation`, `real-time preview` |

## 它解决什么问题

把会议记录、思路草稿或技术方案变成一张能编辑、能分享的 Excalidraw 画布，常见做法是手动画或用其他工具导出。但手动画费时，截图不可编辑，通用导出丢失结构与手绘质感。

| 常见做法 | More Chat Excalidraw |
| --- | --- |
| 手动绘制，费时费力 | 自然语言对话 → 结构化 IR → 自动布局成图 |
| 截图分享，不可编辑 | 交付原生 `.excalidraw` v2 JSON，随时可编辑 |
| 结构混乱、配色随意 | 10 种模板 + 语义色板 + 4 套主题，一键切换 |
| 修改要整图重画 | 增量编辑保留元素 id，只改变化的部分 |
| 无法衔接已有工具 | Mermaid 导入、知识图谱生成、MCP 协议调用 |

## 核心闭环

```text
自然语言/文档/Mermaid/知识图谱
  → 理解意图（template_selector 推荐模板）
  → 结构化 IR（references/ir-format.md）
  → ir_to_excalidraw.py（布局 + 配色 + 绑定 + 动画元数据）
  → validate_excalidraw.py（结构 + 引用 + 视觉质量门）
  → preview_server.js（SVG 轮询预览 / 内嵌编辑器 / 动画播放）
  → render_preview.js（PNG / SVG / PDF 导出）
  → open_in_excalidraw.js（打开本地 Excalidraw 编辑）
```

## 你可以用它做什么

### 1. Excalidraw 手绘分析板

```bash
python3 scripts/ir_to_excalidraw.py --example thermal-runaway --output examples/thermal-runaway.excalidraw --validate
node scripts/render_preview.js examples/thermal-runaway.excalidraw --format both
```

该案例不是普通流程图，而是“电芯热失控：触发—机理—防护”研究画布：中文明确使用本地 Excalidraw 已有的 `Long Cang`（龙藏体），英文使用 Virgil；配合便签/批注框、红绿蓝语义箭头、虚线机理链、曲线汇聚与发散箭头共同表达分析关系。IR 节点可用 `font: long-cang|ma-shan-zheng|liu-jian-mao-cao` 选择 `localhost:5001` 内置字体，也可用顶层 `cjkFontFamily` / `cjkFontFallbacks` 覆盖回退顺序；字体文件不会被重复复制或分发。

### 2. 白底极简工程架构示例

```bash
python3 scripts/ir_to_excalidraw.py --example battery-thermal --output examples/battery-thermal.excalidraw --validate
node scripts/render_preview.js examples/battery-thermal.excalidraw --format both
```

该案例展示电池包热管理多物理场仿真架构，采用工况与边界、多物理场模型、试验校核、设计决策四列布局；极简主题使用无衬线字体、低饱和分区和克制连线。

### 3. 工程有限元流程示例

可直接对 Agent 说：

> 使用 more-chat-excalidraw 绘制一张结构力学有限元仿真流程图，包含需求与工况、CAD 几何清理、材料本构、单元类型、网格划分、边界与载荷、接触/连接、求解器与步长、收敛判断、结果提取、网格无关性、试验或解析验证、结果归档；画出不收敛、网格未独立和验证失败的回路，使用蓝图主题，严格校验并输出 Excalidraw、PNG、SVG 和 PDF。

也可直接运行内置示例：

```bash
python3 scripts/ir_to_excalidraw.py --example fea --output examples/fea-workflow.excalidraw --validate
```

该示例采用四阶段横向工程泳道，覆盖工况、几何、材料本构、单元/网格、边界与接触、求解收敛、网格无关性、验证及报告归档，并将失败回路布置在主流程之外。

### 4. 一句话生成图表

对 Agent 说"画一个微服务架构图"，自动推荐模板、生成 IR、完成布局配色并输出 `.excalidraw`：

```bash
python3 scripts/template_selector.py --recommend "画一个微服务架构图"
python3 scripts/ir_to_excalidraw.py --example architecture --output output/arch.excalidraw --validate
```

### 2. 从 Mermaid 或知识图谱生成

```bash
# Mermaid → Excalidraw（flowchart / sequenceDiagram 子集）
node scripts/mermaid_to_excalidraw.js --string "graph TD; A-->B" --output output/mmd.excalidraw

# 知识图谱 → 架构图（实体/关系自动分层）
python3 scripts/knowledge_graph.py --text arch.txt --output output/kg.excalidraw
```

### 3. 自动布局、主题与图标

```bash
# Graphviz 自动布局（可选）：dot 层次 / neato 力导向 / twopi 树形
python3 scripts/ir_to_excalidraw.py --example architecture --layout dot --output output/arch.excalidraw

# 4 套主题一键切换：default / sketch / blueprint / minimal
python3 scripts/ir_to_excalidraw.py --example flowchart --theme blueprint --output output/flow.excalidraw

# 云架构技术图标（自包含 67 个 SVG，无需外部资源）
python3 scripts/ir_to_excalidraw.py --example architecture --icons --output output/arch-icons.excalidraw
```

### 4. 实时预览、编辑与动画

```bash
node scripts/preview_server.js output/arch.excalidraw --open
```

- `http://localhost:6060/`：SVG 轮询实时预览（`push_preview.js` 推送，约 1.5s 刷新）
- `http://localhost:6060/editor`：内嵌完整 Excalidraw 编辑器，编辑后"保存到服务器"写回本地
- `http://localhost:6060/animate`：关键帧动画逐帧播放（自动注入 `customData.animate`）
- `python3 scripts/render_animation_gif.py <file.excalidraw>`：导出动画 GIF（[示例](output/animation-demo.gif)）

### 5. 增量编辑与回退

```bash
python3 scripts/merge_excalidraw.py patch output/flow.excalidraw --set 'n3.backgroundColor=#ffc9c9' --move 'n5:20,0'
python3 scripts/merge_excalidraw.py restore output/flow.excalidraw output/history/backup-*.excalidraw
```

### 6. 导出与交付

```bash
node scripts/render_preview.js output/arch.excalidraw /tmp/out --format both   # PNG + SVG
node scripts/render_preview.js output/arch.excalidraw /tmp/out --format pdf   # PDF
```

### 7. 通过 MCP 协议调用

```bash
node scripts/mcp_server.mjs
```

暴露 `generate_diagram` / `validate_diagram` / `push_preview` / `list_templates` 四个工具，供 Codex 等 MCP 客户端（stdio）直接调用。

## 支持的图表类型

| 类型 | 说明 |
| --- | --- |
| 流程图 Flowchart | 纵向/横向步骤 + 菱形决策 + 箭头 |
| 架构图 Architecture | 分层：用户层 → 应用层 → 服务层 → 数据层 |
| 时序图 Sequence | 角色竖线 + 横向箭头消息 |
| 思维导图 Mind Map | 中心主题 + 一级/二级分支 |
| 泳道图 Swimlane | 水平泳道按角色分区，流程穿越泳道 |
| ER 图 ERD | 实体矩形 + 关系菱形 + 基数标注 |
| 层级图 Hierarchy | 自上而下树形结构，适合组织/系统拆解 |
| 关系图 Relationship | 节点 + 连线 + 关系标注，无严格方向 |
| 对比图 Comparison | 左右两栏或表格，标明比较维度 |
| 时间线图 Timeline | 水平时间轴 + 关键节点 + 事件标注 |

## 前置条件

- **Node.js 18+**、**Python 3**
- **Playwright**（可选，PNG/PDF 高质量渲染）：`npm install -g playwright`
- **Graphviz**（可选，自动布局）：`brew install graphviz`
- **本地 Excalidraw**（可选，打开画布）：`http://localhost:5001/`

本 skill 完全自包含，不依赖其他 skill。编辑器与渲染 bundle 源码在 `scripts/web/`
（@excalidraw/excalidraw 0.18.1 + React 19，`cd scripts/web && npm run build`），
MCP SDK/zod 从本 skill 内 `scripts/web/node_modules` 加载。

### 安装与构建

```bash
npm ci --prefix scripts/web
npm run build:all --prefix scripts/web
node scripts/check_web_lock.mjs
```

CI 会真实执行依赖安装、editor/render bundle 构建、MCP 工具调用与 e2e suite。Playwright、Graphviz、本地 Excalidraw 和端口服务均是可选环境能力；沙箱可能阻止端口、浏览器或 web root 写入，此时保留 SVG fallback 并明确报告环境受阻。生成默认字节级可复现；`EXCALIDRAW_UPDATED` 可显式控制更新时间。`--library` 默认使用内置 self-authored MIT 组件、无需下载；自定义或第三方 Library 仅可通过 `--library-dir` 显式覆盖。

需要把视觉警告当作质量门时使用 `python3 scripts/validate_excalidraw.py <file> --visual --fail-on-warning`；默认模式仍兼容仅报告 warning。

## 快速开始

```bash
# 1. 模板选择：根据意图推荐最佳模板
python3 scripts/template_selector.py --recommend "画一个微服务架构图"

# 2. IR → Excalidraw（推荐生成路径）
python3 scripts/ir_to_excalidraw.py --example flowchart --output output/flow.excalidraw --validate

# 3. 实时预览
node scripts/preview_server.js output/flow.excalidraw --open

# 4. 推送更新
node scripts/push_preview.js output/flow.excalidraw

# 5. 校验 + 渲染
python3 scripts/validate_excalidraw.py output/flow.excalidraw --visual
node scripts/render_preview.js output/flow.excalidraw /tmp/out --format both

# 6. 打开本地 Excalidraw 编辑
node scripts/open_in_excalidraw.js output/flow.excalidraw

# 7. 端到端测试
bash scripts/test_e2e.sh
```

## 沙箱兼容性

- **preview_server.js**：需要绑定端口，沙箱内运行需 escalation；启动后一切写入都在内存和预览页，不碰本地 Excalidraw web root
- **render_preview.js**：PNG/PDF 默认裁切到画布边界，不输出验证页眉和视口空白；沙箱内无法启动 HTTP 服务器或 Chromium 时，自动 fallback 到 SVG 渲染
- **浏览器安全**：PNG/PDF 渲染只自动选择 Playwright 的 `chrome-headless-shell`，不启动完整的 “Google Chrome for Testing” GUI 应用；可用 `node scripts/render_preview.js --check-browser` 查看选择结果
- **open_in_excalidraw.js**：沙箱内无法写入 web root 时，给出明确提示和手动操作命令（exit code 3）
- **ir_to_excalidraw.py / validate_excalidraw.py**：纯 Python 标准库，沙箱内可直接运行

## 质量与验证

- **结构校验**：元素 id 唯一、字段类型、引用完整性（boundElements / containerId / frameId / 箭头绑定交叉检查）
- **视觉质量门**：`--visual` 检查元素重叠、悬空箭头、布局密度
- **e2e 测试**：`bash scripts/test_e2e.sh` 覆盖生成、校验、渲染、预览、编辑器、保存、多画布、动画、Mermaid、知识图谱、Graphviz、增量编辑、MCP、确定性与 Library visual；具体结果以当前环境输出为准
- **CI**：GitHub Actions（validate + smoke + e2e），见 `.github/workflows/ci.yml`

## 版本历史

| 版本 | 日期 | 要点 |
| --- | --- | --- |
| v0.0.1 | 2026-08-08 | 初始开发版：自然对话生成 Excalidraw 画布；持续补充手绘双语分析板、显式中文手写字体、视觉提炼契约、Library、工程案例与 strict 视觉回归，版本号保持不变。 |

详细变更见 [CHANGELOG.md](CHANGELOG.md)。

## 许可

MIT
