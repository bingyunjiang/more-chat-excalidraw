#!/usr/bin/env python3
"""
IR → Excalidraw JSON 转换器（Pillar C 核心引擎）

把 Pillar A 输出的 IR 中间格式（references/ir-format.md）转为完整的 .excalidraw v2 JSON：
模板布局 → 节点元素生成 → 箭头绑定 → 应用色板 → 输出文件。

用法：
  python3 scripts/ir_to_excalidraw.py <ir.json> [--output out.excalidraw] [--validate]
  python3 scripts/ir_to_excalidraw.py --example flowchart   # 生成示例 IR 并转换
  python3 scripts/ir_to_excalidraw.py --template-list       # 列出支持的模板
"""

import json
import sys
import os
import time
import hashlib
import argparse
import shutil
import subprocess

# ─── 语义色板（对应 references/color-palette.md）───────────────────────────
SEMANTIC_FILL = {
    "input": "#a5d8ff", "output": "#b2f2bb", "warning": "#ffd8a8",
    "processing": "#d0bfff", "error": "#ffc9c9", "note": "#fff3bf",
    "storage": "#c3fae8", "analysis": "#fcc2d7",
}

NODE_TYPE_STYLE = {
    "start":    {"shape": "ellipse",   "fill": SEMANTIC_FILL["input"],      "w": 120, "h": 60},
    "end":      {"shape": "ellipse",   "fill": SEMANTIC_FILL["output"],     "w": 120, "h": 60},
    "process":  {"shape": "rectangle", "fill": "#ffffff",                   "w": 200, "h": 80},
    "decision": {"shape": "diamond",   "fill": SEMANTIC_FILL["note"],       "w": 160, "h": 80},
    "actor":    {"shape": "rectangle", "fill": SEMANTIC_FILL["input"],      "w": 100, "h": 40},
    "entity":   {"shape": "rectangle", "fill": SEMANTIC_FILL["input"],      "w": 160, "h": 70},
    "relation": {"shape": "diamond",   "fill": SEMANTIC_FILL["note"],       "w": 140, "h": 60},
    "component":{"shape": "rectangle", "fill": "#ffffff",                   "w": 160, "h": 60},
    "service":  {"shape": "rectangle", "fill": SEMANTIC_FILL["processing"], "w": 160, "h": 60},
    "database": {"shape": "ellipse",   "fill": SEMANTIC_FILL["storage"],    "w": 140, "h": 60},
    "topic":    {"shape": "ellipse",   "fill": SEMANTIC_FILL["input"],      "w": 120, "h": 60},
    "branch":   {"shape": "rectangle", "fill": SEMANTIC_FILL["processing"], "w": 140, "h": 50},
    "leaf":     {"shape": "rectangle", "fill": SEMANTIC_FILL["analysis"],   "w": 140, "h": 50},
    "input":    {"shape": "rectangle", "fill": SEMANTIC_FILL["input"],      "w": 160, "h": 60},
    "output":   {"shape": "rectangle", "fill": SEMANTIC_FILL["output"],     "w": 160, "h": 60},
    "marker":   {"shape": "ellipse",   "fill": "#ffffff",                   "w": 14,  "h": 14},
    "milestone":{"shape": "ellipse",   "fill": SEMANTIC_FILL["input"],      "w": 60,  "h": 60},
    "plain":    {"shape": "rectangle", "fill": "#ffffff",                   "w": 160, "h": 60},
}

# 简单 tech 名称 → 节点类型映射（完整版见 tech-node-templates.md）
TECH_TYPE_HINTS = {
    "postgres": "database", "postgresql": "database", "mysql": "database",
    "mongodb": "database", "redis": "database", "elasticsearch": "database",
    "sqlite": "database", "dynamodb": "database", "cassandra": "database",
    "kafka": "service", "rabbitmq": "service", "sqs": "service", "sns": "service",
    "s3": "component", "gcs": "component", "hdfs": "component",
    "nginx": "component", "kong": "component", "envoy": "component", "traefik": "component",
    "lambda": "component", "ec2": "component", "fargate": "component",
    "k8s": "component", "kubernetes": "component", "docker": "component",
    "cd": "component", "prometheus": "component", "grafana": "component",
}

# 主题（对应 color-palette.md）
THEMES = {
    "default": {
        "strokeColor": "#1e1e1e", "bg": "#ffffff", "lineColor": "#868e96",
        "roughness": 1, "strokeWidth": 2, "textColor": "#374151",
        "titleColor": "#1e40af", "frameText": "#1971c2",
    },
    "sketch": {
        "strokeColor": "#2b2b2b", "bg": "#ffffff", "lineColor": "#868e96",
        "roughness": 2, "strokeWidth": 3, "textColor": "#374151",
        "titleColor": "#1e40af", "frameText": "#1971c2",
    },
    "blueprint": {
        "strokeColor": "#e8f4ff", "bg": "#1e3a5f", "lineColor": "#64b5f6",
        "roughness": 0, "strokeWidth": 1, "textColor": "#e8f4ff",
        "titleColor": "#e8f4ff", "frameText": "#e8f4ff",
    },
    "minimal": {
        "strokeColor": "#000000", "bg": "#ffffff", "lineColor": "#666666",
        "roughness": 0, "strokeWidth": 1, "textColor": "#000000",
        "titleColor": "#000000", "frameText": "#000000",
    },
}

