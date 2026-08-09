---
name: more-chat-excalidraw
description: 通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。当用户想"画一张图/流程图/架构图/时序图/思维导图"、要求把对话内容做成 Excalidraw 图表、修改已有的 .excalidraw 文件、或让 agent 用 Excalidraw 呈现思路时使用。覆盖 .excalidraw v2 JSON 生成、结构校验、SVG/PNG 预览渲染，以及打开本地 Excalidraw（http://localhost:5001/）查看与迭代。
---

# Chat-to-Excalidraw

## Overview

把用户的自然语言转化为可打开的 `.excalidraw` v2 画布文件，并在本地 Excalidraw 中展示。核心闭环：理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代。

本 skill 完全自包含，不依赖其他 skill。编辑器/渲染 bundle 与 MCP SDK 均从本 skill 内
（scripts/web/、scripts/render-bundle/）加载；可选外部依赖仅有 Playwright（渲染）、
Graphviz（自动布局）、本地 Excalidraw 应用（打开画布）。

## Workflow

1. **理解意图**：识别要强调的是步骤、角色、系统结构、消息先后、时间演进还是因果分析。运行 `python3 scripts/template_selector.py --choices "<意图>"` 获得面向用户的选择菜单；完整机器结果使用 `--recommend`。模板分类见 [references/template-choice-guide.md](references/template-choice-guide.md)，布局细节见 [references/diagram-templates.md](references/diagram-templates.md)。
2. **主动共同选型**：若用户没有明确 template/theme/sketchStyle，先给出 1 个推荐组合和最多 2 个差异明显的备选项，只集中确认一次；让用户回复序号、模板名或“你直接选”。只明确模板时仅确认手绘风格，只明确风格时仅确认模板；模板与风格两者均明确，或用户授权直接选择时，才不重复追问。最终用一句话说明采用的 `template + sketchStyle` 和理由。不要向用户倾倒 10 个内部 key；CLI 始终非交互，由 Agent 负责对话。
3. **生成结构化文案（IR）**：把用户意图整理为 IR 中间格式（见 [references/ir-format.md](references/ir-format.md)），包含 nodes/edges/groups/template/theme/sketchStyle。IR 独立于 Excalidraw，便于后续迭代与版本化。需要视觉追溯时可声明 [visual-distillation-contract.md](references/visual-distillation-contract.md) 中的 `visual_contract`。
4. **IR → `.excalidraw` JSON**：运行 `python3 scripts/ir_to_excalidraw.py <ir.json> --output output/<topic>.excalidraw` 自动完成布局、元素生成、箭头绑定与配色。也可手工按 [references/excalidraw-schema.md](references/excalidraw-schema.md) 与元素模板生成。默认输出到当前工作区，文件名建议 `output/<topic>-YYYYMMDD-HHMM.excalidraw`。
5. **校验**：运行 `python3 scripts/validate_excalidraw.py <file>`，修复所有 error 后再交付。历史场景若出现箭头 `width/height` 与 `points` 范围不一致，使用 `--fix-arrow-geometry` 确定性修复后再加 `--visual --fail-on-warning` 验收。
6. **实时预览**：启动 `node scripts/preview_server.js [<file>] [--open]`（默认端口 6060，预览页会轮询 API 实时刷新，模式参考 al1y/mcp-excalidraw）。之后每次生成或修改 `.excalidraw`，用 `node scripts/push_preview.js <file>` 推送，已打开的预览页约 1.5 秒内自动更新。交付前先看预览，检查元素是否重叠、文字是否溢出、连线是否绑定正确；发现问题直接修正后重新推送。需要浏览器内编辑时访问 `http://localhost:6060/editor`（完整 Excalidraw 编辑器，编辑后点"保存到服务器"写回文件）；需要分步讲解动画时访问 `http://localhost:6060/animate`（按 customData.animate 顺序逐帧播放）。
7. **静态渲染**（可选，出图）：需要 PNG/SVG/PDF 文件时运行 `node scripts/render_preview.js <file> --format both` 生成同目录预览文件；PNG/PDF 只截取画布边界，不包含验证页眉或视口空白；只自动使用 Playwright `chrome-headless-shell`，不启动完整 GUI Chrome；沙箱内无法起安全浏览器时自动降级为纯 SVG。可用 `node scripts/render_preview.js --check-browser` 查看选择结果。
8. **打开与迭代**：运行 `node scripts/open_in_excalidraw.js <file>` 把画布推送到本地 Excalidraw（http://localhost:5001/）并打开浏览器；页面会自动刷新导入，用户可直接编辑。用户提出修改时增量更新元素（保持既有 `id` 不变，被替换的元素用新 `id`），不要整图重画。

## 质量规则

