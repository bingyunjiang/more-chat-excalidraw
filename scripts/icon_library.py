#!/usr/bin/env python3
"""
自包含云架构图标库（C.7，借鉴 excalidraw-icons-mcp，28★）

程序生成语义化技术图标（SVG data URL），嵌入 Excalidraw image 元素，不依赖
外部图标资源。图标按技术类型配色 + 缩写文字，可被 ir_to_excalidraw.py
（--icons）自动匹配到架构图节点。

用法：
  python3 scripts/icon_library.py --list                 # 列出全部图标
  python3 scripts/icon_library.py --svg PostgreSQL       # 输出单个 SVG
  python3 scripts/icon_library.py --json                 # 输出 JSON 注册表
"""

import argparse
import base64
import json
import sys

# 技术类型 → 配色（与 color-palette.md 语义一致）
TYPE_COLORS = {
    "database": ("#0ca678", "#e6fcf5"),   # 青绿
    "queue":    ("#e8590c", "#fff4e6"),   # 橙
    "gateway":  ("#1c7ed6", "#e7f5ff"),   # 蓝
    "compute":  ("#37b24d", "#ebfbee"),   # 绿
    "storage":  ("#6741d9", "#f3f0ff"),   # 紫
    "cache":    ("#f783ac", "#fff0f6"),   # 粉
    "monitor":  ("#e03131", "#fff5f5"),   # 红
    "cicd":     ("#f59f00", "#fff9db"),   # 黄
    "infra":    ("#495057", "#f1f3f5"),   # 灰
}

# 技术名称 → 类型 + 图标缩写
TECH_ICONS = {
    # 数据库
    "PostgreSQL": ("database", "PG"), "MySQL": ("database", "MY"),
    "MariaDB": ("database", "MA"), "MongoDB": ("database", "MO"),
    "Redis": ("database", "RE"), "Elasticsearch": ("database", "ES"),
    "SQLite": ("database", "SQ"), "DynamoDB": ("database", "DY"),
    "Cassandra": ("database", "CA"), "Neo4j": ("database", "N4"),
    "InfluxDB": ("database", "IN"), "ClickHouse": ("database", "CH"),
    "TiDB": ("database", "TD"), "HBase": ("database", "HB"),
    # 消息队列
    "Kafka": ("queue", "KF"), "RabbitMQ": ("queue", "RQ"),
    "SQS": ("queue", "SQ"), "SNS": ("queue", "SN"),
    "Pulsar": ("queue", "PU"), "ActiveMQ": ("queue", "AM"),
    "RocketMQ": ("queue", "RK"), "NATS": ("queue", "NA"),
    "Flink": ("queue", "FL"), "Kinesis": ("queue", "KI"),
    # 网关
    "Nginx": ("gateway", "NG"), "API Gateway": ("gateway", "GW"),
    "Kong": ("gateway", "KG"), "Traefik": ("gateway", "TR"),
    "Envoy": ("gateway", "EN"), "HAProxy": ("gateway", "HA"),
    "ALB": ("gateway", "AL"), "CloudFront": ("gateway", "CF"),
    # 计算
    "Lambda": ("compute", "LB"), "EC2": ("compute", "EC"),
    "Fargate": ("compute", "FG"), "K8s Pod": ("compute", "PD"),
    "Docker": ("compute", "DK"), "VM": ("compute", "VM"),
    # 存储
    "S3": ("storage", "S3"), "GCS": ("storage", "GC"),
    "Blob Storage": ("storage", "BL"), "MinIO": ("storage", "MI"),
    "HDFS": ("storage", "HF"), "EBS": ("storage", "EB"),
    "EFS": ("storage", "EF"), "NFS": ("storage", "NF"),
    # 缓存/CDN
    "CDN": ("cache", "CD"), "Memcached": ("cache", "MC"),
    "Varnish": ("cache", "VA"),
    # 监测
    "Prometheus": ("monitor", "PR"), "Grafana": ("monitor", "GR"),
    "Datadog": ("monitor", "DD"), "CloudWatch": ("monitor", "CW"),
    "Jaeger": ("monitor", "JA"), "New Relic": ("monitor", "NR"),
    # CI/CD
    "Jenkins": ("cicd", "JN"), "GitHub Actions": ("cicd", "GH"),
    "GitLab CI": ("cicd", "GL"), "ArgoCD": ("cicd", "AG"),
    "Terraform": ("cicd", "TF"), "Ansible": ("cicd", "AN"),
    # 基础设施
    "Kubernetes": ("infra", "K8"), "K8s": ("infra", "K8"),
    "Consul": ("infra", "CS"), "Vault": ("infra", "VT"),
    "Istio": ("infra", "IS"), "CoreDNS": ("infra", "CD"),
}


def make_icon_svg(abbr, category):
    """生成 48x48 圆形图标 SVG（语义色 + 白色缩写）。"""
    color, bg = TYPE_COLORS.get(category, ("#495057", "#f1f3f5"))
    size = 48
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="24" cy="24" r="22" fill="{bg}" stroke="{color}" stroke-width="2.5"/>
  <text x="24" y="24" text-anchor="middle" dominant-baseline="central"
        font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold"
        fill="{color}">{abbr}</text>
</svg>'''


def svg_to_data_url(svg):
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def build_registry():
    """返回 {tech_name: {"abbr", "category", "dataURL", "mimeType"}}。"""
    reg = {}
    for name, (cat, abbr) in TECH_ICONS.items():
        svg = make_icon_svg(abbr, cat)
        reg[name] = {
            "abbr": abbr,
            "category": cat,
            "mimeType": "image/svg+xml",
            "dataURL": svg_to_data_url(svg),
        }
    return reg


def match_icon(tech_name, registry):
    """按技术名称匹配图标；支持子串匹配（如 'postgresql' → PostgreSQL）。"""
    if tech_name in registry:
        return registry[tech_name]
    lower = tech_name.lower()
    for name in registry:
        if name.lower() in lower:
            return registry[name]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="列出全部图标")
    ap.add_argument("--svg", help="输出指定技术的 SVG 源码")
    ap.add_argument("--json", action="store_true", help="输出 JSON 注册表")
    args = ap.parse_args()

    reg = build_registry()

    if args.json:
        print(json.dumps(reg, ensure_ascii=False, indent=2))
        return

    if args.svg:
        hit = match_icon(args.svg, reg)
        if not hit:
            print(f"未找到图标: {args.svg}", file=sys.stderr)
            sys.exit(1)
        # 解码 dataURL 还原 SVG 打印
        import re
        b64 = hit["dataURL"].split(",", 1)[1]
        print(base64.b64decode(b64).decode("utf-8"))
        return

    # 默认 --list
    print(f"共 {len(reg)} 个技术图标（自包含 SVG，按类型配色）\n")
    by_cat = {}
    for name, info in reg.items():
        by_cat.setdefault(info["category"], []).append(name)
    cat_names = {
        "database": "数据库", "queue": "消息队列", "gateway": "网关",
        "compute": "计算", "storage": "存储", "cache": "缓存/CDN",
        "monitor": "监测", "cicd": "CI/CD", "infra": "基础设施",
    }
    for cat, names in by_cat.items():
        print(f"[{cat_names.get(cat, cat)}] {', '.join(names)}")


if __name__ == "__main__":
    main()
