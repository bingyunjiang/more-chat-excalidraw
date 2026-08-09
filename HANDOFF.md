# more-chat-excalidraw 交接文档

> 更新时间：2026-08-08（v0.0.1 初始版本）

## 当前状态

**版本保持 v0.0.1。核心闭环与本轮发布收口已完成；测试统一称为 e2e suite，结果以当前环境输出为准。**

本 skill 完全自包含，不依赖其他 skill：render bundle 已内联到 scripts/render-bundle/，
编辑器 bundle 源码在 scripts/web/，MCP SDK/zod 从本 skill 内加载。

开发路线以四大核心功能支柱组织（Pillar A 交互沟通 / B 预设模板 / C JSON 生成 / D 本地预览），详见 [ROADMAP.md](ROADMAP.md)。

## 完成情况

| 里程碑 | 交付物 | 状态 |
|--------|--------|------|
| M1 基础设施 | git + package.json + 沙箱权限修复 | ✅ |
| M2 闭环跑通 | e2e 测试 + fixture | ✅ |
| M3 可交付 | README + HANDOFF + 增强校验 | ✅ |
| M4 实时预览 | preview_server.js 轮询 API（借鉴 al1y） | ✅ |
| M5 模板系统 | 8 个参考文件 + template_selector + list_templates(SVG 预览) | ✅ |
| M6 文案引擎 | template_selector --recommend + ir-format.md（IR 中间格式） | ✅ |
| M7 JSON 生成 | ir_to_excalidraw.py + Graphviz 布局 + merge 增量编辑 + --visual 质量门 | ✅ |
| M8 完整预览 | 内嵌 Excalidraw 编辑器(/editor) + 双向同步(/api/save) + 多画布 + PDF 导出 | ✅ |
| M9 创新功能 | 动画 + Mermaid + 知识图谱 + Graphviz + MCP + 图标库 | ✅ 核心能力完成，平台边界已记录 |
| E.3 演示 | 13 个示例 + 动画 GIF（output/animation-demo.gif） | ✅ 完成 |
| M10 发布 | v0.0.1 + CHANGELOG + 文档示例 + CI 配置 | ✅ 在线安装与跨平台实机仍待验证 |

## 核心脚本速查

```bash
# 模板选择（意图推荐）
python3 scripts/template_selector.py --recommend "画一个微服务架构图"

# IR → Excalidraw（推荐生成路径）
python3 scripts/ir_to_excalidraw.py --example architecture --layout dot --output out.excalidraw --validate

# Mermaid → Excalidraw（flowchart/sequence 子集）
node scripts/mermaid_to_excalidraw.js --string "graph TD; A-->B" --output out.excalidraw

# 知识图谱 → 架构图
python3 scripts/knowledge_graph.py --text arch.txt --output out.excalidraw

# 云架构技术图标（自包含 67 个 SVG）
python3 scripts/ir_to_excalidraw.py --example architecture --icons --output out-icons.excalidraw

# 增量编辑（合并/微调/回退）
python3 scripts/merge_excalidraw.py patch out.excalidraw --set 'n3.backgroundColor=#ffc9c9' --move 'n5:20,0'

# 实时预览 / 内嵌编辑器 / 动画
node scripts/preview_server.js out.excalidraw --open    # SVG 轮询预览
# 浏览器打开 http://localhost:6060/editor   完整 Excalidraw 编辑器（可保存回写）
# 浏览器打开 http://localhost:6060/animate  关键帧动画逐帧播放

# PDF 导出
node scripts/render_preview.js out.excalidraw /tmp/out --format pdf

# MCP 服务器（stdio，供 agent 调用）
node scripts/mcp_server.mjs   # 工具: generate_diagram / validate_diagram / push_preview / list_templates
```

## 依赖快照

