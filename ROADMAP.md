# more-chat-excalidraw 开发计划

> 最后更新：2026-08-07（v3.1，M5 完成 + M6/M7 核心引擎落地）

## 项目目标（v3）

通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。核心闭环：理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代。

## 当前状态总览

| 模块 | 状态 | 备注 |
|---|---|---|
| SKILL.md | ✅ 完成 | 五步闭环、质量规则、资源说明 |
| references/excalidraw-schema.md | ✅ 完成 | v2 JSON 结构速查 |
| references/diagram-templates.md | ✅ 完成（待扩展） | 6 类图表模板，v2 扩展到 10 类 |
| agents/openai.yaml | ✅ 完成 | 显示名、描述、默认提示词 |
| scripts/validate_excalidraw.py | ✅ 完成 | 结构+引用完整性校验 |
| scripts/render_preview.js | ✅ 已修复 | 沙箱内自动 fallback 到 SVG |
| scripts/open_in_excalidraw.js | ✅ 已修复 | 沙箱内给出明确提示 |
| scripts/preview_server.js | ✅ 完成 | 实时预览服务器（端口 6060） |
| scripts/push_preview.js | ✅ 完成 | 推送 .excalidraw 到预览服务器 |
| scripts/lib/svg_render.js | ✅ 完成 | 共享 SVG 渲染器 |
| git 仓库 | ✅ 已初始化 | |
| README.md | ✅ 完成 | |
| HANDOFF.md | ✅ 完成（待更新 Phase 5+） | |
| package.json | ✅ 完成 | Playwright 为 optional peerDep |
| 测试 | ✅ 完成 | test_e2e.sh 10/10 通过 |
| output/ 目录 | ✅ 已创建 | 含 fixture-flowchart.excalidraw |

## 环境依赖（已验证）

- 本地 Excalidraw：http-server on localhost:5001，launchd 自启，当前未运行
- 实时预览服务器：scripts/preview_server.js（端口 6060，轮询 API 模式，参考 al1y/mcp-excalidraw）
- Mermaid 转换依赖：本地 Excalidraw node_modules 含 @excalidraw/mermaid-to-excalidraw 与 mermaid
- Playwright：全局安装于 ~/.npm-global/，Chromium 在 ~/Library/Caches/ms-playwright/
- Render bundle：~/WorkSpace/render-test/（index.html + render-entry.js + render-bundle.js）
- 自定义 Node：~/.local/bin/node

---

## 开发路线（已完成）

### Phase 1：基础设施与权限修复 ✅

- [x] **1.1 初始化 git 仓库**
  - git init，添加 .gitignore（node_modules、output、*.png、*.svg）
  - 首次 commit：所有现有文件
- [x] **1.2 修复 render_preview.js 的沙箱权限问题**
  - 双路径：Playwright 优先，失败时 fallback 到 SVG 渲染
- [x] **1.3 修复 open_in_excalidraw.js 的沙箱权限问题**
  - 新增 --check-only / --start / --no-browser 参数
  - 沙箱内 EPERM → exit code 3 + 手动操作提示
- [x] **1.4 添加 package.json**
  - 声明 Playwright 为 optional peer dependency
  - 添加 scripts：render、open、validate、test
- [x] **1.5 创建 output/ 目录**
  - 添加 .gitkeep

### Phase 2：核心闭环跑通 ✅

- [x] **2.1 端到端测试：生成一个简单流程图**
  - 手动构造 fixture-flowchart.excalidraw（14 元素）
  - validate → render → open 全链路跑通
- [x] **2.2 编写集成测试脚本**
  - scripts/test_e2e.sh：自动构造 → 校验 → 渲染 → 对比
- [x] **2.3 确保 Excalidraw 本地服务可启动**
  - 检测 localhost:5001 是否可达
  - 不可达时提示用户启动或自动启动

### Phase 3：质量与文档 ✅

- [x] **3.1 编写 README.md**
- [x] **3.2 编写 HANDOFF.md**
- [x] **3.3 增强 validate_excalidraw.py**
  - 添加 --json 输出模式
  - 类型特定必填字段校验、箭头绑定一致性交叉检查
  - containerId/boundElements 双向验证、元素统计
- [x] **3.4 增强 render_preview.js**
  - 双路径渲染：Playwright 优先，fallback 到 SVG

### Phase 4：增强功能（已完成部分）

