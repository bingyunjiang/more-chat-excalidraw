# Excalidraw v2 JSON Schema 速查

## 顶层结构

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {},
  "files": {}
}
```

- `appState` 可选：`viewBackgroundColor`（画布底色，默认 `#ffffff`）、`gridSize`、`currentItemStrokeColor` 等。
- `files` 可选：图片等二进制资源，key 为文件 id，值为 `{ "mimeType": "...", "dataURL": "data:image/png;base64,..." }`。

## 元素通用字段

所有元素（除 `frame` 部分字段外）都包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 全局唯一，字母数字组合，如 `rect-001`；删除后不得复用 |
| `type` | string | 元素类型，见下表 |
| `x`, `y` | number | 左上角坐标（frame 用 x/y 表示尺寸） |
| `width`, `height` | number | 宽高，必须 ≥ 0 |
| `angle` | number | 弧度，0 表示不旋转 |
| `strokeColor` | string | 描边颜色 |
| `backgroundColor` | string | 填充颜色 |
| `fillStyle` | string | `solid` / `hachure` / `cross-hatch` |
| `strokeWidth` | number | 1 或 2 |
| `strokeStyle` | string | `solid` / `dashed` / `dotted` |
| `roughness` | number | 手绘感，0–2 |
| `opacity` | number | 0–100 |
| `groupIds` | string[] | 所属分组 id 列表 |
| `frameId` | string \| null | 所属 frame 的 id |
| `roundness` | object \| null | `{ "type": 3 }`（矩形圆角）等 |
| `seed` | number | 随机种子，影响手绘抖动；同一元素保持稳定 |
| `version` | number | 版本号，每次更新 +1 |
| `versionNonce` | number | 任意递增数 |
| `isDeleted` | boolean | 通常 `false` |
| `boundElements` | array \| null | 绑定到本元素的子元素（如文字标签） |
| `updated` | number | 毫秒时间戳 |
| `link` | string \| null | 超链接 |
| `locked` | boolean | 是否锁定 |

## 元素类型

| type | 说明 | 特有字段 |
|---|---|---|
| `rectangle` | 矩形 | `roundness` |
| `ellipse` | 椭圆/圆形 | - |
| `diamond` | 菱形（决策） | - |
| `line` | 直线/折线 | `points`（相对坐标数组） |
| `arrow` | 箭头 | `points`、`startBinding`、`endBinding`、`startArrowhead`、`endArrowhead` |
| `text` | 文本 | `text`、`fontSize`、`fontFamily`、`textAlign`、`verticalAlign`、`containerId`、`originalText`、`lineHeight` |
| `freedraw` | 手绘笔迹 | `points`、`pressures` |
| `image` | 图片 | `fileId`（对应 `files` 的 key） |
| `frame` | 框架/标题区 | `name`；子元素通过 `frameId` 关联 |
| `embeddable` | 嵌入内容 | `link` |

## 文字标签绑定（重要）

文字属于图形时：

- 图形元素声明 `"boundElements": [{ "id": "<text-id>", "type": "text" }]`
- 文本元素声明 `"containerId": "<shape-id>"`，并保持 `x/y` 与图形对齐、宽度接近图形内宽
- 独立说明文字不绑定任何容器：`containerId` 为 `null`

## 箭头绑定（重要）

```json
"startBinding": { "elementId": "<shape-a>", "focus": 0, "gap": 8 },
"endBinding": { "elementId": "<shape-b>", "focus": 0, "gap": 8 },
"points": [[0, 0], [150, 0]]
```

`points` 为相对坐标；`focus` 0–1 表示箭头在节点边框上的触点比例（0=左上角方向，0.5=水平中点）。箭头两端悬空时可省略对应 binding。

## 分组

同组元素共享同一个 `groupIds` 字符串 id（无需单独声明分组对象）。多个元素用同一 id 即构成一组；嵌套分组按数组顺序表示层级。

## 校验要点（validate_excalidraw.py 已检查）

- JSON 可解析；`type` 为 `excalidraw`，`version` 为 2
- `elements` 存在且为数组
- 每个元素具备 `id/type/x/y`；`width/height` 为数字
- `id` 全局唯一
- `boundElements[].id`、`containerId`、`frameId`、`startBinding.elementId`、`endBinding.elementId` 引用的元素存在
- 文本元素必须有非空 `text` 字段

## 实用提示

- 文字宽度估算：中文字符 ≈ 1.0 × fontSize，ASCII ≈ 0.6 × fontSize；文本元素宽度按此估算，必要时换行。
- 生成后先渲染预览再交付：`node scripts/render_preview.js <file>`。
