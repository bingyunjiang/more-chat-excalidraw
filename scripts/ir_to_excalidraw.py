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
    "note":     {"shape": "rectangle", "fill": SEMANTIC_FILL["note"],       "w": 220, "h": 90},
    "callout":  {"shape": "rectangle", "fill": SEMANTIC_FILL["warning"],    "w": 240, "h": 100},
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

# 中文字体策略：所有模板和主题统一使用已随本地编辑器注册的手写字体。
# 英文仍使用各主题自己的 Virgil / Helvetica，以保持主题层级。
CJK_HANDWRITING = {
    "cjkFontFamily": "Ma Shan Zheng",
    "cjkFontFamilyId": 11,
    "cjkFontFallbacks": [
        "Long Cang", "Liu Jian Mao Cao", "Hannotate SC",
        "HanziPen SC", "Wawati SC", "Kaiti SC", "PingFang SC",
    ],
}

# 主题（对应 color-palette.md）
THEMES = {
    "default": {
        "strokeColor": "#1e1e1e", "bg": "#ffffff", "lineColor": "#868e96",
        "roughness": 1, "strokeWidth": 2, "textColor": "#374151",
        "titleColor": "#1e40af", "frameText": "#1971c2", "fontFamily": 1,
        **CJK_HANDWRITING,
    },
    "sketch": {
        "strokeColor": "#2b2b2b", "bg": "#ffffff", "lineColor": "#868e96",
        "roughness": 2, "strokeWidth": 3, "textColor": "#374151",
        "titleColor": "#1e40af", "frameText": "#1971c2", "fontFamily": 1,
        **CJK_HANDWRITING,
        "edgeLabelFontSize": 32, "edgeLabelOffset": 24,
    },
    "blueprint": {
        "strokeColor": "#e8f4ff", "bg": "#1e3a5f", "lineColor": "#64b5f6",
        "roughness": 0, "strokeWidth": 1, "textColor": "#e8f4ff",
        "titleColor": "#e8f4ff", "frameText": "#e8f4ff", "fontFamily": 2,
        **CJK_HANDWRITING,
    },
    "minimal": {
        "strokeColor": "#64748b", "bg": "#ffffff", "lineColor": "#64748b",
        "roughness": 0, "strokeWidth": 1, "textColor": "#1f2937",
        "titleColor": "#0f172a", "frameText": "#475569", "fontFamily": 2,
        **CJK_HANDWRITING,
    },
}

# Small, intentionally opinionated sketch presets.  Presets change the visual
# grammar (not just a colour swap) while keeping the legacy ``theme=sketch``
# contract and deterministic output intact.
SKETCH_STYLES = {
    "engineering-notebook": {
        "strokeColor": "#34302b", "lineColor": "#6b6258", "titleColor": "#7c2d12",
        "roughness": 2, "strokeWidth": 3, "accent": "#f59f00", "spacing": 1.15,
    },
    "research-board": {
        "strokeColor": "#263238", "lineColor": "#546e7a", "titleColor": "#155e75",
        "roughness": 2, "strokeWidth": 2, "accent": "#0e7490", "spacing": 1.25,
    },
    "root-cause": {
        "strokeColor": "#3b2525", "lineColor": "#9f1239", "titleColor": "#9f1239",
        "roughness": 2, "strokeWidth": 3, "accent": "#e11d48", "spacing": 1.2,
    },
    "mechanism-map": {
        "strokeColor": "#2f3a2f", "lineColor": "#3f6212", "titleColor": "#3f6212",
        "roughness": 2, "strokeWidth": 3, "accent": "#65a30d", "spacing": 1.3,
    },
    "review-markup": {
        "strokeColor": "#292524", "lineColor": "#57534e", "titleColor": "#b45309",
        "roughness": 2, "strokeWidth": 2, "accent": "#d97706", "spacing": 1.1,
    },
}

LAYER_BG = ["#dbe4ff", "#e5dbff", "#d3f9d8", "#ffe8cc", "#fcc2d7"]
LAYER_FRAME_TEXT = ["#1971c2", "#6741d9", "#2f9e44", "#e8590c", "#c2255c"]
FONT_FAMILY_MAP = {
    "hand": 1, "virgil": 1,
    "sans": 2, "helvetica": 2,
    "mono": 3, "cascadia": 3,
    "ma shan zheng": 11, "ma-shan-zheng": 11, "mashanzheng": 11,
    "long cang": 12, "long-cang": 12, "longcang": 12,
    "liu jian mao cao": 13, "liu-jian-mao-cao": 13, "liujianmaocao": 13,
}


def _has_cjk(text):
    return any(ord(ch) >= 0x2E80 for ch in str(text))


def _bilingual_lines(label):
    lines = [line for line in str(label).splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    if not any(_has_cjk(line) for line in lines):
        return None
    if not any(not _has_cjk(line) for line in lines):
        return None
    return lines


def _apply_text_font(el, text, theme):
    """Apply the global CJK-handwriting / theme-Latin font policy."""
    if _has_cjk(text) and theme.get("cjkFontFamily"):
        el["fontFamily"] = int(theme.get("cjkFontFamilyId", 11))
    else:
        el["fontFamily"] = int(theme.get("fontFamily", 1))
    if theme.get("cjkFontFamily"):
        el["customData"] = {
            **(el.get("customData") or {}),
            "cjkFontFamily": theme["cjkFontFamily"],
            "cjkFontFallbacks": theme.get("cjkFontFallbacks", []),
        }
    return el


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
        "text": text, "fontSize": fontSize, "fontFamily": theme.get("fontFamily", 1),
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": container_id, "originalText": text, "lineHeight": 1.25,
    })
    return _apply_text_font(el, text, theme)


