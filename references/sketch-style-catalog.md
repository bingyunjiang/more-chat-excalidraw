# Sketch style catalog

这是 Excalidraw sketch 的自有小型目录，借鉴 `beautiful-feishu-whiteboard` 的 catalogue 思路，但色板、规则与实现均为本项目自编，不复制其资产或媒介限制。

| preset | level / formality / vibe | 适用模板 | 色板 | 字体 | 节点与箭头 | 标题与禁忌 |
|---|---|---|---|---|---|---|
| engineering-notebook | 平衡 / 半正式 / field notes | flowchart, swimlane | 纸白、暖灰、琥珀 | Ma Shan Zheng + Virgil | 留白卡片、短直线 | 标题左上；禁用高饱和背景 |
| research-board | 克制 / 正式 / quiet analytical | flowchart, architecture | 冷灰、青蓝 | Ma Shan Zheng + Virgil | 证据节点、细箭头 | 标题安全区；禁用装饰性图标 |
| root-cause | 克制 / 半正式 / diagnostic | relationship, flowchart | 酒红、砖红、米白 | Ma Shan Zheng + Virgil | 因果曲线、返工虚线 | 标题突出根因；禁用无方向网线 |
| mechanism-map | 平衡 / 半正式 / causal | relationship | 橄榄、苔绿、纸白 | Ma Shan Zheng + Virgil | 中心主题、语义曲线 | 标题居中；禁用重复标签 |
| review-markup | 醒目 / 正式 / annotated critique | architecture, swimlane | 炭黑、赭黄、警示橙 | Ma Shan Zheng + Virgil | 依赖线、风险批注 | 标题留足批注区；禁用整面红色 |

所有 preset 保留 `theme=sketch` 兼容；IR 使用 `sketchStyle`（或兼容别名 `preset`）。
