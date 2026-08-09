#!/usr/bin/env python3
"""
Excalidraw Library 组件加载器（C.7+，基于 excalidraw-libraries 生态）

从本地 .excalidrawlib 文件加载库组件，支持 v1（library 数组）和 v2（libraryItems）
格式。提供按名称查询组件、规范化元素 ID/坐标、重新定位到目标位置的功能。

用法：
  python3 scripts/library_loader.py --list                   # 列出所有可用库
  python3 scripts/library_loader.py --items <library>        # 列出库中所有组件
  python3 scripts/library_loader.py --export <library> <item> # 导出组件 JSON
  python3 scripts/library_loader.py --cache                  # 从 localhost:8080 缓存库
"""

import argparse
import json
import os
import hashlib
import sys
from pathlib import Path

# 默认库缓存目录
DEFAULT_LIB_DIR = os.path.join(os.path.dirname(__file__), "..", "references", "excalidraw-libs")
FALLBACK_LIB_DIR = "/tmp/excalidraw-libs"


# ─── IR 节点类型 → 库组件映射 ─────────────────────────────────────────────
# 每个映射条目: (library_file, item_name, scale)
LIBRARY_MAPPING = {
    # ── 数据库 ──
    "database":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "postgres":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "postgresql":       ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "mysql":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "mongodb":          ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "redis":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "elasticsearch":    ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "dynamodb":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "sqlite":           ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),
    "cassandra":        ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Database", 0.8),

    # ── 服务/组件 ──
    "service":          ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "component":        ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "process":          ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "apigateway":       ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "api gateway":      ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "api 网关":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "nginx":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "docker":           ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "kubernetes":       ("boemska-nik_kubernetes-icons.excalidrawlib", "deploy", 0.6),
    "k8s":              ("boemska-nik_kubernetes-icons.excalidrawlib", "deploy", 0.6),

    # ── 消息队列 ──
    "kafka":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "queue":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),
    "rabbitmq":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Component", 0.8),

    # ── 人物/用户 ──
    "actor":            ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Person", 0.7),
    "user":             ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Person", 0.7),
    "person":           ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Person", 0.7),

    # ── Web 应用 ──
    "web app":          ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Web App", 0.7),
    "web 前端":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Web App", 0.7),
    "frontend":         ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Web App", 0.7),
    "mobile app":       ("dmitry-burnyshev_c4-architecture.excalidrawlib", "Mobile App", 0.7),

    # ── AWS 服务 ──
    "lambda":           ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "Lambda", 1.2),
    "s3":               ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "S3", 1.2),
    "cloudfront":       ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "CloudFront", 1.2),
    "dynamodb_aws":     ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "DynamoDB", 1.2),
    "eventbridge":      ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "EventBridge", 1.2),
    "sqs_aws":          ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "SQS", 1.2),
    "sns_aws":          ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "SNS", 1.2),
    "appsync":          ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "AppSync", 1.2),
    "aurora":           ("stojanovic_aws-serverless-icons-v2.excalidrawlib", "Aurora", 1.2),

    # ── BPMN ──
    "task":             ("fraoustin_bpmn.excalidrawlib", "task", 0.7),
    "start event":      ("fraoustin_bpmn.excalidrawlib", "start event", 0.7),
    "end event":        ("fraoustin_bpmn.excalidrawlib", "end event", 0.7),

    # ── 通用形状回退（保持简单形状）──
    "start":            None,
    "end":              None,
    "decision":         None,
    "topic":            None,
    "branch":           None,
    "leaf":             None,
    "input":            None,
    "output":           None,
    "marker":           None,
    "milestone":        None,
    "plain":            None,
}

# tech 名称 → 类型别名（用于 label 匹配）
TECH_LABEL_ALIASES = {
    "postgresql": "postgres",
    "mysql": "database",
    "mongodb": "database",
    "redis": "database",
    "elasticsearch": "database",
    "dynamodb": "database",
    "api gateway": "apigateway",
    "api 网关": "apigateway",
    "web 前端": "web app",
    "nginx": "nginx",
    "kafka": "kafka",
    "rabbitmq": "queue",
    "docker": "docker",
    "kubernetes": "k8s",
    "lambda": "lambda",
    "s3": "s3",
    "cloudfront": "cloudfront",
}


