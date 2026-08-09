# more-chat-excalidraw 测试示例

本目录包含 skill 各功能的真实测试结果，所有 .excalidraw 和渲染文件均由脚本实际生成并校验通过。

## 测试概览

| # | 测试项 | 脚本 | 输入 | 输出 | 状态 |
|---|--------|------|------|------|------|
| 1 | 模板列表与推荐 | `template_selector.py` | `--list` / `--recommend` | 10 种模板 + 4 套主题 | OK |
| 2 | 内置示例生成 | `ir_to_excalidraw.py --example` | flowchart / architecture / mindmap | 3 个 .excalidraw | OK |
| 3 | IR to Excalidraw（手工 IR） | `ir_to_excalidraw.py` | 微服务架构 IR JSON | 53 元素 | OK |
| 4 | 校验 | `validate_excalidraw.py` | 所有生成文件 | 全部通过 | OK |
| 5 | 渲染预览 | `render_preview.js --format both` | 所有 .excalidraw | PNG/SVG/PDF | OK |
| 6 | Mermaid 流程图转换 | `mermaid_to_excalidraw.js` | flowchart TD | 31 元素 | OK |
| 7 | Mermaid 时序图转换 | `mermaid_to_excalidraw.js` | sequenceDiagram | 34 元素 | OK |
| 8 | 知识图谱 | `knowledge_graph.py --text` | 电商架构文本描述 | 41 元素 | OK |
| 9 | 主题切换 | `--theme sketch/blueprint` | 流程图 | 2 种主题 | OK |
| 10 | 图标注入 | `--icons` | 微服务架构 IR | 53 元素 | OK |
| 11 | Graphviz 布局 | `--layout dot` | 微服务架构 IR | dot 自动布局 | OK |
| 12 | Graphviz neato 布局 + 视觉检查 | `--layout neato --validate` | 微服务架构 IR | 重叠警告（预期） | OK |
| 13 | 增量编辑 | `merge_excalidraw.py patch` | 修改文字 + 位移 | 备份 + 保存 | OK |
| 14 | 图标库 | `icon_library.py --list` | — | 67 个技术图标 | OK |
| 15 | **库组件替换** | `ir_to_excalidraw.py --library` | 架构图 IR | C4/手绘组件替换 | OK |
| 16 | **库组件 + Graphviz** | `--library --layout dot` | 微服务/AWS IR | 精美架构图 | OK |

## 库组件示例（`--library`）

### 设计理念

`--library` 标志从 Excalidraw Libraries 生态加载手绘风格组件，替换 IR 中的简单矩形/椭圆节点。当前支持的映射：

| IR 节点类型/标签 | 库组件 | 来源 |
|---|---|---|
| database / PostgreSQL / Redis / MongoDB | C4 Database（手绘圆柱体） | dmitry-burnyshev_c4-architecture |
| service / component / process | C4 Component（手绘矩形） | dmitry-burnyshev_c4-architecture |
| Web 前端 / frontend | C4 Web App（带窗口装饰） | dmitry-burnyshev_c4-architecture |
| actor / user / person | C4 Person（人物轮廓） | dmitry-burnyshev_c4-architecture |
| Lambda / S3 / CloudFront / DynamoDB | AWS Serverless Icons | stojanovic_aws-serverless-icons-v2 |
| Kafka | Kafka Icon | chuqbach_data-platform |
| Docker | Docker Icon | anna-pastushko_architecture-diagram-components |
| Kubernetes / K8s | K8s Deploy Icon | boemska-nik_kubernetes-icons |

### 对比：默认 vs 库组件

| 特性 | 默认模式 | 库组件模式 |
|------|----------|------------|
| Database 节点 | 简单椭圆 | 手绘圆柱体（line + ellipse） |
| Service 节点 | 白色矩形 | C4 Component（矩形 + 标签 + 类型标注） |
| Web 前端 | 简单矩形 | C4 Web App（带窗口装饰点） |
| 元素数量 | 24（微服务示例） | 44（微服务示例） |
| 视觉效果 | 简洁 | 精美手绘风格 |

### 生成文件

- `architecture-library.excalidraw` — 内置架构示例 + 库组件
- `architecture-library-dot.excalidraw` — 同上 + Graphviz dot 布局
- `microservice-library-dot.excalidraw` — 10 节点微服务架构 + 库组件 + dot 布局
- `microservice-default-dot.excalidraw` — 对比：同 IR 无库组件
- `aws-serverless-library.excalidraw` — AWS Serverless 架构 + 库组件 + dot 布局
- `flowchart-library.excalidraw` — 流程图（start/end/decision 保持简单形状）

## 测试文件说明

### IR 中间格式

- `microservice-arch-ir.json`：微服务架构图 IR，包含 11 个节点、11 条边、4 个分组

### Excalidraw 画布

所有文件均经 `validate_excalidraw.py` 校验通过。

### 渲染预览

每个 .excalidraw 均可渲染为 PNG/SVG/PDF，使用 `node scripts/render_preview.js <file> --format both`。

## 测试环境

- 日期：2026-08-08
- macOS / Python 3 / Node.js
- Graphviz 15.1.1（dot/neato 布局测试）
- Playwright（渲染引擎）
- Excalidraw Libraries（localhost:8080，140 个本地缓存库）

## 库组件缓存

`references/excalidraw-libs/` 包含 140 个 `.excalidrawlib` 文件（56MB），来自 Excalidraw Libraries 生态。这些文件由 `library_loader.py --cache` 从 `localhost:8080` 下载，也可通过 `python3 scripts/library_loader.py --search <关键词>` 搜索更多组件。

`library_loader.py` 的搜索路径优先级：`references/excalidraw-libs/` → `/tmp/excalidraw-libs/`。
