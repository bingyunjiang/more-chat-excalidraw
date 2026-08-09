# 模板选择指南

本指南把 10 个内部模板整理成 4 类用户选择。交互时不要一次展示完整技术清单；先根据内容推荐 1 项，再提供最多 2 个差异明显的备选项。

## 先区分三个概念

- `template`：信息怎样组织，例如流程、架构、关系或时间线。
- `theme`：整体渲染主题，包含 `default`、`sketch`、`blueprint`、`minimal`。
- `sketchStyle`：选择 `sketch` 后的手绘气质，例如工程笔记、根因诊断或评审批注。

## 四类模板

| 类别 | 模板 | 用户看到的名称 | 最适合 | 不适合 |
|---|---|---|---|---|
| 流程与协作 | `flowchart` | 步骤流程 | 有明确先后、判断和返工的操作流程 | 复杂因果网络、多角色职责交接 |
| 流程与协作 | `swimlane` | 角色泳道 | 跨部门、跨角色、分阶段职责交接 | 单一路径且不关心责任主体 |
| 系统与结构 | `architecture` | 系统架构 | 组件、分层、依赖、部署和数据流 | 单次调用的严格时间顺序 |
| 系统与结构 | `erd` | 数据实体 | 数据库实体、字段关系和基数 | 服务调用或业务步骤 |
| 系统与结构 | `hierarchy` | 层级拆解 | 组织、分类、系统分解和树形结构 | 多对多影响网络 |
| 交互与时间 | `sequence` | 消息时序 | 请求、响应、协议和消息先后 | 静态组件关系 |
| 交互与时间 | `timeline` | 事件时间线 | 里程碑、历史演进、路线图和进度 | 没有清晰时间轴的内容 |
| 分析与思考 | `relationship` | 关系分析板 | 因果、机理、根因、影响链和依赖 | 严格步骤或职责分工 |
| 分析与思考 | `mindmap` | 主题脑图 | 头脑风暴、知识梳理和主题发散 | 严格方向、职责或时间 |
| 分析与思考 | `comparison` | 方案对比 | 方案、指标、观点和优缺点对照 | 连续步骤或依赖网络 |

## 推荐的手绘组合

| 内容信号 | 推荐组合 |
|---|---|
| 工程步骤、计算流程 | `flowchart + engineering-notebook` |
| 多角色、多阶段协作 | `swimlane + engineering-notebook` |
| 根因、不收敛、故障诊断 | `relationship + root-cause` |
| 机理、因果、影响链 | `relationship + mechanism-map` |
| 架构风险与整改评审 | `architecture + review-markup` |
| 证据梳理、知识结构 | `mindmap/hierarchy + research-board` |
| 方案取舍 | `comparison + research-board` |

## Agent 交互协议

1. 用户已明确模板和风格：直接执行，用一句话复述选择，不重复提问。
2. 用户明确模板但未明确风格：推荐一个 `sketchStyle`，只确认视觉气质。
3. 用户只提供内容：运行 `template_selector.py --choices "<意图>"`，展示推荐项和最多两个备选项。
4. 用户说“你直接选”“不用问”：采用第一推荐项并说明理由。
5. 用户可回复序号、用户名称或内部模板名；Agent 将选择写入 IR 的 `template/theme/sketchStyle`。

推荐话术：

> 我推荐“关系分析板 + 根因诊断”，因为内容重点是不收敛原因和返工闭环。你可以选：1）关系分析板，2）步骤流程，3）角色泳道；也可以回复“你直接选”。

## CLI

```bash
# 查看按四类整理的目录
python3 scripts/template_selector.py --guide

# 输出机器可读目录
python3 scripts/template_selector.py --guide --json

# 生成可直接展示给用户的候选菜单
python3 scripts/template_selector.py --choices "分析有限元不收敛原因"

# 完整机器可读推荐结果
python3 scripts/template_selector.py --recommend "做一张架构风险评审图"

# 将确认结果解析为完整生成参数
python3 scripts/template_selector.py --params relationship --theme sketch --sketch-style root-cause
```

兼容性：原有 `--list`、`--info`、`--params` 和推荐结果中的 `primary/alternatives/recommendation/parameters` 字段继续保留。