def _find_lib_dir():
    """定位库文件目录。"""
    if os.path.isdir(DEFAULT_LIB_DIR):
        return DEFAULT_LIB_DIR
    if os.path.isdir(FALLBACK_LIB_DIR):
        return FALLBACK_LIB_DIR
    return None


def list_available_libraries(lib_dir=None):
    """列出所有可用的 .excalidrawlib 文件。"""
    d = lib_dir or _find_lib_dir()
    if not d:
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".excalidrawlib"))


def load_library(lib_file, lib_dir=None):
    """加载 .excalidrawlib 文件，返回统一格式。

    返回: {"items": [{"name": str, "elements": [dict]}], "format": "v1"|"v2"}
    """
    d = lib_dir or _find_lib_dir()
    if not d:
        raise FileNotFoundError(f"库目录不存在: {d}")
    path = os.path.join(d, lib_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"库文件不存在: {path}")

    with open(path, "r") as f:
        data = json.load(f)

    if "libraryItems" in data:
        items = []
        for item in data["libraryItems"]:
            items.append({
                "name": item.get("name", "unnamed"),
                "elements": item.get("elements", []),
                "id": item.get("id", ""),
            })
        return {"items": items, "format": "v2"}

    elif "library" in data:
        items = []
        for i, group in enumerate(data["library"]):
            items.append({
                "name": f"group-{i}",
                "elements": group if isinstance(group, list) else [],
                "id": f"v1-{i}",
            })
        return {"items": items, "format": "v1"}

    else:
        return {"items": [], "format": "unknown"}


def _bounding_box(elements):
    """计算元素组的边界框。"""
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")
    for el in elements:
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", 0) or 0
        h = el.get("height", 0) or 0
        if el.get("type") in ("line", "arrow", "draw") and el.get("points"):
            for px, py in el["points"]:
                min_x = min(min_x, x + px)
                min_y = min(min_y, y + py)
                max_x = max(max_x, x + px)
                max_y = max(max_y, y + py)
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
    if min_x == float("inf"):
        return 0, 0, 0, 0
    return min_x, min_y, max_x - min_x, max_y - min_y


def _new_id(namespace="library"):
    """生成可复现且足够短的 Excalidraw 元素 ID。"""
    return hashlib.sha256(namespace.encode("utf-8")).hexdigest()[:18]


def _new_group_id(namespace="group"):
    """生成新的 group ID。"""
    return _new_id(namespace)