- [x] **4.0 实时预览服务器（参考 al1y/mcp-excalidraw，15★）**
  - 新增 scripts/preview_server.js：内存存储 + 轮询 API
  - 新增 scripts/push_preview.js：推送 .excalidraw 到预览服务器
  - 共享 SVG 渲染器 scripts/lib/svg_render.js
  - 端到端测试扩展至 10 项（10/10 通过）

---


## 四大核心功能支柱（v3 路线图）

基于调研与创新方向，将开发路线重构为**四大核心功能支柱**，每个支柱对应一整套端到端能力：

| 支柱 | 名称 | 核心交付 | 优先级 |
|------|------|----------|--------|
| Pillar A | 交互沟通与文案生成 | 对话式意图理解 → 结构化文案/大纲 | P0 |
| Pillar B | 预设模板选择与匹配 | 多类型模板库 + 对话式选择 + 自动匹配 | P0 |
| Pillar C | 结构化 JSON 生成与校验 | 模板 → 元素组合 → 布局 → .excalidraw | P0 |
| Pillar D | 本地网页版实时预览 | 浏览器内 Excalidraw 编辑器 + 实时推送 | P0 |

---

### Pillar A：交互沟通与文案生成（P0）

**目标**：用户通过自然对话表达意图，系统自动生成结构化文案/大纲，作为图表生成的基础。

**参考项目**：coleam00/excalidraw-diagram-skill（4339★）的对话式图表生成、axtonliu/axton-obsidian-visual-skills（3278★）的 8 种分类体系

- [ ] **A.1 意图分类器（对话路由）**
  - 在 SKILL.md 中增强 prompt 模板，首次交互时自动识别用户意图：
    - 图类型：流程图/架构图/时序图/思维导图/泳道图/ER图/层级图/关系图/对比图/时间线图
    - 场景：技术架构/业务流程/项目规划/知识梳理/方案对比/系统设计
    - 复杂度：简单（3-5 节点）/中等（6-12 节点）/复杂（>12 节点）
  - 输出格式：`{ "type": "flowchart", "scene": "tech-arch", "complexity": "medium", "title": "..." }`

- [ ] **A.2 文案生成引擎**
  - 根据意图分类结果，自动生成图表所需的文案大纲：
    - 流程图：步骤列表 + 决策点 + 分支条件
    - 架构图：层次划分 + 每层组件 + 组件间调用关系
    - 时序图：角色列表 + 消息序列 + 返回消息
    - 思维导图：中心主题 + 一级/二级分支节点
    - 对比图：比较维度 + 两/多方内容
    - 时间线图：时间节点 + 事件描述
  - 用户可交互修改文案（增删改节点），确认后进入 Pillar C

- [ ] **A.3 文案 → 结构化中间表示**
  - 定义 JSON 中间格式（Intermediate Representation，IR），独立于 Excalidraw 格式
  - IR 为独立格式，可序列化、版本化、作为 LLM 输出与模板引擎的桥梁

- [ ] **A.4 创新方向：文案增强**
  - 支持多轮迭代优化文案（参考 coleam00 的迭代优化模式）
  - 从已有文档/Markdown 自动提取结构生成图表文案
  - 支持从 Mermaid 源码导入（参考 al1y + axtonliu）

---

### Pillar B：预设模板选择与匹配（P0，当前优先级最高）

**目标**：建立可复用的预设模板体系，用户在对话中可选择模板，系统自动匹配最佳模板。

**参考项目**：coleam00/excalidraw-diagram-skill（4339★）的元素模板、axtonliu（3278★）的 8 种分类体系、drawmode（16★）的主题系统

- [ ] **B.1 图类型模板（10 种，已定义 6 种 + 新增 4 种）**
  - 已存在的 6 种：流程图、架构图、时序图、思维导图、泳道图、ER 图
  - 新增 4 种（已经纳入 diagram-templates.md）：
    - 层级图 Hierarchy（组织结构/系统拆解，自上而下树形）
    - 关系图 Relationship（要素间依赖/影响，连线+标注）
    - 对比图 Comparison（左右两栏/表格，标明比较维度）
    - 时间线图 Timeline（时间轴+关键事件，适合项目进度/演化）
  - 每种模板提供完整 JSON 示例 + 布局参数 + 适用场景说明

### 以下为新增的参考文件（v3 新增）

- [ ] **B.2 元素级构建块模板**
  - 文件：`references/element-templates.md`
  - 独立可复用的模板：rectangle / ellipse / diamond / arrow / text（独立）/ text（容器内绑定）/ line / marker dot / frame
  - 每种模板标注必填字段、可选字段、默认值
  - 生成时按需组合，而非每次都写完整 JSON
  - 参考 coleam00 的模板化生成思路