def estimate_text_width(text, font_size):
    widths = []
    for line in str(text).splitlines() or [""]:
        width = 0
        for ch in line:
            width += 1.0 if ord(ch) > 0x2E80 else 0.6
        widths.append(width * font_size)
    return max(widths, default=0)


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


def _text_color_for_fill(fill, fallback):
    if not isinstance(fill, str) or not fill.startswith("#"):
        return fallback
    try:
        h = fill.lstrip("#"); h = "".join(c * 2 for c in h) if len(h) == 3 else h
        rgb = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        lum = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
        return "#ffffff" if lum < 0.30 else "#374151"
    except (ValueError, IndexError):
        return fallback


def _node_center(x, y, style):
    return x + style["w"] / 2, y + style["h"] / 2


def _boundary_point(x, y, style, toward_x, toward_y):
    """Point where the center→target ray leaves a node bbox."""
    cx, cy = _node_center(x, y, style)
    dx, dy = toward_x - cx, toward_y - cy
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return cx, cy
    half_w = max(float(style["w"]) / 2, 1)
    half_h = max(float(style["h"]) / 2, 1)
    scale = min(
        half_w / abs(dx) if abs(dx) > 1e-9 else float("inf"),
        half_h / abs(dy) if abs(dy) > 1e-9 else float("inf"),
    )
    return cx + dx * scale, cy + dy * scale


def _edge_boundary_points(fx, fy, st_from, tx, ty, st_to):
    """Return visual start/end points on the two node boundaries."""
    fcx, fcy = _node_center(fx, fy, st_from)
    tcx, tcy = _node_center(tx, ty, st_to)
    return (
        _boundary_point(fx, fy, st_from, tcx, tcy),
        _boundary_point(tx, ty, st_to, fcx, fcy),
    )


