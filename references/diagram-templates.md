# 图表模板与布局规范

先选类型，再按对应布局生成。默认画布方向：节点按从上到下、从左到右排布，间距 60–80px；字体 20–28px。

## 模板选择

| 用户意图 | 模板 | 核心结构 |
|---|---|---|
| 流程/步骤/顺序 | 流程图 Flowchart | 纵向或横向：矩形步骤 + 菱形决策 + 箭头 |
| 系统组件/调用关系 | 架构图 Architecture | 分层：用户层 → 应用层 → 服务层 → 数据层，层间大箭头 |
| 先后消息/时间顺序 | 时序图 Sequence | 三条竖线（角色）+ 横向箭头消息，编号 1/2/3 |
| 头脑风暴/知识点 | 思维导图 Mind Map | 中心主题 + 一级/二级分支 |
| 角色职责/多部门流程 | 泳道图 Swimlane | 水平泳道按角色分区，流程穿越泳道 |
| 实体与关系 | ER 图 ERD | 实体矩形 + 关系菱形/连线 + 基数标注 |
| 组织/内容/系统拆解 | 层级图 Hierarchy | 自上而下树形结构，节点逐级展开 |
| 要素间依赖/影响 | 关系图 Relationship | 节点 + 连线 + 关系标注，无严格方向 |
| 方案/观点对照分析 | 对比图 Comparison | 左右两栏或表格，标明比较维度 |
| 事件发展/项目进度 | 时间线图 Timeline | 水平时间轴 + 关键节点 + 事件标注 |

## 色板（完整版见 color-palette.md）

同一图内只用一个色板。此处列出常用色，完整语义色板见 `color-palette.md`。

- 文字色：标题 `#1e40af` 深蓝、正文 `#374151` 深灰、强调 `#f59e0b` 金色
- 填充色：`#a5d8ff` 浅蓝（输入/数据源）、`#b2f2bb` 浅绿（成功/输出）、`#ffd8a8` 浅橙（警告/外部依赖）、`#d0bfff` 浅紫（处理中）、`#ffc9c9` 浅红（错误/关键）、`#fff3bf` 浅黄（备注/决策）
- 连线：`#868e96`，粗线 `strokeWidth: 2`
- 分层背景（opacity: 30）：`#dbe4ff` 前端/UI、`#e5dbff` 逻辑/处理、`#d3f9d8` 数据/工具

---

## 1. 流程图 Flowchart