- [ ] **B.3 语义色板**
  - 文件：`references/color-palette.md`
  - 按语义组织的颜色体系
  - 对比度规则：白底不低于 `#757575`，浅色填充用深色变体文字

- [ ] **B.4 主题系统（参考 drawmode）**
  - 提供 4 套可一键切换的矢量主题：
    - default：深灰描边 `#1e1e1e`，白色填充，标注连线
    - sketch：roughness=2，手绘感更强，更粗描边
    - blueprint：蓝底白线（`#1e3a5f` 背景，`#e8f4ff` 描边，`#64b5f6` 连线）
    - minimal：纯黑白，roughness=0，strokeWidth=1
  - 主题参数化：theme 参数影响所有元素的颜色/roughness/strokeWidth

- [ ] **B.5 架构感知节点模板（参考 excalidraw-architect-mcp，139★）**
  - 文件：`references/tech-node-templates.md`
  - 50+ 常见技术组件预定义样式（形状+颜色+图标占位）
  - 架构图生成时自动根据技术名称匹配对应样式

- [ ] **B.6 视觉模式模板（参考 coleam00）**
  - 文件：`references/visual-patterns.md`
  - 把常见关系模式抽象为可复用模板：扇出、汇聚、时间线、分组、请求-响应、流水线
  - 每种模式提供 DSL 表示和对应的 Excalidraw JSON 骨架

- [ ] **B.7 动画关键帧模板（参考 excalimate，50★ + axtonliu）**
  - 文件：`references/animation-template.md`
  - 支持 `customData.animate` 字段，使生成的图可拖入 excalidraw-animate 生成动画
  - 动画顺序规则：标题(1) → 框架(2) → 主要节点(3) → 连线(4) → 细节文字(5)

- [ ] **B.8 模板选择交互脚本**
  - 文件：`scripts/template_selector.py`
  - 列出所有可用模板（按类型/场景/复杂度分类）
  - 根据用户意图自动推荐最佳模板
  - 支持模板预览（展示模板的 JSON 结构 + 预期效果描述）
  - 模板参数调整（颜色/主题/布局方向）
  - 输出：选定的模板元数据 + 填充参数，供 Pillar C 使用

- [ ] **B.9 模板列表与预览脚本**
  - 文件：`scripts/list_templates.js`
  - 命令行列出所有模板，输出 JSON 格式
  - 支持 `--preview <template-name>` 输出该模板的 SVG 预览

---

### Pillar C：结构化 JSON 生成与校验（P0）

**目标**：将文案（Pillar A 输出）与模板（Pillar B 输出）组合，自动生成结构完整、颜色正确的 .excalidraw JSON 文件。

**参考项目**：coleam00（4339★）的完整 JSON 生成、drawmode（16★）的 Graphviz 自动布局、excalidraw-architect-mcp（139★）的知识图谱生成

- [ ] **C.1 IR → Excalidraw JSON 转换器**
  - 文件：`scripts/ir_to_excalidraw.py`
  - 输入：IR JSON（Pillar A 输出）+ 模板元数据（Pillar B 输出）
  - 处理流程：模板布局 → 元素生成 → 箭头绑定 → 应用色板 → 输出 JSON
  - 输出：完整的 `.excalidraw` JSON 文件

- [ ] **C.2 自动布局引擎（参考 drawmode + excalidraw-architect-mcp）**
  - 集成 Graphviz 作为可选布局引擎
  - 支持布局算法：层次布局（dot）、力导向布局（neato）、树形布局（twopi）
  - 布局后自动调整元素尺寸适配文字内容
  - 无 Graphviz 时使用内置布局计算器

- [ ] **C.3 模板驱动的元素组合器**
  - 从 element-templates.md 读取元素模板定义
  - 根据节点类型选择对应元素模板
  - 自动生成文字绑定 + 箭头绑定
  - 技术组件自动匹配样式（tech-node-templates.md）

- [ ] **C.4 自纠错与质量门（参考 robonuggets，74★ + shannhk，5★）**
  - 增强现有 validate_excalidraw.py
  - 视觉质量检查：文字溢出、元素重叠、连线悬空
  - 布局合理性检查：间距、层级清晰度
  - 自纠错：自动调整布局参数重新生成

- [ ] **C.5 增量编辑与迭代（参考 coleam00）**
  - 文件：`scripts/merge_excalidraw.py`
  - 合并新旧元素，保留旧 id，新增元素用新 id
  - 支持微调 + 重排 + 回退