def _arrow_el(
    el_id, x, y, points, theme, from_id, to_id, style="solid",
    bidirectional=False, curved=False, color=None, stroke_width=None,
    start_arrowhead=None, end_arrowhead="arrow",
):
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    width = max(xs) - min(xs) if xs else 0
    height = max(ys) - min(ys) if ys else 0
    return _base_el(el_id, "arrow", x, y, width, height, theme, {
        "strokeColor": color or theme["lineColor"],
        "backgroundColor": "transparent", "strokeStyle": style,
        # Orthogonal routes must stay orthogonal after restoreElements(). A
        # rounded multi-point arrow can be reinterpreted as a large Bézier arc.
        "roundness": {"type": 2} if len(points) == 2 or curved else None,
        "strokeWidth": stroke_width or theme["strokeWidth"],
        "points": points,
        "startBinding": {"elementId": from_id, "focus": 0, "gap": 4},
        "endBinding": {"elementId": to_id, "focus": 0, "gap": 4},
        "startArrowhead": start_arrowhead or ("arrow" if bidirectional else None),
        "endArrowhead": end_arrowhead,
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


def _layout_swimlane(nodes, node_styles, groups, start_x=60, start_y=120, h_gap=80, v_gap=100):
    """泳道布局：每个 group 一横行，节点从左到右"""
    positions = {}
    lane_nodes = {}
    for g in groups:
        for nid in g.get("nodes", []):
            lane_nodes.setdefault(g["id"], []).append(nid)
    lane_ids = [g["id"] for g in groups]
    lane_widths = {}
    for gid in lane_ids:
        ids = lane_nodes.get(gid, [])
        lane_widths[gid] = sum(node_styles[nid]["w"] for nid in ids) + h_gap * max(0, len(ids) - 1)
    max_lane_width = max(lane_widths.values(), default=0)
    y = start_y
    for gid in lane_ids:
        ids = lane_nodes.get(gid, [])
        # Center shorter stages under the widest lane. Engineering workflows
        # then read around a stable visual axis instead of leaving a large,
        # accidental blank area to the right of later stages.
        x = start_x + 80 + (max_lane_width - lane_widths.get(gid, 0)) / 2
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


def _visual_contract_annotations(ir):
    """Validate and index an optional visual contract."""
    contract = ir.get("visual_contract")
    if contract is None:
        return None
    if not isinstance(contract, dict):
        raise ValueError("visual_contract must be an object")
    facts = contract.get("decisive_facts")
    if not isinstance(facts, list) or not 3 <= len(facts) <= 6:
        raise ValueError("visual_contract.decisive_facts must contain 3-6 facts")
    known_targets = {
        entry.get("id")
        for key in ("nodes", "edges")
        for entry in (ir.get(key) or [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry.get("id")
    }
    by_target, fact_ids = {}, set()
    for fact in facts:
        if not isinstance(fact, dict) or not isinstance(fact.get("id"), str) or not fact["id"]:
            raise ValueError("each visual fact needs a non-empty string id")
        fid = fact["id"]
        if fid in fact_ids:
            raise ValueError(f"duplicate visual fact id: {fid}")
        fact_ids.add(fid)
        if not isinstance(fact.get("statement"), str) or not fact["statement"].strip():
            raise ValueError(f"visual fact {fid!r} needs a statement")
        refs = [fact["refs"]] if isinstance(fact.get("refs"), str) else fact.get("refs")
        if not isinstance(refs, list) or not refs or len(set(refs)) != len(refs) or not all(isinstance(ref, str) and ref for ref in refs):
            raise ValueError(f"visual fact {fid!r} needs one or more refs")
        targets = [fact["targets"]] if isinstance(fact.get("targets"), str) else fact.get("targets", [])
        if not isinstance(targets, list) or not targets or len(set(targets)) != len(targets) or not all(isinstance(target, str) and target for target in targets):
            raise ValueError(f"visual fact {fid!r} targets must be one or more unique string IDs")
        unknown_targets = sorted(set(targets) - known_targets)
        if unknown_targets:
            raise ValueError(f"visual fact {fid!r} targets unknown IR IDs: {', '.join(unknown_targets)}")
        status = fact.get("status", "proposed")
        if status not in ("proposed", "confirmed"):
            raise ValueError(f"visual fact {fid!r} status must be proposed or confirmed")
        for target in targets:
            by_target.setdefault(target, []).append({
                "id": fid, "refs": refs, "role": fact.get("semanticRole"),
                "family": fact.get("family"), "status": status,
            })
    families = contract.get("visual_families")
    if not isinstance(families, dict) or not isinstance(families.get("primary"), str) or not families["primary"]:
        raise ValueError("visual_contract.visual_families.primary is required")
    supporting = [families["supporting"]] if isinstance(families.get("supporting"), str) else families.get("supporting", [])
    if not isinstance(supporting, list) or len(supporting) > 2 or len(set(supporting)) != len(supporting) or families["primary"] in supporting or not all(isinstance(v, str) and v for v in supporting):
        raise ValueError("visual_contract.visual_families.supporting must contain at most two distinct non-primary names")
    allowed = {families["primary"], *supporting}
    for fact in facts:
        if fact.get("family") and fact["family"] not in allowed:
            raise ValueError(f"visual fact {fact['id']!r} uses an undeclared family")
    for key in ("preserve", "allowed_abstraction", "forbidden_invention"):
        entries = contract.get(key, [])
        if not isinstance(entries, list) or not all(isinstance(item, (str, dict)) for item in entries):
            raise ValueError(f"visual_contract.{key} must be a list")
        if any(isinstance(item, dict) and item.get("status", "proposed") not in ("proposed", "confirmed") for item in entries):
            raise ValueError(f"visual_contract.{key} status must be proposed or confirmed")
    return {"by_target": by_target, "primary": families["primary"]}


def _apply_visual_contract(elements, ir):
    indexed = _visual_contract_annotations(ir)
    if indexed is None:
        return
    for el in elements:
        eid = el.get("id", "")
        target = (el.get("customData") or {}).get("libraryNodeId")
        if not target:
            for prefix in ("txt-", "libtxt-", "arrow-", "elbl-"):
                if eid.startswith(prefix):
                    target = eid[len(prefix):]
                    break
        if not target and el.get("type") in ("rectangle", "ellipse", "diamond"):
            target = eid
        facts = indexed["by_target"].get(target)
        if not facts:
            continue
        custom = dict(el.get("customData") or {})
        custom.update({
            "semanticRole": next((f["role"] for f in facts if f["role"]), "visual-fact"),
            "visualFactIds": [f["id"] for f in facts],
            "visualSources": sorted({ref for f in facts for ref in f["refs"]}),
            "visualFamily": facts[0]["family"] or indexed["primary"],
            "visualStatus": "confirmed" if all(f["status"] == "confirmed" for f in facts) else "proposed",
        })
        el["customData"] = custom


# ─── 主转换 ────────────────────────────────────────────────────────────────
def convert(ir, template_override=None, layout_engine=None, icons=False, library=False, library_dir=None):
    """IR dict → .excalidraw dict"""
    template = template_override or ir.get("template", "flowchart")
    theme_key = ir.get("theme", "default")
    theme = dict(THEMES.get(theme_key, THEMES["default"]))
    sketch_style = ir.get("sketchStyle", ir.get("preset"))
    if theme_key == "sketch" and sketch_style in SKETCH_STYLES:
        theme.update(SKETCH_STYLES[sketch_style])
        theme["sketchStyle"] = sketch_style
    direction = ir.get("direction")
    metadata = ir.get("metadata", {})
    cjk_font_family = ir.get("cjkFontFamily", metadata.get("cjkFontFamily", theme.get("cjkFontFamily")))
    cjk_font_fallbacks = ir.get(
        "cjkFontFallbacks", metadata.get("cjkFontFallbacks", theme.get("cjkFontFallbacks", []))
    )
    if isinstance(cjk_font_fallbacks, str):
        cjk_font_fallbacks = [cjk_font_fallbacks]
    elif not isinstance(cjk_font_fallbacks, list):
        cjk_font_fallbacks = []
    if cjk_font_family:
        theme["cjkFontFamily"] = str(cjk_font_family)
        theme["cjkFontFallbacks"] = [str(name) for name in cjk_font_fallbacks]
        theme["cjkFontFamilyId"] = FONT_FAMILY_MAP.get(str(cjk_font_family).lower(), 11)
    ir_nodes = ir.get("nodes", [])
    ir_edges = ir.get("edges", [])
    ir_groups = ir.get("groups", [])

    # Make sketch templates structurally distinct and deterministic.  The
    # flags are consumed below when routing edges and styling cards.
    sketch_template = theme_key == "sketch"

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
        # Size simple nodes from their semantic label before layout. Fixed
        # widths make engineering terms overflow ellipses/diamonds even when
        # the text element itself reports a valid container binding.
        if node.get("type") not in ("marker", "milestone"):
            label_font = float(node.get("fontSize") or (16 if style.get("shape") == "diamond" else 18))
            required_w = estimate_text_width(node.get("label", ""), label_font) + 40
            style["w"] = max(style["w"], min(280, required_w))
            line_count = max(1, len(str(node.get("label", "")).splitlines()))
            required_h = label_font * 1.25 * line_count + 28
            style["h"] = max(style["h"], min(180, required_h))
        if sketch_template:
                # Handwritten cards have a little more breathing room and a
                # restrained paper tint; semantic fills remain user-overridable.
            style["w"] = int(style["w"] * theme.get("spacing", 1.0))
            style["h"] = int(style["h"] * theme.get("spacing", 1.0))
            if not node.get("style"):
                if template == "relationship" and node.get("type") in ("topic", "note", "callout"):
                    style["fill"] = "#fff7ed" if node.get("type") != "topic" else "#ffedd5"
                elif template == "flowchart" and node.get("type") in ("process", "note", "callout"):
                    style["fill"] = "#fef3c7"
                elif template == "architecture" and node.get("type") in ("component", "service"):
                    style["fill"] = "#e0f2fe"
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
                match = lib_loader.lookup_component(
                    node.get("type", "plain"),
                    node.get("label", ""),
                    lib_dir=library_dir,
                )
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

    # Reserve a generous title safety band for sketch architecture boards;
    # review labels otherwise sit too close to the two-line heading.
    if sketch_template and template == "architecture" and ir.get("title"):
        positions = {nid: (x, y + 70) for nid, (x, y) in positions.items()}

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
                _apply_text_font(lel, value, theme)
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
                    color=("#374151" if node.get("type") == "database" else _library_text_color(lib_els)),
                    container_id=nid,
                )
                overlay["groupIds"] = list(anchor_el.get("groupIds") or [])
                overlay["frameId"] = frame_id
                overlay["customData"] = {
                    **(overlay.get("customData") or {}),
                    "libraryNodeId": nid,
                    "libraryTitle": True,
                }
                lib_els.append(overlay)
                anchor_el.setdefault("boundElements", []).append({"id": overlay["id"], "type": "text"})
            # 添加所有库组件元素
            for lel in lib_els:
                if lel.get("frameId") is None and lel["id"] != nid:
                    lel["frameId"] = frame_id
                elements.append(lel)
        else:
            # 传统简单形状生成
            node_extra = {
                "backgroundColor": st["fill"],
                "frameId": frame_id,
                "boundElements": [{"id": f"txt-{nid}", "type": "text"}],
            }
            for field in ("strokeColor", "strokeWidth", "strokeStyle", "roughness", "opacity"):
                if field in node:
                    node_extra[field] = node[field]
            el = _base_el(nid, shape, x, y, w, h, theme, node_extra)
            elements.append(el)
            # 节点文字（容器内绑定）
            label = node.get("label", "")
            font_size = float(node.get("fontSize") or (16 if shape == "diamond" else 18))
            tw = max(40, w - 40)
            tx = x + (w - tw) / 2
            text_color = node.get("textColor") or _text_color_for_fill(st["fill"], theme["textColor"])
            if shape == "ellipse" and st["fill"] in (SEMANTIC_FILL["input"], SEMANTIC_FILL["storage"]):
                text_color = "#1e3a5f" if theme_key == "default" else theme["textColor"]
            split_lines = _bilingual_lines(label) if theme.get("cjkFontFamily") else None
            if split_lines:
                line_gap = max(2, font_size * 0.18)
                line_specs = []
                for line in split_lines:
                    line_font = font_size + 2 if _has_cjk(line) else font_size
                    line_h = max(18, line_font * 1.22)
                    line_specs.append((line, line_font, line_h))
                text_h = sum(spec[2] for spec in line_specs) + line_gap * (len(line_specs) - 1)
                cursor_y = y + (h - text_h) / 2
                bound = []
                for idx, (line, line_font, line_h) in enumerate(line_specs):
                    line_has_cjk = _has_cjk(line)
                    suffix = "cjk" if line_has_cjk else "en"
                    tid = f"txt-{nid}-{suffix}" if idx < 2 else f"txt-{nid}-{idx}"
                    line_el = _text_el(
                        tid, tx, cursor_y, line, theme, fontSize=line_font,
                        w=tw, h=line_h, color=text_color,
                        container_id=nid if line_has_cjk else None,
                    )
                    elements.append(line_el)
                    if line_has_cjk:
                        bound.append({"id": tid, "type": "text"})
                    cursor_y += line_h + line_gap
                el["boundElements"] = bound
            else:
                line_count = max(1, len(str(label).splitlines()))
                text_h = max(24, font_size * 1.25 * line_count)
                ty = y + (h - text_h) / 2
                text_el = _text_el(
                    f"txt-{nid}", tx, ty, label, theme, fontSize=font_size,
                    w=tw, h=text_h, color=text_color, container_id=nid,
                )
                requested_font = node.get("fontFamily") or node.get("font")
                if requested_font is not None:
                    requested_key = str(requested_font).lower()
                    requested_family = FONT_FAMILY_MAP.get(requested_key, requested_font)
                    if not (theme.get("cjkFontFamily") and _has_cjk(label) and requested_family in (1, 2, 3)):
                        text_el["fontFamily"] = requested_family
                elements.append(text_el)

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
        if sketch_template and template == "relationship" and "curve" not in edge:
            edge = dict(edge)
            edge["curve"] = True
            edge["curveOffset"] = 28 + (sum(ord(c) for c in str(eid)) % 3) * 10
        if sketch_template and template == "flowchart" and edge.get("feedback"):
            edge = dict(edge)
            edge.setdefault("style", "dashed")
        # Start/end on node boundaries.  Earlier versions started at center or
        # fixed bottom/side points and let Excalidraw re-bind the arrow, which
        # made heads/tails drift or cross through cards in the native editor.
        (ax, ay), (end_x, end_y) = _edge_boundary_points(fx, fy, st_from, tx2, ty2, st_to)
        dx = end_x - ax
        dy = end_y - ay
        pts = [[0, 0], [dx, dy]]
        preferred_label_segment = None
        same_lane = abs((fy + st_from["h"] / 2) - (ty2 + st_to["h"] / 2)) < 30
        if template == "swimlane" and same_lane and tx2 < fx:
            # Backward loop inside one lane: route above the nodes instead of
            # drawing a straight line through the intermediate process boxes.
            ax = fx
            ay = fy + st_from["h"] / 2
            target_x = tx2 + st_to["w"]
            target_y = ty2 + st_to["h"] / 2
            lane = 50 + (sum(ord(c) for c in str(eid)) % 3) * 16
            dx = target_x - ax
            dy = target_y - ay
            pts = [[0, 0], [0, -lane], [dx, -lane], [dx, dy]]
            preferred_label_segment = 1
        elif template == "swimlane" and same_lane:
            # Normal lane flow is a short, direct horizontal connector.
            ax = fx + st_from["w"]
            ay = fy + st_from["h"] / 2
            dx = tx2 - ax
            dy = ty2 + st_to["h"] / 2 - ay
            pts = [[0, 0], [dx, dy]]
        elif template == "swimlane" and ty2 < fy:
            # Validation/refinement loops returning to an earlier lane travel
            # around the left edge of the diagram, keeping the main flow clear.
            ax = fx
            ay = fy + st_from["h"] / 2
            target_x = tx2
            target_y = ty2 + st_to["h"] / 2
            lane = 70 + (sum(ord(c) for c in str(eid)) % 3) * 20
            diagram_left = min((pos[0] for pos in positions.values()), default=min(fx, tx2))
            outer_x = diagram_left - lane
            dx = target_x - ax
            dy = target_y - ay
            pts = [[0, 0], [outer_x - ax, 0], [outer_x - ax, dy], [dx, dy]]
            preferred_label_segment = 1
        elif template in ("architecture", "swimlane") and abs(dy) > 20:
            lane = ((sum(ord(c) for c in str(eid)) % 5) - 2) * 12
            mid_y = (ay + end_y) / 2 + lane
            pts = [[0, 0], [0, mid_y - ay], [end_x - ax, mid_y - ay], [dx, dy]]
        if (direction == "horizontal" or (abs(dy) < 30 and dx != 0)) and not (
            template == "swimlane" and same_lane and tx2 < fx
        ):
            (ax, ay), (end_x, end_y) = _edge_boundary_points(fx, fy, st_from, tx2, ty2, st_to)
            dx = end_x - ax
            dy = end_y - ay
            pts = [[0, 0], [dx, dy]]
        if edge.get("curve") and len(pts) == 2:
            curve_offset = float(edge.get("curveOffset", 36))
            direction_sign = -1 if sum(ord(c) for c in str(eid)) % 2 else 1
            length = max((dx * dx + dy * dy) ** 0.5, 1)
            nx, ny = -dy / length, dx / length
            pts = [[0, 0], [dx / 2 + nx * curve_offset * direction_sign, dy / 2 + ny * curve_offset * direction_sign], [dx, dy]]
        arrow_id = f"arrow-{eid}"
        el = _arrow_el(
            arrow_id, ax, ay, pts, theme,
            frm, to, style=edge.get("style", "solid"),
            bidirectional=edge.get("bidirectional", False),
            curved=bool(edge.get("curve")), color=edge.get("color"),
            stroke_width=edge.get("strokeWidth"),
            start_arrowhead=edge.get("startArrowhead"),
            end_arrowhead=edge.get("endArrowhead", "arrow"),
        )
        if sketch_template:
            role = {
                "relationship": "semantic-curve",
                "flowchart": "feedback-loop" if edge.get("feedback") else "critical-path",
                "swimlane": "validation-loop" if edge.get("feedback") else "stage-handoff",
                "architecture": "dependency" if edge.get("dependency") else "review-link",
            }.get(template)
            if role:
                el["customData"] = {"sketchTemplateRole": role, "sketchStyle": sketch_style or "engineering-notebook"}
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
            label_font = float(edge.get("labelFontSize") or theme.get("edgeLabelFontSize", 13))
            label_h = max(20, label_font * 1.35)
            label_w = max(60, int(estimate_text_width(edge["label"], label_font) + label_font * 1.4))
            # Put the label on the longest routed segment. This keeps labels
            # attached to detours instead of floating across unrelated nodes.
            segments = list(zip(pts, pts[1:]))
            if preferred_label_segment is not None and preferred_label_segment < len(segments):
                p1, p2 = segments[preferred_label_segment]
            else:
                p1, p2 = max(
                    segments,
                    key=lambda pair: abs(pair[1][0] - pair[0][0]) + abs(pair[1][1] - pair[0][1]),
                )
            seg_dx, seg_dy = p2[0] - p1[0], p2[1] - p1[1]
            seg_len = max((seg_dx * seg_dx + seg_dy * seg_dy) ** 0.5, 1)
            nx, ny = -seg_dy / seg_len, seg_dx / seg_len
            # Prefer labels above mostly horizontal arrows; otherwise use a
            # deterministic side so neighboring labels do not pile up.
            if abs(seg_dx) >= abs(seg_dy):
                if ny > 0:
                    nx, ny = -nx, -ny
            elif (sum(ord(c) for c in str(eid)) % 2) and nx > 0:
                nx, ny = -nx, -ny
            elif not (sum(ord(c) for c in str(eid)) % 2) and nx < 0:
                nx, ny = -nx, -ny
            label_offset = float(edge.get("labelOffset") or theme.get("edgeLabelOffset", 10))
            if sketch_template and template == "relationship":
                label_offset = max(label_offset, 55)
            mx = ax + (p1[0] + p2[0]) / 2 + nx * label_offset
            my = ay + (p1[1] + p2[1]) / 2 + ny * label_offset
            lx = mx - label_w / 2
            ly = my - label_h / 2
            elements.append(_text_el(
                f"elbl-{eid}", lx, ly, edge["label"], theme,
                fontSize=label_font, w=label_w, h=label_h,
                color=edge.get("labelColor") or edge.get("color") or theme["lineColor"],
            ))

    # 6. 标题
    if ir.get("title"):
        title = str(ir["title"])
        min_x = min((positions[nid][0] for nid in positions), default=40)
        max_x = max(
            (positions[nid][0] + node_styles.get(nid, {"w": 0})["w"] for nid in positions),
            default=440,
        )
        min_y = min((positions[nid][1] for nid in positions), default=60)
        title_y = max(10, min_y - (125 if theme.get("cjkFontFamily") else 90))
        if theme.get("cjkFontFamily") and "·" in title and _has_cjk(title):
            cjk_title, english_title = [part.strip() for part in title.split("·", 1)]
            title_w = max(420, int(max(estimate_text_width(cjk_title, 24), estimate_text_width(english_title, 24)) + 80))
            title_x = min_x + (max_x - min_x - title_w) / 2
            elements.append(_text_el(
                "title-0-cjk", title_x, title_y, cjk_title, theme,
                fontSize=24, w=title_w, h=30, color=theme["titleColor"],
            ))
            elements.append(_text_el(
                "title-0-en", title_x, title_y + 28, english_title, theme,
                fontSize=22, w=title_w, h=28, color=theme["titleColor"],
            ))
        else:
            title_w = max(400, int(estimate_text_width(title, 24) + 40))
            title_x = min_x + (max_x - min_x - title_w) / 2
            elements.append(_text_el(
                "title-0", title_x, title_y, title, theme,
                fontSize=24, w=title_w, h=30, color=theme["titleColor"],
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
    if theme_key == "sketch":
        result["appState"]["sketchStyle"] = sketch_style or "engineering-notebook"
        result["appState"]["sketchTemplate"] = template
    if cjk_font_family:
        result["appState"]["cjkFontFamily"] = str(cjk_font_family)
        result["appState"]["cjkFontFallbacks"] = [str(name) for name in cjk_font_fallbacks]
    if ir.get("visual_contract") is not None:
        result["visual_contract"] = ir["visual_contract"]

    # 7.1 动画元数据注入（借鉴 excalimate：customData.animate + 7 级顺序规则）
    # 标题(1) → 框架(2) → 主要节点(3) → 连线(4) → 细节文字(5)
    for el in elements:
        etype = el["type"]
        if etype == "text" and str(el.get("id", "")).startswith("title-0"):
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 1, "duration": 400, "type": "fade-in"}}
        elif etype == "frame":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 2, "duration": 400, "type": "fade-in"}}
        elif etype in ("rectangle", "ellipse", "diamond"):
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 3, "duration": 500, "type": "slide-up"}}
        elif etype == "arrow":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 4, "duration": 300, "type": "draw"}}
        elif etype == "text":
            el["customData"] = {**(el.get("customData") or {}), "animate": {"order": 5, "duration": 400, "type": "fade-in"}}

    # Optional only: do not alter legacy IR output when no contract exists.
    _apply_visual_contract(elements, ir)

    return result


