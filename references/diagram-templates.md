# 图表模板与布局规范

先选类型，再按对应布局生成。默认画布方向：节点按从上到下、从左到右排布，间距 60–80px；字体 20–28px。

## 模板选择

| 用户意图 | 模板 | 核心结构 |
|---|---|---|
| 流程/步骤/顺序 | 流程图 | 纵向或横向：矩形步骤 + 菱形决策 + 箭头 |
| 系统组件/调用关系 | 架构图 | 分层：用户层 → 应用层 → 服务层 → 数据层，层间大箭头 |
| 先后消息/时间顺序 | 时序图 | 三条竖线（角色）+ 横向箭头消息，编号 1/2/3 |
| 头脑风暴/知识点 | 思维导图 | 中心主题 + 一级/二级分支 |
| 角色职责/多部门流程 | 泳道图 | 水平泳道按角色分区，流程穿越泳道 |
| 实体与关系 | ER 图 | 实体矩形 + 关系菱形/连线 + 基数标注 |

## 色板

同一图内只用一个色板：

- 中性：描边 `#1e1e1e`，填充 `#ffffff`
- 强调（步骤/节点）：填充 `#d0ebff`（蓝）、`#b2f2bb`（绿）、`#ffd8a8`（橙）三选一
- 决策：`#ffec99`（黄）
- 连线：`#868e96`，粗线 `strokeWidth: 2`

## 流程图模板（最小示例）

三个元素：开始（ellipse）→ 处理（rectangle）→ 结束（ellipse），两个箭头绑定。

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "start-1", "type": "ellipse", "x": 100, "y": 80,
      "width": 120, "height": 60, "angle": 0,
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0ebff",
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
      "boundElements": [{ "id": "txt-1", "type": "text" }],
      "updated": 1, "link": null, "locked": false
    },
    {
      "id": "txt-1", "type": "text", "x": 130, "y": 230,
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
    }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 }
}
```

## 布局经验值

- 节点间距：垂直 80–120px，水平 80–150px
- 矩形内文字：`x + 20`，宽度 = 矩形宽 − 40，垂直居中
- 菱形决策：width/height 建议 ≥ 160×80
- 架构图分层层间距 ≥ 100px，层标题用独立文本（不绑定容器）
- 时序图：角色竖线高 300–400px，消息箭头编号 `1. `、`2. ` 前缀
