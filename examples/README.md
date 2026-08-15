# more-chat-excalidraw 真实案例

本目录只保留真实项目案例，避免旧的演示型样例干扰维护和展示。v0.1.0 首个公开案例来自真实的 `more-paper-workflow` 工作流。

## 当前案例

- [more-paper-workflow-video-rich-sketch](./more-paper-workflow-video-rich-sketch/)

这是基于真实 GitHub 项目 `bingyunjiang/more-paper-workflow` 制作的 6 帧 Excalidraw 视频录屏白板，当前目录发布主白板资产：

- 完整 `.excalidraw` 白板
- 主 PNG / SVG / PDF
- 统一的 16:9 storyboard 主画布
- 中文手绘字体与英文层级
- 安全边距、动画顺序和讲解结构

## 校验

主白板保留结构校验结果，并基于真实 PNG 做过人工视觉复核；自动生成的 storyboard smoke fixture 使用 strict 视觉质量门：

```bash
python3 scripts/validate_excalidraw.py <file.excalidraw> --visual
```

## 来源信息

- GitHub: <https://github.com/bingyunjiang/more-paper-workflow>
- 作者: Bingyun Jiang / bingyunjiang
- 日期: 2026-08-15
