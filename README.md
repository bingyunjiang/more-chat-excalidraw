# more-chat-excalidraw

通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。

核心闭环：**理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代**

## 快速开始

### 依赖

- Node.js ≥ 18
- Python 3
- Playwright（可选，用于高质量渲染）— `npm install -g playwright`
- 本地 Excalidraw（可选，用于打开画布）— `http://localhost:5001/`

### 使用

作为 Codex skill 使用：当用户要求"画一张图/流程图/架构图"时自动触发。

也可手动运行脚本：

```bash
# 模板选择：根据意图推荐最佳模板
python3 scripts/template_selector.py --recommend "画一个微服务架构图"

# IR → Excalidraw（推荐流程）：文案整理为 IR 后自动布局生成
python3 scripts/ir_to_excalidraw.py --example flowchart --output output/flow.excalidraw --validate

# Graphviz 自动布局（可选，brew install graphviz）：层次/力导向/树形
python3 scripts/ir_to_excalidraw.py --example architecture --layout dot --output output/arch.excalidraw

# Mermaid → Excalidraw（支持 flowchart/sequenceDiagram 子集）
node scripts/mermaid_to_excalidraw.js --string "graph TD; A-->B" --output output/mmd.excalidraw

# 增量编辑：合并/微调/回退
python3 scripts/merge_excalidraw.py patch output/flow.excalidraw --set 'n3.backgroundColor=#ffc9c9' --move 'n5:20,0'

# 知识图谱 → 架构图：从实体/关系描述自动分层生成
python3 scripts/knowledge_graph.py --text arch.txt --output output/kg.excalidraw

# MCP 服务器（stdio，供 agent 调用）：node scripts/mcp_server.mjs
# 工具：generate_diagram / validate_diagram / push_preview / list_templates

# 列出/预览模板（--preview 渲染 SVG）
node scripts/list_templates.js --preview flowchart

# 校验 .excalidraw 文件
python3 scripts/validate_excalidraw.py output/fixture-flowchart.excalidraw

# 实时预览（推荐）：启动预览服务器并打开浏览器
node scripts/preview_server.js --open

# 推送图表到预览页（约 1.5 秒内实时更新）
node scripts/push_preview.js output/fixture-flowchart.excalidraw

# 渲染为 PNG + SVG
node scripts/render_preview.js output/fixture-flowchart.excalidraw output/ --format both

# 仅输出 SVG（不依赖 HTTP 服务器）
node scripts/render_preview.js output/fixture-flowchart.excalidraw output/ --format svg --no-server

# 推送到本地 Excalidraw 并打开浏览器
node scripts/open_in_excalidraw.js output/fixture-flowchart.excalidraw

# 检查 Excalidraw 服务是否可达
node scripts/open_in_excalidraw.js --check-only

# 运行端到端测试
bash scripts/test_e2e.sh
```

## 项目结构

```
├── SKILL.md                          # Skill 定义（工作流、质量规则）
├── ROADMAP.md                        # 开发大纲与里程碑
├── README.md                         # 本文件
├── package.json                      # npm 脚本与依赖声明
├── agents/
│   └── openai.yaml                   # Codex 接口定义
├── references/
│   ├── excalidraw-schema.md          # v2 JSON 结构速查
│   ├── ir-format.md                  # IR 中间格式（文案引擎 ↔ JSON 生成器接口）
│   ├── diagram-templates.md          # 10 种图表模板（含完整 JSON 示例）
│   ├── color-palette.md              # 语义色板与 4 套主题系统
│   ├── element-templates.md          # 元素级构建块模板
│   ├── tech-node-templates.md        # 50+ 技术组件预定义样式
│   ├── visual-patterns.md            # 9 种视觉模式模板
│   └── animation-template.md         # 动画关键帧模板
├── scripts/
│   ├── template_selector.py          # 模板选择器（意图推荐 + 参数调整）
│   ├── ir_to_excalidraw.py           # IR → Excalidraw JSON 转换器（自动布局+配色+动画元数据）
│   ├── mermaid_to_excalidraw.js      # Mermaid → Excalidraw（flowchart/sequence 子集）
│   ├── merge_excalidraw.py           # 增量编辑：merge/patch/restore
│   ├── knowledge_graph.py            # 知识图谱 → 架构图（实体/关系自动分层）
│   ├── list_templates.js             # 模板列表与 SVG 预览
│   ├── validate_excalidraw.py        # 校验 .excalidraw 结构与引用完整性
│   ├── preview_server.js             # 实时预览服务器（轮询 API 模式）
│   ├── push_preview.js               # 推送 .excalidraw 到预览服务器
│   ├── render_preview.js             # 渲染 PNG/SVG（Playwright + fallback）
│   ├── open_in_excalidraw.js         # 推送到本地 Excalidraw 并打开
│   ├── lib/svg_render.js             # 共享轻量 SVG 渲染器（预览/fallback 复用）
│   └── test_e2e.sh                   # 端到端测试
└── output/
    └── fixture-flowchart.excalidraw  # 测试用流程图
```

## 沙箱兼容性

- **preview_server.js**：需要绑定端口，沙箱内运行需 escalation；启动后一切写入都在内存和预览页，不碰本地 Excalidraw web root
- **render_preview.js**：沙箱内无法启动 HTTP 服务器或 Chromium 时，自动 fallback 到 SVG 渲染
- **open_in_excalidraw.js**：沙箱内无法写入 web root 时，给出明确提示和手动操作命令（exit code 3）

## 实时预览（参考 al1y/mcp-excalidraw）

预览服务器采用 al1y/mcp-excalidraw 的"内存图 + 轮询 API"模式：

```
push_preview.js ──POST /api/current-diagram──▶ preview_server.js（内存存储）
                                                        │
预览页 ◀──每 1.5s 轮询 /api/preview─────────────────────┘
```

- `POST /api/current-diagram`：接收 `{elements, appState}` 或原始 `.excalidraw` JSON
- `GET /api/preview`：返回 `{svg, stats, updated}`，预览页据此实时刷新
- `GET /api/diagram.svg`：可直接取当前图的 SVG
- 与参考项目的区别：参考项目内嵌完整 Excalidraw React 编辑器，本 skill 用轻量 SVG 渲染做快速预览，完整编辑仍走本地 Excalidraw（localhost:5001）

## 支持的图表类型

| 类型 | 说明 |
|---|---|
| 流程图 | 纵向/横向步骤 + 菱形决策 + 箭头 |
| 架构图 | 分层：用户层 → 应用层 → 服务层 → 数据层 |
| 时序图 | 角色竖线 + 横向箭头消息 |
| 思维导图 | 中心主题 + 一级/二级分支 |
| 泳道图 | 水平泳道按角色分区 |
| ER 图 | 实体矩形 + 关系菱形 + 基数标注 |
| 层级图 | 自上而下树形结构，适合组织/系统拆解 |
| 关系图 | 节点+连线+关系标注，无严格方向 |
| 对比图 | 左右两栏或表格，标明比较维度 |
| 时间线图 | 水平时间轴+关键节点+事件标注 |

## 许可

MIT