LAYER_BG = ["#dbe4ff", "#e5dbff", "#d3f9d8", "#ffe8cc", "#fcc2d7"]
LAYER_FRAME_TEXT = ["#1971c2", "#6741d9", "#2f9e44", "#e8590c", "#c2255c"]


# ─── 基础元素构造 ─────────────────────────────────────────────────────────
def _base_el(el_id, etype, x, y, w, h, theme, extra=None):
    el = {
        "id": el_id, "type": etype, "x": x, "y": y,
        "width": w, "height": h, "angle": 0,
        "strokeColor": theme["strokeColor"],
        "backgroundColor": "#ffffff",
        "fillStyle": "solid", "strokeWidth": theme["strokeWidth"],
        "strokeStyle": "solid", "roughness": theme["roughness"],
        "opacity": 100, "groupIds": [], "frameId": None,
        # Python's hash is salted per process; derive stable values from the id.
        "roundness": None, "seed": int(hashlib.sha256(el_id.encode("utf-8")).hexdigest()[:8], 16) % 100000,
        "version": 1, "versionNonce": 0, "isDeleted": False,
        # Keep generated scenes byte-stable by default.  Set EXCALIDRAW_UPDATED
        # explicitly when an external timestamp is required.
        "boundElements": None, "updated": int(os.environ.get("EXCALIDRAW_UPDATED", "1")),
        "link": None, "locked": False,
    }
    if etype == "rectangle":
        el["roundness"] = {"type": 3}
    if etype == "frame":
        el["name"] = ""
    if extra:
        el.update(extra)
    return el


def _text_el(el_id, x, y, text, theme, fontSize=18, w=None, h=None, color=None, container_id=None):
    if w is None:
        w = max(40, int(estimate_text_width(text, fontSize) + 20))
    if h is None:
        h = fontSize + 8
    el = _base_el(el_id, "text", x, y, w, h, theme, {
        "strokeColor": color or theme["textColor"],
        "backgroundColor": "transparent",
        "text": text, "fontSize": fontSize, "fontFamily": 1,
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": container_id, "originalText": text, "lineHeight": 1.25,
    })
    return el


def estimate_text_width(text, font_size):
    w = 0
    for ch in str(text):
        w += 1.0 if ord(ch) > 0x2E80 else 0.6
    return w * font_size


def _library_text_color(elements):
    """Choose readable text from the dominant visible library fill."""
    fills = []
    for el in elements:
        color = el.get("backgroundColor")
        if el.get("type") not in ("rectangle", "ellipse", "diamond") or not isinstance(color, str) or not color.startswith("#") or color in ("#ffffff", "#fff"):
            continue
        try:
            h = color.lstrip("#")
            if len(h) == 3: h = "".join(c * 2 for c in h)
            rgb = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
            linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
            lum = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
            area = float(el.get("width", 0) or 0) * float(el.get("height", 0) or 0)
            fills.append((area, lum))
        except ValueError:
            continue
    return "#ffffff" if fills and max(fills)[1] < 0.30 else "#374151"


def _arrow_el(el_id, x, y, points, theme, from_id, to_id, style="solid", bidirectional=False):
    return _base_el(el_id, "arrow", x, y, 0, 0, theme, {
        "strokeColor": theme["lineColor"],
        "backgroundColor": "transparent",
        "strokeStyle": style, "roundness": {"type": 2},
        "points": points,
        "startBinding": {"elementId": from_id, "focus": 0.5, "gap": 8},
        "endBinding": {"elementId": to_id, "focus": 0.5, "gap": 8},
        "startArrowhead": "arrow" if bidirectional else None,
        "endArrowhead": "arrow",
    })


# ─── 布局计算（内置简单布局器）─────────────────────────────────────────────
def _layout_vertical(nodes, node_styles, start_x=100, start_y=60, v_gap=100):
    """流程/顺序布局：从上到下排列"""
    positions = {}
    y = start_y
    max_w = 0
    for node in nodes:
        st = node_styles[node["id"]]
        x = start_x + (max_w - st["w"]) // 2
        positions[node["id"]] = (x, y)
        y += st["h"] + v_gap
        max_w = max(max_w, st["w"])
    return positions


def _layout_tree(nodes, node_styles, root_id=None, start_x=100, start_y=60, h_gap=140, v_gap=80):
    """树形布局（思维导图/层级图）：DFS 逐层展开"""
    children_map = {}
    for node in nodes:
        for cid in node.get("children", []):
            children_map.setdefault(node["id"], []).append(cid)
    # roots = 不是任何其他节点 children 的节点
    child_ids = set()
    for kids in children_map.values():
        child_ids.update(kids)
    roots = [n["id"] for n in nodes if n["id"] not in child_ids]
    if root_id:
        roots = [root_id]
    positions = {}

    def place(nid, x, y):
        st = node_styles.get(nid, {"w": 140, "h": 50})
        positions[nid] = (x, y)
        kids = children_map.get(nid, [])
        if not kids:
            return y
        child_y = y
        for kid in kids:
            child_y = place(kid, x + st["w"] + h_gap, child_y)
            child_y += v_gap
        # 居中父节点
        first = positions.get(kids[0])
        last = positions.get(kids[-1])
        if first and last:
            cy = (first[1] + last[1]) / 2
            positions[nid] = (x, cy)
        return child_y

    y = start_y
    for rid in roots:
        y = place(rid, start_x, y)
        y += v_gap * 2
    return positions


