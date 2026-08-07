# more-chat-excalidraw 交接文档

> 更新时间：2026-08-07

## 当前状态

**Phase 1-3 完成，Phase 4 进行中（实时预览已完成，10/10 测试通过）。**

核心闭环已跑通：validate → 实时预览 → render → open 全链路在 escalation 下正常工作，沙箱内有 fallback SVG 渲染。

## 已完成

- [x] Phase 1：基础设施与权限修复
  - git 仓库初始化
  - render_preview.js 沙箱 fallback（EPERM → SVG 渲染）
  - open_in_excalidraw.js 沙箱兼容（EPERM → 手动提示 + exit code 3）
  - package.json + output/ 目录
- [x] Phase 2：核心闭环跑通
  - 端到端测试 5/5 通过
  - fixture-flowchart.excalidraw（14 元素流程图）
  - test_e2e.sh 集成测试脚本
- [x] Phase 3：质量与文档
  - README.md、HANDOFF.md
  - validate_excalidraw.py 增强（--json、类型必填字段、箭头绑定交叉检查）
- [x] Phase 4（部分）：实时预览服务器（参考 al1y/mcp-excalidraw）
  - preview_server.js：内存存储 + 轮询 API（/api/current-diagram、/api/preview、/api/diagram.svg）
  - push_preview.js：推送 .excalidraw 到预览服务器，预览页 ~1.5s 实时刷新
  - lib/svg_render.js：共享轻量 SVG 渲染器（render fallback + 预览复用）
  - 端到端测试扩展至 10/10 通过

## 进行中

- [ ] Phase 4：增强功能
  - Mermaid → Excalidraw 转换（参考项目核心能力，本地 node_modules 已含依赖）
  - 增量更新（merge_excalidraw.py）
  - 更多图表模板、智能布局
- [ ] Phase 5：发布与维护
  - 版本号与 CHANGELOG
  - CI/CD
  - 用户文档

## 依赖快照

| 依赖 | 版本/路径 | 说明 |
|---|---|---|
| Node.js | 系统全局 | 运行 render 和 open 脚本 |
| Python 3 | 系统全局 | 运行 validate 脚本 |
| Playwright | 全局安装 `~/.npm-global/` | 可选，用于高质量渲染 |
| Chromium | `~/Library/Caches/ms-playwright/chromium-1228/` | Playwright 浏览器 |
| Render bundle | `~/WorkSpace/render-test/` | Excalidraw 渲染包 |
| 本地 Excalidraw | `http://localhost:5001/` | launchd 自启的 http-server |
| @excalidraw/mermaid-to-excalidraw | `~/.local/share/excalidraw/node_modules/` | Phase 4 Mermaid 转换复用 |

## 已知问题

1. **沙箱内无法渲染 PNG**：Chromium EPERM，只能输出 SVG
2. **沙箱内无法推送画布**：`~/.local/share/` 写入受限，需 escalation
3. **沙箱内无法启动预览服务器**：端口绑定 EPERM，需 escalation；用 `preview_server.js` 时推荐常驻进程
4. **Excalidraw 服务可能未运行**：`--check-only` 可检测，`--start` 可尝试启动
5. **Render bundle 路径硬编码**：默认 `~/WorkSpace/render-test/`，需通过 `EXCALIDRAW_RENDER_BUNDLE` 环境变量覆盖
6. **Playwright 全局安装**：非项目本地，版本可能漂移

## Git 历史

```
4e9d214 feat: Phase 2 - e2e test suite, fixture flowchart
8202947 feat: Phase 1 - sandbox fallback, service detection, package.json
cd4cdbb feat: initial commit - SKILL.md, scripts, references, agents
```
