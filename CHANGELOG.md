# Changelog

本项目的所有显著变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-08-15

这是 more-chat-excalidraw 的初始公开版本，包含此前开发阶段积累并完成验收的能力。

### Added

- 自然语言 → IR → Excalidraw v2 → 校验 → SVG/PNG/PDF 预览 → 本地编辑的完整闭环。
- 流程图、架构图、时序图、思维导图、泳道图、ER 图、层级图、关系图、对比图和时间线图共 10 种模板。
- 4 套主题、5 套手绘 preset、语义色板、50+ 技术组件样式和自包含 MIT Library。
- Mermaid、知识图谱、Graphviz、MCP、增量编辑、动画 GIF 和实时预览能力。
- 全部模板统一的中文手写字体策略、`visual_contract` 视觉追溯契约和 strict 视觉质量门。
- `video-storyboard` 交付模式：共享 16:9 画布、安全边距、双语字体、逐帧导出、contact sheet 和 QA 报告。
- 真实 `more-paper-workflow` 视频白板案例，作为 README 的初始宣讲示例。

### Changed

- 修正箭头 `width/height` 与 `points` 不一致、中文字体回退、普通文本碰撞、旋转边界、低对比度和小字号等交付问题。
- 模板选择器增加 delivery profile，并修复 `ER` 等短 Latin alias 在普通单词中的误匹配。
- 渲染链明确区分 native 与 fallback；fallback 会写出 manifest，`--require-native` 和 `--require-png` 可作为正式交付质量门。
- 文档、Library manifest、MCP server、web bundle 和 package metadata 统一为 `v0.1.0`。

### License

MIT License，详见 [LICENSE](LICENSE)。
