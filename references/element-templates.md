# 元素级构建块模板

> 独立可复用的 Excalidraw 元素模板，按需组合生成图表。每个模板标注必填字段、可选字段、默认值。
> 参考：coleam00/excalidraw-diagram-skill（4339★）的模板化生成思路

## 1. 矩形 rectangle

用于：流程步骤、架构组件、实体、actor

```json
{
  "id": "<unique-id>",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 200, "height": 80,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": [{ "id": "<text-id>", "type": "text" }],
  "updated": 1,
  "link": null,
  "locked": false
}
```

**必填字段**：`id`, `type`, `x`, `y`, `width`, `height`
**常用尺寸**：
- 标准节点：200×60（文本 16-18px）或 200×80（文本 18-20px）
- 宽节点：240×60（用于长标签）
- 高节点：200×100（用于多行文字）
- 小节点：140×50（用于标注）

## 2. 椭圆 ellipse

用于：开始/结束节点、数据库、标记点

```json
{
  "id": "<unique-id>",
  "type": "ellipse",
  "x": 100, "y": 100,
  "width": 120, "height": 60,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": [{ "id": "<text-id>", "type": "text" }],
  "updated": 1,
  "link": null,
  "locked": false
}
```

**常用尺寸**：
- 开始/结束节点：120×60（文本 18px）
- 数据库节点：120×60（椭圆，或 150×70）
- 标记点：14×14（小圆点）
- 时间轴节点：16×16（圆点）

## 3. 菱形 diamond

用于：决策节点、判断分支

```json
{
  "id": "<unique-id>",
  "type": "diamond",
  "x": 100, "y": 100,
  "width": 160, "height": 80,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": [{ "id": "<text-id>", "type": "text" }],
  "updated": 1,
  "link": null,
  "locked": false
}
```

**常用尺寸**：
- 标准决策：160×80（文本 16px）
- 宽决策：200×80（文本 16px，用于长条件文字）

## 4. 箭头 arrow

用于：连接线、有向边、流程方向

