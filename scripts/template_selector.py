#!/usr/bin/env python3
"""
模板选择器 — 根据用户意图自动推荐最佳模板，支持模板预览和参数调整。

用法：
  python3 scripts/template_selector.py                     # 列出所有模板
  python3 scripts/template_selector.py --list               # 列出所有模板（JSON 格式）
  python3 scripts/template_selector.py --recommend "画一个微服务架构图"  # 根据意图推荐
  python3 scripts/template_selector.py --info flowchart     # 查看模板详情
  python3 scripts/template_selector.py --params flowchart --theme blueprint  # 带参数选择
"""

import json
import sys
import os
import re

# 模板注册表
TEMPLATES = {
    "flowchart": {
        "name": "流程图 Flowchart",
        "aliases": ["流程", "步骤", "顺序", "流程"],
        "scenes": ["business-process", "workflow", "step-by-step"],
        "complexity": "all",
        "description": "纵向或横向：矩形步骤 + 菱形决策 + 箭头",
        "core_structure": "开始 → 处理 → 决策 → 重试/完成",
        "layout": "vertical",
        "spacing": {"vertical": 80, "horizontal": 120},
        "colors": {"primary": "blue", "decision": "yellow", "end": "green"},
        "elements": ["ellipse", "rectangle", "diamond", "arrow", "text"],
        "max_nodes": 50,
        "example_file": "output/fixture-flowchart.excalidraw"
    },
    "architecture": {
        "name": "架构图 Architecture",
        "aliases": ["架构", "系统", "组件", "部署"],
        "scenes": ["tech-arch", "system-design", "deployment", "infrastructure"],
        "complexity": "medium",
        "description": "分层：用户层 → 应用层 → 服务层 → 数据层，层间大箭头",
        "core_structure": "分层架构 + 每层组件 + 层间调用",
        "layout": "layered",
        "spacing": {"vertical": 120, "horizontal": 100},
        "colors": {"user": "blue", "app": "purple", "data": "green"},
        "elements": ["frame", "rectangle", "ellipse", "arrow", "text"],
        "max_nodes": 40,
        "example_file": None
    },
    "sequence": {
        "name": "时序图 Sequence",
        "aliases": ["时序", "消息", "序列", "顺序图"],
        "scenes": ["communication", "api-call", "interaction", "protocol"],
        "complexity": "all",
        "description": "三条竖线（角色）+ 横向箭头消息，编号 1/2/3",
        "core_structure": "角色1 → 角色2 → 角色3，消息编号",
        "layout": "horizontal",
        "spacing": {"vertical": 60, "horizontal": 200},
        "colors": {"actor1": "blue", "actor2": "purple", "actor3": "green"},
        "elements": ["rectangle", "line", "arrow", "text"],
        "max_nodes": 30,
        "example_file": None
    },
    "mindmap": {
        "name": "思维导图 Mind Map",
        "aliases": ["思维导图", "脑图", "脑暴", "头脑风暴", "知识"],
        "scenes": ["brainstorm", "knowledge", "idea", "outline"],
        "complexity": "all",
        "description": "中心主题 + 一级/二级分支",
        "core_structure": "中心主题 → 一级分支 → 二级分支",
        "layout": "tree",
        "spacing": {"vertical": 60, "horizontal": 150},
        "colors": {"center": "blue", "level1": "purple", "level2": "gray"},
        "elements": ["ellipse", "rectangle", "line", "arrow", "text"],
        "max_nodes": 60,
        "example_file": None
    },
    "swimlane": {
        "name": "泳道图 Swimlane",
        "aliases": ["泳道", "跨部门", "分工"],
        "scenes": ["business-process", "role-responsibility", "cross-team"],
        "complexity": "medium",
        "description": "水平泳道按角色分区，流程穿越泳道",
        "core_structure": "角色A泳道 → 角色B泳道 → 角色C泳道，流程横穿",
        "layout": "swimlane",
        "spacing": {"vertical": 100, "horizontal": 120},
        "colors": {"lane1": "blue", "lane2": "purple", "lane3": "green"},
        "elements": ["frame", "rectangle", "arrow", "text"],
        "max_nodes": 40,
        "example_file": None
    },
    "erd": {
        "name": "ER 图 ERD",
        "aliases": ["ER", "实体关系", "数据模型"],
        "scenes": ["database-design", "data-model", "schema"],
        "complexity": "all",
        "description": "实体矩形 + 关系菱形/连线 + 基数标注",
        "core_structure": "实体 ↔ 关系 ↔ 实体，标注 1:N / M:N",
        "layout": "free",
        "spacing": {"vertical": 80, "horizontal": 150},
        "colors": {"entity": "blue", "relation": "yellow", "attr": "gray"},
        "elements": ["rectangle", "diamond", "line", "arrow", "text"],
        "max_nodes": 30,
        "example_file": None
    },
    "hierarchy": {
        "name": "层级图 Hierarchy",
        "aliases": ["层级", "组织", "树形", "结构"],
        "scenes": ["org-chart", "decomposition", "taxonomy", "breakdown"],
        "complexity": "all",
        "description": "自上而下树形结构，节点逐级展开",
        "core_structure": "根节点 → 子节点 → 叶节点（多级树）",
        "layout": "tree",
        "spacing": {"vertical": 80, "horizontal": 100},
        "colors": {"root": "blue", "level1": "purple", "level2": "green", "leaf": "gray"},
        "elements": ["rectangle", "line", "arrow", "text"],
        "max_nodes": 50,
        "example_file": None
    },
    "relationship": {
        "name": "关系图 Relationship",
        "aliases": ["关系", "依赖", "影响", "网络"],
        "scenes": ["dependency", "network", "influence", "mapping"],
        "complexity": "medium",
        "description": "节点 + 连线 + 关系标注，无严格方向",
        "core_structure": "节点A ↔ 节点B ↔ 节点C，标注关系类型",
        "layout": "free",
        "spacing": {"vertical": 80, "horizontal": 120},
        "colors": {"primary": "blue", "secondary": "purple", "line": "gray"},
        "elements": ["ellipse", "rectangle", "line", "arrow", "text"],
        "max_nodes": 25,
        "example_file": None
    },
    "comparison": {
        "name": "对比图 Comparison",
        "aliases": ["对比", "比较", "对照", "方案对比"],
        "scenes": ["comparison", "evaluation", "decision", "pros-cons"],
        "complexity": "simple",
        "description": "左右两栏或表格，标明比较维度",
        "core_structure": "维度1 | 方案A | 方案B",
        "layout": "table",
        "spacing": {"vertical": 35, "horizontal": 200},
        "colors": {"header": "blue", "colA": "purple", "colB": "green"},
        "elements": ["rectangle", "line", "text"],
        "max_nodes": 30,
        "example_file": None
    },
    "timeline": {
        "name": "时间线图 Timeline",
        "aliases": ["时间线", "时间轴", "历史", "里程碑", "进度"],
        "scenes": ["project-timeline", "history", "evolution", "roadmap"],
        "complexity": "all",
        "description": "水平时间轴 + 关键节点 + 事件标注",
        "core_structure": "时间轴 → 节点1 → 节点2 → 节点3 → 节点4",
        "layout": "horizontal",
        "spacing": {"vertical": 60, "horizontal": 120},
        "colors": {"axis": "dark", "node1": "blue", "node2": "purple", "node3": "green", "node4": "orange"},
        "elements": ["line", "ellipse", "text"],
        "max_nodes": 20,
        "example_file": None
    }
}