def _layout_layered(nodes, node_styles, groups, start_x=60, start_y=60, v_gap=120, h_gap=100):
    """分层布局（架构图）：按 group level 分列"""
    positions = {}
    # group level → 节点
    level_nodes = {}
    node_level = {}
    for g in groups:
        for nid in g.get("nodes", []):
            level_nodes.setdefault(g.get("level", 0), []).append(nid)
            node_level[nid] = g.get("level", 0)
    ungrouped = [n["id"] for n in nodes if n["id"] not in node_level]
    if ungrouped:
        level_nodes.setdefault(0, []).extend(ungrouped)
    y = start_y
    for level in sorted(level_nodes.keys()):
        ids = level_nodes[level]
        x = start_x
        for nid in ids:
            st = node_styles[nid]
            positions[nid] = (x, y)
            x += st["w"] + h_gap
        y += max((node_styles[i]["h"] for i in ids), default=60) + v_gap
    return positions


def _layout_horizontal(nodes, node_styles, start_x=80, start_y=60, h_gap=200, v_gap=60):
    """水平布局（时序图/时间线）"""
    positions = {}
    x = start_x
    for node in nodes:
        st = node_styles[node["id"]]
        positions[node["id"]] = (x, start_y)
        x += st["w"] + h_gap
    return positions


def _layout_swimlane(nodes, node_styles, groups, start_x=60, start_y=60, h_gap=100, v_gap=100):
    """泳道布局：每个 group 一横行，节点从左到右"""
    positions = {}
    lane_nodes = {}
    for g in groups:
        for nid in g.get("nodes", []):
            lane_nodes.setdefault(g["id"], []).append(nid)
    lane_ids = [g["id"] for g in groups]
    y = start_y
    for gid in lane_ids:
        ids = lane_nodes.get(gid, [])
        x = start_x + 80
        for nid in ids:
            st = node_styles[nid]
            positions[nid] = (x, y)
            x += st["w"] + h_gap
        y += max((node_styles[i]["h"] for i in ids), default=50) + v_gap
    return positions


def _layout_table(nodes, node_styles, metadata, start_x=20, start_y=80, col_w=180, row_h=35):
    """表格布局（对比图）"""
    positions = {}
    cmp = metadata.get("comparison", {})
    dims = cmp.get("dimensions", [])
    cols = cmp.get("columns", [])
    rows = cmp.get("rows", [])
    # 表头
    positions["header-a"] = (start_x + 80, start_y - 40)
    positions["header-b"] = (start_x + 80 + col_w, start_y - 40)
    y = start_y
    for i, dim in enumerate(dims):
        positions[f"dim-{i}"] = (start_x, y)
        positions[f"val-a-{i}"] = (start_x + 80, y)
        positions[f"val-b-{i}"] = (start_x + 80 + col_w, y)
        y += row_h
    return positions