```json
{
  "id": "<unique-id>",
  "type": "arrow",
  "x": 100, "y": 100,
  "width": 0, "height": 60,
  "angle": 0,
  "strokeColor": "#868e96",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 2 },
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 60]],
  "startBinding": { "elementId": "<from-id>", "focus": 0.5, "gap": 8 },
  "endBinding": { "elementId": "<to-id>", "focus": 0.5, "gap": 8 },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

**四种箭头类型**：

| 类型 | endArrowhead | 用途 |
|------|-------------|------|
| 有向边 | `"arrow"` | 流程图、调用关系 |
| 双向边 | `"arrow"`（双端） | 请求-响应、双向调用 |
| 虚线边 | `strokeStyle: "dashed"` | 数据流、异步消息 |
| 标注线 | `startArrowhead: null, endArrowhead: null` | 注释指向 |

**points 坐标计算**：
- 垂直向下：`[[0, 0], [0, height]]`
- 水平向右：`[[0, 0], [width, 0]]`
- 斜线：`[[0, 0], [dx, dy]]`
- 折线：`[[0, 0], [dx, 0], [dx, dy]]`

**箭头绑定**：
- `startBinding.elementId`：起点绑定的元素 ID
- `endBinding.elementId`：终点绑定的元素 ID
- `focus`：0-1 之间的值，表示箭头在元素边框上的触点比例（0=左上角，0.5=水平中点，1=右下角）
- `gap`：箭头尖端与元素边框的距离，通常 8-12px

## 5. 文本 text（独立）

用于：标题、独立标注、注释

```json
{
  "id": "<unique-id>",
  "type": "text",
  "x": 100, "y": 100,
  "width": 200, "height": 28,
  "angle": 0,
  "strokeColor": "#374151",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "示例文字",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "left",
  "verticalAlign": "top",
  "containerId": null,
  "originalText": "示例文字",
  "lineHeight": 1.25
}
```

**字体大小规范**：

| 用途 | fontSize | 说明 |
|------|----------|------|
| 图表标题 | 24-28px | 居中，独立文字 |
| 节点标签 | 16-20px | 容器内绑定 |
| 辅助文字 | 13-14px | 日期、序号、标注 |
| 小号标注 | 11-12px | 图例、注释 |

**文字宽度估算**：
- 中文字符 ≈ 1.0 × fontSize
- ASCII 字符 ≈ 0.6 × fontSize
- 数字 ≈ 0.6 × fontSize
- 示例："处理步骤" 4 中文字 × 20px = 80px 宽度

## 6. 文本 text（容器内绑定）

用于：节点标签、按钮文字、框内文字

```json
{
  "id": "<text-id>",
  "type": "text",
  "x": 120, "y": 130,
  "width": 160, "height": 28,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "标签文字",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "<shape-id>",
  "originalText": "标签文字",
  "lineHeight": 1.25
}
```

**坐标计算**：
- `x = shape.x + (shape.width - text.width) / 2`
- `y = shape.y + (shape.height - text.height) / 2`
- 注意：`textAlign: "center"` 时，x 可以简单设为 shape.x + 20，宽度 = shape.width - 40

## 7. 直线 line

用于：时间轴、分隔线、生命线、基线

```json
{
  "id": "<unique-id>",
  "type": "line",
  "x": 60, "y": 140,
  "width": 480, "height": 0,
  "angle": 0,
  "strokeColor": "#868e96",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 60,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "points": [[0, 0], [480, 0]]
}
```

**常用变体**：

| 用途 | strokeWidth | strokeStyle | roughness | 说明 |
|------|-----------|-------------|-----------|------|
| 时间轴 | 3 | solid | 1 | 粗实线 |
| 生命线 | 1 | dashed | 0 | 细虚线 |
| 分隔线 | 1 | dashed | 0 | 分隔区域 |
| 基线 | 1 | solid | 0 | 标注基线 |

## 8. frame（框架）

用于：分层区域、分组标题、层级标注

```json
{
  "id": "<unique-id>",
  "type": "frame",
  "x": 40, "y": 40,
  "width": 520, "height": 100,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#dbe4ff",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 30,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "seed": 0,
  "version": 1,
  "versionNonce": 0,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "name": "层名称"
}
```

**frame 规范**：
- `opacity` 建议 20-40（半透明背景）
- 子元素通过 `frameId` 关联（非 boundElements）
- `name` 字段显示为框架标题
- frame 不绑定文字，标题用独立 text 元素

## 9. 模板组合规则

### 规则 1：文字绑定

图形 + 文字绑定：
```
图形: boundElements: [{ "id": "<text-id>", "type": "text" }]
文字: containerId: "<shape-id>"
```

### 规则 2：箭头绑定

箭头 + 节点绑定：
```
箭头: startBinding: { "elementId": "<from-id>", "focus": 0.5, "gap": 8 }
箭头: endBinding: { "elementId": "<to-id>", "focus": 0.5, "gap": 8 }
```

### 规则 3：分组

同组元素共享 groupIds：
```
元素A: groupIds: ["group-1"]
元素B: groupIds: ["group-1"]
嵌套分组：groupIds: ["group-parent", "group-child"]
```

### 规则 4：frame 关联

子元素声明 frameId：
```
子元素: frameId: "frame-user"
frame: （无需额外声明，由子元素 frameId 隐式关联）
```

### 规则 5：id 生成

- 字母数字组合，如 `rect-001`、`arrow-002`
- 全局唯一，删除后不得复用
- 增量编辑时保留旧 id，新增元素用新 id
- 建议格式：`<type-prefix>-<seq>`，如 `proc-001`、`dec-001`

## 10. 快速参考

| 元素类型 | 必填字段 | 额外常见字段 |
|----------|---------|------------|
| rectangle | id, type, x, y, width, height | roundness, boundElements |
| ellipse | id, type, x, y, width, height | boundElements |
| diamond | id, type, x, y, width, height | boundElements |
| arrow | id, type, x, y, points | startBinding, endBinding, endArrowhead |
| text（独立） | id, type, x, y, text, fontSize | textAlign, verticalAlign |
| text（绑定） | id, type, x, y, text, fontSize, containerId | textAlign: "center", verticalAlign: "middle" |
| line | id, type, x, y, points | strokeWidth, strokeStyle |
| frame | id, type, x, y, width, height, name | backgroundColor, opacity |