# ─── 示例 IR ───────────────────────────────────────────────────────────────
EXAMPLES = {
    "thermal-runaway": {
        "version": 1,
        "title": "电芯热失控手绘分析板  ·  THERMAL RUNAWAY MAP",
        "template": "relationship",
        "theme": "sketch",
        "nodes": [
            {"id": "tr01", "label": "内部短路\nINTERNAL SHORT", "type": "note", "style": "#ffe3e3", "font": "hand", "strokeColor": "#e03131", "strokeWidth": 2, "position": {"x": 100, "y": 250}},
            {"id": "tr02", "label": "过充电\nOVERCHARGE", "type": "note", "style": "#ffe3e3", "font": "hand", "strokeColor": "#e03131", "strokeWidth": 2, "position": {"x": 100, "y": 430}},
            {"id": "tr03", "label": "外部加热\nEXTERNAL HEAT", "type": "note", "style": "#ffe3e3", "font": "hand", "strokeColor": "#e03131", "strokeWidth": 2, "position": {"x": 100, "y": 610}},
            {"id": "tr04", "label": "SEI 膜分解\nSEI DECOMPOSITION", "type": "callout", "style": "#fff3bf", "font": "mono", "fontSize": 17, "strokeColor": "#f08c00", "strokeStyle": "dashed", "strokeWidth": 2, "position": {"x": 540, "y": 240}},
            {"id": "tr05", "label": "电芯热失控\nTHERMAL RUNAWAY", "type": "topic", "style": "#ffc9c9", "font": "hand", "fontSize": 25, "strokeColor": "#c92a2a", "strokeWidth": 4, "position": {"x": 520, "y": 420}},
            {"id": "tr06", "label": "放热链式反应\nEXOTHERMIC CHAIN", "type": "callout", "style": "#ffe8cc", "font": "mono", "fontSize": 17, "strokeColor": "#e8590c", "strokeStyle": "dashed", "strokeWidth": 2, "position": {"x": 540, "y": 620}},
            {"id": "tr07", "label": "多源早期预警\nEARLY WARNING", "type": "note", "style": "#d3f9d8", "font": "hand", "strokeColor": "#2b8a3e", "strokeWidth": 2, "position": {"x": 1020, "y": 250}},
            {"id": "tr08", "label": "热阻隔与定向排气\nTHERMAL BARRIER", "type": "note", "style": "#dbe4ff", "font": "hand", "strokeColor": "#1971c2", "strokeWidth": 2, "position": {"x": 1020, "y": 430}},
            {"id": "tr09", "label": "液冷快速抑制\nLIQUID COOLING", "type": "note", "style": "#d3f9d8", "font": "hand", "strokeColor": "#2b8a3e", "strokeWidth": 2, "position": {"x": 1020, "y": 610}},
        ],
        "edges": [
            {"id": "tre01", "from": "tr01", "to": "tr05", "curve": True, "curveOffset": 34, "color": "#e03131", "strokeWidth": 2},
            {"id": "tre02", "from": "tr02", "to": "tr05", "curve": True, "curveOffset": 26, "color": "#e03131", "strokeWidth": 3, "label": "trigger"},
            {"id": "tre03", "from": "tr03", "to": "tr05", "curve": True, "curveOffset": 34, "color": "#e03131", "strokeWidth": 2},
            {"id": "tre04", "from": "tr04", "to": "tr05", "style": "dashed", "color": "#f08c00", "strokeWidth": 2, "label": ""},
            {"id": "tre05", "from": "tr05", "to": "tr06", "style": "dashed", "color": "#e8590c", "strokeWidth": 2, "label": "propagation"},
            {"id": "tre06", "from": "tr05", "to": "tr07", "curve": True, "curveOffset": 34, "color": "#2b8a3e", "strokeWidth": 2, "label": "detect"},
            {"id": "tre07", "from": "tr05", "to": "tr08", "curve": True, "curveOffset": 24, "color": "#1971c2", "strokeWidth": 3, "label": "isolate"},
            {"id": "tre08", "from": "tr05", "to": "tr09", "curve": True, "curveOffset": 34, "color": "#2b8a3e", "strokeWidth": 2, "label": "suppress"},
        ],
        "groups": [
            {"id": "tr-trigger", "name": "TRIGGERS  ·  触发源", "nodes": ["tr01", "tr02", "tr03"], "level": 0, "backgroundColor": "#fff5f5"},
            {"id": "tr-mechanism", "name": "MECHANISM  ·  失控机理", "nodes": ["tr04", "tr05", "tr06"], "level": 1, "backgroundColor": "#fff9db"},
            {"id": "tr-mitigation", "name": "MITIGATION  ·  防护策略", "nodes": ["tr07", "tr08", "tr09"], "level": 2, "backgroundColor": "#ebfbee"},
        ],
        "metadata": {"scene": "thermal-runaway-concept-board", "complexity": "medium"},
    },
    "battery-thermal": {
        "version": 1,
        "title": "电池包热管理多物理场仿真架构",
        "template": "architecture",
        "theme": "minimal",
        "nodes": [
            {"id": "bt01", "label": "整车驾驶工况", "type": "input", "style": "#dbeafe", "position": {"x": 100, "y": 180}},
            {"id": "bt02", "label": "电芯发热功率", "type": "input", "style": "#dbeafe", "position": {"x": 100, "y": 330}},
            {"id": "bt03", "label": "冷却液与环境边界", "type": "input", "style": "#dbeafe", "position": {"x": 100, "y": 480}},
            {"id": "bt04", "label": "电化学-热耦合模型", "type": "process", "style": "#ede9fe", "position": {"x": 440, "y": 180}},
            {"id": "bt05", "label": "电池包传热模型", "type": "process", "style": "#ede9fe", "position": {"x": 440, "y": 330}},
            {"id": "bt06", "label": "冷却流道 CFD", "type": "process", "style": "#ede9fe", "position": {"x": 440, "y": 480}},
            {"id": "bt07", "label": "台架温度与流量数据", "type": "input", "style": "#ffedd5", "position": {"x": 800, "y": 180}},
            {"id": "bt08", "label": "模型可信度判定", "type": "decision", "style": "#fef3c7", "position": {"x": 800, "y": 330}},
            {"id": "bt09", "label": "参数标定与误差归因", "type": "process", "style": "#ffedd5", "position": {"x": 800, "y": 480}},
            {"id": "bt10", "label": "最高温度与温差", "type": "output", "style": "#dcfce7", "position": {"x": 1160, "y": 180}},
            {"id": "bt11", "label": "冷却策略与能耗", "type": "output", "style": "#dcfce7", "position": {"x": 1160, "y": 330}},
            {"id": "bt12", "label": "热安全设计包络", "type": "output", "style": "#dcfce7", "position": {"x": 1160, "y": 480}},
        ],
        "edges": [
            {"id": "bte01", "from": "bt01", "to": "bt04"},
            {"id": "bte02", "from": "bt02", "to": "bt05"},
            {"id": "bte03", "from": "bt03", "to": "bt06"},
            {"id": "bte04", "from": "bt04", "to": "bt05"},
            {"id": "bte05", "from": "bt06", "to": "bt05"},
            {"id": "bte06", "from": "bt05", "to": "bt08", "label": "仿真响应"},
            {"id": "bte07", "from": "bt07", "to": "bt08", "label": "试验基准"},
            {"id": "bte08", "from": "bt08", "to": "bt09", "label": "偏差超限", "style": "dashed"},
            {"id": "bte09", "from": "bt08", "to": "bt10"},
            {"id": "bte10", "from": "bt08", "to": "bt11"},
            {"id": "bte11", "from": "bt08", "to": "bt12"},
        ],
        "groups": [
            {"id": "bt-input", "name": "01  工况与边界", "nodes": ["bt01", "bt02", "bt03"], "level": 0, "backgroundColor": "#e7f5ff"},
            {"id": "bt-model", "name": "02  多物理场模型", "nodes": ["bt04", "bt05", "bt06"], "level": 1, "backgroundColor": "#f3f0ff"},
            {"id": "bt-validation", "name": "03  试验校核", "nodes": ["bt07", "bt08", "bt09"], "level": 2, "backgroundColor": "#fff4e6"},
            {"id": "bt-decision", "name": "04  设计决策", "nodes": ["bt10", "bt11", "bt12"], "level": 3, "backgroundColor": "#ebfbee"},
        ],
        "metadata": {"scene": "battery-thermal-management", "complexity": "medium"},
    },
    "fea": {
        "version": 1,
        "title": "有限元结构仿真工作流",
        "template": "swimlane",
        "theme": "blueprint",
        "nodes": [
            {"id": "fea01", "label": "需求与工况定义", "type": "start"},
            {"id": "fea02", "label": "CAD 几何清理", "type": "process", "style": "#dbeafe"},
            {"id": "fea03", "label": "材料本构参数", "type": "process", "style": "#dbeafe"},
            {"id": "fea04", "label": "单元类型选择", "type": "process", "style": "#dbeafe"},
            {"id": "fea05", "label": "网格划分", "type": "process", "style": "#dbeafe"},
            {"id": "fea06", "label": "边界条件与载荷", "type": "process", "style": "#dbeafe"},
            {"id": "fea07", "label": "接触/连接定义", "type": "process", "style": "#dbeafe"},
            {"id": "fea08", "label": "求解器与增量步", "type": "process", "style": "#ede9fe"},
            {"id": "fea09", "label": "提交计算", "type": "process", "style": "#ede9fe"},
            {"id": "fea10", "label": "收敛判断", "type": "decision", "style": "#fef3c7"},
            {"id": "fea11", "label": "场变量与响应提取", "type": "process", "style": "#dcfce7"},
            {"id": "fea12", "label": "网格无关性判断", "type": "decision", "style": "#fef3c7"},
            {"id": "fea13", "label": "试验或解析验证", "type": "decision", "style": "#fef3c7"},
            {"id": "fea14", "label": "模型、结果与报告归档", "type": "end"},
        ],
        "edges": [
            {"id":"feae01","from":"fea01","to":"fea02"},{"id":"feae02","from":"fea02","to":"fea03"},{"id":"feae03","from":"fea03","to":"fea04"},{"id":"feae04","from":"fea04","to":"fea05"},{"id":"feae05","from":"fea05","to":"fea06"},{"id":"feae06","from":"fea06","to":"fea07"},{"id":"feae07","from":"fea07","to":"fea08"},{"id":"feae08","from":"fea08","to":"fea09"},{"id":"feae09","from":"fea09","to":"fea10"},{"id":"feae10","from":"fea10","to":"fea11","label":"是"},{"id":"feae11","from":"fea10","to":"fea08","label":"否/调整"},{"id":"feae12","from":"fea11","to":"fea12"},{"id":"feae13","from":"fea12","to":"fea13","label":"是"},{"id":"feae14","from":"fea12","to":"fea05","label":"否/细化网格"},{"id":"feae15","from":"fea13","to":"fea14","label":"是"},{"id":"feae16","from":"fea13","to":"fea03","label":"否/修正模型假设"}
        ],
        "groups": [
            {"id": "fea-pre", "name": "1  前处理", "nodes": ["fea01", "fea02", "fea03", "fea04", "fea05", "fea06", "fea07"], "level": 0},
            {"id": "fea-solve", "name": "2  求解与收敛", "nodes": ["fea08", "fea09", "fea10"], "level": 1},
            {"id": "fea-post", "name": "3  后处理与网格验证", "nodes": ["fea11", "fea12"], "level": 2},
            {"id": "fea-verify", "name": "4  可信度验证与归档", "nodes": ["fea13", "fea14"], "level": 3},
        ],
        "metadata": {"scene": "finite-element-analysis", "complexity": "complex"},
    },
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
    ap.add_argument("--example", help="使用内置示例：thermal-runaway/battery-thermal/fea/flowchart/architecture/mindmap")
    ap.add_argument("--template-list", action="store_true", help="列出支持的模板")
    ap.add_argument("--theme", help="覆盖主题：default/sketch/blueprint/minimal")
    ap.add_argument("--layout", help="布局引擎：dot/neato/twopi（Graphviz，需 brew install graphviz）")
    ap.add_argument("--icons", action="store_true", help="注入云架构技术图标（自包含 SVG，icon_library.py）")
    ap.add_argument("--library", action="store_true", help="使用 Excalidraw Libraries 组件替换简单形状（library_loader.py）")
    ap.add_argument("--library-dir", help="显式使用自定义 .excalidrawlib 目录（同时启用 --library）")
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

    use_library = args.library or bool(args.library_dir)
    result = convert(
        ir,
        layout_engine=args.layout,
        icons=args.icons,
        library=use_library,
        library_dir=args.library_dir,
    )

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
    print(f"  主题: {ir.get('theme', 'default')}  布局: {args.layout or '内置'}  图标: {'是' if args.icons else '否'}  库组件: {'是' if use_library else '否'}")

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