- [ ] **C.6 Mermaid ↔ Excalidraw 互转**
  - 利用本地 @excalidraw/mermaid-to-excalidraw 包
  - Mermaid 源码 → IR → Excalidraw 元素
  - 作为 Pillar A 的输入通道之一

- [ ] **C.7 云架构图标库（参考 excalidraw-icons-mcp，28★）**
  - 内置 AWS/Azure/GCP/Kubernetes 常用图标文件
  - 架构图生成时自动根据技术名称匹配对应图标

- [ ] **C.8 知识图谱架构生成（参考 excalidraw-architect-mcp，139★）**
  - 从架构描述提取实体/关系 → 知识图谱 → 自动布局
  - 支持自然语言增量修改

---

### Pillar D：本地网页版实时预览（P0）

**目标**：在浏览器中嵌入完整 Excalidraw 编辑器，实现实时预览、推送更新、交互编辑的闭环体验。

**参考项目**：excalidraw/excalidraw-mcp（5069★）的 MCP 协议集成、al1y/mcp-excalidraw（15★）的实时 Web 预览、yctimlin/mcp_excalidraw（2258★）的 MCP 服务器模式、drawmode（16★）的 SDK 引用模式

- [ ] **D.1 升级预览服务器为完整 Excalidraw 编辑器**
  - 当前：preview_server.js 仅提供 SVG 渲染（轮询 API 模式）
  - 升级目标：预览页内嵌 Excalidraw React 组件，用户可在浏览器中直接编辑
  - 实现方式：CDN 引入 Excalidraw standalone bundle 或本地 node_modules 包
  - 预览页功能：全功能编辑器 + 实时推送 + 导出

- [ ] **D.2 实时双向同步**
  - 当前：单向推送（push → preview）
  - 新增：预览页编辑后，自动同步回本地文件
  - 用户确认后，更新本地 .excalidraw 文件

- [ ] **D.3 多画布管理**
  - 预览服务器支持同时管理多个画布，独立 ID 和名称
  - 用户可切换/对比不同画布

- [ ] **D.4 创新方向：关键帧动画预览（参考 excalimate，50★）**
  - 在预览页中嵌入动画播放功能
  - 支持定义关键帧 → 自动生成序列展开动画
  - 导出为 GIF/WebM 视频

- [ ] **D.5 多格式导出增强**
  - 当前：PNG/SVG 预览
  - 新增：PDF 导出、HTML 嵌入代码生成、Markdown 嵌入

- [ ] **D.6 MCP 协议集成（参考 excalidraw/excalidraw-mcp，5069★）**
  - 对接官方 MCP 协议，支持实时画布读写
  - 支持在已有画布上追加元素
  - 作为 Codex 与浏览器预览页之间的标准通信协议

---

## 创新方向摘要（外部项目参考）

| 创新方向 | 源项目 | Stars | 对应 Pillar | 借鉴点 |
|----------|--------|-------|-------------|--------|
| 关键帧动画 | excalimate/excalidraw-animate | 50★ | D.4 | 动画序列生成、关键帧定义 |
| 知识图谱+自动布局 | BV-Venky/excalidraw-architect-mcp | 139★ | C.8, C.2 | 实体关系提取、自动布局 |
| 云厂商图标库 | excalidraw-icons-mcp | 28★ | C.7 | 图标匹配、资源管理 |
| Graphviz 布局 | drawmode | 16★ | C.2 | TypeScript → Graphviz → Excalidraw |
| 实时预览 MCP | al1y/mcp-excalidraw | 15★ | D.1 | 轮询预览模式（已实现） |
| 官方 MCP 协议 | excalidraw/excalidraw-mcp | 5069★ | D.6 | 标准通信协议 |
| 迭代优化 | coleam00/excalidraw-diagram-skill | 4339★ | C.5 | 增量编辑、多轮优化 |
| 自纠错验证 | robonuggets/excalidraw-skill | 74★ | C.4 | 视觉质量检查 |
| WCAG 可访问性 | shannhk/improved-excaldrawing | 5★ | C.4 | 认知负荷验证 |
| 分类体系 | axtonliu/axton-obsidian-visual-skills | 3278★ | B.1 | 8 种图类型、动画模板 |
| MCP 服务器 | yctimlin/mcp_excalidraw | 2258★ | D.6 | 服务器模式参考 |

---

## 里程碑（v3）