| 依赖 | 位置 | 说明 |
|---|---|---|
| Node.js ≥ 18 | 系统 | 运行 JS 脚本 |
| Python 3 | 系统 | 运行 Python 脚本 |
| Playwright + Chromium | 全局 | render_preview PNG/PDF（可选，SVG fallback） |
| Graphviz | brew（dot/neato/twopi） | ir_to_excalidraw.py --layout 自动布局 |
| @excalidraw/excalidraw 0.18.1 + React 19 | scripts/web/node_modules | 内嵌编辑器 bundle 源码（npm run build 重建） |
| @modelcontextprotocol/sdk + zod | scripts/web/node_modules | MCP 服务器 |
| 本地 Excalidraw | localhost:5001 | open_in_excalidraw.js 打开画布 |
| render bundle | scripts/render-bundle/（内置） | render_preview 自包含 bundle（EXCALIDRAW_RENDER_BUNDLE 可覆盖） |

## 本轮已完成与仍待验证

- 新增 `thermal-runaway` 手绘双语分析板及四格式产物；中文、英文手绘注记、便签框、彩色曲线箭头和虚线机理链已目检。
- 新增 `battery-thermal` 白底极简工程架构视觉基准及四格式产物；四列布局、无衬线字体和洁净裁切已目检。
- 新增 `fea` 工程有限元流程示例及四格式产物；经 PNG 目检优化为四阶段横向泳道，严格视觉、洁净裁切与确定性已验证。
- 核心 Library 已 self-authored MIT 内置；第三方缓存仅作可选覆盖且 needs_verification。

- 已完成：web 依赖声明与 build:all、CI 构建、MCP 实际调用、默认确定性、Library 两阶段布局、跨平台 opener 安全调用。
- 已完成：Library 代表性 `--visual` 校验与本地缓存 SHA-256 清单。
- 已在当前 macOS 环境完成 `npm ci`、web bundle 构建与 45 项 e2e；尚未在真实 Windows/Linux 桌面实机验证浏览器/服务启动。

## 已知问题与后续

1. **沙箱限制**：端口绑定/Chromium/子进程需 escalation；`scripts/web/editor-bundle.js` 是构建产物（gitignore），全新 checkout 需 `npm ci --prefix scripts/web && npm run build:all --prefix scripts/web`
2. **C.7 云架构图标库**：需外部图标资源（AWS/GCP/Azure SVG），留作可选扩展
3. **CI**：无 git remote，GitHub Actions 待推送远端后启用
4. **Mermaid 子集**：当前支持 flowchart/sequenceDiagram 常用语法；完整 mermaid（gantt/class/er）未覆盖
5. **文案生成（A.2）**：IR 生成依赖 LLM 在对话中完成，未做独立文案生成器（符合 skill 定位）

## Git 历史

```
1eb739f chore: remove deprecated mcp_server.js
d5be421 feat: M9 MCP protocol integration (D.6)
105100b feat: M9 Graphviz auto-layout (C.2)
e8ea1a3 feat: M10 prep + M9 knowledge graph (C.8)
7b06739 feat: M8 completion + M9 animation/mermaid/quality-gate
c7d921f feat: M7 completion + M8 embedded editor preview server
adb9da1 feat: M5 template system
75724c6 chore: remove __pycache__
75be64f feat: M5 completion + M6/M7 core engines
9edf39d feat: Phase 4.0 - real-time preview server
61f14ea feat: Phase 3 - README, HANDOFF, enhanced validate
4e9d214 feat: Phase 2 - e2e test suite
8202947 feat: Phase 1 - sandbox fallback
cd4cdbb feat: initial commit
```
# Current sketch handoff

Sketch presets and case outputs are generated and strict-validated. Re-run `bash scripts/test_e2e.sh` after any renderer/font environment change; browser font availability remains an environment boundary.

The localhost:5001 build may ignore scene `scrollY` and invisible viewport spacers during auto-fit, so editor toolbar overlap is not automatically preventable; use PNG/SVG for formal visual acceptance or pan manually.
