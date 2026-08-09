# Handdrawn visual rules

## 自动检查

- CJK 文本使用 Ma Shan Zheng（fontFamily 11），纯英文使用 Virgil（1）。
- 双语内容拆成 CJK/English 两行；边标签字号至少 32px。
- 标题位于顶部安全区（y >= 10）；节点文字留有内边距。
- 边标签、批注和装饰性线条不得遮住节点正文；如果节点编号和标题已经表达顺序，优先删减边标签。
- 箭头必须绑定起止节点，端点落在节点边界附近。
- 检查明显容器重叠、过小间距、悬空箭头，以及边标签是否覆盖可读文本。
- sketch 输出必须有 `appState.sketchStyle` 与 `sketchTemplate`，不得把 prompt 或任务说明写入图中文字。

## 人工目检清单

渲染 PNG/SVG 后依次检查字体退化、文字溢出、双语层级、标题安全区、箭头是否穿过节点、边标签是否压住正文、曲线是否表达语义、泳道/架构批注是否有留白，以及是否存在意外重叠。

## 闭环

`render → look → targeted fix → render`。只针对发现的问题做局部修正，再以 strict visual 校验和第二次字节比较确认确定性。

边界：当前 localhost:5001 本地 build 可能自动 fit 到顶部并被浮动工具栏覆盖；scene 的 `appState.scrollY` 与不可见 spacer 均未被该 build 尊重。正式视觉验收以 PNG/SVG 为准，编辑器内可手动平移画布。
