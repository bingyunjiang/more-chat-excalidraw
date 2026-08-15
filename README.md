<p align="center">
  <strong>More Chat Excalidraw</strong><br>
  <em>把自然语言变成可编辑、可验证、可交付的 Excalidraw 图表</em>
</p>

<p align="center">
  <a href="https://github.com/bingyunjiang/more-chat-excalidraw/releases/tag/v0.1.0">v0.1.0</a> ·
  <a href="https://github.com/bingyunjiang/more-chat-excalidraw/blob/main/LICENSE">MIT License</a> ·
  <a href="https://github.com/bingyunjiang/more-chat-excalidraw/actions">CI</a> ·
  <a href="https://github.com/bingyunjiang/more-chat-excalidraw/issues">Issues</a>
</p>

<p align="center">
  <a href="https://github.com/bingyunjiang/more-chat-excalidraw">
    <img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815.png" alt="more-paper-workflow 真实案例：六帧 Excalidraw 视频白板" width="100%">
  </a>
</p>

<p align="center"><sub>真实案例预览：把论文工作流拆成可讲解、可编辑、可逐帧交付的 Excalidraw 白板。点击图片查看原图。</sub></p>

<p align="center">
  <a href="#真实案例">查看案例</a> ·
  <a href="#3-分钟开始">3 分钟开始</a> ·
  <a href="#它能交付什么">查看能力</a>
</p>

<blockquote>
  <strong>作者 / Author：</strong> Dr. Jiang（Bingyun Jiang）<br>
  微信：Bingyunjiang　·　邮箱：bingyunjiang@qq.com　·　GitHub：<a href="https://github.com/bingyunjiang">bingyunjiang</a>
</blockquote>

## 它是什么

More Chat Excalidraw 是一个本地优先的 AI Agent Skill：你只需要描述想表达的内容，它就能完成模板选择、结构化、布局、校验、预览和编辑交付。

```text
一句话意图
  → 选择表达方式
  → 结构化 IR
  → 可编辑 Excalidraw v2
  → 结构 + 视觉质量门
  → SVG / PNG / PDF / 逐帧 storyboard
```

它解决的不是“画一个好看的截图”，而是把思路变成一份仍然可编辑、可追踪、可复核的图表资产。

## 为什么值得用

| 你遇到的问题 | More Chat Excalidraw 的回答 |
| --- | --- |
| 手动画图耗时，截图又不可编辑 | 自然语言 → IR → 原生 `.excalidraw` v2 |
| 图表结构混乱，模板选不对 | 根据意图推荐模板、主题和手绘气质 |
| 中英文混排容易失控 | 中文手写字体、英文层级、双语卡片规则统一 |
| 改一个节点要整图重画 | 增量编辑保留元素 id，只更新必要部分 |
| 交付前不知道哪里会出问题 | 结构校验、绑定检查、碰撞、安全区、字号和对比度审计 |
| 一张图讲不清完整过程 | 支持 16:9 video-storyboard、逐帧导出和讲解元数据 |

## 真实案例

上面的主图来自真实的 `more-paper-workflow` 工作流案例：将“梳理 → 选型 → 生成 → 校验 → 预览 → 交付”组织成 6 帧录屏白板。

它展示了：

- 中文手写字体与英文标题层级并存；
- 每个 frame 保持 16:9 安全边距；
- 研究流程、证据链、工具链和质量门放在同一套视觉叙事中；
- 同一份源资产可打开编辑，也可导出 PNG、SVG、PDF。

### 六帧画廊

<table>
  <tr>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-01.svg" alt="Frame 01：为什么需要可信论文工作流" width="100%"><br><sub>01 · WHY</sub></td>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-02.svg" alt="Frame 02：工作流闭环" width="100%"><br><sub>02 · WORKFLOW</sub></td>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-03.svg" alt="Frame 03：工具链与能力层" width="100%"><br><sub>03 · TOOLCHAIN</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-04.svg" alt="Frame 04：从研究到写作的交接" width="100%"><br><sub>04 · HANDOFF</sub></td>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-05.svg" alt="Frame 05：证据与状态" width="100%"><br><sub>05 · EVIDENCE</sub></td>
    <td align="center"><img src="examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815-frame-06.svg" alt="Frame 06：最终交付" width="100%"><br><sub>06 · DELIVERY</sub></td>
  </tr>
</table>

| 资产 | 用途 |
| --- | --- |
| [`.excalidraw` 白板](examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815.excalidraw) | 在 Excalidraw 中继续编辑 |
| [`PNG` 预览](examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815.png) | 快速查看完整画布 |
| [`SVG` 矢量图](examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815.svg) | 网页和矢量交付 |
| [`PDF` 文件](examples/more-paper-workflow-video-rich-sketch/more-paper-workflow-video-rich-sketch-20260815.pdf) | 汇报和归档 |
| [6 个逐帧 SVG](examples/more-paper-workflow-video-rich-sketch/) | README 画廊和逐帧讲解 |
| [案例说明](examples/more-paper-workflow-video-rich-sketch/README.md) | 查看来源与打开方法 |

你可以直接对 Agent 说：

> 梳理 more-paper-workflow 的实际工作流，制作 3–6 个 16:9 Excalidraw 视频分镜；每帧选择合适的图表模板，保留中文手绘字体、英文层级、提词器和严格视觉校验。