开始 → 处理 → 决策 → 重试/完成。三个元素 + 菱形决策 + 箭头绑定。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "start-1", "type": "ellipse", "x": 100, "y": 80,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 1, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "proc-1", "type": "rectangle", "x": 100, "y": 200,
      "width": 200, "height": 80, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#ffffff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 2, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-proc-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-proc-1", "type": "text", "x": 130, "y": 230,
      "width": 140, "height": 28, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 3, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "处理步骤", "fontSize": 24, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "proc-1", "originalText": "处理步骤",
      "lineHeight": 1.25
    },
    {
      "id": "end-1", "type": "ellipse", "x": 100, "y": 340,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 4, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "arr-1", "type": "arrow", "x": 160, "y": 140,
      "width": 0, "height": 60, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 5, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 60]],
      "startBinding": { "elementId": "start-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "proc-1", "focus": 0.5, "gap": 0 },
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-2", "type": "arrow", "x": 160, "y": 280,
      "width": 0, "height": 60, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 6, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 60]],
      "startBinding": { "elementId": "proc-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "end-1", "focus": 0.5, "gap": 0 },
      "startArrowhead": null, "endArrowhead": "arrow"
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 2. 架构图 Architecture

三层架构：用户层 → 应用层 → 数据层，用 frame 承载层标题，层间大箭头。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "frame-user", "type": "frame", "x": 40, "y": 40,
      "width": 520, "height": 100, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#dbe4ff",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
      "roughness": 1, "opacity": 30, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 10, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false, "name": "用户层"
    },
    {
      "id": "frame-app", "type": "frame", "x": 40, "y": 220,
      "width": 520, "height": 100, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#e5dbff",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
      "roughness": 1, "opacity": 30, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 11, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false, "name": "应用层"
    },
    {
      "id": "frame-data", "type": "frame", "x": 40, "y": 400,
      "width": 520, "height": 100, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d3f9d8",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
      "roughness": 1, "opacity": 30, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 12, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false, "name": "数据层"
    },
    {
      "id": "web-1", "type": "rectangle", "x": 100, "y": 60,
      "width": 160, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": "frame-user",
      "roundness": { "type": 3 }, "seed": 13, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-web-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-web-1", "type": "text", "x": 120, "y": 78,
      "width": 120, "height": 25, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 14, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "Web 前端", "fontSize": 20, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "web-1", "originalText": "Web 前端", "lineHeight": 1.25
    },
    {
      "id": "api-1", "type": "rectangle", "x": 340, "y": 60,
      "width": 160, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": "frame-user",
      "roundness": { "type": 3 }, "seed": 15, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-api-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-api-1", "type": "text", "x": 365, "y": 78,
      "width": 110, "height": 25, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 16, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "API 网关", "fontSize": 20, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "api-1", "originalText": "API 网关", "lineHeight": 1.25
    },
    {
      "id": "svc-1", "type": "rectangle", "x": 100, "y": 240,
      "width": 160, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": "frame-app",
      "roundness": { "type": 3 }, "seed": 17, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-svc-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-svc-1", "type": "text", "x": 120, "y": 258,
      "width": 120, "height": 25, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 18, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "订单服务", "fontSize": 20, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "svc-1", "originalText": "订单服务", "lineHeight": 1.25
    },
    {
      "id": "db-1", "type": "ellipse", "x": 120, "y": 420,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#c3fae8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": "frame-data",
      "roundness": null, "seed": 19, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-db-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-db-1", "type": "text", "x": 140, "y": 438,
      "width": 80, "height": 25, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 20, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "PostgreSQL", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "db-1", "originalText": "PostgreSQL", "lineHeight": 1.25
    },
    {
      "id": "arr-layer-1", "type": "arrow", "x": 180, "y": 120,
      "width": 0, "height": 100, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 21, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 100]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-layer-2", "type": "arrow", "x": 180, "y": 300,
      "width": 0, "height": 100, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 22, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 100]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 3. 时序图 Sequence