- 每个元素必须有唯一 `id`、正确的 `type` 和数值型 `x/y/width/height`。
- 文字标签用 `containerId` 绑定到图形（图形同时声明 `boundElements`），不要用独立文本框拼凑。
- 箭头用 `startBinding/endBinding` 绑定节点，保证移动节点时连线跟随。
- 默认配色：节点描边 `#1e1e1e`、填充 `#ffffff` 或模板色板，连线 `#868e96`；同图内色板保持一致。
- 文本宽度不超过所在图形宽度（经验值：宽度 ≈ 字号 × 中文字数 × 1.0），必要时放大图形或换行。
- 同一逻辑分区的元素放入同一 `groupIds` 分组；顶层框架用 `frame` 元素承载标题区。
- 交付前必须实际查看 PNG 或 SVG；不得仅凭 JSON 校验宣称视觉完成。检查画布比例、文字溢出、回路穿越节点、阶段对齐以及导出是否混入调试页眉/大面积空白。
- 视觉修复时先判断用户喜欢的是哪种图的气质。内容地图、机理图谱和研究板应优先保留有机手绘布局，可用编号、色块和少量引导线建立阅读顺序；不要为了“有章法”把它硬改成拥挤的网格流程图。装饰性线条或框体局部遮挡可以接受，但任何箭头标签、批注或线条都不得遮住节点正文。
- 箭头 `width/height` 必须匹配 `points` 的真实几何范围；多段正交线不得使用会被恢复为大弧线的圆角配置。
- 当用户要求突出 Excalidraw 风格时，优先使用关系图、概念图或研究分析板，而不是退化成普通流程图。组合 `note/callout/topic`、双语多行文字、分组框和语义箭头。
- 节点可用 `font: hand|sans|mono|long-cang|ma-shan-zheng|liu-jian-mao-cao` 建立字体层级。**所有 10 种模板和 4 套主题中的中文**默认使用本地 Excalidraw（`http://localhost:5001/`）提供的 `Ma Shan Zheng`（fontFamily 11），可切换 `Long Cang`（12）或 `Liu Jian Mao Cao`（13）；default/sketch 的纯英文继续使用 Virgil，minimal/blueprint 的纯英文继续使用 Helvetica。IR 顶层 `cjkFontFamily` / `cjkFontFallbacks` 可覆盖中文字体栈。含中文文本不得被通用 `font: hand|sans|mono` 覆盖回英文/等宽字体；只有显式中文字体名才切换中文字体。字体仅引用用户已有的本地 Excalidraw 资产、不随 skill 重复分发；服务不可用时回退本机手写字体。交付前必须目检 PNG，确认中文不是系统无衬线回退。边可用 `curve`、`curveOffset`、`color`、`strokeWidth`、`style: dashed`、`startArrowhead/endArrowhead` 表达因果、反馈和证据关系；手绘主题边标签默认 32px，并可用 `labelFontSize` / `labelOffset` 调整，避免 trigger/detect 一类注记小到不可读或压在线上。

## Resources

## 安装、复现与平台边界

```bash
npm ci --prefix scripts/web
npm run build:all --prefix scripts/web
node scripts/check_web_lock.mjs
```

相同 IR 默认生成字节级稳定场景；只有显式设置 `EXCALIDRAW_UPDATED` 才控制更新时间。`--library` 默认使用 skill 自带的 self-authored MIT 核心组件，无需下载；只有需要自定义组件时才使用 `--library-dir <目录>` 显式覆盖。`open_in_excalidraw.js` 仅在 macOS 自动使用 launchd 启动服务，浏览器打开按 macOS/Linux/Windows 分别使用 `open`/`xdg-open`/`cmd.exe start`。

严格视觉验收可加 `--visual --fail-on-warning`；默认校验仍只报告 warning，不破坏兼容性。

### scripts/