def _layout_graphviz(ir_nodes, ir_edges, node_styles, engine="dot"):
    """Graphviz 自动布局（借鉴 drawmode + excalidraw-architect-mcp）。

    把 IR 节点/边转成 DOT 源码，运行 graphviz（dot/neato/twopi），解析
    "pos" 属性得到节点坐标。返回 {node_id: (x, y)}，坐标为图中心坐标，
    转换时需换算为元素左上角（减去宽高一半）。

    需要系统安装 graphviz（brew install graphviz）。找不到时返回 None。
    """
    dot_bin = shutil.which(engine)
    if not dot_bin:
        return None

    lines = [f"digraph G {{", "  graph [pad=0.5, nodesep=1.6, ranksep=1.8];",
             "  node [shape=box, width=2.2, height=0.8, fixedsize=true];"]
    for node in ir_nodes:
        nid = node["id"]
        label = node.get("label", nid).replace('"', '\\"')
        lines.append(f'  "{nid}" [label="{label}"];')
    for edge in ir_edges:
        lines.append(f'  "{edge["from"]}" -> "{edge["to"]}";')
    lines.append("}")
    dot_src = "\n".join(lines)

    try:
        # -Tplain 输出节点坐标（node name x y w h label）
        r = subprocess.run(
            [dot_bin, "-Tplain"],
            input=dot_src, capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            return None
    except (subprocess.SubprocessError, OSError):
        return None

    positions = {}
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "node":
            nid = parts[1].strip('"')
            x, y = float(parts[2]), float(parts[3])
            positions[nid] = (x, y)
    return positions


# ─── 主转换 ────────────────────────────────────────────────────────────────
def convert(ir, template_override=None, layout_engine=None, icons=False, library=False):
    """IR dict → .excalidraw dict"""
    template = template_override or ir.get("template", "flowchart")
    theme_key = ir.get("theme", "default")
    theme = THEMES.get(theme_key, THEMES["default"])
    direction = ir.get("direction")
    metadata = ir.get("metadata", {})
    ir_nodes = ir.get("nodes", [])
    ir_edges = ir.get("edges", [])
    ir_groups = ir.get("groups", [])

    # 1. 解析节点样式
    node_styles = {}
    for node in ir_nodes:
        nid = node["id"]
        style = dict(NODE_TYPE_STYLE.get(node.get("type", "plain"), NODE_TYPE_STYLE["plain"]))
        # tech 名称提示（style 字段优先）
        hint_key = str(node.get("style", "")).lower() or node.get("label", "").lower()
        for tech, ntype in TECH_TYPE_HINTS.items():
            if tech in hint_key:
                style = dict(NODE_TYPE_STYLE[ntype])
                break
        # 用户自定义形状/颜色
        if isinstance(node.get("style"), str) and node["style"].startswith("#"):
            style["fill"] = node["style"]
        node_styles[nid] = style

    # Library components have their own geometry. Resolve their bounding boxes
    # before any layout engine runs so spacing, frames and arrow anchors use
    # the actual rendered dimensions (not the placeholder node style).
    lib_loader = None
    lib_matches = {}
    if library:
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            import library_loader as _ll
            lib_loader = _ll
            for node in ir_nodes:
                match = lib_loader.lookup_component(node.get("type", "plain"), node.get("label", ""))
                if not match:
                    continue
                raw_elements, scale = match
                _, _, raw_w, raw_h = lib_loader._bounding_box(raw_elements)
                if raw_w > 0 and raw_h > 0:
                    node_styles[node["id"]]["w"] = raw_w * scale
                    node_styles[node["id"]]["h"] = raw_h * scale
                    lib_matches[node["id"]] = (raw_elements, scale)
        except ImportError:
            print("[WARN] library_loader.py 不可用，跳过库组件替换", file=sys.stderr)
            library = False

    # 2. 布局
    if layout_engine in ("dot", "neato", "twopi"):
        positions = _layout_graphviz(ir_nodes, ir_edges, node_styles, layout_engine)
        if positions is None:
            print(
                f"[WARN] Graphviz ({layout_engine}) 不可用，回退到内置布局。"
                "安装: brew install graphviz",
                file=sys.stderr,
            )
            positions = None
        else:
            # Graphviz 返回英寸单位节点中心坐标；换算为像素（×72）后
            # 再转为 Excalidraw 左上角坐标
            for nid, (cx, cy) in positions.items():
                st = node_styles.get(nid, {"w": 160, "h": 60})
                positions[nid] = (cx * 72 - st["w"] / 2, cy * 72 - st["h"] / 2)
    else:
        positions = None

    if positions is None and template == "flowchart":
        positions = _layout_vertical(ir_nodes, node_styles)
    elif positions is None and template in ("mindmap", "hierarchy"):
        positions = _layout_tree(ir_nodes, node_styles)
    elif positions is None and template == "architecture":
        positions = _layout_layered(ir_nodes, node_styles, ir_groups)
    elif positions is None and template == "swimlane":
        positions = _layout_swimlane(ir_nodes, node_styles, ir_groups)
    elif positions is None and template in ("sequence", "timeline"):
        positions = _layout_horizontal(ir_nodes, node_styles)
    elif positions is None and template == "comparison":
        positions = _layout_table(ir_nodes, node_styles, metadata)
    elif positions is None:
        positions = _layout_vertical(ir_nodes, node_styles)

    # 手动位置覆盖
    for node in ir_nodes:
        if node.get("position"):
            positions[node["id"]] = (node["position"]["x"], node["position"]["y"])

    elements = []

    # 3. 生成分组 frame
    frame_ids = set()
    for gi, g in enumerate(ir_groups):
        gid = g["id"]
        frame_ids.add(gid)
        xs = [positions.get(nid, (0, 0))[0] for nid in g.get("nodes", []) if nid in positions]
        ys = [positions.get(nid, (0, 0))[1] for nid in g.get("nodes", []) if nid in positions]
        ws = [node_styles[nid]["w"] for nid in g.get("nodes", []) if nid in positions]
        hs = [node_styles[nid]["h"] for nid in g.get("nodes", []) if nid in positions]
        if not xs:
            continue
        fx = min(xs) - 20
        fy = min(ys) - 40
        fw = max(x + w for x, w in zip(xs, ws)) - fx + 20
        fh = max(y + h for y, h in zip(ys, hs)) - fy + 20
        bg = g.get("backgroundColor") or LAYER_BG[gi % len(LAYER_BG)]
        frame = _base_el(f"frame-{gid}", "frame", fx, fy, fw, fh, theme, {
            "backgroundColor": bg, "opacity": 30, "name": g.get("name", ""),
            "strokeWidth": 1,
        })
        elements.append(frame)
        # Frame `name` is rendered by Excalidraw; avoid a duplicate title text.

    # 4. 生成节点元素
    # 4.1 库组件加载器（如果启用 --library）
    lib_components = {}  # nid → (normalized_elements, bbox)

    # 4.2 查找每个节点的库组件匹配
    if library and lib_loader:
        for node in ir_nodes:
            nid = node["id"]
            if nid not in positions:
                continue
            result = lib_matches.get(nid)
            if result:
                raw_elements, scale = result
                x, y = positions[nid]
                st = node_styles[nid]
                # 库组件居中到原节点位置
                # 先算出缩放后的组件尺寸，然后偏移使其居中
                _, _, raw_w, raw_h = lib_loader._bounding_box(raw_elements)
                scaled_w = raw_w * scale
                scaled_h = raw_h * scale
                # 居中偏移：原节点中心 → 库组件左上角
                center_x = x + st["w"] / 2
                center_y = y + st["h"] / 2
                offset_x = center_x - scaled_w / 2
                offset_y = center_y - scaled_h / 2
                normed, bbox = lib_loader.normalize_component(
                    raw_elements, target_x=offset_x, target_y=offset_y, scale=scale
                )
                lib_components[nid] = (normed, bbox)
                # 更新节点样式为库组件的实际尺寸（用于箭头绑定）
                node_styles[nid]["w"] = scaled_w
                node_styles[nid]["h"] = scaled_h

    # 4.3 生成节点元素
    for node in ir_nodes:
        nid = node["id"]
        if nid not in positions:
            continue
        x, y = positions[nid]
        st = node_styles[nid]
        shape = st["shape"]
        w, h = st["w"], st["h"]
        frame_id = None
        for g in ir_groups:
            if nid in g.get("nodes", []):
                frame_id = f"frame-{g['id']}"
                break

        if nid in lib_components:
            # 使用库组件替换简单形状
            lib_els, lib_bbox = lib_components[nid]
            label = node.get("label", "")
            # 用库组件的元素替换节点
            # 为库组件中的主要形状元素设置 boundElements（用于箭头绑定）
            # 策略：优先选择面积最大的矩形作为锚定元素；
            # 如果没有合适矩形（如 Database 只有 line+ellipse），则添加一个
            # 透明矩形覆盖整个组件，作为箭头绑定目标
            anchor_el = None
            anchor_area = 0
            for lel in lib_els:
                if lel.get("type") in ("rectangle", "ellipse", "diamond"):
                    area = (lel.get("width", 0) or 0) * (lel.get("height", 0) or 0)
                    # 优先选矩形（矩形更适合作为箭头绑定目标）
                    if lel.get("type") == "rectangle" and area > anchor_area:
                        anchor_area = area
                        anchor_el = lel
                    elif anchor_el is None and area > anchor_area:
                        anchor_area = area
                        anchor_el = lel
            # 如果锚定元素太小（面积 < 组件面积 50%），添加透明覆盖矩形
            if anchor_el is None or anchor_area < lib_bbox["width"] * lib_bbox["height"] * 0.3:
                # 创建一个透明矩形覆盖整个组件，作为箭头绑定目标
                anchor_el = _base_el(nid, "rectangle", lib_bbox["x"], lib_bbox["y"],
                                     lib_bbox["width"], lib_bbox["height"], theme, {
                    "backgroundColor": "transparent",
                    "fillStyle": "solid",
                    "strokeColor": "transparent",
                    "strokeWidth": 0,
                    "opacity": 0,
                    "frameId": frame_id,
                    "boundElements": [],
                })
                # 将透明矩形插入到组件元素列表前面（最底层）
                lib_els.insert(0, anchor_el)
            else:
                # 重命名锚定元素 ID 为节点 ID，以便箭头绑定
                old_anchor_id = anchor_el["id"]
                anchor_el["id"] = nid
                # 更新库组件中其他元素对旧 ID 的引用
                for lel in lib_els:
                    if lel.get("boundElements") and isinstance(lel["boundElements"], list):
                        for be in lel["boundElements"]:
                            if be.get("id") == old_anchor_id:
                                be["id"] = nid
                # 设置锚定元素的 boundElements
                anchor_el["boundElements"] = []
                # 设置 frameId
                anchor_el["frameId"] = frame_id
            # Keep one centered title and at most one type subtitle; clear all
            # other library placeholder/description text.
            text_els = [lel for lel in lib_els if lel.get("type") == "text"]
            label_seen = False
            for index, lel in enumerate(text_els):
                value = label if index == 0 else (f"[{node.get('type', 'component')}]" if index == 1 else "")
                lel["text"] = value
                lel["originalText"] = value
                if not value:
                    continue
                available_w = max(24, lib_bbox["width"] - 12)
                font = min(float(lel.get("fontSize") or 16), 18.0)
                while font > 8 and estimate_text_width(value, font) > available_w:
                    font -= 1
                lel["fontSize"] = font
                lel["width"] = available_w
                lel["height"] = max(18, font * 1.35)
                lel["x"] = lib_bbox["x"] + (lib_bbox["width"] - available_w) / 2
                title_ratio = 0.52 if node.get("type") == "database" else 0.38
                lel["y"] = lib_bbox["y"] + (lib_bbox["height"] * (title_ratio if index == 0 else 0.68)) - lel["height"] / 2
                lel["strokeColor"] = "#374151" if node.get("type") == "database" else _library_text_color(lib_els)
                lel["customData"] = {**(lel.get("customData") or {}), "libraryNodeId": nid, "libraryTitle": index == 0}
                if index == 0:
                    label_seen = True
            # Some libraries (notably cylinder/database symbols) contain no
            # usable text placeholder. Add one deterministic bound overlay so
            # every replaced IR node exposes its label exactly once.
            if not label_seen and label:
                available_w = max(24, lib_bbox["width"] - 12)
                font = 16.0
                while font > 8 and estimate_text_width(label, font) > available_w:
                    font -= 1
                overlay = _text_el(
                    f"libtxt-{nid}", lib_bbox["x"] + (lib_bbox["width"] - available_w) / 2,
                    lib_bbox["y"] + (lib_bbox["height"] - font * 1.35) / 2,
                    label, theme, fontSize=font, w=available_w, h=max(18, font * 1.35),
                    color=theme["textColor"], container_id=nid,
                )
                overlay["groupIds"] = list(anchor_el.get("groupIds") or [])
                overlay["frameId"] = frame_id
                overlay["customData"] = {"libraryNodeId": nid, "libraryTitle": True}
                lib_els.append(overlay)
                anchor_el.setdefault("boundElements", []).append({"id": overlay["id"], "type": "text"})
            # 添加所有库组件元素
            for lel in lib_els:
                if lel.get("frameId") is None and lel["id"] != nid:
                    lel["frameId"] = frame_id
                elements.append(lel)
        else:
            # 传统简单形状生成
            el = _base_el(nid, shape, x, y, w, h, theme, {
                "backgroundColor": st["fill"],
                "frameId": frame_id,
                "boundElements": [{"id": f"txt-{nid}", "type": "text"}],
            })
            elements.append(el)
            # 节点文字（容器内绑定）
            label = node.get("label", "")
            tw = max(40, w - 40)
            tx = x + (w - tw) / 2
            ty = y + (h - (node.get("type") in ("start", "end", "topic", "marker", "milestone") and 24 or 26)) / 2
            if shape == "diamond":
                ty = y + (h - 24) / 2
            text_color = theme["textColor"]
            if shape == "ellipse" and st["fill"] in (SEMANTIC_FILL["input"], SEMANTIC_FILL["storage"]):
                text_color = "#1e3a5f" if theme_key == "default" else theme["textColor"]
            elements.append(_text_el(
                f"txt-{nid}", tx, ty, label, theme, fontSize=18 if shape != "diamond" else 16,
                w=tw, h=24, color=text_color, container_id=nid,
            ))

    # 4.3 对比图：从 metadata.comparison 生成表格元素
    if template == "comparison":
        cmp = metadata.get("comparison", {})
        dims = cmp.get("dimensions", [])
        cols = cmp.get("columns", ["方案A", "方案B"])
        rows = cmp.get("rows", [])
        start_x = 60
        start_y = 100
        col_w = 180
        row_h = 35
        # 表头
        for ci, col in enumerate(cols):
            cx = start_x + 80 + ci * col_w
            el = _base_el(f"cmp-head-{ci}", "rectangle", cx - 10, start_y - 45, col_w - 20, 34, theme, {
                "backgroundColor": SEMANTIC_FILL["input"] if ci == 0 else SEMANTIC_FILL["processing"],
                "roundness": {"type": 3},
                "boundElements": [{"id": f"cmp-head-txt-{ci}", "type": "text"}],
            })
            elements.append(el)
            elements.append(_text_el(f"cmp-head-txt-{ci}", cx, start_y - 38, col, theme, fontSize=16, w=col_w - 40, h=22, container_id=f"cmp-head-{ci}"))
        # 分隔线
        elements.append(_base_el("cmp-sep", "line", start_x + 70, start_y - 40, 0, 0, theme, {
            "strokeStyle": "dashed", "strokeWidth": 1, "opacity": 50, "roughness": 0,
            "points": [[0, 0], [0, len(dims) * row_h + 10]],
        }))
        # 维度行
        for i, dim in enumerate(dims):
            dy = start_y + i * row_h
            elements.append(_text_el(f"cmp-dim-{i}", start_x, dy, dim, theme, fontSize=15, w=60, h=22, color=theme["titleColor"]))
            if i < len(rows):
                for ci in range(len(cols)):
                    val = rows[i][ci] if ci < len(rows[i]) else ""
                    vx = start_x + 80 + ci * col_w
                    elements.append(_text_el(f"cmp-val-{i}-{ci}", vx, dy, val, theme, fontSize=14, w=col_w - 20, h=22))
        # 已有 table positions 键保留（兼容）

    # 4.4 时间线图：生成水平时间轴
    if template == "timeline":
        axis_y = 140
        title_w = 200
        n = len(ir_nodes)
        if n > 0:
            first_x = positions.get(ir_nodes[0]["id"], (100, 0))[0]
            last_node = ir_nodes[-1]
            last_x, _ = positions.get(last_node["id"], (500, 0))
            axis_x = first_x - 20
            axis_len = (last_x - first_x) + 60
            elements.append(_base_el("tl-axis", "line", axis_x, axis_y, 0, 0, theme, {
                "strokeWidth": 3, "strokeColor": theme["strokeColor"],
                "points": [[0, 0], [axis_len, 0]],
            }))

    # 4.5 树形模板：从 children 关系自动生成边（mindmap/hierarchy）
    if template in ("mindmap", "hierarchy") and not ir_edges:
        auto_edges = []
        eidx = 1
        for node in ir_nodes:
            for cid in node.get("children", []):
                auto_edges.append({
                    "id": f"auto{eidx}", "from": node["id"], "to": cid,
                    "style": "solid", "label": None,
                })
                eidx += 1
        ir_edges = auto_edges

    # 5. 生成边（箭头）
    for edge in ir_edges:
        eid = edge["id"]
        frm, to = edge["from"], edge["to"]
        if frm not in positions or to not in positions:
            continue
        fx, fy = positions[frm]
        tx2, ty2 = positions[to]
        st_from = node_styles[frm]
        st_to = node_styles[to]
        # Layered diagrams use orthogonal routes through the whitespace between
        # rows; a deterministic lane offset separates fan-out edges.
        ax = fx + st_from["w"] / 2
        ay = fy + st_from["h"]
        dx = tx2 + st_to["w"] / 2 - ax
        dy = ty2 - ay
        pts = [[0, 0], [dx, dy]]
        if template in ("architecture", "swimlane") and abs(dy) > 20:
            lane = ((sum(ord(c) for c in str(eid)) % 5) - 2) * 12
            mid_y = (ay + ty2) / 2 + lane
            pts = [[0, 0], [0, mid_y - ay], [tx2 + st_to["w"] / 2 - ax, mid_y - ay], [dx, dy]]
        if direction == "horizontal" or (abs(dy) < 30 and dx != 0):
            ax = fx + st_from["w"]
            ay = fy + st_from["h"] / 2
            dx = tx2 - ax
            dy = ty2 + st_to["h"] / 2 - ay
            pts = [[0, 0], [dx, dy]]
        arrow_id = f"arrow-{eid}"
        el = _arrow_el(
            arrow_id, ax, ay, pts, theme,
            frm, to, style=edge.get("style", "solid"),
            bidirectional=edge.get("bidirectional", False),
        )
        elements.append(el)
        # 箭头反向绑定：起点/终点节点的 boundElements 追加该箭头
        for nid in (frm, to):
            for existing in elements:
                if existing["id"] == nid and existing["type"] in ("rectangle", "ellipse", "diamond"):
                    if existing.get("boundElements") is None:
                        existing["boundElements"] = []
                    existing["boundElements"].append({"id": arrow_id, "type": "arrow"})
                    break
        # 边标签
        if edge.get("label"):
            lx = ax + dx / 2 - 20
            ly = ay + dy / 2 - 14
            elements.append(_text_el(
                f"elbl-{eid}", lx, ly, edge["label"], theme,
                fontSize=13, w=60, h=20, color=theme["lineColor"],
            ))

    # 6. 标题
    if ir.get("title"):
        elements.append(_text_el(
            "title-0", 40, 10, ir["title"], theme,
            fontSize=24, w=400, h=30, color=theme["titleColor"],
        ))

    # 6.5 云架构图标注入（C.7，借鉴 excalidraw-icons-mcp）
    # 架构图节点按 label 匹配技术名，叠加 image 元素 + files 资源
    files = {}
    if icons:
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            import icon_library
        except ImportError:
            print("[WARN] icon_library.py 不可用，跳过图标注入", file=sys.stderr)
            icons = False
    if icons:
        registry = icon_library.build_registry()
        icon_elements = []
        used_files = set()
        for node in ir_nodes:
            nid = node["id"]
            if nid not in positions:
                continue
            hit = icon_library.match_icon(node.get("label", ""), registry)
            if not hit:
                continue
            x, y = positions[nid]
            st = node_styles.get(nid, {"w": 160, "h": 60})
            file_id = f"icon-{nid}"
            files[file_id] = {
                "mimeType": hit["mimeType"],
                "dataURL": hit["dataURL"],
            }
            # 图标放在节点左上角，尺寸 36x36
            icon_elements.append(_base_el(
                f"img-{nid}", "image", x + 6, y + 6, 36, 36, theme, {
                    "fileId": file_id,
                    "opacity": 90,
                    "customData": {"animate": {"order": 3, "duration": 500, "type": "fade-in", "delay": 300}},
                }
            ))
        # 图标追加到元素列表末尾（避免覆盖节点文字）
        elements.extend(icon_elements)

    # 7. 组装
    result = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "files": files,
        "appState": {
            "viewBackgroundColor": theme["bg"],
            "gridSize": 20,
        },
    }

    # 7.1 动画元数据注入（借鉴 excalimate：customData.animate + 7 级顺序规则）
    # 标题(1) → 框架(2) → 主要节点(3) → 连线(4) → 细节文字(5)
    for el in elements:
        etype = el["type"]
        if etype == "text" and el.get("id") == "title-0":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 1, "duration": 400, "type": "fade-in"}}
        elif etype == "frame":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 2, "duration": 400, "type": "fade-in"}}
        elif etype in ("rectangle", "ellipse", "diamond"):
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 3, "duration": 500, "type": "slide-up"}}
        elif etype == "arrow":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 4, "duration": 300, "type": "draw"}}
        elif etype == "text":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 5, "duration": 400, "type": "fade-in"}}

    return result


