#!/usr/bin/env python3
"""
知识图谱架构生成（C.8，借鉴 BV-Venky/excalidraw-architect-mcp，139★）

从结构化描述（JSON）或简单文本提取实体/关系，生成 IR 中间格式，再调用
ir_to_excalidraw.py 转为 Excalidraw 架构图。

用法：
  # 从 JSON 结构描述生成
  python3 scripts/knowledge_graph.py --json '{"entities":[{"id":"api","name":"API网关","type":"component"},...],"relations":[{"from":"api","to":"svc","label":"调用"}]}' --output out.excalidraw

  # 从简单文本生成（每行：实体名|类型|层；关系行：A -> B 标签）
  python3 scripts/knowledge_graph.py --text arch.txt --output out.excalidraw

文本格式示例（arch.txt）：
  entity: Web前端|component|用户层
  entity: 订单服务|service|应用层
  entity: PostgreSQL|database|数据层
  rel: Web前端 -> 订单服务 调用
  rel: 订单服务 -> PostgreSQL 读写

  # 列出示例
  python3 scripts/knowledge_graph.py --example
"""

import argparse
import json
import os
import subprocess
import sys
import time

TYPE_LAYER = {
    "用户层": 0, "前端": 0, "ui": 0,
    "应用层": 1, "服务层": 1, "中间层": 1, "app": 1,
    "数据层": 2, "存储层": 2, "基础设施": 2, "data": 2,
    "外部": 3, "第三方": 3, "external": 3,
}
DEFAULT_LAYER = 1

# 实体类型 → 节点类型映射（与 ir-format.md / NODE_TYPE_STYLE 对应）
ENTITY_TYPE_MAP = {
    "database": "database", "db": "database", "存储": "database",
    "queue": "service", "mq": "service", "消息": "service",
    "gateway": "component", "网关": "component",
    "service": "service", "服务": "service",
    "component": "component", "组件": "component",
    "client": "input", "前端": "input", "用户": "input",
    "cache": "component", "缓存": "component",
    "storage": "component", "对象存储": "component",
}


def parse_json_desc(data):
    """解析 JSON 结构描述为 (entities, relations, groups)。"""
    entities = data.get("entities", [])
    relations = data.get("relations", [])
    groups = data.get("groups", [])
    nodes = []
    for e in entities:
        ntype = ENTITY_TYPE_MAP.get(str(e.get("type", "")).lower(), "component")
        nodes.append({
            "id": e.get("id", f"n{len(nodes) + 1}"),
            "label": e.get("name", e.get("id", "?" )),
            "type": ntype,
            "style": e.get("style"),
        })
    edges = []
    for r in relations:
        edges.append({
            "id": f"e{len(edges) + 1}",
            "from": r.get("from"),
            "to": r.get("to"),
            "label": r.get("label"),
        })
    # 默认分层：按 groups 或推断
    if not groups:
        layer_map = {}
        for e in entities:
            layer = TYPE_LAYER.get(str(e.get("layer", "")).lower(), DEFAULT_LAYER)
            layer_map.setdefault(layer, []).append(e.get("id", f"n{entities.index(e) + 1}"))
        group_names = {0: "用户层", 1: "应用层", 2: "数据层", 3: "外部"}
        groups = [
            {"id": f"g{layer}", "name": group_names.get(layer, f"层{layer}"), "nodes": ids, "level": layer}
            for layer, ids in sorted(layer_map.items())
        ]
    return nodes, edges, groups