- `template_selector.py`：模板选择器。`--guide` 按四类汇整 10 种模板；`--choices "<意图>"` 输出可直接展示给用户的最多三项菜单；`--recommend` 输出完整候选卡、推荐理由、置信度和确认条件；原有 `--list/--info/--params` 继续兼容。
- `ir_to_excalidraw.py`：IR → Excalidraw JSON 转换器。`--example thermal-runaway/battery-thermal/fea/flowchart/architecture/mindmap` 生成内置示例；`--validate` 转换后自动校验（含视觉质量检查）；`--layout dot|neato|twopi` 使用 Graphviz 自动布局（借鉴 drawmode）；`--icons` 注入云架构技术图标（自包含 SVG）。支持手绘双语分析板、便签与批注框、曲线/彩色/粗细/虚线箭头、白底极简四列工程架构、四阶段横向 FEA 泳道、10 种模板布局和 4 套主题。所有模板/主题的中文统一使用 Ma Shan Zheng 等中文手写字体；纯英文按主题保留 Virgil 或 Helvetica，预览/导出与 `localhost:5001` 原生字体编号对齐。
- `icon_library.py`：自包含云架构图标库（借鉴 excalidraw-icons-mcp）。67 个技术图标按类型配色（数据库/队列/网关/计算/存储/缓存/监测/CI/CD/基础设施），`--list` 列出、`--svg <技术>` 输出、`--json` 导出注册表。
- `render_animation_gif.py`：关键帧动画 → GIF 导出（借鉴 excalimate）。读取 `customData.animate` 顺序，按帧渲染合成 GIF（依赖 pillow，SVG→PNG 用 cairosvg 或 rsvg-convert）。
- `mermaid_to_excalidraw.js`：Mermaid → Excalidraw 转换（flowchart/sequenceDiagram 子集）。解析为 IR 后复用 ir_to_excalidraw.py 完成布局。
- `merge_excalidraw.py`：增量编辑与迭代。`merge` 合并新旧场景（保留旧 id）；`patch --set id.field=value --move id:dx,dy` 微调；`restore` 从 `output/history/` 备份回退。
- `knowledge_graph.py`：知识图谱架构生成（借鉴 excalidraw-architect-mcp）。从 JSON 或 `entity:/rel:` 文本提取实体/关系 → IR → 架构图，自动分层。
- `mcp_server.mjs`：MCP 服务器（借鉴 excalidraw/excalidraw-mcp）。暴露 generate_diagram / validate_diagram / push_preview / list_templates 四个工具，供 MCP 客户端（stdio）调用。运行：`node scripts/mcp_server.mjs`。
- `list_templates.js`：模板列表与预览。`--json` 输出元数据；`--preview <模板> [--out 目录]` 渲染 10 种模板的 SVG 预览图。
- `validate_excalidraw.py`：校验 `.excalidraw` 文件结构与引用完整性；`--fix-arrow-geometry` 可按 `points` 精确修正旧箭头的 `width/height`，返回非零退出码表示仍有错误。
- `preview_server.js`：实时预览服务器（轮询 API 模式）。启动后 `push_preview.js` 推送的图会实时出现在预览页，无需写本地 Excalidraw web root。
- `push_preview.js`：把 `.excalidraw` 推送到运行中的预览服务器。
- `render_preview.js`：无头浏览器渲染 `.excalidraw` 为 PNG（和 SVG），供 agent 自检与交付。
- `open_in_excalidraw.js`：把 `.excalidraw` 推送到本地 Excalidraw 的 `scene.excalidraw` 并打开 http://localhost:5001/，供用户即时编辑。

### references/

- `excalidraw-schema.md`：v2 JSON 结构、元素字段、箭头绑定、分组、文本与图片的完整说明。
- `template-choice-guide.md`：面向用户的四类模板目录、模板—手绘风格组合和一次确认交互协议。
- `diagram-templates.md`：**10 种**图表模板（流程图、架构图、时序图、思维导图、泳道图、ER图、层级图、关系图、对比图、时间线图），含完整 JSON 示例与布局参数。
- `color-palette.md`：按语义组织的颜色体系（8 种语义填充色 + 3 种分层背景色），以及 4 套一键切换主题（default/sketch/blueprint/minimal）。
- `element-templates.md`：元素级构建块模板，按需组合生成（rectangle / ellipse / diamond / arrow / text / line / frame），标注必填字段与默认值。
- `tech-node-templates.md`：**50+** 常见技术组件（Kafka / PostgreSQL / Redis / K8s 等）预定义样式，架构图生成时自动匹配形状/颜色。
- `visual-patterns.md`：常见关系模式模板（扇出、汇聚、时间线、分组、请求-响应、流水线、星型、矩阵、循环），每种模式提供 DSL 描述与 JSON 骨架。
- `animation-template.md`：动画关键帧模板，支持 `customData.animate` 字段，定义 7 级动画顺序规则，可拖入 excalidraw-animate 生成动画。
- `ir-format.md`：IR 中间格式定义——独立于 Excalidraw 的图表语义表示，是文案引擎与 JSON 生成器之间的标准接口（19 种节点类型、边/分组/模板专用字段、转换规则）。
- `sketch-style-catalog.md`、`handdrawn-visual-rules.md`：sketch preset 目录与 render→look→targeted fix 验收规则。
- 本地编辑器边界：localhost:5001 可能自动 fit 到顶部并被浮动工具栏覆盖；正式验收以 PNG/SVG 为准，必要时在编辑器内手动平移画布。
- `visual-distillation-contract.md`：可选视觉蒸馏契约，定义决定性事实、来源映射、边界、布局信号、视觉家族及 proposed/confirmed 状态。