# 主题定义
THEMES = {
    "default": {
        "name": "默认",
        "description": "深灰描边 #1e1e1e，白色填充，标注连线",
        "strokeColor": "#1e1e1e",
        "backgroundColor": "#ffffff",
        "roughness": 1,
        "strokeWidth": 2
    },
    "sketch": {
        "name": "手绘",
        "description": "roughness=2，手绘感更强，更粗描边",
        "strokeColor": "#2b2b2b",
        "backgroundColor": "#ffffff",
        "roughness": 2,
        "strokeWidth": 3
    },
    "blueprint": {
        "name": "蓝图",
        "description": "蓝底白线（#1e3a5f 背景，#e8f4ff 描边）",
        "viewBackgroundColor": "#1e3a5f",
        "strokeColor": "#e8f4ff",
        "roughness": 0,
        "strokeWidth": 1
    },
    "minimal": {
        "name": "极简",
        "description": "纯黑白，roughness=0，strokeWidth=1",
        "strokeColor": "#000000",
        "backgroundColor": "#ffffff",
        "roughness": 0,
        "strokeWidth": 1
    }
}

# 场景 → 模板映射
SCENE_MAP = {
    "business-process": ["flowchart", "swimlane"],
    "workflow": ["flowchart", "swimlane"],
    "step-by-step": ["flowchart", "timeline"],
    "tech-arch": ["architecture", "relationship"],
    "system-design": ["architecture", "hierarchy"],
    "deployment": ["architecture", "flowchart"],
    "infrastructure": ["architecture", "relationship"],
    "communication": ["sequence", "request-response"],
    "api-call": ["sequence", "request-response"],
    "interaction": ["sequence", "relationship"],
    "brainstorm": ["mindmap", "relationship"],
    "knowledge": ["mindmap", "hierarchy"],
    "idea": ["mindmap", "mindmap"],
    "outline": ["mindmap", "hierarchy"],
    "database-design": ["erd", "relationship"],
    "data-model": ["erd", "hierarchy"],
    "schema": ["erd", "relationship"],
    "org-chart": ["hierarchy", "relationship"],
    "decomposition": ["hierarchy", "mindmap"],
    "taxonomy": ["hierarchy", "mindmap"],
    "comparison": ["comparison", "table"],
    "evaluation": ["comparison", "table"],
    "decision": ["comparison", "flowchart"],
    "project-timeline": ["timeline", "flowchart"],
    "history": ["timeline", "relationship"],
    "evolution": ["timeline", "architecture"],
    "roadmap": ["timeline", "hierarchy"],
    "dependency": ["relationship", "architecture"],
    "network": ["relationship", "architecture"],
    "influence": ["relationship", "mindmap"],
    "mapping": ["relationship", "hierarchy"],
    "role-responsibility": ["swimlane", "flowchart"],
    "cross-team": ["swimlane", "flowchart"],
    "pros-cons": ["comparison", "table"],
}


