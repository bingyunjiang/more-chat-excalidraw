# more-chat-excalidraw 开发大纲

> 最后更新：2026-08-07

## 项目目标

通过自然对话生成、预览、打开和迭代编辑本地 Excalidraw 画布。核心闭环：理解意图 → 生成 JSON → 校验 → 渲染预览 → 打开/迭代。

## 当前状态总览

| 模块 | 状态 | 备注 |
|---|---|---|
| SKILL.md | ✅ 完成 | 五步闭环、质量规则、资源说明 |
| references/excalidraw-schema.md | ✅ 完成 | v2 JSON 结构速查 |
| references/diagram-templates.md | ✅ 完成 | 六类图表模板 + 色板 + 最小示例 |
| agents/openai.yaml | ✅ 完成 | 显示名、描述、默认提示词 |
| scripts/validate_excalidraw.py | ✅ 完成 | smoke test 通过 |
| scripts/render_preview.js | ✅ 已修复 | 沙箱内自动 fallback 到 SVG 渲染 |
| scripts/open_in_excalidraw.js | ✅ 已修复 | 沙箱内给出明确提示，escalation 下正常工作 |
| git 仓库 | ✅ 已初始化 | |
| README.md | ❌ 不存在 | |
| HANDOFF.md | ❌ 不存在 | |
| package.json | ✅ 已创建 | 声明 Playwright 为 optional peerDependency |
| 测试 | ✅ 已创建 | test_e2e.sh 5/5 通过 |
| output/ 目录 | ✅ 已创建 | 含 fixture-flowchart.excalidraw |

## 环境依赖（已验证）

- 本地 Excalidraw：http-server on localhost:5001，launchd 自启，当前未运行
- Playwright：全局安装于 ~/.npm-global/，Chromium 缓存在 ~/Library/Caches/ms-playwright/
- Render bundle：~/WorkSpace/render-test/（index.html + render-entry.js + render-bundle.js）
- 自定义 Node：~/.local/bin/node

---

## 开发路线

### Phase 1：基础设施与权限修复（优先级最高）

- [x] **1.1 初始化 git 仓库**
  - git init，添加 .gitignore（node_modules、output、*.png、*.svg）
  - 首次 commit：所有现有文件

- [x] **1.2 修复 render_preview.js 的沙箱权限问题**
  - 当前问题：http.createServer().listen() 在沙箱内 EPERM
  - 方案 A：为脚本添加 escalation 支持（require_escalated）
  - 方案 B：改用 qlmanage -t 做 QuickLook 预览（已批准前缀 qlmanage -t）
  - 方案 C：在 render_preview.js 中用 child_process.execFile('qlmanage', ...) 做备选渲染
  - 推荐：方案 B+C 双路径——优先 Playwright 渲染（高质量），失败时 fallback 到 qlmanage

- [x] **1.3 修复 open_in_excalidraw.js 的沙箱权限问题**
  - 当前问题：copyFileSync 到 ~/.local/share/excalidraw/ 时 EPERM
  - 方案：为脚本添加 escalation 支持，或改用 cp 命令（需 escalation）
  - 另考虑：如果 Excalidraw 未运行，自动 launchctl start com.excalidraw.editor

- [x] **1.4 添加 package.json**
  - 声明 Playwright 为 optional peer dependency
  - 添加 scripts：render、open、validate、test

- [x] **1.5 创建 output/ 目录**
  - 添加 .gitkeep

### Phase 2：核心闭环跑通

- [x] **2.1 端到端测试：生成一个简单流程图**
  - 手动构造一个 3 节点流程图 .excalidraw
  - validate → render → open 全链路跑通
  - 验证 Excalidraw 页面能正确加载和显示

- [x] **2.2 编写集成测试脚本**
  - scripts/test_e2e.sh：自动构造 → 校验 → 渲染 → 对比
  - 用已知 fixture 文件做回归

- [x] **2.3 确保 Excalidraw 本地服务可启动**
  - 检测 localhost:5001 是否可达
  - 不可达时提示用户启动或自动启动

### Phase 3：质量与文档

- [x] **3.1 编写 README.md**
  - 项目简介、安装依赖、快速开始、脚本说明
  - 环境要求（Node.js、Playwright、本地 Excalidraw）

- [x] **3.2 编写 HANDOFF.md**
  - 当前状态、已知问题、下一步计划
  - 依赖版本和路径快照

- [x] **3.3 增强 validate_excalidraw.py**
  - 添加更多校验规则：箭头绑定完整性、文本溢出检测、groupIds 一致性
  - 添加 --json 输出模式，方便脚本解析

- [x] **3.4 增强 render_preview.js**
  - 双路径渲染：Playwright 优先，qlmanage 备选
  - 输出渲染质量元数据（元素数、尺寸、渲染时间）
  - 支持 --format svg|png|both

### Phase 4：增强功能

- [ ] **4.1 增量更新支持**
  - SKILL.md 要求"保持既有 id 不变"的增量更新
  - 编写 scripts/merge_excalidraw.py：合并新旧元素，保留旧 id，新增元素用新 id
  - 支持删除元素（标记 isDeleted）

- [ ] **4.2 更多图表模板**
  - 补充：甘特图、鱼骨图、价值流图、状态机图
  - 模板中增加中文标注和实用示例

- [ ] **4.3 智能布局**
  - 编写 scripts/auto_layout.py：自动排列节点位置
  - 支持纵向/横向/层次/力导向布局

- [ ] **4.4 多语言支持**
  - 文本宽度估算：中文 1.0×fontSize，英文 0.6×fontSize
  - 混合文本精确估算

### Phase 5：发布与维护

- [ ] **5.1 版本号与 CHANGELOG**
  - 语义化版本号（当前 v0.1.0）
  - CHANGELOG.md 追踪每次变更

- [ ] **5.2 CI/CD**
  - GitHub Actions：validate + render smoke test
  - 自动发布到 skill 仓库

- [ ] **5.3 用户文档与示例**
  - 6 类图表的完整示例文件
  - 使用视频或 GIF 动画

---

## 已知问题与风险

1. **沙箱权限**：render 和 open 脚本在 Codex 沙箱内无法直接运行，需要 escalation 或备选方案
2. **Excalidraw 本地服务**：当前未运行，launchd 配置存在但可能未加载
3. **Playwright 依赖**：全局安装而非项目本地，版本可能漂移
4. **render bundle 路径硬编码**：默认指向 ~/WorkSpace/render-test/，不够通用
5. **无 git 历史**：无法追踪变更，回滚困难

## 里程碑

| 里程碑 | 目标 | 预计完成 |
|---|---|---|
| M1：基础设施 | git + package.json + 权限修复 | Phase 1 完成时 |
| M2：闭环跑通 | 端到端测试通过 | Phase 2 完成时 |
| M3：可交付 | README + HANDOFF + 增强校验 | Phase 3 完成时 |
| M4：可用 | 增量更新 + 更多模板 + 智能布局 | Phase 4 完成时 |
| M5：可发布 | 版本号 + CI + 文档 | Phase 5 完成时 |
