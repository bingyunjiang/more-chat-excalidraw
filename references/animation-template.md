# 动画关键帧模板

> 支持 `customData.animate` 字段，使生成的 Excalidraw 图可拖入 excalidraw-animate 生成动画。
> 参考：excalimate/excalidraw-animate（50★）、axtonliu/obsidian-visual-skills（3278★）

## 1. 动画字段规范

在 Excalidraw 元素的 `customData` 中嵌入动画信息：

```json
{
  "id": "rect-001",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 200, "height": 80,
  "customData": {
    "animate": {
      "order": 1,
      "duration": 500,
      "delay": 0,
      "type": "fade-in",
      "group": "title"
    }
  }
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `order` | number | 否 | 0 | 动画播放顺序（1=最先，越大越后） |
| `duration` | number | 否 | 500 | 动画持续时间（毫秒） |
| `delay` | number | 否 | 0 | 延迟播放（毫秒） |
| `type` | string | 否 | "fade-in" | 动画类型（见下） |
| `group` | string | 否 | null | 分组名，同组元素同时播放 |

## 2. 动画类型

| 类型 | 说明 | 效果 |
|------|------|------|
| `fade-in` | 淡入 | 透明度从 0 → 100 |
| `slide-up` | 上滑 | 从 y+20 滑动到原位 |
| `slide-left` | 左滑 | 从 x+20 滑动到原位 |
| `slide-right` | 右滑 | 从 x-20 滑动到原位 |
| `grow` | 放大 | 从 scale 0 → 1 |
| `draw` | 绘制 | 描边逐渐出现（箭头/线） |
| `highlight` | 高亮 | 颜色闪烁（黄色 → 本色） |
| `bounce` | 弹跳 | 弹跳出现 |

## 3. 动画顺序规则（推荐）

自然阅读顺序，逐层展开：

| 顺序 | 元素类型 | 动画类型 | 说明 |
|------|----------|---------|------|
| 1 | 图表标题 | fade-in | 最先出现 |
| 2 | frame/分组名称 | fade-in | 框架标题 |
| 3 | 主要节点 | slide-up | 核心概念 |
| 4 | 次要节点 | slide-up | 补充信息 |
| 5 | 连线/箭头 | draw | 结构关系 |
| 6 | 标注文字 | fade-in | 解释说明 |
| 7 | 装饰元素 | fade-in | 最后出现 |

## 4. 完整示例：动画流程图

```json
{
  "elements": [
    // 标题（order=1）
    {
      "id": "title-1", "type": "text",
      "x": 150, "y": 40, "width": 200, "height": 28,
      "strokeColor": "#1e40af", "fontSize": 22,
      "text": "用户注册流程",
      "customData": { "animate": { "order": 1, "duration": 400, "type": "fade-in" } }
    },
    // 开始节点（order=2）
    {
      "id": "start-1", "type": "ellipse",
      "x": 200, "y": 100, "width": 120, "height": 60,
      "backgroundColor": "#a5d8ff",
      "boundElements": [{ "id": "txt-start-1", "type": "text" }],
      "customData": { "animate": { "order": 2, "duration": 500, "type": "slide-up" } }
    },
    { "id": "txt-start-1", "type": "text", "x": 220, "y": 118,
      "width": 80, "height": 25, "fontSize": 18, "text": "开始",
      "containerId": "start-1", "textAlign": "center", "verticalAlign": "middle",
      "customData": { "animate": { "order": 2, "duration": 500, "type": "fade-in", "delay": 200 } } },
    // 箭头 1（order=5，draw 类型）
    {
      "id": "arr-1", "type": "arrow",
      "x": 260, "y": 160, "width": 0, "height": 60,
      "points": [[0, 0], [0, 60]],
      "startBinding": { "elementId": "start-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "proc-1", "focus": 0.5, "gap": 0 },
      "endArrowhead": "arrow",
      "customData": { "animate": { "order": 5, "duration": 300, "type": "draw" } }
    },
    // 处理节点（order=3）
    {
      "id": "proc-1", "type": "rectangle",
      "x": 160, "y": 220, "width": 200, "height": 80,
      "roundness": { "type": 3 },
      "boundElements": [{ "id": "txt-proc-1", "type": "text" }],
      "customData": { "animate": { "order": 3, "duration": 500, "type": "slide-up" } }
    },
    { "id": "txt-proc-1", "type": "text", "x": 180, "y": 248,
      "width": 160, "height": 25, "fontSize": 18, "text": "填写注册信息",
      "containerId": "proc-1", "textAlign": "center", "verticalAlign": "middle",
      "customData": { "animate": { "order": 3, "duration": 500, "type": "fade-in", "delay": 200 } } },
    // 结束节点（order=4）
    {
      "id": "end-1", "type": "ellipse",
      "x": 200, "y": 360, "width": 120, "height": 60,
      "backgroundColor": "#b2f2bb",
      "boundElements": [{ "id": "txt-end-1", "type": "text" }],
      "customData": { "animate": { "order": 4, "duration": 500, "type": "slide-up" } }
    },
    { "id": "txt-end-1", "type": "text", "x": 220, "y": 378,
      "width": 80, "height": 25, "fontSize": 18, "text": "完成",
      "containerId": "end-1", "textAlign": "center", "verticalAlign": "middle",
      "customData": { "animate": { "order": 4, "duration": 500, "type": "fade-in", "delay": 200 } } }
  ]
}
```

## 5. excalidraw-animate 兼容性

此模板遵循 excalidraw-animate 的 `customData.animate` 规范：

- 元素可以直接拖入 excalidraw-animate 播放动画
- 动画顺序由 `order` 字段控制
- 同组元素（`group` 相同）同时播放
- 文字元素自动跟随其容器元素的动画顺序

## 6. 关键帧序列（高级）

对于需要预定义关键帧序列的场景：

```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [
    // 所有元素（含动画信息）
  ],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  },
  "customData": {
    "animation": {
      "frames": [
        { "title": "第 1 帧：标题", "order": 1, "elements": ["title-1"] },
        { "title": "第 2 帧：核心节点", "order": 2, "elements": ["start-1", "proc-1", "end-1"] },
        { "title": "第 3 帧：连线", "order": 3, "elements": ["arr-1", "arr-2"] },
        { "title": "第 4 帧：完整图", "order": 4, "elements": [] }
      ],
      "loop": false,
      "interval": 2000
    }
  }
}
```

## 7. 生成建议

- 简单图（≤5 节点）：动画顺序 1-3，每个节点 400ms
- 中等图（6-12 节点）：动画顺序 1-5，分组播放
- 复杂图（>12 节点）：动画顺序 1-7，分组播放，每组间隔 1s
- 连线动画建议使用 `draw` 类型
- 标题和关键文字使用 `fade-in` 类型
- 主要节点使用 `slide-up` 或 `grow` 类型
