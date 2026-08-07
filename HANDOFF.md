# more-chat-excalidraw 交接文档

> 更新时间：2026-08-07（v3）

## 当前状态

**M1-M4 完成（基础设施 → 实时预览），M5 模板系统进行中（参考文件已全部落盘，交互脚本已就绪）。**

开发路线已重构为四大核心功能支柱（Pillar A 交互沟通 / B 预设模板 / C JSON 生成 / D 本地预览），详见 [ROADMAP.md](ROADMAP.md)。

## 已完成

- [x] Phase 1：基础设施与权限修复
  - git 仓库初始化、render/open 沙箱 fallback、package.json、output/ 目录
- [x] Phase 2：核心闭环跑通
  - 端到端测试 5/5 → 10/10 通过，fixture-flowchart.excalidraw
- [x] Phase 3：质量与文档
  - README.md、HANDOFF.md、validate_excalidraw.py 增强（--json、类型校验、绑定交叉检查）
- [x] Phase 4：实时预览服务器（参考 al1y/mcp-excalidraw）
  - preview_server.js 轮询 API + push_preview.js + lib/svg_render.js，10/10 测试通过
- [x] **M5 模板系统（本次新增）**
  - `references/diagram-templates.md`：扩展至 10 种图类型（+层级/关系/对比/时间线）
  - `references/color-palette.md`：8 种语义填充色 + 3 种分层背景 + 4 套主题（default/sketch/blueprint/minimal）
  - `references/element-templates.md`：9 类元素构建块（含必填字段、尺寸规范、绑定规则）
  - `references/tech-node-templates.md`：50+ 技术组件样式（数据库/队列/存储/网关/计算/缓存等 9 类）
  - `references/visual-patterns.md`：9 种视觉模式（扇出/汇聚/时间线/分组/请求-响应/流水线/星型/矩阵/循环）
  - `references/animation-template.md`：customData.animate 关键帧模板 + 7 级动画顺序规则
  - `scripts/template_selector.py`：模板选择器（--list / --recommend / --info / --params）
  - `scripts/list_templates.js`：模板列表与预览（--json / --preview）
  - SKILL.md / README.md / package.json（v0.2.0）同步更新

## 进行中

- [ ] M5 剩余：模板预览 SVG 渲染（list_templates.js --preview 当前仅输出元数据）
- [ ] M6 文案引擎（Pillar A）：意图分类器 + 文案生成 + IR 中间格式
- [ ] M7 JSON 生成（Pillar C）：ir_to_excalidraw.py + 自动布局 + 自纠错
- [ ] M8 完整预览（Pillar D）：内嵌 Excalidraw 编辑器 + 双向同步 + 多画布
- [ ] M9 创新功能：动画 + 图标 + 知识图谱 + MCP
- [ ] M10 发布：版本号 + CI + 文档

## 依赖快照

| 依赖 | 版本/路径 | 说明 |
|---|---|---|
| Node.js | 系统全局 | 运行 render/open/list_templates 脚本 |
| Python 3 | 系统全局 | 运行 validate/template_selector 脚本 |
| Playwright | 全局安装 `~/.npm-global/` | 可选，用于高质量渲染 |
| Chromium | `~/Library/Caches/ms-playwright/chromium-1228/` | Playwright 浏览器 |
| Render bundle | `~/WorkSpace/render-test/` | Excalidraw 渲染包（可用 EXCALIDRAW_RENDER_BUNDLE 覆盖） |
| 本地 Excalidraw | `http://localhost:5001/` | launchd 自启的 http-server |
| @excalidraw/mermaid-to-excalidraw | `~/.local/share/excalidraw/node_modules/` | M7 Mermaid 转换复用 |

## 已知问题

1. **沙箱内无法渲染 PNG**：Chromium EPERM，只能输出 SVG
2. **沙箱内无法推送画布**：`~/.local/share/` 写入受限，需 escalation
3. **沙箱内无法启动预览服务器**：端口绑定 EPERM，需 escalation
4. **Excalidraw 服务可能未运行**：`--check-only` 可检测，`--start` 可尝试启动
5. **list_templates.js --preview 仅输出元数据**：尚未渲染 SVG 预览（M5 收尾项）
6. **template_selector.py 关键词匹配是启发式**：中文意图推荐可能不准，M6 可接入 LLM 分类

## Git 历史

```
（M5 提交待创建）
9edf39d feat: Phase 4.0 - real-time preview server (al1y/mcp-excalidraw pattern)
61f14ea feat: Phase 3 - README, HANDOFF, enhanced validate
4e9d214 feat: Phase 2 - e2e test suite, fixture flowchart
8202947 feat: Phase 1 - sandbox fallback, service detection, package.json
cd4cdbb feat: initial commit - SKILL.md, scripts, references, agents
```
