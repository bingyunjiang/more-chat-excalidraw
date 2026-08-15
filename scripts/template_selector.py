#!/usr/bin/env python3
"""
模板选择器 — 根据用户意图自动推荐最佳模板，支持模板预览和参数调整。

用法：
  python3 scripts/template_selector.py                     # 列出所有模板
  python3 scripts/template_selector.py --list               # 按四类列出所有模板
  python3 scripts/template_selector.py --guide --json        # 机器可读选择目录
  python3 scripts/template_selector.py --recommend "画一个微服务架构图"  # 根据意图推荐
  python3 scripts/template_selector.py --choices "分析不收敛原因"        # 用户选择菜单
  python3 scripts/template_selector.py --info flowchart     # 查看模板详情
  python3 scripts/template_selector.py --params flowchart --theme sketch --sketch-style engineering-notebook
"""

import json
import sys
import os
import re

# 模板注册表
TEMPLATES = {
    "flowchart": {
        "name": "流程图 Flowchart",
        "aliases": ["流程", "步骤", "顺序", "有限元", "FEA", "finite element", "结构力学", "网格收敛", "网格无关性", "接触非线性", "材料本构", "热-结构耦合", "modal", "fatigue"],
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
        "aliases": ["架构", "系统", "组件", "部署", "电池热管理", "多物理场", "热流固耦合", "联合仿真", "数字孪生", "仿真架构"],
        "scenes": ["tech-arch", "system-design", "deployment", "infrastructure", "battery-thermal-management", "multiphysics-simulation"],
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
        "aliases": ["泳道", "跨部门", "分工", "有限元流程", "仿真流程"],
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
        "aliases": ["关系", "依赖", "影响", "网络", "热失控", "机理", "因果", "触发源", "防护策略", "手绘分析板", "concept map"],
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

SKETCH_STYLES = {
    "engineering-notebook": {"label": "工程笔记", "aliases": ["工程笔记"], "formality": "balanced", "vibe": "field notes", "use": "工程流程与记录"},
    "research-board": {"label": "研究分析板", "aliases": ["研究分析", "研究板"], "formality": "balanced", "vibe": "quiet analytical", "use": "研究分析与证据链"},
    "root-cause": {"label": "根因诊断", "aliases": ["根因风格", "诊断风格"], "formality": "restrained", "vibe": "diagnostic", "use": "根因、故障与收敛诊断"},
    "mechanism-map": {"label": "机理图谱", "aliases": ["机理风格", "因果风格"], "formality": "balanced", "vibe": "causal", "use": "机理、因果与关系分析"},
    "review-markup": {"label": "评审批注", "aliases": ["评审风格", "批注风格"], "formality": "striking", "vibe": "annotated critique", "use": "架构评审与风险批注"},
}

# Delivery mode is orthogonal to the content template. A recording request can
# legitimately use several templates across frames, so it must not be forced
# into a single relationship/flowchart choice.
DELIVERY_PROFILES = {
    "single-diagram": {
        "label": "单张图",
        "signals": [],
        "frame_count": 1,
        "aspect_ratio": None,
        "description": "一张画布完成表达",
    },
    "long-canvas": {
        "label": "长画布",
        "signals": [r"长画布", r"横向移动", r"一张大图"],
        "frame_count": "variable",
        "aspect_ratio": None,
        "description": "在同一张画布上横向或纵向推进",
    },
    "video-storyboard": {
        "label": "视频分镜",
        "signals": [r"录屏", r"视频", r"分镜", r"逐帧", r"镜头", r"提词器", r"16[:：]9", r"讲解"],
        "frame_count": "3-6",
        "aspect_ratio": "16:9",
        "description": "按镜头拆成多个 16:9 frame，可逐帧导出",
    },
    "presentation-board": {
        "label": "演示白板",
        "signals": [r"演示", r"汇报", r"路演", r"presentation", r"PPT"],
        "frame_count": "variable",
        "aspect_ratio": "16:9",
        "description": "适合讲解、汇报和投屏阅读",
    },
}

# 面向用户的模板选择信息。TEMPLATES 保持生成层兼容；此处只负责把
# “10 个技术 key”整理成用户容易比较的四组选择卡。
TEMPLATE_CATEGORIES = {
    "process": {
        "name": "流程与协作",
        "question": "要突出连续步骤，还是角色之间的交接？",
        "templates": ["flowchart", "swimlane"],
    },
    "system": {
        "name": "系统与结构",
        "question": "要展示组件调用、数据实体，还是上下级结构？",
        "templates": ["architecture", "erd", "hierarchy"],
    },
    "interaction": {
        "name": "交互与时间",
        "question": "要展示消息先后，还是事件沿时间推进？",
        "templates": ["sequence", "timeline"],
    },
    "analysis": {
        "name": "分析与思考",
        "question": "要解释因果关系、发散知识，还是比较方案？",
        "templates": ["relationship", "mindmap", "comparison"],
    },
}

TEMPLATE_GUIDE = {
    "flowchart": {
        "label": "步骤流程",
        "category": "process",
        "best_for": "有明确先后、判断和返工的操作流程",
        "avoid_when": "重点是多角色交接或复杂因果网络",
        "styles": ["engineering-notebook", "research-board"],
    },
    "swimlane": {
        "label": "角色泳道",
        "category": "process",
        "best_for": "跨部门、跨角色或分阶段的职责交接",
        "avoid_when": "只有单一路径且不关心责任主体",
        "styles": ["engineering-notebook", "review-markup"],
    },
    "architecture": {
        "label": "系统架构",
        "category": "system",
        "best_for": "组件、分层、依赖、部署和数据流",
        "avoid_when": "重点是单次调用的严格时间顺序",
        "styles": ["review-markup", "research-board"],
    },
    "erd": {
        "label": "数据实体",
        "category": "system",
        "best_for": "数据库实体、字段关系和基数",
        "avoid_when": "重点是服务调用或业务步骤",
        "styles": ["research-board", "engineering-notebook"],
    },
    "hierarchy": {
        "label": "层级拆解",
        "category": "system",
        "best_for": "组织、分类、系统分解和树形结构",
        "avoid_when": "节点之间是多对多影响而非上下级",
        "styles": ["research-board", "engineering-notebook"],
    },
    "sequence": {
        "label": "消息时序",
        "category": "interaction",
        "best_for": "角色之间按时间发生的请求、响应和消息",
        "avoid_when": "只关心静态组件关系，不关心先后顺序",
        "styles": ["engineering-notebook", "research-board"],
    },
    "timeline": {
        "label": "事件时间线",
        "category": "interaction",
        "best_for": "里程碑、历史演进、路线图和项目进度",
        "avoid_when": "事件没有清晰时间轴",
        "styles": ["research-board", "engineering-notebook"],
    },
    "relationship": {
        "label": "关系分析板",
        "category": "analysis",
        "best_for": "因果、机理、根因、影响链和依赖网络",
        "avoid_when": "必须严格按步骤执行或按角色分工",
        "styles": ["mechanism-map", "root-cause", "research-board"],
    },
    "mindmap": {
        "label": "主题脑图",
        "category": "analysis",
        "best_for": "头脑风暴、知识梳理和主题发散",
        "avoid_when": "需要严格表达方向、职责或时间",
        "styles": ["research-board", "mechanism-map"],
    },
    "comparison": {
        "label": "方案对比",
        "category": "analysis",
        "best_for": "方案、观点、指标和优缺点对照",
        "avoid_when": "内容主要是连续步骤或依赖网络",
        "styles": ["research-board", "review-markup"],
    },
}

INTENT_SIGNALS = {
    "flowchart": [r"步骤", r"操作流程", r"审批流程", r"处理流程", r"算法流程", r"怎么做"],
    "swimlane": [r"跨部门", r"跨团队", r"角色分工", r"职责", r"交接", r"仿真流程"],
    "architecture": [r"系统架构", r"技术架构", r"组件", r"模块", r"部署", r"服务依赖", r"数据流"],
    "erd": [r"\bERD?\b", r"实体关系", r"数据模型", r"表结构", r"数据库设计"],
    "hierarchy": [r"层级", r"组织架构", r"分类体系", r"系统分解", r"树形"],
    "sequence": [r"时序", r"调用顺序", r"消息交互", r"请求响应", r"协议交互"],
    "timeline": [r"时间线", r"时间轴", r"里程碑", r"演进", r"路线图", r"roadmap"],
    "relationship": [r"根因", r"机理", r"因果", r"不收敛", r"故障", r"失效", r"诊断", r"影响链", r"热失控"],
    "mindmap": [r"思维导图", r"脑图", r"头脑风暴", r"知识梳理", r"主题发散"],
    "comparison": [r"对比", r"比较", r"对照", r"优缺点", r"方案选择", r"选型"],
}

EXPLICIT_TEMPLATE_TERMS = {
    "flowchart": ["flowchart", "流程图"],
    "swimlane": ["swimlane", "泳道图"],
    "architecture": ["architecture", "架构图"],
    "erd": ["erd", "er 图", "er图"],
    "hierarchy": ["hierarchy", "层级图"],
    "sequence": ["sequence", "时序图", "顺序图"],
    "timeline": ["timeline", "时间线图", "时间轴图"],
    "relationship": ["relationship", "关系图", "关系分析板"],
    "mindmap": ["mindmap", "mind map", "思维导图"],
    "comparison": ["comparison", "对比图"],
}

# 场景 → 模板映射
SCENE_MAP = {
    "finite-element-analysis": ["flowchart", "swimlane"],
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


def _category_for(template_key):
    guide = TEMPLATE_GUIDE[template_key]
    category_key = guide["category"]
    return category_key, TEMPLATE_CATEGORIES[category_key]


def _style_for_template(template_key, intent_lower):
    if template_key == "relationship":
        if any(term in intent_lower for term in ("根因", "不收敛", "故障", "失效", "诊断")):
            return "root-cause"
        return "mechanism-map"
    if template_key == "architecture" and any(term in intent_lower for term in ("评审", "风险", "整改", "审计")):
        return "review-markup"
    if template_key in ("flowchart", "swimlane", "sequence"):
        return "engineering-notebook"
    return TEMPLATE_GUIDE[template_key]["styles"][0]


def _score_templates(intent_lower):
    scores = {key: 0 for key in TEMPLATES}
    matched = {key: [] for key in TEMPLATES}
    for key, tmpl in TEMPLATES.items():
        for alias in tmpl["aliases"]:
            alias_lower = alias.lower()
            if _alias_matches(alias_lower, intent_lower):
                # Longer phrases carry more intent than generic one-character terms.
                weight = 3 if len(alias_lower) >= 4 else 2 if len(alias_lower) >= 2 else 1
                scores[key] += weight
                matched[key].append(alias)
        for pattern in INTENT_SIGNALS.get(key, []):
            if re.search(pattern, intent_lower, re.IGNORECASE):
                scores[key] += 5
                matched[key].append(pattern)
    return scores, matched


def _alias_matches(alias_lower, intent_lower):
    """Match Chinese phrases by substring and Latin aliases by token boundary.

    A raw substring match makes the alias ``ER`` match the ``er`` in
    ``paper-workflow``. Latin abbreviations must be bounded by non-word
    characters, while Chinese phrases still need normal substring matching.
    """
    if not alias_lower:
        return False
    if re.search(r"[a-z0-9]", alias_lower):
        escaped = re.escape(alias_lower)
        return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", intent_lower, re.IGNORECASE) is not None
    return alias_lower in intent_lower


def _delivery_profile(intent_lower):
    for key, profile in DELIVERY_PROFILES.items():
        if any(re.search(pattern, intent_lower, re.IGNORECASE) for pattern in profile["signals"]):
            return key
    return "single-diagram"


def _fallback_alternatives(primary, ranked_keys):
    result = [key for key in ranked_keys if key != primary]
    category_key, category = _category_for(primary)
    for key in category["templates"]:
        if key != primary and key not in result:
            result.append(key)
    adjacent = {
        "flowchart": ["swimlane", "relationship"],
        "swimlane": ["flowchart", "architecture"],
        "architecture": ["relationship", "sequence"],
        "erd": ["architecture", "hierarchy"],
        "hierarchy": ["mindmap", "architecture"],
        "sequence": ["architecture", "flowchart"],
        "timeline": ["flowchart", "relationship"],
        "relationship": ["flowchart", "mindmap"],
        "mindmap": ["relationship", "hierarchy"],
        "comparison": ["flowchart", "relationship"],
    }
    for key in adjacent[primary]:
        if key not in result:
            result.append(key)
    return result[:2]


def _choice_card(template_key, intent_lower, reason, recommended=False, style_override=None):
    guide = TEMPLATE_GUIDE[template_key]
    category_key, category = _category_for(template_key)
    style = style_override or _style_for_template(template_key, intent_lower)
    return {
        "id": template_key,
        "label": guide["label"],
        "template": template_key,
        "category": {"key": category_key, "name": category["name"]},
        "sketchStyle": style,
        "style_label": SKETCH_STYLES[style]["label"],
        "why": reason,
        "best_for": guide["best_for"],
        "avoid_when": guide["avoid_when"],
        "structure": TEMPLATES[template_key]["core_structure"],
        "recommended": recommended,
    }


def _find_explicit_template(intent_lower):
    for key, terms in EXPLICIT_TEMPLATE_TERMS.items():
        if any(term in intent_lower for term in terms):
            return key
    return None


def _find_explicit_style(intent_lower):
    for key, style in SKETCH_STYLES.items():
        terms = [key, key.replace("-", " "), style["label"], *style.get("aliases", [])]
        if any(term.lower() in intent_lower for term in terms):
            return key
    return None


def _strip_style_terms(intent_lower, style_key):
    if not style_key:
        return intent_lower
    style = SKETCH_STYLES[style_key]
    style_terms = [style_key, style_key.replace("-", " "), style["label"], *style.get("aliases", [])]
    scoring_text = intent_lower
    for term in style_terms:
        scoring_text = scoring_text.replace(term.lower(), " ")
    return scoring_text


def _intent_profile(intent_text):
    intent_lower = intent_text.lower()
    explicit_style_key = _find_explicit_style(intent_lower)
    return {
        "text": intent_text,
        "lower": intent_lower,
        "explicit_template": _find_explicit_template(intent_lower),
        "explicit_style": explicit_style_key,
        "delivery_profile": _delivery_profile(intent_lower),
        "direct_select": any(k in intent_lower for k in ("你直接选", "直接选", "不用问", "随便")),
        "scoring_text": _strip_style_terms(intent_lower, explicit_style_key),
    }


def _rank_templates(scores):
    template_order = list(TEMPLATES)
    return sorted(TEMPLATES, key=lambda key: (-scores[key], template_order.index(key)))


def _select_primary_template(profile, scores, ranked):
    if profile["explicit_template"]:
        return profile["explicit_template"], ranked
    if scores[ranked[0]] > 0:
        return ranked[0], ranked
    fallback_ranked = ["relationship", "flowchart", "architecture"] + [
        key for key in ranked if key not in ("relationship", "flowchart", "architecture")
    ]
    return "relationship", fallback_ranked


def _ranked_alternatives(primary, scores, ranked):
    positive_ranked = [key for key in ranked if scores[key] > 0]
    return _fallback_alternatives(primary, positive_ranked if positive_ranked else ranked)


def _confidence_for(primary, alternatives, scores):
    primary_score = scores.get(primary, 0)
    next_score = max((scores.get(key, 0) for key in alternatives), default=0)
    if primary_score >= 8 and primary_score - next_score >= 3:
        return "high"
    if primary_score > 0:
        return "medium"
    return "low"


def _recommendation_reason(primary, matched, explicit_template_key):
    matched_terms = [term for term in matched.get(primary, []) if not term.startswith("\\b")]
    if explicit_template_key:
        return f"用户已明确选择{TEMPLATE_GUIDE[primary]['label']}"
    if matched_terms:
        return f"识别到“{'、'.join(matched_terms[:3])}”，更适合{TEMPLATE_GUIDE[primary]['label']}"
    return f"信息不足，先用最能承载自由关系的{TEMPLATE_GUIDE[primary]['label']}"


def _style_options(primary, intent_lower, preferred_style):
    style_keys = [preferred_style] + [key for key in TEMPLATE_GUIDE[primary]["styles"] if key != preferred_style]
    return [
        _choice_card(
            primary,
            intent_lower,
            SKETCH_STYLES[style_key]["use"],
            recommended=index == 0,
            style_override=style_key,
        )
        for index, style_key in enumerate(style_keys[:3])
    ]


def _template_options(primary, alternatives, intent_lower, reason, style, lock_style=False):
    cards = [
        _choice_card(primary, intent_lower, reason, recommended=True, style_override=style),
        *[
            _choice_card(
                key,
                intent_lower,
                f"如果更关注{TEMPLATE_GUIDE[key]['best_for']}，可选此项",
                style_override=style if lock_style else None,
            )
            for key in alternatives
        ],
    ]
    return cards[:3]


def _build_interaction(profile, primary, alternatives, style, reason):
    intent_lower = profile["lower"]
    explicit_template_key = profile["explicit_template"]
    explicit_style_key = profile["explicit_style"]

    if profile["direct_select"]:
        cards = [_choice_card(primary, intent_lower, reason, recommended=True, style_override=style)]
        return {
            "mode": "auto",
            "requires_confirmation": False,
            "cards": cards,
            "prompt": f"将采用“{cards[0]['label']} + {cards[0]['style_label']}”，{reason}。",
        }
    if explicit_template_key and explicit_style_key:
        cards = [_choice_card(primary, intent_lower, reason, recommended=True, style_override=style)]
        return {
            "mode": "ready",
            "requires_confirmation": False,
            "cards": cards,
            "prompt": f"模板与风格已确定：{cards[0]['label']} + {cards[0]['style_label']}。",
        }
    if explicit_template_key:
        cards = _style_options(primary, intent_lower, style)
        return {
            "mode": "select_style",
            "requires_confirmation": True,
            "cards": cards,
            "prompt": f"模板已确定为“{TEMPLATE_GUIDE[primary]['label']}”。我推荐“{cards[0]['style_label']}”，请选择手绘气质。",
        }

    mode = "select_template" if explicit_style_key else "select_both"
    cards = _template_options(primary, alternatives, intent_lower, reason, style, lock_style=bool(explicit_style_key))
    if explicit_style_key:
        prompt = f"风格已确定为“{SKETCH_STYLES[style]['label']}”。我推荐“{cards[0]['label']}”，请选择叙事模板。"
    else:
        prompt = f"我推荐“{cards[0]['label']} + {cards[0]['style_label']}”，{reason}。请选择下面一种，或让我直接按推荐生成。"
    return {"mode": mode, "requires_confirmation": True, "cards": cards, "prompt": prompt}


def catalog_payload():
    categories = []
    for category_key, category in TEMPLATE_CATEGORIES.items():
        categories.append({
            "key": category_key,
            "name": category["name"],
            "question": category["question"],
            "templates": [
                {
                    "key": key,
                    "label": TEMPLATE_GUIDE[key]["label"],
                    "name": TEMPLATES[key]["name"],
                    "best_for": TEMPLATE_GUIDE[key]["best_for"],
                    "avoid_when": TEMPLATE_GUIDE[key]["avoid_when"],
                    "recommended_styles": TEMPLATE_GUIDE[key]["styles"],
                }
                for key in category["templates"]
            ],
        })
    return {"categories": categories, "template_count": len(TEMPLATES), "sketch_styles": SKETCH_STYLES}


def format_catalog():
    lines = ["Excalidraw 模板选择指南（10 个模板 / 4 类）"]
    for category in catalog_payload()["categories"]:
        lines.append(f"\n{category['name']}｜{category['question']}")
        for item in category["templates"]:
            lines.append(f"  - {item['label']} [{item['key']}]：{item['best_for']}")
    lines.append("\n选择时只向用户展示推荐项和最多 2 个备选项。")
    return "\n".join(lines)


def format_choices(intent_text):
    result = json.loads(recommend(intent_text))
    interaction = result["interaction"]
    if interaction["mode"] in ("auto", "ready"):
        return interaction["prompt"]
    lines = [interaction["prompt"]]
    for index, card in enumerate(interaction["options"], 1):
        mark = "（推荐）" if card["recommended"] else ""
        detail = card["why"] if interaction["mode"] == "select_style" else card["best_for"]
        lines.append(
            f"{index}. {card['label']}{mark}｜{card['style_label']}（{card['sketchStyle']}）：{detail}"
        )
    lines.append(interaction["reply_hint"] + "。")
    return "\n".join(lines)


def list_templates(format="text"):
    """列出所有可用模板"""
    if format == "json":
        data = {}
        for key, tmpl in TEMPLATES.items():
            guide = TEMPLATE_GUIDE[key]
            data[key] = {
                "name": tmpl["name"],
                "label": guide["label"],
                "category": guide["category"],
                "description": tmpl["description"],
                "best_for": guide["best_for"],
                "avoid_when": guide["avoid_when"],
                "recommended_styles": guide["styles"],
                "scenes": tmpl["scenes"],
                "complexity": tmpl["complexity"],
                "layout": tmpl["layout"],
                "elements": tmpl["elements"],
                "max_nodes": tmpl["max_nodes"]
            }
        data["_themes"] = {k: {"name": v["name"], "description": v["description"]} for k, v in THEMES.items()}
        data["_categories"] = catalog_payload()["categories"]
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        lines = [format_catalog(), "\n可用主题:"]
        for key, theme in THEMES.items():
            lines.append(f"  [{key:12s}] {theme['name']} - {theme['description']}")
        return "\n".join(lines)


def get_template_info(template_name):
    """查看模板详情"""
    key = _resolve_template_key(template_name)
    if not key:
        return json.dumps({"error": f"未找到模板: {template_name}"}, ensure_ascii=False, indent=2)
    
    tmpl = TEMPLATES[key]
    guide = TEMPLATE_GUIDE[key]
    category_key, category = _category_for(key)
    result = {
        "key": key,
        "name": tmpl["name"],
        "label": guide["label"],
        "category": {"key": category_key, "name": category["name"]},
        "description": tmpl["description"],
        "best_for": guide["best_for"],
        "avoid_when": guide["avoid_when"],
        "recommended_styles": guide["styles"],
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
    profile = _intent_profile(intent_text)
    scores, matched = _score_templates(profile["scoring_text"])
    ranked = _rank_templates(scores)
    primary, ranked = _select_primary_template(profile, scores, ranked)
    alternatives = _ranked_alternatives(primary, scores, ranked)
    style = profile["explicit_style"] or _style_for_template(primary, profile["lower"])
    confidence = _confidence_for(primary, alternatives, scores)
    reason = _recommendation_reason(primary, matched, profile["explicit_template"])
    interaction = _build_interaction(profile, primary, alternatives, style, reason)
    if profile["delivery_profile"] == "video-storyboard":
        interaction["prompt"] += " 交付方式为视频分镜，建议按 3–6 个 16:9 frame 组织内容；每帧可以使用不同图表模板。"
    elif profile["delivery_profile"] == "presentation-board":
        interaction["prompt"] += " 交付方式为演示白板，建议优先保证投屏字号和安全边距。"
    result = {
        "delivery": {
            "profile": profile["delivery_profile"],
            **DELIVERY_PROFILES[profile["delivery_profile"]],
        },
        "primary": {
            "key": primary,
            "name": TEMPLATES[primary]["name"],
            "label": TEMPLATE_GUIDE[primary]["label"],
            "category": TEMPLATE_GUIDE[primary]["category"],
            "description": TEMPLATES[primary]["description"],
            "reason": reason,
            "confidence": confidence,
        },
        "alternatives": [
            {
                "key": alt,
                "name": TEMPLATES[alt]["name"],
                "label": TEMPLATE_GUIDE[alt]["label"],
                "description": TEMPLATES[alt]["description"]
            }
            for alt in alternatives[:3]
        ],
        "available_themes": list(THEMES.keys()),
        "sketch_styles": SKETCH_STYLES,
        "recommendation": {
            "template": primary,
            "sketchStyle": style,
            "deliveryProfile": profile["delivery_profile"],
            "rationale": reason,
            "confidence": confidence,
            "requires_confirmation": interaction["requires_confirmation"],
        },
        "interaction": {
            "mode": interaction["mode"],
            "prompt": interaction["prompt"],
            "options": interaction["cards"],
            "max_options": 3,
            "reply_hint": (
                "回复序号、风格名，或“你直接选”"
                if interaction["mode"] == "select_style"
                else "回复序号、模板名，或“你直接选”"
            ),
        },
        "parameters": {
            "theme": "sketch",
            "sketchStyle": style,
            "delivery_profile": profile["delivery_profile"],
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

    elif cmd in ("--guide", "-g"):
        if "--json" in sys.argv:
            print(json.dumps(catalog_payload(), ensure_ascii=False, indent=2))
        else:
            print(format_catalog())
    
    elif cmd in ("--recommend", "-r"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --recommend \"画一个微服务架构图\"")
            sys.exit(1)
        intent = " ".join(sys.argv[2:])
        print(recommend(intent))

    elif cmd in ("--choices", "-c"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --choices \"分析有限元不收敛原因\"")
            sys.exit(1)
        intent = " ".join(arg for arg in sys.argv[2:] if arg != "--json")
        if "--json" in sys.argv:
            print(recommend(intent))
        else:
            print(format_choices(intent))
    
    elif cmd in ("--info", "-i"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --info flowchart")
            print("可用模板:", ", ".join(TEMPLATES.keys()))
            sys.exit(1)
        print(get_template_info(sys.argv[2]))
    
    elif cmd in ("--params", "-p"):
        if len(sys.argv) < 3:
            print("用法: template_selector.py --params flowchart --theme sketch --sketch-style engineering-notebook")
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
        sketch_style = None
        if "--sketch-style" in sys.argv:
            idx = sys.argv.index("--sketch-style")
            if idx + 1 < len(sys.argv):
                sketch_style = sys.argv[idx + 1]
                if sketch_style not in SKETCH_STYLES:
                    print(f"未知 sketchStyle: {sketch_style}")
                    sys.exit(1)
        if theme == "sketch" and sketch_style is None:
            sketch_style = TEMPLATE_GUIDE[key]["styles"][0]
        result = {
            "template": key,
            "name": TEMPLATES[key]["name"],
            "theme": theme,
            "sketchStyle": sketch_style,
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
        print("  template_selector.py --guide [--json]    # 分组选择指南")
        print("  template_selector.py --recommend <文本>  # 根据意图推荐")
        print("  template_selector.py --choices <文本>    # 生成用户选择菜单")
        print("  template_selector.py --info <模板名>     # 查看模板详情")
        print("  template_selector.py --params <模板名> [--theme <主题>] [--sketch-style <风格>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
