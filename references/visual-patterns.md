# 视觉模式模板

> 把常见关系模式抽象为可复用模板，每种模式提供 DSL 描述和对应的 Excalidraw JSON 骨架。
> 参考：coleam00/excalidraw-diagram-skill（4339★）

## 0. 与 visual_contract 的配合

当 IR 声明 `visual_contract` 时，先选一个 `visual_families.primary` 作为
主模式，再选择不超过两个 supporting families。例如流水线可用
`pipeline` 为 primary、`group` 为 supporting。把决定性事实的 `targets`
指向节点或边 ID；转换器会将事实 ID、来源、语义角色和家族写入相关元素，
严格视觉校验据此发现未解释的装饰形状或越界家族。没有契约的旧模式仍可
直接使用本页骨架，不要求额外字段。

## 1. 扇出模式 Fan-out

一个源节点 → 多个目标节点，用于发布/订阅/广播/分派。

**适用场景**：事件分发、任务调度、广播通知、数据复制

```
          ┌──→ 目标 A
源 ──→ 分发 ──→ 目标 B
          └──→ 目标 C
```

**DSL**：
```
fanout(source: "事件源", splitter: "分发器", targets: ["服务A", "服务B", "服务C"])
```

**JSON 骨架**：
```json
{
  "elements": [
    // 源节点（矩形，x=60, y=100）
    {
      "id": "src-1", "type": "rectangle", "x": 60, "y": 100,
      "width": 140, "height": 60, "roundness": { "type": 3 },
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "boundElements": [{ "id": "txt-src-1", "type": "text" }]
    },
    { "id": "txt-src-1", "type": "text", "x": 80, "y": 118,
      "width": 100, "height": 25, "fontSize": 18, "text": "事件源",
      "textAlign": "center", "verticalAlign": "middle", "containerId": "src-1" },
    // 分发器（菱形，x=280, y=90）
    {
      "id": "split-1", "type": "diamond", "x": 280, "y": 90,
      "width": 120, "height": 80,
      "strokeColor": "#1e1e1e", "backgroundColor": "#fff3bf",
      "boundElements": [{ "id": "txt-split-1", "type": "text" }]
    },
    { "id": "txt-split-1", "type": "text", "x": 310, "y": 118,
      "width": 60, "height": 25, "fontSize": 16, "text": "分发",
      "textAlign": "center", "verticalAlign": "middle", "containerId": "split-1" },
    // 三个目标节点（矩形，y 分别 = 60, 160, 260）
    { "id": "tgt-1", "type": "rectangle", "x": 480, "y": 40,
      "width": 140, "height": 60, "roundness": { "type": 3 },
      "strokeColor": "#1e1e1e", "backgroundColor": "#b2f2bb",
      "boundElements": [{ "id": "txt-tgt-1", "type": "text" }] },
    { "id": "txt-tgt-1", "type": "text", "x": 500, "y": 58, "width": 100, "height": 25,
      "fontSize": 18, "text": "服务A", "containerId": "tgt-1",
      "textAlign": "center", "verticalAlign": "middle" },
    // ... 目标 B、C 类似，y 偏移 60
    // 箭头：源→分发器
    { "id": "arr-src-split", "type": "arrow", "x": 200, "y": 130,
      "width": 80, "height": 0, "points": [[0, 0], [80, 0]],
      "startBinding": { "elementId": "src-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "split-1", "focus": 0.5, "gap": 0 },
      "endArrowhead": "arrow" },
    // 箭头：分发器→三个目标
    { "id": "arr-split-tgt1", "type": "arrow", "x": 400, "y": 110,
      "width": 80, "height": -60, "points": [[0, 0], [80, -60]],
      "startBinding": { "elementId": "split-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "tgt-1", "focus": 0.5, "gap": 0 },
      "endArrowhead": "arrow" }
    // ... arr-split-tgt2（水平），arr-split-tgt3（向下）
  ]
}
```

## 2. 汇聚模式 Converge

多个源节点 → 一个目标节点，用于聚合/汇总/收集。

**适用场景**：日志收集、数据聚合、事件汇聚、报表汇总

```
源 A ──┐
源 B ──┼──→ 汇聚器 → 目标
源 C ──┘
```

**DSL**：
```
converge(sources: ["传感器A", "传感器B", "传感器C"], merger: "汇聚器", target: "数据湖")
```

## 3. 时间线模式 Timeline

水平轴 + 节点 + 标注，用于演进/流程/历史。

**适用场景**：项目里程碑、产品演进、版本历史、事件线

```
○──────○──────○──────○
Q1      Q2      Q3      Q4
需求    设计    开发    上线
```

**DSL**：
```
timeline(title: "项目里程碑", events: [
  { date: "Q1 2026", label: "需求分析", color: "blue" },
  { date: "Q2 2026", label: "原型设计", color: "purple" },
  { date: "Q3 2026", label: "开发迭代", color: "green" },
  { date: "Q4 2026", label: "上线发布", color: "orange" }
])
```

## 4. 分组模式 Group

用 frame/group 包裹相关节点，标注区域名称。

**适用场景**：分层架构、模块划分、安全区域、环境隔离

```
┌─────────────── 用户层 ───────────────┐
│  Web前端          API网关             │
└──────────────────────────────────────┘
┌─────────────── 应用层 ───────────────┐
│  订单服务       支付服务              │
└──────────────────────────────────────┘
```

**DSL**：
```
group(layers: [
  { name: "用户层", bg: "#dbe4ff", nodes: ["Web前端", "API网关"] },
  { name: "应用层", bg: "#e5dbff", nodes: ["订单服务", "支付服务"] },
  { name: "数据层", bg: "#d3f9d8", nodes: ["PostgreSQL", "Redis"] }
])
```

## 5. 请求-响应模式 Request-Response