def list_templates(format="text"):
    """列出所有可用模板"""
    if format == "json":
        data = {}
        for key, tmpl in TEMPLATES.items():
            data[key] = {
                "name": tmpl["name"],
                "description": tmpl["description"],
                "scenes": tmpl["scenes"],
                "complexity": tmpl["complexity"],
                "layout": tmpl["layout"],
                "elements": tmpl["elements"],
                "max_nodes": tmpl["max_nodes"]
            }
        data["_themes"] = {k: {"name": v["name"], "description": v["description"]} for k, v in THEMES.items()}
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        lines = []
        lines.append("=" * 70)
        lines.append("Excalidraw 模板列表")
        lines.append("=" * 70)
        for key, tmpl in TEMPLATES.items():
            lines.append(f"\n  [{key:15s}] {tmpl['name']}")
            lines.append(f"  {'':15s}  {tmpl['description']}")
            lines.append(f"  {'':15s}  布局: {tmpl['layout']:10s} 复杂度: {tmpl['complexity']:10s} 最大节点: {tmpl['max_nodes']}")
            lines.append(f"  {'':15s}  场景: {', '.join(tmpl['scenes'][:3])}")
        lines.append("\n" + "=" * 70)
        lines.append("可用主题:")
        for key, theme in THEMES.items():
            lines.append(f"  [{key:12s}] {theme['name']} - {theme['description']}")
        lines.append("=" * 70)
        return "\n".join(lines)