| 里程碑 | 目标 | 包含 Pillar | 预计交付 |
|--------|------|-------------|----------|
| M1：基础设施 | git + package.json + 权限修复 | — | ✅ 完成 |
| M2：闭环跑通 | 端到端测试通过 | — | ✅ 完成 |
| M3：可交付 | README + HANDOFF + 增强校验 | — | ✅ 完成 |
| M4：实时预览 | 实时预览服务器（轮询 API） | D（基础版） | ✅ 完成 |
| M5：模板系统 | 全部 8 个参考文件 + 交互选择脚本 + SVG 预览 | B | ✅ 完成 |
| M6：文案引擎 | 意图分类 + 文案生成 + IR 中间格式 | A | 🔄 IR 已定义，意图分类器已具备（template_selector --recommend），文案生成待接入 LLM |
| M7：JSON 生成 | IR→Excalidraw + 自动布局 + 自纠错 | C | 🔄 ir_to_excalidraw.py 已实现，自动布局/配色/绑定完成，自纠错待增强 |
| M8：完整预览 | 内嵌编辑器 + 双向同步 + 多画布 | D（完整版） | 待开始 |
| M9：创新功能 | 动画 + 图标 + 知识图谱 + MCP | A/B/C/D 创新 | 待开始 |
| M10：可发布 | 版本号 + CI + 文档 + 演示 | — | 待开始 |

## 后续阶段（P3）

### Phase E：发布与维护（P3，M10）

- [ ] **E.1 版本号与 CHANGELOG**
  - 语义化版本号（当前 v0.2.0）
  - CHANGELOG.md 追踪每次变更
- [ ] **E.2 CI/CD**
  - GitHub Actions：validate + render smoke test
  - 自动发布到 skill 仓库
- [ ] **E.3 用户文档与示例**
  - 各类图表的完整示例文件
  - 使用视频或 GIF 动画

---

## 已知问题与风险（v3）---

## 已知问题与风险

1. **沙箱权限**：render、open、preview 脚本在 Codex 沙箱内无法直接运行（端口/写盘受限），需要 escalation 或备选方案
2. **Excalidraw 本地服务**：当前未运行，launchd 配置存在但可能未加载
3. **Playwright 依赖**：全局安装而非项目本地，版本可能漂移
4. **render bundle 路径硬编码**：默认指向 ~/WorkSpace/render-test/，不够通用
5. **无 git 历史**：无法追踪变更，回滚困难

## 调研参考摘要

| 来源项目 | Stars | 借鉴内容 |
|----------|-------|----------|
| excalidraw/excalidraw-mcp | 5069★ | MCP 协议集成（Phase 7） |
| coleam00/excalidraw-diagram-skill | 4339★ | 元素模板、语义色板、视觉模式、迭代优化（Phase 5-6） |
| axtonliu/axton-obsidian-visual-skills | 3278★ | 8 种图类型、动画模板、分层背景（Phase 5） |
| yctimlin/mcp_excalidraw | 2258★ | MCP 服务器模式（Phase 7） |
| BV-Venky/excalidraw-architect-mcp | 139★ | 技术组件模板、知识图谱架构生成（Phase 5.5+6.6） |
| excalimate/excalidraw-animate | 50★ | 关键帧动画与序列展开（Phase 6.7） |
| drawmode | 16★ | 4 套主题、Graphviz 自动布局、SDK 模式（Phase 5.4+6.5） |
| excalidraw-icons-mcp | 28★ | 云架构图标库（Phase 6.4） |
| robonuggets/excalidraw-skill | 74★ | 自纠错与视觉验证（Phase 6.2） |
| shannhk/improved-excaldrawing | 5★ | 认知负荷验证、WCAG 可访问性（Phase 6.2） |
| al1y/mcp-excalidraw | 15★ | 实时 Web 预览 MCP 服务器（Phase 4.0 已实现） |

## 里程碑

| 里程碑 | 目标 | 状态 |
|--------|------|------|
| M1：基础设施 | git + package.json + 权限修复 | ✅ 完成 |
| M2：闭环跑通 | 端到端测试通过 | ✅ 完成 |
| M3：可交付 | README + HANDOFF + 增强校验 | ✅ 完成 |
| M4：可用 | 实时预览 + 增量更新 + 模板 + Mermaid | 🔄 进行中（实时预览已完成，Phase 5 待开始） |
| M5：差异化 | 模板系统扩展完成 | 待开始 |
| M6：创新 | 知识图谱 + 动画 + 自动布局 + 图标库 | 待开始 |
| M7：可发布 | 版本号 + CI + 文档 + MCP | 待开始 |