def normalize_component(elements, target_x=0, target_y=0, scale=1.0, new_group_id=None):
    """规范化组件元素：重新分配 ID、坐标偏移到目标位置、缩放。

    Args:
        elements: 库组件元素列表
        target_x, target_y: 目标左上角坐标
        scale: 缩放比例
        new_group_id: 新的 group ID（None 则自动生成）

    Returns:
        (normalized_elements, bbox_dict) 元组
        bbox_dict = {"x", "y", "width", "height", "center_x", "center_y"}
    """
    if not elements:
        return [], {"x": 0, "y": 0, "width": 0, "height": 0, "center_x": 0, "center_y": 0}

    orig_x, orig_y, orig_w, orig_h = _bounding_box(elements)
    gid = new_group_id or _new_group_id(f"group:{target_x}:{target_y}:{scale}:{len(elements)}")

    # 旧 ID → 新 ID 映射
    id_map = {}
    for index, el in enumerate(elements):
        old_id = el.get("id", "")
        if old_id:
            id_map[old_id] = _new_id(f"element:{gid}:{index}:{old_id}")

    normalized = []
    for el in elements:
        nel = dict(el)

        # 重新分配 ID
        old_id = nel.get("id", "")
        nel["id"] = id_map.get(old_id, _new_id(f"element:{gid}:{len(normalized)}:{old_id}"))

        # 坐标偏移 + 缩放
        if "x" in nel:
            nel["x"] = target_x + (nel["x"] - orig_x) * scale
        if "y" in nel:
            nel["y"] = target_y + (nel["y"] - orig_y) * scale

        # 缩放尺寸
        if "width" in nel and nel["width"]:
            nel["width"] = nel["width"] * scale
        if "height" in nel and nel["height"]:
            nel["height"] = nel["height"] * scale

        # 缩放线条/箭头的 points
        if nel.get("type") in ("line", "arrow", "draw") and nel.get("points"):
            nel["points"] = [[px * scale, py * scale] for px, py in nel["points"]]

        # 缩放字体大小
        if "fontSize" in nel and nel["fontSize"]:
            nel["fontSize"] = nel["fontSize"] * scale

        # 统一 groupIds
        nel["groupIds"] = [gid]

        # 更新绑定引用：只保留映射到当前组件内的引用
        if "boundElements" in nel and isinstance(nel["boundElements"], list):
            new_be = []
            for be in nel["boundElements"]:
                if "id" in be and be["id"] in id_map:
                    be["id"] = id_map[be["id"]]
                    new_be.append(be)
                # 丢弃不在当前组件内的引用（如外部箭头绑定）
            nel["boundElements"] = new_be if new_be else None

        if "startBinding" in nel and isinstance(nel["startBinding"], dict):
            if nel["startBinding"].get("elementId") in id_map:
                nel["startBinding"]["elementId"] = id_map[nel["startBinding"]["elementId"]]

        if "endBinding" in nel and isinstance(nel["endBinding"], dict):
            if nel["endBinding"].get("elementId") in id_map:
                nel["endBinding"]["elementId"] = id_map[nel["endBinding"]["elementId"]]

        # 清除 containerId（库组件内的绑定关系在复制后无效）
        if "containerId" in nel:
            nel["containerId"] = None

        # 清除 version
        nel["version"] = 1
        nel["versionNonce"] = 0

        # 清除 frameId
        nel["frameId"] = None

        normalized.append(nel)

    new_w = orig_w * scale
    new_h = orig_h * scale
    bbox = {
        "x": target_x,
        "y": target_y,
        "width": new_w,
        "height": new_h,
        "center_x": target_x + new_w / 2,
        "center_y": target_y + new_h / 2,
    }

    return normalized, bbox


def lookup_component(node_type, label="", lib_dir=None):
    """根据节点类型和标签查找最佳匹配的库组件。

    Args:
        node_type: IR 节点类型（如 "database", "service"）
        label: 节点标签文本（如 "PostgreSQL", "API 网关"）
        lib_dir: 库文件目录

    Returns:
        (elements, scale) 或 None（无匹配时）
    """
    label_lower = label.lower().strip()

    # 1. 精确标签匹配
    if label_lower in LIBRARY_MAPPING:
        mapping = LIBRARY_MAPPING[label_lower]
        if mapping is None:
            return None
        return _load_mapped_component(mapping, lib_dir)

    # 2. 标签别名匹配
    if label_lower in TECH_LABEL_ALIASES:
        alias = TECH_LABEL_ALIASES[label_lower]
        if alias in LIBRARY_MAPPING:
            mapping = LIBRARY_MAPPING[alias]
            if mapping is None:
                return None
            return _load_mapped_component(mapping, lib_dir)

    # 3. 子串匹配标签
    for key, mapping in LIBRARY_MAPPING.items():
        if mapping is None:
            continue
        if key in label_lower:
            return _load_mapped_component(mapping, lib_dir)

    # 4. 节点类型匹配
    type_lower = node_type.lower()
    if type_lower in LIBRARY_MAPPING:
        mapping = LIBRARY_MAPPING[type_lower]
        if mapping is None:
            return None
        return _load_mapped_component(mapping, lib_dir)

    # 5. 模糊匹配
    for key, mapping in LIBRARY_MAPPING.items():
        if mapping is None:
            continue
        if key in type_lower or type_lower in key:
            return _load_mapped_component(mapping, lib_dir)

    return None


def _load_mapped_component(mapping, lib_dir=None):
    """加载映射条目对应的库组件。"""
    lib_file, item_name, scale = mapping
    try:
        lib = load_library(lib_file, lib_dir)
    except FileNotFoundError:
        return None

    for item in lib["items"]:
        if item["name"].lower() == item_name.lower():
            return item["elements"], scale
        if item_name.lower() in item["name"].lower():
            return item["elements"], scale

    return None


