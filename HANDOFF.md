# more-chat-excalidraw 交接文档

> 更新时间：2026-08-07

## 当前状态

**Phase 1-2 完成，Phase 3 进行中。**

核心闭环已跑通：validate → render → open 全链路在 escalation 下正常工作，沙箱内有 fallback SVG 渲染。

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

## 进行中

- [ ] Phase 3：质量与文档
  - [x] README.md
  - [x] HANDOFF.md
  - [ ] 增强 validate_excalidraw.py（--json 输出、更多校验规则）
  - [ ] 增强 render_preview.js（--format 支持）

## 待做

- [ ] Phase 4：增强功能
  - 增量更新（merge_excalidraw.py）
  - 更多图表模板
  - 智能布局
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

## 已知问题

1. **沙箱内无法渲染 PNG**：Chromium EPERM，只能输出 SVG
2. **沙箱内无法推送画布**：`~/.local/share/` 写入受限，需 escalation
3. **Excalidraw 服务可能未运行**：`--check-only` 可检测，`--start` 可尝试启动
4. **Render bundle 路径硬编码**：默认 `~/WorkSpace/render-test/`，需通过 `EXCALIDRAW_RENDER_BUNDLE` 环境变量覆盖
5. **Playwright 全局安装**：非项目本地，版本可能漂移

## Git 历史

```
4e9d214 feat: Phase 2 - e2e test suite, fixture flowchart
8202947 feat: Phase 1 - sandbox fallback, service detection, package.json
cd4cdbb feat: initial commit - SKILL.md, scripts, references, agents
```