def get_template_info(template_name):
    """查看模板详情"""
    key = _resolve_template_key(template_name)
    if not key:
        return json.dumps({"error": f"未找到模板: {template_name}"}, ensure_ascii=False, indent=2)
    
    tmpl = TEMPLATES[key]
    result = {
        "key": key,
        "name": tmpl["name"],
        "description": tmpl["description"],
        "core_structure": tmpl["core_structure"],
        "layout": tmpl["layout"],
        "spacing": tmpl["spacing"],
        "colors": tmpl["colors"],
        "elements": tmpl["elements"],
        "max_nodes": tmpl["max_nodes"],
        "example_file": tmpl["example_file"],
        "scenes": tmpl["scenes"],
        "complexity": tmpl["complexity"],
        "aliases": tmpl["aliases"]
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def recommend(intent_text):
    """根据用户意图推荐最佳模板"""
    intent_lower = intent_text.lower()
    
    # 提取关键词
    all_keywords = []
    for key, tmpl in TEMPLATES.items():
        for alias in tmpl["aliases"]:
            if alias.lower() in intent_lower:
                all_keywords.append((key, alias))
    
    # 按关键词匹配数排序
    if all_keywords:
        # 统计每个模板的匹配次数
        match_counts = {}
        for key, alias in all_keywords:
            match_counts[key] = match_counts.get(key, 0) + 1
        sorted_matches = sorted(match_counts.items(), key=lambda x: -x[1])
        primary = sorted_matches[0][0]
        alternatives = [k for k, _ in sorted_matches[1:]]
    else:
        # 尝试场景匹配
        for scene, templates in SCENE_MAP.items():
            if scene in intent_lower:
                primary = templates[0]
                alternatives = templates[1:]
                break
        else:
            primary = "flowchart"
            alternatives = ["mindmap", "architecture"]
    
    # 构建结果
    result = {
        "primary": {
            "key": primary,
            "name": TEMPLATES[primary]["name"],
            "description": TEMPLATES[primary]["description"],
            "reason": f"匹配到 {match_counts.get(primary, 0)} 个关键词"
        },
        "alternatives": [
            {
                "key": alt,
                "name": TEMPLATES[alt]["name"],
                "description": TEMPLATES[alt]["description"]
            }
            for alt in alternatives[:3]
        ],
        "available_themes": list(THEMES.keys()),
        "parameters": {
            "theme": "default",
            "layout_direction": TEMPLATES[primary].get("layout", "vertical"),
            "spacing": TEMPLATES[primary].get("spacing", {"vertical": 80, "horizontal": 120})
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def _resolve_template_key(name):
    """解析模板名称到 key"""
    if name in TEMPLATES:
        return name
    for key, tmpl in TEMPLATES.items():
        if tmpl["name"].lower().startswith(name.lower()):
            return key
        for alias in tmpl["aliases"]:
            if name.lower() == alias.lower():
                return key
    return None


def main():
    if len(sys.argv) < 2:
        print(list_templates())
        return
    
    cmd = sys.argv[1]
    
    if cmd in ("--list", "-l"):
        format = "json" if "--json" in sys.argv else "text"
        print(list_templates(format))
    
    elif cmd in ("--recommend", "-r"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --recommend \"画一个微服务架构图\"")
            sys.exit(1)
        intent = " ".join(sys.argv[2:])
        print(recommend(intent))
    
    elif cmd in ("--info", "-i"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --info flowchart")
            print("可用模板:", ", ".join(TEMPLATES.keys()))
            sys.exit(1)
        print(get_template_info(sys.argv[2]))
    
    elif cmd in ("--params", "-p"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --params flowchart --theme blueprint")
            sys.exit(1)
        template_name = sys.argv[2]
        key = _resolve_template_key(template_name)
        if not key:
            print(f"未找到模板: {template_name}")
            sys.exit(1)
        theme = "default"
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            if idx + 1 < len(sys.argv):
                theme = sys.argv[idx + 1]
        result = {
            "template": key,
            "name": TEMPLATES[key]["name"],
            "theme": theme,
            "theme_info": THEMES.get(theme, THEMES["default"]),
            "layout": TEMPLATES[key]["layout"],
            "spacing": TEMPLATES[key]["spacing"]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")
        print("用法:")
        print("  template_selector.py                     # 列出所有模板")
        print("  template_selector.py --list [--json]     # 列出模板（JSON 格式）")
        print("  template_selector.py --recommend <文本>  # 根据意图推荐")
        print("  template_selector.py --info <模板名>     # 查看模板详情")
        print("  template_selector.py --params <模板名> [--theme <主题>]  # 带参数选择")
        sys.exit(1)


if __name__ == "__main__":
    main()