# ─── 示例 IR ───────────────────────────────────────────────────────────────
EXAMPLES = {
    "flowchart": {
        "version": 1,
        "title": "用户注册流程",
        "template": "flowchart",
        "theme": "default",
        "direction": "vertical",
        "nodes": [
            {"id": "n1", "label": "开始", "type": "start"},
            {"id": "n2", "label": "填写注册信息", "type": "process"},
            {"id": "n3", "label": "信息合法？", "type": "decision"},
            {"id": "n4", "label": "创建账号", "type": "process"},
            {"id": "n5", "label": "完成", "type": "end"},
        ],
        "edges": [
            {"id": "e1", "from": "n1", "to": "n2"},
            {"id": "e2", "from": "n2", "to": "n3"},
            {"id": "e3", "from": "n3", "to": "n4", "label": "是"},
            {"id": "e4", "from": "n3", "to": "n5", "label": "否"},
            {"id": "e5", "from": "n4", "to": "n5"},
        ],
        "metadata": {"scene": "business-process", "complexity": "simple"},
    },
    "architecture": {
        "version": 1,
        "title": "微服务架构",
        "template": "architecture",
        "theme": "default",
        "nodes": [
            {"id": "n1", "label": "Web 前端", "type": "component"},
            {"id": "n2", "label": "API 网关", "type": "component"},
            {"id": "n3", "label": "订单服务", "type": "service"},
            {"id": "n4", "label": "支付服务", "type": "service"},
            {"id": "n5", "label": "PostgreSQL", "type": "database"},
            {"id": "n6", "label": "Redis", "type": "database"},
        ],
        "edges": [
            {"id": "e1", "from": "n1", "to": "n2"},
            {"id": "e2", "from": "n2", "to": "n3"},
            {"id": "e3", "from": "n2", "to": "n4"},
            {"id": "e4", "from": "n3", "to": "n5"},
            {"id": "e5", "from": "n4", "to": "n6"},
        ],
        "groups": [
            {"id": "g1", "name": "用户层", "nodes": ["n1", "n2"], "level": 0},
            {"id": "g2", "name": "应用层", "nodes": ["n3", "n4"], "level": 1},
            {"id": "g3", "name": "数据层", "nodes": ["n5", "n6"], "level": 2},
        ],
        "metadata": {"scene": "tech-arch", "complexity": "medium"},
    },
    "mindmap": {
        "version": 1,
        "title": "项目计划",
        "template": "mindmap",
        "theme": "default",
        "nodes": [
            {"id": "n1", "label": "项目", "type": "topic"},
            {"id": "n2", "label": "需求", "type": "branch", "children": ["n5", "n6"]},
            {"id": "n3", "label": "开发", "type": "branch", "children": ["n7"]},
            {"id": "n4", "label": "测试", "type": "branch"},
            {"id": "n5", "label": "调研", "type": "leaf"},
            {"id": "n6", "label": "评审", "type": "leaf"},
            {"id": "n7", "label": "编码", "type": "leaf"},
        ],
        "edges": [],
        "metadata": {"scene": "knowledge", "complexity": "medium"},
    },
}