## 3 分钟开始

### 1. 准备环境

- Node.js 18+
- Python 3
- Playwright（可选，用于 PNG/PDF 高质量渲染）
- Graphviz（可选，用于自动布局）

```bash
npm ci --prefix scripts/web
npm run build:all --prefix scripts/web
```

### 2. 让 Agent 先选表达方式

```bash
python3 scripts/template_selector.py --recommend "画一个微服务架构图"
```

如果是录屏或逐帧讲解，直接说出交付目标：

```bash
python3 scripts/template_selector.py --recommend \
  "梳理论文工作流并制作 16:9 视频分镜"
```

选择器会把“内容模板”和“交付方式”分开处理，不会因为要录视频就强行套用某一种图表。

### 3. 生成并校验

```bash
# 普通图表
python3 scripts/ir_to_excalidraw.py \
  --example architecture \
  --output /tmp/architecture.excalidraw \
  --validate

# 真实 storyboard smoke fixture
python3 scripts/ir_to_excalidraw.py \
  examples/storyboard-smoke.ir.json \
  --output /tmp/storyboard.excalidraw \
  --validate

python3 scripts/validate_excalidraw.py \
  /tmp/storyboard.excalidraw \
  --visual --fail-on-warning
```

### 4. 预览、编辑和导出

```bash
# 本地实时预览与编辑
node scripts/preview_server.js /tmp/architecture.excalidraw --open

# SVG fallback：适合无浏览器或沙箱环境
node scripts/render_preview.js /tmp/storyboard.excalidraw /tmp/storyboard-render \
  --format svg --no-server --frames --contact-sheet

# 正式 PNG/PDF 交付：要求真实 native renderer 和 PNG
node scripts/render_preview.js /tmp/storyboard.excalidraw /tmp/storyboard-render \
  --format both --frames --contact-sheet --require-native --require-png
```

## 它能交付什么

### 10 种内容模板

| 类别 | 模板 |
| --- | --- |
| 流程与协作 | Flowchart、Swimlane |
| 系统与结构 | Architecture、ERD、Hierarchy |
| 交互与时间 | Sequence、Timeline |
| 分析与思考 | Mind Map、Relationship、Comparison |

### 4 种交付模式

| 交付模式 | 适合场景 |
| --- | --- |
| `single-diagram` | 一张图完成表达 |
| `long-canvas` | 横向展开、连续阅读 |
| `video-storyboard` | 录屏、逐帧讲解、16:9 分镜 |
| `presentation-board` | 汇报、演示、投屏阅读 |

### 多种输出与集成

- 原生 `.excalidraw` v2：可继续编辑、增量修改和复用；
- SVG / PNG / PDF：适合网页、汇报、论文和归档；
- Mermaid：导入 flowchart / sequenceDiagram 子集；
- Graphviz：dot / neato / twopi 自动布局；
- 知识图谱：从实体与关系描述生成架构图；
- MCP：通过 `generate_diagram`、`validate_diagram`、`push_preview`、`list_templates` 调用；
- 动画：关键帧播放与 GIF 导出。

## 可靠性不是最后再补的一步

每次交付都可以经过以下质量门：

1. 元素 id、类型、坐标和引用完整性；
2. 箭头与节点的绑定关系；
3. 文本互撞、箭线穿字、悬空箭头和布局密度；
4. 旋转后的安全区、视频字号和文字对比度；
5. native / fallback 渲染模式与 render manifest；
6. 同一 IR 的字节级确定性回归。

```bash
python3 scripts/validate_excalidraw.py <file.excalidraw> \
  --visual --fail-on-warning

bash scripts/test_e2e.sh --sandbox
```

在沙箱中无法监听端口或启动 Chromium 时，工具会明确标记 fallback，不把 fallback 结果冒充成正式 native PNG。

## 更多文档

- [Storyboard 交付规范](references/video-storyboard.md)
- [IR 中间格式](references/ir-format.md)
- [模板选择指南](references/template-choice-guide.md)
- [10 种图表模板](references/diagram-templates.md)
- [Excalidraw v2 schema](references/excalidraw-schema.md)
- [视觉蒸馏契约](references/visual-distillation-contract.md)
- [变更记录](CHANGELOG.md)
- [交接文档](HANDOFF.md)

## More 系列

More 系列强调过程透明、来源可追溯和结果可复核。相关项目包括：

- [more-paper-workflow](https://github.com/bingyunjiang/more-paper-workflow)：论文定题、检索、证据组织与引用审计；
- [more-sci-figure](https://github.com/bingyunjiang/more-sci-figure)：科研图表提取、重绘与交付验证；
- [more-news-briefing](https://github.com/bingyunjiang/more-news-briefing)：新闻与行业信息核验和简报；
- [more-comic-digitizer](https://github.com/bingyunjiang/more-comic-digitizer)：手绘漫画数字化与出版；
- [more-excalidraw-feishu](https://github.com/bingyunjiang/more-excalidraw-feishu)：Excalidraw 与飞书白板转换。

## 版本与许可

- 当前版本：`v0.1.0`，见 [GitHub Release](https://github.com/bingyunjiang/more-chat-excalidraw/releases/tag/v0.1.0)；
- 许可证：[MIT License](LICENSE)；
- 运行平台：macOS / Windows / Linux。