三个角色 + 横向箭头消息，编号 1/2/3。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "actor-1", "type": "rectangle", "x": 80, "y": 40,
      "width": 100, "height": 40, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 30, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-act-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-act-1", "type": "text", "x": 95, "y": 49,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 31, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "用户", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "actor-1", "originalText": "用户", "lineHeight": 1.25
    },
    {
      "id": "actor-2", "type": "rectangle", "x": 280, "y": 40,
      "width": 100, "height": 40, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 32, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-act-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-act-2", "type": "text", "x": 295, "y": 49,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 33, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "服务端", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "actor-2", "originalText": "服务端", "lineHeight": 1.25
    },
    {
      "id": "actor-3", "type": "rectangle", "x": 480, "y": 40,
      "width": 100, "height": 40, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#c3fae8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 34, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-act-3", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-act-3", "type": "text", "x": 495, "y": 49,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 35, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "数据库", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "actor-3", "originalText": "数据库", "lineHeight": 1.25
    },
    {
      "id": "line-act-1", "type": "line", "x": 130, "y": 80,
      "width": 0, "height": 320, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "dashed",
      "roughness": 0, "opacity": 60, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 36, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 320]]
    },
    {
      "id": "line-act-2", "type": "line", "x": 330, "y": 80,
      "width": 0, "height": 320, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "dashed",
      "roughness": 0, "opacity": 60, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 37, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 320]]
    },
    {
      "id": "line-act-3", "type": "line", "x": 530, "y": 80,
      "width": 0, "height": 320, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "dashed",
      "roughness": 0, "opacity": 60, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 38, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 320]]
    },
    {
      "id": "msg-1", "type": "arrow", "x": 130, "y": 120,
      "width": 200, "height": 0, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 39, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [200, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "txt-msg-1", "type": "text", "x": 155, "y": 105,
      "width": 150, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 40, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "1. 发送请求", "fontSize": 16, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "middle",
      "containerId": null, "originalText": "1. 发送请求", "lineHeight": 1.25
    },
    {
      "id": "msg-2", "type": "arrow", "x": 330, "y": 180,
      "width": 200, "height": 0, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 41, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [200, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "txt-msg-2", "type": "text", "x": 355, "y": 165,
      "width": 150, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 42, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "2. 查询数据", "fontSize": 16, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "middle",
      "containerId": null, "originalText": "2. 查询数据", "lineHeight": 1.25
    },
    {
      "id": "msg-3", "type": "arrow", "x": 530, "y": 240,
      "width": -400, "height": 0, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 43, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [-400, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "txt-msg-3", "type": "text", "x": 200, "y": 225,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 44, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "3. 返回结果", "fontSize": 16, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "middle",
      "containerId": null, "originalText": "3. 返回结果", "lineHeight": 1.25
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 4. 思维导图 Mind Map

中心主题 + 一级/二级分支，放射状结构。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "center", "type": "ellipse", "x": 220, "y": 160,
      "width": 160, "height": 80, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 50, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-center", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-center", "type": "text", "x": 255, "y": 190,
      "width": 90, "height": 25, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 51, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "中心主题", "fontSize": 22, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "center", "originalText": "中心主题", "lineHeight": 1.25
    },
    {
      "id": "branch-1", "type": "rectangle", "x": 460, "y": 60,
      "width": 140, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 52, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-br-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-br-1", "type": "text", "x": 480, "y": 75,
      "width": 100, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 53, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "分支 1", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "branch-1", "originalText": "分支 1", "lineHeight": 1.25
    },
    {
      "id": "branch-2", "type": "rectangle", "x": 460, "y": 150,
      "width": 140, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 54, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-br-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-br-2", "type": "text", "x": 480, "y": 165,
      "width": 100, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 55, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "分支 2", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "branch-2", "originalText": "分支 2", "lineHeight": 1.25
    },
    {
      "id": "branch-3", "type": "rectangle", "x": 460, "y": 240,
      "width": 140, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#ffd8a8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 56, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-br-3", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-br-3", "type": "text", "x": 480, "y": 255,
      "width": 100, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 57, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "分支 3", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "branch-3", "originalText": "分支 3", "lineHeight": 1.25
    },
    {
      "id": "arr-mm-1", "type": "arrow", "x": 380, "y": 85,
      "width": 80, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 58, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [80, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-mm-2", "type": "arrow", "x": 380, "y": 175,
      "width": 80, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 59, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [80, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-mm-3", "type": "arrow", "x": 380, "y": 265,
      "width": 80, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 60, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [80, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "sub-1a", "type": "text", "x": 480, "y": 110,
      "width": 100, "20": 0, "height": 20, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 61, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "  └ 子项 1", "fontSize": 14, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "  └ 子项 1", "lineHeight": 1.25
    },
    {
      "id": "sub-2a", "type": "text", "x": 480, "y": 200,
      "width": 100, "height": 20, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 62, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "  └ 子项 2", "fontSize": 14, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "  └ 子项 2", "lineHeight": 1.25
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 5. 泳道图 Swimlane

水平泳道按角色分区，流程穿越泳道。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "lane-1", "type": "rectangle", "x": 40, "y": 40,
      "width": 600, "height": 120, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#dbe4ff",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
      "roughness": 1, "opacity": 20, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 70, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "lane-2", "type": "rectangle", "x": 40, "y": 160,
      "width": 600, "height": 120, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d3f9d8",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
      "roughness": 1, "opacity": 20, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 71, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "label-lane-1", "type": "text", "x": 50, "y": 50,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e40af", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 72, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "前端团队", "fontSize": 16, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "前端团队", "lineHeight": 1.25
    },
    {
      "id": "label-lane-2", "type": "text", "x": 50, "y": 170,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e40af", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 73, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "后端团队", "fontSize": 16, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "后端团队", "lineHeight": 1.25
    },
    {
      "id": "step-sw-1", "type": "rectangle", "x": 160, "y": 60,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 74, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-sw-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-sw-1", "type": "text", "x": 175, "y": 75,
      "width": 90, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 75, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "设计页面", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "step-sw-1", "originalText": "设计页面", "lineHeight": 1.25
    },
    {
      "id": "step-sw-2", "type": "rectangle", "x": 360, "y": 60,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 76, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-sw-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-sw-2", "type": "text", "x": 380, "y": 75,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 77, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "发版测试", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "step-sw-2", "originalText": "发版测试", "lineHeight": 1.25
    },
    {
      "id": "step-sw-3", "type": "rectangle", "x": 160, "y": 180,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 78, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-sw-3", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-sw-3", "type": "text", "x": 175, "y": 195,
      "width": 90, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 79, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "开发 API", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "step-sw-3", "originalText": "开发 API", "lineHeight": 1.25
    },
    {
      "id": "arr-sw-1", "type": "arrow", "x": 280, "y": 85,
      "width": 80, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 80, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [80, 0]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-sw-2", "type": "arrow", "x": 220, "y": 110,
      "width": 0, "height": 70, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 81, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 70]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 6. ER 图 ERD

两个实体 + 关系连线 + 基数标注。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "entity-1", "type": "rectangle", "x": 80, "y": 120,
      "width": 180, "height": 100, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 90, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-ent-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-ent-1", "type": "text", "x": 130, "y": 148,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 91, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "用户", "fontSize": 20, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "entity-1", "originalText": "用户", "lineHeight": 1.25
    },
    {
      "id": "attr-u-1", "type": "text", "x": 95, "y": 170,
      "width": 150, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 92, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "PK 用户ID | 姓名", "fontSize": 12, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "PK 用户ID | 姓名", "lineHeight": 1.25
    },
    {
      "id": "entity-2", "type": "rectangle", "x": 380, "y": 120,
      "width": 180, "height": 100, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#c3fae8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 93, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-ent-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-ent-2", "type": "text", "x": 430, "y": 148,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 94, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "订单", "fontSize": 20, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "entity-2", "originalText": "订单", "lineHeight": 1.25
    },
    {
      "id": "attr-o-1", "type": "text", "x": 395, "y": 170,
      "width": 150, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 95, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "PK 订单ID | 用户ID(FK)", "fontSize": 12, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "PK 订单ID | 用户ID(FK)", "lineHeight": 1.25
    },
    {
      "id": "rel-1", "type": "diamond", "x": 270, "y": 130,
      "width": 100, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#fff3bf",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 96, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-rel-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-rel-1", "type": "text", "x": 295, "y": 150,
      "width": 50, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 97, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "拥有", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "rel-1", "originalText": "拥有", "lineHeight": 1.25
    },
    {
      "id": "arr-er-1", "type": "arrow", "x": 260, "y": 160,
      "width": 110, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 98, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [110, 0]],
      "startBinding": { "elementId": "entity-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "rel-1", "focus": 0.5, "gap": 0 },
      "startArrowhead": null, "endArrowhead": null
    },
    {
      "id": "arr-er-2", "type": "arrow", "x": 370, "y": 160,
      "width": 110, "height": 0, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 99, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [110, 0]],
      "startBinding": { "elementId": "rel-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "entity-2", "focus": 0.5, "gap": 0 },
      "startArrowhead": null, "endArrowhead": null
    },
    {
      "id": "card-1", "type": "text", "x": 300, "y": 110,
      "width": 40, "height": 18, "angle": 0,
      "strokeColor": "#f59e0b", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 100, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "1", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "1", "lineHeight": 1.25
    },
    {
      "id": "card-2", "type": "text", "x": 370, "y": 200,
      "width": 40, "height": 18, "angle": 0,
      "strokeColor": "#f59e0b", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 101, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "N", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "N", "lineHeight": 1.25
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 7. 层级图 Hierarchy

组织结构/系统拆解，自上而下树形，逐级展开。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "hi-root", "type": "rectangle", "x": 250, "y": 40,
      "width": 140, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 110, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-hi-root", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-hi-root", "type": "text", "x": 275, "y": 56,
      "width": 90, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 111, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "根节点", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "hi-root", "originalText": "根节点", "lineHeight": 1.25
    },
    {
      "id": "hi-l1-1", "type": "rectangle", "x": 80, "y": 160,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 112, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-hi-l1-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-hi-l1-1", "type": "text", "x": 100, "y": 176,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 113, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "子节点 A", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "hi-l1-1", "originalText": "子节点 A", "lineHeight": 1.25
    },
    {
      "id": "hi-l1-2", "type": "rectangle", "x": 260, "y": 160,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 114, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-hi-l1-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-hi-l1-2", "type": "text", "x": 280, "y": 176,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 115, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "子节点 B", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "hi-l1-2", "originalText": "子节点 B", "lineHeight": 1.25
    },
    {
      "id": "hi-l1-3", "type": "rectangle", "x": 440, "y": 160,
      "width": 120, "height": 50, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#ffd8a8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 116, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-hi-l1-3", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-hi-l1-3", "type": "text", "x": 460, "y": 176,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 117, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "子节点 C", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "hi-l1-3", "originalText": "子节点 C", "lineHeight": 1.25
    },
    {
      "id": "hi-l2-1", "type": "text", "x": 95, "y": 230,
      "width": 90, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 118, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "  └ 叶节点 1", "fontSize": 13, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "  └ 叶节点 1", "lineHeight": 1.25
    },
    {
      "id": "hi-l2-2", "type": "text", "x": 95, "y": 250,
      "width": 90, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 119, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "  └ 叶节点 2", "fontSize": 13, "fontFamily": 1,
      "textAlign": "left", "verticalAlign": "top",
      "containerId": null, "originalText": "  └ 叶节点 2", "lineHeight": 1.25
    },
    {
      "id": "arr-hi-1", "type": "arrow", "x": 320, "y": 90,
      "width": -180, "height": 70, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 120, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [-180, 70]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-hi-2", "type": "arrow", "x": 320, "y": 90,
      "width": 0, "height": 70, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 121, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 70]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "arr-hi-3", "type": "arrow", "x": 320, "y": 90,
      "width": 180, "height": 70, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 122, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [180, 70]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 8. 关系图 Relationship

节点 + 连线 + 关系标注，无严格方向。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "rel-node-1", "type": "ellipse", "x": 60, "y": 120,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 130, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-rn-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-rn-1", "type": "text", "x": 85, "y": 142,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 131, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "服务 A", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "rel-node-1", "originalText": "服务 A", "lineHeight": 1.25
    },
    {
      "id": "rel-node-2", "type": "ellipse", "x": 280, "y": 40,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 132, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-rn-2", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-rn-2", "type": "text", "x": 305, "y": 62,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 133, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "服务 B", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "rel-node-2", "originalText": "服务 B", "lineHeight": 1.25
    },
    {
      "id": "rel-node-3", "type": "ellipse", "x": 280, "y": 200,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 134, "version": 1, "versionNonce": 0,
      "isDeleted": false,
      "boundElements": [{ "id": "txt-rn-3", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-rn-3", "type": "text", "x": 305, "y": 222,
      "width": 70, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 135, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "服务 C", "fontSize": 16, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "rel-node-3", "originalText": "服务 C", "lineHeight": 1.25
    },
    {
      "id": "conn-ab", "type": "arrow", "x": 180, "y": 130,
      "width": 100, "height": -60, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 136, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [100, -60]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "label-ab", "type": "text", "x": 195, "y": 85,
      "width": 80, "height": 18, "angle": 0,
      "strokeColor": "#f59e0b", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 137, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "REST 调用", "fontSize": 12, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "REST 调用", "lineHeight": 1.25
    },
    {
      "id": "conn-ac", "type": "arrow", "x": 180, "y": 160,
      "width": 100, "height": 60, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 138, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [100, 60]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "label-ac", "type": "text", "x": 195, "y": 205,
      "width": 80, "height": 18, "angle": 0,
      "strokeColor": "#f59e0b", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 139, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "消息队列", "fontSize": 12, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "消息队列", "lineHeight": 1.25
    },
    {
      "id": "conn-bc", "type": "arrow", "x": 340, "y": 100,
      "width": 0, "height": 100, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 2 }, "seed": 140, "version": 1,
      "versionNonce": 0, "isDeleted": false, "boundElements": null,
      "updated": 1, "link": null, "locked": false,
      "points": [[0, 0], [0, 100]],
      "startBinding": null, "endBinding": null,
      "startArrowhead": null, "endArrowhead": "arrow"
    },
    {
      "id": "label-bc", "type": "text", "x": 345, "y": 140,
      "width": 60, "height": 18, "angle": 0,
      "strokeColor": "#f59e0b", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 141, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "gRPC", "fontSize": 12, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "gRPC", "lineHeight": 1.25
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 9. 对比图 Comparison

左右两栏对照，标明比较维度。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "cmp-title", "type": "text", "x": 200, "y": 40,
      "width": 200, "height": 28, "angle": 0,
      "strokeColor": "#1e40af", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 150, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "方案对比：A vs B", "fontSize": 22, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "方案对比：A vs B", "lineHeight": 1.25
    },
    {
      "id": "header-a", "type": "rectangle", "x": 60, "y": 90,
      "width": 200, "height": 40, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 151, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-ha", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-ha", "type": "text", "x": 120, "y": 100,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 152, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "方案 A", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "header-a", "originalText": "方案 A", "lineHeight": 1.25
    },
    {
      "id": "header-b", "type": "rectangle", "x": 340, "y": 90,
      "width": 200, "height": 40, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": { "type": 3 }, "seed": 153, "version": 1,
      "versionNonce": 0, "isDeleted": false,
      "boundElements": [{ "id": "txt-hb", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-hb", "type": "text", "x": 400, "y": 100,
      "width": 80, "height": 22, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 154, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "方案 B", "fontSize": 18, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": "header-b", "originalText": "方案 B", "lineHeight": 1.25
    },
    {
      "id": "row-1-label", "type": "text", "x": 10, "y": 155,
      "width": 40, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 155, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "性能", "fontSize": 16, "fontFamily": 1,
      "textAlign": "right", "verticalAlign": "middle",
      "containerId": null, "originalText": "性能", "lineHeight": 1.25
    },
    {
      "id": "row-1-a", "type": "text", "x": 80, "y": 155,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 156, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "⭐⭐⭐⭐ 高吞吐", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "⭐⭐⭐⭐ 高吞吐", "lineHeight": 1.25
    },
    {
      "id": "row-1-b", "type": "text", "x": 360, "y": 155,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 157, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "⭐⭐⭐ 中等", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "⭐⭐⭐ 中等", "lineHeight": 1.25
    },
    {
      "id": "row-2-label", "type": "text", "x": 10, "y": 190,
      "width": 40, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 158, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "成本", "fontSize": 16, "fontFamily": 1,
      "textAlign": "right", "verticalAlign": "middle",
      "containerId": null, "originalText": "成本", "lineHeight": 1.25
    },
    {
      "id": "row-2-a", "type": "text", "x": 80, "y": 190,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 159, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "💰💰 中等", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "💰💰 中等", "lineHeight": 1.25
    },
    {
      "id": "row-2-b", "type": "text", "x": 360, "y": 190,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 160, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "💰💰💰 较高", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "💰💰💰 较高", "lineHeight": 1.25
    },
    {
      "id": "row-3-label", "type": "text", "x": 10, "y": 225,
      "width": 40, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 161, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "学习曲线", "fontSize": 16, "fontFamily": 1,
      "textAlign": "right", "verticalAlign": "middle",
      "containerId": null, "originalText": "学习曲线", "lineHeight": 1.25
    },
    {
      "id": "row-3-a", "type": "text", "x": 80, "y": 225,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 162, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "⭐ 简单", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "⭐ 简单", "lineHeight": 1.25
    },
    {
      "id": "row-3-b", "type": "text", "x": 360, "y": 225,
      "width": 160, "height": 22, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 163, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "⭐⭐⭐ 中等", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "middle",
      "containerId": null, "originalText": "⭐⭐⭐ 中等", "lineHeight": 1.25
    },
    {
      "id": "sep-line", "type": "line", "x": 300, "y": 90,
      "width": 0, "height": 170, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "dashed",
      "roughness": 0, "opacity": 50, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 164, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 170]]
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 10. 时间线图 Timeline

水平时间轴 + 关键节点 + 事件标注。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "tl-title", "type": "text", "x": 200, "y": 40,
      "width": 200, "height": 28, "angle": 0,
      "strokeColor": "#1e40af", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 170, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "项目里程碑", "fontSize": 22, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "项目里程碑", "lineHeight": 1.25
    },
    {
      "id": "tl-axis", "type": "line", "x": 60, "y": 140,
      "width": 480, "height": 0, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 3, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 171, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [480, 0]]
    },
    {
      "id": "tl-marker-1", "type": "line", "x": 100, "y": 130,
      "width": 0, "height": 20, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 172, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 20]]
    },
    {
      "id": "tl-marker-2", "type": "line", "x": 220, "y": 130,
      "width": 0, "height": 20, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 173, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 20]]
    },
    {
      "id": "tl-marker-3", "type": "line", "x": 340, "y": 130,
      "width": 0, "height": 20, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 174, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 20]]
    },
    {
      "id": "tl-marker-4", "type": "line", "x": 460, "y": 130,
      "width": 0, "height": 20, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 175, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "points": [[0, 0], [0, 20]]
    },
    {
      "id": "tl-dot-1", "type": "ellipse", "x": 93, "y": 123,
      "width": 14, "height": 14, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 176, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "tl-dot-2", "type": "ellipse", "x": 213, "y": 123,
      "width": 14, "height": 14, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 177, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "tl-dot-3", "type": "ellipse", "x": 333, "y": 123,
      "width": 14, "height": 14, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 178, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "tl-dot-4", "type": "ellipse", "x": 453, "y": 123,
      "width": 14, "height": 14, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#ffd8a8",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 179, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false
    },
    {
      "id": "tl-date-1", "type": "text", "x": 75, "y": 155,
      "width": 60, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 180, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "Q1 2026", "fontSize": 13, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "Q1 2026", "lineHeight": 1.25
    },
    {
      "id": "tl-event-1", "type": "text", "x": 65, "y": 80,
      "width": 80, "height": 36, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 181, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "需求\n分析", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "需求分析", "lineHeight": 1.25
    },
    {
      "id": "tl-date-2", "type": "text", "x": 195, "y": 155,
      "width": 60, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 182, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "Q2 2026", "fontSize": 13, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "Q2 2026", "lineHeight": 1.25
    },
    {
      "id": "tl-event-2", "type": "text", "x": 185, "y": 80,
      "width": 80, "height": 36, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 183, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "原型\n设计", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "原型设计", "lineHeight": 1.25
    },
    {
      "id": "tl-date-3", "type": "text", "x": 315, "y": 155,
      "width": 60, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 184, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "Q3 2026", "fontSize": 13, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "Q3 2026", "lineHeight": 1.25
    },
    {
      "id": "tl-event-3", "type": "text", "x": 305, "y": 80,
      "width": 80, "height": 36, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 185, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "开发\n迭代", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "开发迭代", "lineHeight": 1.25
    },
    {
      "id": "tl-date-4", "type": "text", "x": 435, "y": 155,
      "width": 60, "height": 18, "angle": 0,
      "strokeColor": "#868e96", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 186, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "Q4 2026", "fontSize": 13, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "Q4 2026", "lineHeight": 1.25
    },
    {
      "id": "tl-event-4", "type": "text", "x": 425, "y": 80,
      "width": 80, "height": 36, "angle": 0,
      "strokeColor": "#374151", "backgroundColor": "transparent",
      "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
      "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null,
      "roundness": null, "seed": 187, "version": 1, "versionNonce": 0,
      "isDeleted": false, "boundElements": null, "updated": 1,
      "link": null, "locked": false,
      "text": "上线\n发布", "fontSize": 14, "fontFamily": 1,
      "textAlign": "center", "verticalAlign": "top",
      "containerId": null, "originalText": "上线发布", "lineHeight": 1.25
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

---

## 布局经验值

- 节点间距：垂直 80–120px，水平 80–150px
- 矩形内文字：`x + 20`，宽度 = 矩形宽 − 40，垂直居中
- 菱形决策：width/height 建议 ≥ 160×80
- 架构图分层层间距 ≥ 100px，层标题用独立文本（不绑定容器）
- 时序图：角色竖线高 300–400px，消息箭头编号 `1. `、`2. ` 前缀
- 层级图：同级节点水平间距 80–120px，上下层垂直间距 80–100px
- 对比图：分隔线居中，左右两栏宽度一致，行高 30–35px
- 时间线图：时间轴用粗线（strokeWidth: 3），事件标注在轴上方，日期在轴下方
# Sketch template behavior

Under `theme=sketch`, relationship uses semantic curves and a center/topic emphasis; flowchart uses note-like cards and dashed feedback; swimlane uses stage frames and validation/return loops; architecture adds review, risk and dependency annotations while preserving native/library fallback.