双向箭头 + 标注，用于客户端-服务端、API 调用、查询。

**适用场景**：HTTP API 调用、RPC 通信、数据库查询、用户交互

```
客户端 ──请求──→ 服务端
客户端 ←─响应─── 服务端
```

**DSL**：
```
request_response(
  client: "浏览器",
  server: "API 服务",
  request: "GET /api/users",
  response: "200 OK + JSON 数据"
)
```

**JSON 骨架**：
```json
{
  "elements": [
    // 客户端（矩形，x=60, y=100）
    {
      "id": "client-1", "type": "rectangle", "x": 60, "y": 100,
      "width": 140, "height": 60, "roundness": { "type": 3 },
      "strokeColor": "#1e1e1e", "backgroundColor": "#a5d8ff",
      "boundElements": [{ "id": "txt-client-1", "type": "text" }]
    },
    { "id": "txt-client-1", "type": "text", "x": 80, "y": 118,
      "width": 100, "height": 25, "fontSize": 18, "text": "浏览器",
      "containerId": "client-1", "textAlign": "center", "verticalAlign": "middle" },
    // 服务端（矩形，x=400, y=100）
    {
      "id": "server-1", "type": "rectangle", "x": 400, "y": 100,
      "width": 140, "height": 60, "roundness": { "type": 3 },
      "strokeColor": "#1e1e1e", "backgroundColor": "#d0bfff",
      "boundElements": [{ "id": "txt-server-1", "type": "text" }]
    },
    { "id": "txt-server-1", "type": "text", "x": 420, "y": 118,
      "width": 100, "height": 25, "fontSize": 18, "text": "API 服务",
      "containerId": "server-1", "textAlign": "center", "verticalAlign": "middle" },
    // 请求箭头（上方，从左到右）
    { "id": "arr-req", "type": "arrow", "x": 200, "y": 110,
      "width": 200, "height": 0, "points": [[0, 0], [200, 0]],
      "strokeColor": "#1e1e1e",
      "startBinding": { "elementId": "client-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "server-1", "focus": 0.5, "gap": 0 },
      "endArrowhead": "arrow" },
    // 请求标注（箭头上面）
    { "id": "txt-req", "type": "text", "x": 240, "y": 85,
      "width": 120, "height": 22, "fontSize": 14, "text": "GET /api/users",
      "strokeColor": "#868e96", "textAlign": "center" },
    // 响应箭头（下方，从右到左）
    { "id": "arr-resp", "type": "arrow", "x": 400, "y": 150,
      "width": -200, "height": 0, "points": [[0, 0], [-200, 0]],
      "strokeColor": "#868e96",
      "startBinding": { "elementId": "server-1", "focus": 0.5, "gap": 0 },
      "endBinding": { "elementId": "client-1", "focus": 0.5, "gap": 0 },
      "endArrowhead": "arrow" },
    // 响应标注（箭头下面）
    { "id": "txt-resp", "type": "text", "x": 240, "y": 160,
      "width": 120, "height": 22, "fontSize": 14, "text": "200 OK + JSON",
      "strokeColor": "#868e96", "textAlign": "center" }
  ]
}
```

## 6. 流水线模式 Pipeline

线性串联，节点间可传递数据，类似 conveyor belt。

**适用场景**：数据处理管道、CI/CD 流水线、装配线、ETL

```
输入 → 处理 A → 处理 B → 处理 C → 输出
```

**DSL**：
```
pipeline(stages: [
  { name: "数据采集", color: "blue" },
  { name: "清洗", color: "purple" },
  { name: "转换", color: "purple" },
  { name: "加载", color: "green" }
])
```

## 7. 星型模式 Star

中心节点 + 辐射到多个外围节点，用于中心化拓扑。

**适用场景**：Hub-Spoke 架构、中心化路由、微服务网关

```
         ┌── 服务 A ──┐
         │             │
 服务 C ──┼── 网关 ──┼── 服务 B
         │             │
         └── 服务 D ──┘
```

## 8. 矩阵模式 Matrix

行和列交叉，形成二维网格，用于对比/分类。

**适用场景**：方案对比、能力矩阵、优先级矩阵

```
         │ 方案 A │ 方案 B
─────────┼────────┼────────
性能     │ 高     │ 中
成本     │ 低     │ 高
复杂度   │ 简单   │ 复杂
```

## 9. 循环模式 Cycle

节点形成闭环，表示迭代/循环/反馈。

**适用场景**：开发循环、持续集成、反馈环、迭代流程

```
  ┌→ 开发 → 测试 → 部署 ─┐
  │                       │
  └─────── 反馈 ←─────────┘
```

## 10. 模式组合规则

- 扇出 + 汇聚：先分发再聚合（如 MapReduce）
- 分组 + 流水线：层内流水线，层间分层
- 请求-响应 + 时间线：异步消息时序
- 星型 + 分组：中心化分层架构

## 模式匹配参考

| 用户描述 | 推荐模式 | 说明 |
|----------|---------|------|
| "发布/订阅"、"广播"、"分派" | 扇出 Fan-out | 一对多 |
| "收集"、"聚合"、"汇总" | 汇聚 Converge | 多对一 |
| "项目进度"、"历史"、"演进" | 时间线 Timeline | 时间轴 |
| "分层"、"环境"、"区域" | 分组 Group | 框架包裹 |
| "API 调用"、"查询"、"通信" | 请求-响应 | 双向箭头 |
| "流水线"、"链路"、"通道" | 流水线 Pipeline | 线性串联 |
| "中心化"、"Hub"、"路由" | 星型 Star | 中心辐射 |
| "对比"、"矩阵"、"评估" | 矩阵 Matrix | 网格布局 |
| "迭代"、"循环"、"反馈" | 循环 Cycle | 闭环 |