def main():
    ap = argparse.ArgumentParser(description="IR → Excalidraw JSON 转换器")
    ap.add_argument("input", nargs="?", help="IR JSON 文件路径")
    ap.add_argument("--output", "-o", help="输出 .excalidraw 文件路径")
    ap.add_argument("--validate", action="store_true", help="转换后运行校验")
    ap.add_argument("--example", help="使用内置示例：flowchart/architecture/mindmap")
    ap.add_argument("--template-list", action="store_true", help="列出支持的模板")
    ap.add_argument("--theme", help="覆盖主题：default/sketch/blueprint/minimal")
    ap.add_argument("--layout", help="布局引擎：dot/neato/twopi（Graphviz，需 brew install graphviz）")
    ap.add_argument("--icons", action="store_true", help="注入云架构技术图标（自包含 SVG，icon_library.py）")
    ap.add_argument("--library", action="store_true", help="使用 Excalidraw Libraries 组件替换简单形状（library_loader.py）")
    args = ap.parse_args()

    if args.template_list:
        print("支持模板:", ", ".join(NODE_TYPE_STYLE.keys()))
        print("节点类型:", ", ".join(sorted(set(n["type"] for n in NODE_TYPE_STYLE.values()) or [])) or "见 NODE_TYPE_STYLE")
        return

    if args.example:
        if args.example not in EXAMPLES:
            print(f"示例不存在: {args.example}，可用: {', '.join(EXAMPLES.keys())}")
            sys.exit(1)
        ir = EXAMPLES[args.example]
    elif args.input:
        with open(args.input, "r") as f:
            ir = json.load(f)
    else:
        ap.print_help()
        sys.exit(1)

    if args.theme:
        ir = dict(ir)
        ir["theme"] = args.theme

    result = convert(ir, layout_engine=args.layout, icons=args.icons, library=args.library)

    out_path = args.output
    if not out_path:
        name = ir.get("title") or args.example or os.path.splitext(os.path.basename(args.input or ""))[0] or "diagram"
        out_path = f"output/{name}-{time.strftime('%Y%m%d-%H%M')}.excalidraw"
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"已生成: {out_path}")
    print(f"  元素数: {len(result['elements'])}")
    by_type = {}
    for el in result["elements"]:
        by_type[el["type"]] = by_type.get(el["type"], 0) + 1
    print(f"  类型统计: {by_type}")
    print(f"  主题: {ir.get('theme', 'default')}  布局: {args.layout or '内置'}  图标: {'是' if args.icons else '否'}  库组件: {'是' if args.library else '否'}")

    if args.validate:
        import subprocess
        r = subprocess.run(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "validate_excalidraw.py"),
                out_path,
                "--visual",
            ],
            capture_output=True, text=True,
        )
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
