# IR 中间格式（Intermediate Representation）

> 独立于 Excalidraw 的图表中间表示，是 Pillar A（文案引擎）与 Pillar C（JSON 生成）之间的标准接口。
> 用户：LLM 生成 IR → ir_to_excalidraw.py 转为 .excalidraw → 校验 → 预览。

## 1. 设计原则

- **独立于 Excalidraw**：IR 不包含任何 Excalidraw 元素字段（x/y/seed/versionNonce 等），只描述图表语义
- **可版本化**：IR 有自身 version，可做 diff/合并/回退
- **LLM 友好**：字段名直观，避免嵌套过深，JSON 体积小
- **模板驱动**：IR 声明 template 与 theme，由转换器负责布局与配色

## 2. 顶层结构

```json
{
  "version": 1,
  "title": "用户注册流程",
  "template": "flowchart",
  "theme": "default",
  "direction": "vertical",
  "nodes": [],
  "edges": [],
  "groups": [],
  "visual_contract": null,
  "metadata": {}
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | number | 是 | IR 格式版本，当前为 1 |
| `title` | string | 否 | 图表标题（显示在画布顶部） |
| `template` | string | 是 | 模板 key：flowchart/architecture/sequence/mindmap/swimlane/erd/hierarchy/relationship/comparison/timeline |
| `theme` | string | 否 | default/sketch/blueprint/minimal，默认 default |
| `direction` | string | 否 | 布局方向：vertical/horizontal/tree/layered/free/table/swimlane |
| `nodes` | array | 是 | 节点列表（见下） |
| `edges` | array | 否 | 边列表（见下） |
| `groups` | array | 否 | 分组/frame 列表（见下） |
| `metadata` | object | 否 | 来源、创建时间、LLM 提示词等附加信息 |
| `visual_contract` | object | 否 | 可选视觉蒸馏契约，见 `visual-distillation-contract.md` |

## 3. 节点 node

```json
{
  "id": "n1",
  "label": "处理请求",
  "type": "process",
  "style": null,
  "children": [],
  "position": null,
  "note": ""
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 节点唯一 ID（字母数字，如 n1/n2） |
| `label` | string | 是 | 节点显示文字 |
| `type` | string | 否 | 节点语义类型（见下） |
| `style` | string | 否 | 覆盖模板样式；可使用 tech 名称或 `#RRGGBB` 填充色 |
| `children` | string[] | 否 | 子节点 ID（树形结构用） |
| `position` | object | 否 | 手动位置 `{x, y}`，转换器优先使用 |
| `note` | string | 否 | 备注（渲染为小号注释文字） |
| `font` / `fontFamily` | string/number | 否 | `hand`/`sans`/`mono` 或 Excalidraw 字体编号 |
| `fontSize` | number | 否 | 节点文字字号；多行文字会自动扩展节点高度 |
| `textColor` | string | 否 | 节点文字颜色 |
| `strokeColor` | string | 否 | 节点描边颜色 |
| `strokeWidth` | number | 否 | 节点描边粗细 |
| `strokeStyle` | string | 否 | `solid`/`dashed`/`dotted` |
| `roughness` | number | 否 | 手绘粗糙度，`sketch` 常用 2 |
| `opacity` | number | 否 | 0–100 不透明度 |

### 节点类型

| 类型 | 默认形状 | 默认填充 | 说明 |
|------|---------|---------|------|
| `start` | 椭圆 | 浅蓝 `#a5d8ff` | 流程起点 |
| `end` | 椭圆 | 浅绿 `#b2f2bb` | 流程终点 |
| `process` | 矩形 | 白 `#ffffff` | 处理步骤 |
| `decision` | 菱形 | 浅黄 `#fff3bf` | 判断/分支 |
| `actor` | 矩形 | 浅蓝 `#a5d8ff` | 参与者（时序图） |
| `entity` | 矩形 | 浅蓝 `#a5d8ff` | 实体（ER 图） |
| `relation` | 菱形 | 浅黄 `#fff3bf` | 关系（ER 图） |
| `component` | 矩形 | 白 `#ffffff` | 组件（架构图） |
| `service` | 矩形 | 浅紫 `#d0bfff` | 服务（架构图） |
| `database` | 椭圆 | 浅青 `#c3fae8` | 数据库/存储 |
| `topic` | 椭圆 | 浅蓝 `#a5d8ff` | 中心主题（思维导图/概念板） |
| `branch` | 矩形 | 浅紫 `#d0bfff` | 一级分支（思维导图） |
| `leaf` | 矩形 | 浅粉 `#fcc2d7` | 叶节点 |
| `input` | 矩形 | 浅蓝 `#a5d8ff` | 输入/数据源 |
| `output` | 矩形 | 浅绿 `#b2f2bb` | 输出/结果 |
| `note` | 圆角矩形 | 浅黄 `#fff3bf` | 手绘便签/双语卡片 |
| `callout` | 圆角矩形 | 浅橙 `#ffd8a8` | 强调框/技术批注 |
| `marker` | 椭圆 | 白 `#ffffff` | 时间线标记点 |
| `milestone` | 椭圆 | 浅蓝 `#a5d8ff` | 里程碑 |
| `plain` | 矩形 | 白 `#ffffff` | 通用节点 |

## 4. 边 edge

```json
{
  "id": "e1",
  "from": "n1",
  "to": "n2",
  "label": "成功",
  "style": "solid",
  "bidirectional": false,
  "note": ""
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 边唯一 ID |
| `from` | string | 是 | 起点节点 ID |
| `to` | string | 是 | 终点节点 ID |
| `label` | string | 否 | 边标签（渲染为箭头旁注释） |
| `style` | string | 否 | solid/dashed/dotted，默认 solid |
| `bidirectional` | boolean | 否 | 双向箭头（请求-响应模式） |
| `note` | string | 否 | 备注 |
| `curve` | boolean | 否 | 使用手绘曲线箭头 |
| `curveOffset` | number | 否 | 曲线控制点偏移，默认 36 |
| `color` | string | 否 | 箭头语义颜色 |
| `labelColor` | string | 否 | 箭头标签颜色，默认跟随箭头 |
| `strokeWidth` | number | 否 | 箭头粗细 |
| `startArrowhead` | string/null | 否 | 起点样式，如 arrow/dot/bar/triangle |
| `endArrowhead` | string/null | 否 | 终点样式，默认 arrow |

## 5. 分组 group

```json
{
  "id": "g1",
  "name": "用户层",
  "type": "frame",
  "nodes": ["n1", "n2"],
  "backgroundColor": "#dbe4ff",
  "level": 1
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 分组 ID |
| `name` | string | 是 | 分组标题（frame 名称） |
| `type` | string | 否 | frame/group，默认 frame |
| `nodes` | string[] | 是 | 属于该组的节点 ID |
| `backgroundColor` | string | 否 | 分层背景色（覆盖模板默认） |
| `level` | number | 否 | 分层序号（用于垂直布局计算） |

## 6. 模板专用字段

部分模板需要额外结构化输入，统一放在 `metadata` 中：

```json
{
  "metadata": {
    "scene": "tech-arch",
    "complexity": "medium",
    "actors": ["用户", "服务端", "数据库"],
    "messages": [
      { "from": 0, "to": 1, "label": "请求", "order": 1 },
      { "from": 1, "to": 2, "label": "查询", "order": 2 }
    ],
    "comparison": {
      "dimensions": ["性能", "成本"],
      "columns": ["方案A", "方案B"],
      "rows": [["高", "中"], ["低", "高"]]
    },
    "timeline": {
      "events": [
        { "date": "Q1 2026", "label": "需求分析", "color": "blue" },
        { "date": "Q2 2026", "label": "原型设计", "color": "purple" }
      ]
    }
  }
}
```

## 7. 完整示例：流程图 IR

```json
{
  "version": 1,
  "title": "用户注册流程",
  "template": "flowchart",
  "theme": "default",
  "direction": "vertical",
  "nodes": [
    { "id": "n1", "label": "开始", "type": "start" },
    { "id": "n2", "label": "填写注册信息", "type": "process" },
    { "id": "n3", "label": "信息合法？", "type": "decision" },
    { "id": "n4", "label": "创建账号", "type": "process" },
    { "id": "n5", "label": "发送验证邮件", "type": "process" },
    { "id": "n6", "label": "完成", "type": "end" },
    { "id": "n7", "label": "提示错误", "type": "process", "style": "#ffc9c9" }
  ],
  "edges": [
    { "id": "e1", "from": "n1", "to": "n2" },
    { "id": "e2", "from": "n2", "to": "n3" },
    { "id": "e3", "from": "n3", "to": "n4", "label": "是" },
    { "id": "e4", "from": "n3", "to": "n7", "label": "否" },
    { "id": "e5", "from": "n7", "to": "n2", "label": "重试" },
    { "id": "e6", "from": "n4", "to": "n5" },
    { "id": "e7", "from": "n5", "to": "n6" }
  ],
  "metadata": {
    "scene": "business-process",
    "complexity": "simple"
  }
}
```

## 8. IR → Excalidraw 转换规则

转换由 `scripts/ir_to_excalidraw.py` 完成，规则：

1. **布局**：根据 template 与 direction 计算节点位置（内置布局器），`position` 字段可覆盖
2. **节点**：按 type 映射到元素模板（element-templates.md），style 可覆盖（tech 名称走 tech-node-templates.md）
3. **边**：生成 arrow 元素，from/to 绑定到对应节点，label 渲染为独立文字
4. **分组**：frame 元素包裹对应节点，按 level 垂直排列
5. **配色**：应用 theme 色板（color-palette.md），同图单色板
6. **校验**：输出后运行 validate_excalidraw.py，error 必须清零
7. **视觉追溯（可选）**：存在 `visual_contract` 时，把事实 ID、来源、语义角色和视觉家族写入相关元素 `customData`；缺失时不改变旧 IR 输出。

## 9. 扩展通道

- **Mermaid 导入**：Mermaid 源码 → 解析 → IR（metadata 保留原始源码）
- **Markdown 导入**：文档标题/列表 → IR 层级结构
- **已有画布**：.excalidraw 元素 → 反解 IR（增量编辑基础）
