# 语义色板与主题系统

> 用于 Excalidraw 图表生成时自动应用颜色方案。所有颜色值按语义组织，支持 4 套一键切换主题。

## 1. 语义色板

同一图内只用一套色板，按语义选择填充色和文字色。

### 文字色

| 用途 | 色值 | 说明 |
|------|------|------|
| 标题 | `#1e40af` 深蓝 | 图表主标题、section 标题 |
| 副标题 | `#3b82f6` 中蓝 | 子标题、分组名称 |
| 正文 | `#374151` 深灰 | 正文文字、节点标签 |
| 强调 | `#f59e0b` 金色 | 关键路径、高亮数字 |
| 次要 | `#868e96` 中灰 | 辅助文字、时间戳、序号 |
| 连线 | `#868e96` 中灰 | 箭头、连线、标注线 |

### 填充色（8 种语义）

| 语义 | 色值 | 用途 | 文字色（对比度） |
|------|------|------|------------------|
| 输入/数据源 | `#a5d8ff` 浅蓝 | API 网关、输入框、用户入口 | `#1e3a5f` |
| 成功/输出 | `#b2f2bb` 浅绿 | 完成状态、输出端、绿灯 | `#1e3a3a` |
| 警告/外部依赖 | `#ffd8a8` 浅橙 | 外部系统、第三方服务、告警 | `#5f3a1e` |
| 处理中/中间件 | `#d0bfff` 浅紫 | 消息队列、处理节点、中间件 | `#2e1e5f` |
| 错误/关键 | `#ffc9c9` 浅红 | 错误状态、关键路径、阻断 | `#5f1e1e` |
| 备注/决策 | `#fff3bf` 浅黄 | 决策节点、注释、备注 | `#5f4a1e` |
| 存储/缓存 | `#c3fae8` 浅青 | 数据库、缓存、文件存储 | `#1e4a3a` |
| 分析/指标 | `#fcc2d7` 浅粉 | 监控面板、指标、分析报告 | `#5f1e3a` |

### 分层背景色（frame 用）

| 层 | 色值 | 透明度 | 用途 |
|----|------|--------|------|
| 前端/UI | `#dbe4ff` | 30% | 用户层、展示层 |
| 逻辑/处理 | `#e5dbff` | 30% | 应用层、服务层 |
| 数据/工具 | `#d3f9d8` | 30% | 数据层、基础设施 |

### 对比度规则

- 白底（`#ffffff`）上文字不低于 `#757575`（3:1 对比度）
- 浅色填充（`#a5d8ff`、`#b2f2bb` 等）上用深色变体文字（见上表"文字色"列）
- 深色背景（如 blueprint 主题的 `#1e3a5f`）上用浅色文字 `#e8f4ff`
- 重要文字（标题、关键数字）对比度不低于 4.5:1

## 2. 主题系统

四种可一键切换的主题，theme 参数影响所有元素的颜色/roughness/strokeWidth。

### default（默认）

Excalidraw 默认风格，手绘感适中，彩色填充。

```json
{
  "theme": "default",
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffffff",
  "roughness": 1,
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "fillStyle": "solid",
  "opacity": 100
}
```

### sketch（手绘）

更强的手绘感，更粗的描边，适合创意/概念图。

```json
{
  "theme": "sketch",
  "strokeColor": "#2b2b2b",
  "backgroundColor": "#ffffff",
  "roughness": 2,
  "strokeWidth": 3,
  "strokeStyle": "solid",
  "fillStyle": "hachure",
  "opacity": 100
}
```

### blueprint（蓝图）

蓝底白线，技术蓝图风格，适合架构图/设计图。

```json
{
  "theme": "blueprint",
  "viewBackgroundColor": "#1e3a5f",
  "strokeColor": "#e8f4ff",
  "backgroundColor": "#1e3a5f",
  "roughness": 0,
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "fillStyle": "solid",
  "opacity": 90
}
```
蓝图主题特殊规则：
- 文字色统一为 `#e8f4ff`
- 连线色统一为 `#64b5f6`
- 填充色使用 `#1e3a5f` 的变体（`#2a4a6f`、`#3a5a7f`）
- 不透明度降至 90
- roughness 设为 0（干净线条）

### minimal（极简）

纯黑白，零手绘，干净线条，适合正式文档/印刷。

```json
{
  "theme": "minimal",
  "strokeColor": "#000000",
  "backgroundColor": "#ffffff",
  "roughness": 0,
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "fillStyle": "solid",
  "opacity": 100
}
```
极简主题特殊规则：
- 所有彩色填充降级为白色或灰色（`#f5f5f5`）
- 强调色降级为黑色加粗（`strokeWidth: 2`）
- 分层背景色降级为灰色（`#f0f0f0`）
- 连线统一为 `#666666`

## 3. 主题参数化

生成时通过 `theme` 参数控制：

```json
{
  "template": "flowchart",
  "theme": "blueprint",
  "palette": {
    "strokeColor": "#e8f4ff",
    "backgroundColor": "#1e3a5f",
    "roughness": 0
  }
}
```

- 主题可覆盖：用户选择主题后，可单独调整某个参数（如"用 blueprint 主题但 roughness=2"）
- 主题感知的语义色板：不同主题下，8 种语义填充色自动映射到主题色系

## 4. 主题 — 语义色板映射

| 主题 | 输入/数据源 | 成功/输出 | 警告/外部 | 处理中 | 错误/关键 | 备注/决策 | 存储/缓存 | 分析/指标 |
|------|------------|----------|----------|--------|----------|----------|----------|----------|
| default | `#a5d8ff` | `#b2f2bb` | `#ffd8a8` | `#d0bfff` | `#ffc9c9` | `#fff3bf` | `#c3fae8` | `#fcc2d7` |
| sketch | `#87ceeb` | `#98fb98` | `#f4a460` | `#b19cd9` | `#f08080` | `#f0e68c` | `#7fffd4` | `#dda0dd` |
| blueprint | `#4a7ab5` | `#4a9a6a` | `#b58a4a` | `#7a5ab5` | `#b54a4a` | `#b5a54a` | `#4a9a8a` | `#b56a8a` |
| minimal | `#e0e0e0` | `#e0e0e0` | `#f5f5f5` | `#e0e0e0` | `#cccccc` | `#f5f5f5` | `#e0e0e0` | `#e0e0e0` |

---

> 参考来源：coleam00/excalidraw-diagram-skill（4339★）的语义色板、axtonliu/obsidian-visual-skills（3278★）的分层背景、drawmode（16★）的 4 套主题