def search_components(query, lib_dir=None, max_results=20):
    """在所有库中搜索组件。"""
    d = lib_dir or _find_lib_dir()
    if not d:
        return []

    results = []
    query_lower = query.lower()
    libs = list_available_libraries(d)

    for lib_file in libs:
        try:
            lib = load_library(lib_file, d)
        except (json.JSONDecodeError, FileNotFoundError):
            continue
        for item in lib["items"]:
            if query_lower in item["name"].lower():
                results.append({
                    "library": lib_file,
                    "name": item["name"],
                    "elements_count": len(item["elements"]),
                    "format": lib["format"],
                })
                if len(results) >= max_results:
                    return results

    return results


# ─── CLI ───────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Excalidraw Library 组件加载器")
    ap.add_argument("--list", action="store_true", help="列出所有可用库")
    ap.add_argument("--items", help="列出指定库中的所有组件")
    ap.add_argument("--export", nargs=2, metavar=("LIBRARY", "ITEM"),
                     help="导出指定库组件的 JSON")
    ap.add_argument("--search", help="搜索所有库中的组件")
    ap.add_argument("--cache", action="store_true",
                     help="从 localhost:8080 缓存库到本地")
    ap.add_argument("--lib-dir", help="指定库文件目录")
    args = ap.parse_args()

    lib_dir = args.lib_dir

    if args.list:
        libs = list_available_libraries(lib_dir)
        if not libs:
            print("未找到库文件。请先运行 --cache 下载。")
            return
        print(f"共 {len(libs)} 个库文件：\n")
        for lib in libs:
            try:
                data = load_library(lib, lib_dir)
                print(f"  {lib} ({data['format']}, {len(data['items'])} items)")
            except Exception:
                print(f"  {lib} (读取失败)")

    elif args.items:
        try:
            data = load_library(args.items, lib_dir)
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return
        print(f"库: {args.items} ({data['format']}, {len(data['items'])} items)\n")
        for item in data["items"]:
            print(f"  {item['name']}: {len(item['elements'])} elements")

    elif args.export:
        lib_file, item_name = args.export
        try:
            data = load_library(lib_file, lib_dir)
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return
        for item in data["items"]:
            if item["name"].lower() == item_name.lower():
                print(json.dumps(item, ensure_ascii=False, indent=2))
                return
        print(f"未找到组件: {item_name}")

    elif args.search:
        results = search_components(args.search, lib_dir)
        if not results:
            print(f"未找到匹配 '{args.search}' 的组件")
            return
        print(f"搜索 '{args.search}' 结果 ({len(results)}):\n")
        for r in results:
            print(f"  [{r['library']}] {r['name']} ({r['elements_count']} elements, {r['format']})")

    elif args.cache:
        import urllib.request
        import urllib.error

        target_dir = lib_dir or DEFAULT_LIB_DIR
        os.makedirs(target_dir, exist_ok=True)

        print("正在从 localhost:8080 获取库列表...")
        try:
            resp = urllib.request.urlopen("http://localhost:8080/libraries.json", timeout=10)
            libraries = json.loads(resp.read())
        except urllib.error.URLError as e:
            print(f"连接失败: {e}")
            print("请确保 Excalidraw Libraries 服务运行在 localhost:8080")
            return

        print(f"发现 {len(libraries)} 个库，开始下载...")
        downloaded = 0
        for lib in libraries:
            source = lib.get("source", "")
            if not source:
                continue
            fname = source.replace("/", "_") + ".excalidrawlib"
            target = os.path.join(target_dir, fname)
            if os.path.exists(target):
                downloaded += 1
                continue
            try:
                url = f"http://localhost:8080/libraries/{source}"
                resp = urllib.request.urlopen(url, timeout=30)
                with open(target, "wb") as f:
                    f.write(resp.read())
                downloaded += 1
            except Exception as e:
                print(f"  下载失败 {source}: {e}")

        print(f"完成！共 {downloaded} 个库已缓存到 {target_dir}")

    else:
        ap.print_help()


if __name__ == "__main__":
    main()