def parse_text_desc(text):
    """解析文本描述（entity:/rel: 行）。"""
    nodes = []
    edges = []
    groups = []
    id_map = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("entity:") or line.startswith("实体:"):
            parts = line.split(":", 1)[1].split("|")
            name = parts[0].strip()
            etype = parts[1].strip() if len(parts) > 1 else "component"
            layer = parts[2].strip() if len(parts) > 2 else ""
            eid = f"n{len(nodes) + 1}"
            id_map[name] = eid
            ntype = ENTITY_TYPE_MAP.get(etype.lower(), "component")
            nodes.append({"id": eid, "label": name, "type": ntype})
            layer_idx = TYPE_LAYER.get(layer.lower(), DEFAULT_LAYER)
            groups.append({"id": f"g{layer_idx}", "name": layer or "应用层", "nodes": [eid], "level": layer_idx})
        elif line.startswith("rel:") or line.startswith("关系:"):
            body = line.split(":", 1)[1]
            # A -> B 标签
            m = body.split("->")
            if len(m) == 2:
                from_name = m[0].strip()
                rest = m[1].strip()
                # split label (last token)
                parts = rest.split()
                to_name = parts[0] if parts else rest
                label = " ".join(parts[1:]) if len(parts) > 1 else None
                edges.append({
                    "id": f"e{len(edges) + 1}",
                    "from": id_map.get(from_name, from_name),
                    "to": id_map.get(to_name, to_name),
                    "label": label,
                })
    # 合并 groups：同一 level 的 nodes 合并
    merged = {}
    for g in groups:
        merged.setdefault(g["level"], {"id": g["id"], "name": g["name"], "nodes": [], "level": g["level"]})
        for nid in g["nodes"]:
            if nid not in merged[g["level"]]["nodes"]:
                merged[g["level"]]["nodes"].append(nid)
    groups = list(merged.values())
    return nodes, edges, groups


def build_ir(nodes, edges, groups, title):
    return {
        "version": 1,
        "title": title or "知识图谱架构",
        "template": "architecture",
        "theme": "default",
        "nodes": nodes,
        "edges": edges,
        "groups": groups,
        "metadata": {"scene": "tech-arch", "complexity": "medium", "source": "knowledge-graph"},
    }


def to_excalidraw(ir, out_path):
    script = os.path.join(os.path.dirname(__file__), "ir_to_excalidraw.py")
    tmp_ir = os.path.join("/tmp", f"kg-ir-{int(time.time())}.json")
    with open(tmp_ir, "w", encoding="utf-8") as f:
        json.dump(ir, f, ensure_ascii=False, indent=2)
    try:
        r = subprocess.run(
            [sys.executable, script, tmp_ir, "--output", out_path, "--validate"],
            capture_output=True, text=True,
        )
        print(r.stdout, end="")
        if r.returncode != 0:
            print(r.stderr, end="")
            sys.exit(r.returncode)
    finally:
        try:
            os.unlink(tmp_ir)
        except OSError:
            pass


EXAMPLE = """entity: Web前端|component|用户层
entity: API网关|gateway|用户层
entity: 订单服务|service|应用层
entity: 支付服务|service|应用层
entity: PostgreSQL|database|数据层
entity: Redis|cache|数据层
rel: Web前端 -> API网关 调用
rel: API网关 -> 订单服务 转发
rel: API网关 -> 支付服务 转发
rel: 订单服务 -> PostgreSQL 读写
rel: 支付服务 -> Redis 读写
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", dest="json_desc", help="JSON 结构描述")
    ap.add_argument("--text", help="文本描述文件路径")
    ap.add_argument("--output", "-o", help="输出 .excalidraw 文件")
    ap.add_argument("--title", help="图表标题")
    ap.add_argument("--example", action="store_true", help="打印示例文本格式")
    args = ap.parse_args()

    if args.example:
        print(EXAMPLE)
        return

    if not args.output:
        ap.print_help()
        sys.exit(2)

    if args.json_desc:
        data = json.loads(args.json_desc)
        nodes, edges, groups = parse_json_desc(data)
    elif args.text:
        with open(args.text, encoding="utf-8") as f:
            nodes, edges, groups = parse_text_desc(f.read())
    else:
        ap.print_help()
        sys.exit(2)

    if not nodes:
        print("[ERROR] 未解析到实体。JSON 需含 entities，或文本需以 entity:/rel: 行开头。")
        sys.exit(1)

    ir = build_ir(nodes, edges, groups, args.title)
    print(f"[OK] 知识图谱: {len(nodes)} 实体, {len(edges)} 关系, {len(groups)} 层")
    to_excalidraw(ir, args.output)


if __name__ == "__main__":
    main()
